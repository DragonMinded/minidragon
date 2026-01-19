import builtins
import os
import libcst as cst
import libcst.metadata as meta

from enum import Enum, auto
from typing import Callable, Dict, Final, Iterable, Iterator, List, Mapping, Optional, Sequence, Set, Tuple, Union, overload

from .core import assemble
from .util import comment_source, hexstr, hexval, sanitize


MAX_STRING_LENGTH: Final[int] = 127
VERSION: Final[str] = "1.2.1"  # Also bump version in pyproject.toml


class CompilerSettings:
    def __init__(self, *, optimize: bool = False) -> None:
        self.optimize = optimize


class Context:
    def __init__(self, module: str, settings: CompilerSettings, node: cst.CSTNode, meta: Mapping[cst.CSTNode, meta.CodeRange], extra: str = "") -> None:
        self.module = module
        self.settings = settings
        self.node = node
        self.meta = meta
        self.extra = extra
        self.mapping: Dict[cst.CSTNode, cst.CSTNode] = {}

    @property
    def label(self) -> str:
        shortmodule: str = self.module
        if os.path.sep in shortmodule:
            shortmodule = shortmodule.rsplit(os.path.sep, 1)[1]

        modulename: str = ""
        for c in shortmodule:
            if c.isalnum():
                modulename += c
            else:
                modulename += "_" if (not modulename) or modulename[-1] != "_" else ""

        while modulename and modulename[-1] == "_":
            modulename = modulename[:-1]
        return modulename

    def wrap(self, node: cst.CSTNode, extra: str = "") -> "Context":
        context = Context(self.module, self.settings, node, self.meta, extra)
        context.mapping = {x: y for x, y in self.mapping.items()}
        return context

    def virtual(self, node: cst.CSTNode, extra: str = "") -> "Context":
        context = Context(self.module, self.settings, node, self.meta, extra)
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


class NonConstantExpressionException(Exception):
    pass


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
        safe_ref: bool = False,
        extern: bool = False,
        return_padding: bool = True,
    ) -> None:
        self.type = base_type
        self.pointed_type = pointed_type
        self.const = const
        self.safe_ref = safe_ref
        self.__length = length or None
        self.extern = extern
        self.return_padding = return_padding
        if self.type == "pointer" and pointed_type is None:
            raise Exception("Logic error, creating a pointer without a pointed type!")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.type == other
        if isinstance(other, CoreType):
            return (
                self.type == other.type and
                self.pointed_type == other.pointed_type and
                self.const == other.const and
                self.length == other.length
            )
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
            safe_ref=False,
            extern=self.extern,
            return_padding=self.return_padding,
        )

    def nonconst_clone(self) -> "CoreType":
        if not self.const:
            return self
        if self.type not in {"str", "pointer"}:
            return self

        return CoreType(
            self.type,
            self.pointed_type,
            length=self.length or MAX_STRING_LENGTH,
            const=False,
            safe_ref=False,
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

    @property
    def is_void(self) -> bool:
        return self.type == "void"


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

    def nonconst_clone(self) -> "CoreType":
        raise Exception("Logic error, cannot have non-const PreservedCoreType!")


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

    def nonconst_clone(self) -> "CoreType":
        if self.type not in {"str", "pointer"}:
            return self

        new_type = InOutCoreType(
            self.type,
        )
        new_type.const = False
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

    def nonconst_clone(self) -> "OutCoreType":
        if self.type not in {"str", "pointer"}:
            return self

        new_type = OutCoreType(
            self.type,
        )
        new_type.const = False
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

    def nonconst_clone(self) -> "RegisterCoreType":
        if self.type not in {"str", "pointer"}:
            return self

        new_type = RegisterCoreType(
            self.type, self.register
        )
        new_type.const = False
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

    def nonconst_clone(self) -> "ParamReturnCoreType":
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

    def nonconst_clone(self) -> "PaddingCoreType":
        # This is just a padding value.
        return self

    @property
    def padbytes(self) -> int:
        return int(self.type[9:])


class Constant:
    def __init__(self, name: str, vartype: CoreType, value: object) -> None:
        self.name = name
        self.type = vartype
        self.value = value

    def __repr__(self) -> str:
        return f"Local constant {self.type!r} {self.name!r}: {self.value!r}"


class SysConstant:
    def __init__(self) -> None:
        versionbytes: List[int] = [int(x) for x in VERSION.split(".")]
        self.byteorder: str = "big"
        self.hexversion: int = int(f"0x{hexstr(versionbytes[0], 2)}{hexstr(versionbytes[1], 2)}{hexstr(versionbytes[2], 4)}", 16)
        self.maxsize: int = 2**31 - 1
        self.maxunicode: int = 0xFF
        self.platform: str = "minidragon"
        self.version: str = VERSION


class Allocation:
    def __init__(self, var: str, storage: str, size: int) -> None:
        self.var: str = var
        self.storage: str = storage
        self.size: int = size
        self.used: bool = True

    def __repr__(self) -> str:
        return f"Allocation(var={self.var!r}, storage={self.storage!r}, size={self.size!r}, used={self.used!r})"


class FunctionParam:
    def __init__(self, name: Optional[str], paramtype: CoreType) -> None:
        self.name = name
        self.type = paramtype


class UnvalidatedName(cst.Name):
    """
    Exists solely to be able to call create_call() with builtin references which are
    intentionally designed to include invalid characters for a python identifier. They
    do this so that it isn't possible to name a variable an internal identifier in a
    program you are attempting to compile.
    """

    def _validate(self) -> None:
        pass


class SentinelInteger(cst.Integer):
    """
    Exists solely to be able to create default arguments to compiler intrinsics so that
    we can detect if a user-provided value was given or omitted.
    """


class FunctionPrototype:
    def __init__(
        self,
        name: str,
        return_type: CoreType,
        params: Optional[List[CoreType]] = None,
        paramnames: Optional[List[str]] = None,
        paramdefaults: Optional[List[Optional[cst.BaseExpression]]] = None,
    ) -> None:
        self.name = name
        self.return_type = return_type
        self.params: List[CoreType] = params or []
        self.paramnames: List[str] = paramnames or []
        self.paramdefaults: List[Optional[cst.BaseExpression]] = paramdefaults or []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FunctionPrototype):
            return False

        return (
            self.name == other.name and
            self.return_type == other.return_type and
            self.params == other.params and
            self.paramnames == other.paramnames and
            self.paramdefaults == other.paramdefaults
        )

    def __repr__(self) -> str:
        params: str
        if self.paramnames and len(self.params) == len(self.paramnames):
            params = ', '.join(f"{self.paramnames[i]}: '{self.params[i]}'" for i in range(len(self.params)))
        else:
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
    def __init__(self, name: str, vartype: CoreType, location: Optional[int] = None, initialized: bool = False, relocated: bool = False) -> None:
        self.name = name
        self.type = vartype
        self.location = location
        self.initialized = initialized
        self.relocated = relocated

    @property
    def size(self) -> int:
        return self.type.size

    @property
    def const(self) -> bool:
        return self.type.const

    def label(self, context: Context, label: str = "") -> str:
        if self.type.type not in {"str"}:
            raise Exception("Logic error, trying to get a label name for a non-string type!")

        if label:
            label = f"{label}_"

        for c in self.name:
            if c.isalnum():
                label += c
            else:
                label += "_" if (not label) or (label[-1] != "_") else ""

        while label and label[-1] == "_":
            label = label[:-1]

        modulename = context.label
        if modulename[-1] != "_":
            modulename = modulename + "_"
        if modulename[0] != "_":
            modulename = "_" + modulename

        return modulename + label

    def __repr__(self) -> str:
        return f"{self.type!r} {self.name}: {self.location} size {self.size}{' uninitialized' if not self.initialized else ''}{' relocated' if self.relocated else ''}"


class StackOperation(Enum):
    LOAD = auto()
    STORE = auto()


class Stack:
    def __init__(self, funcname: str) -> None:
        self.funcname = funcname
        self.stack: List[StackVar] = []
        self.size: int = 0
        self.location: int = 0
        self.__tempnames: List[Tuple[str, int, int, StackOperation]] = []

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

    def nameloc(self, name: str, location: int, size: int, operation: StackOperation) -> None:
        self.__tempnames.append((name, location, size, operation))

    def unnameloc(self, name: str) -> None:
        self.__tempnames = [x for x in self.__tempnames if x[0] != name]

    def clone(self) -> "Stack":
        stack = Stack(self.funcname)
        for entry in self.stack:
            stack.stack.append(StackVar(entry.name, entry.type, location=entry.location, initialized=entry.initialized, relocated=entry.relocated))
        stack.size = self.size
        stack.location = self.location
        stack.__tempnames = [*self.__tempnames]
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
                entry.relocated = True
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

    def labelof(self, name: str, context: Context) -> Optional[str]:
        for entry in self.stack:
            if entry.name == name:
                return f"{entry.label(context, self.funcname)}"
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

    def comment(self, offset: int, stackop: StackOperation) -> str:
        # First, try to apply temporary names.
        names: List[Tuple[str, int, int, StackOperation]] = []
        for name, location, size, operation in self.__tempnames:
            if offset >= location and offset < (location + size):
                names.append((name, location, size, operation))

        if len(names) == 1:
            return f" ; STACKOFF: {names[0][0]} + {offset - names[0][1]}"
        if len(names) == 2:
            for name, location, size, operation in names:
                if operation != stackop:
                    continue
                return f" ; STACKOFF: {name} + {offset - location}"

        # Now, look in the stack and figure out what we're messing with.
        potentials: List[StackVar] = []

        for entry in self.stack:
            entryloc = entry.location
            if entryloc is None:
                continue
            size = entry.size or 0
            if offset >= entryloc and offset < (entryloc + size):
                potentials.append(entry)

        if len(potentials) == 1:
            return f" ; STACKOFF: {potentials[0].name} + {offset - (potentials[0].location or 0)}"
        if len(potentials) == 2:
            for potential in potentials:
                if stackop == StackOperation.LOAD and potential.relocated:
                    continue
                if stackop == StackOperation.STORE and not potential.relocated:
                    continue
                return f" ; STACKOFF: {potential.name} + {offset - (potential.location or 0)}"

        # Finally, give up.
        raise Exception(f"Logic error, could not name stack location at offset {offset}!")

    def __repr__(self) -> str:
        lines = [str(e) for e in self.stack]
        lines.append(f"Size: {self.size}, Loc: {self.location}")
        return "\n".join(lines)


def strtoint(val: str, context: Context) -> int:
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
    if left.type == "string" and (right.is_string or right.is_char or right.type == "string"):
        return True
    if right.type == "string" and (left.is_string or left.is_char or left.type == "string"):
        return True
    return False


def create_call(name: str, params: Iterable[cst.BaseExpression]) -> cst.Call:
    return cst.Call(
        func=cst.Name(value=name),
        args=[cst.Arg(value=param) for param in params],
    )


def global_by_name(globs: Sequence[Union[FunctionPrototype, GlobalVariable]], name: str) -> Optional[GlobalVariable]:
    for glob in globs:
        if isinstance(glob, GlobalVariable) and glob.name == name:
            return glob
    return None


def get_assembled_length(compiled: List[str], refs: Sequence[Union[FunctionPrototype, GlobalVariable]], labels: List[str] = []) -> int:
    compiled = [sanitize(c) for c in compiled]
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


def comment_stack(stack: Stack) -> List[str]:
    if not os.environ.get("INSERT_STACK_COMMENTS"):
        return []

    return [
        f"  ; Stack location: {stack.location}",
    ]


def expr_to_str(expr: cst.BaseExpression) -> str:
    fresh_module = cst.parse_module("")
    code = fresh_module.code_for_node(
        cst.SimpleStatementLine(
            body=[
                cst.Expr(value=expr),
            ],
        )
    )
    return code.strip()


def unescape_literal(val: str) -> str:
    escaping: str = ""
    retval: str = ""

    for v in val:
        if escaping:
            if escaping == "\\":
                if v == "\'":
                    retval += "\'"
                    escaping = ""
                elif v == "\\":
                    retval += "\\"
                    escaping = ""
                elif v == "n":
                    retval += "\n"
                    escaping = ""
                elif v == "r":
                    retval += "\r"
                    escaping = ""
                elif v == "t":
                    retval += "\t"
                    escaping = ""
                elif v == "b":
                    retval += "\b"
                    escaping = ""
                elif v == "f":
                    retval += "\f"
                    escaping = ""
                elif v in "01234567":
                    escaping += v
                elif v in "x":
                    escaping += v
                else:
                    raise Exception(f"Logic error, couldn't unescape {val!r}!")

                continue

            elif escaping == "\\x":
                if v in "0123456789abcdefABCDEF":
                    escaping += v
                    continue

            elif escaping[:2] == "\\x" and escaping[2] in "0123456789abcdefABCDEF":
                if v in "0123456789abcdefABCDEF":
                    retval += chr(int(escaping[2] + v, 16))
                    escaping = ""
                    continue

            else:
                if escaping[:1] == "\\" and len(escaping) < 4:
                    # Could be an octal escape.
                    if all(x in "01234567" for x in escaping[1:]):
                        if v in "01234567":
                            escaping += v
                            if len(escaping) == 4:
                                retval += chr(int(escaping[1:], 8))
                                escaping = ""

                            continue

            raise Exception(f"Logic error, couldn't unescape {val!r}!")

        else:
            if v == "\\":
                escaping = "\\"
            else:
                retval += v

    return retval


def expr_integer_type(size: int) -> CoreType:
    if size == 1:
        return CoreType("int8")
    elif size == 2:
        return CoreType("int16")
    elif size == 4:
        return CoreType("int32")
    else:
        raise Exception("Logic error, unrecognized integer size!")


def stack_is_at(destination: str, stack: Stack, *, offset: int = 0) -> bool:
    move_amt = stack.find(destination)
    if move_amt is None:
        raise Exception(f"Logic error, could not find {destination} on stack to compare to!")
    move_amt += offset
    return move_amt == 0


def safe_assign(
    destination: str,
) -> bool:
    """
    Checks whether the current assignment is a safe assignment to perform without a strcpy. Basically
    that only happens when the destination we're assigning to is the return value builtin.
    """
    return destination == "builtin(retval)"


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


class NameCheckVisitor(cst.CSTVisitor):
    def __init__(self, name: str) -> None:
        self.name = name
        self.count = 0

    def visit_Name(self, node: cst.Name) -> bool:
        if node.value == self.name:
            self.count += 1
        return True


def is_leftmost(name: str, expr: cst.BaseExpression) -> bool:
    if isinstance(expr, cst.Name):
        return expr.value == name

    if isinstance(expr, cst.BinaryOperation):
        return is_leftmost(name, expr.left)

    if isinstance(expr, cst.Subscript):
        return is_leftmost(name, expr.value)

    return False


def assignment_needs_temporary(destination: str, expr: cst.BaseExpression) -> bool:
    visitor = NameCheckVisitor(destination)
    expr.visit(visitor)

    if visitor.count == 0:
        # Doesn't self-reference, so no need for a temporary.
        return False
    if visitor.count > 1:
        # Self-references multiple times, so we need a temporary for the multiple copies to be correct.
        return True

    # If the reference is the left-most in the expression, then this is safe.
    return not is_leftmost(destination, expr)


def string_prefix(expr: cst.BaseExpression) -> str:
    if isinstance(expr, cst.SimpleString):
        raw_value = expr.value
        prefix = ""
        for ch in raw_value:
            if ch == '"' or ch == "'":
                break
            prefix += ch
        return prefix

    return ""


class Compiler:
    def __init__(
        self,
        settings: CompilerSettings,
        *,
        file_loader: Optional[Callable[[str], Optional[str]]] = None,
        working_directory: Optional[str] = None,
        library_directories: Optional[List[str]] = None,
    ) -> None:
        self.__comment_ref_count: int = 0
        self.__expr_global_count: int = 0
        self.__local_label_count: int = 0
        self.__saved_counts: List[Tuple[int, int]] = []
        self.__file_loader: Callable[[str], Optional[str]] = file_loader or self.__default_file_loader
        self.__working_directory: str = working_directory or "."
        self.__library_directory: List[str] = library_directories or []
        self.settings = settings

    def comment_ref(self) -> str:
        self.__comment_ref_count += 1
        return f"##comment_ref_{self.__comment_ref_count}##"

    def expr_temp_name(self) -> str:
        self.__expr_global_count += 1
        return f"builtin(expr_temp_{self.__expr_global_count})"

    def local_label_name(self, context: Context, label: str = "") -> str:
        self.__local_label_count += 1

        if label:
            label = f"_{label}_"
        else:
            label = "_"

        modulename = context.label
        if modulename[-1] != "_":
            modulename = modulename + "_"
        if modulename[0] != "_":
            modulename = "_" + modulename

        return f"{modulename}local{label}{self.__local_label_count}"

    def _push_names(self, ) -> None:
        self.__saved_counts.append((self.__expr_global_count, self.__local_label_count))

    def _pop_names(self, ) -> None:
        if not self.__saved_counts:
            raise Exception("Logic error, popping saved counts without a push!")

        self.__expr_global_count = self.__saved_counts[-1][0]
        self.__local_label_count = self.__saved_counts[-1][1]
        self.__saved_counts.pop()

    def intrinsic_eval(self, expr: cst.BaseExpression, constants: List[Constant], context: Context) -> object:
        if not isinstance(expr, cst.Call):
            return None

        if not isinstance(expr.func, cst.Name):
            return None

        try:
            function_prototype = self.get_function_prototype(expr, builtin_functions(), constants, context)
        except CompilerError:
            # This isn't a built-in function so it can't be an intrinsic.
            return None

        intrinsic_args, _ = self.get_function_params(expr, function_prototype, context)

        if function_prototype.name == "fixed":
            # Fixed width conversion intrinsic.
            if len(intrinsic_args) != 2:
                raise CompilerError("Intrinsic function fixed takes two arguments.", context)

            number = self.codegen_eval(intrinsic_args[0].value, constants, context)
            if len(intrinsic_args) == 2:
                fracbits = self.codegen_eval(intrinsic_args[1].value, constants, context)
            else:
                fracbits = 8

            if number is None or fracbits is None:
                raise CompilerError("Intrinsic function fixed takes a number or string as its first parameter and a number of fractional bits as its second.", context)
            try:
                numberString = str(float(number))  # type: ignore
            except ValueError:
                raise CompilerError("Intrinsic function fixed takes a number or string as its first parameter.", context)

            if not isinstance(fracbits, int):
                raise CompilerError("Intrinsic function fixed takes a number of fractional bits as its second parameter.", context)

            if numberString[0] == "-":
                negative = True
                numberString = numberString[1:]
            else:
                negative = False

            if "." in numberString:
                before, after = numberString.split(".", 1)
                precision = len(after)

                numberInt = int(before + after)
                numberInt <<= fracbits
                numberInt //= (10 ** precision)
            else:
                numberInt = int(numberString)
                numberInt <<= fracbits

            return -numberInt if negative else numberInt

        # Unrecognized.
        return None

    def codegen_eval(self, expr: cst.BaseExpression, constants: List[Constant], context: Optional[Context]) -> object:
        if context is not None:
            # Handle compiler intrinsics first.
            if (intrinsic := self.intrinsic_eval(expr, constants, context)) is not None:
                return intrinsic

        # Render out the tree so we can pass to eval().
        code = expr_to_str(expr)

        # If we don't control our builtins, python will eval a bunch of stuff we don't support due to
        # its own builtins, and it will appear to work but only for constant expressions.
        builtins_dict: Dict[str, object] = {}
        for name in ["abs", "bool", "str", "len", "chr", "ord", "min", "max"]:
            builtins_dict[name] = getattr(builtins, name)

        try:
            return eval(code, {"__builtins__": builtins_dict}, {c.name: c.value for c in constants})
        except Exception:
            pass

        raise NonConstantExpressionException(f"{expr} is not constant, cannot eval!")

    def is_safe_return(
        self,
        assign_value: cst.BaseExpression,
        stack: Stack,
        refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
        local_consts: List[Constant],
        context: Context,
    ) -> bool:
        """
        Given an expression, determine if that expression is safe to return without a strcpy.
        """
        if self.is_safe_ref(assign_value, stack, refs, local_consts, context):
            # This could actually have been a constant return.
            return True

        if isinstance(assign_value, cst.Name):
            # Safe to return an alias because we know the caller will strcpy.
            return True

        if isinstance(assign_value, cst.Call):
            # Safe to return an alias because we know the caller will strcpy.
            return True

        return False

    def is_safe_ref(
        self,
        assign_value: cst.BaseExpression,
        stack: Stack,
        refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
        local_consts: List[Constant],
        context: Context,
    ) -> bool:
        """
        Given an expression, determine if that expression is a reference to a constant that's safe
        to treat as a string without a strcpy.
        """

        if isinstance(assign_value, cst.Name):
            possible_type = stack.typeof(assign_value.value)
            if possible_type and possible_type.safe_ref:
                # This is being assigned from another constant variable that was a safe reference.
                return True

        if isinstance(assign_value, cst.Call):
            # Functions returning string constants are only allowed to do so if they are returning a
            # safe ref themselves, so we only need to look at the return value for this function.
            try:
                function_prototype = self.get_function_prototype(assign_value, refs, local_consts, context)
                return_type = function_prototype.return_type
                return return_type.is_string and return_type.const
            except CompilerError:
                # Ignore this, it's probably somebody trying to return a builtin such as cast() or str().
                pass

        try:
            # If we can evaluate the assign value directly that means it's a safe ref. This only
            # happens for global variables, string literals, and local constants, which strings are
            # never part of.
            consts = [
                *[Constant(gv.name, gv.type, None) for gv in refs if isinstance(gv, GlobalVariable)],
                *local_consts
            ]

            self.codegen_eval(assign_value, consts, context)
            return True
        except NonConstantExpressionException:
            pass

        return False

    def get_type(
        self,
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
                            value = self.codegen_eval(sliceval.slice.value, constants, None)
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
                    pointed = self.get_type(expr, constants, allow_nopad=allow_nopad, allow_extern=allow_extern, allow_array=allow_array)
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
                        return CoreType("void", None, const=True, extern=extern, return_padding=False)
                else:
                    if expr.value not in {"uint8", "int8", "uint16", "int16", "uint32", "int32", "bool", "char", "str"}:
                        return None
                    if length and expr.value not in {"str"}:
                        return None

                    return CoreType(expr.value, None, length=length, const=const, extern=extern, return_padding=not nopad)

            else:
                return None

    def generate_global_variable(self, assign: cst.AnnAssign, globs: List[GlobalVariable], consts: List[Constant], context: Context) -> Sections:
        compiled = Sections(code=[context.comment()])

        target_node = assign.target
        if not isinstance(target_node, cst.Name):
            raise CompilerError("Unsupported name for global variable definition", context)

        assign_name = target_node.value
        assign_type = self.get_type(assign.annotation.annotation, consts, allow_extern=True, allow_array=True)
        assign_value = assign.value

        if assign_type is None:
            raise CompilerError("Unsupported type for global variable definition", context)

        for const in consts:
            if const.name == assign_name:
                raise CompilerError("Cannot reassign global variable", context)
        for glob in globs:
            if glob.name == assign_name:
                raise CompilerError("Cannot reassign global variable", context)

        if assign_type.const and assign_type.extern:
            if assign_value:
                raise CompilerError("Cannot initialize an extern global const variable", context)

            # All we need to do is register a global for this.
            globs.append(GlobalVariable(assign_name, assign_type))

        elif assign_type.const:
            if assign_value is None:
                raise CompilerError("Expecting initialization value for global const definition", context)
            if not isinstance(assign_value, cst.BaseExpression):
                raise CompilerError("Unsupported initialization value for global const definition", context)

            # Attempt to codegen and evaluate the python code.
            prefix = string_prefix(assign_value)
            try:
                value = self.codegen_eval(assign_value, consts, context)
                if "b" in prefix:
                    if not isinstance(value, bytes):
                        raise Exception("Logic error, expected a bytestring when given a bytes prefix!")
                    value = "".join([chr(x) for x in value])
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
                compiled.append_code(f"  .byte {hexval((value >> 0) & 0xFF, 2)}")

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
                compiled.append_code(f"  .byte {hexval((value >> 8) & 0xFF, 2)}")
                compiled.append_code(f"  .byte {hexval((value >> 0) & 0xFF, 2)}")

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
                compiled.append_code(f"  .byte {hexval((value >> 24) & 0xFF, 2)}")
                compiled.append_code(f"  .byte {hexval((value >> 16) & 0xFF, 2)}")
                compiled.append_code(f"  .byte {hexval((value >> 8) & 0xFF, 2)}")
                compiled.append_code(f"  .byte {hexval((value >> 0) & 0xFF, 2)}")

            elif assign_type == "char":
                if assign_type.is_array:
                    raise CompilerError("Unsupported array length for global const definition", context)
                if not isinstance(value, str):
                    raise CompilerError("Unsupported initialization value for global const definition", context)
                if "r" not in prefix:
                    value = unescape_literal(value)
                if len(value) != 1:
                    raise CompilerError("Unsupported initialization value for global const definition", context)
                compiled.append_code(f"  .char {value[0]!r}")

            elif assign_type == "str":
                if not isinstance(value, str):
                    raise CompilerError("Unsupported initialization value for global const definition", context)

                if "r" not in prefix:
                    value = unescape_literal(value)
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
                    value = self.codegen_eval(assign_value, consts, context)
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
                    compiled.append_init(f"  STOREI {hexval((value >> 0) & 0xFF, 2)}")

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
                    compiled.append_init(f"  STOREI {hexval((value >> 8) & 0xFF, 2)}")
                    compiled.append_init("  INCPC")
                    compiled.append_init(f"  STOREI {hexval((value >> 0) & 0xFF, 2)}")

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
                    compiled.append_init(f"  STOREI {hexval((value >> 24) & 0xFF, 2)}")
                    compiled.append_init("  INCPC")
                    compiled.append_init(f"  STOREI {hexval((value >> 16) & 0xFF, 2)}")
                    compiled.append_init("  INCPC")
                    compiled.append_init(f"  STOREI {hexval((value >> 8) & 0xFF, 2)}")
                    compiled.append_init("  INCPC")
                    compiled.append_init(f"  STOREI {hexval((value >> 0) & 0xFF, 2)}")

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

    def generate_addpci(self, move_amt: int, reason: Optional[str] = None, prefix: Optional[str] = None) -> Sections:
        compiled = Sections()
        while move_amt > 31:
            if prefix is not None:
                compiled.append_code(prefix)
            compiled.append_code("  ADDPCI 31" + comment_source(reason))
            move_amt -= 31
        if move_amt:
            if prefix is not None:
                compiled.append_code(prefix)
            compiled.append_code(f"  ADDPCI {move_amt}" + comment_source(reason))
        return compiled

    def generate_subpci(self, move_amt: int, reason: Optional[str] = None, prefix: Optional[str] = None) -> Sections:
        compiled = Sections()
        while move_amt > 32:
            if prefix is not None:
                compiled.append_code(prefix)
            compiled.append_code("  SUBPCI 32" + comment_source(reason))
            move_amt -= 32
        if move_amt:
            if prefix is not None:
                compiled.append_code(prefix)
            compiled.append_code(f"  SUBPCI {move_amt}" + comment_source(reason))
        return compiled

    def generate_move_by(self, reason: str, move_amt: int, stack: Stack, clobbers: Set[str], context: Context, prefix: Optional[str] = None) -> Sections:
        compiled = Sections()
        if move_amt == 0:
            return compiled

        if move_amt > 0:
            compiled += self.generate_subpci(move_amt, reason, prefix=prefix)
        elif move_amt < 0:
            compiled += self.generate_addpci(-move_amt, reason, prefix=prefix)

        stack.move(move_amt)
        compiled.code += comment_stack(stack)

        return compiled

    def generate_move_to(self, destination: str, stack: Stack, clobbers: Set[str], context: Context, *, offset: int = 0, prefix: Optional[str] = None) -> Sections:
        compiled = Sections()
        move_amt = stack.find(destination)
        if move_amt is None:
            raise Exception(f"Logic error, could not find {destination} on stack to move to!")
        move_amt += offset
        if move_amt == 0:
            return compiled

        if move_amt > 0:
            compiled += self.generate_subpci(move_amt, f"seeking {destination}", prefix=prefix)
        elif move_amt < 0:
            compiled += self.generate_addpci(-move_amt, f"seeking {destination}", prefix=prefix)

        stack.move(move_amt)
        compiled.code += comment_stack(stack)

        return compiled

    def generate_memcpy_locations(
        self,
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

        # First, figure out if we can copy backwards to save an instruction.
        off_from_end = stack.diff(src_loc + (size - 1))
        handled = False
        if off_from_end == 0:
            shuffle_amount = stack.location - (dst_loc + (size - 1))
            if shuffle_amount == 0:
                return compiled

            if shuffle_amount > 0:
                # We don't have anything for the < 0 case, so fall back to the below code.
                handled = True

                for i in range(size):
                    clobbers.add(register)

                    compiled.append_code(f"  LOAD {register}" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled += self.generate_addpci(shuffle_amount)

                    stack.move(-shuffle_amount)
                    compiled.code += comment_stack(stack)

                    compiled.append_code(f"  STORE {register}" + stack.comment(stack.location, StackOperation.STORE))

                    if i < size - 1:
                        compiled += self.generate_subpci(shuffle_amount - 1)
                        stack.move(shuffle_amount - 1)
                        compiled.code += comment_stack(stack)

        if not handled:
            from_rel = stack.diff(src_loc)
            compiled += self.generate_move_by("memcpy_unrolled", from_rel, stack, clobbers, context)
            shuffle_amount = stack.location - dst_loc
            if shuffle_amount == 0:
                return compiled

            if shuffle_amount < 0:
                for i in range(size):
                    clobbers.add(register)

                    compiled.append_code(f"  LOAD {register}" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled += self.generate_subpci(-shuffle_amount)

                    stack.move(-shuffle_amount)
                    compiled.code += comment_stack(stack)

                    compiled.append_code(f"  STORE {register}" + stack.comment(stack.location, StackOperation.STORE))

                    if i < size - 1:
                        compiled += self.generate_addpci((-shuffle_amount) - 1)
                        stack.move(-((-shuffle_amount) - 1))
                        compiled.code += comment_stack(stack)

            else:
                for i in range(size):
                    clobbers.add(register)

                    compiled.append_code(f"  LOAD {register}" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled += self.generate_addpci(shuffle_amount)

                    stack.move(-shuffle_amount)
                    compiled.code += comment_stack(stack)

                    compiled.append_code(f"  STORE {register}" + stack.comment(stack.location, StackOperation.STORE))

                    if i < size - 1:
                        compiled += self.generate_subpci(shuffle_amount + 1)
                        stack.move(shuffle_amount + 1)
                        compiled.code += comment_stack(stack)

        return compiled

    def generate_memcpy_stackvars(
        self,
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
            compiled += self.generate_move_to(source, stack, clobbers, context, offset=actual_expr_offset(offset))
            compiled.append_code(f"  LOAD {register}" + stack.comment(stack.location, StackOperation.LOAD))
            compiled += self.generate_move_to(destination, stack, clobbers, context, offset=actual_expr_offset(offset))
            compiled.append_code(f"  STORE {register}" + stack.comment(stack.location, StackOperation.STORE))

        return compiled

    def can_relocate_return(self, function_type: CoreType, stack: Stack, clobbers: Set[str], context: Context) -> bool:
        if function_type.is_void:
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

    def generate_return(self, function_type: CoreType, stack: Stack, clobbers: Set[str], context: Context) -> Sections:
        compiled = Sections(code=[context.comment()])

        # Because we could have more than one return, make sure we clone the stack to not mess with the rest of the function.
        stack = stack.clone()

        # We need to ensure that our stack only contains the return value and the return pointer.
        # Make sure to move the return value, the return pointer, and then pop all of our saved builtins.
        retptr_in_uv = False
        retptr_final_loc = 0
        if not function_type.is_void:
            # First, we need to figure out if where we're copying the return value will clobber the return pointer.
            # If so, we need to store that in the U/V registers. We could put it on the stack but that's way more
            # shuffling so much slower. Much better to just mark U/V as clobbered and use them.
            if not self.can_relocate_return(function_type, stack, clobbers, context):
                cref = self.comment_ref()
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
                compiled += self.generate_move_by("seeking builtin(retptr)", first_move, stack, clobbers, context)
                compiled.append_code("  LOAD U" + stack.comment(stack.location, StackOperation.LOAD))
                compiled.append_code("  DECPC")

                stack.move(1)
                compiled.code += comment_stack(stack)

                compiled.append_code("  LOAD V" + stack.comment(stack.location, StackOperation.LOAD))
                compiled.append_code(f"  ; {cref}")

            # Second, make sure the top of the stack is our return.
            top_spot = stack.at(0)
            if top_spot is not None and top_spot.name != "builtin(retval)":
                cref = self.comment_ref()
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
                stack.nameloc("builtin(retval)", src_loc, number_of_moves, StackOperation.LOAD)
                stack.nameloc("builtin(retval)", 0, number_of_moves, StackOperation.STORE)
                compiled += self.generate_memcpy_locations(src_loc, 0, number_of_moves, stack, clobbers, context)
                compiled.append_code(f"  ; {cref}")
                stack.unnameloc("builtin(retval)")

        # Now, move the return pointer if needed.
        if retptr_in_uv:
            cref = self.comment_ref()
            compiled.append_code(f"  ; Restoring the return pointer from U/V to the correct location. {cref}")

            # Gotta grab it out of the saved U/V registers.
            restore_move_amt = retptr_final_loc - stack.location
            compiled += self.generate_move_by("seeking return pointer restoration point", restore_move_amt, stack, clobbers, context)
            stack.nameloc("builtin(retptr)", retptr_final_loc, 2, StackOperation.STORE)
            compiled.append_code("  STORE U" + stack.comment(stack.location, StackOperation.STORE))
            compiled.append_code("  DECPC")

            stack.move(1)
            compiled.code += comment_stack(stack)

            compiled.append_code("  STORE V" + stack.comment(stack.location, StackOperation.STORE))
            compiled.append_code(f"  ; {cref}")
            stack.unnameloc("builtin(retptr)")
        else:
            retptr_abs = stack.absfind("builtin(retptr)")
            if retptr_abs is None:
                raise Exception("Logic error, failed to calculate the source location of builtin(retptr)!")
            initialized = stack.initof("builtin(retptr)")
            if not initialized:
                raise Exception("Logic error, builtin(retptr) has not been initialized!")

            if retptr_abs != retptr_final_loc:
                cref = self.comment_ref()
                compiled.append_code(f"  ; Moving return pointer to correct location in stack. {cref}")

                # We need to use the A register to move the value, so it's clobbered now.
                clobbers.add("A")

                # We need to relocate the retptr to this spot.
                src_loc = stack.absfind("builtin(retptr)")
                number_of_moves = stack.sizeof("builtin(retptr)")

                if src_loc is None or number_of_moves is None:
                    raise Exception("Logic error, failed to get move amounts for builtin(retptr)!")

                # Name the location so we don't end up clobbering it in an optimization pass.
                stack.nameloc("builtin(retptr)", retptr_final_loc, number_of_moves, StackOperation.STORE)
                stack.nameloc("builtin(retptr)", src_loc, number_of_moves, StackOperation.LOAD)

                # Generate code to move from our position to the first byte of the retptr.
                compiled += self.generate_memcpy_locations(src_loc, retptr_final_loc, number_of_moves, stack, clobbers, context)
                compiled.append_code(f"  ; {cref}")

                stack.unnameloc("builtin(retptr)")

        # Now, pop all of our saved registers, and then return.
        tlcref: Optional[str] = None
        if clobbers:
            tlcref = self.comment_ref()
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
                compiled += self.generate_move_by(f"seeking {name}", move_amt, stack, clobbers, context)

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
        compiled += self.generate_move_by("skipping past temporary locals", final_move_to_ret, stack, clobbers, context)
        compiled.append_code("  RET")

        return compiled

    def generate_const_load(self, val: object, destination: str, stack: Stack, clobbers: Set[str], context: Context) -> Sections:
        compiled = Sections()

        dtype = stack.typeof(destination)
        if dtype is None:
            raise Exception("Logic error, could not determine type of destination to load constant to!")

        if dtype.is_integer:
            if not isinstance(val, int):
                raise CompilerError("Unsupported non-integer constant load", context)

            if dtype.is_unsigned and val < 0:
                raise CompilerError("Cannot use a negative value in an unsigned expression", context)

            if is_register_destination(destination):
                compiled.append_code(f"  LOADI {hexval((val >> 0) & 0xFF, 2)}")
            else:
                clobbers.add("A")

                dest_loc = stack.find(destination)
                dest_size = stack.sizeof(destination)
                if dest_loc is None or dest_size is None:
                    raise Exception("Logic error, cannot find destination to load constant to!")

                compiled += self.generate_move_by(f"seeking {destination}", dest_loc, stack, clobbers, context)
                if dest_size == 1:
                    compiled.append_code(f"  LOADI {hexval((val >> 0) & 0xFF, 2)}")
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                elif dest_size == 2:
                    compiled.append_code(f"  LOADI {hexval((val >> 0) & 0xFF, 2)}")
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                    compiled.append_code("  DECPC")

                    stack.move(1)
                    compiled.code += comment_stack(stack)

                    compiled.append_code(f"  LOADI {hexval((val >> 8) & 0xFF, 2)}")
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                elif dest_size == 4:
                    compiled.append_code(f"  LOADI {hexval((val >> 0) & 0xFF, 2)}")
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                    compiled.append_code("  DECPC")

                    stack.move(1)
                    compiled.code += comment_stack(stack)

                    compiled.append_code(f"  LOADI {hexval((val >> 8) & 0xFF, 2)}")
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                    compiled.append_code("  DECPC")

                    stack.move(1)
                    compiled.code += comment_stack(stack)

                    compiled.append_code(f"  LOADI {hexval((val >> 16) & 0xFF, 2)}")
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                    compiled.append_code("  DECPC")

                    stack.move(1)
                    compiled.code += comment_stack(stack)

                    compiled.append_code(f"  LOADI {hexval((val >> 24) & 0xFF, 2)}")
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                else:
                    raise CompilerError(f"Unsupported destination {destination} for const load", context)

        elif dtype.is_bool:
            if not isinstance(val, bool):
                raise CompilerError("Unsupported non-boolean constant load", context)

            intval = 0xFF if val else 0x00

            if is_register_destination(destination):
                compiled.append_code(f"  LOADI {hexval((intval >> 0) & 0xFF, 2)}")
            else:
                clobbers.add("A")

                dest_loc = stack.find(destination)
                dest_size = stack.sizeof(destination)
                if dest_loc is None or dest_size is None:
                    raise Exception("Logic error, cannot find destination to load constant to!")

                compiled += self.generate_move_by(f"seeking {destination}", dest_loc, stack, clobbers, context)
                compiled.append_code(f"  LOADI {hexval((intval >> 0) & 0xFF, 2)}")
                compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

        elif dtype.is_char:
            if not isinstance(val, str):
                raise CompilerError("Unsupported non-character constant load", context)
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

                compiled += self.generate_move_by(f"seeking {destination}", dest_loc, stack, clobbers, context)
                compiled.append_code(f"  LOADI {val!r}")
                compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

        else:
            raise CompilerError(f"Unsupported constant load of type {dtype.type}", context)

        return compiled

    def get_function_prototype(
        self,
        call: cst.Call,
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
        self,
        call: cst.Call,
        function_prototype: FunctionPrototype,
        context: Context,
    ) -> Tuple[List[cst.Arg], List[FunctionParam]]:
        # Gather up arguments, including any defaults and in the future respecting kwargs.
        args: List[cst.Arg] = []
        kwargs: Dict[str, cst.Arg] = {}

        for arg in call.args:
            if arg.keyword is not None:
                name = arg.keyword.value
                if name in kwargs:
                    raise CompilerError(f"Keyword argument {name} specified multiple times", context)

                kwargs[name] = arg
                continue

            if arg.star != "":
                raise CompilerError("Unsupported star argument in function call", context)

            args.append(arg)

        # Make sure that the number of arguments supplied matches
        param_count: int = 0
        needed_args: List[FunctionParam] = []
        for i, needed_arg in enumerate(function_prototype.params):
            try:
                paramname = function_prototype.paramnames[i]
            except IndexError:
                paramname = None

            if paramname is None:
                # All arguments that are passed by reference (strings, pointers, arrays) need to be marked as const
                # here, simply to stop any sort of internal copy on assign operation. We don't want to force the
                # programmer to declare all params of this type const because then they couldn't have mutatable params.
                needed_args.append(FunctionParam(None, needed_arg.const_clone()))
            else:
                needed_args.append(FunctionParam(paramname, needed_arg))

            if isinstance(needed_arg, PaddingCoreType):
                # Not the responsibility of the caller, we will set this up.
                continue
            if isinstance(needed_arg, OutCoreType):
                # Not the responsibility of the caller, we will set this up.
                continue

            if param_count >= len(args):
                try:
                    paramdefault = function_prototype.paramdefaults[i]
                except IndexError:
                    paramdefault = None

                if paramname in kwargs:
                    args.append(kwargs[paramname])
                    del kwargs[paramname]

                elif paramdefault is not None:
                    args.append(cst.Arg(value=paramdefault))

            else:
                if paramname in kwargs:
                    raise CompilerError(f"Keyword argument {paramname} specified for argument that already has a positional value", context)

            param_count += 1

        if kwargs:
            for name in kwargs:
                raise CompilerError(f"Function {function_prototype.name} does not have a parameter named {name}", context)

        if param_count != len(args):
            raise CompilerError(f"Function {function_prototype.name} expects {param_count} args but {len(args)} were given", context)

        return args, needed_args

    def get_function_params(
        self,
        call: cst.Call,
        function_prototype: FunctionPrototype,
        context: Context,
    ) -> Tuple[List[cst.Arg], List[FunctionParam]]:
        args, needed_args = self.get_function_params_impl(call, function_prototype, context)
        needed_args = [na for na in needed_args if not isinstance(na.type, (PaddingCoreType, OutCoreType))]
        return args, needed_args

    def generate_function_call_internal(
        self,
        call: cst.Call,
        destination: Optional[str],
        types: Dict[cst.CSTNode, CoreType],
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
        refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
        local_consts: List[Constant],
        context: Context,
    ) -> Sections:
        compiled = Sections(code=[context.comment()])
        function_prototype = self.get_function_prototype(call, refs, local_consts, context)

        # Ensure that we're not trying to assign a void function call to an expression.
        if destination is not None and function_prototype.return_type.is_void:
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
        args, computed_params = self.get_function_params_impl(call, function_prototype, context)

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
                if stackvars[i].size != params[i].type.size:
                    break
            else:
                # All of the stack variables line up, let's double check that calling semantics
                # allow for us to use these as-is instead of making copies.
                if destination is not None and argnames[0] == destination:
                    # If the first parameter is also our return value, then we can only keep this
                    # optimization if the first parameter is a normal core type and the return
                    # value is a normal return type, or if the first parameter is in/out or out
                    # and the return value comes from this parameter.
                    if isinstance(params[0].type, (PreservedCoreType, RegisterCoreType, PaddingCoreType)):
                        # Cannot make these match under any circumstances.
                        continue
                    elif isinstance(params[0].type, (InOutCoreType, OutCoreType)):
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
                        if isinstance(params[0].type, InOutCoreType):
                            actual_arg = considered[0].value
                            if isinstance(actual_arg, cst.Name):
                                arg_type = stack.typeof(actual_arg.value)
                                if not arg_type:
                                    raise Exception("Logic error, could not determine type of function argument!")
                                if arg_type.const:
                                    continue

                match = False
                for i in range(arglen):
                    if isinstance(params[i].type, RegisterCoreType):
                        # These can match if they're the final param, because we'll end up popping
                        # it off the stack to put the value in a register.
                        if not full_params or i != (arglen - 1):
                            break
                    elif isinstance(params[i].type, PaddingCoreType):
                        # These can never match. We'd need to be even more clever with picking out
                        # register types from the middle of the argument list, and padding needs to
                        # be inserted in the stack at the right spot.
                        break
                    elif isinstance(params[i].type, OutCoreType):
                        # This is added to the stack, and I genuinely don't know what to do in this
                        # optimization case if this shows up here.
                        break
                    elif isinstance(params[i].type, PreservedCoreType):
                        # These are a match, since they either preserve the value, or replace it.
                        pass
                    elif isinstance(params[i].type, InOutCoreType):
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
                        param_in_question = params[i].type

                        stackloc: Optional[int] = stackvars[i].location
                        stacksize: Optional[int] = stackvars[i].size
                        if stackloc is None or stacksize is None:
                            raise Exception("Logic error, couldn't determine stack size or location for storage tracking!")
                        for z in range(stacksize):
                            compiled.append_code("  NOP" + stack.comment(stackloc + z, StackOperation.LOAD))

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

            if isinstance(needed_arg.type, PaddingCoreType):
                # Simple padding that the function will clean up on its own. Add that padding to the stack.
                for _ in range(needed_arg.type.padbytes):
                    stack.alloc(StackVar("builtin(padding)", CoreType('int8')))
                    temporary_stack_entries.append("builtin(padding)")

            elif isinstance(needed_arg.type, OutCoreType):
                # This is an out parameter, so we need to be able to track its position and what temporary
                # variable we assign to it so we can copy the value to our destination after calling.
                out_dest = self.expr_temp_name()
                out_mapping[pos] = out_dest
                stack_on_exit += stack.alloc(StackVar(out_dest, needed_arg.type, initialized=True))
                temporary_stack_entries.append(out_dest)

                stackloc = stack.absfind(out_dest)
                stacksize = stack.sizeof(out_dest)
                if stackloc is None or stacksize is None:
                    raise Exception("Logic error, couldn't determine stack size or location for storage tracking!")
                for z in range(stacksize):
                    compiled.append_code("  NOP" + stack.comment(stackloc + z, StackOperation.LOAD))

            elif isinstance(needed_arg.type, RegisterCoreType):
                # Because we can't just do the calculation here since a subsequent arg expression calculation
                # might clobber one of the registers, we delay this so that we do this after everything else.
                delayed_params.append(needed_arg.type)
                delayed_args.append(args[which_arg])
                delayed_generate.append(True)
                which_arg += 1

            elif isinstance(needed_arg.type, InOutCoreType):
                # Not only do we need to compute the input for this, but we need to copy the value back if the
                # input was a variable name or global variable reference, so we preserve in-out behavior.
                expr_dest = self.expr_temp_name()
                out_mapping[pos] = expr_dest

                arg_in_question = args[which_arg].value
                if isinstance(arg_in_question, cst.Name):
                    copy_mapping[arg_in_question.value] = expr_dest

                if needed_arg.type.is_string:
                    if needed_arg.type.const:
                        if isinstance(arg_in_question, cst.Name):
                            # We can use this directly, since there's no string copying that might occur.
                            is_usable = True
                        else:
                            try:
                                self.codegen_eval(arg_in_question, local_consts, context)
                                is_usable = True
                            except NonConstantExpressionException:
                                is_usable = False

                        if is_usable:
                            stack_on_exit += stack.alloc(StackVar(expr_dest, needed_arg.type))
                        else:
                            stack_on_exit += stack.alloc(StackVar(expr_dest, needed_arg.type.nonconst_clone()))

                    else:
                        if not needed_arg.name:
                            raise Exception("Logic error, cannot determine local string storage for unnamed parameter!")

                        # Initialize this variable with the local storage of the function parameter.
                        local_destination_storage = f"{function_prototype.name}_{needed_arg.name}_param"
                        stack_on_exit += stack.alloc(StackVar(expr_dest, needed_arg.type, initialized=True))

                        # We only clobber the A register with the string init macro.
                        clobbers.add("A")

                        compiled += self.generate_move_to(expr_dest, stack, clobbers, context, offset=-1)
                        compiled.append_code(f"  PUSHADDR {local_destination_storage}")
                        stack.location += 2
                else:
                    stack_on_exit += stack.alloc(StackVar(expr_dest, needed_arg.type))

                temporary_stack_entries.append(expr_dest)
                compiled += self.generate_expr_internal(arg_in_question, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(arg_in_question))
                which_arg += 1

                stackloc = stack.absfind(expr_dest)
                stacksize = stack.sizeof(expr_dest)
                if stackloc is None or stacksize is None:
                    raise Exception("Logic error, couldn't determine stack size or location for storage tracking!")
                for z in range(stacksize):
                    compiled.append_code("  NOP" + stack.comment(stackloc + z, StackOperation.LOAD))

            elif isinstance(needed_arg.type, PreservedCoreType):
                # This is just preserved, so we don't have to worry about copy it out, but we do need to allocate it.
                expr_dest = self.expr_temp_name()
                stack_on_exit += stack.alloc(StackVar(expr_dest, needed_arg.type))
                temporary_stack_entries.append(expr_dest)
                compiled += self.generate_expr_internal(args[which_arg].value, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(args[which_arg].value))
                which_arg += 1

                stackloc = stack.absfind(expr_dest)
                stacksize = stack.sizeof(expr_dest)
                if stackloc is None or stacksize is None:
                    raise Exception("Logic error, couldn't determine stack size or location for storage tracking!")
                for z in range(stacksize):
                    compiled.append_code("  NOP" + stack.comment(stackloc + z, StackOperation.LOAD))

            else:
                # This is just a normal core type, so we put it on the stack, and the function takes it back off again.
                # So we don't need to fix up the stack any when we come back from the function call.
                arg_in_question = args[which_arg].value
                expr_dest = self.expr_temp_name()

                if needed_arg.type.is_string:
                    if needed_arg.type.const:
                        if isinstance(arg_in_question, cst.Name):
                            # We can use this directly, since there's no string copying that might occur.
                            is_usable = True
                        else:
                            try:
                                self.codegen_eval(arg_in_question, local_consts, context)
                                is_usable = True
                            except NonConstantExpressionException:
                                is_usable = False

                        if is_usable:
                            stack.alloc(StackVar(expr_dest, needed_arg.type))
                        else:
                            stack.alloc(StackVar(expr_dest, needed_arg.type.nonconst_clone()))

                    else:
                        if not needed_arg.name:
                            raise Exception("Logic error, cannot determine local string storage for unnamed parameter!")

                        # Initialize this variable with the local storage of the function parameter.
                        local_destination_storage = f"{function_prototype.name}_{needed_arg.name}_param"
                        stack.alloc(StackVar(expr_dest, needed_arg.type, initialized=True))

                        # We only clobber the A register with the string init macro.
                        clobbers.add("A")

                        compiled += self.generate_move_to(expr_dest, stack, clobbers, context, offset=-1)
                        compiled.append_code(f"  PUSHADDR {local_destination_storage}")
                        stack.location += 2
                else:
                    stack.alloc(StackVar(expr_dest, needed_arg.type))

                temporary_stack_entries.append(expr_dest)
                compiled += self.generate_expr_internal(arg_in_question, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(args[which_arg].value))
                which_arg += 1

                stackloc = stack.absfind(expr_dest)
                stacksize = stack.sizeof(expr_dest)
                if stackloc is None or stacksize is None:
                    raise Exception("Logic error, couldn't determine stack size or location for storage tracking!")
                for z in range(stacksize):
                    compiled.append_code("  NOP" + stack.comment(stackloc + z, StackOperation.LOAD))

        # Now, load our registers up with any register parameters.
        stack_skip = 0
        for i in range(len(delayed_params) - 1, -1, -1):
            delayed_needed_arg = delayed_params[i]
            provided_arg = delayed_args[i]

            # All functions that take a register core type assume signed integers.
            reg_to_type = {
                "A": "int8",
            }
            if delayed_needed_arg.register not in reg_to_type:
                raise Exception(f"Logic error, tried to assign a param to unsupported register {delayed_needed_arg.register} in function {function_prototype.name}")

            # Make sure we mark this as clobbered since we're going to mess it up.
            clobbers.add(delayed_needed_arg.register)

            if delayed_generate[i]:
                reg_dest = self.expr_temp_name()
                stack.alloc(StackVar(reg_dest, CoreType(reg_to_type[delayed_needed_arg.register])))
                compiled += self.generate_expr_internal(provided_arg.value, reg_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(provided_arg.value))
                compiled += self.generate_move_to(reg_dest, stack, clobbers, context)
                compiled.append_code(f"  LOAD {delayed_needed_arg.register}" + stack.comment(stack.location, StackOperation.LOAD))
                stack.free(reg_dest)
            else:
                if not isinstance(arg.value, UnvalidatedName):
                    raise Exception("Logic error, params that don't need generation should be on the stack!")
                reg_dest = arg.value.value
                compiled += self.generate_move_to(reg_dest, stack, clobbers, context)
                compiled.append_code(f"  LOAD {delayed_needed_arg.register}" + stack.comment(stack.location, StackOperation.LOAD))
                stack_skip += 1

        # Now, we're ready to actually call the function. Move to the last byte of the last parameter on the stack.
        move_amount = stack.diff(stack.size - (stack_skip + 1))
        compiled += self.generate_move_by("moving to last parameter", move_amount, stack, clobbers, context)
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
                    compiled += self.generate_move_to(destination, stack, clobbers, context)
                    if function_prototype.return_type.register == "A":
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
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
                    compiled += self.generate_memcpy_stackvars(dst, src, stack, clobbers, context, register="U" if unsafe_to_clobber else "A")
                else:
                    raise CompilerError("Unsupported byref assignment from different variable sizes", context)

        # Now, if the return is in one of the parameters, copy that to our destination.
        if isinstance(function_prototype.return_type, ParamReturnCoreType):
            return_handled = True
            if destination is not None:
                src = out_mapping[function_prototype.return_type.position]
                dst = destination

                source_size = stack.sizeof(src)
                source_type = stack.typeof(src)
                dest_size = stack.sizeof(dst)
                dest_type = stack.typeof(dst)
                if source_size is None or source_type is None:
                    raise Exception(f"Logic error, undefined variable reference to {src!r}", context)
                if dest_size is None or dest_type is None:
                    raise Exception("Logic error, cannot find destination to copy variable value to!")

                if source_type.is_string and dest_type.is_string and not ((source_type.const and dest_type.const) or safe_assign(dst)):
                    # We need to allocate locally and strcpy over.
                    if not stack.initof(dst):
                        compiled += self.generate_local_storage_alloc(dst, stack, clobbers, allocations, context)

                        # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                        stack.init(dst)

                    # Now, set up the stack for a strcpy operation, to initialize the local data with
                    # a copy of the function return we're copying in.
                    if stack[-1].name != dst:
                        # In order to ensure that it's possible to do stack math on this value, locate it in
                        # a temporary location for the time being if the destination isn't the top of the stack.
                        lhs_dest = self.expr_temp_name()
                        stack.alloc(StackVar(lhs_dest, CoreType("str"), initialized=True))

                        compiled += self.generate_memcpy_stackvars(lhs_dest, dst, stack, clobbers, context)
                    else:
                        # Safe to put first parameter in the top of the stack where it already is useful for math.
                        lhs_dest = dst

                    # Now, point at it.
                    rhs_dest = self.expr_temp_name()
                    stack.alloc(StackVar(rhs_dest, CoreType("str"), initialized=True))
                    compiled += self.generate_memcpy_stackvars(rhs_dest, src, stack, clobbers, context)

                    # Now call strcpy.
                    compiled += self.generate_function_call_internal(
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
                    if lhs_dest != dst:
                        stack.free(lhs_dest)

                else:
                    stack.init(dst)

                    if source_size == dest_size:
                        compiled += self.generate_memcpy_stackvars(dst, src, stack, clobbers, context, register="U" if unsafe_to_clobber else "A")
                    else:
                        raise CompilerError("Unsupported function return from different variable sizes", context)

        # Now, fix up our view of the stack.
        for entry in reversed(temporary_stack_entries):
            stack.free(entry)

        # Now, if needed, copy the return value from the stack to its location.
        if (not return_handled) and (not (function_prototype.return_type.is_void)):
            if destination is not None:
                if is_register_destination(destination):
                    # Pop the value from the stack, instead of copying.
                    src_loc = normal_return_loc
                    src_size = function_prototype.return_type.size
                    if src_size != 1:
                        raise Exception(f"Logic error, trying to assign value of size {src_size} to A register")

                    move_amt = stack.diff(src_loc)
                    compiled += self.generate_move_by("seeking return location", move_amt, stack, clobbers, context)
                    compiled.append_code("  LOAD A" + f" ; STACKOFF: func({function_prototype.name}) + 0")
                else:
                    src_loc = normal_return_loc
                    src_type = function_prototype.return_type
                    src_size = function_prototype.return_type.size
                    dest_loc = stack.absfind(destination)
                    dest_type = stack.typeof(destination)
                    dest_size = stack.sizeof(destination)
                    if dest_loc is None or dest_size is None or dest_type is None:
                        raise Exception(f"Logic error, cannot find destination {destination} to copy variable value to!")

                    if src_type.is_string and dest_type.is_string and not ((src_type.const and dest_type.const) or safe_assign(destination)):
                        # We need to make room on the stack for temporary values to call strcpy(), but the return loc is on the
                        # stack and untracked. So, while we get back stack locations that are less than the return location plus
                        # the return size, keep allocating padding.
                        padding_names: List[str] = []
                        while stack.size < src_loc + src_size:
                            pad_name = f"builtin(retpad_{stack.size})"
                            stack.alloc(StackVar(pad_name, CoreType("uint8", const=True), initialized=True))
                            padding_names.append(pad_name)

                        # We need to allocate locally and strcpy over.
                        if not stack.initof(destination):
                            compiled += self.generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                            # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                            stack.init(destination)

                        # Now, set up the stack for a strcpy operation, to initialize the local data with
                        # a copy of the function return we're copying in.
                        if stack[-1].name != destination:
                            # In order to ensure that it's possible to do stack math on this value, locate it in
                            # a temporary location for the time being if the destination isn't the top of the stack.
                            lhs_dest = self.expr_temp_name()
                            stack.alloc(StackVar(lhs_dest, CoreType("str"), initialized=True))

                            compiled += self.generate_memcpy_stackvars(lhs_dest, destination, stack, clobbers, context)
                        else:
                            # Safe to put first parameter in the top of the stack where it already is useful for math.
                            lhs_dest = destination

                        # Now, point at it.
                        rhs_dest = self.expr_temp_name()
                        stack.alloc(StackVar(rhs_dest, CoreType("str"), initialized=True))
                        rhs_loc = stack.absfind(rhs_dest)
                        if rhs_loc is None:
                            raise Exception("Logic error, cannot find stack variable we just created!")

                        stack.nameloc(f"func({function_prototype.name})", src_loc, src_size, StackOperation.LOAD)
                        compiled += self.generate_memcpy_locations(src_loc, rhs_loc, src_size, stack, clobbers, context, register="U" if unsafe_to_clobber else "A")
                        stack.unnameloc(f"func({function_prototype.name})")

                        # Now call strcpy.
                        compiled += self.generate_function_call_internal(
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

                        # Now, free the padding.
                        for pad_name in reversed(padding_names):
                            stack.free(pad_name)

                    else:
                        stack.init(destination)

                        if src_size == dest_size:
                            stack.nameloc(f"func({function_prototype.name})", src_loc, src_size, StackOperation.LOAD)
                            compiled += self.generate_memcpy_locations(src_loc, dest_loc, dest_size, stack, clobbers, context, register="U" if unsafe_to_clobber else "A")
                            stack.unnameloc(f"func({function_prototype.name})")
                        else:
                            raise CompilerError("Unsupported function return from different variable sizes", context)

        return compiled

    def generate_function_call(
        self,
        call: cst.Call,
        destination: Optional[str],
        types: Dict[cst.CSTNode, CoreType],
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
        refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
        local_consts: List[Constant],
        context: Context,
    ) -> Sections:
        # Generate builtins code for python intrinsics that we wish to support.
        if isinstance(call.func, cst.Name) and call.func.value in {"len", "str", "peek", "poke", "abs", "bool", "chr", "ord", "int", "hex", "min", "max", "fixed", "range", "cast"}:
            function_prototype = self.get_function_prototype(call, [*refs, *builtin_functions()], local_consts, context)
            args, arg_types = self.get_function_params(call, function_prototype, context)

            if function_prototype.name == "range":
                # Should only be uesd inside of for statements.
                raise CompilerError("Unsupported use of range function.", context)

            if function_prototype.name == "fixed":
                # Should only be uesd inside of for statements.
                raise CompilerError("Unsupported use of fixed function.", context)

            if function_prototype.name == "len":
                if len(args) != 1 or len(arg_types) != 1:
                    raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

                if destination is None:
                    raise CompilerError("Unsupported expression without assignment", context)

                # String or array length calculation.
                return self.generate_function_call_internal(
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
                    raise CompilerError("Unsupported expression without assignment", context)

                # Cast from whatever data type to string, so we must handle this on a case by case basis.
                expr = args[0].value

                if types[expr].is_string:
                    # We're done, this is already a string.
                    return self.generate_expr_internal(expr, destination, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

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

                        compiled += self.generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                        # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                        stack.init(destination)

                    # We need to do a strcpy at this point, to the destination.
                    clobbers.add("SPC")
                    clobbers.add("A")

                    # Calculate the expression we're converting to a string.
                    compiled += self.generate_expr_internal(expr, "register(A, char)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                    # Set up the SPC to point at the string.
                    compiled += self.generate_move_to(destination, stack, clobbers, context, offset=1)
                    compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
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
                    return self.generate_expr_internal(
                        fake_expr,
                        destination,
                        types,
                        stack,
                        clobbers,
                        allocations,
                        refs,
                        local_consts,
                        context.virtual(true).virtual(false).virtual(fake_expr),
                    )

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

                        compiled += self.generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

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
                    compiled += self.generate_function_call_internal(
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

                if len(args) != 2 or len(arg_types) != 2:
                    raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

                # Figure out if we have a sentinel second parameter or if it's real.
                sentinel = isinstance(args[1].value, SentinelInteger)

                # Generate the actual memory address that we're going to peek from.
                addr_expr = args[0].value
                addr_dest = self.expr_temp_name()
                stack.alloc(StackVar(addr_dest, CoreType("uint16"), initialized=True))
                compiled += self.generate_expr_internal(addr_expr, addr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(addr_expr))

                # This is going to clobber the SPC no matter what.
                clobbers.add("SPC")

                if destination is None:
                    if not sentinel:
                        # We could support this, but there isn't anything that needs it, so let's keep it simple.
                        raise CompilerError("Cannot provide a length parameter to peek when performing a dummy read", context)

                    # Assume that this is just a read of an address to clear a hardware register that's clear on read.
                    compiled += self.generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                    compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
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
                        if not sentinel:
                            if destination_type.type == "char":
                                raise CompilerError("Cannot provide a length parameter to peek when reading characters", context)
                            else:
                                raise CompilerError("Cannot provide a length parameter to peek when reading integers", context)

                        # This one's an easy one, just move to the right spot and load the value, copying it over.
                        compiled += self.generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                        compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                        compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
                        compiled.append_code("  POP SPC")
                        stack.move(-2)
                        compiled.code += comment_stack(stack)

                        clobbers.add("A")
                        compiled.append_code("  SWAP PC, SPC")
                        compiled.append_code("  LOAD A")
                        compiled.append_code("  SWAP PC, SPC")

                        if not is_register_destination(destination):
                            compiled += self.generate_move_to(destination, stack, clobbers, context)
                            compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                            stack.init(destination)

                    elif destination_type.type == "bool":
                        if not sentinel:
                            raise CompilerError("Cannot provide a length parameter to peek when reading booleans", context)

                        # Can't just load like above, our compiler assumes that boolean true/false is always 0xff/0x00.
                        # So if we load a value and pretend it's boolean it could mess up any other boolean checks.
                        compiled += self.generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                        compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                        compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
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
                            compiled += self.generate_move_to(destination, stack, clobbers, context)
                            compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                            stack.init(destination)

                    elif destination_type.type in {"int16", "uint16"}:
                        if not sentinel:
                            raise CompilerError("Cannot provide a length parameter to peek when reading integers", context)

                        # This one's slightly harder, need to copy two things, but that's manageable.
                        compiled += self.generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                        compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                        compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
                        compiled.append_code("  POP SPC")
                        stack.move(-2)
                        compiled.code += comment_stack(stack)

                        clobbers.add("A")
                        compiled.append_code("  SWAP PC, SPC")
                        compiled.append_code("  LOAD A")
                        compiled.append_code("  SWAP PC, SPC")

                        compiled += self.generate_move_to(destination, stack, clobbers, context, offset=1)
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

                        compiled.append_code("  SWAP PC, SPC")
                        compiled.append_code("  INCPC")
                        compiled.append_code("  LOAD A")
                        compiled.append_code("  SWAP PC, SPC")

                        compiled.append_code("  INCPC")
                        stack.move(-1)
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

                    elif destination_type.type in {"int32", "uint32"}:
                        if not sentinel:
                            raise CompilerError("Cannot provide a length parameter to peek when reading integers", context)

                        # This one needs to copy 4 things, but I'm gonna unroll that since it's easier than writing a loop.
                        compiled += self.generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                        compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                        compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
                        compiled.append_code("  POP SPC")
                        stack.move(-2)
                        compiled.code += comment_stack(stack)

                        clobbers.add("A")
                        compiled.append_code("  SWAP PC, SPC")
                        compiled.append_code("  LOAD A")
                        compiled.append_code("  SWAP PC, SPC")

                        compiled += self.generate_move_to(destination, stack, clobbers, context, offset=3)
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

                        # Second byte.
                        compiled.append_code("  SWAP PC, SPC")
                        compiled.append_code("  INCPC")
                        compiled.append_code("  LOAD A")
                        compiled.append_code("  SWAP PC, SPC")

                        compiled.append_code("  INCPC")
                        stack.move(-1)
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

                        # Third byte.
                        compiled.append_code("  SWAP PC, SPC")
                        compiled.append_code("  INCPC")
                        compiled.append_code("  LOAD A")
                        compiled.append_code("  SWAP PC, SPC")

                        compiled.append_code("  INCPC")
                        stack.move(-1)
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

                        # Fourth byte.
                        compiled.append_code("  SWAP PC, SPC")
                        compiled.append_code("  INCPC")
                        compiled.append_code("  LOAD A")
                        compiled.append_code("  SWAP PC, SPC")

                        compiled.append_code("  INCPC")
                        stack.move(-1)
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

                    elif destination_type.type == "str":
                        # Recast this as a string pointer, since that's what it is.
                        stack.retype(addr_dest, CoreType("str", const=True))

                        # We also need to make sure the destination is initalized so we can do a strcpy.
                        if not stack.initof(destination):
                            compiled += self.generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                            # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                            stack.init(destination)

                        if not sentinel:
                            length_dest = self.expr_temp_name()
                            stack.alloc(StackVar(length_dest, CoreType("uint8")))
                            compiled += self.generate_expr_internal(args[1].value, length_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(args[1].value))

                            compiled += self.generate_function_call_internal(
                                create_call("strncpy", [UnvalidatedName(destination), UnvalidatedName(addr_dest), UnvalidatedName(length_dest)]),
                                None,
                                types,
                                stack,
                                clobbers,
                                allocations,
                                refs,
                                local_consts,
                                context,
                            )

                            stack.free(length_dest)

                        else:
                            compiled += self.generate_function_call_internal(
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
                addr_dest = self.expr_temp_name()
                stack.alloc(StackVar(addr_dest, CoreType("uint16"), initialized=True))
                compiled += self.generate_expr_internal(addr_expr, addr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(addr_expr))

                # Then, generate the expression we're going to poke into the above address.
                data_expr = args[1].value
                data_dest = self.expr_temp_name()
                stack.alloc(StackVar(data_dest, types[data_expr].const_clone(), initialized=True))
                compiled += self.generate_expr_internal(data_expr, data_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(data_expr))

                # This is going to clobber the SPC and A no matter what.
                clobbers.add("SPC")
                clobbers.add("A")

                if types[data_expr].type in {"int8", "uint8", "char", "bool"}:
                    # This one's an easy one, just move to the right spot and store the value, copying it over.
                    # There's no special case for bool here, since we control it's contents and are just storing it.
                    compiled += self.generate_move_to(data_dest, stack, clobbers, context)
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))

                    compiled += self.generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                    compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
                    compiled.append_code("  POP SPC")
                    stack.move(-2)
                    compiled.code += comment_stack(stack)

                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  STORE A")
                    compiled.append_code("  SWAP PC, SPC")

                elif types[data_expr].type in {"int16", "uint16"}:
                    # This one's slightly harder, need to copy two things, but that's manageable.
                    compiled += self.generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                    compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
                    compiled.append_code("  POP SPC")
                    stack.move(-2)
                    compiled.code += comment_stack(stack)

                    compiled += self.generate_move_to(data_dest, stack, clobbers, context, offset=1)
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  STORE A")

                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  INCPC")
                    stack.move(-1)
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  SWAP PC, SPC")

                    compiled.append_code("  INCPC")
                    compiled.append_code("  STORE A")
                    compiled.append_code("  SWAP PC, SPC")

                elif types[data_expr].type in {"int32", "uint32"}:
                    # This one needs to copy 4 things, but I'm gonna unroll that since it's easier than writing a loop.
                    compiled += self.generate_move_to(addr_dest, stack, clobbers, context, offset=1)
                    compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
                    compiled.append_code("  POP SPC")
                    stack.move(-2)
                    compiled.code += comment_stack(stack)

                    compiled += self.generate_move_to(data_dest, stack, clobbers, context, offset=3)
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  STORE A")

                    # Second byte.
                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  INCPC")
                    stack.move(-1)
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  SWAP PC, SPC")

                    compiled.append_code("  INCPC")
                    compiled.append_code("  STORE A")

                    # Third byte.
                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  INCPC")
                    stack.move(-1)
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  SWAP PC, SPC")

                    compiled.append_code("  INCPC")
                    compiled.append_code("  STORE A")

                    # Fourth byte.
                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code("  INCPC")
                    stack.move(-1)
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  SWAP PC, SPC")

                    compiled.append_code("  INCPC")
                    compiled.append_code("  STORE A")
                    compiled.append_code("  SWAP PC, SPC")

                elif types[data_expr].type == "str":
                    # Recast this as a string pointer, since that's what it is.
                    stack.retype(addr_dest, CoreType("str"))

                    compiled += self.generate_function_call_internal(
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
                    raise CompilerError("Unsupported expression without assignment", context)

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
                    raise CompilerError("The builtin function abs() only works on integers", context)

                # If it's already unsigned, don't do anything to it.
                if destination_type.is_unsigned:
                    return self.generate_expr_internal(args[0].value, destination, types, stack, clobbers, allocations, refs, local_consts, context.wrap(args[0].value))
                else:
                    return self.generate_function_call_internal(
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
                    raise CompilerError("Unsupported expression without assignment", context)

                # Cast from whatever data type to string, so we must handle this on a case by case basis.
                expr = args[0].value

                if types[expr].is_bool:
                    # We're done, this is already a boolean.
                    return self.generate_expr_internal(expr, destination, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                elif types[expr].is_string:
                    # Need to see if this string is an empty string or not.
                    compiled = Sections()

                    # Evaluate the expression itself.
                    expr_dest = self.expr_temp_name()
                    stack.alloc(StackVar(expr_dest, CoreType("str", const=True), initialized=True))
                    compiled += self.generate_expr_internal(expr, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                    clobbers.add("SPC")
                    clobbers.add("A")

                    # Now, dereference the string and find out if it's an empty string or not.
                    compiled += self.generate_move_to(expr_dest, stack, clobbers, context, offset=1)
                    compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
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
                        compiled += self.generate_move_to(destination, stack, clobbers, context)
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
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
                    compiled += self.generate_expr_internal(expr, dest_loc, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                    # Now, figure out if the expression was nonzero (boolean True) or zero (boolean False)
                    compiled.append_code("  ADDI 0")
                    compiled.append_code("  LOADI 0x00")
                    compiled.append_code("  SKIPIF ZF")
                    compiled.append_code("  INV")

                    if not is_register_destination(destination):
                        compiled += self.generate_move_to(destination, stack, clobbers, context)
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                        stack.init(destination)

                    return compiled

                elif types[expr].size == 2:
                    compiled = Sections()

                    # Evaluate the expression itself.
                    expr_dest = self.expr_temp_name()
                    stack.alloc(StackVar(expr_dest, types[expr], initialized=True))
                    compiled += self.generate_expr_internal(expr, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                    # Now, figure out if the expression was nonzero (boolean True) or zero (boolean False)
                    compiled += self.generate_move_to(expr_dest, stack, clobbers, context, offset=1)

                    end_conversion = self.local_label_name(context, "end_conversion")

                    # First byte check with short circuiting for non-zero.
                    clobbers.add("A")
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  INCPC")
                    compiled.append_code("  ADDI 0")
                    compiled.append_code("  LOADI 0xFF")
                    compiled.append_code(f"  JRINZ {end_conversion}")
                    stack.move(-1)

                    # Second byte check.
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  ADDI 0")
                    compiled.append_code("  LOADI 0x00")
                    compiled.append_code("  SKIPIF ZF")
                    compiled.append_code("  INV")
                    compiled.append_code(f"{end_conversion}:")

                    stack.free(expr_dest)

                    if not is_register_destination(destination):
                        compiled += self.generate_move_to(destination, stack, clobbers, context)
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                        stack.init(destination)

                    return compiled

                elif types[expr].size == 4:
                    compiled = Sections()

                    # Evaluate the expression itself.
                    expr_dest = self.expr_temp_name()
                    stack.alloc(StackVar(expr_dest, types[expr], initialized=True))
                    compiled += self.generate_expr_internal(expr, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                    # Now, figure out if the expression was nonzero (boolean True) or zero (boolean False)
                    compiled += self.generate_move_to(expr_dest, stack, clobbers, context, offset=3)

                    end_conversion_first_byte = self.local_label_name(context, "end_conversion_first_byte")
                    end_conversion_second_byte = self.local_label_name(context, "end_conversion_second_byte")
                    end_conversion = self.local_label_name(context, "end_conversion")

                    # First byte check with short circuiting for non-zero.
                    clobbers.add("A")
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  INCPC")
                    compiled.append_code("  ADDI 0")
                    compiled.append_code("  LOADI 0xFF")
                    compiled.append_code(f"  JRINZ {end_conversion_first_byte}")
                    stack.move(-1)

                    # Second byte check with short circuiting for non-zero.
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  INCPC")
                    compiled.append_code("  ADDI 0")
                    compiled.append_code("  LOADI 0xFF")
                    compiled.append_code(f"  JRINZ {end_conversion_second_byte}")
                    stack.move(-1)

                    # Third byte check with short circuiting for non-zero.
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  INCPC")
                    compiled.append_code("  ADDI 0")
                    compiled.append_code("  LOADI 0xFF")
                    compiled.append_code(f"  JRINZ {end_conversion}")
                    stack.move(-1)

                    # Fourth byte check.
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
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

                    stack.free(expr_dest)

                    if not is_register_destination(destination):
                        compiled += self.generate_move_to(destination, stack, clobbers, context)
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                        stack.init(destination)

                    return compiled

                else:
                    raise Exception(f"Logic error, unexpected type {types[expr]} in bool() evaluation!")

            elif function_prototype.name == "chr":
                if len(args) != 1 or len(arg_types) != 1:
                    raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

                if destination is None:
                    raise CompilerError("Unsupported expression without assignment", context)

                # Cast from integer to char, but the 8-bit case is simple.
                expr = args[0].value

                if not types[expr].is_integer:
                    raise CompilerError("Unsupported conversion from {types[expr].type} to character", context)

                if types[expr].size == 1:
                    # Simply evaluate the expression into the destination directly, but pretend that the destination
                    # is an integer instead of a character.
                    compiled = Sections()

                    # Evaluate the expression itself.
                    dest_loc = "register(A, uint8)" if types[expr].is_unsigned else "register(A, int8)"
                    clobbers.add("A")
                    compiled += self.generate_expr_internal(expr, dest_loc, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                    if not is_register_destination(destination):
                        compiled += self.generate_move_to(destination, stack, clobbers, context)
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                        stack.init(destination)

                    return compiled

                elif types[expr].size in {2, 4}:
                    compiled = Sections()

                    # Evaluate the expression itself.
                    expr_dest = self.expr_temp_name()
                    stack.alloc(StackVar(expr_dest, types[expr], initialized=True))
                    compiled += self.generate_expr_internal(expr, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                    # Now, load the bottom byte into the A register to return it.
                    compiled += self.generate_move_to(expr_dest, stack, clobbers, context)
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    stack.free(expr_dest)

                    if not is_register_destination(destination):
                        clobbers.add("A")
                        compiled += self.generate_move_to(destination, stack, clobbers, context)
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                        stack.init(destination)

                    return compiled

                else:
                    raise Exception(f"Logic error, unexpected type {types[expr]} in chr() evaluation!")

            elif function_prototype.name == "ord":
                if len(args) != 1 or len(arg_types) != 1:
                    raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

                if destination is None:
                    raise CompilerError("Unsupported expression without assignment", context)

                # Cast from integer to char, but the 8-bit case is simple.
                expr = args[0].value

                if not types[expr].is_char:
                    raise CompilerError("Unsupported conversion from {types[expr].type} to integer", context)

                # Figure out what to do based on the destination type.
                destination_type = stack.typeof(destination)
                if destination_type is None:
                    raise Exception("Logic error, couldn't determine destination type for ord!")

                # Simply evaluate the expression into the destination directly, but pretend that the destination
                # is a character instead of an integer.
                compiled = Sections()

                # Evaluate the expression itself.
                clobbers.add("A")
                compiled += self.generate_expr_internal(expr, "register(A, char)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                # Intentionally zero-sign in the signed int16/int32 cases below since we know that the ord(some_char) should never be negative.
                if destination_type.size == 1:
                    if not is_register_destination(destination):
                        compiled += self.generate_move_to(destination, stack, clobbers, context)
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                        stack.init(destination)

                    return compiled

                elif destination_type.size == 2:
                    compiled += self.generate_move_to(destination, stack, clobbers, context)
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                    compiled.append_code("  INCPC")
                    compiled.append_code("  STOREI 0")
                    stack.move(-1)
                    stack.init(destination)

                    return compiled

                elif destination_type.size == 4:
                    compiled += self.generate_move_to(destination, stack, clobbers, context)
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                    compiled.append_code("  INCPC")
                    stack.move(-1)
                    compiled.append_code("  LOADI 0")
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                    compiled.append_code("  INCPC")
                    stack.move(-1)
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                    compiled.append_code("  INCPC")
                    stack.move(-1)
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                    stack.init(destination)

                    return compiled

                else:
                    raise Exception(f"Logic error, unexpected type {destination_type} in ord() evaluation!")

            elif function_prototype.name == "int":
                if len(args) != 1 or len(arg_types) != 1:
                    raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

                if destination is None:
                    raise CompilerError("Unsupported expression without assignment", context)

                # This could be a passthrough, in the case of an integer input, undefined in case of char, a simple
                # cast in case of bool, and an atoi call in case of a string.
                expr = args[0].value

                if types[expr].is_integer:
                    compiled = Sections()
                    compiled += self.generate_expr_internal(expr, destination, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))
                    return compiled

                elif types[expr].is_char:
                    raise CompilerError("Unsupported conversion from {types[expr].type} to integer", context)

                elif types[expr].is_bool:
                    clobbers.add("A")
                    compiled = Sections()
                    compiled += self.generate_expr_internal(expr, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))

                    # Set to 0 or 1 like python does for boolean values. Load immediate is a 2 byte instruction so we can't
                    # SKIPIF it. However, we know that booleans in our system are either 0x00 or 0xFF so we can set to 0 by
                    # leaving A alone, and set to 1 by adding 2 to 255.
                    compiled.append_code("  ADDI 0")
                    compiled.append_code("  SKIPIF ZF")
                    compiled.append_code("  ADDI 2")

                    if not is_register_destination(destination):
                        compiled += self.generate_move_to(destination, stack, clobbers, context)
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                        stack.init(destination)

                    return compiled

                elif types[expr].is_string:
                    destination_type = stack.typeof(destination)
                    if destination_type is None:
                        raise Exception("Logic error, couldn't determine destination type for int!")

                    if not destination_type.is_integer:
                        raise CompilerError("Cannot assign the result of ord to non-integer type {destination_type.type}", context)

                    if destination_type.size == 1:
                        func = "atoi8"
                    elif destination_type.size == 2:
                        func = "atoi16"
                    elif destination_type.size == 4:
                        func = "atoi32"
                    else:
                        raise Exception("Logic error, unsupported destination size for int()!")

                    return self.generate_function_call_internal(
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

            elif function_prototype.name == "hex":
                if len(args) != 1 or len(arg_types) != 1:
                    raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

                if destination is None:
                    raise CompilerError("Unsupported expression without assignment", context)

                destination_type = stack.typeof(destination)
                if destination_type is None:
                    raise Exception("Logic error, cannot find destination type for hex() conversion!")

                expr = args[0].value
                if not destination_type.is_string or not types[expr].is_integer:
                    raise CompilerError("The builtin function hex() only converts integers to strings", context)

                compiled = Sections()

                # Now, convert to hexadecimal.
                if types[expr].size == 1:
                    needed_function = "itohex8"
                elif types[expr].size == 2:
                    needed_function = "itohex16"
                else:
                    needed_function = "itohex32"

                # We need to cast this by creating a string, so we need to allocate that string on the stack.
                if not stack.initof(destination):
                    # We're creating a string in an unusual place, given that normally we only create strings on the LHS
                    # of any assignment. So, we must hand-check our destination's size in case it was declared const as
                    # an optimization for avoiding strcpy.
                    if (not destination_type.is_array) and destination_type.const:
                        destination_type.length = needed_length

                    compiled += self.generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                    # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                    stack.init(destination)

                compiled += self.generate_function_call_internal(
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

            elif function_prototype.name in {"min", "max"}:
                if len(args) != 2 or len(arg_types) != 2:
                    raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

                if destination is None:
                    raise CompilerError("Unsupported expression without assignment", context)

                destination_type = stack.typeof(destination)
                if destination_type is None:
                    raise Exception("Logic error, cannot find destination type for min/max function!")

                left = args[0].value
                right = args[1].value
                if not destination_type.is_integer or not types[left].is_integer or not types[right].is_integer:
                    raise CompilerError(f"The builtin function {function_prototype.name}() only compares integers", context)

                if destination_type.size == 1:
                    if destination_type.is_unsigned:
                        func_name = f"u{function_prototype.name}8"
                    else:
                        func_name = f"{function_prototype.name}8"
                elif destination_type.size == 2:
                    if destination_type.is_unsigned:
                        func_name = f"u{function_prototype.name}16"
                    else:
                        func_name = f"{function_prototype.name}16"
                elif destination_type.size == 4:
                    if destination_type.is_unsigned:
                        func_name = f"u{function_prototype.name}32"
                    else:
                        func_name = f"{function_prototype.name}32"
                else:
                    raise Exception(f"Logic error, unexpected comparison size {destination_type.size}!")

                return self.generate_function_call_internal(
                    create_call(func_name, [left, right]),
                    destination,
                    types,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context,
                )

            elif function_prototype.name == "cast":
                if len(args) != 2 or len(arg_types) != 2:
                    raise Exception("Logic error, should have raised a compiler error for incorrect parameters above!")

                if destination is None:
                    raise CompilerError("Unsupported expression without assignment", context)

                # Cast from given type to specified type.
                requested = self.get_type(args[0].value, local_consts, allow_nopad=False, allow_extern=False, allow_array=False)
                expr = args[1].value

                if not requested:
                    raise CompilerError("Unrecognized type in cast", context)

                if requested.type in {"uint16", "int16"}:
                    if not types[expr].is_string:
                        raise CompilerError("Unsupported cast from {types[expr]} to {requested}", context)
                elif requested.type in {"str"}:
                    if types[expr].type not in {"uint16", "int16"}:
                        raise CompilerError("Unsupported cast from {types[expr]} to {requested}", context)

                # Figure out what to do based on the destination type.
                destination_type = stack.typeof(destination)
                if destination_type is None:
                    raise Exception("Logic error, couldn't determine destination type for cast!")

                if destination_type.size != 2:
                    raise CompilerError("Cannot assign result of a cast to {destination_type}", context)

                # Simply evaluate the expression into the destination directly, but pretend that the destination
                # is the type we're casting to.
                compiled = Sections()

                # Evaluate the expression itself, but pretend the expr_dest is the source type.
                expr_dest = self.expr_temp_name()
                stack.alloc(StackVar(expr_dest, types[expr].const_clone(), initialized=True))
                compiled += self.generate_expr_internal(expr, expr_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expr))
                compiled += self.generate_memcpy_stackvars(destination, expr_dest, stack, clobbers, context)

                stack.free(expr_dest)
                return compiled

            else:
                raise Exception(f"Logic error, attempted to generate unsupported internal function {function_prototype.name}!")

        else:
            return self.generate_function_call_internal(call, destination, types, stack, clobbers, allocations, refs, local_consts, context)

    def generate_local_storage_alloc(
        self,
        destination: str,
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
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

        local_destination_storage = stack.labelof(destination, context)
        if local_destination_storage is None:
            raise Exception("Logic error, couldn't get local storage for string!")

        requested_length = dest_type.length or MAX_STRING_LENGTH
        if local_destination_storage in allocations:
            if allocations[local_destination_storage].size < requested_length:
                raise Exception("Logic error, re-allocation of local storage with different size!")
        else:
            # Attempt to re-use an earlier expression temporary if possible.
            found: Optional[str] = None

            if destination.startswith("builtin(expr_temp_"):
                for label, alloc in allocations.items():
                    if alloc.var.startswith("builtin(expr_temp_") and not alloc.used:
                        if alloc.size >= requested_length:
                            found = label
                            break

            if found:
                # Remember that we did this so we don't duplicate the allocation if we're conditionally allocating,
                # such as when an unallocated variable gets assigned two values in an if/else conditional.
                allocations[found].used = True
                allocations[local_destination_storage] = allocations[found]

            else:
                compiled.append_data(f"{local_destination_storage}:")
                compiled.append_data(f"  .pad {requested_length}")

                # Remember that we did this so we don't duplicate the allocation if we're conditionally allocating,
                # such as when an unallocated variable gets assigned two values in an if/else conditional.
                allocations[local_destination_storage] = Allocation(destination, local_destination_storage, requested_length)

        # We only clobber the A register with the string init macro.
        clobbers.add("A")

        compiled += self.generate_move_to(destination, stack, clobbers, context, offset=-1)
        compiled.append_code(f"  PUSHADDR {allocations[local_destination_storage].storage}")
        stack.location += 2

        return compiled

    def generate_variable_lookup(
        self,
        source: str,
        destination: Optional[str],
        stack: Stack,
        types: Dict[cst.CSTNode, CoreType],
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
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

                compiled += self.generate_move_to(source, stack, clobbers, context)
                compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))

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
                            compiled += self.generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                            # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                            stack.init(destination)

                        # Now, set up the stack for a strcpy operation, to initialize the local data with
                        # a copy of the constant we're initializing from.
                        if stack[-1].name != destination:
                            # In order to ensure that it's possible to do stack math on this value, locate it in
                            # a temporary location for the time being if the destination isn't the top of the stack.
                            lhs_dest = self.expr_temp_name()
                            stack.alloc(StackVar(lhs_dest, CoreType("str"), initialized=True))

                            compiled += self.generate_memcpy_stackvars(lhs_dest, destination, stack, clobbers, context)
                        else:
                            # Safe to put first parameter in the top of the stack where it already is useful for math.
                            lhs_dest = destination

                        # Now, point at it.
                        clobbers.add("A")

                        rhs_dest = self.expr_temp_name()
                        stack.alloc(StackVar(rhs_dest, CoreType("str"), initialized=True))
                        compiled += self.generate_move_to(rhs_dest, stack, clobbers, context, offset=-1)
                        compiled.append_code(f"  PUSHADDR {global_var.name}")
                        stack.location += 2

                        # Now call strcpy.
                        compiled += self.generate_function_call_internal(
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

                        compiled += self.generate_move_to(destination, stack, clobbers, context, offset=-1)
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

                            compiled += self.generate_move_to(destination, stack, clobbers, context, offset=i)
                            compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

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

                            compiled += self.generate_move_to(destination, stack, clobbers, context, offset=i)
                            compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

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
                            compiled += self.generate_move_by("seeking sign extend byte", move_amt, stack, clobbers, context)
                            compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

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
                            compiled += self.generate_move_by("seeking copy byte", move_amt, stack, clobbers, context)
                            compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

        else:
            if destination is None:
                raise CompilerError("Unsupported expression without assignment", context)
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
                    compiled += self.generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                    # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                    stack.init(destination)

                # Initializing this requires us to clobber the SPC and A.
                clobbers.add("SPC")
                clobbers.add("A")

                # Grab the character value itself.
                compiled += self.generate_move_to(source, stack, clobbers, context)
                compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))

                # Set up the SPC to point at the string.
                compiled += self.generate_move_to(destination, stack, clobbers, context, offset=1)
                compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
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
                    compiled += self.generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                    # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                    stack.init(destination)

                # Now, set up the stack for a strcpy operation, to initialize the local data with
                # a copy of the constant we're initializing from.
                if stack[-1].name != destination:
                    # In order to ensure that it's possible to do stack math on this value, locate it in
                    # a temporary location for the time being if the destination isn't the top of the stack.
                    lhs_dest = self.expr_temp_name()
                    stack.alloc(StackVar(lhs_dest, CoreType("str"), initialized=True))

                    compiled += self.generate_memcpy_stackvars(lhs_dest, destination, stack, clobbers, context)
                else:
                    # Safe to put first parameter in the top of the stack where it already is useful for math.
                    lhs_dest = destination

                # Now, point at it.
                rhs_dest = self.expr_temp_name()
                stack.alloc(StackVar(rhs_dest, CoreType("str"), initialized=True))

                compiled += self.generate_memcpy_stackvars(rhs_dest, source, stack, clobbers, context)

                # Now call strcpy.
                compiled += self.generate_function_call_internal(
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
                compiled += self.generate_memcpy_stackvars(destination, source, stack, clobbers, context)
            elif source_type.size > dest_type.size:
                # Copy, but with the destination size in mind, which should grab only the lower bits of the source.
                compiled += self.generate_memcpy_locations(source_loc, dest_loc, dest_type.size, stack, clobbers, context)
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
                    compiled += self.generate_move_by("seeking {source}", move_amt, stack, clobbers, context)
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  SHL")
                    compiled.append_code("  LOADI 0")
                    compiled.append_code("  SKIPIF !CF")
                    compiled.append_code("  INV")

                for pos in range(dest_type.size - source_type.size):
                    actual_pos = pos + dest_loc + source_type.size

                    move_amt = stack.diff(actual_pos)
                    compiled += self.generate_move_by("seeking sign extend byte", move_amt, stack, clobbers, context)
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

                # Need to copy the whole thing, and then zero out the top bytes we didn't touch.
                compiled += self.generate_memcpy_locations(source_loc, dest_loc, source_type.size, stack, clobbers, context)

        return compiled

    def generate_unary_expr(
        self,
        expression: cst.UnaryOperation,
        destination: str,
        types: Dict[cst.CSTNode, CoreType],
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
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
                raise CompilerError(f"Unsupported type {destination_type.type} for integer expression", context)

            if destination_size == 1:
                if is_register_destination(destination) or stack[-1].name != destination:
                    # In order to ensure that it's possible to negate this value, locate the rest of the expression
                    # in a temporary location.
                    internal_dest = self.expr_temp_name()
                    stack.alloc(StackVar(internal_dest, expr_integer_type(destination_size)))
                else:
                    # Safe to put the expression evaluation in our destination because we're just going to negate it.
                    internal_dest = destination

                compiled += self.generate_expr_internal(expression.expression, internal_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.expression))

                # Negation clobbers the A register, since it is the accumulator.
                clobbers.add("A")

                # Move to the parameter and negate it.
                compiled += self.generate_move_to(internal_dest, stack, clobbers, context)
                compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))

                if isinstance(expression.operator, cst.Minus):
                    compiled.append_code("  NEG")
                elif isinstance(expression.operator, cst.BitInvert):
                    compiled.append_code("  INV")
                else:
                    raise CompilerError("Unsupported unary operation {expr_to_str(expression)}", context)

                # This call puts the result in a, so check if that's what we want.
                if is_register_destination(destination):
                    stack.free(internal_dest)
                else:
                    compiled += self.generate_move_to(destination, stack, clobbers, context)
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                    if internal_dest != destination:
                        stack.free(internal_dest)
            elif destination_size in {2, 4}:
                # Calculate the expression inside the negation here, so we can send the temporary name to the function call
                # and trigger its optimized case.
                if stack[-1].name != destination:
                    internal_dest = self.expr_temp_name()
                    stack.alloc(StackVar(internal_dest, expr_integer_type(destination_size)))
                else:
                    internal_dest = destination

                compiled += self.generate_expr_internal(expression.expression, internal_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.expression))

                if isinstance(expression.operator, cst.Minus):
                    # Using the neg16 or neg32 function that's part of our stdlib.
                    function = "neg16" if destination_size == 2 else "neg32"
                    compiled += self.generate_function_call_internal(
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
                        compiled += self.generate_move_to(internal_dest, stack, clobbers, context, offset=actual_neg_offset(offset))
                        compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                        compiled.append_code("  INV")
                        compiled += self.generate_move_to(destination, stack, clobbers, context, offset=actual_neg_offset(offset))
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

                else:
                    raise CompilerError("Unsupported unary operation {expr_to_str(expression)}", context)

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

            if not types[expression.expression].is_bool:
                # Auto-coerce this to a bool by using the bool() builtin instead of forcing the coder to explicitly
                # wrap the statement in a boolean.
                test_coerced = create_call("bool", [expression.expression])
                types[test_coerced] = CoreType("bool")

                compiled += self.generate_expr_internal(
                    test_coerced, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.virtual(test_coerced).wrap(test_coerced)
                )
            else:
                compiled += self.generate_expr_internal(expression.expression, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context)

            compiled.append_code("  INV")

            if not is_register_destination(destination):
                compiled += self.generate_move_to(destination, stack, clobbers, context)
                compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

        else:
            # TODO: Handle Plus (no-op, just call with the expression value).
            raise CompilerError("Unsupported unary operation {expr_to_str(expression)}", context)

        return compiled

    def generate_binary_expr(
        self,
        expression: cst.BinaryOperation,
        destination: str,
        types: Dict[cst.CSTNode, CoreType],
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
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
                compiled += self.generate_expr_internal(expression.left, destination, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.left))

                # Now, again with the right!
                rhs_dest = self.expr_temp_name()
                stack.alloc(StackVar(rhs_dest, CoreType("str", const=True, length=destination_type.length)))
                compiled += self.generate_expr_internal(expression.right, rhs_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.right))

                # Now, call strcat to concatenate the two together!
                compiled += self.generate_function_call_internal(
                    create_call(
                        "strcat",
                        [UnvalidatedName(destination), UnvalidatedName(rhs_dest)]
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

            elif types[expression.right].is_char:
                # First, generate the left hand side of the expression.
                compiled += self.generate_expr_internal(expression.left, destination, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.left))

                # Now, generate the right hand side so we can assign it to the end of the string.
                clobbers.add("A")
                compiled += self.generate_expr_internal(expression.right, "register(A, char)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.right))

                # Save that character, since we need to use the A register to advance until the null pointer.
                clobbers.add("V")
                compiled.append_code("  MOV A, V")

                # Need to clobber the SPC to move to that location.
                clobbers.add("SPC")
                compiled += self.generate_move_to(destination, stack, clobbers, context, offset=1)
                compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
                compiled.append_code("  POP SPC")
                stack.move(-2)
                compiled.code += comment_stack(stack)

                advance_top = self.local_label_name(context, "advance_top")
                advance_bottom = self.local_label_name(context, "advance_bottom")

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
                lhs_dest = self.expr_temp_name()
                stack.alloc(StackVar(lhs_dest, expr_integer_type(destination_size)))
            else:
                # Safe to put first parameter in the top of the stack where it already is useful for math.
                lhs_dest = destination

            compiled += self.generate_expr_internal(expression.left, lhs_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.left))

            # Now, get the second parameter onto the stack in the right spot.
            rhs_dest = self.expr_temp_name()
            if isinstance(expression.operator, (cst.LeftShift, cst.RightShift)):
                stack.alloc(StackVar(rhs_dest, CoreType("uint8")))
            else:
                stack.alloc(StackVar(rhs_dest, expr_integer_type(destination_size)))
            compiled += self.generate_expr_internal(expression.right, rhs_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.right))

            # Now, perform some math of matics!
            if destination_size == 1:
                if isinstance(expression.operator, cst.Subtract):
                    if not destination_type.is_integer:
                        raise CompilerError(f"Unsupported type {destination_type.type} for integer expression", context)

                    if not is_register_destination(destination):
                        # Subtracting clobbers the A register, since it is the accumulator.
                        clobbers.add("A")

                    # Move to the second parameter and negate it.
                    compiled += self.generate_move_to(rhs_dest, stack, clobbers, context)
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  NEG")

                    # Move to the right spot on the stack to add to the negated right hand side.
                    compiled += self.generate_move_to(lhs_dest, stack, clobbers, context)
                    compiled.append_code("  ADD" + stack.comment(stack.location, StackOperation.LOAD))

                elif isinstance(expression.operator, (cst.Add, cst.BitAnd, cst.BitOr, cst.BitXor)):
                    if not destination_type.is_integer:
                        raise CompilerError(f"Unsupported type {destination_type.type} for integer expression", context)

                    if not is_register_destination(destination):
                        # Adding clobbers the A register, since it is the accumulator.
                        clobbers.add("A")

                    # Move to the right spot on the stack and then add the two numbers.
                    compiled += self.generate_move_to(rhs_dest, stack, clobbers, context)
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled += self.generate_move_to(lhs_dest, stack, clobbers, context)

                    if isinstance(expression.operator, cst.Add):
                        compiled.append_code("  ADD" + stack.comment(stack.location, StackOperation.LOAD))
                    elif isinstance(expression.operator, cst.BitAnd):
                        compiled.append_code("  AND" + stack.comment(stack.location, StackOperation.LOAD))
                    elif isinstance(expression.operator, cst.BitOr):
                        compiled.append_code("  OR" + stack.comment(stack.location, StackOperation.LOAD))
                    elif isinstance(expression.operator, cst.BitXor):
                        compiled.append_code("  XOR" + stack.comment(stack.location, StackOperation.LOAD))
                    else:
                        raise CompilerError(f"Unsupported operator {expression.operator} in integer expression", context)

                elif isinstance(expression.operator, (cst.Multiply, cst.LeftShift, cst.RightShift)):
                    if not destination_type.is_integer:
                        raise CompilerError(f"Unsupported type {destination_type.type} for integer expression", context)

                    if isinstance(expression.operator, cst.Multiply):
                        func = "mult8"
                    elif isinstance(expression.operator, cst.LeftShift):
                        func = "lshift8"
                    elif isinstance(expression.operator, cst.RightShift):
                        func = "rshift8"
                    else:
                        raise CompilerError(f"Unsupported operator {expression.operator} in integer expression", context)

                    compiled.append_code("  ; just before function call")
                    compiled += self.generate_function_call_internal(
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
                        raise CompilerError(f"Unsupported type {destination_type.type} for unsigned division expression", context)

                    # Division is weird, since the built-in stdlib function handles both modulo and division.
                    # The stdlib function is setup to return both in the input stack locations, so we need to
                    # copy the correct one out.
                    compiled += self.generate_function_call_internal(
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

                    compiled += self.generate_move_to(
                        rhs_dest if isinstance(expression.operator, cst.Modulo) else lhs_dest,
                        stack,
                        clobbers,
                        context,
                    )
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))

                else:
                    raise CompilerError(f"Unsupported run-time computation for {expression.operator}", context)

                # This call puts the result in a, so check if that's what we want.
                if is_register_destination(destination):
                    # Just make sure we bookkeep things. Both the LHS and RHS need to be unwound.
                    stack.free(rhs_dest)
                    stack.free(lhs_dest)
                else:
                    stack.free(rhs_dest)
                    compiled += self.generate_move_to(destination, stack, clobbers, context)
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
                    if lhs_dest != destination:
                        stack.free(lhs_dest)

            else:
                if isinstance(expression.operator, cst.Subtract):
                    if not destination_type.is_integer:
                        raise CompilerError(f"Unsupported type {destination_type.type} for integer expression", context)

                    # Using the neg16 or neg32 fnction that's part of our stdlib.
                    negfunc = "neg16" if destination_size == 2 else "neg32"
                    compiled += self.generate_function_call_internal(
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

                    compiled += self.generate_function_call_internal(
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
                        raise CompilerError(f"Unsupported type {destination_type.type} for integer expression", context)

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
                        raise CompilerError(f"Unsupported operator {expression.operator} in integer expression", context)

                    compiled += self.generate_function_call_internal(
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
                        raise CompilerError(f"Unsupported type {destination_type.type} for unsigned division expression", context)

                    # Division is weird, since the built-in stdlib function handles both modulo and division.
                    # The stdlib function is setup to return both in the input stack locations, so we need to
                    # copy the correct one out.
                    function = "udiv16" if destination_size == 2 else "udiv32"
                    compiled += self.generate_function_call_internal(
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
                        compiled += self.generate_memcpy_stackvars(destination, location, stack, clobbers, context)

                    # Now that we copied this to the destination, this is useless.
                    stack.free(rhs_dest)
                    if lhs_dest != destination:
                        stack.free(lhs_dest)

                elif isinstance(expression.operator, (cst.BitAnd, cst.BitOr, cst.BitXor)):
                    if not destination_type.is_integer:
                        raise CompilerError(f"Unsupported type {destination_type.type} for integer expression", context)

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
                        raise CompilerError(f"Unsupported operator {expression.operator} in integer expression", context)

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
                        compiled += self.generate_move_to(rhs_dest, stack, clobbers, context, offset=actual_expr_offset(offset))
                        compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                        compiled += self.generate_move_to(lhs_dest, stack, clobbers, context, offset=actual_expr_offset(offset))
                        compiled.append_code(function + stack.comment(stack.location, StackOperation.LOAD))
                        compiled += self.generate_move_to(destination, stack, clobbers, context, offset=actual_expr_offset(offset))
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

                    stack.free(rhs_dest)
                    if lhs_dest != destination:
                        stack.free(lhs_dest)

                else:
                    raise CompilerError(f"Unsupported run-time computation for {expression.operator}", context)

        return compiled

    def generate_boolean_expr(
        self,
        expression: cst.BooleanOperation,
        destination: str,
        types: Dict[cst.CSTNode, CoreType],
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
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

            if not types[expression.left].is_bool:
                # Auto-coerce this to a bool by using the bool() builtin instead of forcing the coder to explicitly
                # wrap the statement in a boolean.
                test_coerced = create_call("bool", [expression.left])
                types[test_coerced] = CoreType("bool")

                left_compiled = self.generate_expr_internal(
                    test_coerced, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.virtual(test_coerced).wrap(test_coerced)
                )
            else:
                left_compiled = self.generate_expr_internal(expression.left, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.left))

            cloned_stack = stack.clone()
            if not types[expression.right].is_bool:
                # Auto-coerce this to a bool by using the bool() builtin instead of forcing the coder to explicitly
                # wrap the statement in a boolean.
                test_coerced = create_call("bool", [expression.right])
                types[test_coerced] = CoreType("bool")

                right_compiled = self.generate_expr_internal(
                    test_coerced, "register(A, bool)", types, cloned_stack, clobbers, allocations, refs, local_consts, context.virtual(test_coerced).wrap(test_coerced)
                )
            else:
                right_compiled = self.generate_expr_internal(
                    expression.right,
                    "register(A, bool)",
                    types,
                    cloned_stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context.wrap(expression.right),
                )

            # Not unifying the stack here because short circuiting could mean that a walrus assign doesn't get run.
            if stack.size != cloned_stack.size:
                raise Exception("Logic error, stacks on both expressions not equal in size!")
            if stack.location != cloned_stack.location:
                # Need to make the right hand side move back to where it was before it started.
                move_amount = stack.location - cloned_stack.location
                right_compiled += self.generate_move_by("restore stack to start of expression", move_amount, cloned_stack, clobbers, context)

            # In order to possibly jump past the right expression, we need to know its length, so we can either JRI or LNGJUMP.
            right_length = get_assembled_length(right_compiled.code, refs)
            short_circuit = self.local_label_name(context, "short_circuit")
            if right_length >= 32:
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
                compiled += self.generate_move_to(destination, stack, clobbers, context)
                compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

        elif isinstance(expression.operator, cst.Or):
            # Perform short-circuiting OR, first by handling the left hand side, and if it
            # is True immediately skipping the second half.
            clobbers.add("A")

            if not types[expression.left].is_bool:
                # Auto-coerce this to a bool by using the bool() builtin instead of forcing the coder to explicitly
                # wrap the statement in a boolean.
                test_coerced = create_call("bool", [expression.left])
                types[test_coerced] = CoreType("bool")

                left_compiled = self.generate_expr_internal(
                    test_coerced, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.virtual(test_coerced).wrap(test_coerced)
                )
            else:
                left_compiled = self.generate_expr_internal(expression.left, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.left))

            cloned_stack = stack.clone()
            if not types[expression.right].is_bool:
                # Auto-coerce this to a bool by using the bool() builtin instead of forcing the coder to explicitly
                # wrap the statement in a boolean.
                test_coerced = create_call("bool", [expression.right])
                types[test_coerced] = CoreType("bool")

                right_compiled = self.generate_expr_internal(
                    test_coerced, "register(A, bool)", types, cloned_stack, clobbers, allocations, refs, local_consts, context.virtual(test_coerced).wrap(test_coerced)
                )
            else:
                right_compiled = self.generate_expr_internal(
                    expression.right,
                    "register(A, bool)",
                    types,
                    cloned_stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context.wrap(expression.right),
                )

            # Not unifying the stack here because short circuiting could mean that a walrus assign doesn't get run.
            if stack.size != cloned_stack.size:
                raise Exception("Logic error, stacks on both expression not equal in size!")
            if stack.location != cloned_stack.location:
                # Need to make the right hand side move back to where it was before it started.
                move_amount = stack.location - cloned_stack.location
                right_compiled += self.generate_move_by("restore stack to start of expression", move_amount, cloned_stack, clobbers, context)

            # In order to possibly jump past the right expression, we need to know its length, so we can either JRI or LNGJUMP.
            right_length = get_assembled_length(right_compiled.code, refs)
            short_circuit = self.local_label_name(context, "short_circuit")
            if right_length >= 32:
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
                compiled += self.generate_move_to(destination, stack, clobbers, context)
                compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

        else:
            raise CompilerError(f"Unsupported boolean operation {expr_to_str(expression)}", context)

        return compiled

    def generate_comparison_expr(
        self,
        expression: cst.Comparison,
        destination: str,
        types: Dict[cst.CSTNode, CoreType],
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
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
            raise CompilerError(f"Unsupported multi-comparison expression {expr_to_str(expression)}", context)

        # Special case for is checks.
        if isinstance(expression.comparisons[0].operator, cst.Is):
            rhs_expr = expression.comparisons[0].comparator

            try:
                value = self.codegen_eval(rhs_expr, local_consts, context)
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

            compiled += self.generate_expr_internal(expression.left, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context)
            if value is False:
                # Gotta invert our output since it's already a boolean.
                compiled.append_code("  INV")

            if not is_register_destination(destination):
                compiled += self.generate_move_to(destination, stack, clobbers, context)
                compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

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
                compiled += self.generate_function_call_internal(
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
                    first_dest = self.expr_temp_name()
                    equal_cleanup.append(first_dest)
                    stack.alloc(StackVar(first_dest, left_type))
                    compiled += self.generate_expr_internal(left_expr, first_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(left_expr))

                    second_dest = self.expr_temp_name()
                    equal_cleanup.append(second_dest)
                    stack.alloc(StackVar(second_dest, right_type))
                    compiled += self.generate_expr_internal(right_expr, second_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(right_expr))

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
                    first_dest = self.expr_temp_name()
                    equal_cleanup.append(first_dest)
                    stack.alloc(StackVar(first_dest, first_type))
                    compiled += self.generate_expr_internal(first_expr, first_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(first_expr))

                    # Now, allocate a spot for the second to be sign extended into.
                    second_dest = self.expr_temp_name()
                    equal_cleanup.append(second_dest)
                    stack.alloc(StackVar(second_dest, first_type))

                    # And allocate where we'll calculate it before sign-extending.
                    second_temp = self.expr_temp_name()
                    stack.alloc(StackVar(second_temp, second_type))
                    compiled += self.generate_expr_internal(second_expr, second_temp, types, stack, clobbers, allocations, refs, local_consts, context.wrap(second_expr))

                    # Now, copy it with a sign extension.
                    compiled += self.generate_variable_lookup(second_temp, second_dest, stack, types, clobbers, allocations, refs, local_consts, context.wrap(second_expr))

                    # Now, we don't need the temp location now that we've computed and sign extended.
                    stack.free(second_temp)

                # Doing the comparison itself requires the A register.
                clobbers.add("A")

                comparison_size = max(left_type.size, right_type.size)
                if comparison_size == 1:
                    compiled += self.generate_move_to(second_dest, stack, clobbers, context)
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled += self.generate_move_to(first_dest, stack, clobbers, context)

                    # XOR the two numbers, which will give us 0 if they equal.
                    compiled.append_code("  XOR" + stack.comment(stack.location, StackOperation.LOAD))

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
                    second_byte_comparison = self.local_label_name(context, "second_byte_comparison")
                    finished_comparison = self.local_label_name(context, "finished_comparison")

                    compiled += self.generate_move_to(second_dest, stack, clobbers, context, offset=actual_expr_offset(0))
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled += self.generate_move_to(first_dest, stack, clobbers, context, offset=actual_expr_offset(0))

                    # XOR the two numbers, which will give us 0 if they equal.
                    compiled.append_code("  XOR" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code(f"  JRIZ {second_byte_comparison}")

                    # We failed the comparison on the first byte, move to where we would have moved to and set our result to False.
                    compiled += self.generate_move_to(first_dest, stack.clone(), clobbers, context, offset=actual_expr_offset(1))
                    compiled.append_code(f"  LOADI {preload_value}")
                    compiled.append_code(f"  JRI {finished_comparison}")

                    # Now, do the second byte comparison.
                    compiled.append_code(f"{second_byte_comparison}:")
                    compiled += self.generate_move_to(second_dest, stack, clobbers, context, offset=actual_expr_offset(1))
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled += self.generate_move_to(first_dest, stack, clobbers, context, offset=actual_expr_offset(1))

                    # XOR the two numbers, which will give us 0 if they equal.
                    compiled.append_code("  XOR" + stack.comment(stack.location, StackOperation.LOAD))

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
                    second_byte_comparison = self.local_label_name(context, "second_byte_comparison")
                    third_byte_comparison = self.local_label_name(context, "third_byte_comparison")
                    fourth_byte_comparison = self.local_label_name(context, "fourth_byte_comparison")
                    finished_comparison = self.local_label_name(context, "finished_comparison")

                    compiled += self.generate_move_to(second_dest, stack, clobbers, context, offset=actual_expr_offset(0))
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled += self.generate_move_to(first_dest, stack, clobbers, context, offset=actual_expr_offset(0))

                    # XOR the two numbers, which will give us 0 if they equal.
                    compiled.append_code("  XOR" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code(f"  JRIZ {second_byte_comparison}")

                    # We failed the comparison on the first byte, move to where we would have moved to and set our result to False.
                    compiled += self.generate_move_to(first_dest, stack.clone(), clobbers, context, offset=actual_expr_offset(3))
                    compiled.append_code(f"  LOADI {preload_value}")
                    compiled.append_code(f"  JRI {finished_comparison}")

                    # Now, do the second byte comparison.
                    compiled.append_code(f"{second_byte_comparison}:")
                    compiled += self.generate_move_to(second_dest, stack, clobbers, context, offset=actual_expr_offset(1))
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled += self.generate_move_to(first_dest, stack, clobbers, context, offset=actual_expr_offset(1))

                    # XOR the two numbers, which will give us 0 if they equal.
                    compiled.append_code("  XOR" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code(f"  JRIZ {third_byte_comparison}")

                    # We failed the comparison on the second byte, move to where we would have moved to and set our result to False.
                    compiled += self.generate_move_to(first_dest, stack.clone(), clobbers, context, offset=actual_expr_offset(3))
                    compiled.append_code(f"  LOADI {preload_value}")
                    compiled.append_code(f"  JRI {finished_comparison}")

                    # Now, do the third byte comparison.
                    compiled.append_code(f"{third_byte_comparison}:")
                    compiled += self.generate_move_to(second_dest, stack, clobbers, context, offset=actual_expr_offset(2))
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled += self.generate_move_to(first_dest, stack, clobbers, context, offset=actual_expr_offset(2))

                    # XOR the two numbers, which will give us 0 if they equal.
                    compiled.append_code("  XOR" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code(f"  JRIZ {fourth_byte_comparison}")

                    # We failed the comparison on the third byte, move to where we would have moved to and set our result to False.
                    compiled += self.generate_move_to(first_dest, stack.clone(), clobbers, context, offset=actual_expr_offset(3))
                    compiled.append_code(f"  LOADI {preload_value}")
                    compiled.append_code(f"  JRI {finished_comparison}")

                    # Now, do the fourth byte comparison.
                    compiled.append_code(f"{fourth_byte_comparison}:")
                    compiled += self.generate_move_to(second_dest, stack, clobbers, context, offset=actual_expr_offset(3))
                    compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled += self.generate_move_to(first_dest, stack, clobbers, context, offset=actual_expr_offset(3))

                    # XOR the two numbers, which will give us 0 if they equal.
                    compiled.append_code("  XOR" + stack.comment(stack.location, StackOperation.LOAD))

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
                compiled += self.generate_move_to(destination, stack, clobbers, context)
                compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

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
                raise CompilerError("Unsupported comparison operator {expression.comparisons[0].operator}", context)

            if left_type.is_string or right_type.is_string:
                if not (left_type.is_string and right_type.is_string):
                    raise CompilerError("Unsupported comparison expression against types {left_type.type} and {right_type.type}", context)

                # In this case, don't even try to set up the stack, just let the function call handle it.
                compiled += self.generate_function_call_internal(
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
                    first_dest = self.expr_temp_name()
                    unequal_cleanup.append(first_dest)
                    stack.alloc(StackVar(first_dest, left_type))
                    compiled += self.generate_expr_internal(left_expr, first_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(left_expr))

                    second_dest = self.expr_temp_name()
                    unequal_cleanup.append(second_dest)
                    stack.alloc(StackVar(second_dest, right_type))
                    compiled += self.generate_expr_internal(right_expr, second_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(right_expr))

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
                    first_dest = self.expr_temp_name()
                    unequal_cleanup.append(first_dest)
                    stack.alloc(StackVar(first_dest, first_type))
                    compiled += self.generate_expr_internal(first_expr, first_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(first_expr))

                    # Now, allocate a spot for the second to be sign extended into.
                    second_dest = self.expr_temp_name()
                    unequal_cleanup.append(second_dest)
                    stack.alloc(StackVar(second_dest, first_type, initialized=True))

                    # And allocate where we'll calculate it before sign-extending.
                    second_temp = self.expr_temp_name()
                    stack.alloc(StackVar(second_temp, second_type))
                    compiled += self.generate_expr_internal(second_expr, second_temp, types, stack, clobbers, allocations, refs, local_consts, context.wrap(second_expr))

                    # Now, copy it with a sign extension.
                    compiled += self.generate_variable_lookup(second_temp, second_dest, stack, types, clobbers, allocations, refs, local_consts, context.wrap(second_expr))

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

                compiled += self.generate_function_call_internal(
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
                raise CompilerError("Unsupported comparison operator {op}", context)

            if not is_register_destination(destination):
                compiled += self.generate_move_to(destination, stack, clobbers, context)
                compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

        else:
            raise CompilerError(f"Unsupported comparison expression {expr_to_str(expression)}", context)

        return compiled

    def generate_ternary_expr(
        self,
        expression: cst.IfExp,
        destination: str,
        types: Dict[cst.CSTNode, CoreType],
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
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

            compiled += self.generate_expr_internal(
                test_coerced, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.virtual(test_coerced).wrap(test_coerced)
            )
        else:
            compiled += self.generate_expr_internal(expression.test, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.test))

        # Now, we need a place to jump to if the expression above is false, as well as a
        # place to jump to at the end of the true expression.
        false_expr = self.local_label_name(context, "false_expr")
        expr_end = self.local_label_name(context, "expr_end")

        # Now, compile the two expressions themselves, so that we can calculate whether
        # we can JRI or LNGJUMP to the various locations.
        left_stack = stack.clone()
        left_compiled = self.generate_expr_internal(expression.body, destination, types, left_stack, clobbers, allocations, refs, local_consts, context.wrap(expression.body))

        right_stack = stack.clone()
        right_compiled = self.generate_expr_internal(expression.orelse, destination, types, right_stack, clobbers, allocations, refs, local_consts, context.wrap(expression.orelse))

        # We could add this manually at the end of this function, but then we wouldn't be able
        # to compile the left hand side to determine length since it would have an undefined
        # jump location.
        right_compiled.append_code(f"{expr_end}:")

        if left_stack.size != right_stack.size:
            raise Exception("Logic error, stacks on both expressions not equal in size!")
        if left_stack.location != right_stack.location:
            # Arbitrarily choose the left side expression to fix up to the right.
            move_amount = right_stack.location - left_stack.location
            left_compiled += self.generate_move_by("move stack to same spot as else expression", move_amount, left_stack, clobbers, context)

        # Unify initialization tracking across cloned stacks so we can identify all paths that don't lead to variable initialization.
        stack.unify(left_stack, right_stack)

        # Now, figure out the else size so we can jump past it in the body.
        right_length = get_assembled_length(right_compiled.code, refs)
        if right_length >= 32:
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
        if left_length >= 32:
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
        self,
        expression: cst.Subscript,
        destination: Optional[str],
        types: Dict[cst.CSTNode, CoreType],
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
        refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
        local_consts: List[Constant],
        context: Context,
    ) -> Sections:
        compiled = Sections()

        if len(expression.slice) != 1:
            raise CompilerError("Unsupported slice count in subscript expression", context)
        slice_or_index = expression.slice[0].slice

        if isinstance(slice_or_index, cst.Index):
            if destination is not None:
                destination_type = stack.typeof(destination)
                if destination_type is None:
                    raise Exception("Logic error, could not calculate type of destination!")
            else:
                destination_type = CoreType("str", const=True, length=MAX_STRING_LENGTH)

            # We always end up needing the string on the left hand size, regardless of whether we're indexing or slicing into it.
            # However, if the expression is already a local variable we can save a few instructions by just moving to it directly.
            base_dest = self.expr_temp_name()
            allocated = True
            if isinstance(expression.value, cst.Name):
                varname = expression.value.value
                vartype = stack.typeof(varname)
                if vartype is not None and vartype.is_string:
                    # We can save here!
                    base_dest = varname
                    allocated = False

            if allocated:
                stack.alloc(StackVar(base_dest, CoreType("str", const=True, length=destination_type.length)))
                compiled += self.generate_expr_internal(expression.value, base_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.value))

            # Calculate the offset into the string that we're gonna need, first.
            clobbers.add("A")
            compiled += self.generate_expr_internal(slice_or_index.value, "register(A, uint8)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(slice_or_index.value))

            # We clobber the SPC to do this index lookup.
            clobbers.add("SPC")

            # Move to the correct spot on the stack to pop the pointer onto the SPC.
            compiled += self.generate_move_to(base_dest, stack, clobbers, context, offset=1)
            compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
            compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
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
                    raise CompilerError(f"Unsupported conversion from character to {destination_type.type}", context)

                if not is_register_destination(destination):
                    compiled += self.generate_move_to(destination, stack, clobbers, context)
                    compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

            if allocated:
                stack.free(base_dest)

        elif isinstance(slice_or_index, cst.Slice):
            if destination is None:
                raise CompilerError("Unsupported expression without assignment", context)

            destination_type = stack.typeof(destination)
            if destination_type is None:
                raise Exception("Logic error, could not calculate type of destination!")

            if slice_or_index.step is not None:
                # We don't support copying with a step size other than the default.
                raise CompilerError("Unsupported step for slice in subscript expression", context)

            # In the case of truncation, it's possible to avoid a strncpy and instead just insert
            # a null in the right spot. This is far faster, so it's worth detecting and doing so.
            same_destination: bool = False
            beginning = slice_or_index.lower
            ending = slice_or_index.upper
            if beginning is None and ending is not None:
                if isinstance(expression.value, cst.Name):
                    same_destination = expression.value.value == destination

            # This is a subscript in the form of var[:] which in Python land is a copy,
            # so we can do that here.
            if not stack.initof(destination):
                compiled += self.generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                stack.init(destination)

            # We copy this here, because if we don't, then the function call ends up needing to copy a ton more
            # on the stack later.
            if not same_destination and stack[-1].name != destination:
                # In order to ensure that it's possible to do stack math on this value, locate it in
                # a temporary location for the time being if the destination isn't the top of the stack.
                lhs_dest = self.expr_temp_name()
                stack.alloc(StackVar(lhs_dest, CoreType("str"), initialized=True))

                compiled += self.generate_memcpy_stackvars(lhs_dest, destination, stack, clobbers, context)
            else:
                # Safe to put first parameter in the top of the stack where it already is useful for math.
                lhs_dest = destination

            # We always end up needing the string on the left hand size, regardless of whether we're indexing or slicing into it.
            base_dest = self.expr_temp_name()
            allocated = False
            if not same_destination:
                allocated = True
                stack.alloc(StackVar(base_dest, CoreType("str", const=True, length=destination_type.length)))
                compiled += self.generate_expr_internal(expression.value, base_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression.value))

            # Figure out if this is a copy operation, or a substring operation.
            if beginning is None and ending is None:
                # Now, just strcpy it over.
                compiled += self.generate_function_call_internal(
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
                # This can be mapped onto a simple strncpy, so we should calculate the ending value and do that.
                ending_dest = self.expr_temp_name()
                stack.alloc(StackVar(ending_dest, CoreType("uint8")))
                compiled += self.generate_expr_internal(ending, ending_dest, types, stack, clobbers, allocations, refs, local_consts, context.wrap(ending))

                if same_destination:
                    if lhs_dest != destination:
                        raise Exception("Logic error, expected these to equal for optimized case to work!")

                    # Instead of just using ADDPC here to increment past the bytes we don't want, we increment one at
                    # a time. This is so we can check for an early null-terminator to make truncation memory safe.
                    clobbers.add("A")
                    clobbers.add("U")
                    clobbers.add("V")
                    clobbers.add("SPC")

                    # Get the offset value that we just calculated.
                    compiled += self.generate_move_to(ending_dest, stack, clobbers, context)
                    compiled.append_code("  LOAD V")

                    # Move to the correct spot on the stack to move the pointer to the right offset.
                    compiled += self.generate_move_to(lhs_dest, stack, clobbers, context, offset=1)

                    advance_top = self.local_label_name(context, "advance_top")
                    advance_bottom = self.local_label_name(context, "advance_bottom")

                    # Swap over so we can check the string one byte at a time.
                    compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                    compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
                    compiled.append_code("  POP SPC")
                    stack.move(-2)
                    compiled.code += comment_stack(stack)

                    # Loop through, checking for termination conditions. First check for end of loop by advancing enough.
                    # Then, check if we've hit a null byte.
                    compiled.append_code("  SWAP PC, SPC")
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

                    # Swap to it, add our destination offset and then null terminate at that location.
                    compiled.append_code("  STOREI 0")
                    compiled.append_code("  SWAP PC, SPC")

                else:
                    compiled += self.generate_function_call_internal(
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
                compiled += self.generate_expr_internal(beginning, "register(A, uint8)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(beginning))

                # Move to the correct spot on the stack to move the pointer to the right offset.
                compiled += self.generate_move_to(base_dest, stack, clobbers, context, offset=1)

                # Instead of just using ADDPC here to increment past the bytes we don't want, we increment one at
                # a time. This is so we can check for an early null-terminator to make start indexing memory safe
                # just like end indexing is.
                clobbers.add("U")
                clobbers.add("V")

                advance_top = self.local_label_name(context, "advance_top")
                advance_bottom = self.local_label_name(context, "advance_bottom")

                # Swap over so we can check the string one byte at a time.
                compiled.append_code("  MOV A, V")
                compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
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
                    compiled += self.generate_function_call_internal(
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
                        self.codegen_eval(expr, local_consts, context)

                        ending_dest = self.expr_temp_name()
                        stack.alloc(StackVar(ending_dest, CoreType("int8")))
                        compiled += self.generate_expr_internal(expr, ending_dest, types, stack, clobbers, allocations, refs, local_consts, context.virtual(expr))

                    except NonConstantExpressionException:
                        # First, store the beginning value that we calculated so that we can subtract it later.
                        ending_dest = self.expr_temp_name()
                        stack.alloc(StackVar(ending_dest, CoreType("int8"), initialized=True))
                        compiled += self.generate_move_to(ending_dest, stack, clobbers, context)
                        compiled.append_code("  NEG")
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

                        # This can be mapped onto a simple strncpy, so we should calculate the ending value and do that.
                        ending_temp = self.expr_temp_name()
                        stack.alloc(StackVar(ending_temp, CoreType("uint8")))
                        compiled += self.generate_expr_internal(ending, ending_temp, types, stack, clobbers, allocations, refs, local_consts, context.wrap(ending))
                        compiled += self.generate_move_to(ending_temp, stack, clobbers, context)
                        compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))
                        stack.free(ending_temp)

                        compiled += self.generate_move_to(ending_dest, stack, clobbers, context)
                        compiled.append_code("  ADD" + stack.comment(stack.location, StackOperation.LOAD))
                        compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

                    compiled += self.generate_function_call_internal(
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

            if allocated:
                stack.free(base_dest)
            if lhs_dest != destination:
                stack.free(lhs_dest)

        else:
            raise Exception("Logic error, unexpected node {slice_or_index} for subscript slice!")

        return compiled

    def generate_fstring_expr(
        self,
        expression: cst.FormattedString,
        destination: Optional[str],
        types: Dict[cst.CSTNode, CoreType],
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
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
            return self.generate_expr_internal(node, destination, types, stack, clobbers, allocations, refs, local_consts, virtual.virtual(node))

        if len(concatenation) == 1:
            return self.generate_expr_internal(concatenation[0], destination, types, stack, clobbers, allocations, refs, local_consts, virtual)

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

        return self.generate_expr_internal(tree, destination, types, stack, clobbers, allocations, refs, local_consts, virtual)

    def generate_expr_internal(
        self,
        expression: cst.BaseExpression,
        destination: Optional[str],
        types: Dict[cst.CSTNode, CoreType],
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
        refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
        local_consts: List[Constant],
        context: Context,
    ) -> Sections:
        compiled = Sections()

        if destination is not None:
            destination_size = stack.sizeof(destination)
            if destination_size is None:
                raise Exception("Logic error, could not calculate size of destination!")

            # Early exit if we have something in the form of "a = a". This can most often happen
            # during string evaluation when concatenating or slicing oneself.
            if isinstance(expression, cst.Name):
                if expression.value == destination:
                    return compiled
        else:
            destination_size = 0

        try:
            # If we can evaluate this directly, do so!
            value = self.codegen_eval(expression, local_consts, context)
            if isinstance(value, (bool, int)):
                if destination is not None:
                    compiled += self.generate_const_load(value, destination, stack, clobbers, context)

                    # We're gonna assign to this, so it should be considered initialized. Do this here instead of at the top
                    # so we can catch variables assigning from themselves when unassigned.
                    stack.init(destination)

                return compiled

            prefix = string_prefix(expression)
            if "b" in prefix:
                if not isinstance(value, bytes):
                    raise Exception("Logic error, expected a bytestring when given a bytes prefix!")
                value = "".join([chr(x) for x in value])

            if isinstance(value, str):
                if "r" not in prefix:
                    value = unescape_literal(value)
                if len(value) >= MAX_STRING_LENGTH:
                    raise CompilerError(f"Unsupported too-long string, strings are required to be {MAX_STRING_LENGTH} characters maximum", context)

                if destination is not None:
                    destination_type = stack.typeof(destination)
                    if destination_type is None:
                        raise Exception("Logic error, could not find type of string pointer destination!")

                    # Python treats strings and characters the same, so let's fix that here.
                    if destination_type.is_char:
                        compiled += self.generate_const_load(value, destination, stack, clobbers, context)

                        # We're gonna assign to this, so it should be considered initialized. Do this here instead of at the top
                        # so we can catch variables assigning from themselves when unassigned.
                        stack.init(destination)

                        return compiled

                    if not destination_type.is_string:
                        raise CompilerError("Unsupported string assignment to type {destination_type.type)", context)

                    if destination_type.const:
                        # First, set up somewhere to put the initialized string data so we can point at it.
                        label = self.local_label_name(context, "function_string_data")
                        compiled.append_preamble(f"{label}:")
                        for c in value:
                            compiled.append_preamble(f"  .char {c[0]!r}")
                        compiled.append_preamble("  .byte 0x00")

                        # Now, point at it.
                        clobbers.add("A")

                        compiled += self.generate_move_to(destination, stack, clobbers, context, offset=-1)
                        compiled.append_code(f"  PUSHADDR {label}")
                        stack.location += 2
                    else:
                        # Need to allocate static space for the string, then strcpy it over.
                        if not stack.initof(destination):
                            compiled += self.generate_local_storage_alloc(destination, stack, clobbers, allocations, context)

                            # This is initialized now, so we know that we won't have to allocate local storage for it anymore.
                            stack.init(destination)

                        if value:
                            static_source_storage = self.local_label_name(context, "function_string_data")
                            compiled.append_preamble(f"{static_source_storage}:")
                            for c in value:
                                compiled.append_preamble(f"  .char {c[0]!r}")
                            compiled.append_preamble("  .byte 0x00")

                            # Now, set up the stack for a strcpy operation, to initialize the local data with
                            # a copy of the constant we're initializing from.
                            if stack[-1].name != destination:
                                # In order to ensure that it's possible to do stack math on this value, locate it in
                                # a temporary location for the time being if the destination isn't the top of the stack.
                                lhs_dest = self.expr_temp_name()
                                stack.alloc(StackVar(lhs_dest, CoreType("str"), initialized=True))

                                compiled += self.generate_memcpy_stackvars(lhs_dest, destination, stack, clobbers, context)
                            else:
                                # Safe to put first parameter in the top of the stack where it already is useful for math.
                                lhs_dest = destination

                            # Now, point at it.
                            clobbers.add("A")

                            rhs_dest = self.expr_temp_name()
                            stack.alloc(StackVar(rhs_dest, CoreType("str"), initialized=True))
                            compiled += self.generate_move_to(rhs_dest, stack, clobbers, context, offset=-1)
                            compiled.append_code(f"  PUSHADDR {static_source_storage}")
                            stack.location += 2

                            # Now call strcpy.
                            compiled += self.generate_function_call_internal(
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
                        else:
                            # We can do a much faster initialization by simply setting the first byte of the string to null.
                            clobbers.add("A")
                            clobbers.add("SPC")

                            compiled += self.generate_move_to(destination, stack, clobbers, context, offset=1)
                            compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                            compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
                            compiled.append_code("  POP SPC")
                            stack.move(-2)
                            compiled.code += comment_stack(stack)

                            compiled.append_code("  SWAP PC, SPC")
                            compiled.append_code("  STOREI 0")
                            compiled.append_code("  SWAP PC, SPC")

                    # We're gonna assign to this, so it should be considered initialized. Do this here instead of at the top
                    # so we can catch variables assigning from themselves when unassigned.
                    stack.init(destination)

                return compiled

        except NonConstantExpressionException:
            # We must treat this as a non-unrolled expression.
            pass

        if isinstance(expression, cst.Name):
            # Explicitly allowing variable lookup because it could allow a register clear on read.
            compiled += self.generate_variable_lookup(expression.value, destination, stack, types, clobbers, allocations, refs, local_consts, context)

        elif isinstance(expression, cst.UnaryOperation):
            if destination is not None:
                compiled += self.generate_unary_expr(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

        elif isinstance(expression, cst.BinaryOperation):
            if destination is not None:
                compiled += self.generate_binary_expr(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

        elif isinstance(expression, cst.Call):
            function_return_type = types[expression]
            if destination is not None and function_return_type.type != "any" and function_return_type.size != destination_size:
                # We need to put this in a local temporary variable, and then copy it out.
                return_temp = self.expr_temp_name()
                stack.alloc(StackVar(return_temp, function_return_type))

                compiled += self.generate_function_call(expression, return_temp, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression))
                compiled += self.generate_variable_lookup(return_temp, destination, stack, types, clobbers, allocations, refs, local_consts, context.wrap(expression))

                stack.free(return_temp)
            else:
                # We could possibly be making a function call with no destination here, such as calling a void function.
                compiled += self.generate_function_call(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context.wrap(expression))

        elif isinstance(expression, cst.Comparison):
            if destination is not None:
                compiled += self.generate_comparison_expr(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

        elif isinstance(expression, cst.BooleanOperation):
            if destination is not None:
                compiled += self.generate_boolean_expr(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

        elif isinstance(expression, cst.IfExp):
            if destination is not None:
                compiled += self.generate_ternary_expr(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

        elif isinstance(expression, cst.Subscript):
            # Allowing subscript operation without a destination because it could allow register clear on read.
            compiled += self.generate_subscript_expr(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

        elif isinstance(expression, cst.FormattedString):
            if destination is not None:
                compiled += self.generate_fstring_expr(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

        else:
            raise CompilerError(f"Unsupported expression {expr_to_str(expression)} in expression compiler", context)

        if destination is not None:
            # We're gonna assign to this, so it should be considered initialized. Do this here instead of at the top
            # so we can catch variables assigning from themselves when unassigned.
            stack.init(destination)

        return compiled

    def infer_expr_types(
        self,
        expression: cst.BaseExpression,
        destination_type: CoreType,
        stack: Stack,
        refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
        local_consts: List[Constant],
        context: Context,
    ) -> Dict[cst.CSTNode, CoreType]:
        types = self.infer_expr_types_impl(expression, stack, refs, local_consts, context)
        self.infer_tree(types, destination_type, context)
        return types

    def infer_tree(
        self,
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
        self,
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
                value = self.codegen_eval(expression, [], context)
            except NonConstantExpressionException:
                raise Exception("Logic error, couldn't get string from SimpleString!")
            if not isinstance(value, (str, bytes)):
                raise Exception("Logic error, didn't get string back from codegen_eval!")

            length_needed = len(value) + 1

            if length_needed > MAX_STRING_LENGTH:
                raise CompilerError(f"Unsupported too-long string, strings are required to be {MAX_STRING_LENGTH} characters maximum", context)

            inferred[expression] = CoreType("string", const=True, length=length_needed)
            return inferred

        elif isinstance(expression, cst.UnaryOperation):
            inferred.update(self.infer_expr_types_impl(expression.expression, stack, refs, local_consts, context.wrap(expression.expression)))
            inferred_type = inferred[expression.expression]

            if isinstance(expression.operator, (cst.Minus, cst.BitInvert)):
                if not inferred_type.is_integer:
                    raise CompilerError(f"Unsupported unary operation for type {inferred_type.type}", context)

            if isinstance(expression.operator, cst.Not):
                inferred[expression] = CoreType("bool")
            else:
                inferred[expression] = CoreType(
                    inferred_type.type,
                    inferred_type.pointed_type,
                    const=inferred_type.const,
                    extern=inferred_type.extern,
                    return_padding=inferred_type.return_padding
                )

            return inferred

        elif isinstance(expression, cst.BinaryOperation):
            left_tree = self.infer_expr_types_impl(expression.left, stack, refs, local_consts, context.wrap(expression.left))
            right_tree = self.infer_expr_types_impl(expression.right, stack, refs, local_consts, context.wrap(expression.right))

            left_inferred = left_tree[expression.left]
            right_inferred = right_tree[expression.right]

            if isinstance(expression.operator, (cst.Add, cst.Subtract, cst.BitAnd, cst.BitOr, cst.BitXor, cst.Multiply, cst.Divide, cst.FloorDivide, cst.Modulo)):
                if isinstance(expression.operator, cst.Add):
                    if left_inferred.type == "string":
                        self.infer_tree(left_tree, CoreType("str"), context)
                    if right_inferred.type == "string":
                        self.infer_tree(right_tree, CoreType("str"), context)

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
                    raise CompilerError(f"Unsupported binary operation for types {left_inferred.type} and {right_inferred.type}", context)
                if not right_inferred.is_integer:
                    raise CompilerError(f"Unsupported binary operation for types {left_inferred.type} and {right_inferred.type}", context)

                # Any math against two integers will result in an integer. Pick the wider of two types.
                if right_inferred.type == "int":
                    if left_inferred.type != "int":
                        self.infer_tree(right_tree, left_inferred, context)

                    # Just arbitrarily pick the left, which could be an unspecified int as well.
                    picked = left_inferred

                elif left_inferred.type == "int" and right_inferred != "int":
                    # Pick the right since it is specified, the left will have to be filled in later.
                    self.infer_tree(left_tree, right_inferred, context)
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
                    self.infer_tree(right_tree, CoreType("uint8"), context)

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
            function_prototype = self.get_function_prototype(expression, [*refs, *builtin_functions()], local_consts, context)

            # Intrinsics can end up complicated since they're built-in functions that the compiler substitutes
            # a constant value for. So, check for those first and if we get a value back, don't evaluate types on the args.
            if self.intrinsic_eval(expression, local_consts, context):
                # Ignore the arg expression evaluation below. This would cause an exception when we tried to
                # ask for their types, but we know we're going to substitute a constant value at compile time.
                inferred[expression] = function_prototype.return_type
                return inferred

            args, arg_types = self.get_function_params(expression, function_prototype, context)

            # Special case for cast, since the return type is the first parameter.
            if function_prototype.name == "cast":
                requested = self.get_type(args[0].value, local_consts, allow_nopad=False, allow_extern=False, allow_array=False)

                if len(args) != 2 or len(arg_types) != 2:
                    raise Exception("Logic error, unexpected argument count for cast that should have been caught in get_function_params")

                arg = args[1]
                argtype = arg_types[1]
                arg_inferred = self.infer_expr_types_impl(arg.value, stack, refs, local_consts, context.wrap(arg.value))

                if not type_comparison_compatible(arg_inferred[arg.value], argtype.type):
                    raise CompilerError(f"Unsupported cast from {arg_inferred[arg.value].type} to {argtype.type.type} in function call parameter 2", context)

                # Special case for functions like abs(), min() and max() where the input and output are both inferred.
                if argtype.type.type != "int":
                    self.infer_tree(arg_inferred, argtype.type, context)
                inferred.update(arg_inferred)

                if requested:
                    inferred[expression] = requested
                else:
                    inferred[expression] = function_prototype.return_type

                return inferred
            else:
                for i, (arg, argtype) in enumerate(zip(args, arg_types)):
                    arg_inferred = self.infer_expr_types_impl(arg.value, stack, refs, local_consts, context.wrap(arg.value))

                    if not type_comparison_compatible(arg_inferred[arg.value], argtype.type):
                        raise CompilerError(f"Unsupported cast from {arg_inferred[arg.value].type} to {argtype.type.type} in function call parameter {i + 1}", context)

                    # Special case for functions like abs(), min() and max() where the input and output are both inferred.
                    if argtype.type.type != "int":
                        self.infer_tree(arg_inferred, argtype.type, context)
                    inferred.update(arg_inferred)

                inferred[expression] = function_prototype.return_type
                return inferred

        elif isinstance(expression, cst.Comparison):
            left_tree = self.infer_expr_types_impl(expression.left, stack, refs, local_consts, context.wrap(expression.left))
            for comparison in expression.comparisons:
                right_tree = self.infer_expr_types_impl(comparison.comparator, stack, refs, local_consts, context.wrap(comparison.comparator))

                if not type_comparison_compatible(left_tree[expression.left], right_tree[comparison.comparator]):
                    raise CompilerError(f"Unsupported comparison of types {left_tree[expression.left].type} and {right_tree[comparison.comparator].type}", context)

                # Infer constant widths based on comparison types.
                if left_tree[expression.left].type == "int" and right_tree[comparison.comparator].type != "int":
                    self.infer_tree(left_tree, right_tree[comparison.comparator], context)
                if left_tree[expression.left].type != "int" and right_tree[comparison.comparator].type == "int":
                    self.infer_tree(right_tree, left_tree[expression.left], context)
                if left_tree[expression.left].type == "string" and right_tree[comparison.comparator].type != "string":
                    self.infer_tree(left_tree, right_tree[comparison.comparator], context)
                if left_tree[expression.left].type != "string" and right_tree[comparison.comparator].type == "string":
                    self.infer_tree(right_tree, left_tree[expression.left], context)

                # Verify that we're comparing two equivalent types.
                if left_tree[expression.left].is_unsigned != right_tree[comparison.comparator].is_unsigned:
                    raise CompilerError(f"Unsupported comparison of types {left_tree[expression.left].type} and {right_tree[comparison.comparator].type}", context)

                inferred.update(right_tree)

            inferred[expression] = CoreType("bool")
            inferred.update(left_tree)
            return inferred

        elif isinstance(expression, cst.BooleanOperation):
            inferred.update(self.infer_expr_types_impl(expression.left, stack, refs, local_consts, context.wrap(expression.left)))
            inferred.update(self.infer_expr_types_impl(expression.right, stack, refs, local_consts, context.wrap(expression.right)))

            left_inferred = inferred[expression.left]
            right_inferred = inferred[expression.right]

            inferred[expression] = CoreType("bool")
            return inferred

        elif isinstance(expression, cst.IfExp):
            body_tree = self.infer_expr_types_impl(expression.body, stack, refs, local_consts, context.wrap(expression.body))
            orelse_tree = self.infer_expr_types_impl(expression.orelse, stack, refs, local_consts, context.wrap(expression.orelse))
            inferred.update(self.infer_expr_types_impl(expression.test, stack, refs, local_consts, context.wrap(expression.test)))
            inferred.update(body_tree)
            inferred.update(orelse_tree)

            body_inferred = body_tree[expression.body]
            orelse_inferred = orelse_tree[expression.orelse]
            if not type_comparison_compatible(body_inferred, orelse_inferred):
                raise CompilerError(f"Unsupported mixed types {body_inferred.type} and {orelse_inferred.type} in if expression", context)

            # Infer constants and pick the widest of the two sides for this expression's type.
            if orelse_inferred.type == "int":
                if body_inferred.type != "int":
                    self.infer_tree(orelse_tree, body_inferred, context)

                # Just arbitrarily pick the left, which could be an unspecified int as well.
                picked = body_inferred

            elif body_inferred.type == "int" and orelse_inferred != "int":
                # Pick the right since it is specified, the left will have to be filled in later.
                self.infer_tree(body_tree, orelse_inferred, context)
                picked = orelse_inferred

            elif orelse_inferred.type == "string":
                if body_inferred.type != "string":
                    self.infer_tree(orelse_tree, body_inferred, context)

                # Just arbitrarily pick the left, which could be an unspecified int as well.
                picked = body_inferred

            elif body_inferred.type == "string" and orelse_inferred != "string":
                # Pick the right since it is specified, the left will have to be filled in later.
                self.infer_tree(body_tree, orelse_inferred, context)
                picked = orelse_inferred

            elif body_inferred.size > orelse_inferred.size:
                # Pick the left because it's wider than the right.
                picked = body_inferred

            else:
                # Pick the right because its either wider than the left, or equivalent in width.
                picked = orelse_inferred

            if body_inferred.is_unsigned != orelse_inferred.is_unsigned:
                raise CompilerError(f"Unsupported mixed types {body_inferred.type} and {orelse_inferred.type} in if expression", context)

            inferred[expression] = CoreType(picked.type, picked.pointed_type, const=picked.const, extern=picked.extern, return_padding=picked.return_padding)
            return inferred

        elif isinstance(expression, cst.Subscript):
            array_tree = self.infer_expr_types_impl(expression.value, stack, refs, local_consts, context.wrap(expression.value))
            array_inferred = array_tree[expression.value]
            if array_inferred.type == "string":
                self.infer_tree(array_tree, CoreType("str"), context)
            if not array_inferred.is_string:
                raise CompilerError(f"Unsupported non-string type {array_inferred.type} in subscript expression", context)

            if len(expression.slice) != 1:
                raise CompilerError("Unsupported slice count in subscript expression", context)
            slice_or_index = expression.slice[0].slice

            if isinstance(slice_or_index, cst.Index):
                index_tree = self.infer_expr_types_impl(slice_or_index.value, stack, refs, local_consts, context.wrap(slice_or_index.value))
                index_type = index_tree[slice_or_index.value]

                if index_type.type == "int":
                    self.infer_tree(index_tree, CoreType("uint8"), context)
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

                    slice_tree = self.infer_expr_types_impl(node, stack, refs, local_consts, context.wrap(node))
                    slice_type = slice_tree[node]

                    if slice_type.type == "int":
                        self.infer_tree(slice_tree, CoreType("uint8", const=True), context)
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
                    expr_tree = self.infer_expr_types_impl(part.expression, stack, refs, local_consts, context.wrap(part.expression))
                    expr_type = expr_tree[part.expression]

                    if expr_type.type in {"int", "string"}:
                        self.infer_tree(expr_tree, CoreType("any"), context)

                    inferred.update(expr_tree)
                else:
                    raise Exception("Logic error, unexpected node in f-string!")

            inferred[expression] = CoreType("str", const=True)
            return inferred

        elif isinstance(expression, cst.Attribute):
            # This could be a sys reference.
            try:
                possible_val = self.codegen_eval(expression, local_consts, context)
            except NonConstantExpressionException:
                possible_val = None

            if isinstance(possible_val, str):
                inferred[expression] = CoreType("str", const=True)
            elif isinstance(possible_val, int):
                inferred[expression] = CoreType("int", const=True)
            else:
                raise CompilerError(f"Unsupported expression {expr_to_str(expression)}", context)
            return inferred

        else:
            raise CompilerError(f"Unsupported expression {expr_to_str(expression)}", context)

    def generate_expr(
        self,
        expression: cst.BaseExpression,
        destination: Optional[str],
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
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
            dtype = CoreType("void")

        types: Dict[cst.CSTNode, CoreType] = self.infer_expr_types(expression, dtype, stack, refs, local_consts, context)

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

            compiled += self.generate_expr_internal(expression, dest, types, stack, clobbers, allocations, refs, local_consts, context)
            compiled += self.generate_move_to(destination, stack, clobbers, context)
            compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))
        else:
            # Just do stack-based operations.
            compiled += self.generate_expr_internal(expression, destination, types, stack, clobbers, allocations, refs, local_consts, context)

        if destination is not None:
            # We're gonna assign to this, so it should be considered initialized. Do this here instead of at the top
            # so we can catch variables assigning from themselves when unassigned.
            stack.init(destination)

        # Mark all builtin string temporaries as unused.
        for alloc in allocations.values():
            if alloc.var.startswith("builtin(expr_temp_"):
                alloc.used = False

        return compiled

    def global_variable_assign(
        self,
        assign_target: GlobalVariable,
        assign_value: cst.BaseExpression,
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
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

            expr_temp = self.expr_temp_name()
            stack.alloc(StackVar(expr_temp, assign_target.type, initialized=True))

            compiled += self.generate_move_to(expr_temp, stack, clobbers, context, offset=-1)
            compiled.append_code(f"  PUSHADDR {assign_target.name}")
            stack.location += 2

            compiled += self.generate_expr(assign_value, expr_temp, stack, clobbers, allocations, refs, local_consts, context.wrap(assign_value))
            stack.free(expr_temp)

        else:
            # To grab a global variable offset, we need to use the SPC. To copy we need A.
            clobbers.add("SPC")
            clobbers.add("A")

            expr_temp = self.expr_temp_name()
            stack.alloc(StackVar(expr_temp, assign_target.type))

            compiled += self.generate_expr(assign_value, expr_temp, stack, clobbers, allocations, refs, local_consts, context.wrap(assign_value))

            for i in range(assign_target.type.size):
                # First, we need to set the SPC to our variable pointer, which clobbers A.
                if i == 0:
                    compiled.append_code("  SWAP PC, SPC")
                    compiled.append_code(f"  SETPC {assign_target.name}, {assign_target.type.size - 1}")
                    compiled.append_code("  SWAP PC, SPC")

                compiled += self.generate_move_to(expr_temp, stack, clobbers, context, offset=i)
                compiled.append_code("  LOAD A" + stack.comment(stack.location, StackOperation.LOAD))

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
        self,
        assign_target: cst.BaseExpression,
        assign_annotation: Optional[cst.Annotation],
        assign_value: Optional[cst.BaseExpression],
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
        refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
        local_consts: List[Constant],
        context: Context,
    ) -> Sections:
        compiled = Sections(code=[context.comment()])

        assign_type = self.get_type(assign_annotation.annotation, local_consts, allow_array=True) if assign_annotation is not None else None

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

            assign_types: Dict[cst.CSTNode, CoreType] = self.infer_expr_types(assign_value, CoreType("char"), stack, refs, local_consts, context)
            if not assign_types[assign_value].is_char:
                raise CompilerError(f"Unsupported non-character assignment {assign_types[assign_value].type} in subscript assignment", context)

            offset_types: Dict[cst.CSTNode, CoreType] = self.infer_expr_types(assign_offset, CoreType("uint8"), stack, refs, local_consts, context)
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

                compiled += self.generate_move_to(assign_name, stack, clobbers, context, offset=1)
                compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
                compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
                compiled.append_code("  POP SPC")
                stack.move(-2)
                compiled.code += comment_stack(stack)

            # Now, calculate the offset we need to assign at.
            compiled += self.generate_expr_internal(assign_offset, "register(A, uint8)", offset_types, stack, clobbers, allocations, refs, local_consts, context.wrap(assign_offset))

            compiled.append_code("  SWAP PC, SPC")
            compiled.append_code("  ADDPC")
            compiled.append_code("  SWAP PC, SPC")

            # Now, calculate the character that we're assigning.
            compiled += self.generate_expr_internal(assign_value, "register(A, char)", assign_types, stack, clobbers, allocations, refs, local_consts, context.wrap(assign_value))

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

                compiled += self.global_variable_assign(global_var, assign_value, stack, clobbers, allocations, refs, local_consts, context)
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

                        value = self.codegen_eval(assign_value, local_consts, context)
                        local_consts.append(Constant(assign_name, assign_type, value))
                        return compiled
                    except NonConstantExpressionException:
                        pass

                reassigned = False
                if needs_alloc:
                    # Allocate space on the stack for this local variable.
                    if assign_type is None:
                        raise Exception("Logic error, we should always have a type in this condition!")

                    # We might need to treat this as a non-constant if it's a string that has a
                    # non-constant expression on the right hand side but it's assigning to a constant.
                    # If we don't, we won't end up assigning local storage for this variable and then
                    # we will end up trying to concatenate against the constant in ROM.
                    if assign_type.is_string and assign_type.const:
                        if self.is_safe_ref(assign_value, stack, refs, local_consts, context):
                            # This constant was initialized from a true constant (const string, global variable, another constant)
                            # so we can safely do a copy and mark it as also a safe ref.
                            assign_type.safe_ref = True
                            stack.alloc(StackVar(assign_name, assign_type))
                        else:
                            stack.alloc(StackVar(assign_name, assign_type.nonconst_clone()))
                            reassigned = True

                    else:
                        stack.alloc(StackVar(assign_name, assign_type))

                # For strings, ensure that the destination does not appear in the expression. If it does, we will need
                # to generate temporary storage to manpulate since we manipulate strings by mutating the destination pointer.
                stack_assign_type = stack.typeof(assign_name)
                if stack_assign_type is None:
                    raise Exception("Logic error, can't get type of variable we just defined!")

                if stack_assign_type.is_string and assignment_needs_temporary(assign_name, assign_value):
                    # This can only happen in assignment operations that have already allocated the destination, otherwise we'd
                    # be assigning to a variable that was not initialized.
                    if not stack.initof(assign_name):
                        raise CompilerError(f"Use of uninitialized variable {assign_name!r}", context)

                    # First, create a temporary string with the same length as the destination.
                    temp_assign_name = self.expr_temp_name()
                    stack.alloc(StackVar(temp_assign_name, CoreType("str", length=stack_assign_type.length), initialized=True))

                    compiled += self.generate_local_storage_alloc(temp_assign_name, stack, clobbers, allocations, context)

                    # Now, render the expression into that temporary string.
                    compiled += self.generate_expr(
                        assign_value,
                        temp_assign_name,
                        stack,
                        clobbers,
                        allocations,
                        refs,
                        local_consts,
                        context.wrap(assign_value),
                    )

                    # Now call strcpy to copy the temporary string back to the destination.
                    compiled += self.generate_function_call_internal(
                        create_call("strcpy", [UnvalidatedName(assign_name), UnvalidatedName(temp_assign_name)]),
                        None,
                        {},
                        stack,
                        clobbers,
                        allocations,
                        refs,
                        local_consts,
                        context,
                    )

                    # Finally, free the stack.
                    stack.free(temp_assign_name)
                else:
                    compiled += self.generate_expr(
                        assign_value,
                        assign_name,
                        stack,
                        clobbers,
                        allocations,
                        refs,
                        local_consts,
                        context.wrap(assign_value),
                    )

                if assign_type is not None and reassigned:
                    # Might need to retype back to the assign type if we temporarily marked a string
                    # as non-const.
                    stack.retype(assign_name, assign_type)

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
        self,
        assign_target: cst.BaseExpression,
        assign_op: cst.BaseAugOp,
        assign_value: cst.BaseExpression,
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
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
        return self.generate_assign_expr(
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
        self,
        statement: cst.If,
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
        function_type: CoreType,
        refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
        loop: Optional[LoopInfo],
        local_consts: List[Constant],
        context: Context,
    ) -> Tuple[Sections, bool, bool]:
        compiled = Sections()

        # First, we need to infer the expression type, so we can figure out if we need to implicitly coerce the value.
        types: Dict[cst.CSTNode, CoreType] = self.infer_expr_types(statement.test, CoreType("bool"), stack, refs, local_consts, context)

        if not types[statement.test].is_bool:
            test_coerced = create_call("bool", [statement.test])
            types[test_coerced] = CoreType("bool")

            compiled += self.generate_expr_internal(
                test_coerced, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.virtual(test_coerced).wrap(test_coerced)
            )
        else:
            compiled += self.generate_expr_internal(statement.test, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(statement.test))

        # Now, depending on if this if statement has an else body or not,
        if statement.orelse is None:
            # Simpler logic, no need to generate two labels for skipping between each, no worrying about unifying the stack.
            if_body_stack = stack.clone()
            child_compiled, _, _ = self.compile_chunk(
                statement.body, if_body_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=False,
            )

            # Not unifying the stack here because in the false case we skip the body and don't initialize.
            if stack.location != if_body_stack.location:
                # Arbitrarily choose the left side expression to fix up to the right.
                move_amount = stack.location - if_body_stack.location
                child_compiled += self.generate_move_by("move if body stack to original location", move_amount, if_body_stack, clobbers, context)

                if stack.location != if_body_stack.location:
                    raise Exception("Logic error, stacks differ after fixup!")

            # Now, figure out how far we need to jump on false.
            child_length = get_assembled_length(child_compiled.code, refs, loop.labels if loop else [])
            false_case = self.local_label_name(context, "false_case")
            if child_length >= 32:
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
            if_body_compiled, if_body_returned, if_body_continued = self.compile_chunk(
                statement.body, if_body_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=False,
            )

            else_body_stack = stack.clone()
            else_body_compiled, else_body_returned, else_body_continued = self.compile_chunk(
                statement.orelse.body, else_body_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=False,
            )

            false_case = self.local_label_name(context, "false_case")

            # Only need somewhere to jump to if we don't return as our last instruction in the if body.
            if not if_body_returned:
                if_end = self.local_label_name(context, "if_end")
                else_body_compiled.append_code(f"{if_end}:")

            # Unify initialization tracking across cloned stacks so we can identify all paths that don't lead to variable initialization.
            stack.unify(if_body_stack, else_body_stack)

            # Not asserting that both sides are the same size, because they could have defined local variables. We don't follow python's
            # scope rules for defining variables in sub-scopes propagating upwards. Instead we follow C scope style which makes it easier
            # to compile.
            if if_body_stack.location != else_body_stack.location:
                # Arbitrarily choose the if side to fix up to the else.
                move_amount = else_body_stack.location - if_body_stack.location
                if_body_compiled += self.generate_move_by("move if body stack to same spot as else body", move_amount, if_body_stack, clobbers, context)

            # Now, figure out the else size so we can jump past it in the body.
            else_length = get_assembled_length(else_body_compiled.code, refs, loop.labels if loop else [])
            if not if_body_returned:
                if else_length >= 32:
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
            if if_length >= 32:
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
            if_body_compiled, if_body_returned, if_body_continued = self.compile_chunk(
                statement.body, if_body_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=False,
            )

            else_body_compiled, else_body_returned, else_body_continued = self.generate_if_statement(
                statement.orelse, stack, clobbers, allocations, function_type, refs, loop, local_consts, context
            )

            false_case = self.local_label_name(context, "false_case")

            # Only need somewhere to jump to if we don't return as our last instruction in the if body.
            if not if_body_returned:
                if_end = self.local_label_name(context, "if_end")
                else_body_compiled.append_code(f"{if_end}:")

            # Not asserting that both sides are the same size, because they could have defined local variables. We don't follow python's
            # scope rules for defining variables in sub-scopes propagating upwards. Instead we follow C scope style which makes it easier
            # to compile.
            if if_body_stack.location != stack.location:
                # Arbitrarily choose the if side to fix up to the else.
                move_amount = stack.location - if_body_stack.location
                if_body_compiled += self.generate_move_by("move if body stack to same spot as else body", move_amount, if_body_stack, clobbers, context)

            # Clone the else body stack just to see if any of it got unified or not.
            else_body_stack = stack.clone()
            stack.unwind(stack_before)

            # Unify initialization tracking across cloned stacks so we can identify all paths that don't lead to variable initialization.
            # It's safe to do here unlike in the if with no else case, because the else body is going to do its own unification checks.
            stack.unify(if_body_stack, else_body_stack)

            # Now, figure out the else size so we can jump past it in the body.
            else_length = get_assembled_length(else_body_compiled.code, refs, loop.labels if loop else [])
            if not if_body_returned:
                if else_length >= 32:
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
            if if_length >= 32:
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
        self,
        statement: cst.While,
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
        function_type: CoreType,
        refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
        parent_loop: Optional[LoopInfo],
        local_consts: List[Constant],
        context: Context,
    ) -> Tuple[Sections, bool, bool]:
        compiled = Sections()

        # First, we need to infer the expression type, so we can figure out if we need to implicitly coerce the value.
        types: Dict[cst.CSTNode, CoreType] = self.infer_expr_types(statement.test, CoreType("bool"), stack, refs, local_consts, context)

        # Now, figure out our loop control points so that break/continue can be handled inside the nested compiled_chunk,
        # and so that we can support else statements in while loops.
        test_label = self.local_label_name(context, "loop_test")
        else_label = self.local_label_name(context, "loop_else") if statement.orelse else None
        exit_label = self.local_label_name(context, "loop_exit")
        loop = LoopInfo(stack.location, iter_label=test_label, else_label=else_label, exit_label=exit_label)

        # We're at the point we want to loop back to, so label it now, and generate the test itself.
        compiled.append_code(f"{test_label}:")

        if not types[statement.test].is_bool:
            test_coerced = create_call("bool", [statement.test])
            types[test_coerced] = CoreType("bool")

            compiled += self.generate_expr_internal(
                test_coerced, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.virtual(test_coerced).wrap(test_coerced)
            )
        else:
            compiled += self.generate_expr_internal(statement.test, "register(A, bool)", types, stack, clobbers, allocations, refs, local_consts, context.wrap(statement.test))

        # Now, generate the code necessary to perform the loop, as well as optionally the else.
        if statement.orelse is None:
            loop_stack = stack.clone()
            loop_compiled, _, _ = self.compile_chunk(
                statement.body, loop_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=True,
            )

            # Now, figure out how far we need to jump on loop condition is false.
            child_length = get_assembled_length(loop_compiled.code, refs, loop.labels)
            if child_length >= 32:
                insn = "LNGJUMPNZ"
            else:
                insn = "JRINZ"

            # Now, generate the code that actually performs the conditional loop statement.
            compiled.append_code("  INV")

            if loop.stack_location != stack.location:
                # If we're exiting, we have to put ourselves back to the right spot on the stack because
                # that's the spot we promised to be in when we exit the loop through a break.
                move_amount = loop.stack_location - stack.location
                compiled += self.generate_move_by("move stack to same spot as beginning of loop check", move_amount, stack, clobbers, context, prefix="  SKIPIF ZF")

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
            loop_compiled, _, _ = self.compile_chunk(
                statement.body, loop_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=True,
            )

            else_stack = stack.clone()
            else_compiled, _, _ = self.compile_chunk(
                statement.orelse.body, else_stack, clobbers, allocations, function_type, refs, parent_loop, local_consts, context, require_return=False, require_continue=False,
            )

            # We always jump to the else from the while conditional, so we don't need to move to our expected position until the end of the else.
            # Everyone jumping from within the loop will either jump to the conditional or straight to the exit, skipping the else case.
            if loop.stack_location != else_stack.location:
                move_amount = loop.stack_location - else_stack.location
                else_compiled += self.generate_move_by("move stack to same spot as beginning of loop check", move_amount, else_stack, clobbers, context)

            # Now, figure out how far we need to jump on loop condition is false.
            child_length = get_assembled_length(loop_compiled.code, refs, loop.labels)
            if child_length >= 32:
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

    def generate_for_statement(
        self,
        statement: cst.For,
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
        function_type: CoreType,
        refs: Sequence[Union[FunctionPrototype, GlobalVariable]],
        parent_loop: Optional[LoopInfo],
        local_consts: List[Constant],
        context: Context,
    ) -> Tuple[Sections, bool, bool]:
        compiled = Sections()
        free_list: List[str] = []

        # Before anything, we need to be sure we know the type of the iterator variable.
        if not isinstance(statement.target, cst.Name):
            raise CompilerError("Unsupported for statement iteration variable", context)

        iterator_dest = statement.target.value
        iterator_type = stack.typeof(iterator_dest)
        if iterator_type is None:
            raise CompilerError(f"Undefined variable reference to {iterator_dest!r}", context)

        # First, figure out if the iter is actually a string. If so, we'll iterate over that.
        itertypes = self.infer_expr_types_impl(statement.iter, stack, refs, local_consts, context)
        if itertypes[statement.iter].type in {"str", "string"}:
            if not iterator_type.is_char:
                raise CompilerError(f"Unsupported destination type {iterator_type} in for statement iteration variable", context)

            # Figure out if the string we have is already ready.
            allocated = False
            if isinstance(statement.iter, cst.Name):
                iter_name = statement.iter.value
                iter_type = stack.typeof(iter_name)
                if iter_type is not None and iter_type.is_string:
                    str_dest = self.expr_temp_name()
                    free_list.append(str_dest)
                    stack.alloc(StackVar(str_dest, CoreType("str"), initialized=True))
                    compiled += self.generate_memcpy_stackvars(str_dest, iter_name, stack, clobbers, context)
                    allocated = True

            if not allocated:
                # We need to generate a temporary string that can be used for the expression evaluation.
                str_dest = self.expr_temp_name()
                free_list.append(str_dest)
                stack.alloc(StackVar(str_dest, CoreType("str", length=MAX_STRING_LENGTH), initialized=True))

                compiled += self.generate_local_storage_alloc(str_dest, stack, clobbers, allocations, context)
                compiled += self.generate_expr_internal(
                    statement.iter,
                    str_dest,
                    itertypes,
                    stack,
                    clobbers,
                    allocations,
                    refs,
                    local_consts,
                    context.wrap(statement.iter),
                )

            # Now, figure out our loop control points so that break/continue can be handled inside the nested compiled_chunk,
            # and so that we can support else statements in for loops.
            test_label = self.local_label_name(context, "loop_test")
            increment_label = self.local_label_name(context, "loop_increment")
            else_label = self.local_label_name(context, "loop_else") if statement.orelse else None
            exit_label = self.local_label_name(context, "loop_exit")
            loop = LoopInfo(stack.location, iter_label=increment_label, else_label=else_label, exit_label=exit_label)

            # Need somewhere to put our test which is also our increment, and need empty space for the unused increment spot.
            increment_compiled = Sections()
            test_compiled = Sections()

            # We're gonna use the SPC for looping, as well as the A register for grabbing the value.
            clobbers.add("SPC")
            clobbers.add("A")

            # First, move to the string variable.
            test_compiled += self.generate_move_to(str_dest, stack, clobbers, context, offset=1)
            test_compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.LOAD))
            test_compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.LOAD))
            test_compiled.append_code("  POP SPC")

            # Now, grab the value at that location, and increment the pointer.
            test_compiled.append_code("  SWAP PC, SPC")
            test_compiled.append_code("  LOAD A")
            test_compiled.append_code("  INCPC")
            test_compiled.append_code("  SWAP PC, SPC")

            # Now, save the new SPC into our temporary string since we advanced past that character.
            test_compiled.append_code("  NOP" + stack.comment(stack.location, StackOperation.STORE))
            test_compiled.append_code("  NOP" + stack.comment(stack.location - 1, StackOperation.STORE))
            test_compiled.append_code("  PUSH SPC")

            # Now, move to the location of our loop variable and store the value we looked up.
            test_compiled += self.generate_move_to(iterator_dest, stack, clobbers, context)
            stack.init(iterator_dest)
            test_compiled.append_code("  STORE A" + stack.comment(stack.location, StackOperation.STORE))

            # Finally, prime the boolean test with whether the character was a null.
            test_compiled.append_code("  ADDI 0")
            test_compiled.append_code("  LOADI 0xFF")
            test_compiled.append_code("  SKIPIF !ZF")
            test_compiled.append_code("  INV")

        else:
            # We need to figure out if this is a for x in range() statement, which is the only other type of iterator we support.
            range_params = get_range_params(statement.iter)
            if range_params is None:
                raise CompilerError("Unsupported for statement iterator", context)

            # Make sure that any fabricated nodes we created in the range params helper are recognized.
            context = context.virtual(range_params[0]).virtual(range_params[1]).virtual(range_params[2])

            # First we want to generate the iterator initialization.
            compiled += self.generate_assign_expr(
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
            test_label = self.local_label_name(context, "loop_test")
            increment_label = self.local_label_name(context, "loop_increment")
            else_label = self.local_label_name(context, "loop_else") if statement.orelse else None
            exit_label = self.local_label_name(context, "loop_exit")
            loop = LoopInfo(stack.location, iter_label=increment_label, else_label=else_label, exit_label=exit_label)

            # Since everything will be jumping back to the increment label, we need to make sure that it is generated from the
            # perspective of the stack at this point.
            increment = cst.BinaryOperation(left=statement.target, operator=cst.Add(), right=range_params[2])
            types = self.infer_expr_types(increment, iterator_type, stack, refs, local_consts, context)

            increment_stack = stack.clone()
            increment_compiled = self.generate_expr_internal(
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
                increment_compiled += self.generate_move_by("move stack to same spot as beginning of loop check", move_amount, increment_stack, clobbers, context)

            # We're at the point we want to loop back to, so generate the test itself.
            comparison = cst.Comparison(left=statement.target, comparisons=[cst.ComparisonTarget(cst.LessThan(), range_params[1])])
            types = self.infer_expr_types(comparison, CoreType("bool"), stack, refs, local_consts, context)

            test_compiled = self.generate_expr_internal(
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
            loop_compiled, _, _ = self.compile_chunk(
                statement.body, loop_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=True,
            )

            # Now, figure out how far we need to jump on loop condition is false.
            child_length = get_assembled_length(loop_compiled.code, refs, loop.labels) + get_assembled_length(increment_compiled.code, refs, loop.labels)
            if child_length >= 32:
                conditionalinsn = "LNGJUMPNZ"
            else:
                conditionalinsn = "JRINZ"

            # Now, generate the code that actually performs the conditional loop statement.
            test_compiled.append_code("  INV")

            if loop.stack_location != stack.location:
                # If we're exiting, we have to put ourselves back to the right spot on the stack because
                # that's the spot we promised to be in when we exit the loop through a break.
                move_amount = loop.stack_location - stack.location
                test_compiled += self.generate_move_by("move stack to same spot as beginning of loop check", move_amount, stack, clobbers, context, prefix="  SKIPIF ZF")

            test_compiled.append_code(f"  {conditionalinsn} {exit_label}")

            # Also figure out how far we have to jump for the increment back to loop case.
            increment_length = get_assembled_length(test_compiled.code, refs, loop.labels) + child_length
            if increment_length >= 32:
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

        else:
            # Generate both the loop stack and the else stack from the same stack location, because we jump to the else stack from the
            # same spot at the end of the test where we would fall into the loop stack.
            loop_stack = stack.clone()
            loop_compiled, _, _ = self.compile_chunk(
                statement.body, loop_stack, clobbers, allocations, function_type, refs, loop, local_consts, context, require_return=False, require_continue=True,
            )

            else_stack = stack.clone()
            else_compiled, _, _ = self.compile_chunk(
                statement.orelse.body, else_stack, clobbers, allocations, function_type, refs, parent_loop, local_consts, context, require_return=False, require_continue=False,
            )

            # We always jump to the else from the loop conditional, so we don't need to move to our expected position until the end of the else.
            # Everyone jumping from within the loop will either jump to the increment code or straight to the exit, skipping the else case.
            if loop.stack_location != else_stack.location:
                move_amount = loop.stack_location - else_stack.location
                else_compiled += self.generate_move_by("move stack to same spot as beginning of loop check", move_amount, else_stack, clobbers, context)

            # Now, figure out how far we need to jump on loop condition is false.
            child_length = get_assembled_length(loop_compiled.code, refs, loop.labels) + get_assembled_length(increment_compiled.code, refs, loop.labels)
            if child_length >= 32:
                conditionalinsn = "LNGJUMPNZ"
            else:
                conditionalinsn = "JRINZ"

            # Now, generate the code that actually performs the conditional loop statement.
            test_compiled.append_code("  INV")
            test_compiled.append_code(f"  {conditionalinsn} {else_label}")

            # Also figure out how far we have to jump for the increment back to loop case.
            increment_length = get_assembled_length(test_compiled.code, refs, loop.labels) + child_length
            if increment_length >= 32:
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

        for free in reversed(free_list):
            stack.free(free)

        # The last statement isn't always a return, because even if the loop returned,
        # we could still skip that for the false loop control case.
        return compiled, False, False

    def generate_continue(
        self,
        stack: Stack,
        clobbers: Set[str],
        loop: Optional[LoopInfo],
        context: Context,
    ) -> Sections:
        compiled = Sections()

        if loop is None:
            raise CompilerError("Attempting to continue outside of active loop", context)

        move_amount = loop.stack_location - stack.location
        compiled += self.generate_move_by("move stack to same spot as beginning of loop check", move_amount, stack, clobbers, context)
        compiled.append_code(f"  LNGJUMP {loop.iter_label}")
        return compiled

    def generate_break(
        self,
        stack: Stack,
        clobbers: Set[str],
        loop: Optional[LoopInfo],
        context: Context,
    ) -> Sections:
        compiled = Sections()

        if loop is None:
            raise CompilerError("Attempting to break outside of active loop", context)

        move_amount = loop.stack_location - stack.location
        compiled += self.generate_move_by("move stack to same spot as beginning of loop check", move_amount, stack, clobbers, context)
        compiled.append_code(f"  LNGJUMP {loop.exit_label}")
        return compiled

    def compile_chunk(
        self,
        chunk: cst.BaseSuite,
        stack: Stack,
        clobbers: Set[str],
        allocations: Dict[str, Allocation],
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

        for statement_no, statement in enumerate(chunk.body):
            if isinstance(statement, cst.SimpleStatementLine):
                for substatement_no, simple_statement in enumerate(statement.body):
                    if isinstance(simple_statement, cst.Return):
                        if simple_statement.value is None:
                            # Simple return by itself, doesn't update the retval.
                            if not function_type.is_void:
                                raise CompilerError("Returning nothing from a function marked with a return value", context)
                            compiled += self.generate_return(function_type, stack, clobbers, context.wrap(simple_statement))
                        else:
                            # Return of some sort of expression.
                            if function_type.is_void:
                                raise CompilerError("Returning something from a function marked with no return value", context)

                            # Since we're performing one last expression before returning, we know that any
                            # parameters we'd be overwriting can be overwritten safely. So, figure out if
                            # we can relocate the retval.
                            if self.can_relocate_return(function_type, stack, clobbers, context):
                                stack.relocate("builtin(retval)", 0)

                            # If they're returning a constant from a function marked as non-constant, we end up wanting a
                            # string length for things that provably do not need one, such as returning a string literal.
                            # Fix up the definition here so that we can avoid a strcpy as well as avoid requiring a length.
                            original_type = stack.typeof("builtin(retval)")
                            if original_type is None:
                                raise Exception("Logic error, can't determine type of return value!")

                            free_list: List[str] = []
                            return_dest = "builtin(retval)"
                            if function_type.is_string and not function_type.const:
                                if self.is_safe_return(simple_statement.value, stack, refs_copy, local_consts, context.wrap(simple_statement.value)):
                                    # Help out with optmiizations by skipping out on a strcpy.
                                    stack.retype("builtin(retval)", original_type.const_clone())
                                else:
                                    # Ensure that downstream code doesn't try to accidentally strcat to a const.
                                    compiled += self.generate_local_storage_alloc("builtin(retval)", stack, clobbers, allocations, context)
                                    stack.init("builtin(retval)")

                                    return_dest = self.expr_temp_name()
                                    stack.alloc(StackVar(return_dest, original_type, initialized=True))
                                    free_list.append(return_dest)

                                    compiled += self.generate_memcpy_stackvars(return_dest, "builtin(retval)", stack, clobbers, context)

                            # Functions that return const[str] are only allowed to do so if they return a safe ref. That
                            # means a string literal, a global constant string, a local constant string that is also a
                            # safe ref, or another function that returns a const[str]. Since functions are only allowed to
                            # return a const[str] if the value being returned is a safe ref, we can assume another function
                            # marked as returning const[str] is safe in itself.
                            if function_type.is_string and function_type.const:
                                # Ensure that the value we're returning is actually a safe ref const.
                                if not self.is_safe_ref(simple_statement.value, stack, refs_copy, local_consts, context.wrap(simple_statement.value)):
                                    raise CompilerError("Cannot return a locally-computed constant value from a function marked as const.", context.wrap(simple_statement))

                            compiled += self.generate_expr(
                                simple_statement.value,
                                return_dest,
                                stack,
                                clobbers,
                                allocations,
                                refs_copy,
                                local_consts,
                                context.wrap(simple_statement.value),
                            )
                            compiled += self.generate_return(function_type, stack, clobbers, context.wrap(simple_statement))

                            # If we modified the type to avoid a strcpy, put it back here.
                            stack.retype("builtin(retval)", original_type)

                            for var in reversed(free_list):
                                stack.free(var)

                        # We lie here, because while the last statement wasn't a continue, it serves a similar purpose.
                        last_statement_was_return = True
                        last_statement_was_continue = True

                    elif isinstance(simple_statement, cst.AnnAssign):
                        compiled += self.generate_assign_expr(
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

                        target = simple_statement.targets[0].target
                        assignment = expr_to_str(simple_statement.value).strip()
                        if target != assignment:
                            compiled += self.generate_assign_expr(
                                target,
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
                        compiled += self.generate_augassign_expr(
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
                        if statement_no == 0 and substatement_no == 0:
                            # Possible special case where we ignore docstrings.
                            possible_string = simple_statement.value
                            if isinstance(possible_string, cst.SimpleString):
                                if possible_string.value[:3] == '"""' or possible_string.value[:3] == "'''":
                                    continue

                        # Expression without an assignment. Most likely a function call.
                        compiled += self.generate_expr(
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
                        compiled += self.generate_break(stack, clobbers, loop, context)
                        last_statement_was_return = False
                        last_statement_was_continue = True

                    elif isinstance(simple_statement, cst.Continue):
                        compiled += self.generate_continue(stack, clobbers, loop, context)
                        last_statement_was_return = False
                        last_statement_was_continue = True

                    else:
                        raise CompilerError(f"Unsupported node to compile {simple_statement}", context)

            elif isinstance(statement, cst.If):
                if_compiled, last_statement_was_return, last_statement_was_continue = self.generate_if_statement(
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
                while_compiled, last_statement_was_return, last_statement_was_continue = self.generate_while_statement(
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
                for_compiled, last_statement_was_return, last_statement_was_continue = self.generate_for_statement(
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
                raise CompilerError(f"Unsupported node to compile {statement}", context)

        if require_return and not last_statement_was_return:
            # Simple return by itself, doesn't update the retval.
            if not function_type.is_void:
                raise CompilerError("Function is missing a return statement", context)
            compiled += self.generate_return(function_type, stack, clobbers, context)
            last_statement_was_return = True
            last_statement_was_continue = True

        if require_continue and not last_statement_was_continue:
            compiled += self.generate_continue(stack, clobbers, loop, context)
            last_statement_was_continue = True

        return compiled, last_statement_was_return, last_statement_was_continue

    def function_prototype(self, func: cst.FunctionDef, context: Context) -> FunctionPrototype:
        function_type = self.get_type(func.returns, [], allow_nopad=True, allow_extern=True, allow_array=True)
        function_params = func.params.params

        if function_type is None:
            raise CompilerError("Unsupported return type for function definition", context)

        if func.params.kwonly_params or func.params.posonly_params:
            raise CompilerError("Unsupported parameter definition for function definition", context)

        prototype = FunctionPrototype(func.name.value, function_type)
        stack: Stack = Stack(prototype.name)

        for func_param in function_params:
            # Function parameters are passed on the stack, so we must know their locations and types.
            param_type = self.get_type(func_param.annotation, [], allow_array=True)
            if param_type is None:
                raise CompilerError(f"Expecting type for function parameter {func_param.name.value}", context)

            # For non-const strings, we need to know the local storage name, based on the parameter name.
            param_name = func_param.name.value

            prototype.paramnames.append(param_name)
            prototype.params.append(param_type)
            prototype.paramdefaults.append(func_param.default)

            stack.alloc(StackVar(func_param.name.value, param_type))

        if function_type.return_padding and stack.size < function_type.size:
            # We need to request padding out to the return size.
            prototype.params.append(PaddingCoreType(function_type.size - stack.size))

        return prototype

    def function(self, func: cst.FunctionDef, refs: Sequence[Union[FunctionPrototype, GlobalVariable]], global_consts: List[Constant], context: Context) -> Sections:
        compiled = Sections()
        function_name = func.name.value
        function_type = self.get_type(func.returns, [], allow_nopad=True, allow_extern=True, allow_array=True)
        function_params = func.params.params
        stack: Stack = Stack(function_name)

        if function_type is None:
            raise CompilerError("Unsupported return type for function definition", context)

        # If this is an extern function, make sure it has no body.
        if function_type.extern:
            if len(func.body.body) != 1:
                raise CompilerError("Unsupported body in extern function definition", context)
            element = func.body.body[0]
            if not isinstance(element, cst.Expr):
                raise CompilerError("Unsupported body in extern function definition", context)
            if not isinstance(element.value, cst.Ellipsis):
                raise CompilerError("Unsupported body in extern function definition", context)

            return compiled

        if func.params.kwonly_params or func.params.posonly_params:
            raise CompilerError("Unsupported parameter definition for function definition", context)

        for func_param in function_params:
            # Function parameters are passed on the stack, so we must know their locations and types.
            param_type = self.get_type(func_param.annotation, [], allow_array=True)
            if param_type is None:
                raise CompilerError(f"Expecting type for function parameter {func_param.name.value}", context)

            # If it is a non-const string, we need to allocate data for this that callers will copy
            # into when calling this function.
            if param_type.is_string and not param_type.const:
                if not param_type.is_array:
                    raise CompilerError(f"Non-constant string parameter{func_param.name.value} requires a length", context)

                local_destination_storage = f"{function_name}_{func_param.name.value}_param"
                compiled.append_data(f"{local_destination_storage}:")
                compiled.append_data(f"  .pad {param_type.length or MAX_STRING_LENGTH}")

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
        if not function_type.is_void:
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
        if not function_type.is_void:
            temp_size = stack.alloc(StackVar("builtin(retval)", function_type))
            stack.move(temp_size)

        # First pass to figure out clobbers, but don't use up any variable names or label names.
        clobbers: Set[str] = set()

        self._push_names()
        self.compile_chunk(func.body, stack.clone(), clobbers, {}, function_type, refs, None, global_consts[:], context, require_return=True, require_continue=False)
        self._pop_names()

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
            compiled += self.generate_subpci(padding_move_amt, "allocating padding")
            stack.move(padding_move_amt)
            compiled.code += comment_stack(stack)

        # Now, let's save all of our clobbered values.
        cref = None
        if clobbers:
            cref = self.comment_ref()
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
        if not function_type.is_void:
            stack.alloc(StackVar("builtin(retval)", function_type))

        # Now, second pass to actually compile.
        chunk, _, _ = self.compile_chunk(func.body, stack, set(), {}, function_type, refs, None, global_consts[:], context, require_return=True, require_continue=False)
        compiled += chunk

        # Function boundary is where we optimize redundant stack moves and load/store operations.
        compiled.code = self.optimization_pass(compiled.code, context.settings.optimize)

        # Finally, find any comments that comment on empty blocks after optimization, and remove them.
        compiled.code = self.remove_empty_comments(compiled.code)
        compiled.code = self.remove_duplicate_source_comments(context, compiled.code)
        compiled_preamble = compiled.preamble
        if compiled_preamble:
            compiled_preamble.append("")
        compiled.preamble = []

        return Sections(
            code=self.remove_empty_lines([
                *compiled_preamble,
                f"{function_name}:",
                *preamble,
                *compiled.code,
            ]),
            data=compiled.data,
            init=compiled.init,
        )

    def remove_duplicate_source_comments(self, context: Context, code: List[str]) -> List[str]:
        # Clone this so we aren't mutating the input because that's bad form.
        code = code[:]

        pos = 0
        length = len(code)
        seen: Set[str] = set()
        lastseen: int = -100

        while pos < length:
            line = code[pos]

            trimmed = line.strip()
            if not trimmed or trimmed[0] != ";":
                pos += 1
                continue

            if ":" not in trimmed:
                pos += 1
                continue

            coderef, _ = trimmed.split(":", 1)

            if context.module in coderef and " line " in coderef:
                # This works because we always add more general comments before more
                # specific comments for an expression generator. So, if we have redundant
                # comments, the more general one will always end up on a line above a more
                # specific one.
                if coderef in seen and lastseen == pos - 1:
                    code.pop(pos)
                    length -= 1
                else:
                    seen.add(coderef)
                    lastseen = pos
                    pos += 1
            else:
                pos += 1

        return code

    def remove_empty_comments(self, code: List[str]) -> List[str]:
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

                    meat = sanitize(checkline)
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

    def remove_empty_lines(self, code: List[str]) -> List[str]:
        # Clone this so we aren't mutating the input because that's bad form.
        code = code[:]

        while code and (not code[0].strip()):
            code.pop(0)

        while code and (not code[-1].strip()):
            code.pop(-1)

        return code

    def optimization_pass(self, code: List[str], enabled: bool) -> List[str]:
        # Clone this so we aren't mutating the input because that's bad form.
        code = code[:]

        if enabled:
            old_code = "\n".join(code)

            while True:
                code = self.optimization_pass_impl(code)
                new_code = "\n".join(code)
                if new_code == old_code:
                    break

                old_code = new_code

        def strip_opt_comment(line: str) -> str:
            return line.split("; STACKOFF", 1)[0].rstrip()

        code = [strip_opt_comment(c) for c in code]
        code = [c for c in code if c.strip() != "NOP"]
        return code

    def optimization_pass_impl(self, code: List[str]) -> List[str]:
        codelen = len(code)

        def calcoffsets(pos: int, offset: int, amount: int) -> List[int]:
            # First, find the base offset based on our current pos, skipping comments.
            while offset:
                if offset > 0:
                    # Search positively.
                    while True:
                        pos += 1

                        # Did we overrun?
                        if pos >= codelen:
                            return []
                        # Did we find code.
                        if sanitize(code[pos]):
                            break

                    offset -= 1
                else:
                    # Search negatively.
                    while True:
                        pos -= 1

                        # Did we overrun?
                        if pos < 0:
                            return []
                        # Did we find code.
                        if sanitize(code[pos]):
                            break

                    offset += 1

            # Now, gather a list of offsets based on the amount of entries we want.
            retval: List[int] = []
            while len(retval) < amount:
                retval.append(pos)

                while True:
                    pos += 1

                    # Did we overrun?
                    if pos >= codelen:
                        return []
                    # Did we find code.
                    if sanitize(code[pos]):
                        break

            return retval

        def getline(pos: int, offset: int = 0, **kwargs: bool) -> str:
            locs = calcoffsets(pos, offset, 1)
            if len(locs) != 1:
                if not kwargs.get("sanitize", True):
                    raise Exception("Logic error, trying to get un-sanitized line that doesn't exist!")
                return ""
            loc = locs[0]

            return sanitize(code[loc]) if kwargs.get("sanitize", True) else code[loc]

        def curpos(pos: int, offset: int = 0) -> Optional[str]:
            locs = calcoffsets(pos, offset, 1)
            if len(locs) != 1:
                return None
            loc = locs[0]

            return stackpos(code[loc])

        def remove(pos: int, length: int = 1, offset: int = 0) -> None:
            nonlocal code
            nonlocal codelen

            locs = calcoffsets(pos, offset, length)
            if len(locs) != length:
                raise Exception("Logic error, cannot remove locations that do not exist!")

            for off in sorted(locs, reverse=True):
                code = code[:off] + code[(off + 1):]
            codelen -= length

        def replace(pos: int, length: int, new: List[str], offset: int = 0) -> None:
            nonlocal code
            nonlocal codelen

            locs = calcoffsets(pos, offset, length)
            if len(locs) != length:
                raise Exception("Logic error, cannot replace locations that do not exist!")
            insertloc = locs[0]

            # First, remove the old vales.
            for off in sorted(locs, reverse=True):
                code = code[:off] + code[(off + 1):]

            code = code[:insertloc] + new + code[insertloc:]
            codelen -= length
            codelen += len(new)

        def offset(pos: int, amount: int) -> int:
            locs = calcoffsets(pos, amount, 1)
            if len(locs) != 1:
                if amount < 0:
                    return 0
                else:
                    return codelen

            return locs[0]

        def insn(line: str) -> str:
            return line.split(" ", 1)[0]

        def params(line: str) -> str:
            return line.split(" ", 1)[1]

        def param_as_int(line: str) -> Optional[int]:
            try:
                return int(params(line))
            except ValueError:
                try:
                    return int(params(line), base=16)
                except ValueError:
                    return None

        def stackpos(line: str) -> Optional[str]:
            if "; STACKOFF:" in line:
                _, pos = line.split("; STACKOFF: ", 1)
                return pos.strip()
            return None

        def moveamt(line: str) -> int:
            if insn(line) == "INCPC":
                return 1
            if insn(line) == "DECPC":
                return -1
            if insn(line) == "ADDPCI":
                return int(line.split(" ", 1)[1])
            if insn(line) == "SUBPCI":
                return -int(line.split(" ", 1)[1])
            raise Exception("Logic error, unexpected instruction!")

        def toggle_check(param: str) -> str:
            if param.endswith(" ZF"):
                return param[:-3] + " !ZF"
            if param.endswith(" !ZF"):
                return param[:-4] + " ZF"
            if param.endswith(" CF"):
                return param[:-3] + " !CF"
            if param.endswith(" !CF"):
                return param[:-4] + " !CF"
            raise Exception("Logic error, shouldn't be inverting instruction that isn't SKIPIF!")

        stack_counts: Dict[str, int] = {
            'builtin(retptr) + 0': 1,
            'builtin(retptr) + 1': 1,
            'builtin(retval) + 0': 1,
            'builtin(retval) + 1': 1,
            'builtin(retval) + 2': 1,
            'builtin(retval) + 3': 1,
        }
        for line in code:
            stpos = stackpos(line)
            if stpos:
                stack_counts[stpos] = stack_counts.get(stpos, 0) + 1

        stackop = {"ADDPCI", "INCPC", "SUBPCI", "DECPC"}
        memoryop = {"LOADI", "ADDI", "INV", "SHL", "SHR", "RCL", "RCR", "ROL", "ROR", "ZERO", "NOP", "NEG", "INC", "DEC"}
        aluop = {"INV", "NEG", "ADD", "ADC", "AND", "OR", "XOR", "ADDU", "ADCU", "ANDU", "ORU", "XORU", "ADDV", "ADCV", "ANDV", "ORV", "XORV", "SHL", "SHR", "RCL", "RCR", "ROL", "ROR"}

        pos = 0
        while pos < codelen:
            cur = getline(pos)

            if not cur:
                # Nothing here, no sense wasting time checking.
                pos += 1
                continue

            nxt = getline(pos, offset=1)
            prv = getline(pos, offset=-1)

            if cur == "SWAP PC, SPC" and nxt == "SWAP PC, SPC":
                # Shouldn't ever happen, but is super easy to get rid of.
                remove(pos, 2)

            elif insn(cur) in stackop and insn(nxt) in stackop:
                # Opportunity to combine as long as it doesn't overrun.
                first_move = moveamt(cur)
                second_move = moveamt(nxt)

                total_move = first_move + second_move
                if total_move == 0:
                    remove(pos, 2)
                elif total_move == 1:
                    replace(pos, 2, ["  INCPC"])
                elif total_move == -1:
                    replace(pos, 2, ["  DECPC"])
                elif total_move > 1 and total_move <= 31:
                    replace(pos, 2, [f"  ADDPCI {total_move}"])
                elif total_move < -1 and total_move >= -32:
                    replace(pos, 2, [f"  SUBPCI {-total_move}"])
                else:
                    # Can't combine, move too great.
                    pos = offset(pos, 1)

            elif insn(cur) in memoryop and insn(prv) in stackop and insn(nxt) in stackop:
                # In this case, we can reorder instructions since it doesn't matter what order they
                # happen, but it also means that we can possibly fold redundant moves. This may only
                # exist because we reduced redundant store/loads with a constant load.
                replace(pos, 2, [getline(pos, offset=1, sanitize=False), getline(pos, sanitize=False)])

            elif insn(prv) == "INV" and insn(cur) in {"JRIZ", "JRINZ", "LNGJUMPZ", "LNGJUMPNZ"}:
                # Strict equality/inequality checks for string/integer/characters.
                if (
                    getline(pos, offset=-2) == "INV" and
                    getline(pos, offset=-3) == "SKIPIF ZF" and
                    insn(getline(pos, offset=-4)) == "LOADI" and param_as_int(getline(pos, offset=-4)) in {0x00, 0xFF} and
                    (insn(getline(pos, offset=-5)) in {"XOR", "AND", "OR"} or (insn(getline(pos, offset=-5)) == "ADDI" and param_as_int(getline(pos, offset=-5)) == 0))
                ):
                    param_val = param_as_int(getline(pos, offset=-4))

                    if insn(cur) == "JRIZ":
                        replacement = [f"  JRINZ {params(cur)}"] if param_val == 0x00 else [f"  JRIZ {params(cur)}"]
                    elif insn(cur) == "JRINZ":
                        replacement = [f"  JRIZ {params(cur)}"] if param_val == 0x00 else [f"  JRINZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPZ":
                        replacement = [f"  LNGJUMPNZ {params(cur)}"] if param_val == 0x00 else [f"  LNGJUMPZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPNZ":
                        replacement = [f"  LNGJUMPZ {params(cur)}"] if param_val == 0x00 else [f"  LNGJUMPNZ {params(cur)}"]
                    else:
                        raise Exception("Logic error, unknown replacement!")

                    replace(pos, 5, replacement, offset=-4)
                    pos = offset(pos, -4)

                # Strict equality/inequality checks for string/integer/characters.
                elif (
                    getline(pos, offset=-2) == "INV" and
                    getline(pos, offset=-3) == "SKIPIF !ZF" and
                    insn(getline(pos, offset=-4)) == "LOADI" and param_as_int(getline(pos, offset=-4)) in {0x00, 0xFF} and
                    (insn(getline(pos, offset=-5)) in {"XOR", "AND", "OR"} or (insn(getline(pos, offset=-5)) == "ADDI" and param_as_int(getline(pos, offset=-5)) == 0))
                ):
                    param_val = param_as_int(getline(pos, offset=-4))

                    if insn(cur) == "JRIZ":
                        replacement = [f"  JRINZ {params(cur)}"] if param_val == 0xFF else [f"  JRIZ {params(cur)}"]
                    elif insn(cur) == "JRINZ":
                        replacement = [f"  JRIZ {params(cur)}"] if param_val == 0xFF else [f"  JRINZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPZ":
                        replacement = [f"  LNGJUMPNZ {params(cur)}"] if param_val == 0xFF else [f"  LNGJUMPZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPNZ":
                        replacement = [f"  LNGJUMPZ {params(cur)}"] if param_val == 0xFF else [f"  LNGJUMPNZ {params(cur)}"]
                    else:
                        raise Exception("Logic error, unknown replacement!")

                    replace(pos, 5, replacement, offset=-4)
                    pos = offset(pos, -4)

                # Alligator expression inequality checks for integers.
                elif (
                    getline(pos, offset=-2) == "INV" and
                    getline(pos, offset=-3) == "SKIPIF !ZF" and
                    insn(getline(pos, offset=-4)) == "ZERO" and
                    insn(getline(pos, offset=-5)) == "ADDI" and param_as_int(getline(pos, offset=-5)) in {1, -1}
                ):
                    if insn(cur) == "JRIZ":
                        replacement = [f"  JRIZ {params(cur)}"]
                    elif insn(cur) == "JRINZ":
                        replacement = [f"  JRINZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPZ":
                        replacement = [f"  LNGJUMPZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPNZ":
                        replacement = [f"  LNGJUMPNZ {params(cur)}"]
                    else:
                        raise Exception("Logic error, unknown replacement!")

                    replace(pos, 5, replacement, offset=-4)
                    pos = offset(pos, -4)

                elif (
                    getline(pos, offset=-2) == "INV" and
                    getline(pos, offset=-3) == "SKIPIF ZF" and
                    insn(getline(pos, offset=-4)) == "ZERO" and
                    insn(getline(pos, offset=-5)) == "ADDI" and param_as_int(getline(pos, offset=-5)) in {1, -1}
                ):
                    if insn(cur) == "JRIZ":
                        replacement = [f"  JRINZ {params(cur)}"]
                    elif insn(cur) == "JRINZ":
                        replacement = [f"  JRIZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPZ":
                        replacement = [f"  LNGJUMPNZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPNZ":
                        replacement = [f"  LNGJUMPZ {params(cur)}"]
                    else:
                        raise Exception("Logic error, unknown replacement!")

                    replace(pos, 5, replacement, offset=-4)
                    pos = offset(pos, -4)

                else:
                    pos = offset(pos, 1)

            elif insn(cur) in {"JRIZ", "JRINZ", "LNGJUMPZ", "LNGJUMPNZ"} and getline(pos, offset=-3) == "INV" and insn(getline(pos, offset=-2)) == "SKIPIF":
                # Strict equality/inequality checks for string/integer/characters.
                if (
                    getline(pos, offset=-4) == "INV" and
                    getline(pos, offset=-5) == "SKIPIF ZF" and
                    insn((pos_6 := getline(pos, offset=-6))) == "LOADI" and param_as_int(pos_6) in {0x00, 0xFF} and
                    (insn((pos_7 := getline(pos, offset=-7))) in {"XOR", "AND", "OR"} or (insn(pos_7) == "ADDI" and param_as_int(pos_7) == 0))
                ):
                    param_val = param_as_int(pos_6)
                    if param_val == 0x00:
                        skip_insn = toggle_check(getline(pos, offset=-2, sanitize=False))
                    else:
                        skip_insn = getline(pos, offset=-2, sanitize=False)

                    if insn(cur) == "JRIZ":
                        replacement = [f"  JRINZ {params(cur)}"] if param_val == 0x00 else [f"  JRIZ {params(cur)}"]
                    elif insn(cur) == "JRINZ":
                        replacement = [f"  JRIZ {params(cur)}"] if param_val == 0x00 else [f"  JRINZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPZ":
                        replacement = [f"  LNGJUMPNZ {params(cur)}"] if param_val == 0x00 else [f"  LNGJUMPZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPNZ":
                        replacement = [f"  LNGJUMPZ {params(cur)}"] if param_val == 0x00 else [f"  LNGJUMPNZ {params(cur)}"]
                    else:
                        raise Exception("Logic error, unknown replacement!")

                    replacement = [
                        skip_insn,
                        getline(pos, offset=-1, sanitize=False),
                        *replacement,
                    ]
                    replace(pos, 7, replacement, offset=-6)
                    pos = offset(pos, -6)

                # Strict equality/inequality checks for string/integer/characters.
                elif (
                    getline(pos, offset=-4) == "INV" and
                    getline(pos, offset=-5) == "SKIPIF !ZF" and
                    insn((pos_6 := getline(pos, offset=-6))) == "LOADI" and param_as_int(pos_6) in {0x00, 0xFF} and
                    (insn((pos_7 := getline(pos, offset=-7))) in {"XOR", "AND", "OR"} or (insn(pos_7) == "ADDI" and param_as_int(pos_7) == 0))
                ):
                    param_val = param_as_int(pos_6)
                    if param_val == 0xFF:
                        skip_insn = toggle_check(getline(pos, offset=-2, sanitize=False))
                    else:
                        skip_insn = getline(pos, offset=-2, sanitize=False)

                    if insn(cur) == "JRIZ":
                        replacement = [f"  JRINZ {params(cur)}"] if param_val == 0xFF else [f"  JRIZ {params(cur)}"]
                    elif insn(cur) == "JRINZ":
                        replacement = [f"  JRIZ {params(cur)}"] if param_val == 0xFF else [f"  JRINZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPZ":
                        replacement = [f"  LNGJUMPNZ {params(cur)}"] if param_val == 0xFF else [f"  LNGJUMPZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPNZ":
                        replacement = [f"  LNGJUMPZ {params(cur)}"] if param_val == 0xFF else [f"  LNGJUMPNZ {params(cur)}"]
                    else:
                        raise Exception("Logic error, unknown replacement!")

                    replacement = [
                        skip_insn,
                        getline(pos, offset=-1, sanitize=False),
                        *replacement,
                    ]
                    replace(pos, 7, replacement, offset=-6)
                    pos = offset(pos, -6)

                # Alligator expression inequality checks for integers.
                elif (
                    getline(pos, offset=-4) == "INV" and
                    getline(pos, offset=-5) == "SKIPIF !ZF" and
                    insn(getline(pos, offset=-6)) == "ZERO" and
                    insn((pos_7 := getline(pos, offset=-7))) == "ADDI" and param_as_int(pos_7) in {1, -1}
                ):
                    if insn(cur) == "JRIZ":
                        replacement = [f"  JRIZ {params(cur)}"]
                    elif insn(cur) == "JRINZ":
                        replacement = [f"  JRINZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPZ":
                        replacement = [f"  LNGJUMPZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPNZ":
                        replacement = [f"  LNGJUMPNZ {params(cur)}"]
                    else:
                        raise Exception("Logic error, unknown replacement!")

                    replacement = [
                        getline(pos, offset=-2, sanitize=False),
                        getline(pos, offset=-1, sanitize=False),
                        *replacement,
                    ]
                    replace(pos, 7, replacement, offset=-6)
                    pos = offset(pos, -6)

                elif (
                    getline(pos, offset=-4) == "INV" and
                    getline(pos, offset=-5) == "SKIPIF ZF" and
                    insn(getline(pos, offset=-6)) == "ZERO" and
                    insn((pos_7 := getline(pos, offset=-7))) == "ADDI" and param_as_int(pos_7) in {1, -1}
                ):
                    if insn(cur) == "JRIZ":
                        replacement = [f"  JRINZ {params(cur)}"]
                    elif insn(cur) == "JRINZ":
                        replacement = [f"  JRIZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPZ":
                        replacement = [f"  LNGJUMPNZ {params(cur)}"]
                    elif insn(cur) == "LNGJUMPNZ":
                        replacement = [f"  LNGJUMPZ {params(cur)}"]
                    else:
                        raise Exception("Logic error, unknown replacement!")

                    replacement = [
                        toggle_check(getline(pos, offset=-2, sanitize=False)),
                        getline(pos, offset=-1, sanitize=False),
                        *replacement,
                    ]
                    replace(pos, 7, replacement, offset=-6)
                    pos = offset(pos, -6)

                else:
                    pos = offset(pos, 1)

            elif insn(prv) in aluop and cur == "ADDI 0":
                remove(pos)

            elif cur == "ADDI 0" and nxt == "ADDI 0":
                remove(pos, offset=1)

            elif cur == "STORE A" and nxt == "LOAD A":
                remove(pos, offset=1)

            elif cur == "STORE A" and nxt == "STORE A":
                remove(pos, offset=1)

            elif cur == "STORE U" and nxt == "LOAD U":
                remove(pos, offset=1)

            elif cur == "STORE U" and nxt == "STORE U":
                remove(pos, offset=1)

            elif cur == "STORE V" and nxt == "STORE V":
                remove(pos, offset=1)

            elif cur == "STORE V" and nxt == "LOAD V":
                remove(pos, offset=1)

            elif cur == "LOAD A" and nxt == "STORE A":
                remove(pos, offset=1)

            elif cur == "LOAD A" and nxt == "LOAD A":
                remove(pos, offset=1)

            elif cur == "LOAD U" and nxt == "STORE U":
                remove(pos, offset=1)

            elif cur == "LOAD U" and nxt == "LOAD U":
                remove(pos, offset=1)

            elif cur == "LOAD V" and nxt == "STORE V":
                remove(pos, offset=1)

            elif cur == "LOAD V" and nxt == "LOAD V":
                remove(pos, offset=1)

            elif insn(cur) == "STORE" and (key := curpos(pos)) is not None and stack_counts[key] == 1:
                remove(pos)

            elif insn(cur) in {"JRI", "JRIZ", "JRINZ", "LNGJUMP", "LNGJUMPZ", "LNGJUMPNZ"} and (params(cur) + ":") == nxt:
                remove(pos)

            elif insn(prv) == "LOADI" and insn(cur) == "INV" and insn(nxt) in {"JRIZ", "JRINZ", "LNGJUMPZ", "LNGJUMPNZ"}:
                # This can be statically computed and is probably a "while True" check.
                intparam = param_as_int(prv)
                if intparam is None:
                    pos = offset(pos, 1)
                    continue

                intparam = (~intparam) & 0xFF
                if intparam:
                    if insn(nxt) in {"JRIZ", "LNGJUMPZ"}:
                        # Will never be taken.
                        remove(pos, 3, offset=-1)
                        pos = offset(pos, -1)
                    elif insn(nxt) == "JRINZ":
                        # Will always be taken.
                        replace(pos, 3, [f"  JRI {params(nxt)}"], offset=-1)
                        pos = offset(pos, -1)
                    elif insn(nxt) == "LNGJUMPNZ":
                        # Will always be taken.
                        replace(pos, 3, [f"  LNGJUMP {params(nxt)}"], offset=-1)
                        pos = offset(pos, -1)
                    else:
                        raise Exception("Logic error, unrecognized instruction to replace!")
                else:
                    if insn(nxt) in {"JRINZ", "LNGJUMPNZ"}:
                        # Will never be taken.
                        remove(pos, 3, offset=-1)
                        pos = offset(pos, -1)
                    elif insn(nxt) == "JRIZ":
                        # Will always be taken.
                        replace(pos, 3, [f"  JRI {params(nxt)}"], offset=-1)
                        pos = offset(pos, -1)
                    elif insn(nxt) == "LNGJUMPZ":
                        # Will always be taken.
                        replace(pos, 3, [f"  LNGJUMP {params(nxt)}"], offset=-1)
                        pos = offset(pos, -1)
                    else:
                        raise Exception("Logic error, unrecognized instruction to replace!")

            elif insn(prv) == "NEG" and insn(cur) == "NEG" and insn(nxt) == "NEG":
                if insn(getline(pos, offset=-2)) != "SKIPIF":
                    # Triple negation is equivalent to a single, including flags. However,
                    # if the instruction before the first NEG is a SKIPIF, we can't skip
                    # since sometimes we wouldn't perform an ALU operation to set flags.
                    remove(pos, 2)

                else:
                    # Didn't remove anything, onward.
                    pos = offset(pos, 1)

            elif insn(prv) == "INV" and insn(cur) == "INV" and insn(nxt) == "INV":
                if insn(getline(pos, offset=-2)) != "SKIPIF":
                    # Triple negation is equivalent to a single, including flags.
                    remove(pos, 2)

                elif (
                    insn(getline(pos, offset=-2)) == "SKIPIF" and
                    insn((pos_3 := getline(pos, offset=-3))) == "LOADI" and param_as_int(pos_3) in {0x00, 0xFF}
                ):
                    param_val = param_as_int(pos_3)
                    actual = getline(pos, offset=-3, sanitize=False)
                    if ";" in actual:
                        raise Exception("Logic error, unexpected comment in load immediate!")
                    if param_val is None:
                        raise Exception("Logic error, param value cannot be null!")

                    replacement = [
                        f"  LOADI {hex((~param_val) & 0xFF)}",
                        getline(pos, offset=-2, sanitize=False)
                    ]

                    replace(pos, 3, replacement, offset=-3)
                    pos = offset(pos, -3)

                else:
                    # Didn't remove anything, onward.
                    pos = offset(pos, 1)

            elif insn(prv) == "LOADI" and insn(cur) in {"INV", "NEG"} and insn(nxt) not in {"SKIPIF", "JRIZ", "JRINZ", "LNGJUMPZ", "LNGJUMPNZ"}:
                intparam = param_as_int(prv)
                if intparam is not None:
                    if insn(cur) == "INV":
                        intparam = (~intparam) & 0xFF
                    elif insn(cur) == "NEG":
                        intparam = ((~intparam) + 1) & 0xFF
                    else:
                        intparam = None

                if intparam is not None:
                    actual = getline(pos, offset=-1, sanitize=False)
                    if ";" in actual:
                        raise Exception("Logic error, unexpected comment in load immediate!")

                    replace(pos, 2, [f"  LOADI {hex(intparam)}"], offset=-1)
                    pos = offset(pos, -1)
                else:
                    pos = offset(pos, 1)

            elif insn(cur) == "LOADI" and insn(nxt) == "ADD":
                intparam = param_as_int(cur)
                if intparam is not None:
                    intparam = intparam & 0xFF
                    if intparam & 0x80:
                        intparam = -(((~intparam) + 1) & 0xFF)

                    curstackpos = curpos(pos, offset=1)
                    if intparam >= -32 and intparam <= 31 and curstackpos is not None:
                        replace(pos, 2, [f"  LOAD A ; STACKOFF: {curstackpos}", f"  ADDI {intparam}"])
                        continue

                pos = offset(pos, 1)

            else:
                # Didn't remove anything, onward.
                pos = offset(pos, 1)

        return code

    def is_assign_type_definition(self, assign: cst.Assign) -> bool:
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

    def is_annassign_type_definition(self, assign: cst.AnnAssign) -> bool:
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

    def compile_module(self, module: str, code: str, refs: Sequence[Union[FunctionPrototype, GlobalVariable]]) -> Sections:
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
            context = Context(module, self.settings, statement, metadata)

            if isinstance(statement, cst.SimpleStatementLine):
                bodylines = statement.body
                if len(bodylines) != 1:
                    raise CompilerError("Multi-statement lines are not supported", context.wrap(statement))

                body = bodylines[0]
                if isinstance(body, cst.Assign):
                    # This could be a mypy type assignment so that the python source files can be typechecked.
                    if not self.is_assign_type_definition(body):
                        raise CompilerError("Global variable declarations must have a type", context.wrap(body))
                elif isinstance(body, cst.AnnAssign):
                    if not self.is_annassign_type_definition(body):
                        compiled += self.generate_global_variable(body, global_vars, global_consts, context.wrap(body))
                elif isinstance(body, cst.ImportFrom):
                    is_typing_import = False

                    if isinstance(body.module, cst.Name) and body.module.value == "typing":
                        is_typing_import = True

                    if not is_typing_import:
                        # Attempt to resolve the imports we need to handle.
                        new_refs = self.parse_import_refs(body, context.wrap(body))

                        old_names = {r.name for r in refs}
                        new_names = {r.name for r in new_refs}
                        common_names = old_names & new_names
                        if common_names:
                            raise CompilerError(f"Import of {', '.join(common_names)} shadows local definitions", context.wrap(body))

                        refs = [*refs, *new_refs]
                elif isinstance(body, cst.Import):
                    for alias in body.names:
                        name_str = expr_to_str(alias.name).strip()
                        if name_str not in {"sys"}:
                            raise CompilerError(f"Import of {name_str} is not supported", context.wrap(body))

                        if alias.asname:
                            alias_str = expr_to_str(alias.asname.name).strip()
                        else:
                            alias_str = name_str

                        if not alias_str.isidentifier():
                            raise CompilerError(f"Import of {name_str} as {alias_str} is not supported", context.wrap(body))

                        global_consts.append(Constant(alias_str, CoreType("object", const=True), value=SysConstant()))

                else:
                    raise CompilerError("Arbitrary top-level statements are not supported", context.wrap(body))

            elif isinstance(statement, cst.FunctionDef):
                compiled += self.function(statement, refs, global_consts, context.wrap(statement))
            else:
                # TODO: What other statement types are we missing here?
                raise CompilerError("Unsupported statement {statement}", context.wrap(statement))

            compiled.append_code("")

        compiled.code = self.remove_empty_lines(compiled.code)
        if compiled.preamble:
            raise Exception("Logic error, shouldn't have any unconsumed preamble!")

        return compiled

    def __default_file_loader(self, filename: str) -> Optional[str]:
        try:
            with open(filename, "r") as fp:
                return fp.read()
        except FileNotFoundError:
            return None

    def set_file_loader(self, loader: Optional[Callable[[str], Optional[str]]]) -> None:
        self.__file_loader = loader or self.__default_file_loader

    def set_working_directory(self, directory: Optional[str]) -> None:
        self.__working_directory = directory or "."

    def add_library_directory(self, directory: str) -> None:
        self.__library_directory.append(directory)

    def parse_import_refs(self, body: cst.ImportFrom, context: Context) -> List[Union[FunctionPrototype, GlobalVariable]]:
        # First, figure out any relative import location.
        relative = len(body.relative)
        if relative < 1:
            relative = 1

        # Now figure out the relative file path based on the dotted name.
        dotted_name = body.module
        if dotted_name is None:
            raise CompilerError("Purely relative imports are not supported", context)

        def resolve_path(node: cst.BaseExpression) -> str:
            if isinstance(node, cst.Name):
                return node.value
            elif isinstance(node, cst.Attribute):
                return os.path.join(resolve_path(node.value), node.attr.value)
            else:
                raise Exception("Logic error, unexpected node!")

        path = resolve_path(dotted_name) + ".py"
        if relative == 1:
            path = os.path.join(".", path)
        else:
            path = os.path.join(*([".."] * (relative - 1)), path)

        # Now load the file and parse its forward refs, preferring the working directory and then
        # looking in library paths.
        for wd in [self.__working_directory, *self.__library_directory]:
            fullpath = os.path.abspath(os.path.join(wd, path))
            code = self.__file_loader(fullpath)
            if code:
                break

        if code is None:
            raise CompilerError(f"File {path} not found when attempting import", context)

        file_refs = self.parse_forward_refs(fullpath, code)

        # Now, filter them down to what was imported.
        if not isinstance(body.names, cst.ImportStar):
            actual_names = set()
            for name in body.names:
                if not isinstance(name.name, cst.Name):
                    raise CompilerError("Dotted names are not supported in import statements", context)

                actual_names.add(name.name.value)

            actual_refs = {r.name for r in file_refs}
            for import_name in actual_names:
                if import_name not in actual_refs:
                    raise CompilerError(f"File {path} does not export importable {import_name}", context)

            file_refs = [f for f in file_refs if f.name in actual_names]

        # Now, return them.
        return file_refs

    def parse_forward_refs(self, module: str, code: str) -> List[Union[FunctionPrototype, GlobalVariable]]:
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
            context = Context(module, CompilerSettings(optimize=False), statement, metadata)

            if isinstance(statement, cst.FunctionDef):
                prototype = self.function_prototype(statement, context)
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
                    if not self.is_annassign_type_definition(body):
                        global_vars: List[GlobalVariable] = []
                        self.generate_global_variable(body, global_vars, [], context)
                        prototypes += global_vars

        return prototypes

    def parse_and_compile_module(self, module: str, code: str) -> Sections:
        forward_refs: List[Union[FunctionPrototype, GlobalVariable]] = builtin_forward_refs()
        forward_refs += self.parse_forward_refs(module, code)
        return self.compile_module(module, code, forward_refs)


VoidType = CoreType("void", None, const=True, extern=False, return_padding=False)


def builtin_functions() -> List[FunctionPrototype]:
    return [
        # Defined by python to have positional-only parameters, so no named params.
        FunctionPrototype("len", RegisterCoreType("uint8", "A"), [CoreType("str")]),
        # Allows for an optional named parameter.
        FunctionPrototype("str", CoreType("str"), [CoreType("any")], ["object"]),
        # Defined by python to have positional-only parameters, so no named params.
        FunctionPrototype("int", CoreType("int"), [CoreType("any")]),
        # Allows for a named parameter if needed. We don't normally support None, but we use this as a sentinel to ignore the param in cases that shouldn't need it.
        FunctionPrototype("peek", CoreType("any"), [CoreType("uint16"), CoreType("uint8")], ["addr", "length"], [None, SentinelInteger("0")]),
        # Allows for a named parameter if desired.
        FunctionPrototype("poke", VoidType, [CoreType("uint16"), CoreType("any")], ["addr", "object"]),
        # Allows for a named parameter if desired.
        FunctionPrototype("cast", CoreType("any"), [CoreType("any"), CoreType("any")], ["typ", "val"]),
        # Defined by python to have positional-only parameters, so no named params.
        FunctionPrototype("abs", CoreType("int"), [CoreType("int")]),
        # Defined by python to have positional-only parameters, so no named params.
        FunctionPrototype("bool", CoreType("bool"), [CoreType("any")]),
        # Defined by python to have positional-only parameters, so no named params.
        FunctionPrototype("chr", CoreType("char"), [CoreType("int")]),
        # Defined by python to have positional-only parameters, so no named params.
        FunctionPrototype("ord", CoreType("uint8"), [CoreType("char")]),
        # Defined by python to have positional-only parameters, so no named params.
        FunctionPrototype("hex", CoreType("str"), [CoreType("int")]),
        # Defined by python to have positional-only parameters, so no named params.
        FunctionPrototype("min", CoreType("int"), [CoreType("int"), CoreType("int")]),
        # Defined by python to have positional-only parameters, so no named params.
        FunctionPrototype("max", CoreType("int"), [CoreType("int"), CoreType("int")]),
        # Allows for named parameters if so desired, with the second parameter being optional and defaulting to 8 frac bits.
        FunctionPrototype("fixed", CoreType("int32"), [CoreType("int"), CoreType("int")], ["value", "fracbits"], [None, cst.Integer("8")]),
        # Defined by python to have positional-only parameters, so no named params. Defined defaults, however, to bypass type checking.
        FunctionPrototype("range", CoreType("int"), [CoreType("int"), CoreType("int"), CoreType("int")], None, [None, cst.Integer("0"), cst.Integer("0")]),
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
        FunctionPrototype("itohex8", VoidType, [RegisterCoreType("int8", "A"), PreservedCoreType("str")]),
        FunctionPrototype("itohex16", VoidType, [PreservedCoreType("int16"), PreservedCoreType("str")]),
        FunctionPrototype("itohex32", VoidType, [PreservedCoreType("int32"), PreservedCoreType("str")]),

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
        FunctionPrototype("umin8", RegisterCoreType("uint8", "A"), [InOutCoreType("uint8"), InOutCoreType("uint8")]),
        FunctionPrototype("umin16", CoreType("uint16"), [CoreType("uint16"), CoreType("uint16")]),
        FunctionPrototype("umin32", CoreType("uint32"), [CoreType("uint32"), CoreType("uint32")]),
        FunctionPrototype("umax8", RegisterCoreType("uint8", "A"), [InOutCoreType("uint8"), InOutCoreType("uint8")]),
        FunctionPrototype("umax16", CoreType("uint16"), [CoreType("uint16"), CoreType("uint16")]),
        FunctionPrototype("umax32", CoreType("uint32"), [CoreType("uint32"), CoreType("uint32")]),
        FunctionPrototype("min8", RegisterCoreType("int8", "A"), [InOutCoreType("int8"), InOutCoreType("int8")]),
        FunctionPrototype("min16", CoreType("int16"), [CoreType("int16"), CoreType("int16")]),
        FunctionPrototype("min32", CoreType("int32"), [CoreType("int32"), CoreType("int32")]),
        FunctionPrototype("max8", RegisterCoreType("int8", "A"), [InOutCoreType("int8"), InOutCoreType("int8")]),
        FunctionPrototype("max16", CoreType("int16"), [CoreType("int16"), CoreType("int16")]),
        FunctionPrototype("max32", CoreType("int32"), [CoreType("int32"), CoreType("int32")]),
    ]

    return prototypes
