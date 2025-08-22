import builtins
import os
import traceback
import libcst as cst
import libcst.metadata as meta

from typing import Dict, Final, Iterable, Iterator, List, Mapping, Optional, Sequence, Set, Tuple, Union, overload

from .assembler import assemble


MAX_STRING_LENGTH: Final[int] = 127


def comment_source(extra: Optional[str] = None) -> str:
    if not os.environ.get("INSERT_CALLER_COMMENTS"):
        return ""

    lines = [line for line in traceback.format_stack() if line.strip().startswith("File")]

    # We should be the first line, so our caller is the second.
    relevant = lines[-2]
    relevant, _ = relevant.split(os.linesep, 1)
    _, details = relevant.split(", ", 1)

    if extra:
        details += f" ({extra})"

    return f"  ; {details}"


class Context:
    def __init__(self, module: str, node: cst.CSTNode, meta: Mapping[cst.CSTNode, meta.CodeRange], extra: str = "") -> None:
        self.module = module
        self.node = node
        self.meta = meta
        self.extra = extra
        self.mapping: Dict[cst.CSTNode, cst.CSTNode] = {}

    def wrap(self, node: cst.CSTNode, extra: str = "") -> "Context":
        context = Context(self.module, node, self.meta, extra)
        context.mapping = {x: y for x, y in self.mapping.items()}
        return context

    def virtual(self, node: cst.CSTNode, extra: str = "") -> "Context":
        context = Context(self.module, node, self.meta, extra)
        context.mapping = {x: y for x, y in self.mapping.items()}
        context.mapping[node] = self.node
        return context

    def coderange(self) -> Optional[meta.CodeRange]:
        # Look up virtual references.
        node = self.node
        while node in self.mapping:
            node = self.mapping[node]
        return self.meta.get(node)

    def comment(self) -> str:
        # Look up virtual references.
        node = self.node
        while node in self.mapping:
            node = self.mapping[node]

        fresh_module = cst.parse_module("")
        code = fresh_module.code_for_node(node)
        while code[-1] == "\n":
            code = code[:-1]
        codelines = code.split("\n")
        codelines = [c for c in codelines if c.strip()]
        return f"  ; {self.module} line {self.meta[node].start.line}: {self.extra}{codelines[0]}"


class CompilerError(Exception):
    def __init__(self, error: str, context: Context) -> None:
        metaval = context.coderange()
        if metaval:
            super().__init__(f"{context.module} line {metaval.start.line}: " + error)
        else:
            super().__init__(f"{context.module} line unknown: " + error)
        self.module = context.module
        self.line = metaval.start.line if metaval else None


class Sections:
    def __init__(
        self,
        *,
        preamble: Optional[List[str]] = None,
        code: Optional[List[str]] = None,
        data: Optional[List[str]] = None,
        init: Optional[List[str]] = None,
    ) -> None:
        self.preamble: List[str] = preamble or []
        self.code: List[str] = code or []
        self.data: List[str] = data or []
        self.init: List[str] = init or []

    def __iadd__(self, other: "Sections") -> "Sections":
        self.preamble += other.preamble
        self.code += other.code
        self.data += other.data
        self.init += other.init
        return self

    def append_preamble(self, line: str) -> None:
        self.preamble.append(line)

    def append_code(self, line: str) -> None:
        self.code.append(line)

    def append_data(self, line: str) -> None:
        self.data.append(line)

    def append_init(self, line: str) -> None:
        self.init.append(line)


class CoreType:
    """
    A standard type reference. Depending on where it's encountered, it can have a const[] modifier
    applied to it, and sometimes a nopad[] modifier applied to it.
    """

    def __init__(
        self,
        base_type: str,
        pointed_type: Optional["CoreType"] = None,
        *,
        length: Optional[int] = None,
        const: bool = False,
        extern: bool = False,
        return_padding: bool = True,
    ) -> None:
        self.type = base_type
        self.pointed_type = pointed_type
        self.const = const
        self.__length = length
        self.extern = extern
        self.return_padding = return_padding
        if self.type == "pointer" and pointed_type is None:
            raise Exception("Logic error, creating a pointer without a pointed type!")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.type == other
        if isinstance(other, CoreType):
            return self.type == other.type and self.pointed_type == other.pointed_type and self.const == other.const and self.length == other.length
        return False

    def __repr__(self) -> str:
        pre = ""
        post = ""
        typestr = self.type

        if self.type == "pointer":
            pre = "pointer[" + pre
            typestr = repr(self.pointed_type)
            post = post + "]"
        if self.const:
            pre = "const[" + pre
            post = post + "]"
        if not self.return_padding:
            pre = "nopad[" + pre
            post = post + "]"
        if self.extern:
            pre = "extern[" + pre
            post = post + "]"

        if self.__length is not None:
            typestr = f"{typestr}[{self.length}]"

        return pre + typestr + post

    def const_clone(self) -> "CoreType":
        if self.const:
            return self
        if self.type not in {"str", "pointer"}:
            return self

        return CoreType(
            self.type,
            self.pointed_type,
            length=self.length,
            const=True,
            extern=self.extern,
            return_padding=self.return_padding,
        )

    @property
    def length(self) -> int:
        return self.__length or 0

    @length.setter
    def length(self, newval: Optional[int]) -> None:
        if newval is not None and newval < 1:
            raise Exception("Logic error, setting length to negative or zero!")
        self.__length = newval

    @property
    def is_array(self) -> bool:
        return self.__length is not None

    @property
    def size(self) -> int:
        # Mostly a dummy type, for void returns.
        if self.type == "void":
            return 0
        if self.type in {"int8", "uint8"}:
            return 1
        if self.type in {"int16", "uint16"}:
            return 2
        if self.type in {"int32", "uint32"}:
            return 4
        # We do not support unicode because we talk to a VT-100 which is unaware of anything outside of English.
        if self.type == "char":
            return 1
        # Booleans are a single byte so we can compare with "ADDI".
        if self.type == "bool":
            return 1
        # Strings are passed by reference pointer.
        if self.type == "str":
            return 2
        # Pointers are 16 bit due to CPU arch.
        if self.type == "pointer":
            return 2
        raise NotImplementedError(f"Type {self.type} not implemented!")

    @property
    def is_unsigned(self) -> bool:
        return self.type in {"uint8", "uint16", "uint32", "char", "bool", "str", "pointer"}

    @property
    def is_signed(self) -> bool:
        return not self.is_unsigned

    @property
    def is_integer(self) -> bool:
        # int isn't a real type, but it is an integer from our perspective, we just haven't figured out the size yet.
        return self.type in {"int", "uint8", "uint16", "uint32", "int8", "int16", "int32"}

    @property
    def is_char(self) -> bool:
        return self.type == "char"

    @property
    def is_bool(self) -> bool:
        return self.type == "bool"

    @property
    def is_string(self) -> bool:
        return self.type == "str"

    @property
    def is_pointer(self) -> bool:
        return self.type == "pointer"


VoidType = CoreType("void", None, const=True, extern=False, return_padding=False)


class PreservedCoreType(CoreType):
    """
    A function call parmeter type that implies the called function will not clean this reference
    off of the stack, but instead that the stack will still contain this value upon return from
    the function. This does not imply that the values change, only that the values are not removed
    from the stack upon function call.
    """
    def __init__(self, base_type: str) -> None:
        super().__init__(base_type, None, const=True)

    def const_clone(self) -> "PreservedCoreType":
        # Always constant, already.
        if not self.const:
            raise Exception("Logic error, PreservedCoreType is somehow not const?")

        return self


class InOutCoreType(CoreType):
    """
    A function call parameter type that implies the value is not just referenced when calling
    the function, but also that the function updates this value and it should be copied back
    to any calling code's variable references if needed.
    """

    def __init__(self, base_type: str) -> None:
        super().__init__(base_type, None, const=False)

    def const_clone(self) -> "InOutCoreType":
        if self.type not in {"str", "pointer"}:
            return self

        new_type = InOutCoreType(
            self.type,
        )
        new_type.const = True
        return new_type


class OutCoreType(CoreType):
    """
    A function call parameter type that implies that the called function places an output parameter
    here, but that the caller does not need to specify a value for calling. This should be paired
    with a ParamReturnCoreType as the function return to specify that this is where to find the
    output value.
    """

    def __init__(self, base_type: str) -> None:
        super().__init__(base_type, None, const=False)

    def const_clone(self) -> "OutCoreType":
        if self.type not in {"str", "pointer"}:
            return self

        new_type = OutCoreType(
            self.type,
        )
        new_type.const = True
        return new_type


class RegisterCoreType(CoreType):
    """
    A function call parameter type that implies that the called function requests its input or
    places its output in a particular register instead of on the stack.
    """

    def __init__(self, base_type: str, register: str) -> None:
        super().__init__(base_type, None, const=False)
        self.register = register

    def const_clone(self) -> "RegisterCoreType":
        if self.type not in {"str", "pointer"}:
            return self

        new_type = RegisterCoreType(
            self.type, self.register
        )
        new_type.const = True
        return new_type


class ParamReturnCoreType(CoreType):
    """
    A function call return parameter that works in tandem with OutCoreType to specify which out
    argument contains the result of the function call.
    """

    def __init__(self, position: int) -> None:
        super().__init__("position: " + str(position), None, const=False)

    def const_clone(self) -> "ParamReturnCoreType":
        # This is just a pointer to a parameter value.
        return self

    @property
    def position(self) -> int:
        return int(self.type[10:])


class PaddingCoreType(CoreType):
    """
    A function call parameter that does not need to be provided by the code itself, but instead
    implies that the called function needs a certain amount of padding in the stack before calling.
    """

    def __init__(self, padbytes: int) -> None:
        super().__init__("padding: " + str(padbytes), None, const=False)

    def const_clone(self) -> "PaddingCoreType":
        # This is just a padding value.
        return self

    @property
    def padbytes(self) -> int:
        return int(self.type[9:])


def get_int(val: str, context: Context) -> int:
    try:
        if val.startswith("0x"):
            return int(val, 16)
        elif val.startswith("0b"):
            return int(val, 2)
        elif val.startswith("0o"):
            return int(val, 8)
        else:
            return int(val, 10)
    except Exception:
        # Don't want to have the exception linked as a cause.
        pass

    raise CompilerError(f"Could not parse {val} as integer.", context)


class Constant:
    def __init__(self, name: str, vartype: CoreType, value: object) -> None:
        self.name = name
        self.type = vartype
        self.value = value

    def __repr__(self) -> str:
        return f"Local constant {self.type!r} {self.name!r}: {self.value!r}"


def const_by_name(consts: List[Constant], name: str) -> Optional[Constant]:
    for const in consts:
        if const.name == name:
            return const
    return None


def type_comparison_compatible(left: CoreType, right: CoreType) -> bool:
    if left.type == "any":
        return True
    if right.type == "any":
        return True
    if left.is_integer and right.is_integer:
        return True
    if left.is_char and right.is_char:
        return True
    if left.is_bool and right.is_bool:
        return True
    if left.is_string and right.is_string:
        return True
    if left.is_pointer and right.is_pointer:
        return True
    if left.type == "string" and (right.is_string or right.is_char):
        return True
    if right.type == "string" and (left.is_string or left.is_char):
        return True
    return False


def get_type(
    expr: Optional[cst.CSTNode],
    constants: List[Constant],
    *,
    allow_nopad: bool = False,
    allow_extern: bool = False,
    allow_array: bool = False,
) -> Optional[CoreType]:
    if expr is None:
        return None
    if isinstance(expr, cst.Annotation):
        expr = expr.annotation
    if not isinstance(expr, cst.BaseExpression):
        return None

    const: bool = False
    extern: bool = False
    nopad: bool = False
    length: Optional[int] = None

    while True:
        if isinstance(expr, cst.Subscript):
            # Might be a const expr or a nopad expr. Might also be a size expr.
            qualifier = expr.value
            if not isinstance(qualifier, cst.Name):
                return None

            if len(expr.slice) == 1:
                sliceval = expr.slice[0]
                if isinstance(sliceval.slice, cst.Index):
                    # Attempt to evaluate and see if it comes back as an int.
                    try:
                        value = codegen_eval(sliceval.slice.value, constants)
                    except NonConstantExpressionException:
                        value = None

                    if isinstance(value, int):
                        expr = qualifier
                        length = value
                        continue

            if qualifier.value == "const":
                if len(expr.slice) != 1:
                    return None

                sliceval = expr.slice[0]
                if not isinstance(sliceval.slice, cst.Index):
                    return None

                const = True
                expr = sliceval.slice.value
                continue

            if qualifier.value == "extern":
                if len(expr.slice) != 1:
                    return None

                sliceval = expr.slice[0]
                if not isinstance(sliceval.slice, cst.Index):
                    return None

                extern = True
                expr = sliceval.slice.value
                continue

            if qualifier.value == "nopad":
                if len(expr.slice) != 1:
                    return None

                sliceval = expr.slice[0]
                if not isinstance(sliceval.slice, cst.Index):
                    return None

                nopad = True
                expr = sliceval.slice.value
                continue

            if qualifier.value == "pointer":
                if len(expr.slice) != 1:
                    return None

                sliceval = expr.slice[0]
                if not isinstance(sliceval.slice, cst.Index):
                    return None

                expr = sliceval.slice.value
                pointed = get_type(expr, constants, allow_nopad=allow_nopad, allow_extern=allow_extern, allow_array=allow_array)
                if pointed is None:
                    return None
                return CoreType("pointer", pointed, const=const, extern=extern, return_padding=not nopad)

            return None

        elif isinstance(expr, cst.Name):
            if nopad and not allow_nopad:
                return None
            if extern and not allow_extern:
                return None
            if length and not allow_array:
                return None

            if expr.value == "void":
                if length:
                    return None
                else:
                    return VoidType
            else:
                if expr.value not in {"uint8", "int8", "uint16", "int16", "uint32", "int32", "bool", "char", "str"}:
                    return None
                if length and expr.value not in {"str"}:
                    return None

                return CoreType(expr.value, None, length=length, const=const, extern=extern, return_padding=not nopad)

        else:
            return None


class UnvalidatedName(cst.Name):
    """
    Exists solely to be able to call create_call() with builtin references which are
    intentionally designed to include invalid characters for a python identifier. They
    do this so that it isn't possible to name a variable an internal identifier in a
    program you are attempting to compile.
    """

    def _validate(self) -> None:
        pass


def create_call(name: str, params: Iterable[cst.BaseExpression]) -> cst.Call:
    return cst.Call(
        func=cst.Name(value=name),
        args=[cst.Arg(value=param) for param in params],
    )


class FunctionPrototype:
    def __init__(self, name: str, return_type: CoreType, params: Optional[List[CoreType]] = None) -> None:
        self.name = name
        self.return_type = return_type
        self.params: List[CoreType] = params or []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FunctionPrototype):
            return False

        return self.name == other.name and self.return_type == other.return_type and self.params == other.params

    def __repr__(self) -> str:
        params = ', '.join('\'' + str(s) + '\'' for s in self.params)
        if not params:
            params = "none"
        return f"Function {self.name!r} params {params} return value {self.return_type!r}"


class GlobalVariable:
    def __init__(self, name: str, vartype: CoreType, marked: bool = False) -> None:
        self.name = name
        self.type = vartype
        self.marked = marked

    def mark(self) -> None:
        self.marked = True

    def __repr__(self) -> str:
        return f"Global variable {self.type!r} {self.name!r}"


def global_by_name(globs: Sequence[Union[FunctionPrototype, GlobalVariable]], name: str) -> Optional[GlobalVariable]:
    for glob in globs:
        if isinstance(glob, GlobalVariable) and glob.name == name:
            return glob
    return None


def get_assembled_length(compiled: List[str], refs: Sequence[Union[FunctionPrototype, GlobalVariable]], labels: List[str] = []) -> int:
    compiled = [c.split(";", 1)[0].strip() for c in compiled]
    compiled = [c for c in compiled if c]

    # Doesn't matter where these labels point, they're just going to be used with SETPC and CALL instrutions.
    deduped_labels: Set[str] = set()
    for ref in refs:
        deduped_labels.add(ref.name)
    for label in labels:
        deduped_labels.add(label)

    # Fix up any sort of string pointer references.
    for line in compiled:
        if "PUSHADDR" in line:
            label = line.split("PUSHADDR", 1)[1]
            label = label.strip()
            label = label.split(";", 1)[0]
            label = label.split(",", 1)[0]
            label = label.strip()
            deduped_labels.add(label)

    for label in deduped_labels:
        compiled.append(f"{label}:")

    memory = assemble(compiled)
    if not memory:
        return 0

    minval = memory[0][0]
    maxval = minval
    for loc, _ in memory:
        if loc < minval:
            minval = loc
        if loc > maxval:
            maxval = loc

    return (maxval - minval) + 1


def is_register_destination(name: str) -> bool:
    return name.startswith("register(") and name.endswith(")")


def register_type(name: str) -> Optional[CoreType]:
    if not is_register_destination(name):
        return None

    vals = name[9:-1].split(",", 1)
    return CoreType(vals[1].strip())


class LoopInfo:
    def __init__(self, stack_location: int, *, iter_label: str, else_label: Optional[str], exit_label: str) -> None:
        self.stack_location = stack_location
        self.iter_label = iter_label
        self.else_label = else_label
        self.exit_label = exit_label

    @property
    def labels(self) -> List[str]:
        return [self.iter_label, self.else_label, self.exit_label] if self.else_label else [self.iter_label, self.exit_label]


class StackVar:
    def __init__(self, name: str, vartype: CoreType, location: Optional[int] = None, initialized: bool = False) -> None:
        self.name = name
        self.type = vartype
        self.location = location
        self.initialized = initialized

    @property
    def size(self) -> int:
        return self.type.size

    @property
    def const(self) -> bool:
        return self.type.const

    @property
    def label(self) -> str:
        if self.type.type not in {"str"}:
            raise Exception("Logic error, trying to get a label name for a non-string type!")

        label = ""
        for c in self.name:
            if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_":
                label += c
            else:
                label += "_"
        return label

    def __repr__(self) -> str:
        return f"{self.type!r} {self.name}: {self.location} size {self.size}{' uninitialized' if not self.initialized else ''}"


class Stack:
    def __init__(self, funcname: str) -> None:
        self.funcname = funcname
        self.stack: List[StackVar] = []
        self.size: int = 0
        self.location: int = 0

    def __len__(self) -> int:
        return len(self.stack)

    @overload
    def __getitem__(self, index: int) -> StackVar: ...

    @overload
    def __getitem__(self, index: slice) -> List[StackVar]: ...

    def __getitem__(self, index: Union[int, slice]) -> Union[StackVar, List[StackVar]]:
        return self.stack[index]

    def __iter__(self) -> Iterator[StackVar]:
        yield from self.stack

    def clone(self) -> "Stack":
        stack = Stack(self.funcname)
        for entry in self.stack:
            stack.stack.append(StackVar(entry.name, entry.type, location=entry.location, initialized=entry.initialized))
        stack.size = self.size
        stack.location = self.location
        return stack

    def alloc(self, var: StackVar) -> int:
        var.location = self.size

        self.stack.append(var)
        self.size += var.size
        return var.size

    def free(self, name: str) -> None:
        if not self.stack:
            raise Exception("Logic error, freeing from empty stack!")
        if self.stack[-1].name != name:
            raise Exception("Logic error, not popping the right thing from stack!")

        self.size -= self.stack[-1].size
        self.stack = self.stack[:-1]

    def relocate(self, name: str, location: int) -> None:
        for entry in self.stack:
            if entry.name == name:
                entry.location = location
                break
        else:
            raise Exception(f"Logic error, tried relocating stack entry {name!r} that doesn't exist!")

        self.stack.sort(key=lambda s: s.location or 0)

    def retype(self, name: str, newtype: CoreType) -> None:
        for entry in self.stack:
            if entry.name == name:
                entry.type = newtype
                break
        else:
            raise Exception(f"Logic error, tried retyping stack entry {name!r} that doesn't exist!")

    def init(self, name: str) -> None:
        # Special case handling
        if is_register_destination(name):
            return

        for entry in self.stack:
            if entry.name == name:
                entry.initialized = True
                break
        else:
            raise Exception(f"Logic error, tried initializing stack entry {name!r} that doesn't exist!")

    def unwind(self, other_stack: "Stack") -> None:
        for entry in self.stack:
            if entry.initialized and not other_stack.initof(entry.name):
                entry.initialized = False

    def unify(self, *other_stacks: "Stack") -> None:
        if not other_stacks:
            raise Exception("Logic error, tried unifying with no additional stacks!")

        for entry in self.stack:
            # Find all uninitialized stack entries.
            if not entry.initialized:
                # Find out if they're initialized in all cloned stacks.
                for stack in other_stacks:
                    # It isn't so, bail early.
                    if not stack.initof(entry.name):
                        break
                else:
                    # It's initialized everywhere, so it's initialized here too.
                    entry.initialized = True

    def find(self, name: str) -> Optional[int]:
        loc = self.absfind(name)
        if loc is None:
            return None
        return loc - self.location

    def absfind(self, name: str) -> Optional[int]:
        for entry in self.stack:
            if entry.name == name:
                # Found it, calculate our relative offset.
                location = entry.location
                if location is None:
                    raise Exception(f"Logic error, stack allocated variable {entry.name} has no location!")
                return location
        return None

    def sizeof(self, name: str) -> Optional[int]:
        # Special case handling
        if is_register_destination(name):
            sentry = register_type(name)
            return sentry.size if sentry is not None else None

        for entry in self.stack:
            if entry.name == name:
                return entry.size
        return None

    def typeof(self, name: str) -> Optional[CoreType]:
        # Special case handling
        if is_register_destination(name):
            return register_type(name)

        for entry in self.stack:
            if entry.name == name:
                return entry.type
        return None

    def initof(self, name: str) -> Optional[bool]:
        for entry in self.stack:
            if entry.name == name:
                return entry.initialized
        return None

    def labelof(self, name: str) -> Optional[str]:
        for entry in self.stack:
            if entry.name == name:
                return f"{self.funcname}_{entry.label}"
        return None

    def diff(self, desired: int) -> int:
        return desired - self.location

    def move(self, offset: int) -> None:
        self.location = self.location + offset

    def at(self, offset: int) -> Optional[StackVar]:
        for entry in self.stack:
            if entry.location == offset:
                # Found it, return the variable we're at.
                return entry
        return None

    def __repr__(self) -> str:
        lines = [str(e) for e in self.stack]
        lines.append(f"Size: {self.size}, Loc: {self.location}")
        return "\n".join(lines)


def comment_stack(stack: Stack) -> List[str]:
    if not os.environ.get("INSERT_STACK_COMMENTS"):
        return []

    return [
        f"  ; Stack location: {stack.location}",
    ]


class NonConstantExpressionException(Exception):
    pass


def codegen_eval(expr: cst.BaseExpression, constants: List[Constant]) -> object:
    fresh_module = cst.parse_module("")
    code = fresh_module.code_for_node(
        cst.SimpleStatementLine(
            body=[
                cst.Expr(value=expr),
            ],
        )
    )

    # If we don't control our builtins, python will eval a bunch of stuff we don't support due to
    # its own builtins, and it will appear to work but only for constant expressions.
    builtins_dict: Dict[str, object] = {}
    for name in ["abs", "bool", "str", "len", "chr", "ord", "int"]:
        builtins_dict[name] = getattr(builtins, name)

    try:
        return eval(code, {"__builtins__": builtins_dict}, {c.name: c.value for c in constants})
    except Exception:
        pass

    raise NonConstantExpressionException(f"{expr} is not constant, cannot eval!")


def _hex(val: int, pad: int) -> str:
    hexval = hex(val)[2:]
    while len(hexval) < pad:
        hexval = "0" + hexval

    return "0x" + hexval


def generate_global_variable(assign: cst.AnnAssign, globs: List[GlobalVariable], consts: List[Constant], context: Context) -> Sections:
    compiled = Sections(code=[context.comment()])

    target_node = assign.target
    if not isinstance(target_node, cst.Name):
        raise CompilerError("Unsupported name for global variable definition", context)

    assign_name = target_node.value
    assign_type = get_type(assign.annotation.annotation, consts, allow_extern=True, allow_array=True)
    assign_value = assign.value

    if assign_type is None:
        raise CompilerError("Unsupported type for global variable definition", context)

    if assign_type.const and assign_type.extern:
        raise CompilerError("Cannot have a const extern global variable", context)

    for const in consts:
        if const.name == assign_name:
            raise CompilerError("Cannot reassign global variable", context)
    for glob in globs:
        if glob.name == assign_name:
            raise CompilerError("Cannot reassign global variable", context)

    if assign_type.const:
        if assign_value is None:
            raise CompilerError("Expecting initialization value for global const definition", context)
        if not isinstance(assign_value, cst.BaseExpression):
            raise CompilerError("Unsupported initialization value for global const definition", context)

        # Attempt to codegen and evaluate the python code.
        try:
            value = codegen_eval(assign_value, consts)
        except NonConstantExpressionException:
            raise CompilerError("Non-constant initialization value for global const definition", context)

        compiled.append_code(f"{assign_name}:")

        if assign_type.type in {"int8", "uint8"}:
            if assign_type.is_array:
                raise CompilerError("Unsupported array length for global const definition", context)
            if not isinstance(value, int):
                raise CompilerError("Unsupported initialization value for global const definition", context)
            if assign_type == "uint8":
                if value < 0 or value > 255:
                    raise CompilerError("Initialization out of bounds", context)
            else:
                if value < -128 or value > 255:
                    raise CompilerError("Initialization out of bounds", context)

            value = value & 0xFF
            compiled.append_code(f"  .byte {_hex((value >> 0) & 0xFF, 2)}")

        elif assign_type.type in {"int16", "uint16"}:
            if assign_type.is_array:
                raise CompilerError("Unsupported array length for global const definition", context)
            if not isinstance(value, int):
                raise CompilerError("Unsupported initialization value for global const definition", context)
            if assign_type == "uint16":
                if value < 0 or value > 65535:
                    raise CompilerError("Initialization out of bounds", context)
            else:
                if value < -32768 or value > 65535:
                    raise CompilerError("Initialization out of bounds", context)

            value = value & 0xFFFF
            compiled.append_code(f"  .byte {_hex((value >> 8) & 0xFF, 2)}")
            compiled.append_code(f"  .byte {_hex((value >> 0) & 0xFF, 2)}")

        elif assign_type.type in {"int32", "uint32"}:
            if assign_type.is_array:
                raise CompilerError("Unsupported array length for global const definition", context)
            if not isinstance(value, int):
                raise CompilerError("Unsupported initialization value for global const definition", context)
            if assign_type == "uint32":
                if value < 0 or value > 4294967295:
                    raise CompilerError("Initialization out of bounds", context)
            else:
                if value < -2147483648 or value > 4294967295:
                    raise CompilerError("Initialization out of bounds", context)

            value = value & 0xFFFFFFFF
            compiled.append_code(f"  .byte {_hex((value >> 24) & 0xFF, 2)}")
            compiled.append_code(f"  .byte {_hex((value >> 16) & 0xFF, 2)}")
            compiled.append_code(f"  .byte {_hex((value >> 8) & 0xFF, 2)}")
            compiled.append_code(f"  .byte {_hex((value >> 0) & 0xFF, 2)}")

        elif assign_type == "char":
            if assign_type.is_array:
                raise CompilerError("Unsupported array length for global const definition", context)
            if not isinstance(value, str):
                raise CompilerError("Unsupported initialization value for global const definition", context)
            if len(value) != 1:
                raise CompilerError("Unsupported initialization value for global const definition", context)
            compiled.append_code(f"  .char {value[0]!r}")

        elif assign_type == "str":
            if not isinstance(value, str):
                raise CompilerError("Unsupported initialization value for global const definition", context)

            length_needed = len(value) + 1
            if assign_type.is_array:
                # They want to specify an exact length, okay.
                if len(value) >= assign_type.length:
                    value = value[:(assign_type.length - 1)]
                length_needed = assign_type.length

            if length_needed > MAX_STRING_LENGTH:
                raise CompilerError(f"Unsupported too-long string, strings are required to be {MAX_STRING_LENGTH} characters maximum", context)

            length_provided = 0
            for c in value:
                compiled.append_code(f"  .char {c[0]!r}")
                length_provided += 1

            did_terminate = False
            while length_provided < length_needed:
                did_terminate = True
                compiled.append_code("  .byte 0x00")
                length_provided += 1

            if not did_terminate:
                raise Exception("Logic error, didn't terminate null-terminated string!")

        elif assign_type == "bool":
            if assign_type.is_array:
                raise CompilerError("Unsupported array length for global const definition", context)
            if not isinstance(value, bool):
                raise CompilerError("Unsupported initialization value for global const definition", context)
            compiled.append_code(f"  .byte {"0xFF" if value else "0x00"}")

        else:
            raise CompilerError(f"Unsupported type {assign_type.type} for global variable definition", context)

        # Since this was successfully handled, add it to our constants, so future constants may reference it as well.
        if assign_type == "str":
            # String constants are not inlined.
            globs.append(GlobalVariable(assign_name, assign_type))
        else:
            consts.append(Constant(assign_name, assign_type, value))

    else:
        if assign_value is not None:
            # Attempt to codegen and evaluate the python code.
            try:
                value = codegen_eval(assign_value, consts)
            except NonConstantExpressionException:
                raise CompilerError("Non-constant initialization value for global const definition", context)
        else:
            value = None

        if not assign_type.extern:
            compiled.append_data(f"{assign_name}:")

        if value is not None:
            compiled.append_init(f"  SETPC {assign_name}")

        if assign_type.type in {"int8", "uint8"}:
            if assign_type.is_array:
                raise CompilerError("Unsupported array length for global variable definition", context)
            if value is not None:
                if not isinstance(value, int):
                    raise CompilerError("Unsupported initialization value for global variable definition", context)
                if assign_type == "uint8":
                    if value < 0 or value > 255:
                        raise CompilerError("Initialization out of bounds", context)
                else:
                    if value < -128 or value > 255:
                        raise CompilerError("Initialization out of bounds", context)

                value = value & 0xFF
                compiled.append_init(f"  STOREI {_hex((value >> 0) & 0xFF, 2)}")

            if not assign_type.extern:
                compiled.append_data("  .pad 1")

        elif assign_type.type in {"int16", "uint16"}:
            if assign_type.is_array:
                raise CompilerError("Unsupported array length for global variable definition", context)
            if value is not None:
                if not isinstance(value, int):
                    raise CompilerError("Unsupported initialization value for global variable definition", context)
                if assign_type == "uint16":
                    if value < 0 or value > 65535:
                        raise CompilerError("Initialization out of bounds", context)
                else:
                    if value < -32768 or value > 65535:
                        raise CompilerError("Initialization out of bounds", context)

                value = value & 0xFFFF
                compiled.append_init(f"  STOREI {_hex((value >> 8) & 0xFF, 2)}")
                compiled.append_init("  INCPC")
                compiled.append_init(f"  STOREI {_hex((value >> 0) & 0xFF, 2)}")

            if not assign_type.extern:
                compiled.append_data("  .pad 2")

        elif assign_type.type in {"int32", "uint32"}:
            if assign_type.is_array:
                raise CompilerError("Unsupported array length for global variable definition", context)
            if value is not None:
                if not isinstance(value, int):
                    raise CompilerError("Unsupported initialization value for global variable definition", context)
                if assign_type == "uint32":
                    if value < 0 or value > 4294967295:
                        raise CompilerError("Initialization out of bounds", context)
                else:
                    if value < -2147483648 or value > 4294967295:
                        raise CompilerError("Initialization out of bounds", context)

                value = value & 0xFFFFFFFF
                compiled.append_init(f"  STOREI {_hex((value >> 24) & 0xFF, 2)}")
                compiled.append_init("  INCPC")
                compiled.append_init(f"  STOREI {_hex((value >> 16) & 0xFF, 2)}")
                compiled.append_init("  INCPC")
                compiled.append_init(f"  STOREI {_hex((value >> 8) & 0xFF, 2)}")
                compiled.append_init("  INCPC")
                compiled.append_init(f"  STOREI {_hex((value >> 0) & 0xFF, 2)}")

            if not assign_type.extern:
                compiled.append_data("  .pad 4")

        elif assign_type == "char":
            if assign_type.is_array:
                raise CompilerError("Unsupported array length for global variable definition", context)
            if value is not None:
                if not isinstance(value, str):
                    raise CompilerError("Unsupported initialization value for global variable definition", context)
                if len(value) != 1:
                    raise CompilerError("Unsupported initialization value for global variable definition", context)
                compiled.append_init(f"  STOREI {value[0]!r}")

            if not assign_type.extern:
                compiled.append_data("  .pad 1")

        elif assign_type == "str":
            if not assign_type.is_array:
                raise CompilerError("Non-constant global strings require a length", context)

            if value is not None:
                if not isinstance(value, str):
                    raise CompilerError("Unsupported initialization value for global variable definition", context)

                # We've specified an exact length, as we should for non-constant strings.
                if len(value) >= assign_type.length:
                    value = value[:(assign_type.length - 1)]

            length_needed = assign_type.length

            if length_needed > MAX_STRING_LENGTH:
                raise CompilerError(f"Unsupported too-long string, strings are required to be {MAX_STRING_LENGTH} characters maximum", context)

            if value is not None:
                for c in value:
                    compiled.append_init(f"  STOREI {c!r}")
                    compiled.append_init("  INCPC")
            compiled.append_init("  STOREI 0x00")

            compiled.append_data(f"  .pad {length_needed}")

        elif assign_type == "bool":
            if assign_type.is_array:
                raise CompilerError("Unsupported array length for global variable definition", context)
            if value is not None:
                if not isinstance(value, bool):
                    raise CompilerError("Unsupported initialization value for global variable definition", context)
                compiled.append_init(f"  STOREI {"0xFF" if value else "0x00"}")

            if not assign_type.extern:
                compiled.append_data("  .pad 1")

        else:
            raise CompilerError(f"Unsupported type {assign_type.type} for global variable definition", context)

        globs.append(GlobalVariable(assign_name, assign_type))

    return compiled


def generate_move_by(reason: str, move_amt: int, stack: Stack, clobbers: Set[str], context: Context) -> Sections:
    compiled = Sections()
    if move_amt == 0:
        return compiled

    if move_amt > 0:
        compiled.append_code(f"  SUBPCI {move_amt}" + comment_source(reason))
    elif move_amt < 0:
        compiled.append_code(f"  ADDPCI {-move_amt}" + comment_source(reason))

    stack.move(move_amt)
    compiled.code += comment_stack(stack)

    return compiled


def generate_move_to(destination: str, stack: Stack, clobbers: Set[str], context: Context, *, offset: int = 0) -> Sections:
    compiled = Sections()
    move_amt = stack.find(destination)
    if move_amt is None:
        raise Exception(f"Logic error, could not find {destination} on stack to move to!")
    move_amt += offset
    if move_amt == 0:
        return compiled

    if move_amt > 0:
        compiled.append_code(f"  SUBPCI {move_amt}" + comment_source(f"seeking {destination}"))
    elif move_amt < 0:
        compiled.append_code(f"  ADDPCI {-move_amt}" + comment_source(f"seeking {destination}"))

    stack.move(move_amt)
    compiled.code += comment_stack(stack)

    return compiled


def stack_is_at(destination: str, stack: Stack, *, offset: int = 0) -> bool:
    move_amt = stack.find(destination)
    if move_amt is None:
        raise Exception(f"Logic error, could not find {destination} on stack to compare to!")
    move_amt += offset
    return move_amt == 0


def generate_memcpy_locations(
    src_loc: int,
    dst_loc: int,
    size: int,
    stack: Stack,
    clobbers: Set[str],
    context: Context,
    register: str = "A",
) -> Sections:
    compiled = Sections()
    if src_loc == dst_loc:
        return compiled

    if register not in {"A", "U", "V"}:
        raise Exception("Logic error, unsupported register for copying!")

    from_rel = stack.diff(src_loc)
    compiled += generate_move_by("memcpy_unrolled", from_rel, stack, clobbers, context)
    shuffle_amount = stack.location - dst_loc
    if shuffle_amount == 0:
        return compiled

    if shuffle_amount < 0:
        for i in range(size):
            clobbers.add(register)

            compiled.append_code(f"  LOAD {register}")
            compiled.append_code(f"  SUBPCI {-shuffle_amount}" + comment_source())

            stack.move(-shuffle_amount)
            compiled.code += comment_stack(stack)

            compiled.append_code(f"  STORE {register}")

            if i < size - 1:
                compiled.append_code(f"  ADDPCI {(-shuffle_amount) - 1}" + comment_source())
                stack.move(-((-shuffle_amount) - 1))
                compiled.code += comment_stack(stack)

    else:
        for i in range(size):
            clobbers.add(register)

            compiled.append_code(f"  LOAD {register}")
            compiled.append_code(f"  ADDPCI {shuffle_amount}" + comment_source())

            stack.move(-shuffle_amount)
            compiled.code += comment_stack(stack)

            compiled.append_code(f"  STORE {register}")

            if i < size - 1:
                compiled.append_code(f"  SUBPCI {shuffle_amount + 1}" + comment_source())
                stack.move(shuffle_amount + 1)
                compiled.code += comment_stack(stack)

    return compiled


def generate_memcpy_stackvars(
    destination: str,
    source: str,
    stack: Stack,
    clobbers: Set[str],
    context: Context,
    register: str = "A",
) -> Sections:
    compiled = Sections()
    if source == destination:
        return compiled

    if register not in {"A", "U", "V"}:
        raise Exception("Logic error, unsupported register for copying!")

    source_size = stack.sizeof(source)
    destination_size = stack.sizeof(destination)
    if source_size is None or destination_size is None:
        raise Exception("Logic error, could not find variable to memcpy!")
    if source_size != destination_size:
        raise Exception("Logic error, unequal sizes in memcpy!")

    if stack_is_at(source, stack, offset=destination_size - 1):
        # We're already at the top of the stack, generate the load/func/store loop downwards
        # instead of upwards to shave off a move instruction.
        def actual_expr_offset(offset: int) -> int:
            return (destination_size - offset) - 1
    else:
        # We're anywhere else in the stack, so it costs us no unnecessary move instructions
        # to perform the first move.
        def actual_expr_offset(offset: int) -> int:
            return offset

    # Move to the right spot on the stack and then perform the operation on the two numbers.
    # Since bitwise operations are independent we can just do this in a loop.
    for offset in range(destination_size):
        clobbers.add(register)
        compiled += generate_move_to(source, stack, clobbers, context, offset=actual_expr_offset(offset))
        compiled.append_code(f"  LOAD {register}")
        compiled += generate_move_to(destination, stack, clobbers, context, offset=actual_expr_offset(offset))
        compiled.append_code(f"  STORE {register}")

    return compiled


def can_relocate_return(function_type: CoreType, stack: Stack, clobbers: Set[str], context: Context) -> bool:
    if function_type is VoidType:
        raise Exception("Logic error, cannot calculate overlap with void function!")

    # If we are a string type and we overlap with actual values on the stack, we can't relocate since
    # we could end up needing to use those in the expression that we're relocating. Unlike other expression
    # types that only write to the destination on final result, strings check for allocation since they're
    # pointers, and so we could end up writing the pointer over an input param.
    if function_type.is_string:
        for loc in [0, 1]:
            val = stack.at(loc)
            if val is None:
                continue
            if val.name == "builtin(padding)":
                continue
            return False
        return True

    # Figure out if we need to move the retptr to make room for our final value on the stack.
    retval_abs = 0
    retval_size = stack.sizeof("builtin(retval)")
    retptr_abs = stack.absfind("builtin(retptr)")
    retptr_size = stack.sizeof("builtin(retptr)")

    if retval_abs is None or retval_size is None or retptr_abs is None or retptr_size is None:
        raise Exception("Logic error, failed to calculate return value and pointer overlap!")

    retval_locs = {retval_abs + i for i in range(retval_size)}
    retptr_locs = {retptr_abs + i for i in range(retptr_size)}
    overlap = retval_locs.intersection(retptr_locs)
    return not overlap


def generate_return(function_type: CoreType, stack: Stack, clobbers: Set[str], context: Context) -> Sections:
    compiled = Sections(code=[context.comment()])

    # Because we could have more than one return, make sure we clone the stack to not mess with the rest of the function.
    stack = stack.clone()

    # We need to ensure that our stack only contains the return value and the return pointer.
    # Make sure to move the return value, the return pointer, and then pop all of our saved builtins.
    retptr_in_uv = False
    retptr_final_loc = 0
    if function_type is not VoidType:
        # First, we need to figure out if where we're copying the return value will clobber the return pointer.
        # If so, we need to store that in the U/V registers. We could put it on the stack but that's way more
        # shuffling so much slower. Much better to just mark U/V as clobbered and use them.
        if not can_relocate_return(function_type, stack, clobbers, context):
            cref = comment_ref()
            compiled.append_code(f"  ; Saving return pointer to U/V so it isn't overridden by return shuffle. {cref}")

            # We need to actually save the retptr to U/V.
            clobbers.add("U")
            clobbers.add("V")
            retptr_in_uv = True

            first_move = stack.find("builtin(retptr)")
            if first_move is None:
                raise Exception("Logic error, failed to get move amounts for builtin(retptr)!")
            initialized = stack.initof("builtin(retptr)")
            if not initialized:
                raise Exception("Logic error, builtin(retptr) has not been initialized!")

            # Generate code to move from our position to the first byte of the retval.
            compiled += generate_move_by("seeking builtin(retptr)", first_move, stack, clobbers, context)
            compiled.append_code("  LOAD U")
            compiled.append_code("  DECPC")

            stack.move(1)
            compiled.code += comment_stack(stack)

            compiled.append_code("  LOAD V")
            compiled.append_code(f"  ; {cref}")

        # Second, make sure the top of the stack is our return.
        top_spot = stack.at(0)
        if top_spot is not None and top_spot.name != "builtin(retval)":
            cref = comment_ref()
            compiled.append_code(f"  ; Moving return value to correct location in stack. {cref}")

            # We need to use the A register to move the value, so it's clobbered now.
            clobbers.add("A")

            # We need to relocate the retptr to this spot.
            src_loc = stack.absfind("builtin(retval)")
            number_of_moves = stack.sizeof("builtin(retval)")
            initialized = stack.initof("builtin(retval)")

            if src_loc is None or number_of_moves is None:
                raise Exception("Logic error, failed to get move amounts for builtin(retval)!")
            if not initialized:
                raise Exception("Logic error, builtin(retval) has not been initialized!")

            # Generate code to move from our position to the first byte of the retptr.
            retptr_final_loc = number_of_moves
            compiled += generate_memcpy_locations(src_loc, 0, number_of_moves, stack, clobbers, context)
            compiled.append_code(f"  ; {cref}")

    # Now, move the return pointer if needed.
    if retptr_in_uv:
        cref = comment_ref()
        compiled.append_code(f"  ; Restoring the return pointer from U/V to the correct location. {cref}")

        # Gotta grab it out of the saved U/V registers.
        restore_move_amt = retptr_final_loc - stack.location
        compiled += generate_move_by("seeking return pointer restoration point", restore_move_amt, stack, clobbers, context)
        compiled.append_code("  STORE U")
        compiled.append_code("  DECPC")

        stack.move(1)
        compiled.code += comment_stack(stack)

        compiled.append_code("  STORE V")
        compiled.append_code(f"  ; {cref}")
    else:
        retptr_abs = stack.absfind("builtin(retptr)")
        if retptr_abs is None:
            raise Exception("Logic error, failed to calculate the source location of builtin(retptr)!")
        initialized = stack.initof("builtin(retptr)")
        if not initialized:
            raise Exception("Logic error, builtin(retptr) has not been initialized!")

        if retptr_abs != retptr_final_loc:
            cref = comment_ref()
            compiled.append_code(f"  ; Moving return pointer to correct location in stack. {cref}")

            # We need to use the A register to move the value, so it's clobbered now.
            clobbers.add("A")

            # We need to relocate the retptr to this spot.
            src_loc = stack.absfind("builtin(retptr)")
            number_of_moves = stack.sizeof("builtin(retptr)")

            if src_loc is None or number_of_moves is None:
                raise Exception("Logic error, failed to get move amounts for builtin(retptr)!")

            # Generate code to move from our position to the first byte of the retptr.
            compiled += generate_memcpy_locations(src_loc, retptr_final_loc, number_of_moves, stack, clobbers, context)
            compiled.append_code(f"  ; {cref}")

    # Now, pop all of our saved registers, and then return.
    tlcref: Optional[str] = None
    if clobbers:
        tlcref = comment_ref()
        compiled.append_code(f"  ; Restoring all clobbered registers. {tlcref}")
    while stack.size > 0:
        name = stack[-1].name
        if name[:13] == "builtin(saved":
            move_amt = stack.find(name)
            if move_amt is None:
                raise Exception(f"Logic error, failed to get move amounts for {name}!")
            if not stack.initof(name):
                raise Exception(f"Logic error, {name} has not been initialized!")

            if name == "builtin(saved_spc)":
                move_amt += 1
            compiled += generate_move_by(f"seeking {name}", move_amt, stack, clobbers, context)

            if name == "builtin(saved_a)":
                compiled.append_code("  POP A")
                stack.move(-1)
                compiled.code += comment_stack(stack)
            elif name == "builtin(saved_u)":
                compiled.append_code("  POP U")
                stack.move(-1)
                compiled.code += comment_stack(stack)
            elif name == "builtin(saved_v)":
                compiled.append_code("  POP V")
                stack.move(-1)
                compiled.code += comment_stack(stack)
            elif name == "builtin(saved_spc)":
                compiled.append_code("  POP SPC")
                stack.move(-2)
                compiled.code += comment_stack(stack)
            else:
                raise Exception(f"Logic error, unexpected saved type {name}!")

        stack.free(name)

    if tlcref:
        compiled.append_code(f"  ; {tlcref}")

    # Now, if we need to, move past any temporary values we didn't pop but don't care about.
    final_move_to_ret = stack.diff(retptr_final_loc + 1)
    compiled += generate_move_by("skipping past temporary locals", final_move_to_ret, stack, clobbers, context)
    compiled.append_code("  RET")

    return compiled


def generate_const_load(val: object, destination: str, stack: Stack, clobbers: Set[str], context: Context) -> Sections:
    compiled = Sections()

    dtype = stack.typeof(destination)
    if dtype is None:
        raise Exception("Logic error, could not determine type of destination to load constant to!")

    if dtype.is_integer:
        if not isinstance(val, int):
            raise CompilerError("Unsupported non-integer constant load!", context)

        if dtype.is_unsigned and val < 0:
            raise CompilerError("Cannot use a negative value in an unsigned expression!", context)

        if is_register_destination(destination):
            compiled.append_code(f"  LOADI {_hex((val >> 0) & 0xFF, 2)}")
        else:
            clobbers.add("A")

            dest_loc = stack.find(destination)
            dest_size = stack.sizeof(destination)
            if dest_loc is None or dest_size is None:
                raise Exception("Logic error, cannot find destination to load constant to!")

            compiled += generate_move_by(f"seeking {destination}", dest_loc, stack, clobbers, context)
            if dest_size == 1:
                compiled.append_code(f"  LOADI {_hex((val >> 0) & 0xFF, 2)}")
                compiled.append_code("  STORE A")
            elif dest_size == 2:
                compiled.append_code(f"  LOADI {_hex((val >> 0) & 0xFF, 2)}")
                compiled.append_code("  STORE A")
                compiled.append_code("  DECPC")

                stack.move(1)
                compiled.code += comment_stack(stack)

                compiled.append_code(f"  LOADI {_hex((val >> 8) & 0xFF, 2)}")
                compiled.append_code("  STORE A")
            elif dest_size == 4:
                compiled.append_code(f"  LOADI {_hex((val >> 0) & 0xFF, 2)}")
                compiled.append_code("  STORE A")
                compiled.append_code("  DECPC")

                stack.move(1)
                compiled.code += comment_stack(stack)

                compiled.append_code(f"  LOADI {_hex((val >> 8) & 0xFF, 2)}")
                compiled.append_code("  STORE A")
                compiled.append_code("  DECPC")

                stack.move(1)
                compiled.code += comment_stack(stack)

                compiled.append_code(f"  LOADI {_hex((val >> 16) & 0xFF, 2)}")
                compiled.append_code("  STORE A")
                compiled.append_code("  DECPC")

                stack.move(1)
                compiled.code += comment_stack(stack)

                compiled.append_code(f"  LOADI {_hex((val >> 24) & 0xFF, 2)}")
                compiled.append_code("  STORE A")
            else:
                raise CompilerError(f"Unsupported destination {destination} for const load", context)

    elif dtype.is_bool:
        if not isinstance(val, bool):
            raise CompilerError("Unsupported non-boolean constant load!", context)

        intval = 0xFF if val else 0x00

        if is_register_destination(destination):
            compiled.append_code(f"  LOADI {_hex((intval >> 0) & 0xFF, 2)}")
        else:
            clobbers.add("A")

            dest_loc = stack.find(destination)
            dest_size = stack.sizeof(destination)
            if dest_loc is None or dest_size is None:
                raise Exception("Logic error, cannot find destination to load constant to!")

            compiled += generate_move_by(f"seeking {destination}", dest_loc, stack, clobbers, context)
            compiled.append_code(f"  LOADI {_hex((intval >> 0) & 0xFF, 2)}")
            compiled.append_code("  STORE A")

    elif dtype.is_char:
        if not isinstance(val, str):
            raise CompilerError("Unsupported non-character constant load!", context)
        if len(val) != 1:
            raise CompilerError(f"Invalid character constant {val!r}", context)

        if is_register_destination(destination):
            compiled.append_code(f"  LOADI {val!r}")
        else:
            clobbers.add("A")

            dest_loc = stack.find(destination)
            dest_size = stack.sizeof(destination)
            if dest_loc is None or dest_size is None:
                raise Exception("Logic error, cannot find destination to load constant to!")

            compiled += generate_move_by(f"seeking {destination}", dest_loc, stack, clobbers, context)
            compiled.append_code(f"  LOADI {val!r}")
            compiled.append_code("  STORE A")

    else:
        raise CompilerError(f"Unsupported constant load of type {dtype.type}!", context)

    return compiled


def get_function_prototype(
    call: cst.Call,
    stack: Stack,
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> FunctionPrototype:
    if isinstance(call.func, cst.Name):
        # Simple reference to a function on the refs list. If it isn't in the refs list, then it could be
        # a function pointer which needs to be supported but is not for now.
        func_ref = call.func.value
        for ref in refs:
            if isinstance(ref, FunctionPrototype) and ref.name == func_ref:
                return ref
        else:
            raise CompilerError(f"Unknown function {func_ref} in call", context)

    else:
        # TODO: Support function pointers here at some point. Maybe even objects or structs?
        raise CompilerError(f"Unsupported function call with expression node {call.func}", context)


def get_function_params_impl(
    call: cst.Call,
    function_prototype: FunctionPrototype,
    context: Context,
) -> Tuple[List[cst.Arg], List[CoreType]]:
    # Gather up arguments, including any defaults and in the future respecting kwargs.
    args: List[cst.Arg] = []
    for arg in call.args:
        # TODO: At some point, maybe we can support these, because it would just be extraction from a list
        # in the star arg case, and choosing the correct argument order in the keyword argument case.
        if arg.keyword is not None:
            raise CompilerError("Unsupported keyword argument in function call", context)
        if arg.star != "":
            raise CompilerError("Unsupported star argument in function call", context)

        args.append(arg)

    # Make sure that the number of arguments supplied matches
    param_count: int = 0
    needed_args: List[CoreType] = []
    for needed_arg in function_prototype.params:
        # All arguments that are passed by reference (strings, pointers, arrays) need to be marked as const
        # here, simply to stop any sort of internal copy on assign operation. We don't want to force the
        # programmer to declare all params of this type const because then they couldn't have mutatable params.
        needed_args.append(needed_arg.const_clone())

        if isinstance(needed_arg, PaddingCoreType):
            # Not the responsibility of the caller, we will set this up.
            continue
        if isinstance(needed_arg, OutCoreType):
            # Not the responsibility of the caller, we will set this up.
            continue

        param_count += 1

    if param_count != len(args):
        # TODO: This is where we would possibly substitute default arguments.
        raise CompilerError(f"Function {function_prototype.name} expects {param_count} args but {len(args)} were given", context)

    return args, needed_args


def get_function_params(
    call: cst.Call,
    function_prototype: FunctionPrototype,
    context: Context,
) -> Tuple[List[cst.Arg], List[CoreType]]:
    args, needed_args = get_function_params_impl(call, function_prototype, context)
    needed_args = [na for na in needed_args if not isinstance(na, (PaddingCoreType, OutCoreType))]
    return args, needed_args


def generate_function_call_internal(
    call: cst.Call,
    destination: Optional[str],
    types: Dict[cst.CSTNode, CoreType],
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    compiled = Sections(code=[context.comment()])
    function_prototype = get_function_prototype(call, stack, refs, local_consts, context)

    # Ensure that we're not trying to assign a void function call to an expression.
    if destination is not None and function_prototype.return_type is VoidType:
        raise CompilerError(f"Cannot assign result of function {function_prototype.name} returning void", context)

    # Make sure that the prototype's params actually make sense.
    seen_nonpreserved = False
    seen_outtype = False
    for pos, param in enumerate(function_prototype.params):
        if isinstance(param, (InOutCoreType, PreservedCoreType)):
            if seen_nonpreserved:
                raise CompilerError(
                    f"Function {function_prototype.name} includes preserved parameter {pos + 1} after unpreserved parameter",
                    context,
                )
            if seen_outtype:
                raise CompilerError(
                    f"Function {function_prototype.name} includes preserved parameter {pos + 1} after out-only parameter",
                    context,
                )
        elif isinstance(param, OutCoreType):
            seen_outtype = True
        elif isinstance(param, RegisterCoreType):
            pass
        else:
            seen_nonpreserved = True
            if seen_outtype:
                raise CompilerError(
                    f"Function {function_prototype.name} includes normal parameter {pos + 1} after out-only parameter",
                    context,
                )
        if isinstance(param, ParamReturnCoreType):
            raise Exception(f"Logic error, not expecting a return-only type for param {pos + 1} in {function_prototype.name}")

    # Now, we must figure out how to set up the stack to call this function.
    args, computed_params = get_function_params_impl(call, function_prototype, context)

    # Now, go through the requested parameters and set up the stack.
    copy_mapping: Dict[str, str] = {}
    out_mapping: Dict[int, str] = {}
    delayed_params: List[RegisterCoreType] = []
    delayed_args: List[cst.Arg] = []
    delayed_generate: List[bool] = []
    temporary_stack_entries: List[str] = []
    stack_on_exit: int = stack.size - 1
    normal_return_loc: int = stack.size
    optimized_offset: int = 0

    # First, pattern-match on the input parameters we were given to figure out if we can
    # reuse the stack partially or fully.
    for arglen in reversed(range(1, len(args) + 1)):
        # Take the prefix of the arg list, see if they all line up with the stack.
        if len(stack) < arglen:
            # Can't possibly be a match
            continue

        # Only allow register-based matching on the final parameter.
        full_params = arglen == len(args)

        considered = args[:arglen]
        stackvars = stack[-arglen:]
        params = computed_params[:arglen]

        argnames: List[str] = []
        argnodes: List[cst.CSTNode] = []
        for arg in considered:
            if isinstance(arg.value, cst.Name):
                argnames.append(arg.value.value)
                argnodes.append(arg.value)
            else:
                break

        if len(argnames) != arglen or len(argnodes) != arglen:
            continue

        for i in range(arglen):
            # If the names don't match, this isn't an overlay we can use.
            if argnames[i] != stackvars[i].name:
                break
            # If the types don't match, then we can't do anything with this.
            if stackvars[i].size != params[i].size:
                break
        else:
            # All of the stack variables line up, let's double check that calling semantics
            # allow for us to use these as-is instead of making copies.
            if destination is not None and argnames[0] == destination:
                # If the first parameter is also our return value, then we can only keep this
                # optimization if the first parameter is a normal core type and the return
                # value is a normal return type, or if the first parameter is in/out or out
                # and the return value comes from this parameter.
                if isinstance(params[0], (PreservedCoreType, RegisterCoreType, PaddingCoreType)):
                    # Cannot make these match under any circumstances.
                    continue
                elif isinstance(params[0], (InOutCoreType, OutCoreType)):
                    # Can only match these if the return is this stack position.
                    if isinstance(function_prototype.return_type, ParamReturnCoreType):
                        if function_prototype.return_type.position != 0:
                            # Not the right one, need to make space on the stack to not clobber
                            # the values that are there.
                            continue
                    else:
                        # Not the return value, need to make space so these don't clobber the
                        # return value.
                        continue

                    # Also can only match if we're not a const InOutCoreType.
                    if isinstance(params[0], InOutCoreType):
                        actual_arg = considered[0].value
                        if isinstance(actual_arg, cst.Name):
                            arg_type = stack.typeof(actual_arg.value)
                            if not arg_type:
                                raise Exception("Logic error, could not determine type of function argument!")
                            if arg_type.const:
                                continue

            match = False
            for i in range(arglen):
                if isinstance(params[i], RegisterCoreType):
                    # These can match if they're the final param, because we'll end up popping
                    # it off the stack to put the value in a register.
                    if not full_params or i != (arglen - 1):
                        break
                elif isinstance(params[i], PaddingCoreType):
                    # These can never match. We'd need to be even more clever with picking out
                    # register types from the middle of the argument list, and padding needs to
                    # be inserted in the stack at the right spot.
                    break
                elif isinstance(params[i], OutCoreType):
                    # This is added to the stack, and I genuinely don't know what to do in this
                    # optimization case if this shows up here.
                    break
                elif isinstance(params[i], PreservedCoreType):
                    # These are a match, since they either preserve the value, or replace it.
                    pass
                elif isinstance(params[i], InOutCoreType):
                    # These are a match, since they either preserve the value, or replace it.
                    actual_arg = considered[i].value
                    if isinstance(actual_arg, cst.Name):
                        arg_type = stack.typeof(actual_arg.value)
                        if not arg_type:
                            raise Exception("Logic error, could not determine type of function argument!")
                        if arg_type.const:
                            break
                else:
                    # This is a conditional match, but ONLY if we're using internal temporaries
                    # that we know we're good to throw away.
                    if not isinstance(argnodes[i], UnvalidatedName):
                        # It's a real variable, we can't throw it away, it needs to stay on the stack.
                        break
                    if destination is not None and argnames[i] == destination and i > 0:
                        # It's our destination value, so it can't be thrown away, it needs to stay
                        # on the stack. We already checked the first parameter above, however, so
                        # don't bother flagging if that's a match.
                        break
            else:
                match = True

            if match:
                # Need to fix up where the stack is going to be on exit based on params that will
                # be "consumed" by the function call.
                for i in range(arglen):
                    param_in_question = params[i]

                    if not stackvars[i].initialized:
                        raise CompilerError(f"Use of uninitialized variable {stackvars[i].name!r}", context)
                    if isinstance(param_in_question, (PaddingCoreType, OutCoreType)):
                        raise Exception("Logic error, unexpected stackvar type!")
                    elif isinstance(param_in_question, PreservedCoreType):
                        continue
                    elif isinstance(param_in_question, InOutCoreType):
                        out_mapping[i] = stackvars[i].name
                        continue
                    elif isinstance(param_in_question, RegisterCoreType):
                        delayed_params.append(param_in_question)
                        delayed_args.append(considered[i])
                        delayed_generate.append(False)
                        stack_on_exit -= stackvars[i].size
                        normal_return_loc -= stackvars[i].size
                    else:
                        # The calling function is going to consume this.
                        stack_on_exit -= stackvars[i].size
                        normal_return_loc -= stackvars[i].size
                optimized_offset = arglen
                break

    which_arg: int = optimized_offset

    for rawpos, needed_arg in enumerate(computed_params[optimized_offset:]):
        # Special case for if the first argument is already the top of the stack, and it's a preserved or in-out
        # argument. In this case, we don't have to do anything, because the function will do what it should do with
        # that stack location. In theory we should be able to do this with as many elements on the stack as possible
        # for in-out and preserved params but that's a lot of work to think through so we're not doing it for now.
        pos = rawpos + optimized_offset

        if isinstance(needed_arg, PaddingCoreType):
            # Simple padding that the function will clean up on its own. Add that padding to the stack.
            for _ in range(needed_arg.padbytes):
                stack.alloc(StackVar("builtin(padding)", CoreType('int8')))
                temporary_stack_entries.append("builtin(padding)")

        elif isinstance(needed_arg, OutCoreType):
            # This is an out parameter, so we need to be able to track its position and what temporary
            # variable we assign to it so we can copy the value to our destination after calling.
            out_dest = expr_temp_name()
            out_mapping[pos] = out_dest
            stack_on_exit += stack.alloc(StackVar(out_dest, needed_arg, initialized=True))
            temporary_stack_entries.append(out_dest)

        elif isinstance(needed_arg, RegisterCoreType):
            # Because we can't just do the calculation here since a subsequent arg expression calculation
            # might clobber one of the registers, we delay this so that we do this after everything else.
            delayed_params.append(needed_arg)
            delayed_args.append(args[which_arg])
            delayed_generate.append(True)
            which_arg += 1

        elif isinstance(needed_arg, InOutCoreType):
            # Not only do we need to compute the input for this, but we need to copy the value back if the
            # input was a variable name or global variable reference, so we preserve in-out behavior.
            expr_dest = expr_temp_name()
            out_mapping[pos] = expr_dest

            arg_in_question = args[which_arg].value
            if isinstance(arg_in_question, cst.Name):
                copy_mapping[arg_in_question.value] = expr_dest
            stack_on_exit += stack.alloc(StackVar(expr_dest, needed_arg, initialized=True))
            temporary_stack_entries.append(expr_dest)
            compiled += generate_expr_internal(arg_in_question, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(arg_in_question))
            which_arg += 1

        elif isinstance(needed_arg, PreservedCoreType):
            # This is just preserved, so we don't have to worry about copy it out, but we do need to allocate it.
            expr_dest = expr_temp_name()
            stack_on_exit += stack.alloc(StackVar(expr_dest, needed_arg))
            temporary_stack_entries.append(expr_dest)
            compiled += generate_expr_internal(args[which_arg].value, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(args[which_arg].value))
            which_arg += 1

        else:
            # This is just a normal core type, so we put it on the stack, and the function takes it back off again.
            # So we don't need to fix up the stack any when we come back from the function call.
            expr_dest = expr_temp_name()
            stack.alloc(StackVar(expr_dest, needed_arg))
            temporary_stack_entries.append(expr_dest)
            compiled += generate_expr_internal(args[which_arg].value, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(args[which_arg].value))
            which_arg += 1

    # Now, load our registers up with any register parameters.
    stack_skip = 0
    for i in range(len(delayed_params) - 1, -1, -1):
        needed_arg = delayed_params[i]
        provided_arg = delayed_args[i]

        # All functions that take a register core type assume signed integers.
        reg_to_type = {
            "A": "int8",
        }
        if needed_arg.register not in reg_to_type:
            raise Exception(f"Logic error, tried to assign a param to unsupported register {needed_arg.register} in function {function_prototype.name}")

        # Make sure we mark this as clobbered since we're going to mess it up.
        clobbers.add(needed_arg.register)

        if delayed_generate[i]:
            reg_dest = expr_temp_name()
            stack.alloc(StackVar(reg_dest, CoreType(reg_to_type[needed_arg.register])))
            compiled += generate_expr_internal(provided_arg.value, reg_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(provided_arg.value))
            compiled += generate_move_to(reg_dest, stack, clobbers, context)
            compiled.append_code(f"  POP {needed_arg.register}")
            stack.location -= 1
            stack.free(reg_dest)
        else:
            if not isinstance(arg.value, UnvalidatedName):
                raise Exception("Logic error, params that don't need generation should be on the stack!")
            reg_dest = arg.value.value
            compiled += generate_move_to(reg_dest, stack, clobbers, context)
            compiled.append_code(f"  POP {needed_arg.register}")
            stack.location -= 1
            stack_skip += 1

    # Now, we're ready to actually call the function. Move to the last byte of the last parameter on the stack.
    move_amount = stack.diff(stack.size - (stack_skip + 1))
    compiled += generate_move_by("moving to last parameter", move_amount, stack, clobbers, context)
    compiled.append_code(f"  CALL {function_prototype.name}")

    # Now, calculate the true position of the stack after calling the function, so future manipulations of
    # the stack know where we really are. It's important to do this here because some return cleanup bits
    # below end up using the location of the stack.
    if not isinstance(function_prototype.return_type, (RegisterCoreType, ParamReturnCoreType)):
        # We need to understand where we actually are on the stack, so add to the
        # location where the return would have been put on the stack.
        stack_on_exit += function_prototype.return_type.size

    stack.location = stack_on_exit
    compiled.code += comment_stack(stack)

    # Track whether we captured the return value or not.
    return_handled = False

    # Now, if the return type is a register type, put it in the destination.
    unsafe_to_clobber = False
    if isinstance(function_prototype.return_type, RegisterCoreType):
        return_handled = True
        if destination is not None:
            if is_register_destination(destination):
                # We're already returning to a register, so we're done here!
                if function_prototype.return_type.register != "A":
                    raise Exception(f"Logic error, unsupported register destination {function_prototype.return_type.register} for function")
                unsafe_to_clobber = True
            else:
                compiled += generate_move_to(destination, stack, clobbers, context)
                if function_prototype.return_type.register == "A":
                    compiled.append_code("  STORE A")
                    stack.init(destination)
                else:
                    raise Exception(f"Logic error, unsupported register destination {function_prototype.return_type.register} for function")

    # Now, do some bookkeeping, first copying anything that we need to copy that was an in-out param.
    for dst, src in copy_mapping.items():
        source_size = stack.sizeof(src)
        dest_type = stack.typeof(dst)
        if source_size is None:
            raise Exception(f"Logic error, Undefined variable reference to {src!r}", context)
        if dest_type is None:
            raise Exception("Logic error, cannot find destination to copy variable value to!")

        if not dest_type.const:
            stack.init(dst)
            if source_size == dest_type.size:
                compiled += generate_memcpy_stackvars(dst, src, stack, clobbers, context, register="U" if unsafe_to_clobber else "A")
            else:
                raise CompilerError("Unsupported byref assignment from different variable sizes", context)

    # Now, if the return is in one of the parameters, copy that to our destination.
    if isinstance(function_prototype.return_type, ParamReturnCoreType):
        return_handled = True
        if destination is not None:
            src = out_mapping[function_prototype.return_type.position]
            dst = destination

            source_size = stack.sizeof(src)
            dest_size = stack.sizeof(dst)
            if source_size is None:
                raise Exception(f"Logic error, undefined variable reference to {src!r}", context)
            if dest_size is None:
                raise Exception("Logic error, cannot find destination to copy variable value to!")

            stack.init(dst)

            if source_size == dest_size:
                compiled += generate_memcpy_stackvars(dst, src, stack, clobbers, context, register="U" if unsafe_to_clobber else "A")
            else:
                raise CompilerError("Unsupported function return from different variable sizes", context)

    # Now, fix up our view of the stack.
    for entry in reversed(temporary_stack_entries):
        stack.free(entry)

    # Now, if needed, copy the return value from the stack to its location.
    if (not return_handled) and (not (function_prototype.return_type is VoidType)):
        if destination is not None:
            if is_register_destination(destination):
                # Pop the value from the stack, instead of copying.
                src_loc = normal_return_loc
                src_size = function_prototype.return_type.size
                if src_size != 1:
                    raise Exception(f"Logic error, trying to assign value of size {src_size} to A register")

                move_amt = stack.diff(src_loc)
                compiled += generate_move_by("seeking return location", move_amt, stack, clobbers, context)
                compiled.append_code("  LOAD A")
            else:
                src_loc = normal_return_loc
                src_size = function_prototype.return_type.size
                dest_loc = stack.absfind(destination)
                dest_size = stack.sizeof(destination)
                if dest_loc is None or dest_size is None:
                    raise Exception(f"Logic error, cannot find destination {destination} to copy variable value to!")
                stack.init(destination)

                if src_size == dest_size:
                    compiled += generate_memcpy_locations(src_loc, dest_loc, dest_size, stack, clobbers, context, register="U" if unsafe_to_clobber else "A")
                else:
                    raise CompilerError("Unsupported function return from different variable sizes", context)

    return compiled


def generate_function_call(
    call: cst.Call,
    destination: Optional[str],
    types: Dict[cst.CSTNode, CoreType],
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    # Generate builtins code for python intrinsics that we wish to support.
    if isinstance(call.func, cst.Name) and call.func.value in {"len", "str", "peek", "poke", "abs", "bool", "chr", "ord", "int"}:
        function_prototype = get_function_prototype(call, stack, [*refs, *builtin_functions()], local_consts, context)
        args, arg_types = get_function_params(call, function_prototype, context)

        if function_prototype.name == "len":
            if len(args) != 1 or len(arg_types) != 1:
                raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

            if destination is None:
                raise CompilerError("Unsupported expression without assignment!", context)

            # String or array length calculation.
            return generate_function_call_internal(
                create_call("strlen", [args[0].value]),
                destination,
                types,
                stack,
                clobbers,
                allocations,
                refs,
                local_consts,
                context,
            )

        elif function_prototype.name == "str":
            if len(args) != 1 or len(arg_types) != 1:
                raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

            if destination is None:
                raise CompilerError("Unsupported expression without assignment!", context)

            # Cast from whatever data type to string, so we must handle this on a case by case basis.
            expr = args[0].value

            if types[expr].is_string:
                # We're done, this is already a string.
                return generate_expr_internal(expr, destination, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

            elif types[expr].is_char:
                compiled = Sections()

                # We need to cast this by creating a string, so we need to allocate that string on the stack.
                if not stack.initof(destination):
                    # We're creating a string in an unusual place, given that normally we only create strings on the LHS
                    # of any assignment. So, we must hand-check our destination's size in case it was declared const as
                    # an optimization for avoiding strcpy.
                    destination_type = stack.typeof(destination)
                    if destination_type is None:
                        raise Exception("Logic error, cannot find destination type for str() conversion!")

                    if (not destination_type.is_array) and destination_type.const:
                        destination_type.length = 2

                    compiled += generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                    # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                    stack.init(destination)

                # We need to do a strcpy at this point, to the destination.
                clobbers.add("SPC")
                clobbers.add("A")

                # Calculate the expression we're converting to a string.
                compiled += generate_expr_internal(expr, "register(A, char)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                # Set up the SPC to point at the string.
                compiled += generate_move_to(destination, stack, clobbers, context, offset=1)
                compiled.append_code("  POP SPC")
                stack.move(-2)
                compiled.code += comment_stack(stack)

                # Set the character value to the string, null-terminate.
                compiled.append_code("  SWAP PC, SPC")
                compiled.append_code("  STORE A")
                compiled.append_code("  INCPC")
                compiled.append_code("  STOREI 0")
                compiled.append_code("  SWAP PC, SPC")

                return compiled

            elif types[expr].is_bool:
                true = cst.SimpleString('"True"')
                false = cst.SimpleString('"False"')
                fake_expr = cst.IfExp(test=expr, body=true, orelse=false)
                return generate_expr_internal(fake_expr, destination, types, stack, clobbers, allocations, refs, local_consts, context.virtual(true).virtual(false).virtual(fake_expr))

            elif types[expr].is_integer:
                compiled = Sections()

                # Figure out the needed length for any allocation.
                needed_length = {
                    "uint8": 4,
                    "int8": 5,
                    "uint16": 6,
                    "int16": 7,
                    "uint32": 11,
                    "int32": 12,
                }[types[expr].type]

                # We need to cast this by creating a string, so we need to allocate that string on the stack.
                if not stack.initof(destination):
                    # We're creating a string in an unusual place, given that normally we only create strings on the LHS
                    # of any assignment. So, we must hand-check our destination's size in case it was declared const as
                    # an optimization for avoiding strcpy.
                    destination_type = stack.typeof(destination)
                    if destination_type is None:
                        raise Exception("Logic error, cannot find destination type for str() conversion!")

                    if (not destination_type.is_array) and destination_type.const:
                        destination_type.length = needed_length

                    compiled += generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                    # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                    stack.init(destination)

                # Now, call the correct function to convert.
                needed_function = {
                    "uint8": "utoa8",
                    "int8": "itoa8",
                    "uint16": "utoa16",
                    "int16": "itoa16",
                    "uint32": "utoa32",
                    "int32": "itoa32",
                }[types[expr].type]
                compiled += generate_function_call_internal(
                    create_call(needed_function, [expr, UnvalidatedName(destination)]),
                    None,
                    types,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context,
                )

                return compiled

            else:
                raise Exception(f"Logic error, attempted to convert unsupported type {types[expr].type} to string!")

        elif function_prototype.name == "peek":
            compiled = Sections()

            if len(args) != 1 or len(arg_types) != 1:
                raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

            # Generate the actual memory address that we're going to peek from.
            addr_expr = args[0].value
            addr_dest = expr_temp_name()
            stack.alloc(StackVar(addr_dest, CoreType("uint16"), initialized=True))
            compiled += generate_expr_internal(addr_expr, addr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(addr_expr))

            # This is going to clobber the SPC no matter what.
            clobbers.add("SPC")

            if destination is None:
                # Assume that this is just a read of an address to clear a hardware register that's clear on read.
                compiled += generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                compiled.append_code("  POP SPC")
                stack.move(-2)
                compiled.code += comment_stack(stack)

                clobbers.add("A")
                compiled.append_code("  SWAP PC, SPC")
                compiled.append_code("  LOAD A")
                compiled.append_code("  SWAP PC, SPC")

            else:
                # Figure out what to do based on the destination type.
                destination_type = stack.typeof(destination)
                if destination_type is None:
                    raise Exception("Logic error, couldn't determine destination type for peek!")

                if destination_type.type in {"int8", "uint8", "char"}:
                    # This one's an easy one, just move to the right spot and load the value, copying it over.
                    compiled += generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                    compiled.append_code("  POP SPC")
                    stack.move(-2)
                    compiled.code += comment_stack(stack)

                    clobbers.add("A")
                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  LOAD A")
                    compiled.append_code("  SWAP PC, SPC")

                    if not is_register_destination(destination):
                        compiled += generate_move_to(destination, stack, clobbers, context)
                        compiled.append_code("  STORE A")
                        stack.init(destination)

                elif destination_type.type == "bool":
                    # Can't just load like above, our compiler assumes that boolean true/false is always 0xff/0x00.
                    # So if we load a value and pretend it's boolean it could mess up any other boolean checks.
                    compiled += generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                    compiled.append_code("  POP SPC")
                    stack.move(-2)
                    compiled.code += comment_stack(stack)

                    clobbers.add("A")
                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  LOAD A")
                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  ADDI 0")
                    compiled.append_code("  LOADI 0x00")
                    compiled.append_code("  SKIPIF ZF")
                    compiled.append_code("  INV")

                    if not is_register_destination(destination):
                        compiled += generate_move_to(destination, stack, clobbers, context)
                        compiled.append_code("  STORE A")
                        stack.init(destination)

                elif destination_type.type in {"int16", "uint16"}:
                    # This one's slightly harder, need to copy two things, but that's manageable.
                    compiled += generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                    compiled.append_code("  POP SPC")
                    stack.move(-2)
                    compiled.code += comment_stack(stack)

                    clobbers.add("A")
                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  LOAD A")
                    compiled.append_code("  SWAP PC, SPC")

                    compiled += generate_move_to(destination, stack, clobbers, context, offset=1)
                    compiled.append_code("  STORE A")

                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  INCPC")
                    compiled.append_code("  LOAD A")
                    compiled.append_code("  SWAP PC, SPC")

                    compiled.append_code("  INCPC")
                    compiled.append_code("  STORE A")
                    stack.move(-1)

                elif destination_type.type in {"int32", "uint32"}:
                    # This one needs to copy 4 things, but I'm gonna unroll that since it's easier than writing a loop.
                    compiled += generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                    compiled.append_code("  POP SPC")
                    stack.move(-2)
                    compiled.code += comment_stack(stack)

                    clobbers.add("A")
                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  LOAD A")
                    compiled.append_code("  SWAP PC, SPC")

                    compiled += generate_move_to(destination, stack, clobbers, context, offset=3)
                    compiled.append_code("  STORE A")

                    # Second byte.
                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  INCPC")
                    compiled.append_code("  LOAD A")
                    compiled.append_code("  SWAP PC, SPC")

                    compiled.append_code("  INCPC")
                    compiled.append_code("  STORE A")

                    # Third byte.
                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  INCPC")
                    compiled.append_code("  LOAD A")
                    compiled.append_code("  SWAP PC, SPC")

                    compiled.append_code("  INCPC")
                    compiled.append_code("  STORE A")

                    # Fourth byte.
                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  INCPC")
                    compiled.append_code("  LOAD A")
                    compiled.append_code("  SWAP PC, SPC")

                    compiled.append_code("  INCPC")
                    compiled.append_code("  STORE A")
                    stack.move(-3)

                elif destination_type.type == "str":
                    # Recast this as a string pointer, since that's what it is.
                    stack.retype(addr_dest, CoreType("str", const=True))

                    # We also need to make sure the destination is initalized so we can do a strcpy.
                    if not stack.initof(destination):
                        compiled += generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                        # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                        stack.init(destination)

                    compiled += generate_function_call_internal(
                        create_call("strcpy", [UnvalidatedName(destination), UnvalidatedName(addr_dest)]),
                        None,
                        types,
                        stack,
                        clobbers,
                        allocations,
                        refs,
                        local_consts,
                        context,
                    )

                else:
                    raise Exception(f"Logic error, unexpected type {destination_type.type} in peek() evaluation!")

            # Free our temporary variable and move on.
            stack.free(addr_dest)
            return compiled

        elif function_prototype.name == "poke":
            compiled = Sections()

            if len(args) != 2 or len(arg_types) != 2:
                raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

            if destination is not None:
                raise CompilerError("Cannot assign result of function poke returning void", context)

            # Generate the actual memory address that we're going to poke to.
            addr_expr = args[0].value
            addr_dest = expr_temp_name()
            stack.alloc(StackVar(addr_dest, CoreType("uint16"), initialized=True))
            compiled += generate_expr_internal(addr_expr, addr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(addr_expr))

            # Then, generate the expression we're going to poke into the above address.
            data_expr = args[1].value
            data_dest = expr_temp_name()
            stack.alloc(StackVar(data_dest, types[data_expr].const_clone(), initialized=True))
            compiled += generate_expr_internal(data_expr, data_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(data_expr))

            # This is going to clobber the SPC and A no matter what.
            clobbers.add("SPC")
            clobbers.add("A")

            if types[data_expr].type in {"int8", "uint8", "char", "bool"}:
                # This one's an easy one, just move to the right spot and store the value, copying it over.
                # There's no special case for bool here, since we control it's contents and are just storing it.
                compiled += generate_move_to(data_dest, stack, clobbers, context)
                compiled.append_code("  LOAD A")

                compiled += generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                compiled.append_code("  POP SPC")
                stack.move(-2)
                compiled.code += comment_stack(stack)

                compiled.append_code("  SWAP PC, SPC")
                compiled.append_code("  STORE A")
                compiled.append_code("  SWAP PC, SPC")

            elif types[data_expr].type in {"int16", "uint16"}:
                # This one's slightly harder, need to copy two things, but that's manageable.
                compiled += generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                compiled.append_code("  POP SPC")
                stack.move(-2)
                compiled.code += comment_stack(stack)

                compiled += generate_move_to(data_dest, stack, clobbers, context, offset=1)
                compiled.append_code("  LOAD A")
                compiled.append_code("  SWAP PC, SPC")
                compiled.append_code("  STORE A")

                compiled.append_code("  SWAP PC, SPC")
                compiled.append_code("  INCPC")
                compiled.append_code("  LOAD A")
                compiled.append_code("  SWAP PC, SPC")

                compiled.append_code("  INCPC")
                compiled.append_code("  STORE A")
                compiled.append_code("  SWAP PC, SPC")

                stack.move(-1)

            elif types[data_expr].type in {"int32", "uint32"}:
                # This one needs to copy 4 things, but I'm gonna unroll that since it's easier than writing a loop.
                compiled += generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                compiled.append_code("  POP SPC")
                stack.move(-2)
                compiled.code += comment_stack(stack)

                compiled += generate_move_to(data_dest, stack, clobbers, context, offset=3)
                compiled.append_code("  LOAD A")
                compiled.append_code("  SWAP PC, SPC")
                compiled.append_code("  STORE A")

                # Second byte.
                compiled.append_code("  SWAP PC, SPC")
                compiled.append_code("  INCPC")
                compiled.append_code("  LOAD A")
                compiled.append_code("  SWAP PC, SPC")

                compiled.append_code("  INCPC")
                compiled.append_code("  STORE A")

                # Third byte.
                compiled.append_code("  SWAP PC, SPC")
                compiled.append_code("  INCPC")
                compiled.append_code("  LOAD A")
                compiled.append_code("  SWAP PC, SPC")

                compiled.append_code("  INCPC")
                compiled.append_code("  STORE A")

                # Fourth byte.
                compiled.append_code("  SWAP PC, SPC")
                compiled.append_code("  INCPC")
                compiled.append_code("  LOAD A")
                compiled.append_code("  SWAP PC, SPC")

                compiled.append_code("  INCPC")
                compiled.append_code("  STORE A")
                compiled.append_code("  SWAP PC, SPC")

                stack.move(-3)

            elif types[data_expr].type == "str":
                # Recast this as a string pointer, since that's what it is.
                stack.retype(addr_dest, CoreType("str"))

                compiled += generate_function_call_internal(
                    create_call("strcpy", [UnvalidatedName(addr_dest), UnvalidatedName(data_dest)]),
                    None,
                    types,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context,
                )

            else:
                raise Exception(f"Logic error, unexpected type {types[data_expr]} in poke() evaluation!")

            # Free our temporary variable and move on.
            stack.free(data_dest)
            stack.free(addr_dest)
            return compiled

        elif function_prototype.name == "abs":
            if len(args) != 1 or len(arg_types) != 1:
                raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

            if destination is None:
                raise CompilerError("Unsupported expression without assignment!", context)

            # Absolute value calculation.
            destination_type = types[call]
            if destination_type.size == 1:
                func = "abs8"
            elif destination_type.size == 2:
                func = "abs16"
            elif destination_type.size == 4:
                func = "abs32"
            else:
                raise Exception("Logic error, unknown destination size!")

            if not destination_type.is_integer:
                raise CompilerError("The builtin function abs() only works on integers!", context)

            # If it's already unsigned, don't do anything to it.
            if destination_type.is_unsigned:
                return generate_expr_internal(args[0].value, destination, types, stack, clobbers, allocations, refs, local_consts, context.wrap(args[0].value))
            else:
                return generate_function_call_internal(
                    create_call(func, [args[0].value]),
                    destination,
                    types,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context,
                )

        elif function_prototype.name == "bool":
            if len(args) != 1 or len(arg_types) != 1:
                raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

            if destination is None:
                raise CompilerError("Unsupported expression without assignment!", context)

            # Cast from whatever data type to string, so we must handle this on a case by case basis.
            expr = args[0].value

            if types[expr].is_bool:
                # We're done, this is already a boolean.
                return generate_expr_internal(expr, destination, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

            elif types[expr].is_string:
                # Need to see if this string is an empty string or not.
                compiled = Sections()

                # Evaluate the expression itself.
                expr_dest = expr_temp_name()
                stack.alloc(StackVar(expr_dest, CoreType("str", const=True), initialized=True))
                compiled += generate_expr_internal(expr, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                clobbers.add("SPC")
                clobbers.add("A")

                # Now, dereference the string and find out if it's an empty string or not.
                compiled += generate_move_to(expr_dest, stack, clobbers, context, offset=1)
                compiled.append_code("  POP SPC")
                stack.move(-2)
                compiled.code += comment_stack(stack)

                # Grab the first character, either it's a null byte or it's not.
                compiled.append_code("  SWAP PC, SPC")
                compiled.append_code("  LOAD A")
                compiled.append_code("  SWAP PC, SPC")

                compiled.append_code("  ADDI 0")
                compiled.append_code("  LOADI 0x00")
                compiled.append_code("  SKIPIF ZF")
                compiled.append_code("  INV")

                if not is_register_destination(destination):
                    compiled += generate_move_to(destination, stack, clobbers, context)
                    compiled.append_code("  STORE A")
                    stack.init(destination)

                return compiled

            elif types[expr].size == 1:
                compiled = Sections()

                if types[expr].is_char:
                    dest_loc = "register(A, char)"
                elif types[expr].is_integer:
                    dest_loc = "register(A, uint8)" if types[expr].is_unsigned else "register(A, int8)"
                else:
                    raise Exception("Logic error, unexpected type for 1 byte type!")

                # Evaluate the expression itself.
                clobbers.add("A")
                compiled += generate_expr_internal(expr, dest_loc, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                # Now, figure out if the expression was nonzero (boolean True) or zero (boolean False)
                compiled.append_code("  ADDI 0")
                compiled.append_code("  LOADI 0x00")
                compiled.append_code("  SKIPIF ZF")
                compiled.append_code("  INV")

                if not is_register_destination(destination):
                    compiled += generate_move_to(destination, stack, clobbers, context)
                    compiled.append_code("  STORE A")
                    stack.init(destination)

                return compiled

            elif types[expr].size == 2:
                compiled = Sections()

                # Evaluate the expression itself.
                expr_dest = expr_temp_name()
                stack.alloc(StackVar(expr_dest, types[expr], initialized=True))
                compiled += generate_expr_internal(expr, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                # Now, figure out if the expression was nonzero (boolean True) or zero (boolean False)
                compiled += generate_move_to(expr_dest, stack, clobbers, context, offset=1)

                end_conversion = local_label_name("end_conversion")

                # First byte check with short circuiting for non-zero.
                clobbers.add("A")
                compiled.append_code("  LOAD A")
                compiled.append_code("  INCPC")
                compiled.append_code("  ADDI 0")
                compiled.append_code("  LOADI 0xFF")
                compiled.append_code(f"  JRINZ {end_conversion}")

                # Second byte check.
                compiled.append_code("  LOAD A")
                compiled.append_code("  ADDI 0")
                compiled.append_code("  LOADI 0x00")
                compiled.append_code("  SKIPIF ZF")
                compiled.append_code("  INV")
                compiled.append_code(f"{end_conversion}:")

                stack.move(-1)
                stack.free(expr_dest)

                if not is_register_destination(destination):
                    compiled += generate_move_to(destination, stack, clobbers, context)
                    compiled.append_code("  STORE A")
                    stack.init(destination)

                return compiled

            elif types[expr].size == 4:
                compiled = Sections()

                # Evaluate the expression itself.
                expr_dest = expr_temp_name()
                stack.alloc(StackVar(expr_dest, types[expr], initialized=True))
                compiled += generate_expr_internal(expr, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                # Now, figure out if the expression was nonzero (boolean True) or zero (boolean False)
                compiled += generate_move_to(expr_dest, stack, clobbers, context, offset=3)

                end_conversion_first_byte = local_label_name("end_conversion_first_byte")
                end_conversion_second_byte = local_label_name("end_conversion_second_byte")
                end_conversion = local_label_name("end_conversion")

                # First byte check with short circuiting for non-zero.
                clobbers.add("A")
                compiled.append_code("  LOAD A")
                compiled.append_code("  INCPC")
                compiled.append_code("  ADDI 0")
                compiled.append_code("  LOADI 0xFF")
                compiled.append_code(f"  JRINZ {end_conversion_first_byte}")

                # Second byte check with short circuiting for non-zero.
                compiled.append_code("  LOAD A")
                compiled.append_code("  INCPC")
                compiled.append_code("  ADDI 0")
                compiled.append_code("  LOADI 0xFF")
                compiled.append_code(f"  JRINZ {end_conversion_second_byte}")

                # Third byte check with short circuiting for non-zero.
                compiled.append_code("  LOAD A")
                compiled.append_code("  INCPC")
                compiled.append_code("  ADDI 0")
                compiled.append_code("  LOADI 0xFF")
                compiled.append_code(f"  JRINZ {end_conversion}")

                # Fourth byte check.
                compiled.append_code("  LOAD A")
                compiled.append_code("  ADDI 0")
                compiled.append_code("  LOADI 0x00")
                compiled.append_code("  SKIPIF ZF")
                compiled.append_code("  INV")
                compiled.append_code(f"  JRI {end_conversion}")

                compiled.append_code(f"{end_conversion_first_byte}:")
                compiled.append_code("  INCPC")
                compiled.append_code(f"{end_conversion_second_byte}:")
                compiled.append_code("  INCPC")
                compiled.append_code(f"{end_conversion}:")

                stack.move(-3)
                stack.free(expr_dest)

                if not is_register_destination(destination):
                    compiled += generate_move_to(destination, stack, clobbers, context)
                    compiled.append_code("  STORE A")
                    stack.init(destination)

                return compiled

            else:
                raise Exception(f"Logic error, unexpected type {types[expr]} in bool() evaluation!")

        elif function_prototype.name == "chr":
            if len(args) != 1 or len(arg_types) != 1:
                raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

            if destination is None:
                raise CompilerError("Unsupported expression without assignment!", context)

            # Cast from integer to char, but the 8-bit case is simple.
            expr = args[0].value

            if not types[expr].is_integer:
                raise CompilerError("Unsupported conversion from {types[expr].type} to character!", context)

            if types[expr].size == 1:
                # Simply evaluate the expression into the destination directly, but pretend that the destination
                # is an integer instead of a character.
                compiled = Sections()

                # Evaluate the expression itself.
                dest_loc = "register(A, uint8)" if types[expr].is_unsigned else "register(A, int8)"
                clobbers.add("A")
                compiled += generate_expr_internal(expr, dest_loc, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                if not is_register_destination(destination):
                    compiled += generate_move_to(destination, stack, clobbers, context)
                    compiled.append_code("  STORE A")
                    stack.init(destination)

                return compiled

            elif types[expr].size in {2, 4}:
                compiled = Sections()

                # Evaluate the expression itself.
                expr_dest = expr_temp_name()
                stack.alloc(StackVar(expr_dest, types[expr], initialized=True))
                compiled += generate_expr_internal(expr, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                # Now, load the bottom byte into the A register to return it.
                compiled += generate_move_to(expr_dest, stack, clobbers, context)
                compiled.append_code("  LOAD A")
                stack.free(expr_dest)

                if not is_register_destination(destination):
                    clobbers.add("A")
                    compiled += generate_move_to(destination, stack, clobbers, context)
                    compiled.append_code("  STORE A")
                    stack.init(destination)

                return compiled

            else:
                raise Exception(f"Logic error, unexpected type {types[expr]} in chr() evaluation!")

        elif function_prototype.name == "ord":
            if len(args) != 1 or len(arg_types) != 1:
                raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

            if destination is None:
                raise CompilerError("Unsupported expression without assignment!", context)

            # Cast from integer to char, but the 8-bit case is simple.
            expr = args[0].value

            if not types[expr].is_char:
                raise CompilerError("Unsupported conversion from {types[expr].type} to integer!", context)

            # Figure out what to do based on the destination type.
            destination_type = stack.typeof(destination)
            if destination_type is None:
                raise Exception("Logic error, couldn't determine destination type for ord!")

            # Simply evaluate the expression into the destination directly, but pretend that the destination
            # is a character instead of an integer.
            compiled = Sections()

            # Evaluate the expression itself.
            clobbers.add("A")
            compiled += generate_expr_internal(expr, "register(A, char)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

            # Intentionally zero-sign in the signed int16/int32 cases below since we know that the ord(some_char) should never be negative.
            if destination_type.size == 1:
                if not is_register_destination(destination):
                    compiled += generate_move_to(destination, stack, clobbers, context)
                    compiled.append_code("  STORE A")
                    stack.init(destination)

                return compiled

            elif destination_type.size == 2:
                compiled += generate_move_to(destination, stack, clobbers, context)
                compiled.append_code("  STORE A")
                compiled.append_code("  INCPC")
                compiled.append_code("  STOREI 0")
                stack.move(-1)
                stack.init(destination)

                return compiled

            elif destination_type.size == 4:
                compiled += generate_move_to(destination, stack, clobbers, context)
                compiled.append_code("  STORE A")
                compiled.append_code("  INCPC")
                compiled.append_code("  LOADI 0")
                compiled.append_code("  STORE A")
                compiled.append_code("  INCPC")
                compiled.append_code("  STORE A")
                compiled.append_code("  INCPC")
                compiled.append_code("  STORE A")
                stack.move(-3)
                stack.init(destination)

                return compiled

            else:
                raise Exception(f"Logic error, unexpected type {destination_type} in ord() evaluation!")

        elif function_prototype.name == "int":
            if len(args) != 1 or len(arg_types) != 1:
                raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

            if destination is None:
                raise CompilerError("Unsupported expression without assignment!", context)

            # This could be a passthrough, in the case of an integer input, undefined in case of char, a simple
            # cast in case of bool, and an atoi call in case of a string.
            expr = args[0].value

            if types[expr].is_integer:
                compiled = Sections()
                compiled += generate_expr_internal(expr, destination, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))
                return compiled

            elif types[expr].is_char:
                raise CompilerError("Unsupported conversion from {types[expr].type} to integer!", context)

            elif types[expr].is_bool:
                clobbers.add("A")
                compiled = Sections()
                compiled += generate_expr_internal(expr, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                # Set to 0 or 1 like python does for boolean values. Load immediate is a 2 byte instruction so we can't
                # SKIPIF it. However, we know that booleans in our system are either 0x00 or 0xFF so we can set to 0 by
                # leaving A alone, and set to 1 by adding 2 to 255.
                compiled.append_code("  ADDI 0")
                compiled.append_code("  SKIPIF ZF")
                compiled.append_code("  ADDI 2")

                if not is_register_destination(destination):
                    compiled += generate_move_to(destination, stack, clobbers, context)
                    compiled.append_code("  STORE A")
                    stack.init(destination)

                return compiled

            elif types[expr].is_string:
                destination_type = stack.typeof(destination)
                if destination_type is None:
                    raise Exception("Logic error, couldn't determine destination type for ord!")

                if not destination_type.is_integer:
                    raise Exception("Logic error, type checker phase should have guaranteed this!")

                if destination_type.size == 1:
                    func = "atoi8"
                elif destination_type.size == 2:
                    func = "atoi16"
                elif destination_type.size == 4:
                    func = "atoi32"
                else:
                    raise Exception("Logic error, unsupported destination size for int()!")

                return generate_function_call_internal(
                    create_call(func, [args[0].value]),
                    destination,
                    types,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context,
                )

            else:
                raise Exception(f"Logic error, unexpected type {types[expr]} in int() evaluation!")

        else:
            raise Exception(f"Logic error, attempted to generate unsupported internal function {function_prototype.name}!")

    else:
        return generate_function_call_internal(call, destination, types, stack, clobbers, allocations, refs, local_consts, context)


__comment_ref_count: int = 0


def comment_ref() -> str:
    global __comment_ref_count
    __comment_ref_count += 1
    return f"##comment_ref_{__comment_ref_count}##"


__expr_global_count: int = 0


def expr_temp_name() -> str:
    global __expr_global_count
    __expr_global_count += 1
    return f"builtin(expr_temp_{__expr_global_count})"


__local_label_count: int = 0


def local_label_name(label: str = "") -> str:
    global __local_label_count
    __local_label_count += 1

    if label:
        label = f"_{label}_"
    else:
        label = "_"

    return f"local{label}{__local_label_count}"


__saved_counts: List[Tuple[int, int]] = []


def push_names() -> None:
    __saved_counts.append((__expr_global_count, __local_label_count))


def pop_names() -> None:
    if not __saved_counts:
        raise Exception("Logic error, popping saved counts without a push!")

    global __expr_global_count
    global __local_label_count
    __expr_global_count = __saved_counts[-1][0]
    __local_label_count = __saved_counts[-1][1]
    __saved_counts.pop()


def expr_integer_type(size: int) -> CoreType:
    if size == 1:
        return CoreType("int8")
    elif size == 2:
        return CoreType("int16")
    elif size == 4:
        return CoreType("int32")
    else:
        raise Exception("Logic error, unrecognized integer size!")


def generate_local_storage_alloc(
    destination: str,
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    context: Context,
) -> Sections:
    compiled = Sections()

    dest_type = stack.typeof(destination)
    if dest_type is None:
        raise Exception("Logic error, cannot find destination to allocate local storage for!")

    if not dest_type.is_array:
        if destination == "builtin(retval)":
            raise CompilerError("Non-constant string return requires a length", context)
        else:
            raise CompilerError("Non-constant local strings require a length", context)

    local_destination_storage = stack.labelof(destination)
    if local_destination_storage is None:
        raise Exception("Logic error, couldn't get local storage for string!")

    requested_length = dest_type.length or MAX_STRING_LENGTH
    if local_destination_storage in allocations:
        if allocations[local_destination_storage] != requested_length:
            raise Exception("Logic error, re-allocation of local storage with different size!")
    else:
        compiled.append_data(f"{local_destination_storage}:")
        compiled.append_data(f"  .pad {requested_length}")

    # We only clobber the A register with the string init macro.
    clobbers.add("A")

    compiled += generate_move_to(destination, stack, clobbers, context, offset=-1)
    compiled.append_code(f"  PUSHADDR {local_destination_storage}")
    stack.location += 2

    # Remember that we did this so we don't duplicate the allocation if we're conditionally allocating,
    # such as when an unallocated variable gets assigned two values in an if/else conditional.
    allocations[local_destination_storage] = requested_length

    return compiled


def generate_variable_lookup(
    source: str,
    destination: Optional[str],
    stack: Stack,
    types: Dict[cst.CSTNode, CoreType],
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    compiled = Sections()

    if destination is not None and is_register_destination(destination):
        # Just need to load A with the value, which should always be the lowest 8 bits of any variable.
        if stack.absfind(source) is None:
            if (global_var := global_by_name(refs, source)) is not None:
                if not (global_var.type.is_bool or global_var.type.is_char or global_var.type.is_integer):
                    raise CompilerError("Unsupported destination for non-integer assignment", context)

                # We clobber the SPC to be able to point at the variable.
                clobbers.add("A")
                clobbers.add("SPC")

                compiled.append_code("  SWAP PC, SPC")
                compiled.append_code(f"  SETPC {global_var.name}, {global_var.type.size - 1}")
                compiled.append_code("  LOAD A")
                compiled.append_code("  SWAP PC, SPC")

            else:
                raise CompilerError(f"Undefined variable reference to {source!r}", context)

        else:
            source_type = stack.typeof(source)
            if not source_type or not stack.initof(source):
                raise CompilerError(f"Use of uninitialized variable {source!r}", context)

            if not (source_type.is_bool or source_type.is_char or source_type.is_integer):
                raise CompilerError("Unsupported destination for non-integer assignment", context)

            compiled += generate_move_to(source, stack, clobbers, context)
            compiled.append_code("  LOAD A")

    elif stack.absfind(source) is None and (global_var := global_by_name(refs, source)) is not None:
        # Global variable lookup.
        if destination is None:
            if global_var.type.is_string:
                raise CompilerError("Unsupported no-effect string lookup", context)

            # Just load from each position in the global variable, to trigger any memory read side effects
            # in any hardware we're talking to.
            clobbers.add("SPC")
            clobbers.add("A")

            # First, we need to set the SPC to our variable pointer, which clobbers A.
            compiled.append_code("  SWAP PC, SPC")
            compiled.append_code(f"  SETPC {global_var.name}")

            for i in range(global_var.type.size):
                # Now, just trigger loads for each byte in the variable.
                if i == 0:
                    compiled.append_code("  LOAD A")
                else:
                    compiled.append_code("  INCPC")
                    compiled.append_code("  LOAD A")

            compiled.append_code("  SWAP PC, SPC")
        else:
            dest_type = stack.typeof(destination)
            if dest_type is None:
                raise Exception("Logic error, cannot find destination to copy variable value to!")

            if dest_type.is_string:
                if not global_var.type.is_string:
                    raise CompilerError("Unsupported string assignment to non-string expression", context)
                if not dest_type.const and global_var.type.const:
                    # We need to allocate locally and strcpy over.
                    if not stack.initof(destination):
                        compiled += generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                        # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                        stack.init(destination)

                    # Now, set up the stack for a strcpy operation, to initialize the local data with
                    # a copy of the constant we're initializing from.
                    if stack[-1].name != destination:
                        # In order to ensure that it's possible to do stack math on this value, locate it in
                        # a temporary location for the time being if the destination isn't the top of the stack.
                        lhs_dest = expr_temp_name()
                        stack.alloc(StackVar(lhs_dest, CoreType("str"), initialized=True))

                        compiled += generate_memcpy_stackvars(lhs_dest, destination, stack, clobbers, context)
                    else:
                        # Safe to put first parameter in the top of the stack where it already is useful for math.
                        lhs_dest = destination

                    # Now, point at it.
                    clobbers.add("A")

                    rhs_dest = expr_temp_name()
                    stack.alloc(StackVar(rhs_dest, CoreType("str"), initialized=True))
                    compiled += generate_move_to(rhs_dest, stack, clobbers, context, offset=-1)
                    compiled.append_code(f"  PUSHADDR {global_var.name}")
                    stack.location += 2

                    # Now call strcpy.
                    compiled += generate_function_call_internal(
                        create_call("strcpy", [UnvalidatedName(lhs_dest), UnvalidatedName(rhs_dest)]),
                        None,
                        types,
                        stack,
                        clobbers,
                        allocations,
                        refs,
                        local_consts,
                        context,
                    )

                    # Finally, free the stack.
                    stack.free(rhs_dest)
                    if lhs_dest != destination:
                        stack.free(lhs_dest)

                else:
                    # We only clobber the A register with the macro.
                    clobbers.add("A")

                    compiled += generate_move_to(destination, stack, clobbers, context, offset=-1)
                    compiled.append_code(f"  PUSHADDR {global_var.name}")
                    stack.location += 2

            else:
                # We clobber the SPC to be able to point at the variable. We clobber the A register for copies.
                clobbers.add("SPC")
                clobbers.add("A")

                if global_var.type.size == dest_type.size:
                    # Direct copy from source stack to destination stack.
                    for i in range(global_var.type.size):
                        # First, we need to set the SPC to our variable pointer, which clobbers A.
                        if i == 0:
                            compiled.append_code("  SWAP PC, SPC")
                            compiled.append_code(f"  SETPC {global_var.name}, {global_var.type.size - 1}")
                            compiled.append_code("  LOAD A")
                            compiled.append_code("  SWAP PC, SPC")
                        else:
                            compiled.append_code("  SWAP PC, SPC")
                            compiled.append_code("  DECPC")
                            compiled.append_code("  LOAD A")
                            compiled.append_code("  SWAP PC, SPC")

                        compiled += generate_move_to(destination, stack, clobbers, context, offset=i)
                        compiled.append_code("  STORE A")

                elif global_var.type.size > dest_type.size:
                    # Copy, but with the destination size in mind, which should grab only the lower bits of the source.
                    for i in range(dest_type.size):
                        # First, we need to set the SPC to our variable pointer, which clobbers A.
                        if i == 0:
                            compiled.append_code("  SWAP PC, SPC")
                            compiled.append_code(f"  SETPC {global_var.name}, {global_var.type.size - 1}")
                            compiled.append_code("  LOAD A")
                            compiled.append_code("  SWAP PC, SPC")
                        else:
                            compiled.append_code("  SWAP PC, SPC")
                            compiled.append_code("  DECPC")
                            compiled.append_code("  LOAD A")
                            compiled.append_code("  SWAP PC, SPC")

                        compiled += generate_move_to(destination, stack, clobbers, context, offset=i)
                        compiled.append_code("  STORE A")

                else:
                    # Copy, but with either sign extension or zero extension for the missing upper bytes.
                    dest_type = stack.typeof(destination)
                    dest_loc = stack.absfind(destination)
                    if dest_type is None or dest_loc is None:
                        raise Exception("Logic error, cannot find destination to copy variable value to!")

                    if dest_type.is_unsigned:
                        # We always zero-extend unsigned types.
                        compiled.append_code("  LOADI 0")
                    else:
                        # First, go to the high byte and figure out if it needs to be zero or one extended.
                        compiled.append_code("  SWAP PC, SPC")
                        compiled.append_code(f"  SETPC {global_var.name}")
                        compiled.append_code("  LOAD A")
                        compiled.append_code("  SWAP PC, SPC")
                        compiled.append_code("  SHL")
                        compiled.append_code("  LOADI 0")
                        compiled.append_code("  SKIPIF !CF")
                        compiled.append_code("  INV")

                    extend_amount = dest_type.size - global_var.type.size
                    for pos in range(extend_amount):
                        actual_pos = pos + dest_loc + global_var.type.size

                        move_amt = stack.diff(actual_pos)
                        compiled += generate_move_by("seeking sign extend byte", move_amt, stack, clobbers, context)
                        compiled.append_code("  STORE A")

                    # Need to copy the whole source, but to the correct location in the destination.
                    for i in range(global_var.type.size):
                        # First, we need to set the SPC to our variable pointer, which clobbers A.
                        if i == 0:
                            compiled.append_code("  SWAP PC, SPC")
                            # We set this above for the case where we need to check for sign extension.
                            # That doesn't happen for unsigned integers, so we need to set the PC here.
                            if dest_type.is_unsigned:
                                compiled.append_code(f"  SETPC {global_var.name}")
                            compiled.append_code("  LOAD A")
                            compiled.append_code("  SWAP PC, SPC")
                        else:
                            compiled.append_code("  SWAP PC, SPC")
                            compiled.append_code("  INCPC")
                            compiled.append_code("  LOAD A")
                            compiled.append_code("  SWAP PC, SPC")

                        actual_pos = (dest_loc + global_var.type.size) - (i + 1)

                        move_amt = stack.diff(actual_pos)
                        compiled += generate_move_by("seeking copy byte", move_amt, stack, clobbers, context)
                        compiled.append_code("  STORE A")

    else:
        if destination is None:
            raise CompilerError("Unsupported expression without assignment!", context)
        if not stack.initof(source):
            raise CompilerError(f"Use of uninitialized variable {source!r}", context)

        source_loc = stack.absfind(source)
        source_type = stack.typeof(source)
        dest_loc = stack.absfind(destination)
        dest_type = stack.typeof(destination)
        if source_loc is None or source_type is None:
            raise CompilerError(f"Undefined variable reference to {source!r}", context)
        if dest_loc is None or dest_type is None:
            raise Exception("Logic error, cannot find destination to copy variable value to!")

        if dest_type.is_string and not (source_type.is_string or source_type.is_char):
            raise CompilerError("Unsupported non-string expression in string assignment", context)

        if dest_type.is_string and source_type.is_char:
            # Regardless of whether the destination is constant, we need to allocate space for it.
            if not stack.initof(destination):
                compiled += generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                stack.init(destination)

            # Initializing this requires us to clobber the SPC and A.
            clobbers.add("SPC")
            clobbers.add("A")

            # Grab the character value itself.
            compiled += generate_move_to(source, stack, clobbers, context)
            compiled.append_code("  LOAD A")

            # Set up the SPC to point at the string.
            compiled += generate_move_to(destination, stack, clobbers, context, offset=1)
            compiled.append_code("  POP SPC")
            stack.move(-2)
            compiled.code += comment_stack(stack)

            # Set the character value to the string, null-terminate.
            compiled.append_code("  SWAP PC, SPC")
            compiled.append_code("  STORE A")
            compiled.append_code("  INCPC")
            compiled.append_code("  STOREI 0")
            compiled.append_code("  SWAP PC, SPC")

        elif dest_type.is_string and not dest_type.const and destination != "builtin(retval)":
            # We need to allocate locally and strcpy over.
            if not stack.initof(destination):
                compiled += generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                stack.init(destination)

            # Now, set up the stack for a strcpy operation, to initialize the local data with
            # a copy of the constant we're initializing from.
            if stack[-1].name != destination:
                # In order to ensure that it's possible to do stack math on this value, locate it in
                # a temporary location for the time being if the destination isn't the top of the stack.
                lhs_dest = expr_temp_name()
                stack.alloc(StackVar(lhs_dest, CoreType("str"), initialized=True))

                compiled += generate_memcpy_stackvars(lhs_dest, destination, stack, clobbers, context)
            else:
                # Safe to put first parameter in the top of the stack where it already is useful for math.
                lhs_dest = destination

            # Now, point at it.
            rhs_dest = expr_temp_name()
            stack.alloc(StackVar(rhs_dest, CoreType("str"), initialized=True))

            compiled += generate_memcpy_stackvars(rhs_dest, source, stack, clobbers, context)

            # Now call strcpy.
            compiled += generate_function_call_internal(
                create_call("strcpy", [UnvalidatedName(lhs_dest), UnvalidatedName(rhs_dest)]),
                None,
                types,
                stack,
                clobbers,
                allocations,
                refs,
                local_consts,
                context,
            )

            # Finally, free the stack.
            stack.free(rhs_dest)
            if lhs_dest != destination:
                stack.free(lhs_dest)

        elif source_type.size == dest_type.size:
            # Direct copy from source stack to destination stack.
            compiled += generate_memcpy_stackvars(destination, source, stack, clobbers, context)
        elif source_type.size > dest_type.size:
            # Copy, but with the destination size in mind, which should grab only the lower bits of the source.
            compiled += generate_memcpy_locations(source_loc, dest_loc, dest_type.size, stack, clobbers, context)
        else:
            # We need to sign extend the top bit of the top byte for negative numbers, which requires the A register.
            clobbers.add("A")

            dest_type = stack.typeof(destination)
            if dest_type is None:
                raise Exception("Logic error, cannot find destination to copy variable value to!")
            if dest_type.is_unsigned:
                # We always zero-extend unsigned types.
                compiled.append_code("  LOADI 0")
            else:
                # First, go to the high byte and figure out if it needs to be zero or one extended.
                move_amt = stack.diff(source_loc + (source_type.size - 1))
                compiled += generate_move_by("seeking {source}", move_amt, stack, clobbers, context)
                compiled.append_code("  LOAD A")
                compiled.append_code("  SHL")
                compiled.append_code("  LOADI 0")
                compiled.append_code("  SKIPIF !CF")
                compiled.append_code("  INV")

            for pos in range(dest_type.size - source_type.size):
                actual_pos = pos + dest_loc + source_type.size

                move_amt = stack.diff(actual_pos)
                compiled += generate_move_by("seeking sign extend byte", move_amt, stack, clobbers, context)
                compiled.append_code("  STORE A")

            # Need to copy the whole thing, and then zero out the top bytes we didn't touch.
            compiled += generate_memcpy_locations(source_loc, dest_loc, source_type.size, stack, clobbers, context)

    return compiled


def generate_unary_expr(
    expression: cst.UnaryOperation,
    destination: str,
    types: Dict[cst.CSTNode, CoreType],
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    compiled = Sections()

    destination_size = stack.sizeof(destination)
    destination_type = stack.typeof(destination)
    if destination_size is None:
        raise Exception("Logic error, could not calculate size of destination!")
    if destination_type is None:
        raise Exception("Logic error, could not calculate type of destination!")

    if isinstance(expression.operator, (cst.Minus, cst.BitInvert)):
        if not destination_type.is_integer:
            raise CompilerError(f"Unsupported type {destination_type.type} for integer expression!", context)

        if destination_size == 1:
            if is_register_destination(destination) or stack[-1].name != destination:
                # In order to ensure that it's possible to negate this value, locate the rest of the expression
                # in a temporary location.
                internal_dest = expr_temp_name()
                stack.alloc(StackVar(internal_dest, expr_integer_type(destination_size)))
            else:
                # Safe to put the expression evaluation in our destination because we're just going to negate it.
                internal_dest = destination

            compiled += generate_expr_internal(expression.expression, internal_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.expression))

            # Negation clobbers the A register, since it is the accumulator.
            clobbers.add("A")

            # Move to the parameter and negate it.
            compiled += generate_move_to(internal_dest, stack, clobbers, context)
            compiled.append_code("  LOAD A")

            if isinstance(expression.operator, cst.Minus):
                compiled.append_code("  NEG")
            elif isinstance(expression.operator, cst.BitInvert):
                compiled.append_code("  INV")
            else:
                raise CompilerError("Unsupported unary operation {expression}", context)

            # This call puts the result in a, so check if that's what we want.
            if is_register_destination(destination):
                stack.free(internal_dest)
            else:
                compiled += generate_move_to(destination, stack, clobbers, context)
                compiled.append_code("  STORE A")
                if internal_dest != destination:
                    stack.free(internal_dest)
        elif destination_size in {2, 4}:
            # Calculate the expression inside the negation here, so we can send the temporary name to the function call
            # and trigger its optimized case.
            if stack[-1].name != destination:
                internal_dest = expr_temp_name()
                stack.alloc(StackVar(internal_dest, expr_integer_type(destination_size)))
            else:
                internal_dest = destination

            compiled += generate_expr_internal(expression.expression, internal_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.expression))

            if isinstance(expression.operator, cst.Minus):
                # Using the neg16 or neg32 function that's part of our stdlib.
                function = "neg16" if destination_size == 2 else "neg32"
                compiled += generate_function_call_internal(
                    create_call(
                        function,
                        [UnvalidatedName(internal_dest)],
                    ),
                    destination,
                    types,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context.wrap(expression),
                )
            elif isinstance(expression.operator, cst.BitInvert):
                # Move to the right spot on the stack and then perform the operation on the two numbers.
                # Since bitwise operations are independent we can just do this in a loop.
                if stack_is_at(internal_dest, stack, offset=destination_size - 1):
                    # We're already at the top of the stack, generate the load/inv/store loop downwards
                    # instead of upwards to shave off a move instruction.
                    def actual_neg_offset(offset: int) -> int:
                        return (destination_size - offset) - 1
                else:
                    # We're anywhere else in the stack, so it costs us no unnecessary move instructions
                    # to perform the first move.
                    def actual_neg_offset(offset: int) -> int:
                        return offset

                for offset in range(destination_size):
                    compiled += generate_move_to(internal_dest, stack, clobbers, context, offset=actual_neg_offset(offset))
                    compiled.append_code("  LOAD A")
                    compiled.append_code("  INV")
                    compiled += generate_move_to(destination, stack, clobbers, context, offset=actual_neg_offset(offset))
                    compiled.append_code("  STORE A")

            else:
                raise CompilerError("Unsupported unary operation {expression}", context)

            if internal_dest != destination:
                stack.free(internal_dest)

        else:
            # We don't support negation of this type.
            raise CompilerError("Cannot negate expression with destination size {destination_size}", context)

    elif isinstance(expression.operator, cst.Not):
        if destination_size != 1 or not destination_type.is_bool:
            raise CompilerError("Cannot assign boolean expression result to non-bool", context)

        # This one is simple, evaluate the operation and then invert it.
        clobbers.add("A")

        compiled += generate_expr_internal(expression.expression, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context)
        compiled.append_code("  INV")

        if not is_register_destination(destination):
            compiled += generate_move_to(destination, stack, clobbers, context)
            compiled.append_code("  STORE A")

    else:
        # TODO: Handle Plus (no-op, just call with the expression value).
        raise CompilerError(f"Unsupported unary operation {expression}", context)

    return compiled


def generate_binary_expr(
    expression: cst.BinaryOperation,
    destination: str,
    types: Dict[cst.CSTNode, CoreType],
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    compiled = Sections()

    destination_size = stack.sizeof(destination)
    if destination_size is None:
        raise Exception("Logic error, could not calculate size of destination!")
    destination_type = stack.typeof(destination)
    if destination_type is None:
        raise Exception("Logic error, could not calculate type of destination!")

    # First, determine if this is string concatenation.
    if destination_type.is_string:
        if not isinstance(expression.operator, cst.Add):
            raise CompilerError("Unsupported binary expression with string destination", context)

        if not types[expression.left].is_string:
            raise Exception("Logic error, somehow assigning to string without the LHS being a string!")

        if types[expression.right].is_string:
            # First, generate the left hand side of the expression.
            if stack[-1].name != destination:
                lhs_dest = expr_temp_name()
                stack.alloc(StackVar(lhs_dest, CoreType("str", length=destination_type.length)))
            else:
                lhs_dest = destination

            compiled += generate_expr_internal(expression.left, lhs_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.left))

            # Now, again with the right!
            rhs_dest = expr_temp_name()
            stack.alloc(StackVar(rhs_dest, CoreType("str", const=True)))
            compiled += generate_expr_internal(expression.right, rhs_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.right))

            # Now, call strcat to concatenate the two together!
            compiled += generate_function_call_internal(
                create_call(
                    "strcat",
                    [UnvalidatedName(lhs_dest), UnvalidatedName(rhs_dest)]
                ),
                None,
                types,
                stack,
                clobbers,
                allocations,
                refs,
                local_consts,
                context.wrap(expression),
            )

            # No longer needed since we concatenated it.
            stack.free(rhs_dest)

            # Now, copy the destination pointer if needed.
            if lhs_dest != destination:
                compiled += generate_memcpy_stackvars(destination, lhs_dest, stack, clobbers, context)

            # Now that we copied this to the destination, this is useless.
            if lhs_dest != destination:
                stack.free(lhs_dest)

        elif types[expression.right].is_char:
            # First, generate the left hand side of the expression.
            compiled += generate_expr_internal(expression.left, destination, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.left))

            # Now, generate the right hand side so we can assign it to the end of the string.
            clobbers.add("A")
            compiled += generate_expr_internal(expression.right, "register(A, char)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.right))

            # Save that character, since we need to use the A register to advance until the null pointer.
            clobbers.add("V")
            compiled.append_code("  MOV A, V")

            # Need to clobber the SPC to move to that location.
            clobbers.add("SPC")
            compiled += generate_move_to(destination, stack, clobbers, context, offset=1)
            compiled.append_code("  POP SPC")
            stack.move(-2)
            compiled.code += comment_stack(stack)

            advance_top = local_label_name("advance_top")
            advance_bottom = local_label_name("advance_bottom")

            # Swap over so we can check the string one byte at a time.
            compiled.append_code("  SWAP PC, SPC")

            # Loop through, looking for the null termination character.
            compiled.append_code(f"{advance_top}:")
            compiled.append_code("  LOAD A")
            compiled.append_code("  ADDI 0")
            compiled.append_code(f"  JRIZ {advance_bottom}")
            compiled.append_code("  INCPC")
            compiled.append_code(f"  JRI {advance_top}")
            compiled.append_code(f"{advance_bottom}:")
            compiled.append_code("  STORE V")
            compiled.append_code("  INCPC")
            compiled.append_code("  STOREI 0")
            compiled.append_code("  SWAP PC, SPC")

        else:
            raise CompilerError(f"Unsupported string concatenation with {types[expression.right].type}", context)

    else:
        if is_register_destination(destination) or stack[-1].name != destination:
            # In order to ensure that it's possible to do stack math on this value, locate it in
            # a temporary location for the time being if the destination isn't the top of the stack.
            lhs_dest = expr_temp_name()
            stack.alloc(StackVar(lhs_dest, expr_integer_type(destination_size)))
        else:
            # Safe to put first parameter in the top of the stack where it already is useful for math.
            lhs_dest = destination

        compiled += generate_expr_internal(expression.left, lhs_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.left))

        # Now, get the second parameter onto the stack in the right spot.
        rhs_dest = expr_temp_name()
        if isinstance(expression.operator, (cst.LeftShift, cst.RightShift)):
            stack.alloc(StackVar(rhs_dest, CoreType("uint8")))
        else:
            stack.alloc(StackVar(rhs_dest, expr_integer_type(destination_size)))
        compiled += generate_expr_internal(expression.right, rhs_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.right))

        # Now, perform some math of matics!
        if destination_size == 1:
            if isinstance(expression.operator, cst.Subtract):
                if not destination_type.is_integer:
                    raise CompilerError(f"Unsupported type {destination_type.type} for integer expression!", context)

                if not is_register_destination(destination):
                    # Subtracting clobbers the A register, since it is the accumulator.
                    clobbers.add("A")

                # Move to the second parameter and negate it.
                compiled += generate_move_to(rhs_dest, stack, clobbers, context)
                compiled.append_code("  LOAD A")
                compiled.append_code("  NEG")

                # Move to the right spot on the stack to add to the negated right hand side.
                compiled += generate_move_to(lhs_dest, stack, clobbers, context)
                compiled.append_code("  ADD")

            elif isinstance(expression.operator, (cst.Add, cst.BitAnd, cst.BitOr, cst.BitXor)):
                if not destination_type.is_integer:
                    raise CompilerError(f"Unsupported type {destination_type.type} for integer expression!", context)

                if not is_register_destination(destination):
                    # Adding clobbers the A register, since it is the accumulator.
                    clobbers.add("A")

                # Move to the right spot on the stack and then add the two numbers.
                compiled += generate_move_to(rhs_dest, stack, clobbers, context)
                compiled.append_code("  LOAD A")
                compiled += generate_move_to(lhs_dest, stack, clobbers, context)

                if isinstance(expression.operator, cst.Add):
                    compiled.append_code("  ADD")
                elif isinstance(expression.operator, cst.BitAnd):
                    compiled.append_code("  AND")
                elif isinstance(expression.operator, cst.BitOr):
                    compiled.append_code("  OR")
                elif isinstance(expression.operator, cst.BitXor):
                    compiled.append_code("  XOR")
                else:
                    raise Exception("Logic error, unexpected operator {expression.operator)}")

            elif isinstance(expression.operator, (cst.Multiply, cst.LeftShift, cst.RightShift)):
                if not destination_type.is_integer:
                    raise CompilerError(f"Unsupported type {destination_type.type} for integer expression!", context)

                if isinstance(expression.operator, cst.Multiply):
                    func = "mult8"
                elif isinstance(expression.operator, cst.LeftShift):
                    func = "lshift8"
                elif isinstance(expression.operator, cst.RightShift):
                    func = "rshift8"
                else:
                    raise Exception("Logic error, unexpected operator!")

                compiled.append_code("  ; just before function call")
                compiled += generate_function_call_internal(
                    create_call(
                        func,
                        [UnvalidatedName(lhs_dest), UnvalidatedName(rhs_dest)]
                    ),
                    destination,
                    types,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context.wrap(expression),
                )

            elif isinstance(expression.operator, (cst.Divide, cst.FloorDivide, cst.Modulo)):
                if not (destination_type.is_integer and destination_type.is_unsigned):
                    raise CompilerError(f"Unsupported type {destination_type.type} for unsigned division expression!", context)

                # Division is weird, since the built-in stdlib function handles both modulo and division.
                # The stdlib function is setup to return both in the input stack locations, so we need to
                # copy the correct one out.
                compiled += generate_function_call_internal(
                    create_call(
                        "udiv8",
                        [UnvalidatedName(lhs_dest), UnvalidatedName(rhs_dest)]
                    ),
                    None,
                    types,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context.wrap(expression),
                )

                compiled += generate_move_to(
                    rhs_dest if isinstance(expression.operator, cst.Modulo) else lhs_dest,
                    stack,
                    clobbers,
                    context,
                )
                compiled.append_code("  LOAD A")

            else:
                raise CompilerError(f"Unsupported run-time computation for {expression.operator}!", context)

            # This call puts the result in a, so check if that's what we want.
            if is_register_destination(destination):
                # Just make sure we bookkeep things. Both the LHS and RHS need to be unwound.
                stack.free(rhs_dest)
                stack.free(lhs_dest)
            else:
                stack.free(rhs_dest)
                compiled += generate_move_to(destination, stack, clobbers, context)
                compiled.append_code("  STORE A")
                if lhs_dest != destination:
                    stack.free(lhs_dest)

        else:
            if isinstance(expression.operator, cst.Subtract):
                if not destination_type.is_integer:
                    raise CompilerError(f"Unsupported type {destination_type.type} for integer expression!", context)

                # Using the neg16 or neg32 fnction that's part of our stdlib.
                negfunc = "neg16" if destination_size == 2 else "neg32"
                compiled += generate_function_call_internal(
                    create_call(
                        negfunc,
                        [UnvalidatedName(rhs_dest)],
                    ),
                    rhs_dest,
                    types,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context.wrap(expression.right, extra="-"),
                )

                # Using the add16 or add32 function that's part of our stdlib.
                addfunc = "add16" if destination_size == 2 else "add32"

                compiled += generate_function_call_internal(
                    create_call(
                        addfunc,
                        [UnvalidatedName(lhs_dest), UnvalidatedName(rhs_dest)],
                    ),
                    destination,
                    types,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context.wrap(expression),
                )

                stack.free(rhs_dest)
                if lhs_dest != destination:
                    stack.free(lhs_dest)

            elif isinstance(expression.operator, (cst.Add, cst.Multiply, cst.LeftShift, cst.RightShift)):
                if not destination_type.is_integer:
                    raise CompilerError(f"Unsupported type {destination_type.type} for integer expression!", context)

                if isinstance(expression.operator, cst.Add):
                    # Using the add16 or add32 function that's part of our stdlib.
                    function = "add16" if destination_size == 2 else "add32"
                elif isinstance(expression.operator, cst.Multiply):
                    # Using the mult16 or mult32 function that's part of our stdlib.
                    function = "mult16" if destination_size == 2 else "mult32"
                elif isinstance(expression.operator, cst.LeftShift):
                    # Using the lshift16 or lshift32 function that's part of our stdlib.
                    function = "lshift16" if destination_size == 2 else "lshift32"
                elif isinstance(expression.operator, cst.RightShift):
                    # Using the rshift16 or rshift32 function that's part of our stdlib.
                    function = "rshift16" if destination_size == 2 else "rshift32"
                else:
                    raise Exception("Logic error, unexpected operator {expression.operator)}")

                compiled += generate_function_call_internal(
                    create_call(
                        function,
                        [UnvalidatedName(lhs_dest), UnvalidatedName(rhs_dest)]
                    ),
                    destination,
                    types,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context.wrap(expression),
                )

                stack.free(rhs_dest)
                if lhs_dest != destination:
                    stack.free(lhs_dest)

            elif isinstance(expression.operator, (cst.Divide, cst.FloorDivide, cst.Modulo)):
                if not (destination_type.is_integer and destination_type.is_unsigned):
                    raise CompilerError(f"Unsupported type {destination_type.type} for unsigned division expression!", context)

                # Division is weird, since the built-in stdlib function handles both modulo and division.
                # The stdlib function is setup to return both in the input stack locations, so we need to
                # copy the correct one out.
                function = "udiv16" if destination_size == 2 else "udiv32"
                compiled += generate_function_call_internal(
                    create_call(
                        function,
                        [UnvalidatedName(lhs_dest), UnvalidatedName(rhs_dest)]
                    ),
                    None,
                    types,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context.wrap(expression),
                )

                location = rhs_dest if isinstance(expression.operator, cst.Modulo) else lhs_dest
                if location != destination:
                    compiled += generate_memcpy_stackvars(destination, location, stack, clobbers, context)

                # Now that we copied this to the destination, this is useless.
                stack.free(rhs_dest)
                if lhs_dest != destination:
                    stack.free(lhs_dest)

            elif isinstance(expression.operator, (cst.BitAnd, cst.BitOr, cst.BitXor)):
                if not destination_type.is_integer:
                    raise CompilerError(f"Unsupported type {destination_type.type} for integer expression!", context)

                # Adding clobbers the A register, since it is the accumulator.
                clobbers.add("A")

                # Compute our actual function that we will apply as we walk the stack.
                if isinstance(expression.operator, cst.BitAnd):
                    function = "  AND"
                elif isinstance(expression.operator, cst.BitOr):
                    function = "  OR"
                elif isinstance(expression.operator, cst.BitXor):
                    function = "  XOR"
                else:
                    raise Exception("Logic error, unexpected operator {expression.operator)}")

                if stack_is_at(rhs_dest, stack, offset=destination_size - 1):
                    # We're already at the top of the stack, generate the load/func/store loop downwards
                    # instead of upwards to shave off a move instruction.
                    def actual_expr_offset(offset: int) -> int:
                        return (destination_size - offset) - 1
                else:
                    # We're anywhere else in the stack, so it costs us no unnecessary move instructions
                    # to perform the first move.
                    def actual_expr_offset(offset: int) -> int:
                        return offset

                # Move to the right spot on the stack and then perform the operation on the two numbers.
                # Since bitwise operations are independent we can just do this in a loop.
                for offset in range(destination_size):
                    compiled += generate_move_to(rhs_dest, stack, clobbers, context, offset=actual_expr_offset(offset))
                    compiled.append_code("  LOAD A")
                    compiled += generate_move_to(lhs_dest, stack, clobbers, context, offset=actual_expr_offset(offset))
                    compiled.append_code(function)
                    compiled += generate_move_to(destination, stack, clobbers, context, offset=actual_expr_offset(offset))
                    compiled.append_code("  STORE A")

                stack.free(rhs_dest)
                if lhs_dest != destination:
                    stack.free(lhs_dest)

            else:
                raise CompilerError(f"Unsupported run-time computation for {expression.operator}!", context)

    return compiled


def generate_boolean_expr(
    expression: cst.BooleanOperation,
    destination: str,
    types: Dict[cst.CSTNode, CoreType],
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    compiled = Sections()

    destination_size = stack.sizeof(destination)
    if destination_size is None:
        raise Exception("Logic error, could not calculate size of destination!")
    destination_type = stack.typeof(destination)
    if destination_type is None:
        raise Exception("Logic error, could not calculate type of destination!")

    if destination_size != 1 or not destination_type.is_bool:
        raise CompilerError("Cannot assign boolean expression result to non-bool", context)

    if isinstance(expression.operator, cst.And):
        # Perform short-circuiting AND, first by handling the left hand side, and if it
        # is False immediately skipping the second half.
        clobbers.add("A")

        left_compiled = generate_expr_internal(expression.left, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.left))

        cloned_stack = stack.clone()
        right_compiled = generate_expr_internal(expression.right, "register(A, bool)", types, cloned_stack, clobbers, allocations, refs, local_consts, context.wrap(expression.right))

        # Not unifying the stack here because short circuiting could mean that a walrus assign doesn't get run.
        if stack.size != cloned_stack.size:
            raise Exception("Logic error, stacks on both expressions not equal in size!")
        if stack.location != cloned_stack.location:
            # Need to make the right hand side move back to where it was before it started.
            move_amount = stack.location - cloned_stack.location
            right_compiled += generate_move_by("restore stack to start of expression", move_amount, cloned_stack, clobbers, context)

        # In order to possibly jump past the right expression, we need to know its length, so we can either JRI or LNGJUMP.
        right_length = get_assembled_length(right_compiled.code, refs)
        short_circuit = local_label_name("short_circuit")
        if right_length > 32:
            insn = "LNGJUMPZ"
        else:
            insn = "JRIZ"

        # Now, perform the first boolean evaluation.
        compiled += left_compiled

        # Now, check it against False, to short circuit.
        compiled.code += [
            "  ADDI 0",
            f"  {insn} {short_circuit}",
        ]

        # Now, perform the second boolean evaluation.
        compiled += right_compiled

        # Now, provide a place to jump to.
        compiled.append_code(f"{short_circuit}:")

        if not is_register_destination(destination):
            compiled += generate_move_to(destination, stack, clobbers, context)
            compiled.append_code("  STORE A")

    elif isinstance(expression.operator, cst.Or):
        # Perform short-circuiting OR, first by handling the left hand side, and if it
        # is True immediately skipping the second half.
        clobbers.add("A")

        left_compiled = generate_expr_internal(expression.left, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.left))

        cloned_stack = stack.clone()
        right_compiled = generate_expr_internal(expression.right, "register(A, bool)", types, cloned_stack, clobbers, allocations, refs, local_consts, context.wrap(expression.right))

        # Not unifying the stack here because short circuiting could mean that a walrus assign doesn't get run.
        if stack.size != cloned_stack.size:
            raise Exception("Logic error, stacks on both expression not equal in size!")
        if stack.location != cloned_stack.location:
            # Need to make the right hand side move back to where it was before it started.
            move_amount = stack.location - cloned_stack.location
            right_compiled += generate_move_by("restore stack to start of expression", move_amount, cloned_stack, clobbers, context)

        # In order to possibly jump past the right expression, we need to know its length, so we can either JRI or LNGJUMP.
        right_length = get_assembled_length(right_compiled.code, refs)
        short_circuit = local_label_name("short_circuit")
        if right_length > 32:
            insn = "LNGJUMPNZ"
        else:
            insn = "JRINZ"

        # Now, perform the first boolean evaluation.
        compiled += left_compiled

        # Now, check it against False, to short circuit.
        compiled.code += [
            "  ADDI 0",
            f"  {insn} {short_circuit}",
        ]

        # Now, perform the second boolean evaluation.
        compiled += right_compiled

        # Now, provide a place to jump to.
        compiled.append_code(f"{short_circuit}:")

        if not is_register_destination(destination):
            compiled += generate_move_to(destination, stack, clobbers, context)
            compiled.append_code("  STORE A")

    else:
        raise CompilerError(f"Unsupported boolean operation {expression}!", context)

    return compiled


def generate_comparison_expr(
    expression: cst.Comparison,
    destination: str,
    types: Dict[cst.CSTNode, CoreType],
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    compiled = Sections()

    destination_size = stack.sizeof(destination)
    if destination_size is None:
        raise Exception("Logic error, could not calculate size of destination!")
    destination_type = stack.typeof(destination)
    if destination_type is None:
        raise Exception("Logic error, could not calculate type of destination!")

    if destination_size != 1 or not destination_type.is_bool:
        raise CompilerError("Cannot assign comparison expression to non-bool", context)

    if len(expression.comparisons) != 1:
        raise CompilerError(f"Unsupported multi-comparison expression {expression}", context)

    # Special case for is checks.
    if isinstance(expression.comparisons[0].operator, cst.Is):
        rhs_expr = expression.comparisons[0].comparator

        try:
            value = codegen_eval(rhs_expr, local_consts)
        except NonConstantExpressionException:
            value = None

        if value is None:
            raise CompilerError("Unsupported dynamic comparison for is check", context)
        if not isinstance(value, bool):
            raise CompilerError("Expecting comparison against True or False for is check", context)

        # Okay, now that we have the value we care about, generate the expression, evaluate
        # it for True/False, and set the destination accordingly. Clobber the A register because
        # all conditional statements are based on it.
        clobbers.add("A")

        compiled += generate_expr_internal(expression.left, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context)
        if value is False:
            # Gotta invert our output since it's already a boolean.
            compiled.append_code("  INV")

        if not is_register_destination(destination):
            compiled += generate_move_to(destination, stack, clobbers, context)
            compiled.append_code("  STORE A")

    elif isinstance(expression.comparisons[0].operator, (cst.Equal, cst.NotEqual)):
        # Determine preload value based on the comparison type.
        preload_value = 0xFF if isinstance(expression.comparisons[0].operator, cst.NotEqual) else 0x00

        left_expr = expression.left
        left_type = types[left_expr]

        right_expr = expression.comparisons[0].comparator
        right_type = types[right_expr]

        if left_type.is_string or right_type.is_string:
            if not (left_type.is_string and right_type.is_string):
                raise CompilerError("Unsupported comparison expression against types {left_type.type} and {right_type.type}", context)

            # In this case, don't even try to set up the stack, just let the function call handle it.
            compiled += generate_function_call_internal(
                create_call(
                    "strcmp",
                    [left_expr, right_expr],
                ),
                "register(A, int8)",
                types,
                stack,
                clobbers,
                allocations,
                refs,
                local_consts,
                context.wrap(expression),
            )
            compiled.append_code("  ADDI 0")
            compiled.append_code(f"  LOADI {preload_value}")
            compiled.append_code("  SKIPIF !ZF")
            compiled.append_code("  INV")

        else:
            equal_cleanup: List[str] = []
            if left_type.size == right_type.size:
                # First, evaluate both expressions so that we can compare them.
                first_dest = expr_temp_name()
                equal_cleanup.append(first_dest)
                stack.alloc(StackVar(first_dest, left_type))
                compiled += generate_expr_internal(left_expr, first_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(left_expr))

                second_dest = expr_temp_name()
                equal_cleanup.append(second_dest)
                stack.alloc(StackVar(second_dest, right_type))
                compiled += generate_expr_internal(right_expr, second_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(right_expr))

            else:
                # Figure out which one is bigger, we'll evaluate that one first.
                if left_type.size > right_type.size:
                    first_expr = left_expr
                    first_type = left_type
                    second_expr = right_expr
                    second_type = right_type
                else:
                    first_expr = right_expr
                    first_type = right_type
                    second_expr = left_expr
                    second_type = left_type

                # First, handle the expression that's the wider of the two already.
                first_dest = expr_temp_name()
                equal_cleanup.append(first_dest)
                stack.alloc(StackVar(first_dest, first_type))
                compiled += generate_expr_internal(first_expr, first_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(first_expr))

                # Now, allocate a spot for the second to be sign extended into.
                second_dest = expr_temp_name()
                equal_cleanup.append(second_dest)
                stack.alloc(StackVar(second_dest, first_type))

                # And allocate where we'll calculate it before sign-extending.
                second_temp = expr_temp_name()
                stack.alloc(StackVar(second_temp, second_type))
                compiled += generate_expr_internal(second_expr, second_temp, types, stack, clobbers, allocations, refs, local_consts, context.wrap(second_expr))

                # Now, copy it with a sign extension.
                compiled += generate_variable_lookup(second_temp, second_dest, stack, types, clobbers, allocations, refs, local_consts, context.wrap(second_expr))

                # Now, we don't need the temp location now that we've computed and sign extended.
                stack.free(second_temp)

            # Doing the comparison itself requires the A register.
            clobbers.add("A")

            comparison_size = max(left_type.size, right_type.size)
            if comparison_size == 1:
                compiled += generate_move_to(second_dest, stack, clobbers, context)
                compiled.append_code("  LOAD A")
                compiled += generate_move_to(first_dest, stack, clobbers, context)

                # XOR the two numbers, which will give us 0 if they equal.
                compiled.append_code("  XOR")

                # Preload condition result into A.
                compiled.append_code(f"  LOADI {preload_value}")

                # Skip the invert instruction if we were non-zero, which meant not equal.
                compiled.append_code("  SKIPIF !ZF")

                # Set our output to true instead of false.
                compiled.append_code("  INV")

            elif comparison_size == 2:
                if stack_is_at(second_dest, stack, offset=1):
                    # We're already at the top of the stack, generate the load/func/store loop downwards
                    # instead of upwards to shave off a move instruction.
                    def actual_expr_offset(offset: int) -> int:
                        return 1 - offset
                else:
                    # We're anywhere else in the stack, so it costs us no unnecessary move instructions
                    # to perform the first move.
                    def actual_expr_offset(offset: int) -> int:
                        return offset

                # Need somewhere to jump after failing the first half. Need to jump to second half if successful.
                second_byte_comparison = local_label_name("second_byte_comparison")
                finished_comparison = local_label_name("finished_comparison")

                compiled += generate_move_to(second_dest, stack, clobbers, context, offset=actual_expr_offset(0))
                compiled.append_code("  LOAD A")
                compiled += generate_move_to(first_dest, stack, clobbers, context, offset=actual_expr_offset(0))

                # XOR the two numbers, which will give us 0 if they equal.
                compiled.append_code("  XOR")
                compiled.append_code(f"  JRIZ {second_byte_comparison}")

                # We failed the comparison on the first byte, move to where we would have moved to and set our result to False.
                compiled += generate_move_to(first_dest, stack.clone(), clobbers, context, offset=actual_expr_offset(1))
                compiled.append_code(f"  LOADI {preload_value}")
                compiled.append_code(f"  JRI {finished_comparison}")

                # Now, do the second byte comparison.
                compiled.append_code(f"{second_byte_comparison}:")
                compiled += generate_move_to(second_dest, stack, clobbers, context, offset=actual_expr_offset(1))
                compiled.append_code("  LOAD A")
                compiled += generate_move_to(first_dest, stack, clobbers, context, offset=actual_expr_offset(1))

                # XOR the two numbers, which will give us 0 if they equal.
                compiled.append_code("  XOR")

                # Preload condition result into A.
                compiled.append_code(f"  LOADI {preload_value}")

                # Skip the invert instruction if we were non-zero, which meant not equal.
                compiled.append_code("  SKIPIF !ZF")

                # Set our output to true instead of false.
                compiled.append_code("  INV")

                # Provide a jump point to get here from the first half comparison.
                compiled.append_code(f"{finished_comparison}:")

            elif comparison_size == 4:
                if stack_is_at(second_dest, stack, offset=3):
                    # We're already at the top of the stack, generate the load/func/store loop downwards
                    # instead of upwards to shave off a move instruction.
                    def actual_expr_offset(offset: int) -> int:
                        return 3 - offset
                else:
                    # We're anywhere else in the stack, so it costs us no unnecessary move instructions
                    # to perform the first move.
                    def actual_expr_offset(offset: int) -> int:
                        return offset

                # Need somewhere to jump after failing the first half. Need to jump to second half if successful.
                second_byte_comparison = local_label_name("second_byte_comparison")
                third_byte_comparison = local_label_name("third_byte_comparison")
                fourth_byte_comparison = local_label_name("fourth_byte_comparison")
                finished_comparison = local_label_name("finished_comparison")

                compiled += generate_move_to(second_dest, stack, clobbers, context, offset=actual_expr_offset(0))
                compiled.append_code("  LOAD A")
                compiled += generate_move_to(first_dest, stack, clobbers, context, offset=actual_expr_offset(0))

                # XOR the two numbers, which will give us 0 if they equal.
                compiled.append_code("  XOR")
                compiled.append_code(f"  JRIZ {second_byte_comparison}")

                # We failed the comparison on the first byte, move to where we would have moved to and set our result to False.
                compiled += generate_move_to(first_dest, stack.clone(), clobbers, context, offset=actual_expr_offset(3))
                compiled.append_code(f"  LOADI {preload_value}")
                compiled.append_code(f"  JRI {finished_comparison}")

                # Now, do the second byte comparison.
                compiled.append_code(f"{second_byte_comparison}:")
                compiled += generate_move_to(second_dest, stack, clobbers, context, offset=actual_expr_offset(1))
                compiled.append_code("  LOAD A")
                compiled += generate_move_to(first_dest, stack, clobbers, context, offset=actual_expr_offset(1))

                # XOR the two numbers, which will give us 0 if they equal.
                compiled.append_code("  XOR")
                compiled.append_code(f"  JRIZ {third_byte_comparison}")

                # We failed the comparison on the second byte, move to where we would have moved to and set our result to False.
                compiled += generate_move_to(first_dest, stack.clone(), clobbers, context, offset=actual_expr_offset(3))
                compiled.append_code(f"  LOADI {preload_value}")
                compiled.append_code(f"  JRI {finished_comparison}")

                # Now, do the third byte comparison.
                compiled.append_code(f"{third_byte_comparison}:")
                compiled += generate_move_to(second_dest, stack, clobbers, context, offset=actual_expr_offset(2))
                compiled.append_code("  LOAD A")
                compiled += generate_move_to(first_dest, stack, clobbers, context, offset=actual_expr_offset(2))

                # XOR the two numbers, which will give us 0 if they equal.
                compiled.append_code("  XOR")
                compiled.append_code(f"  JRIZ {fourth_byte_comparison}")

                # We failed the comparison on the third byte, move to where we would have moved to and set our result to False.
                compiled += generate_move_to(first_dest, stack.clone(), clobbers, context, offset=actual_expr_offset(3))
                compiled.append_code(f"  LOADI {preload_value}")
                compiled.append_code(f"  JRI {finished_comparison}")

                # Now, do the fourth byte comparison.
                compiled.append_code(f"{fourth_byte_comparison}:")
                compiled += generate_move_to(second_dest, stack, clobbers, context, offset=actual_expr_offset(3))
                compiled.append_code("  LOAD A")
                compiled += generate_move_to(first_dest, stack, clobbers, context, offset=actual_expr_offset(3))

                # XOR the two numbers, which will give us 0 if they equal.
                compiled.append_code("  XOR")

                # Preload condition result into A.
                compiled.append_code(f"  LOADI {preload_value}")

                # Skip the invert instruction if we were non-zero, which meant not equal.
                compiled.append_code("  SKIPIF !ZF")

                # Set our output to true instead of false.
                compiled.append_code("  INV")

                # Provide a jump point to get here from the first half comparison.
                compiled.append_code(f"{finished_comparison}:")

            for entry in reversed(equal_cleanup):
                stack.free(entry)

        if not is_register_destination(destination):
            compiled += generate_move_to(destination, stack, clobbers, context)
            compiled.append_code("  STORE A")

    elif isinstance(expression.comparisons[0].operator, (cst.GreaterThan, cst.GreaterThanEqual, cst.LessThan, cst.LessThanEqual)):
        # Determine preload value based on the comparison type.
        preload_value = 0xFF if isinstance(expression.comparisons[0].operator, cst.NotEqual) else 0x00

        left_expr = expression.left
        left_type = types[left_expr]

        right_expr = expression.comparisons[0].comparator
        right_type = types[right_expr]

        if isinstance(expression.comparisons[0].operator, cst.GreaterThan):
            op = ">"
        elif isinstance(expression.comparisons[0].operator, cst.LessThan):
            op = "<"
        elif isinstance(expression.comparisons[0].operator, cst.GreaterThanEqual):
            op = ">="
        elif isinstance(expression.comparisons[0].operator, cst.LessThanEqual):
            op = "<="
        else:
            raise Exception("Logic error, unexpected comparison type!")

        if left_type.is_string or right_type.is_string:
            if not (left_type.is_string and right_type.is_string):
                raise CompilerError("Unsupported comparison expression against types {left_type.type} and {right_type.type}", context)

            # In this case, don't even try to set up the stack, just let the function call handle it.
            compiled += generate_function_call_internal(
                create_call(
                    "strcmp",
                    [left_expr, right_expr],
                ),
                "register(A, int8)",
                types,
                stack,
                clobbers,
                allocations,
                refs,
                local_consts,
                context.wrap(expression),
            )

        else:
            unequal_cleanup: List[str] = []

            if left_type.size == right_type.size:
                # First, evaluate both expressions so that we can compare them.
                first_dest = expr_temp_name()
                unequal_cleanup.append(first_dest)
                stack.alloc(StackVar(first_dest, left_type))
                compiled += generate_expr_internal(left_expr, first_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(left_expr))

                second_dest = expr_temp_name()
                unequal_cleanup.append(second_dest)
                stack.alloc(StackVar(second_dest, right_type))
                compiled += generate_expr_internal(right_expr, second_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(right_expr))

            else:
                # Figure out which one is bigger, we'll evaluate that one first.
                if left_type.size > right_type.size:
                    first_expr = left_expr
                    first_type = left_type
                    second_expr = right_expr
                    second_type = right_type
                else:
                    first_expr = right_expr
                    first_type = right_type
                    second_expr = left_expr
                    second_type = left_type

                    # Since the two params are swapped, we must swap the op as well.
                    op = {
                        ">": "<",
                        "<": ">",
                        ">=": "<=",
                        "<=": ">=",
                    }[op]

                # First, handle the expression that's the wider of the two already.
                first_dest = expr_temp_name()
                unequal_cleanup.append(first_dest)
                stack.alloc(StackVar(first_dest, first_type))
                compiled += generate_expr_internal(first_expr, first_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(first_expr))

                # Now, allocate a spot for the second to be sign extended into.
                second_dest = expr_temp_name()
                unequal_cleanup.append(second_dest)
                stack.alloc(StackVar(second_dest, first_type, initialized=True))

                # And allocate where we'll calculate it before sign-extending.
                second_temp = expr_temp_name()
                stack.alloc(StackVar(second_temp, second_type))
                compiled += generate_expr_internal(second_expr, second_temp, types, stack, clobbers, allocations, refs, local_consts, context.wrap(second_expr))

                # Now, copy it with a sign extension.
                compiled += generate_variable_lookup(second_temp, second_dest, stack, types, clobbers, allocations, refs, local_consts, context.wrap(second_expr))

                # Now, we don't need the temp location now that we've computed and sign extended.
                stack.free(second_temp)

            # Doing the comparison itself requires the A register.
            clobbers.add("A")

            comparison_size = max(left_type.size, right_type.size)
            if comparison_size == 1:
                if left_type.is_unsigned:
                    func_name = "ucmp8"
                else:
                    func_name = "cmp8"
            elif comparison_size == 2:
                if left_type.is_unsigned:
                    func_name = "ucmp16"
                else:
                    func_name = "cmp16"
            elif comparison_size == 4:
                if left_type.is_unsigned:
                    func_name = "ucmp32"
                else:
                    func_name = "cmp32"
            else:
                raise Exception(f"Logic error, unexpected comparison size {comparison_size}!")

            compiled += generate_function_call_internal(
                create_call(
                    func_name,
                    [UnvalidatedName(x) for x in unequal_cleanup],
                ),
                "register(A, int8)",
                types,
                stack,
                clobbers,
                allocations,
                refs,
                local_consts,
                context.wrap(expression),
            )

            for entry in reversed(unequal_cleanup):
                stack.free(entry)

        # Now, set the output to True or False depending on which comparison we wanted.
        if op == ">":
            # We want the result to be equal to 1.
            compiled.append_code("  ADDI -1")
            compiled.append_code("  ZERO")
            compiled.append_code("  SKIPIF !ZF")
            compiled.append_code("  INV")
        elif op == "<":
            # We want the result to be equal to -1.
            compiled.append_code("  ADDI 1")
            compiled.append_code("  ZERO")
            compiled.append_code("  SKIPIF !ZF")
            compiled.append_code("  INV")
        elif op == ">=":
            # We want the result to be not equal to -1.
            compiled.append_code("  ADDI 1")
            compiled.append_code("  ZERO")
            compiled.append_code("  SKIPIF ZF")
            compiled.append_code("  INV")
        elif op == "<=":
            # We want the result to be not equal to 1.
            compiled.append_code("  ADDI -1")
            compiled.append_code("  ZERO")
            compiled.append_code("  SKIPIF ZF")
            compiled.append_code("  INV")
        else:
            raise Exception("Logic error, unexpected comparison type!")

        if not is_register_destination(destination):
            compiled += generate_move_to(destination, stack, clobbers, context)
            compiled.append_code("  STORE A")

    else:
        # TODO: Additional comparisons.
        raise CompilerError(f"Unsupported comparison expression {expression}!", context)

    return compiled


def generate_ternary_expr(
    expression: cst.IfExp,
    destination: str,
    types: Dict[cst.CSTNode, CoreType],
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    compiled = Sections()

    destination_size = stack.sizeof(destination)
    if destination_size is None:
        raise Exception("Logic error, could not calculate size of destination!")
    destination_type = stack.typeof(destination)
    if destination_type is None:
        raise Exception("Logic error, could not calculate type of destination!")

    # We clobber A by doing the boolean test.
    clobbers.add("A")

    # First, compile the boolean expression, putting the result in A, so we know which
    # of the two expressions to evaluate.
    if not types[expression.test].is_bool:
        test_coerced = create_call("bool", [expression.test])
        types[test_coerced] = CoreType("bool")

        compiled += generate_expr_internal(
            test_coerced, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.virtual(test_coerced).wrap(test_coerced)
        )
    else:
        compiled += generate_expr_internal(expression.test, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.test))

    # Now, we need a place to jump to if the expression above is false, as well as a
    # place to jump to at the end of the true expression.
    false_expr = local_label_name("false_expr")
    expr_end = local_label_name("expr_end")

    # Now, compile the two expressions themselves, so that we can calculate whether
    # we can JRI or LNGJUMP to the various locations.
    left_stack = stack.clone()
    left_compiled = generate_expr_internal(expression.body, destination, types, left_stack, clobbers, allocations, refs, local_consts, context.wrap(expression.body))

    right_stack = stack.clone()
    right_compiled = generate_expr_internal(expression.orelse, destination, types, right_stack, clobbers, allocations, refs, local_consts, context.wrap(expression.orelse))

    # We could add this manually at the end of this function, but then we wouldn't be able
    # to compile the left hand side to determine length since it would have an undefined
    # jump location.
    right_compiled.append_code(f"{expr_end}:")

    if left_stack.size != right_stack.size:
        raise Exception("Logic error, stacks on both expressions not equal in size!")
    if left_stack.location != right_stack.location:
        # Arbitrarily choose the left side expression to fix up to the right.
        move_amount = right_stack.location - left_stack.location
        left_compiled += generate_move_by("move stack to same spot as else expression", move_amount, left_stack, clobbers, context)

    # Unify initialization tracking across cloned stacks so we can identify all paths that don't lead to variable initialization.
    stack.unify(left_stack, right_stack)

    # Now, figure out the else size so we can jump past it in the body.
    right_length = get_assembled_length(right_compiled.code, refs)
    if right_length > 32:
        left_compiled.append_code(f"  LNGJUMP {expr_end}")
    else:
        left_compiled.append_code(f"  JRI {expr_end}")

    # Now, figure out the body size. We can't just compile it because it
    # would fail to find the jump at the end, which can be differently
    # sized depending on if its a JRI or a LNGJUMP. So, compiled the left
    # and right, and subtract the right length since we know it already.
    left_length = get_assembled_length([*left_compiled.code, *right_compiled.code], refs) - right_length

    # Now, generate the code to figure out if the expression is true/false and
    # then jump to it.
    compiled.append_code("  INV")
    if left_length > 32:
        compiled.append_code(f"  LNGJUMPNZ {false_expr}")
    else:
        compiled.append_code(f"  JRINZ {false_expr}")
    compiled += left_compiled
    compiled.append_code(f"{false_expr}:")
    compiled += right_compiled

    # Now, set the stack location for our current stack to the location that both
    # expressions leave it at.
    if left_stack.location != right_stack.location:
        raise Exception("Logic error, stacks should have been the same location at this point!")
    stack.location = left_stack.location

    return compiled


def generate_subscript_expr(
    expression: cst.Subscript,
    destination: Optional[str],
    types: Dict[cst.CSTNode, CoreType],
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    compiled = Sections()

    if len(expression.slice) != 1:
        raise CompilerError("Unsupported slice count in subscript expression", context)
    slice_or_index = expression.slice[0].slice

    if isinstance(slice_or_index, cst.Index):
        # We always end up needing the string on the left hand size, regardless of whether we're indexing or slicing into it.
        base_dest = expr_temp_name()
        stack.alloc(StackVar(base_dest, CoreType("str", const=True)))
        compiled += generate_expr_internal(expression.value, base_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.value))

        # Calculate the offset into the string that we're gonna need, first.
        clobbers.add("A")
        compiled += generate_expr_internal(slice_or_index.value, "register(A, uint8)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(slice_or_index.value))

        # We clobber the SPC to do this index lookup.
        clobbers.add("SPC")

        # Move to the correct spot on the stack to pop the pointer onto the SPC.
        compiled += generate_move_to(base_dest, stack, clobbers, context, offset=1)
        compiled.append_code("  POP SPC")
        stack.move(-2)
        compiled.code += comment_stack(stack)

        compiled.append_code("  SWAP PC, SPC")
        compiled.append_code("  ADDPC")
        compiled.append_code("  LOAD A")
        compiled.append_code("  SWAP PC, SPC")

        if destination is not None:
            destination_size = stack.sizeof(destination)
            if destination_size is None:
                raise Exception("Logic error, could not calculate size of destination!")
            destination_type = stack.typeof(destination)
            if destination_type is None:
                raise Exception("Logic error, could not calculate type of destination!")

            if destination_size != 1 or not destination_type.is_char:
                raise Exception("Logic error, invalid character assignment expression!")

            if not is_register_destination(destination):
                compiled += generate_move_to(destination, stack, clobbers, context)
                compiled.append_code("  STORE A")

        stack.free(base_dest)

    elif isinstance(slice_or_index, cst.Slice):
        if destination is None:
            raise CompilerError("Unsupported expression without assignment!", context)

        destination_type = stack.typeof(destination)
        if destination_type is None:
            raise Exception("Logic error, could not calculate type of destination!")

        # This is a subscript in the form of var[:] which in Python land is a copy,
        # so we can do that here.
        if not stack.initof(destination):
            compiled += generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

            # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
            stack.init(destination)

        # We copy this here, because if we don't, then the function call ends up needing to copy a ton more
        # on the stack later.
        if stack[-1].name != destination:
            # In order to ensure that it's possible to do stack math on this value, locate it in
            # a temporary location for the time being if the destination isn't the top of the stack.
            lhs_dest = expr_temp_name()
            stack.alloc(StackVar(lhs_dest, CoreType("str"), initialized=True))

            compiled += generate_memcpy_stackvars(lhs_dest, destination, stack, clobbers, context)
        else:
            # Safe to put first parameter in the top of the stack where it already is useful for math.
            lhs_dest = destination

        # We always end up needing the string on the left hand size, regardless of whether we're indexing or slicing into it.
        base_dest = expr_temp_name()
        stack.alloc(StackVar(base_dest, CoreType("str", const=True)))
        compiled += generate_expr_internal(expression.value, base_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.value))

        if slice_or_index.step is not None:
            # We don't support copying with a step size other than the default.
            raise CompilerError("Unsupported step for slice in subscript expression", context)

        # Figure out if this is a copy operation, or a substring operation.
        beginning = slice_or_index.lower
        ending = slice_or_index.upper

        if beginning is None and ending is None:
            # Now, just strcpy it over.
            compiled += generate_function_call_internal(
                create_call("strcpy", [UnvalidatedName(lhs_dest), UnvalidatedName(base_dest)]),
                None,
                types,
                stack,
                clobbers,
                allocations,
                refs,
                local_consts,
                context.wrap(expression),
            )

        elif beginning is None and ending is not None:
            # This can be mapped onto a simple strncmp, so we should calculate the ending value and do that.
            ending_dest = expr_temp_name()
            stack.alloc(StackVar(ending_dest, CoreType("uint8")))
            compiled += generate_expr_internal(ending, ending_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(ending))
            compiled += generate_function_call_internal(
                create_call("strncpy", [UnvalidatedName(lhs_dest), UnvalidatedName(base_dest), UnvalidatedName(ending_dest)]),
                None,
                types,
                stack,
                clobbers,
                allocations,
                refs,
                local_consts,
                context.wrap(expression),
            )

            stack.free(ending_dest)

        else:
            if beginning is None:
                raise Exception("Logic error, shouldn't be possible to get a null beginning here!")

            # The beginning is non-null, regardless of whether the ending is present. So, we must adjust the
            # local base destination forward by the slice value.
            clobbers.add("A")
            clobbers.add("SPC")
            compiled += generate_expr_internal(beginning, "register(A, uint8)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(beginning))

            # Move to the correct spot on the stack to move the pointer to the right offset.
            compiled += generate_move_to(base_dest, stack, clobbers, context, offset=1)

            # Instead of just using ADDPC here to increment past the bytes we don't want, we increment one at
            # a time. This is so we can check for an early null-terminator to make start indexing memory safe
            # just like end indexing is.
            clobbers.add("U")
            clobbers.add("V")

            advance_top = local_label_name("advance_top")
            advance_bottom = local_label_name("advance_bottom")

            # Swap over so we can check the string one byte at a time.
            compiled.append_code("  MOV A, V")
            compiled.append_code("  POP SPC")
            compiled.append_code("  SWAP PC, SPC")

            # Loop through, checking for termination conditions. First check for end of loop by advancing enough.
            # Then, check if we've hit a null byte.
            compiled.append_code(f"{advance_top}:")
            compiled.append_code("  ADDI 0")
            compiled.append_code(f"  JRIZ {advance_bottom}")
            compiled.append_code("  DEC")
            compiled.append_code("  MOV A, U")
            compiled.append_code("  LOAD A")
            compiled.append_code("  ADDI 0")
            compiled.append_code(f"  JRIZ {advance_bottom}")
            compiled.append_code("  INCPC")
            compiled.append_code("  MOV U, A")
            compiled.append_code(f"  JRI {advance_top}")
            compiled.append_code(f"{advance_bottom}:")
            compiled.append_code("  SWAP PC, SPC")
            compiled.append_code("  PUSH SPC")
            compiled.append_code("  MOV V, A")

            if ending is None:
                # Now, just strcpy it over.
                compiled += generate_function_call_internal(
                    create_call("strcpy", [UnvalidatedName(lhs_dest), UnvalidatedName(base_dest)]),
                    None,
                    types,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context.wrap(expression),
                )

            else:
                try:
                    # Attempt to do a constant unroll to avoild a bunch of nasty codegen.
                    expr = cst.BinaryOperation(left=ending, operator=cst.Subtract(), right=beginning)
                    codegen_eval(expr, local_consts)

                    ending_dest = expr_temp_name()
                    stack.alloc(StackVar(ending_dest, CoreType("int8")))
                    compiled += generate_expr_internal(expr, ending_dest, types, stack, clobbers, allocations, refs, local_consts, context.virtual(expr))

                except NonConstantExpressionException:
                    # First, store the beginning value that we calculated so that we can subtract it later.
                    ending_dest = expr_temp_name()
                    stack.alloc(StackVar(ending_dest, CoreType("int8"), initialized=True))
                    compiled += generate_move_to(ending_dest, stack, clobbers, context)
                    compiled.append_code("  NEG")
                    compiled.append_code("  STORE A")

                    # This can be mapped onto a simple strncmp, so we should calculate the ending value and do that.
                    ending_temp = expr_temp_name()
                    stack.alloc(StackVar(ending_temp, CoreType("uint8")))
                    compiled += generate_expr_internal(ending, ending_temp, types, stack, clobbers, allocations, refs, local_consts, context.wrap(ending))
                    compiled += generate_move_to(ending_temp, stack, clobbers, context)
                    compiled.append_code("  LOAD A")
                    stack.free(ending_temp)

                    compiled += generate_move_to(ending_dest, stack, clobbers, context)
                    compiled.append_code("  ADD")
                    compiled.append_code("  STORE A")

                compiled += generate_function_call_internal(
                    create_call("strncpy", [UnvalidatedName(lhs_dest), UnvalidatedName(base_dest), UnvalidatedName(ending_dest)]),
                    None,
                    types,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context.wrap(expression),
                )

                stack.free(ending_dest)

        stack.free(base_dest)
        if lhs_dest != destination:
            stack.free(lhs_dest)

    else:
        raise Exception("Logic error, unexpected node {slice_or_index} for subscript slice!")

    return compiled


def generate_fstring_expr(
    expression: cst.FormattedString,
    destination: Optional[str],
    types: Dict[cst.CSTNode, CoreType],
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    node: cst.BaseExpression
    concatenation: List[cst.BaseExpression] = []
    virtual = context

    # Grab all of the pieces of this so we can desugar it.
    for part in expression.parts:
        if isinstance(part, cst.FormattedStringText):
            node = cst.SimpleString(repr(part.value))
            types[node] = CoreType("str", const=True, length=len(part.value) + 1)
            virtual = virtual.virtual(node)
            concatenation.append(node)

        elif isinstance(part, cst.FormattedStringExpression):
            if part.conversion is not None:
                raise CompilerError(f"Unsupported conversion {part.conversion!r} in f-string", context)
            if part.format_spec is not None:
                raise CompilerError(f"Unsupported format specifier {part.format_spec!r} in f-string", context)

            node = create_call("str", [part.expression])
            types[node] = CoreType("str", const=True)
            virtual = virtual.virtual(node)
            concatenation.append(node)

        else:
            raise Exception("Logic error, unexpected node in f-string!")

    if len(concatenation) == 0:
        node = cst.SimpleString('""')
        types[node] = CoreType("str", const=True, length=1)
        return generate_expr_internal(node, destination, types, stack, clobbers, allocations, refs, local_consts, virtual.virtual(node))

    if len(concatenation) == 1:
        return generate_expr_internal(concatenation[0], destination, types, stack, clobbers, allocations, refs, local_consts, virtual)

    # We need to construct a concatenation tree from the list of things to concatenate.
    tree: cst.BinaryOperation = cst.BinaryOperation(left=concatenation[0], right=concatenation[1], operator=cst.Add())
    types[tree] = CoreType("str", const=True)
    virtual = virtual.virtual(tree)
    concatenation = concatenation[2:]

    while concatenation:
        node = concatenation[0]
        concatenation = concatenation[1:]

        tree = cst.BinaryOperation(left=tree, right=node, operator=cst.Add())
        types[tree] = CoreType("str", const=True)
        virtual = virtual.virtual(tree)

    return generate_expr_internal(tree, destination, types, stack, clobbers, allocations, refs, local_consts, virtual)


def generate_expr_internal(
    expression: cst.BaseExpression,
    destination: Optional[str],
    types: Dict[cst.CSTNode, CoreType],
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    compiled = Sections()

    if destination is not None:
        destination_size = stack.sizeof(destination)
        if destination_size is None:
            raise Exception("Logic error, could not calculate size of destination!")
    else:
        destination_size = 0

    try:
        # If we can evaluate this directly, do so!
        value = codegen_eval(expression, local_consts)
        if isinstance(value, (bool, int)):
            if destination is not None:
                compiled += generate_const_load(value, destination, stack, clobbers, context)

                # We're gonna assign to this, so it should be considered initialized. Do this here instead of at the top
                # so we can catch variables assigning from themselves when unassigned.
                stack.init(destination)

            return compiled

        if isinstance(value, str):
            if len(value) >= MAX_STRING_LENGTH:
                raise CompilerError(f"Unsupported too-long string, strings are required to be {MAX_STRING_LENGTH} characters maximum", context)

            if destination is not None:
                destination_type = stack.typeof(destination)
                if destination_type is None:
                    raise Exception("Logic error, could not find type of string pointer destination!")

                # Python treats strings and characters the same, so let's fix that here.
                if destination_type.is_char:
                    compiled += generate_const_load(value, destination, stack, clobbers, context)

                    # We're gonna assign to this, so it should be considered initialized. Do this here instead of at the top
                    # so we can catch variables assigning from themselves when unassigned.
                    stack.init(destination)

                    return compiled

                if not destination_type.is_string:
                    raise Exception("Logic error, tried to assign string pointer to wrong type!")

                if destination_type.const:
                    # First, set up somewhere to put the initialized string data so we can point at it.
                    label = local_label_name("function_string_data")
                    compiled.append_preamble(f"{label}:")
                    for c in value:
                        compiled.append_preamble(f"  .char {c[0]!r}")
                    compiled.append_preamble("  .byte 0x00")

                    # Now, point at it.
                    clobbers.add("A")

                    compiled += generate_move_to(destination, stack, clobbers, context, offset=-1)
                    compiled.append_code(f"  PUSHADDR {label}")
                    stack.location += 2
                else:
                    # Need to allocate static space for the string, then strcpy it over.
                    if not stack.initof(destination):
                        compiled += generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                        # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                        stack.init(destination)

                    static_source_storage = local_label_name("function_string_data")
                    compiled.append_preamble(f"{static_source_storage}:")
                    for c in value:
                        compiled.append_preamble(f"  .char {c[0]!r}")
                    compiled.append_preamble("  .byte 0x00")

                    # Now, set up the stack for a strcpy operation, to initialize the local data with
                    # a copy of the constant we're initializing from.
                    if stack[-1].name != destination:
                        # In order to ensure that it's possible to do stack math on this value, locate it in
                        # a temporary location for the time being if the destination isn't the top of the stack.
                        lhs_dest = expr_temp_name()
                        stack.alloc(StackVar(lhs_dest, CoreType("str"), initialized=True))

                        compiled += generate_memcpy_stackvars(lhs_dest, destination, stack, clobbers, context)
                    else:
                        # Safe to put first parameter in the top of the stack where it already is useful for math.
                        lhs_dest = destination

                    # Now, point at it.
                    clobbers.add("A")

                    rhs_dest = expr_temp_name()
                    stack.alloc(StackVar(rhs_dest, CoreType("str"), initialized=True))
                    compiled += generate_move_to(rhs_dest, stack, clobbers, context, offset=-1)
                    compiled.append_code(f"  PUSHADDR {static_source_storage}")
                    stack.location += 2

                    # Now call strcpy.
                    compiled += generate_function_call_internal(
                        create_call("strcpy", [UnvalidatedName(lhs_dest), UnvalidatedName(rhs_dest)]),
                        None,
                        types,
                        stack,
                        clobbers,
                        allocations,
                        refs,
                        local_consts,
                        context.wrap(expression),
                    )

                    # Finally, free the stack.
                    stack.free(rhs_dest)
                    if lhs_dest != destination:
                        stack.free(lhs_dest)

                # We're gonna assign to this, so it should be considered initialized. Do this here instead of at the top
                # so we can catch variables assigning from themselves when unassigned.
                stack.init(destination)

            return compiled

    except NonConstantExpressionException:
        # We must treat this as a non-unrolled expression.
        pass

    if isinstance(expression, cst.Name):
        # Explicitly allowing variable lookup because it could allow a register clear on read.
        compiled += generate_variable_lookup(expression.value, destination, stack, types, clobbers, allocations, refs, local_consts, context)

    elif isinstance(expression, cst.UnaryOperation):
        if destination is not None:
            compiled += generate_unary_expr(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

    elif isinstance(expression, cst.BinaryOperation):
        if destination is not None:
            compiled += generate_binary_expr(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

    elif isinstance(expression, cst.Call):
        function_return_type = types[expression]
        if destination is not None and function_return_type.type != "any" and function_return_type.size != destination_size:
            # We need to put this in a local temporary variable, and then copy it out.
            return_temp = expr_temp_name()
            stack.alloc(StackVar(return_temp, function_return_type))

            compiled += generate_function_call(expression, return_temp, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression))
            compiled += generate_variable_lookup(return_temp, destination, stack, types, clobbers, allocations, refs, local_consts, context.wrap(expression))

            stack.free(return_temp)
        else:
            # We could possibly be making a function call with no destination here, such as calling a void function.
            compiled += generate_function_call(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression))

    elif isinstance(expression, cst.Comparison):
        if destination is not None:
            compiled += generate_comparison_expr(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

    elif isinstance(expression, cst.BooleanOperation):
        if destination is not None:
            compiled += generate_boolean_expr(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

    elif isinstance(expression, cst.IfExp):
        if destination is not None:
            compiled += generate_ternary_expr(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

    elif isinstance(expression, cst.Subscript):
        # Allowing subscript operation without a destination because it could allow register clear on read.
        compiled += generate_subscript_expr(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

    elif isinstance(expression, cst.FormattedString):
        if destination is not None:
            compiled += generate_fstring_expr(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

    else:
        # TODO: What other expression types are we missing? Probably array and memory operations.
        raise CompilerError(f"Unsupported expression type {expression} in expression compiler!", context)

    if destination is not None:
        # We're gonna assign to this, so it should be considered initialized. Do this here instead of at the top
        # so we can catch variables assigning from themselves when unassigned.
        stack.init(destination)

    return compiled


def infer_expr_types(
    expression: cst.BaseExpression,
    destination_type: CoreType,
    stack: Stack,
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Dict[cst.CSTNode, CoreType]:
    types = infer_expr_types_impl(expression, stack, refs, local_consts, context)
    infer_tree(types, destination_type, context)
    return types


def infer_tree(
    types: Dict[cst.CSTNode, CoreType],
    concrete_type: CoreType,
    context: Context,
) -> None:
    if concrete_type.type == "int":
        raise Exception("Logic error, attempting to infer tree with unspecified type!")
    if concrete_type.type == "string":
        raise Exception("Logic error, attempting to infer tree with unspecified type!")

    for _, ctype in types.items():
        if ctype.type == "int":
            if concrete_type.type == "void":
                raise CompilerError("Unsupported expression without assignment", context)
            if concrete_type.type == "any":
                # Assume the most favorable case.
                ctype.type = "uint8"
                continue
            if not concrete_type.is_integer:
                raise CompilerError(f"Unsupported integer expression assignment to non-integer type {concrete_type.type}", context)
            ctype.type = concrete_type.type
        if ctype.type == "string":
            if concrete_type.type == "void":
                raise CompilerError("Unsupported expression without assignment", context)
            if not (concrete_type.is_string or concrete_type.is_char):
                raise CompilerError(f"Unsupported string expression assignment to non-string type {concrete_type.type}", context)
            if concrete_type.type == "any":
                # Arbitrarily force to string.
                ctype.type = "str"
                continue
            ctype.type = concrete_type.type
            if concrete_type.is_char:
                ctype.length = None


def infer_expr_types_impl(
    expression: cst.BaseExpression,
    stack: Stack,
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Dict[cst.CSTNode, CoreType]:
    inferred: Dict[cst.CSTNode, CoreType] = {}

    if isinstance(expression, cst.Name):
        stack_type = stack.typeof(expression.value)
        if stack_type is not None:
            inferred[expression] = stack_type
            return inferred

        const_type = const_by_name(local_consts, expression.value)
        if const_type is not None:
            inferred[expression] = const_type.type
            return inferred

        global_var = global_by_name(refs, expression.value)
        if global_var is not None:
            inferred[expression] = global_var.type
            return inferred

        raise CompilerError(f"Undefined variable reference to {expression.value!r}", context)

    elif isinstance(expression, cst.Integer):
        inferred[expression] = CoreType("int")
        return inferred

    elif isinstance(expression, cst.SimpleString):
        try:
            value = codegen_eval(expression, [])
        except NonConstantExpressionException:
            raise Exception("Logic error, couldn't get string from SimpleString!")
        if not isinstance(value, str):
            raise Exception("Logic error, didn't get string back from codegen_eval!")

        length_needed = len(value) + 1

        if length_needed > MAX_STRING_LENGTH:
            raise CompilerError(f"Unsupported too-long string, strings are required to be {MAX_STRING_LENGTH} characters maximum", context)

        inferred[expression] = CoreType("string", const=True, length=length_needed)
        return inferred

    elif isinstance(expression, cst.UnaryOperation):
        inferred.update(infer_expr_types_impl(expression.expression, stack, refs, local_consts, context.wrap(expression.expression)))
        inferred_type = inferred[expression.expression]
        inferred[expression] = CoreType(inferred_type.type, inferred_type.pointed_type, const=inferred_type.const, extern=inferred_type.extern, return_padding=inferred_type.return_padding)

        if isinstance(expression.operator, (cst.Minus, cst.BitInvert)):
            if not inferred_type.is_integer:
                raise CompilerError(f"Unsupported unary operation for type {inferred_type.type}", context)
        return inferred

    elif isinstance(expression, cst.BinaryOperation):
        left_tree = infer_expr_types_impl(expression.left, stack, refs, local_consts, context.wrap(expression.left))
        right_tree = infer_expr_types_impl(expression.right, stack, refs, local_consts, context.wrap(expression.right))

        left_inferred = left_tree[expression.left]
        right_inferred = right_tree[expression.right]

        if isinstance(expression.operator, (cst.Add, cst.Subtract, cst.BitAnd, cst.BitOr, cst.BitXor, cst.Multiply, cst.Divide, cst.FloorDivide, cst.Modulo)):
            if isinstance(expression.operator, cst.Add):
                if left_inferred.type == "string":
                    infer_tree(left_tree, CoreType("str"), context)
                if right_inferred.type == "string":
                    infer_tree(right_tree, CoreType("str"), context)

                if left_inferred.is_string and right_inferred.is_string:
                    # This is string concatenation.
                    inferred[expression] = CoreType("str", None, const=False, extern=False)
                    inferred.update(left_tree)
                    inferred.update(right_tree)
                    return inferred

                elif left_inferred.is_string and right_inferred.is_char:
                    # This is adding a character to the end of a string.
                    inferred[expression] = CoreType("str", None, const=False, extern=False)
                    inferred.update(left_tree)
                    inferred.update(right_tree)
                    return inferred

            if not left_inferred.is_integer:
                raise CompilerError(f"Unsupported binary operation for type {left_inferred.type}", context)
            if not right_inferred.is_integer:
                raise CompilerError(f"Unsupported binary operation for type {right_inferred.type}", context)

            # Any math against two integers will result in an integer. Pick the wider of two types.
            if right_inferred.type == "int":
                if left_inferred.type != "int":
                    infer_tree(right_tree, left_inferred, context)

                # Just arbitrarily pick the left, which could be an unspecified int as well.
                picked = left_inferred

            elif left_inferred.type == "int" and right_inferred != "int":
                # Pick the right since it is specified, the left will have to be filled in later.
                infer_tree(left_tree, right_inferred, context)
                picked = right_inferred

            elif left_inferred.size > right_inferred.size:
                # Pick the left because it's wider than the right.
                picked = left_inferred

            else:
                # Pick the right because its either wider than the left, or equivalent in width.
                picked = right_inferred

            inferred[expression] = CoreType(picked.type, picked.pointed_type, const=picked.const, extern=picked.extern, return_padding=picked.return_padding)
            inferred.update(left_tree)
            inferred.update(right_tree)

        elif isinstance(expression.operator, (cst.LeftShift, cst.RightShift)):
            if not left_inferred.is_integer:
                raise CompilerError(f"Unsupported binary operation for type {left_inferred.type}", context)
            if not right_inferred.is_integer:
                raise CompilerError(f"Unsupported binary operation for type {right_inferred.type}", context)

            # We only infer the right hand side sinde it never needs to be more than 8 bit.
            if right_inferred.type == "int":
                infer_tree(right_tree, CoreType("uint8"), context)

            inferred[expression] = CoreType(
                left_inferred.type,
                left_inferred.pointed_type,
                const=left_inferred.const,
                extern=left_inferred.extern,
                return_padding=left_inferred.return_padding,
            )
            inferred.update(left_tree)
            inferred.update(right_tree)

        return inferred

    elif isinstance(expression, cst.Call):
        function_prototype = get_function_prototype(expression, stack, [*refs, *builtin_functions()], local_consts, context)
        args, arg_types = get_function_params(expression, function_prototype, context)

        for i, (arg, argtype) in enumerate(zip(args, arg_types)):
            arg_inferred = infer_expr_types_impl(arg.value, stack, refs, local_consts, context.wrap(arg.value))

            if not type_comparison_compatible(arg_inferred[arg.value], argtype):
                raise CompilerError(f"Unsupported cast from {arg_inferred[arg.value].type} to {argtype.type} in function call parameter {i + 1}", context)

            # Special case for functions like abs(), min() and max() where the input and output are both inferred.
            if argtype.type != "int":
                infer_tree(arg_inferred, argtype, context)
            inferred.update(arg_inferred)

        inferred[expression] = function_prototype.return_type
        return inferred

    elif isinstance(expression, cst.Comparison):
        left_tree = infer_expr_types_impl(expression.left, stack, refs, local_consts, context.wrap(expression.left))
        for comparison in expression.comparisons:
            right_tree = infer_expr_types_impl(comparison.comparator, stack, refs, local_consts, context.wrap(comparison.comparator))

            # Infer constant widths based on comparison types.
            if left_tree[expression.left].type == "int" and right_tree[comparison.comparator].type != "int":
                infer_tree(left_tree, right_tree[comparison.comparator], context)
            if left_tree[expression.left].type != "int" and right_tree[comparison.comparator].type == "int":
                infer_tree(right_tree, left_tree[expression.left], context)
            if left_tree[expression.left].type == "string" and right_tree[comparison.comparator].type != "string":
                infer_tree(left_tree, right_tree[comparison.comparator], context)
            if left_tree[expression.left].type != "string" and right_tree[comparison.comparator].type == "string":
                infer_tree(right_tree, left_tree[expression.left], context)

            # Verify that we're comparing two equivalent types.
            if not type_comparison_compatible(left_tree[expression.left], right_tree[comparison.comparator]):
                raise CompilerError(f"Unsupported comparison of types {left_tree[expression.left].type} and {right_tree[comparison.comparator].type}", context)
            if left_tree[expression.left].is_unsigned != right_tree[comparison.comparator].is_unsigned:
                raise CompilerError(f"Unsupported comparison of types {left_tree[expression.left].type} and {right_tree[comparison.comparator].type}", context)

            inferred.update(right_tree)

        inferred[expression] = CoreType("bool")
        inferred.update(left_tree)
        return inferred

    elif isinstance(expression, cst.BooleanOperation):
        inferred.update(infer_expr_types_impl(expression.left, stack, refs, local_consts, context.wrap(expression.left)))
        inferred.update(infer_expr_types_impl(expression.right, stack, refs, local_consts, context.wrap(expression.right)))

        left_inferred = inferred[expression.left]
        right_inferred = inferred[expression.right]
        if not left_inferred.is_bool:
            raise CompilerError(f"Unsupported non-boolean type {left_inferred.type} in boolean expression", context)
        if not right_inferred.is_bool:
            raise CompilerError(f"Unsupported non-boolean type {right_inferred.type} in boolean expression", context)

        inferred[expression] = CoreType("bool")
        return inferred

    elif isinstance(expression, cst.IfExp):
        body_tree = infer_expr_types_impl(expression.body, stack, refs, local_consts, context.wrap(expression.body))
        orelse_tree = infer_expr_types_impl(expression.orelse, stack, refs, local_consts, context.wrap(expression.orelse))
        inferred.update(infer_expr_types_impl(expression.test, stack, refs, local_consts, context.wrap(expression.test)))

        body_inferred = body_tree[expression.body]
        orelse_inferred = orelse_tree[expression.orelse]
        if not type_comparison_compatible(body_inferred, orelse_inferred):
            raise CompilerError(f"Unsupported mixed types {body_inferred.type} and {orelse_inferred.type} in if expression", context)
        if body_inferred.is_unsigned != orelse_inferred.is_unsigned:
            raise CompilerError(f"Unsupported mixed types {body_inferred.type} and {orelse_inferred.type} in if expression", context)

        # Infer constants and pick the widest of the two sides for this expression's type.
        if orelse_inferred.type == "int":
            if body_inferred.type != "int":
                infer_tree(orelse_tree, body_inferred, context)

            # Just arbitrarily pick the left, which could be an unspecified int as well.
            picked = body_inferred

        elif body_inferred.type == "int" and orelse_inferred != "int":
            # Pick the right since it is specified, the left will have to be filled in later.
            infer_tree(body_tree, orelse_inferred, context)
            picked = orelse_inferred

        elif orelse_inferred.type == "string":
            if body_inferred.type != "string":
                infer_tree(orelse_tree, body_inferred, context)

            # Just arbitrarily pick the left, which could be an unspecified int as well.
            picked = body_inferred

        elif body_inferred.type == "string" and orelse_inferred != "string":
            # Pick the right since it is specified, the left will have to be filled in later.
            infer_tree(body_tree, orelse_inferred, context)
            picked = orelse_inferred

        elif body_inferred.size > orelse_inferred.size:
            # Pick the left because it's wider than the right.
            picked = body_inferred

        else:
            # Pick the right because its either wider than the left, or equivalent in width.
            picked = orelse_inferred

        inferred[expression] = CoreType(picked.type, picked.pointed_type, const=picked.const, extern=picked.extern, return_padding=picked.return_padding)
        return inferred

    elif isinstance(expression, cst.Subscript):
        array_tree = infer_expr_types_impl(expression.value, stack, refs, local_consts, context.wrap(expression.value))
        array_inferred = array_tree[expression.value]
        if array_inferred.type == "string":
            infer_tree(array_tree, CoreType("str"), context)
        if not array_inferred.is_string:
            raise CompilerError(f"Unsupported non-string type {array_inferred.type} in subscript expression", context)

        if len(expression.slice) != 1:
            raise CompilerError("Unsupported slice count in subscript expression", context)
        slice_or_index = expression.slice[0].slice

        if isinstance(slice_or_index, cst.Index):
            index_tree = infer_expr_types_impl(slice_or_index.value, stack, refs, local_consts, context.wrap(slice_or_index.value))
            index_type = index_tree[slice_or_index.value]

            if index_type.type == "int":
                infer_tree(index_tree, CoreType("uint8"), context)
            if not index_type.is_integer:
                raise CompilerError(f"Unsupported non-integer index type {index_type.type} in subscript expression", context)

            inferred.update(array_tree)
            inferred.update(index_tree)
            inferred[expression] = CoreType("char")

        elif isinstance(slice_or_index, cst.Slice):
            if slice_or_index.step is not None:
                raise CompilerError("Unsupported step for slice in subscript expression", context)

            for node in [slice_or_index.lower, slice_or_index.upper]:
                if node is None:
                    continue

                slice_tree = infer_expr_types_impl(node, stack, refs, local_consts, context.wrap(node))
                slice_type = slice_tree[node]

                if slice_type.type == "int":
                    infer_tree(slice_tree, CoreType("uint8", const=True), context)
                if not slice_type.is_integer:
                    raise CompilerError(f"Unsupported non-integer index type {slice_type.type} in subscript expression", context)

                inferred.update(slice_tree)

            inferred.update(array_tree)
            inferred[expression] = CoreType("str", length=array_inferred.length)

        else:
            raise Exception("Logic error, unexpected node {slice_or_index} for subscript slice!")

        return inferred

    elif isinstance(expression, cst.FormattedString):
        for part in expression.parts:
            if isinstance(part, cst.FormattedStringText):
                inferred[part] = CoreType("str", length=len(part.value) + 1, const=True)
            elif isinstance(part, cst.FormattedStringExpression):
                expr_tree = infer_expr_types_impl(part.expression, stack, refs, local_consts, context.wrap(part.expression))
                expr_type = expr_tree[part.expression]

                if expr_type.type in {"int", "string"}:
                    infer_tree(expr_tree, CoreType("any"), context)

                inferred.update(expr_tree)
            else:
                raise Exception("Logic error, unexpected node in f-string!")

        inferred[expression] = CoreType("str", const=True)
        return inferred

    else:
        raise CompilerError(f"Unsupported expression type {expression} in type inferencer!", context)


def generate_expr(
    expression: cst.BaseExpression,
    destination: Optional[str],
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    compiled = Sections(code=[context.comment()])

    if destination is not None:
        dsize = stack.sizeof(destination)
        dtype = stack.typeof(destination)
        if dsize is None:
            raise Exception("Logic error, couldn't determine size of expression destination!")
        if dtype is None:
            raise Exception("Logic error, couldn't determine type of expression destination!")
    else:
        dsize = 0
        dtype = VoidType

    types: Dict[cst.CSTNode, CoreType] = infer_expr_types(expression, dtype, stack, refs, local_consts, context)

    if destination is not None and dsize == 1:
        # We can potentially keep the math in the A register!
        clobbers.add("A")

        if dtype.is_integer:
            if dtype.is_unsigned:
                dest = "register(A, uint8)"
            elif dtype.is_signed:
                dest = "register(A, int8)"
            else:
                raise Exception("Logic error, unexpected type {dtype} for register allocation!")
        elif dtype.is_bool:
            dest = "register(A, bool)"
        elif dtype.is_char:
            dest = "register(A, char)"
        else:
            raise Exception("Logic error, unexpected type {dtype} for register allocation!")

        compiled += generate_expr_internal(expression, dest, types, stack, clobbers, allocations, refs, local_consts, context)
        compiled += generate_move_to(destination, stack, clobbers, context)
        compiled.append_code("  STORE A")
    else:
        # Just do stack-based operations.
        compiled += generate_expr_internal(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

    if destination is not None:
        # We're gonna assign to this, so it should be considered initialized. Do this here instead of at the top
        # so we can catch variables assigning from themselves when unassigned.
        stack.init(destination)

    return compiled


def global_variable_assign(
    assign_target: GlobalVariable,
    assign_value: cst.BaseExpression,
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    compiled = Sections(code=[context.comment()])

    if assign_target.type.is_string:
        # We don't need to generate the expression into a temporary variable and copy it, we just need to strcpy
        # to the destination. That's easiest, however, if we pretend like it's going into a temporary destination,
        # so we don't have to teach all of the downstream functions to look up global destinations.
        clobbers.add("A")

        expr_temp = expr_temp_name()
        stack.alloc(StackVar(expr_temp, assign_target.type, initialized=True))

        compiled += generate_move_to(expr_temp, stack, clobbers, context, offset=-1)
        compiled.append_code(f"  PUSHADDR {assign_target.name}")
        stack.location += 2

        compiled += generate_expr(assign_value, expr_temp, stack, clobbers, allocations, refs, local_consts, context.wrap(assign_value))
        stack.free(expr_temp)

    else:
        # To grab a global variable offset, we need to use the SPC. To copy we need A.
        clobbers.add("SPC")
        clobbers.add("A")

        expr_temp = expr_temp_name()
        stack.alloc(StackVar(expr_temp, assign_target.type))

        compiled += generate_expr(assign_value, expr_temp, stack, clobbers, allocations, refs, local_consts, context.wrap(assign_value))

        for i in range(assign_target.type.size):
            # First, we need to set the SPC to our variable pointer, which clobbers A.
            if i == 0:
                compiled.append_code("  SWAP PC, SPC")
                compiled.append_code(f"  SETPC {assign_target.name}, {assign_target.type.size - 1}")
                compiled.append_code("  SWAP PC, SPC")

            compiled += generate_move_to(expr_temp, stack, clobbers, context, offset=i)
            compiled.append_code("  LOAD A")

            # Now, we need to copy the loaded A from our current expression result to the global value.
            if i == 0:
                compiled.append_code("  SWAP PC, SPC")
                compiled.append_code("  STORE A")
                compiled.append_code("  SWAP PC, SPC")
            else:
                compiled.append_code("  SWAP PC, SPC")
                compiled.append_code("  DECPC")
                compiled.append_code("  STORE A")
                compiled.append_code("  SWAP PC, SPC")

        stack.free(expr_temp)

    return compiled


def generate_assign_expr(
    assign_target: cst.BaseExpression,
    assign_annotation: Optional[cst.Annotation],
    assign_value: Optional[cst.BaseExpression],
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    compiled = Sections(code=[context.comment()])

    assign_type = get_type(assign_annotation.annotation, local_consts, allow_array=True) if assign_annotation is not None else None

    if isinstance(assign_target, cst.Subscript):
        if len(assign_target.slice) != 1:
            raise CompilerError("Unsupported slice count in subscript assignment", context)
        slice_or_index = assign_target.slice[0].slice

        if not isinstance(slice_or_index, cst.Index):
            raise CompilerError("Unsupported slice in subscript assignment", context)

        if not isinstance(assign_target.value, cst.Name):
            raise CompilerError("Unsupported name for subscript assignment", context)

        assign_name = assign_target.value.value
        assign_offset = slice_or_index.value

        if assign_type is not None:
            raise CompilerError("Unsupported type for subscript assignment", context)

        if assign_value is None:
            raise CompilerError("Expecting initialization value for subscript assignment", context)

        assign_types: Dict[cst.CSTNode, CoreType] = infer_expr_types(assign_value, CoreType("char"), stack, refs, local_consts, context)
        if not assign_types[assign_value].is_char:
            raise CompilerError(f"Unsupported non-character assignment {assign_types[assign_value].type} in subscript assignment", context)

        offset_types: Dict[cst.CSTNode, CoreType] = infer_expr_types(assign_offset, CoreType("uint8"), stack, refs, local_consts, context)
        if not offset_types[assign_offset].is_integer:
            raise CompilerError(f"Unsupported non-integer offset {offset_types[assign_offset].type} in subscript assignment", context)

        # We're going to clobber the SPC and A register to assign the value.
        clobbers.add("SPC")
        clobbers.add("A")

        # Figure out if this is a global or local variable assignment.
        orig_type = stack.typeof(assign_name)
        global_var = global_by_name(refs, assign_name)
        if global_var is not None:
            # This is a global variable assignment. No need for checking if it's marked since array access
            # is done without initializing.
            if global_var.type.const:
                raise CompilerError(f"Cannot assign to variable {assign_name!r} declared const", context)

            compiled.append_code("  SWAP PC, SPC")
            compiled.append_code(f"  SETPC {assign_name}")
            compiled.append_code("  SWAP PC, SPC")

        elif orig_type is None:
            # For assignment, we need to simply check if it's const.
            if const_by_name(local_consts, assign_name) is not None:
                raise CompilerError(f"Cannot assign to variable {assign_name!r} declared const", context)
            else:
                raise CompilerError(f"Unknown local variable {assign_name!r} in subscript assignment", context)

        elif orig_type is not None:
            if orig_type.const:
                raise CompilerError(f"Cannot assign to variable {assign_name!r} declared const", context)
            if not orig_type.is_string:
                raise CompilerError(f"Unsupported subscript assignment to variable {assign_name!r}", context)
            if not stack.initof(assign_name):
                raise CompilerError(f"Use of uninitialized variable {assign_name!r}", context)

            compiled += generate_move_to(assign_name, stack, clobbers, context, offset=1)
            compiled.append_code("  POP SPC")
            stack.move(-2)
            compiled.code += comment_stack(stack)

        # Now, calculate the offset we need to assign at.
        compiled += generate_expr_internal(assign_offset, "register(A, uint8)", offset_types, stack, clobbers, allocations, refs, local_consts, context.wrap(assign_offset))

        compiled.append_code("  SWAP PC, SPC")
        compiled.append_code("  ADDPC")
        compiled.append_code("  SWAP PC, SPC")

        # Now, calculate the character that we're assigning.
        compiled += generate_expr_internal(assign_value, "register(A, char)", assign_types, stack, clobbers, allocations, refs, local_consts, context.wrap(assign_value))

        compiled.append_code("  SWAP PC, SPC")
        compiled.append_code("  STORE A")
        compiled.append_code("  SWAP PC, SPC")

        return compiled

    elif isinstance(assign_target, cst.Name):
        assign_name = assign_target.value

        global_var = global_by_name(refs, assign_name)
        if global_var is not None and global_var.marked:
            # This is a global variable assignment.
            if assign_value is None:
                raise CompilerError("Unsupported global variable assignment", context)

            compiled += global_variable_assign(global_var, assign_value, stack, clobbers, allocations, refs, local_consts, context)
            return compiled

        # See if this is a re-assign or a definition.
        orig_loc = stack.absfind(assign_name)
        needs_alloc = False

        if orig_loc is None:
            # For definitions, we need a type. For constants, we need an initial value.
            if const_by_name(local_consts, assign_name) is not None:
                raise CompilerError(f"Cannot assign to variable {assign_name!r} declared const", context)

            if assign_type is None:
                raise CompilerError("Unsupported type for local variable definition", context)

            if assign_type.const and assign_value is None:
                raise CompilerError("Expecting initialization value for local const definition", context)

            if assign_type.is_string and not assign_type.const and not assign_type.is_array:
                raise CompilerError("Expecting length specifier for local string definition", context)

            needs_alloc = True

        else:
            # Variables cannot be re-assigned with types. Variables cannot be re-assigned without values.
            if assign_type is not None:
                raise CompilerError("Unsupported type redefinition for local variable assignment", context)
            if assign_value is None:
                raise CompilerError("Unsupported local variable assignment", context)

            # Make sure we're not overwriting a const.
            stack_var = stack.at(orig_loc)
            if stack_var is None:
                raise Exception(f"Logic error, could not find stack variable for {assign_name} after identifying it exists!")

            if stack_var.const:
                raise CompilerError(f"Cannot assign to variable {stack_var.name!r} declared const", context)

        # Now, if relevant, generate the expression for the assignment and put it in the stack variable.
        if assign_value is not None:
            if not isinstance(assign_value, cst.BaseExpression):
                raise CompilerError(f"Cannot assign local variable with results of {assign_value}", context)

            if assign_type is not None and assign_type.const and not assign_type.is_string:
                try:
                    # Constant evaluation, make sure it's not redefined.
                    if const_by_name(local_consts, assign_name) is not None:
                        raise CompilerError(f"Cannot assign to variable {assign_name!r} declared const", context)

                    value = codegen_eval(assign_value, local_consts)
                    local_consts.append(Constant(assign_name, assign_type, value))
                    return compiled
                except NonConstantExpressionException:
                    pass

            if needs_alloc:
                # Allocate space on the stack for this local variable.
                if assign_type is None:
                    raise Exception("Logic error, we should always have a type in this condition!")
                stack.alloc(StackVar(assign_name, assign_type))

            compiled += generate_expr(assign_value, assign_name, stack, clobbers, allocations, refs, local_consts, context.wrap(assign_value))

        else:
            if needs_alloc:
                # Allocate space on the stack for this local variable.
                if assign_type is None:
                    raise Exception("Logic error, we should always have a type in this condition!")
                stack.alloc(StackVar(assign_name, assign_type))

    else:
        # Not one of our supported expression types.
        raise CompilerError("Unsupported name for local variable definition", context)

    return compiled


def generate_augassign_expr(
    assign_target: cst.BaseExpression,
    assign_op: cst.BaseAugOp,
    assign_value: cst.BaseExpression,
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> Sections:
    # Simply map this onto an existing non-augmented assign and generate the code for that.
    operator: cst.BaseBinaryOp
    if isinstance(assign_op, cst.AddAssign):
        operator = cst.Add()
    elif isinstance(assign_op, cst.BitAndAssign):
        operator = cst.BitAnd()
    elif isinstance(assign_op, cst.BitOrAssign):
        operator = cst.BitOr()
    elif isinstance(assign_op, cst.BitXorAssign):
        operator = cst.BitXor()
    elif isinstance(assign_op, cst.DivideAssign):
        operator = cst.Divide()
    elif isinstance(assign_op, cst.FloorDivideAssign):
        operator = cst.FloorDivide()
    elif isinstance(assign_op, cst.LeftShiftAssign):
        operator = cst.LeftShift()
    elif isinstance(assign_op, cst.ModuloAssign):
        operator = cst.Modulo()
    elif isinstance(assign_op, cst.MultiplyAssign):
        operator = cst.Multiply()
    elif isinstance(assign_op, cst.PowerAssign):
        operator = cst.Power()
    elif isinstance(assign_op, cst.RightShiftAssign):
        operator = cst.RightShift()
    elif isinstance(assign_op, cst.SubtractAssign):
        operator = cst.Subtract()
    else:
        raise CompilerError("Unsupported augmented assign statement", context)

    op = cst.BinaryOperation(left=assign_target, right=assign_value, operator=operator)
    return generate_assign_expr(
        assign_target,
        None,
        op,
        stack,
        clobbers,
        allocations,
        refs,
        local_consts,
        context.virtual(op),
    )


def generate_if_statement(
    statement: cst.If,
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    function_type: CoreType,
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    loop: Optional[LoopInfo],
    local_consts: List[Constant],
    context: Context,
) -> Tuple[Sections, bool, bool]:
    compiled = Sections()

    # First, we need to infer the expression type, so we can figure out if we need to implicitly coerce the value.
    types: Dict[cst.CSTNode, CoreType] = infer_expr_types(statement.test, CoreType("bool"), stack, refs, local_consts, context)

    if not types[statement.test].is_bool:
        test_coerced = create_call("bool", [statement.test])
        types[test_coerced] = CoreType("bool")

        compiled += generate_expr_internal(
            test_coerced, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.virtual(test_coerced).wrap(test_coerced)
        )
    else:
        compiled += generate_expr_internal(statement.test, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(statement.test))

    # Now, depending on if this if statement has an else body or not,
    if statement.orelse is None:
        # Simpler logic, no need to generate two labels for skipping between each, no worrying about unifying the stack.
        if_body_stack = stack.clone()
        child_compiled, _, _ = compile_chunk(
            statement.body, if_body_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=False,
        )

        # Not unifying the stack here because in the false case we skip the body and don't initialize.
        if stack.location != if_body_stack.location:
            # Arbitrarily choose the left side expression to fix up to the right.
            move_amount = stack.location - if_body_stack.location
            child_compiled += generate_move_by("move if body stack to original location", move_amount, if_body_stack, clobbers, context)

            if stack.location != if_body_stack.location:
                raise Exception("Logic error, stacks differ after fixup!")

        # Now, figure out how far we need to jump on false.
        child_length = get_assembled_length(child_compiled.code, refs, loop.labels if loop else [])
        false_case = local_label_name("false_case")
        if child_length > 32:
            insn = "LNGJUMPNZ"
        else:
            insn = "JRINZ"

        # Now, generate the code that actually performs the conditional if statement.
        compiled.append_code("  INV")
        compiled.append_code(f"  {insn} {false_case}")
        compiled += child_compiled
        compiled.append_code(f"{false_case}:")

        # Double-check our stack math one more time.
        if if_body_stack.location != stack.location:
            raise Exception("Logic error, stacks should have been the same location at this point!")

        # The last statement isn't always a return, because even if the true path returned,
        # we could still skip that for the false case. Same with continues.
        return compiled, False, False

    elif isinstance(statement.orelse, cst.Else):
        # This one can be compiled as if it was just a body like the statement.body
        if_body_stack = stack.clone()
        if_body_compiled, if_body_returned, if_body_continued = compile_chunk(
            statement.body, if_body_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=False,
        )

        else_body_stack = stack.clone()
        else_body_compiled, else_body_returned, else_body_continued = compile_chunk(
            statement.orelse.body, else_body_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=False,
        )

        false_case = local_label_name("false_case")

        # Only need somewhere to jump to if we don't return as our last instruction in the if body.
        if not if_body_returned:
            if_end = local_label_name("if_end")
            else_body_compiled.append_code(f"{if_end}:")

        # Unify initialization tracking across cloned stacks so we can identify all paths that don't lead to variable initialization.
        stack.unify(if_body_stack, else_body_stack)

        # Not asserting that both sides are the same size, because they could have defined local variables. We don't follow python's
        # scope rules for defining variables in sub-scopes propagating upwards. Instead we follow C scope style which makes it easier
        # to compile.
        if if_body_stack.location != else_body_stack.location:
            # Arbitrarily choose the if side to fix up to the else.
            move_amount = else_body_stack.location - if_body_stack.location
            if_body_compiled += generate_move_by("move if body stack to same spot as else body", move_amount, if_body_stack, clobbers, context)

        # Now, figure out the else size so we can jump past it in the body.
        else_length = get_assembled_length(else_body_compiled.code, refs, loop.labels if loop else [])
        if not if_body_returned:
            if else_length > 32:
                if_body_compiled.append_code(f"  LNGJUMP {if_end}")
            else:
                if_body_compiled.append_code(f"  JRI {if_end}")

        # Now, figure out the if body size. We can't just compile it because it would fail to find the jump at the end, which can
        # be differently sized depending on if its a JRI or a LNGJUMP. So, compiled the left and right, and subtract the right
        # length since we know it already.
        if_length = get_assembled_length([*if_body_compiled.code, *else_body_compiled.code], refs, loop.labels if loop else []) - else_length

        # Now, generate the code to figure out if the expression is true/false and
        # then jump to it.
        compiled.append_code("  INV")
        if if_length > 32:
            compiled.append_code(f"  LNGJUMPNZ {false_case}")
        else:
            compiled.append_code(f"  JRINZ {false_case}")
        compiled += if_body_compiled
        compiled.append_code(f"{false_case}:")
        compiled += else_body_compiled

        # Now, set the stack location for our current stack to the location that both
        # expressions leave it at.
        if if_body_stack.location != else_body_stack.location:
            raise Exception("Logic error, stacks should have been the same location at this point!")
        stack.location = if_body_stack.location

        return compiled, if_body_returned and else_body_returned, if_body_continued and else_body_continued

    elif isinstance(statement.orelse, cst.If):
        # We need to know what the stack was before, just in case the else body has all assignments but the if body doesn't.
        stack_before = stack.clone()

        # Need to compile this with the orelse if statement at the same level as us stack-wise, so this acts similarly
        # to the empty else case.
        if_body_stack = stack.clone()
        if_body_compiled, if_body_returned, if_body_continued = compile_chunk(
            statement.body, if_body_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=False,
        )

        else_body_compiled, else_body_returned, else_body_continued = generate_if_statement(
            statement.orelse, stack, clobbers, allocations, function_type, refs, loop, local_consts, context
        )

        false_case = local_label_name("false_case")

        # Only need somewhere to jump to if we don't return as our last instruction in the if body.
        if not if_body_returned:
            if_end = local_label_name("if_end")
            else_body_compiled.append_code(f"{if_end}:")

        # Not asserting that both sides are the same size, because they could have defined local variables. We don't follow python's
        # scope rules for defining variables in sub-scopes propagating upwards. Instead we follow C scope style which makes it easier
        # to compile.
        if if_body_stack.location != stack.location:
            # Arbitrarily choose the if side to fix up to the else.
            move_amount = stack.location - if_body_stack.location
            if_body_compiled += generate_move_by("move if body stack to same spot as else body", move_amount, if_body_stack, clobbers, context)

        # Clone the else body stack just to see if any of it got unified or not.
        else_body_stack = stack.clone()
        stack.unwind(stack_before)

        # Unify initialization tracking across cloned stacks so we can identify all paths that don't lead to variable initialization.
        # It's safe to do here unlike in the if with no else case, because the else body is going to do its own unification checks.
        stack.unify(if_body_stack, else_body_stack)

        # Now, figure out the else size so we can jump past it in the body.
        else_length = get_assembled_length(else_body_compiled.code, refs, loop.labels if loop else [])
        if not if_body_returned:
            if else_length > 32:
                if_body_compiled.append_code(f"  LNGJUMP {if_end}")
            else:
                if_body_compiled.append_code(f"  JRI {if_end}")

        # Now, figure out the if body size. We can't just compile it because it would fail to find the jump at the end, which can
        # be differently sized depending on if its a JRI or a LNGJUMP. So, compiled the left and right, and subtract the right
        # length since we know it already.
        if_length = get_assembled_length([*if_body_compiled.code, *else_body_compiled.code], refs, loop.labels if loop else []) - else_length

        # Now, generate the code to figure out if the expression is true/false and
        # then jump to it.
        compiled.append_code("  INV")
        if if_length > 32:
            compiled.append_code(f"  LNGJUMPNZ {false_case}")
        else:
            compiled.append_code(f"  JRINZ {false_case}")
        compiled += if_body_compiled
        compiled.append_code(f"{false_case}:")
        compiled += else_body_compiled

        # Double check our stack math one more time.
        if if_body_stack.location != stack.location:
            raise Exception("Logic error, stacks should have been the same location at this point!")

        return compiled, if_body_returned and else_body_returned, if_body_continued and else_body_continued

    else:
        raise Exception(f"Logic error, unexpected statement {statement.orelse} in orelse clause of if statement!")


def generate_while_statement(
    statement: cst.While,
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    function_type: CoreType,
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    parent_loop: Optional[LoopInfo],
    local_consts: List[Constant],
    context: Context,
) -> Tuple[Sections, bool, bool]:
    compiled = Sections()

    # First, we need to infer the expression type, so we can figure out if we need to implicitly coerce the value.
    types: Dict[cst.CSTNode, CoreType] = infer_expr_types(statement.test, CoreType("bool"), stack, refs, local_consts, context)

    # Now, figure out our loop control points so that break/continue can be handled inside the nested compiled_chunk,
    # and so that we can support else statements in while loops.
    test_label = local_label_name("loop_test")
    else_label = local_label_name("loop_else") if statement.orelse else None
    exit_label = local_label_name("loop_exit")
    loop = LoopInfo(stack.location, iter_label=test_label, else_label=else_label, exit_label=exit_label)

    # We're at the point we want to loop back to, so label it now, and generate the test itself.
    compiled.append_code(f"{test_label}:")

    if not types[statement.test].is_bool:
        test_coerced = create_call("bool", [statement.test])
        types[test_coerced] = CoreType("bool")

        compiled += generate_expr_internal(
            test_coerced, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.virtual(test_coerced).wrap(test_coerced)
        )
    else:
        compiled += generate_expr_internal(statement.test, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(statement.test))

    # Now, generate the code necessary to perform the loop, as well as optionally the else.
    if statement.orelse is None:
        loop_stack = stack.clone()
        loop_compiled, _, _ = compile_chunk(
            statement.body, loop_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=True,
        )

        # Now, figure out how far we need to jump on loop condition is false.
        child_length = get_assembled_length(loop_compiled.code, refs, loop.labels)
        if child_length > 32:
            insn = "LNGJUMPNZ"
        else:
            insn = "JRINZ"

        # Now, generate the code that actually performs the conditional loop statement.
        compiled.append_code("  INV")

        if loop.stack_location != stack.location:
            # If we're exiting, we have to put ourselves back to the right spot on the stack because
            # that's the spot we promised to be in when we exit the loop through a break.
            compiled.append_code("  SKIPIF ZF")

            move_amount = loop.stack_location - stack.location
            compiled += generate_move_by("move stack to same spot as beginning of loop check", move_amount, stack, clobbers, context)

        compiled.append_code(f"  {insn} {exit_label}")
        compiled += loop_compiled
        compiled.append_code(f"{exit_label}:")

        if stack.location != loop.stack_location:
            raise Exception("Logic error, didn't move stack back properly!")

        # The last statement isn't always a return, because even if the loop returned,
        # we could still skip that for the false loop control case.
        return compiled, False, False

    else:
        loop_stack = stack.clone()
        loop_compiled, _, _ = compile_chunk(
            statement.body, loop_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=True,
        )

        else_stack = stack.clone()
        else_compiled, _, _ = compile_chunk(
            statement.orelse.body, else_stack, clobbers, allocations, function_type, refs, parent_loop, local_consts, context, require_return=False, require_continue=False,
        )

        # We always jump to the else from the while conditional, so we don't need to move to our expected position until the end of the else.
        # Everyone jumping from within the loop will either jump to the conditional or straight to the exit, skipping the else case.
        if loop.stack_location != else_stack.location:
            move_amount = loop.stack_location - else_stack.location
            else_compiled += generate_move_by("move stack to same spot as beginning of loop check", move_amount, else_stack, clobbers, context)

        # Now, figure out how far we need to jump on loop condition is false.
        child_length = get_assembled_length(loop_compiled.code, refs, loop.labels)
        if child_length > 32:
            insn = "LNGJUMPNZ"
        else:
            insn = "JRINZ"

        # Now, generate the code that actually performs the conditional loop statement.
        compiled.append_code("  INV")
        compiled.append_code(f"  {insn} {else_label}")
        compiled += loop_compiled
        compiled.append_code(f"{else_label}:")
        compiled += else_compiled
        compiled.append_code(f"{exit_label}:")

        # Manually set the stack back to the location it was in when we started, because when we take the else case it does that as the last
        # instruction, and if somebody uses a "break" inside the loop it will move back to the stack location before jumping to the exit_label.
        stack.location = loop.stack_location

        # The last statement isn't always a return, because even if the loop returned,
        # we could still skip that for the false loop control case.
        return compiled, False, False


def get_range_params(statement: cst.BaseExpression) -> Optional[Tuple[cst.BaseExpression, cst.BaseExpression, cst.BaseExpression]]:
    if not isinstance(statement, cst.Call):
        return None

    if not isinstance(statement.func, cst.Name):
        return None
    if statement.func.value != "range":
        return None

    for arg in statement.args:
        # Don't support kwargs or star args for this.
        if arg.keyword or arg.star:
            return None

    # This looks to be correct, let's make sure that all 3 params are there, otherwise we will have to generate some ourselves.
    if len(statement.args) == 1:
        # This is just the end value, start is 0 and increment is 1.
        return (cst.Integer("0"), statement.args[0].value, cst.Integer("1"))
    elif len(statement.args) == 2:
        # This is a start and end value, and increment is 1 by default.
        return (statement.args[0].value, statement.args[1].value, cst.Integer("1"))
    elif len(statement.args) == 3:
        # This is a start, end and increment value.
        return (statement.args[0].value, statement.args[1].value, statement.args[2].value)
    else:
        return None


def generate_for_statement(
    statement: cst.For,
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    function_type: CoreType,
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    parent_loop: Optional[LoopInfo],
    local_consts: List[Constant],
    context: Context,
) -> Tuple[Sections, bool, bool]:
    compiled = Sections()

    # First, we need to figure out if this is a for x in range() statement, which is the only type of iterator we support.
    range_params = get_range_params(statement.iter)
    if range_params is None:
        raise CompilerError("Unsupported if statement iterator", context)

    # Make sure that any fabricated nodes we created in the range params helper are recognized.
    context = context.virtual(range_params[0]).virtual(range_params[1]).virtual(range_params[2])

    # Now, we need to be sure we know the type of the iterator variable.
    if not isinstance(statement.target, cst.Name):
        raise CompilerError("Unsupported if statement iteration variable", context)

    iterator_dest = statement.target.value
    iterator_type = stack.typeof(iterator_dest)
    if iterator_type is None:
        raise CompilerError(f"Undefined variable reference to {iterator_dest!r}", context)

    # First we want to generate the iterator initialization.
    compiled += generate_assign_expr(
        statement.target,
        None,
        range_params[0],
        stack,
        clobbers,
        allocations,
        refs,
        local_consts,
        context,
    )

    # Now, figure out our loop control points so that break/continue can be handled inside the nested compiled_chunk,
    # and so that we can support else statements in for loops.
    test_label = local_label_name("loop_test")
    increment_label = local_label_name("loop_increment")
    else_label = local_label_name("loop_else") if statement.orelse else None
    exit_label = local_label_name("loop_exit")
    loop = LoopInfo(stack.location, iter_label=increment_label, else_label=else_label, exit_label=exit_label)

    # Since everything will be jumping back to the increment label, we need to make sure that it is generated from the
    # perspective of the stack at this point.
    increment = cst.BinaryOperation(left=statement.target, operator=cst.Add(), right=range_params[2])
    types = infer_expr_types(increment, iterator_type, stack, refs, local_consts, context)

    increment_stack = stack.clone()
    increment_compiled = generate_expr_internal(
        increment,
        iterator_dest,
        types,
        increment_stack,
        clobbers,
        allocations,
        refs,
        local_consts,
        context.virtual(increment),
    )

    if loop.stack_location != increment_stack.location:
        move_amount = loop.stack_location - increment_stack.location
        increment_compiled += generate_move_by("move stack to same spot as beginning of loop check", move_amount, increment_stack, clobbers, context)

    # We're at the point we want to loop back to, so generate the test itself.
    comparison = cst.Comparison(left=statement.target, comparisons=[cst.ComparisonTarget(cst.LessThan(), range_params[1])])
    types = infer_expr_types(comparison, CoreType("bool"), stack, refs, local_consts, context)

    test_compiled = generate_expr_internal(
        comparison,
        "register(A, bool)",
        types,
        stack,
        clobbers,
        allocations,
        refs,
        local_consts,
        context.virtual(comparison),
    )

    # Now, generate the code necessary to perform the loop, as well as optionally the else.
    if statement.orelse is None:
        loop_stack = stack.clone()
        loop_compiled, _, _ = compile_chunk(
            statement.body, loop_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=True,
        )

        # Now, figure out how far we need to jump on loop condition is false.
        child_length = get_assembled_length(loop_compiled.code, refs, loop.labels) + get_assembled_length(increment_compiled.code, refs, loop.labels)
        if child_length > 32:
            conditionalinsn = "LNGJUMPNZ"
        else:
            conditionalinsn = "JRINZ"

        # Now, generate the code that actually performs the conditional loop statement.
        test_compiled.append_code("  INV")

        if loop.stack_location != stack.location:
            # If we're exiting, we have to put ourselves back to the right spot on the stack because
            # that's the spot we promised to be in when we exit the loop through a break.
            test_compiled.append_code("  SKIPIF ZF")

            move_amount = loop.stack_location - stack.location
            test_compiled += generate_move_by("move stack to same spot as beginning of loop check", move_amount, stack, clobbers, context)

        test_compiled.append_code(f"  {conditionalinsn} {exit_label}")

        # Also figure out how far we have to jump for the increment back to loop case.
        increment_length = get_assembled_length(test_compiled.code, refs, loop.labels) + child_length
        if increment_length > 32:
            incrementinsn = "LNGJUMP"
        else:
            incrementinsn = "JRI"

        compiled.append_code(f"{test_label}:")
        compiled += test_compiled
        compiled += loop_compiled
        compiled.append_code(f"{increment_label}:")
        compiled += increment_compiled
        compiled.append_code(f"  {incrementinsn} {test_label}")
        compiled.append_code(f"{exit_label}:")

        if stack.location != loop.stack_location:
            raise Exception("Logic error, didn't move stack back properly!")

        # The last statement isn't always a return, because even if the loop returned,
        # we could still skip that for the false loop control case.
        return compiled, False, False

    else:
        # Generate both the loop stack and the else stack from the same stack location, because we jump to the else stack from the
        # same spot at the end of the test where we would fall into the loop stack.
        loop_stack = stack.clone()
        loop_compiled, _, _ = compile_chunk(
            statement.body, loop_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=True,
        )

        else_stack = stack.clone()
        else_compiled, _, _ = compile_chunk(
            statement.orelse.body, else_stack, clobbers, allocations, function_type, refs, parent_loop, local_consts, context, require_return=False, require_continue=False,
        )

        # We always jump to the else from the loop conditional, so we don't need to move to our expected position until the end of the else.
        # Everyone jumping from within the loop will either jump to the increment code or straight to the exit, skipping the else case.
        if loop.stack_location != else_stack.location:
            move_amount = loop.stack_location - else_stack.location
            else_compiled += generate_move_by("move stack to same spot as beginning of loop check", move_amount, else_stack, clobbers, context)

        # Now, figure out how far we need to jump on loop condition is false.
        child_length = get_assembled_length(loop_compiled.code, refs, loop.labels) + get_assembled_length(increment_compiled.code, refs, loop.labels)
        if child_length > 32:
            conditionalinsn = "LNGJUMPNZ"
        else:
            conditionalinsn = "JRINZ"

        # Now, generate the code that actually performs the conditional loop statement.
        test_compiled.append_code("  INV")
        test_compiled.append_code(f"  {conditionalinsn} {else_label}")

        # Also figure out how far we have to jump for the increment back to loop case.
        increment_length = get_assembled_length(test_compiled.code, refs, loop.labels) + child_length
        if increment_length > 32:
            incrementinsn = "LNGJUMP"
        else:
            incrementinsn = "JRI"

        compiled.append_code(f"{test_label}:")
        compiled += test_compiled
        compiled += loop_compiled
        compiled.append_code(f"{increment_label}:")
        compiled += increment_compiled
        compiled.append_code(f"  {incrementinsn} {test_label}")
        compiled.append_code(f"{else_label}:")
        compiled += else_compiled
        compiled.append_code(f"{exit_label}:")

        # Manually set the stack back to the location it was in when we started, because when we take the else case it does that as the last
        # instruction, and if somebody uses a "break" inside the loop it will move back to the stack location before jumping to the exit_label.
        stack.location = loop.stack_location

        # The last statement isn't always a return, because even if the loop returned,
        # we could still skip that for the false loop control case.
        return compiled, False, False

    return compiled, False, False


def generate_continue(
    stack: Stack,
    clobbers: Set[str],
    loop: Optional[LoopInfo],
    context: Context,
) -> Sections:
    compiled = Sections()

    if loop is None:
        raise CompilerError("Attempting to continue outside of active loop", context)

    move_amount = loop.stack_location - stack.location
    compiled += generate_move_by("move stack to same spot as beginning of loop check", move_amount, stack, clobbers, context)
    compiled.append_code(f"  LNGJUMP {loop.iter_label}")
    return compiled


def generate_break(
    stack: Stack,
    clobbers: Set[str],
    loop: Optional[LoopInfo],
    context: Context,
) -> Sections:
    compiled = Sections()

    if loop is None:
        raise CompilerError("Attempting to break outside of active loop", context)

    move_amount = loop.stack_location - stack.location
    compiled += generate_move_by("move stack to same spot as beginning of loop check", move_amount, stack, clobbers, context)
    compiled.append_code(f"  LNGJUMP {loop.exit_label}")
    return compiled


def compile_chunk(
    chunk: cst.BaseSuite,
    stack: Stack,
    clobbers: Set[str],
    allocations: Dict[str, int],
    function_type: CoreType,
    refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
    loop: Optional[LoopInfo],
    local_consts: List[Constant],
    context: Context,
    *,
    require_return: bool,
    require_continue: bool,
) -> Tuple[Sections, bool, bool]:
    compiled = Sections()

    # We need to track which global variables we know about, so that we can support local assignment over global names.
    refs_copy: List[Union[FunctionPrototype, GlobalVariable]] = [x for x in refs if isinstance(x, FunctionPrototype)]
    globals_copy: List[GlobalVariable] = [GlobalVariable(x.name, x.type, x.marked) for x in refs if isinstance(x, GlobalVariable)]
    refs_copy += globals_copy

    last_statement_was_return = False
    last_statement_was_continue = False

    for statement in chunk.body:
        if isinstance(statement, cst.SimpleStatementLine):
            for simple_statement in statement.body:
                if isinstance(simple_statement, cst.Return):
                    if simple_statement.value is None:
                        # Simple return by itself, doesn't update the retval.
                        if function_type is not VoidType:
                            raise CompilerError("Returning nothing from a function marked with a return value", context)
                        compiled += generate_return(function_type, stack, clobbers, context.wrap(simple_statement))
                    else:
                        # Return of some sort of expression.
                        if function_type is VoidType:
                            raise CompilerError("Returning something from a function marked with no return value", context)

                        # Since we're performing one last expression before returning, we know that any
                        # parameters we'd be overwriting can be overwritten safely. So, figure out if
                        # we can relocate the retval.
                        if can_relocate_return(function_type, stack, clobbers, context):
                            stack.relocate("builtin(retval)", 0)

                        compiled += generate_expr(
                            simple_statement.value,
                            "builtin(retval)",
                            stack,
                            clobbers,
                            allocations,
                            refs_copy,
                            local_consts,
                            context.wrap(simple_statement.value),
                        )
                        compiled += generate_return(function_type, stack, clobbers, context.wrap(simple_statement))

                    # We lie here, because while the last statement wasn't a continue, it serves a similar purpose.
                    last_statement_was_return = True
                    last_statement_was_continue = True

                elif isinstance(simple_statement, cst.AnnAssign):
                    compiled += generate_assign_expr(
                        simple_statement.target,
                        simple_statement.annotation,
                        simple_statement.value,
                        stack,
                        clobbers,
                        allocations,
                        refs_copy,
                        local_consts,
                        context.wrap(simple_statement),
                    )
                    last_statement_was_return = False
                    last_statement_was_continue = False

                elif isinstance(simple_statement, cst.Assign):
                    if len(simple_statement.targets) != 1:
                        raise CompilerError("Unsupported multi-variable assignment", context.wrap(simple_statement))

                    compiled += generate_assign_expr(
                        simple_statement.targets[0].target,
                        None,
                        simple_statement.value,
                        stack,
                        clobbers,
                        allocations,
                        refs_copy,
                        local_consts,
                        context.wrap(simple_statement),
                    )
                    last_statement_was_return = False
                    last_statement_was_continue = False

                elif isinstance(simple_statement, cst.AugAssign):
                    compiled += generate_augassign_expr(
                        simple_statement.target,
                        simple_statement.operator,
                        simple_statement.value,
                        stack,
                        clobbers,
                        allocations,
                        refs_copy,
                        local_consts,
                        context.wrap(simple_statement),
                    )
                    last_statement_was_return = False
                    last_statement_was_continue = False

                elif isinstance(simple_statement, cst.Global):
                    for name in simple_statement.names:
                        global_name = name.name.value
                        for ref in refs_copy:
                            if isinstance(ref, GlobalVariable) and ref.name == global_name:
                                if ref.marked:
                                    raise CompilerError(f"Duplicate global declaration for {global_name}", context.wrap(simple_statement))
                                else:
                                    ref.mark()
                                break
                        else:
                            raise CompilerError(f"Unknown global variable {global_name}", context.wrap(simple_statement))

                    last_statement_was_return = False
                    last_statement_was_continue = False

                elif isinstance(simple_statement, cst.Expr):
                    # Expression without an assignment. Most likely a function call.
                    compiled += generate_expr(
                        simple_statement.value,
                        None,
                        stack,
                        clobbers,
                        allocations,
                        refs_copy,
                        local_consts,
                        context.wrap(simple_statement.value),
                    )

                    last_statement_was_return = False
                    last_statement_was_continue = False

                elif isinstance(simple_statement, cst.Pass):
                    # No-op statement for syntactic correctness since Python requires indentation. Funny enough,
                    # we implement it here with our own pass. How meta.
                    pass

                elif isinstance(simple_statement, cst.Break):
                    # We treat a break as a continue for tracking purposes since it finishes control flow for us.
                    compiled += generate_break(stack, clobbers, loop, context)
                    last_statement_was_return = False
                    last_statement_was_continue = True

                elif isinstance(simple_statement, cst.Continue):
                    compiled += generate_continue(stack, clobbers, loop, context)
                    last_statement_was_return = False
                    last_statement_was_continue = True

                else:
                    raise CompilerError(f"Unsupported node to compile {simple_statement}", context)

        elif isinstance(statement, cst.If):
            if_compiled, last_statement_was_return, last_statement_was_continue = generate_if_statement(
                statement,
                stack,
                clobbers,
                allocations,
                function_type,
                refs_copy,
                loop,
                local_consts,
                context.wrap(statement),
            )
            compiled += if_compiled

        elif isinstance(statement, cst.While):
            while_compiled, last_statement_was_return, last_statement_was_continue = generate_while_statement(
                statement,
                stack,
                clobbers,
                allocations,
                function_type,
                refs_copy,
                loop,
                local_consts,
                context.wrap(statement),
            )
            compiled += while_compiled

        elif isinstance(statement, cst.For):
            for_compiled, last_statement_was_return, last_statement_was_continue = generate_for_statement(
                statement,
                stack,
                clobbers,
                allocations,
                function_type,
                refs_copy,
                loop,
                local_consts,
                context.wrap(statement),
            )
            compiled += for_compiled

        else:
            # TODO: Import statements for forward refs to other modules.
            raise CompilerError(f"Unsupported node to compile {statement}", context)

    if require_return and not last_statement_was_return:
        # Simple return by itself, doesn't update the retval.
        if function_type is not VoidType:
            raise CompilerError("Function is missing a return statement", context)
        compiled += generate_return(function_type, stack, clobbers, context)
        last_statement_was_return = True
        last_statement_was_continue = True

    if require_continue and not last_statement_was_continue:
        compiled += generate_continue(stack, clobbers, loop, context)
        last_statement_was_continue = True

    return compiled, last_statement_was_return, last_statement_was_continue


def function_prototype(func: cst.FunctionDef, context: Context) -> FunctionPrototype:
    function_type = get_type(func.returns, [], allow_nopad=True, allow_array=True)
    function_params = func.params.params

    if function_type is None:
        raise CompilerError("Unsupported return type for function definition", context)

    if func.params.kwonly_params or func.params.posonly_params:
        raise CompilerError("Unsupported parameter definition for function definition", context)

    prototype = FunctionPrototype(func.name.value, function_type)
    stack: Stack = Stack(prototype.name)

    for func_param in function_params:
        if func_param.default is not None:
            # TODO: This wouldn't be terrible to support at some point in the future, so maybe we could?
            raise CompilerError(f"Function parameter {func_param.name.value} has unsupported default", context)

        # Function parameters are passed on the stack, so we must know their locations and types.
        param_type = get_type(func_param.annotation, [])
        if param_type is None:
            raise CompilerError(f"Expecting type for function parameter {func_param.name.value}", context)

        prototype.params.append(param_type)
        stack.alloc(StackVar(func_param.name.value, param_type))

    if function_type.return_padding and stack.size < function_type.size:
        # We need to request padding out to the return size.
        prototype.params.append(PaddingCoreType(function_type.size - stack.size))

    return prototype


def function(func: cst.FunctionDef, refs: Sequence[Union[FunctionPrototype, GlobalVariable]], context: Context) -> Sections:
    compiled = Sections()
    function_name = func.name.value
    function_type = get_type(func.returns, [], allow_nopad=True, allow_array=True)
    function_params = func.params.params
    stack: Stack = Stack(function_name)

    if function_type is None:
        raise CompilerError("Unsupported return type for function definition", context)

    if func.params.kwonly_params or func.params.posonly_params:
        raise CompilerError("Unsupported parameter definition for function definition", context)

    for func_param in function_params:
        if func_param.default is not None:
            raise CompilerError(f"Function parameter {func_param.name.value} has unsupported default", context)

        # Function parameters are passed on the stack, so we must know their locations and types.
        param_type = get_type(func_param.annotation, [])
        if param_type is None:
            raise CompilerError(f"Expecting type for function parameter {func_param.name.value}", context)

        try:
            stack.alloc(StackVar(func_param.name.value, param_type, initialized=True))
        except NotImplementedError:
            raise CompilerError(f"Unsupported type for function parameter {func_param.name.value}", context)

    if function_type.return_padding and stack.size < function_type.size:
        # We need to account for return type padding.
        for _ in range(function_type.size - stack.size):
            stack.alloc(StackVar("builtin(padding)", CoreType('int8')))

    # Need a spot on the stack for our return pointer that is placed when called.
    stack.alloc(StackVar("builtin(retptr)", CoreType("pointer", CoreType("void")), initialized=True))
    stack.location = stack.size - 1

    # Generate before and after call stack documentation.
    preamble: List[str] = []
    if stack.size > 0:
        preamble.append("  ; Stack layout just after call:")
    prevals: List[str] = []
    for entry in stack:
        for i in range(entry.size):
            if entry.location is None:
                raise Exception("Logic error, expected stack entry to have location!")
            prevals.append(f"  ; PC + {stack.size - (entry.location + i + 1)} - {entry.name}")
    preamble += reversed(prevals)
    if preamble:
        preamble.append("  ;")

    preamble.append("  ; Stack layout just before return:")
    fake_stack: Stack = Stack(function_name)
    if function_type is not VoidType:
        fake_stack.alloc(StackVar("builtin(retval)", function_type))
    fake_stack.alloc(StackVar("builtin(retptr)", CoreType("pointer", CoreType("void")), initialized=True))
    prevals = []
    for entry in fake_stack:
        for i in range(entry.size):
            if entry.location is None:
                raise Exception("Logic error, expected stack entry to have location!")
            prevals.append(f"  ; PC + {fake_stack.size - (entry.location + i + 1)} - {entry.name}")
    preamble += reversed(prevals)
    if preamble:
        preamble.append("  ;")

    # Temporary room for the return value, which will be placed after clobbers, but we need
    # somewhere so clobber calculation can work.
    temp_size = 0
    if function_type is not VoidType:
        temp_size = stack.alloc(StackVar("builtin(retval)", function_type))
        stack.move(temp_size)

    # First pass to figure out clobbers, but don't use up any variable names or label names.
    clobbers: Set[str] = set()

    push_names()
    compile_chunk(func.body, stack.clone(), clobbers, {}, function_type, refs, None, builtin_consts(), context, require_return=True, require_continue=False)
    pop_names()

    # Unwind our temporary return value location.
    if temp_size > 0:
        if stack[-1].name != "builtin(retval)":
            raise Exception("Logic error, top of stack isn't the retval temporary!")
        stack.move(-temp_size)
        stack.free("builtin(retval)")

    # Stick some padding between the retval and the saved retptr if we need to so
    # unwinding on return doesn't clobber part of the stack.
    padding_move_amt = 0
    while stack.size < (function_type.size + 2):
        stack.alloc(StackVar("builtin(padding)", CoreType('int8')))
        padding_move_amt += 1

    # Make sure we annotate the source with where we think we started on the stack.
    compiled.code += comment_stack(stack)

    if padding_move_amt > 0:
        compiled.append_code(f"  SUBPCI {padding_move_amt}" + comment_source("allocating padding"))
        stack.move(padding_move_amt)
        compiled.code += comment_stack(stack)

    # Now, let's save all of our clobbered values.
    cref = None
    if clobbers:
        cref = comment_ref()
        compiled.append_code(f"  ; Save clobbered registers {cref}")
    for clobber in sorted(clobbers):
        if clobber == "A":
            stack.alloc(StackVar("builtin(saved_a)", CoreType("uint8"), initialized=True))
            compiled.append_code("  PUSH A")
            stack.move(1)
            compiled.code += comment_stack(stack)
        elif clobber == "U":
            stack.alloc(StackVar("builtin(saved_u)", CoreType("uint8"), initialized=True))
            compiled.append_code("  PUSH U")
            stack.move(1)
            compiled.code += comment_stack(stack)
        elif clobber == "V":
            stack.alloc(StackVar("builtin(saved_v)", CoreType("uint8"), initialized=True))
            compiled.append_code("  PUSH V")
            stack.move(1)
            compiled.code += comment_stack(stack)
        elif clobber == "SPC":
            stack.alloc(StackVar("builtin(saved_spc)", CoreType("uint16"), initialized=True))
            compiled.append_code("  PUSH SPC")
            stack.move(2)
            compiled.code += comment_stack(stack)
        else:
            raise Exception(f"Logic error, unexpected clobber {clobber}!")

    if cref:
        compiled.append_code(f"  ; {cref}")

    # Make sure that we have room on the stack for the return value. Don't move at this point
    # because we might not want to generate instructions to move.
    if function_type is not VoidType:
        stack.alloc(StackVar("builtin(retval)", function_type))

    # Now, second pass to actually compile.
    chunk, _, _ = compile_chunk(func.body, stack, set(), {}, function_type, refs, None, builtin_consts(), context, require_return=True, require_continue=False)
    compiled += chunk

    # TODO: Function boundary is where we will end up optimizing redundant stack moves and load/store operations.

    # Finally, find any comments that comment on empty blocks after optimization, and remove them.
    compiled.code = remove_empty_comments(compiled.code)
    compiled_preamble = compiled.preamble
    if compiled_preamble:
        compiled_preamble.append("")
    compiled.preamble = []

    return Sections(
        code=remove_empty_lines([
            *compiled_preamble,
            f"{function_name}:",
            *preamble,
            *compiled.code,
        ]),
        data=compiled.data,
        init=compiled.init,
    )


def remove_empty_comments(code: List[str]) -> List[str]:
    # Clone this so we aren't mutating the input because that's bad form.
    code = code[:]

    pos = 0
    length = len(code)
    while pos < length:
        line = code[pos]

        if "##comment_ref_" in line:
            # Grab the ref itself.
            _, ref = line.split("##comment_ref_", 1)
            ref = (f"##comment_ref_{ref}").strip()

            # Find the closing ref.
            for end in range(pos + 1, length):
                if ref in code[end]:
                    break
            else:
                raise Exception(f"Logic error, could not find end ref for {ref}!")

            # Now, if the only thing between these two ref markers is comments, nuke all of it.
            should_nuke = True
            for check in range(pos, end):
                checkline = code[check]
                if not checkline.strip():
                    # Empty line, this counts as a comment.
                    continue

                if ";" not in checkline:
                    should_nuke = False
                    break

                meat, _ = checkline.split(";", 1)
                if meat.strip():
                    # There's an instruction here.
                    should_nuke = False
                    break

            if should_nuke:
                # Delete all of the lines including the start and end comment.
                for _ in range((end - pos) + 1):
                    code.pop(pos)
            else:
                # Just delete the end marker, and change the current line to not have the marker.
                code.pop(end)
                code[pos] = code[pos].replace(ref, "").rstrip()
                pos += 1

        else:
            pos += 1

        length = len(code)

    return code


def remove_empty_lines(code: List[str]) -> List[str]:
    # Clone this so we aren't mutating the input because that's bad form.
    code = code[:]

    while code and (not code[0].strip()):
        code.pop(0)

    while code and (not code[-1].strip()):
        code.pop(-1)

    return code


def is_assign_type_definition(assign: cst.Assign) -> bool:
    if len(assign.targets) != 1:
        return False

    target = assign.targets[0]
    if not isinstance(target.target, cst.Name):
        return False

    if target.target.value not in {"uint8", "int8", "uint16", "int16", "uint32", "int32", "pointer", "str", "char", "bool", "void"}:
        return False

    if not isinstance(assign.value, cst.Name):
        return False

    if assign.value.value not in {"int", "str", "bool", "None"}:
        return False

    return True


def is_annassign_type_definition(assign: cst.AnnAssign) -> bool:
    target = assign.target
    if not isinstance(target, cst.Name):
        return False

    if target.value not in {"uint8", "int8", "uint16", "int16", "uint32", "int32", "pointer", "str", "char", "bool", "void"}:
        return False

    if not isinstance(assign.value, cst.Name):
        return False

    if assign.value.value not in {"int", "str", "bool", "None"}:
        return False

    return True


def compile_module(module: str, code: str, refs: Sequence[Union[FunctionPrototype, GlobalVariable]]) -> Sections:
    parsed_module = cst.parse_module(code)

    # Make sure we have access to line/column numbers for errors.
    wrapper = cst.MetadataWrapper(parsed_module)
    metadata = wrapper.resolve(meta.PositionProvider)

    # A deep copy is made by the metadata wrapper, because LibCST is designed around safe mutations. We don't care
    # and only need a read-only copy.
    parsed_module = wrapper.module

    compiled = Sections()
    global_consts: List[Constant] = builtin_consts()
    global_vars: List[GlobalVariable] = []

    for statement in parsed_module.body:
        context = Context(module, statement, metadata)

        if isinstance(statement, cst.SimpleStatementLine):
            bodylines = statement.body
            if len(bodylines) != 1:
                raise CompilerError("Multi-statement lines are not supported", context)

            body = bodylines[0]
            if isinstance(body, cst.Assign):
                # This could be a mypy type assignment so that the python source files can be typechecked.
                if not is_assign_type_definition(body):
                    raise CompilerError("Global variable declarations must have a type", context)
            elif isinstance(body, cst.AnnAssign):
                if not is_annassign_type_definition(body):
                    compiled += generate_global_variable(body, global_vars, global_consts, context)
            elif isinstance(body, cst.ImportFrom):
                is_typing_import = False

                if isinstance(body.module, cst.Name) and body.module.value == "typing":
                    is_typing_import = True

                if not is_typing_import:
                    raise CompilerError("Arbitrary top-level statements are not supported", context)
            else:
                raise CompilerError("Arbitrary top-level statements are not supported", context)
        elif isinstance(statement, cst.FunctionDef):
            compiled += function(statement, refs, context)
        else:
            # TODO: What other statement types are we missing here?
            raise CompilerError("Unsupported statement {statement}", context)

        compiled.append_code("")

    compiled.code = remove_empty_lines(compiled.code)
    if compiled.preamble:
        raise Exception("Logic error, shouldn't have any unconsumed preamble!")

    return compiled


def parse_forward_refs(module: str, code: str) -> List[Union[FunctionPrototype, GlobalVariable]]:
    parsed_module = cst.parse_module(code)

    # Make sure we have access to line/column numbers for errors.
    wrapper = cst.MetadataWrapper(parsed_module)
    metadata = wrapper.resolve(meta.PositionProvider)

    # A deep copy is made by the metadata wrapper, because LibCST is designed around safe mutations. We don't care
    # and only need a read-only copy.
    parsed_module = wrapper.module

    prototypes: List[Union[FunctionPrototype, GlobalVariable]] = []
    names: Set[str] = set()

    for statement in parsed_module.body:
        context = Context(module, statement, metadata)

        if isinstance(statement, cst.FunctionDef):
            prototype = function_prototype(statement, context)
            if prototype.name in names:
                raise CompilerError("Duplicate function definition", context)
            names.add(prototype.name)

            prototypes.append(prototype)
        elif isinstance(statement, cst.SimpleStatementLine):
            bodylines = statement.body
            if len(bodylines) != 1:
                raise CompilerError("Multi-statement lines are not supported", context)

            body = bodylines[0]
            if isinstance(body, cst.AnnAssign):
                if not is_annassign_type_definition(body):
                    global_vars: List[GlobalVariable] = []
                    generate_global_variable(body, global_vars, [], context)
                    prototypes += global_vars

    return prototypes


def parse_and_compile_module(module: str, code: str) -> Sections:
    forward_refs: List[Union[FunctionPrototype, GlobalVariable]] = builtin_forward_refs()
    forward_refs += parse_forward_refs(module, code)
    return compile_module(module, code, forward_refs)


def builtin_functions() -> List[FunctionPrototype]:
    return [
        FunctionPrototype("len", RegisterCoreType("uint8", "A"), [CoreType("str")]),
        FunctionPrototype("str", CoreType("str"), [CoreType("any")]),
        FunctionPrototype("int", CoreType("int"), [CoreType("any")]),
        FunctionPrototype("peek", CoreType("any"), [CoreType("uint16")]),
        FunctionPrototype("poke", VoidType, [CoreType("uint16"), CoreType("any")]),
        FunctionPrototype("abs", CoreType("int"), [CoreType("int")]),
        FunctionPrototype("bool", CoreType("bool"), [CoreType("any")]),
        FunctionPrototype("chr", CoreType("char"), [CoreType("int")]),
        FunctionPrototype("ord", CoreType("int8"), [CoreType("char")]),
    ]


def builtin_consts() -> List[Constant]:
    return [
        Constant("True", CoreType("bool", const=True), value=True),
        Constant("False", CoreType("bool", const=True), value=False),
    ]


def builtin_forward_refs() -> List[Union[FunctionPrototype, GlobalVariable]]:
    prototypes: List[Union[FunctionPrototype, GlobalVariable]] = [
        # STDLIB string functions.
        FunctionPrototype("strcat", VoidType, [PreservedCoreType("str"), PreservedCoreType("str")]),
        FunctionPrototype("strcmp", RegisterCoreType("int8", "A"), [PreservedCoreType("str"), PreservedCoreType("str")]),
        FunctionPrototype("strcpy", VoidType, [PreservedCoreType("str"), PreservedCoreType("str")]),
        FunctionPrototype("strncpy", VoidType, [PreservedCoreType("str"), PreservedCoreType("str"), PreservedCoreType("uint8")]),
        FunctionPrototype("strlen", RegisterCoreType("uint8", "A"), [PreservedCoreType("str")]),

        # STDLIB string/integer conversion functions.
        FunctionPrototype("atoi8", RegisterCoreType("int8", "A"), [InOutCoreType("str")]),
        FunctionPrototype("atoi16", ParamReturnCoreType(1), [InOutCoreType("str"), OutCoreType("int16")]),
        FunctionPrototype("atoi32", ParamReturnCoreType(1), [InOutCoreType("str"), OutCoreType("int32")]),
        FunctionPrototype("itoa8", VoidType, [RegisterCoreType("int8", "A"), PreservedCoreType("str")]),
        FunctionPrototype("itoa16", VoidType, [PreservedCoreType("int16"), PreservedCoreType("str")]),
        FunctionPrototype("itoa32", VoidType, [PreservedCoreType("int32"), PreservedCoreType("str")]),
        FunctionPrototype("utoa8", VoidType, [RegisterCoreType("int8", "A"), PreservedCoreType("str")]),
        FunctionPrototype("utoa16", VoidType, [PreservedCoreType("int16"), PreservedCoreType("str")]),
        FunctionPrototype("utoa32", VoidType, [PreservedCoreType("int32"), PreservedCoreType("str")]),

        # STDLIB integer math functions.
        FunctionPrototype("abs8", RegisterCoreType("int8", "A"), [RegisterCoreType("int8", "A")]),
        FunctionPrototype("abs16", ParamReturnCoreType(0), [InOutCoreType("int16")]),
        FunctionPrototype("abs32", ParamReturnCoreType(0), [InOutCoreType("int32")]),
        FunctionPrototype("neg8", RegisterCoreType("int8", "A"), [PreservedCoreType("int8")]),
        FunctionPrototype("neg16", ParamReturnCoreType(0), [InOutCoreType("int16")]),
        FunctionPrototype("neg32", ParamReturnCoreType(0), [InOutCoreType("int32")]),
        FunctionPrototype("add8", RegisterCoreType("int8", "A"), [PreservedCoreType("int8"), PreservedCoreType("int8")]),
        FunctionPrototype("add16", CoreType("int16"), [CoreType("int16"), CoreType("int16")]),
        FunctionPrototype("add32", CoreType("int32"), [CoreType("int32"), CoreType("int32")]),
        FunctionPrototype("mult8", RegisterCoreType("int8", "A"), [PreservedCoreType("int8"), PreservedCoreType("int8")]),
        FunctionPrototype("mult16", CoreType("int16"), [CoreType("int16"), CoreType("int16")]),
        FunctionPrototype("mult32", CoreType("int32"), [CoreType("int32"), CoreType("int32")]),
        FunctionPrototype("udiv8", VoidType, [InOutCoreType("int8"), InOutCoreType("int8")]),
        FunctionPrototype("udiv16", VoidType, [InOutCoreType("int16"), InOutCoreType("int16")]),
        FunctionPrototype("udiv32", VoidType, [InOutCoreType("int32"), InOutCoreType("int32")]),
        FunctionPrototype("lshift8", RegisterCoreType("uint8", "A"), [PreservedCoreType("uint8"), RegisterCoreType("uint8", "A")]),
        FunctionPrototype("lshift16", ParamReturnCoreType(0), [InOutCoreType("uint16"), RegisterCoreType("uint8", "A")]),
        FunctionPrototype("lshift32", ParamReturnCoreType(0), [InOutCoreType("uint32"), RegisterCoreType("uint8", "A")]),
        FunctionPrototype("rshift8", RegisterCoreType("uint8", "A"), [PreservedCoreType("uint8"), RegisterCoreType("uint8", "A")]),
        FunctionPrototype("rshift16", ParamReturnCoreType(0), [InOutCoreType("uint16"), RegisterCoreType("uint8", "A")]),
        FunctionPrototype("rshift32", ParamReturnCoreType(0), [InOutCoreType("uint32"), RegisterCoreType("uint8", "A")]),

        # STDLIB integer comparison functions.
        FunctionPrototype("ucmp8", RegisterCoreType("int8", "A"), [InOutCoreType("uint8"), InOutCoreType("uint8")]),
        FunctionPrototype("ucmp16", RegisterCoreType("int8", "A"), [InOutCoreType("uint16"), InOutCoreType("uint16")]),
        FunctionPrototype("ucmp32", RegisterCoreType("int8", "A"), [InOutCoreType("uint32"), InOutCoreType("uint32")]),
        FunctionPrototype("cmp8", RegisterCoreType("int8", "A"), [InOutCoreType("int8"), InOutCoreType("int8")]),
        FunctionPrototype("cmp16", RegisterCoreType("int8", "A"), [InOutCoreType("int16"), InOutCoreType("int16")]),
        FunctionPrototype("cmp32", RegisterCoreType("int8", "A"), [InOutCoreType("int32"), InOutCoreType("int32")]),
        FunctionPrototype("umin8", RegisterCoreType("int8", "A"), [InOutCoreType("int8"), InOutCoreType("int8")]),
        FunctionPrototype("umin16", CoreType("int16"), [CoreType("int16"), CoreType("int16")]),
        FunctionPrototype("umin32", CoreType("int32"), [CoreType("int32"), CoreType("int32")]),
        FunctionPrototype("umax8", RegisterCoreType("int8", "A"), [InOutCoreType("int8"), InOutCoreType("int8")]),
        FunctionPrototype("umax16", CoreType("int16"), [CoreType("int16"), CoreType("int16")]),
        FunctionPrototype("umax32", CoreType("int32"), [CoreType("int32"), CoreType("int32")]),
    ]

    return prototypes
