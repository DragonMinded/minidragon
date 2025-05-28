import os
import traceback
import libcst as cst
import libcst.metadata as meta

from typing import Dict, Iterable, Iterator, List, Mapping, Optional, Set, Union, overload


def comment_source(extra: Optional[str] = None) -> str:
    if os.environ.get("SUPPRESS_CALLER_COMMENTS"):
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

    def wrap(self, node: cst.CSTNode, extra: str = "") -> "Context":
        return Context(self.module, node, self.meta, extra)

    def comment(self) -> str:
        fresh_module = cst.parse_module("")
        code = fresh_module.code_for_node(self.node)
        while code[-1] == "\n":
            code = code[:-1]
        return f"  ; {self.module} line {self.meta[self.node].start.line}: {self.extra}{code}"


class CompilerError(Exception):
    def __init__(self, error: str, context: Context) -> None:
        metaval = context.meta[context.node]
        super().__init__(f"{context.module} line {metaval.start.line}: " + error)
        self.module = context.module
        self.line = metaval.start.line


class CoreType:
    """
    A standard type reference. Depending on where it's encountered, it can have a const[] modifier
    applied to it, and sometimes a nopad[] modifier applied to it.
    """

    def __init__(self, base_type: str, pointed_type: Optional["CoreType"] = None, const: bool = False, return_padding: bool = True) -> None:
        self.type = base_type
        self.pointed_type = pointed_type
        self.const = const
        self.return_padding = return_padding
        if self.type == "pointer" and pointed_type is None:
            raise Exception("Logic error, creating a pointer without a pointed type!")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.type == other
        if isinstance(other, CoreType):
            return self.type == other.type and self.pointed_type == other.pointed_type and self.const == other.const
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

        return pre + typestr + post

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
        if self.type == "boolean":
            return 1
        # Strings are passed by reference pointer.
        if self.type == "string":
            return 2
        # Pointers are 16 bit due to CPU arch.
        if self.type == "pointer":
            return 2
        raise NotImplementedError(f"Type {self.type} not implemented!")

    @property
    def is_unsigned(self) -> bool:
        return self.type in {"uint8", "uint16", "uint32", "char", "boolean", "string", "pointer"}

    @property
    def is_signed(self) -> bool:
        return not self.is_unsigned

    @property
    def is_integer(self) -> bool:
        return self.type in {"uint8", "uint16", "uint32", "int8", "int16", "int32"}

    @property
    def is_char(self) -> bool:
        return self.type == "char"

    @property
    def is_boolean(self) -> bool:
        return self.type == "boolean"

    @property
    def is_string(self) -> bool:
        return self.type == "string"

    @property
    def is_pointer(self) -> bool:
        return self.type == "pointer"


VoidType = CoreType("void", None, True, False)


class PreservedCoreType(CoreType):
    """
    A function call parmeter type that implies the called function will not clean this reference
    off of the stack, but instead that the stack will still contain this value upon return from
    the function. This does not imply that the values change, only that the values are not removed
    from the stack upon function call.
    """
    def __init__(self, base_type: str) -> None:
        super().__init__(base_type, None, const=True)


class InOutCoreType(CoreType):
    """
    A function call parameter type that implies the value is not just referenced when calling
    the function, but also that the function updates this value and it should be copied back
    to any calling code's variable references if needed.
    """

    def __init__(self, base_type: str) -> None:
        super().__init__(base_type, None, const=False)


class OutCoreType(CoreType):
    """
    A function call parameter type that implies that the called function places an output parameter
    here, but that the caller does not need to specify a value for calling. This should be paired
    with a ParamReturnCoreType as the function return to specify that this is where to find the
    output value.
    """

    def __init__(self, base_type: str) -> None:
        super().__init__(base_type, None, const=False)


class RegisterCoreType(CoreType):
    """
    A function call parameter type that implies that the called function requests its input or
    places its output in a particular register instead of on the stack.
    """

    def __init__(self, register: str) -> None:
        super().__init__(register, None, const=False)


class ParamReturnCoreType(CoreType):
    """
    A function call return parameter that works in tandem with OutCoreType to specify which out
    argument contains the result of the function call.
    """

    def __init__(self, position: int) -> None:
        super().__init__("position: " + str(position), None, const=False)

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


def get_type(expr: Optional[cst.CSTNode]) -> Optional[CoreType]:
    if expr is None:
        return None
    if isinstance(expr, cst.Annotation):
        expr = expr.annotation
    if not isinstance(expr, cst.BaseExpression):
        return None

    const: bool = False
    nopad: bool = False

    while True:
        if isinstance(expr, cst.Subscript):
            # Might be a const expr or a nopad expr.
            qualifier = expr.value
            if not isinstance(qualifier, cst.Name):
                return None

            if qualifier.value == "const":
                if len(expr.slice) != 1:
                    return None

                sliceval = expr.slice[0]
                if not isinstance(sliceval, cst.SubscriptElement):
                    return None
                if not isinstance(sliceval.slice, cst.Index):
                    return None

                const = True
                expr = sliceval.slice.value
                continue

            if qualifier.value == "nopad":
                if len(expr.slice) != 1:
                    return None

                sliceval = expr.slice[0]
                if not isinstance(sliceval, cst.SubscriptElement):
                    return None
                if not isinstance(sliceval.slice, cst.Index):
                    return None

                nopad = True
                expr = sliceval.slice.value
                continue

            if qualifier.value == "pointer":
                if len(expr.slice) != 1:
                    return None

                sliceval = expr.slice[0]
                if not isinstance(sliceval, cst.SubscriptElement):
                    return None
                if not isinstance(sliceval.slice, cst.Index):
                    return None

                expr = sliceval.slice.value
                pointed = get_type(expr)
                if pointed is None:
                    return None
                return CoreType("pointer", pointed, const, not nopad)

            return None

        elif isinstance(expr, cst.Name):
            if expr.value == "void":
                return VoidType
            else:
                if expr.value not in {"uint8", "int8", "uint16", "int16", "uint32", "int32", "boolean", "char", "string"}:
                    return None

                return CoreType(expr.value, None, const, not nopad)

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
    def __init__(self, name: str, vartype: CoreType) -> None:
        self.name = name
        self.type = vartype

    def __repr__(self) -> str:
        return f"Global variable {self.type!r} {self.name!r}"


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


class StackVar:
    def __init__(self, name: str, vartype: CoreType, location: Optional[int] = None) -> None:
        self.name = name
        self.type = vartype
        self.location = location

    @property
    def size(self) -> int:
        return self.type.size

    @property
    def const(self) -> bool:
        return self.type.const

    def __repr__(self) -> str:
        return f"{self.type!r} {self.name}: {self.location} size {self.size}"


class Stack:
    def __init__(self) -> None:
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
        stack = Stack()
        for entry in self.stack:
            stack.stack.append(StackVar(entry.name, entry.type, entry.location))
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
        if name in {"register(A)", "uregister(A)"}:
            return 1

        for entry in self.stack:
            if entry.name == name:
                return entry.size
        return None

    def typeof(self, name: str) -> Optional[CoreType]:
        # Special case handling
        if name == "register(A)":
            return CoreType("int8", return_padding=False)
        if name == "uregister(A)":
            return CoreType("uint8", return_padding=False)

        for entry in self.stack:
            if entry.name == name:
                return entry.type
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
    try:
        return eval(code, {}, {c.name: c.value for c in constants})
    except Exception:
        pass

    raise NonConstantExpressionException(f"{expr} is not constant, cannot eval!")


def _hex(val: int, pad: int) -> str:
    hexval = hex(val)[2:]
    while len(hexval) < pad:
        hexval = "0" + hexval

    return "0x" + hexval


def generate_global_variable(assign: cst.AnnAssign, consts: List[Constant], context: Context) -> List[str]:
    compiled: List[str] = [context.comment()]

    target_node = assign.target
    if not isinstance(target_node, cst.Name):
        raise CompilerError("Unsupported name for global variable definition", context)

    assign_name = target_node.value
    assign_type = get_type(assign.annotation.annotation)
    assign_value = assign.value

    if assign_type is None:
        raise CompilerError("Unsupported type for global variable definition", context)

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

        compiled.append(f"{assign_name}:")

        if assign_type.type in {"int8", "uint8"}:
            if not isinstance(value, int):
                raise CompilerError("Unsupported initialization value for global const definition", context)
            if assign_type == "uint8":
                if value < 0 or value > 255:
                    raise CompilerError("Initialization out of bounds", context)
            else:
                if value < -128 or value > 255:
                    raise CompilerError("Initialization out of bounds", context)

            value = value & 0xFF
            compiled.append(f"  .byte {_hex((value >> 0) & 0xFF, 2)}")
        elif assign_type.type in {"int16", "uint16"}:
            if not isinstance(value, int):
                raise CompilerError("Unsupported initialization value for global const definition", context)
            if assign_type == "uint16":
                if value < 0 or value > 65535:
                    raise CompilerError("Initialization out of bounds", context)
            else:
                if value < -32768 or value > 65535:
                    raise CompilerError("Initialization out of bounds", context)

            value = value & 0xFFFF
            compiled.append(f"  .byte {_hex((value >> 8) & 0xFF, 2)}")
            compiled.append(f"  .byte {_hex((value >> 0) & 0xFF, 2)}")
        elif assign_type.type in {"int32", "uint32"}:
            if not isinstance(value, int):
                raise CompilerError("Unsupported initialization value for global const definition", context)
            if assign_type == "uint32":
                if value < 0 or value > 4294967295:
                    raise CompilerError("Initialization out of bounds", context)
            else:
                if value < -2147483648 or value > 4294967295:
                    raise CompilerError("Initialization out of bounds", context)

            value = value & 0xFFFFFFFF
            compiled.append(f"  .byte {_hex((value >> 24) & 0xFF, 2)}")
            compiled.append(f"  .byte {_hex((value >> 16) & 0xFF, 2)}")
            compiled.append(f"  .byte {_hex((value >> 8) & 0xFF, 2)}")
            compiled.append(f"  .byte {_hex((value >> 0) & 0xFF, 2)}")
        elif assign_type == "char":
            if not isinstance(value, str):
                raise CompilerError("Unsupported initialization value for global const definition", context)
            if len(value) != 1:
                raise CompilerError("Unsupported initialization value for global const definition", context)
            compiled.append(f"  .char {value[0]!r}")
        elif assign_type == "string":
            if not isinstance(value, str):
                raise CompilerError("Unsupported initialization value for global const definition", context)
            for c in value:
                compiled.append(f"  .char {c[0]!r}")
            compiled.append("  .byte 0x00")
        else:
            raise CompilerError(f"Unsupported type {assign_type.type} for global variable definition", context)

        # Since this was successfully handled, add it to our constants, so future constants may reference it as well.
        consts.append(Constant(assign_name, assign_type, value))

    else:
        # TODO: Support allocating variables in main RAM instead of constants in ROM.
        raise CompilerError("Unsupported type for global variable definition", context)
    return compiled


def generate_move_by(reason: str, move_amt: int, stack: Stack, clobbers: Set[str], context: Context) -> List[str]:
    compiled: List[str] = []
    if move_amt == 0:
        return compiled

    if move_amt > 0:
        compiled.append(f"  SUBPCI {move_amt}" + comment_source(reason))
    elif move_amt < 0:
        compiled.append(f"  ADDPCI {-move_amt}" + comment_source(reason))

    stack.move(move_amt)
    compiled += comment_stack(stack)

    return compiled


def generate_move_to(destination: str, stack: Stack, clobbers: Set[str], context: Context, *, offset: int = 0) -> List[str]:
    compiled: List[str] = []
    move_amt = stack.find(destination)
    if move_amt is None:
        raise Exception(f"Logic error, could not find {destination} on stack to move to!")
    move_amt += offset
    if move_amt == 0:
        return compiled

    if move_amt > 0:
        compiled.append(f"  SUBPCI {move_amt}" + comment_source(f"seeking {destination}"))
    elif move_amt < 0:
        compiled.append(f"  ADDPCI {-move_amt}" + comment_source(f"seeking {destination}"))

    stack.move(move_amt)
    compiled += comment_stack(stack)

    return compiled


def stack_is_at(destination: str, stack: Stack, *, offset: int = 0) -> bool:
    move_amt = stack.find(destination)
    if move_amt is None:
        raise Exception(f"Logic error, could not find {destination} on stack to compare to!")
    move_amt += offset
    return move_amt == 0


def generate_memcpy_unrolled(
    src_loc: int,
    dst_loc: int,
    size: int,
    stack: Stack,
    clobbers: Set[str],
    context: Context,
) -> List[str]:
    compiled: List[str] = []
    if src_loc == dst_loc:
        return compiled

    from_rel = stack.diff(src_loc)
    compiled += generate_move_by("memcpy_unrolled", from_rel, stack, clobbers, context)
    shuffle_amount = stack.location - dst_loc
    if shuffle_amount == 0:
        return compiled

    if shuffle_amount < 0:
        for i in range(size):
            clobbers.add("A")

            compiled.append("  LOAD A")
            compiled.append(f"  SUBPCI {-shuffle_amount}" + comment_source())

            stack.move(-shuffle_amount)
            compiled += comment_stack(stack)

            compiled.append("  STORE A")

            if i < size - 1:
                compiled.append(f"  ADDPCI {(-shuffle_amount) - 1}" + comment_source())
                stack.move(-((-shuffle_amount) - 1))
                compiled += comment_stack(stack)

    else:
        for i in range(size):
            clobbers.add("A")

            compiled.append("  LOAD A")
            compiled.append(f"  ADDPCI {shuffle_amount}" + comment_source())

            stack.move(-shuffle_amount)
            compiled += comment_stack(stack)

            compiled.append("  STORE A")

            if i < size - 1:
                compiled.append(f"  SUBPCI {shuffle_amount + 1}" + comment_source())
                stack.move(shuffle_amount + 1)
                compiled += comment_stack(stack)

    return compiled


def generate_return(function_type: CoreType, stack: Stack, clobbers: Set[str], context: Context) -> List[str]:
    compiled: List[str] = [context.comment()]

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
        retval_abs = 0
        retval_size = stack.sizeof("builtin(retval)")
        retptr_abs = stack.absfind("builtin(retptr)")
        retptr_size = stack.sizeof("builtin(retptr)")

        if retval_abs is None or retval_size is None or retptr_abs is None or retptr_size is None:
            raise Exception("Logic error, failed to calculate return value and pointer overlap!")

        retval_locs = {retval_abs + i for i in range(retval_size)}
        retptr_locs = {retptr_abs + i for i in range(retptr_size)}
        overlap = retval_locs.intersection(retptr_locs)
        if overlap:
            compiled.append("  ; Saving return pointer to U/V so it isn't overridden by return shuffle.")

            # We need to actually save the retptr to U/V.
            clobbers.add("U")
            clobbers.add("V")
            retptr_in_uv = True

            first_move = stack.find("builtin(retptr)")
            if first_move is None:
                raise Exception("Logic error, failed to get move amounts for builtin(retptr)!")

            # Generate code to move from our position to the first byte of the retval.
            compiled += generate_move_by("seeking builtin(retptr)", first_move, stack, clobbers, context)
            compiled.append("  LOAD U")
            compiled.append("  DECPC")

            stack.move(1)
            compiled += comment_stack(stack)

            compiled.append("  LOAD V")

        # Second, make sure the top of the stack is our return.
        top_spot = stack.at(0)
        if top_spot is not None and top_spot.name != "builtin(retval)":
            compiled.append("  ; Moving return value to correct location in stack.")

            # We need to use the A register to move the value, so it's clobbered now.
            clobbers.add("A")

            # We need to relocate the retptr to this spot.
            src_loc = stack.absfind("builtin(retval)")
            number_of_moves = stack.sizeof("builtin(retval)")

            if src_loc is None or number_of_moves is None:
                raise Exception("Logic error, failed to get move amounts for builtin(retval)!")

            # Generate code to move from our position to the first byte of the retptr.
            retptr_final_loc = number_of_moves
            compiled += generate_memcpy_unrolled(src_loc, 0, number_of_moves, stack, clobbers, context)

    # Now, move the return pointer if needed.
    if retptr_in_uv:
        compiled.append("  ; Restoring the return pointer from U/V to the correct location.")

        # Gotta grab it out of the saved U/V registers.
        restore_move_amt = retptr_final_loc - stack.location
        compiled += generate_move_by("seeking return pointer restoration point", restore_move_amt, stack, clobbers, context)
        compiled.append("  STORE U")
        compiled.append("  DECPC")

        stack.move(1)
        compiled += comment_stack(stack)

        compiled.append("  STORE V")
    else:
        retptr_abs = stack.absfind("builtin(retptr)")
        if retptr_abs is None:
            raise Exception("Logic error, failed to calculate the source location of builtin(retptr)!")

        if retptr_abs != retptr_final_loc:
            compiled.append("  ; Moving return pointer to correct location in stack.")

            # We need to use the A register to move the value, so it's clobbered now.
            clobbers.add("A")

            # We need to relocate the retptr to this spot.
            src_loc = stack.absfind("builtin(retptr)")
            number_of_moves = stack.sizeof("builtin(retptr)")

            if src_loc is None or number_of_moves is None:
                raise Exception("Logic error, failed to get move amounts for builtin(retptr)!")

            # Generate code to move from our position to the first byte of the retptr.
            compiled += generate_memcpy_unrolled(src_loc, retptr_final_loc, number_of_moves, stack, clobbers, context)

    # Now, pop all of our saved registers, and then return.
    if clobbers:
        compiled.append("  ; Restoring all clobbered registers.")
    while stack.size > 0:
        name = stack[-1].name
        if name[:13] == "builtin(saved":
            move_amt = stack.find(name)
            if move_amt is None:
                raise Exception(f"Logic error, failed to get move amounts for {name}!")

            compiled += generate_move_by(f"seeking {name}", move_amt, stack, clobbers, context)

            if name == "builtin(saved_a)":
                compiled.append("  POP A")
                stack.move(-1)
            elif name == "builtin(saved_u)":
                compiled.append("  POP U")
                stack.move(-1)
            elif name == "builtin(saved_v)":
                compiled.append("  POP V")
                stack.move(-1)
            elif name == "builtin(saved_spc)":
                compiled.append("  POP SPC")
                stack.move(-2)
            else:
                raise Exception(f"Logic error, unexpected saved type {name}!")

        stack.free(name)

    # Now, if we need to, move past any temporary values we didn't pop but don't care about.
    final_move_to_ret = stack.diff(retptr_final_loc + 1)
    compiled += generate_move_by("skipping past temporary locals", final_move_to_ret, stack, clobbers, context)
    compiled.append("  RET")

    return compiled


def generate_const_load(val: object, destination: str, stack: Stack, clobbers: Set[str], context: Context) -> List[str]:
    compiled: List[str] = []

    dtype = stack.typeof(destination)
    if dtype is None:
        raise Exception("Logic error, could not determine type of destination to load constant to!")

    if not isinstance(val, int):
        raise CompilerError("Unsupported non-integer constant load!", context)

    if dtype.is_unsigned and val < 0:
        raise CompilerError("Cannot use a negative value in an unsigned expression!", context)

    if destination in {"register(A)", "uregister(A)"}:
        compiled.append(f"  LOADI {_hex((val >> 0) & 0xFF, 2)}")
    else:
        clobbers.add("A")

        dest_loc = stack.find(destination)
        dest_size = stack.sizeof(destination)
        if dest_loc is None or dest_size is None:
            raise Exception("Logic error, cannot find destination to load constant to!")

        compiled += generate_move_by(f"seeking {destination}", dest_loc, stack, clobbers, context)
        if dest_size == 1:
            compiled.append(f"  LOADI {_hex((val >> 0) & 0xFF, 2)}")
            compiled.append("  STORE A")
        elif dest_size == 2:
            compiled.append(f"  LOADI {_hex((val >> 0) & 0xFF, 2)}")
            compiled.append("  STORE A")
            compiled.append("  DECPC")

            stack.move(1)
            compiled += comment_stack(stack)

            compiled.append(f"  LOADI {_hex((val >> 8) & 0xFF, 2)}")
            compiled.append("  STORE A")
        elif dest_size == 4:
            compiled.append(f"  LOADI {_hex((val >> 0) & 0xFF, 2)}")
            compiled.append("  STORE A")
            compiled.append("  DECPC")

            stack.move(1)
            compiled += comment_stack(stack)

            compiled.append(f"  LOADI {_hex((val >> 8) & 0xFF, 2)}")
            compiled.append("  STORE A")
            compiled.append("  DECPC")

            stack.move(1)
            compiled += comment_stack(stack)

            compiled.append(f"  LOADI {_hex((val >> 16) & 0xFF, 2)}")
            compiled.append("  STORE A")
            compiled.append("  DECPC")

            stack.move(1)
            compiled += comment_stack(stack)

            compiled.append(f"  LOADI {_hex((val >> 24) & 0xFF, 2)}")
            compiled.append("  STORE A")
        else:
            raise CompilerError(f"Unsupported destination {destination} for const load", context)

    return compiled


def get_function_prototype(
    call: cst.Call,
    stack: Stack,
    refs: List[Union[FunctionPrototype, GlobalVariable]],
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


def generate_function_call(
    call: cst.Call,
    destination: Optional[str],
    types: Dict[cst.CSTNode, CoreType],
    stack: Stack,
    clobbers: Set[str],
    refs: List[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> List[str]:
    compiled: List[str] = [context.comment()]
    function_prototype = get_function_prototype(call, stack, refs, local_consts, context)

    # Ensure that we're not trying to assign a void function call to an expression.
    if destination is not None and function_prototype.return_type is VoidType:
        raise CompilerError(f"Cannot assign result of function {call.func} returning void", context)

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
    param_count = 0
    for needed_arg in function_prototype.params:
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

    # Now, go through the requested parameters and set up the stack.
    copy_mapping: Dict[str, str] = {}
    out_mapping: Dict[int, str] = {}
    delayed_params: List[RegisterCoreType] = []
    delayed_args: List[cst.Arg] = []
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

        considered = args[:arglen]
        stackvars = stack[-arglen:]
        params = function_prototype.params[:arglen]

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
                if isinstance(stackvars[0], (PreservedCoreType, RegisterCoreType, PaddingCoreType)):
                    # Cannot make these match under any circumstances.
                    continue
                elif isinstance(stackvars[0], (InOutCoreType, OutCoreType)):
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

            match = False
            for i in range(arglen):
                if isinstance(stackvars[i], (RegisterCoreType, PaddingCoreType)):
                    # These can never match. We'd need to be even more clever with picking out
                    # register types from the middle of the argument list, and padding needs to
                    # be inserted in the stack at the right spot.
                    break
                elif isinstance(stackvars[i], OutCoreType):
                    # This is added to the stack, and I genuinely don't know what to do in this
                    # optimization case if this shows up here.
                    break
                elif isinstance(stackvars[i], (PreservedCoreType, InOutCoreType)):
                    # These are a match, since they either preserve the value, or replace it.
                    pass
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
                # Need to fix up where the stack is going to be on exit based on paramst that will
                # be "consumed" by the function call.
                for i in range(arglen):
                    if isinstance(params[i], (RegisterCoreType, PaddingCoreType, OutCoreType)):
                        raise Exception("Logic error, unexpected stackvar type!")
                    elif isinstance(params[i], PreservedCoreType):
                        continue
                    elif isinstance(params[i], InOutCoreType):
                        out_mapping[i] = stackvars[i].name
                        continue
                    else:
                        # The calling function is going to consume this.
                        stack_on_exit -= stackvars[i].size
                        normal_return_loc -= stackvars[i].size
                optimized_offset = arglen
                break

    which_arg: int = optimized_offset

    for rawpos, needed_arg in enumerate(function_prototype.params[optimized_offset:]):
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
            stack_on_exit += stack.alloc(StackVar(out_dest, needed_arg))
            temporary_stack_entries.append(out_dest)

        elif isinstance(needed_arg, RegisterCoreType):
            # Because we can't just do the calculation here since a subsequent arg expression calculation
            # might clobber one of the registers, we delay this so that we do this after everything else.
            delayed_params.append(needed_arg)
            delayed_args.append(args[which_arg])
            which_arg += 1

        elif isinstance(needed_arg, InOutCoreType):
            # Not only do we need to compute the input for this, but we need to copy the value back if the
            # input was a variable name or global variable reference, so we preserve in-out behavior.
            expr_dest = expr_temp_name()
            out_mapping[pos] = expr_dest

            arg_in_question = args[which_arg].value
            if isinstance(arg_in_question, cst.Name):
                copy_mapping[arg_in_question.value] = expr_dest
            stack_on_exit += stack.alloc(StackVar(expr_dest, needed_arg))
            temporary_stack_entries.append(expr_dest)
            compiled += generate_expr_internal(arg_in_question, expr_dest, types, stack, clobbers, refs, local_consts, context.wrap(arg_in_question))
            which_arg += 1

        elif isinstance(needed_arg, PreservedCoreType):
            # This is just preserved, so we don't have to worry about copy it out, but we do need to allocate it.
            expr_dest = expr_temp_name()
            stack_on_exit += stack.alloc(StackVar(expr_dest, needed_arg))
            temporary_stack_entries.append(expr_dest)
            compiled += generate_expr_internal(args[which_arg].value, expr_dest, types, stack, clobbers, refs, local_consts, context.wrap(args[which_arg].value))
            which_arg += 1

        else:
            # This is just a normal core type, so we put it on the stack, and the function takes it back off again.
            # So we don't need to fix up the stack any when we come back from the function call.
            expr_dest = expr_temp_name()
            stack.alloc(StackVar(expr_dest, needed_arg))
            temporary_stack_entries.append(expr_dest)
            compiled += generate_expr_internal(args[which_arg].value, expr_dest, types, stack, clobbers, refs, local_consts, context.wrap(args[which_arg].value))
            which_arg += 1

    # Now, load our registers up with any register parameters.
    for i in range(len(delayed_params)):
        reg_dest = expr_temp_name()
        needed_arg = delayed_params[i]
        provided_arg = delayed_args[i]

        # All functions that take a register core type assume signed integers.
        reg_to_type = {
            "A": "int8",
        }
        if needed_arg.type not in reg_to_type:
            raise Exception(f"Logic error, tried to assign a param to unsupported register {needed_arg.type} in function {function_prototype.name}")

        stack.alloc(StackVar(reg_dest, CoreType(reg_to_type[needed_arg.type])))
        compiled += generate_expr_internal(provided_arg.value, reg_dest, types, stack, clobbers, refs, local_consts, context.wrap(provided_arg.value))
        compiled += generate_move_to(reg_dest, stack, clobbers, context)
        compiled += f"POP {needed_arg.type}"
        stack.free(reg_dest)

    # Now, we're ready to actually call the function. Move to the last byte of the last parameter on the stack.
    move_amount = stack.diff(stack.size - 1)
    compiled += generate_move_by("moving to last parameter", move_amount, stack, clobbers, context)
    compiled.append(f"  CALL {function_prototype.name}")

    # Now, calculate the true position of the stack after calling the function, so future manipulations of
    # the stack know where we really are. It's important to do this here because some return cleanup bits
    # below end up using the location of the stack.
    if not isinstance(function_prototype.return_type, (RegisterCoreType, ParamReturnCoreType)):
        # We need to understand where we actually are on the stack, so add to the
        # location where the return would have been put on the stack.
        stack_on_exit += function_prototype.return_type.size

    stack.location = stack_on_exit
    compiled += comment_stack(stack)

    # Track whether we captured the return value or not.
    return_handled = False

    # Now, if the return type is a register type, put it in the destination.
    if isinstance(function_prototype.return_type, RegisterCoreType):
        return_handled = True
        if destination is not None:
            if destination in {"register(A)", "uregister(A)"}:
                # We're already returning to a register, so we're done here!
                if function_prototype.return_type.type != "A":
                    raise Exception(f"Logic error, unsupported register destination {function_prototype.return_type.type} for function")
            else:
                compiled += generate_move_to(destination, stack, clobbers, context)
                if function_prototype.return_type.type == "A":
                    compiled.append("  STORE A")
                else:
                    raise Exception(f"Logic error, unsupported register destination {function_prototype.return_type.type} for function")

    # Now, do some bookkeeping, first copying anything that we need to copy that was an in-out param.
    for dst, src in copy_mapping.items():
        source_loc = stack.absfind(src)
        source_size = stack.sizeof(src)
        dest_loc = stack.absfind(dst)
        dest_size = stack.sizeof(dst)
        if source_loc is None or source_size is None:
            raise Exception(f"Logic error, Undefined variable reference to {src!r}", context)
        if dest_loc is None or dest_size is None:
            raise Exception("Logic error, cannot find destination to copy variable value to!")

        if source_size == dest_size:
            compiled += generate_memcpy_unrolled(source_loc, dest_loc, dest_size, stack, clobbers, context)
        else:
            raise CompilerError("Unsupported byref assignment from different variable sizes", context)

    # Now, if the return is in one of the parameters, copy that to our destination.
    if isinstance(function_prototype.return_type, ParamReturnCoreType):
        return_handled = True
        if destination is not None:
            src = out_mapping[function_prototype.return_type.position]
            dst = destination

            source_loc = stack.absfind(src)
            source_size = stack.sizeof(src)
            dest_loc = stack.absfind(dst)
            dest_size = stack.sizeof(dst)
            if source_loc is None or source_size is None:
                raise Exception(f"Logic error, undefined variable reference to {src!r}", context)
            if dest_loc is None or dest_size is None:
                raise Exception("Logic error, cannot find destination to copy variable value to!")

            if source_size == dest_size:
                compiled += generate_memcpy_unrolled(source_loc, dest_loc, dest_size, stack, clobbers, context)
            else:
                raise CompilerError("Unsupported function return from different variable sizes", context)

    # Now, fix up our view of the stack.
    for entry in reversed(temporary_stack_entries):
        stack.free(entry)

    # Now, if needed, copy the return value from the stack to its location.
    if (not return_handled) and (not (function_prototype.return_type is VoidType)):
        if destination is not None:
            if destination in {"register(A)", "uregister(A)"}:
                # Pop the value from the stack, instead of copying.
                src_loc = normal_return_loc
                src_size = function_prototype.return_type.size
                if src_size != 1:
                    raise Exception(f"Logic error, trying to assign value of size {src_size} to A register")

                move_amt = stack.diff(src_loc)
                compiled += generate_move_by("seeking return location", move_amt, stack, clobbers, context)
                compiled.append("  LOAD A")
            else:
                src_loc = normal_return_loc
                src_size = function_prototype.return_type.size
                dest_loc = stack.absfind(destination)
                dest_size = stack.sizeof(destination)
                if dest_loc is None or dest_size is None:
                    raise Exception(f"Logic error, cannot find destination {destination} to copy variable value to!")

                if src_size == dest_size:
                    compiled += generate_memcpy_unrolled(src_loc, dest_loc, dest_size, stack, clobbers, context)
                else:
                    raise CompilerError("Unsupported function return from different variable sizes", context)

    return compiled


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


def expr_integer_type(size: int) -> CoreType:
    if size == 1:
        return CoreType("int8")
    elif size == 2:
        return CoreType("int16")
    elif size == 4:
        return CoreType("int32")
    else:
        raise Exception("Logic error, unrecognized integer size!")


def generate_variable_lookup(
    source: str,
    destination: str,
    stack: Stack,
    clobbers: Set[str],
    refs: List[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> List[str]:
    compiled: List[str] = []

    # TODO: This needs to support looking up global variables, for any variable that is defined globally and
    # then locally marked with the "global" keyword.

    if destination in {"register(A)", "uregister(A)"}:
        # Just need to load A with the value, which should always be the lowest 8 bits of any variable.
        if stack.absfind(source) is None:
            raise CompilerError(f"Undefined variable reference to {source!r}", context)
        compiled += generate_move_to(source, stack, clobbers, context)
        compiled.append("  LOAD A")
    else:
        source_loc = stack.absfind(source)
        source_size = stack.sizeof(source)
        dest_loc = stack.absfind(destination)
        dest_size = stack.sizeof(destination)
        if source_loc is None or source_size is None:
            raise CompilerError(f"Undefined variable reference to {source!r}", context)
        if dest_loc is None or dest_size is None:
            raise Exception("Logic error, cannot find destination to copy variable value to!")

        if source_size == dest_size:
            # Direct copy from source stack to destination stack.
            compiled += generate_memcpy_unrolled(source_loc, dest_loc, dest_size, stack, clobbers, context)
        elif source_size > dest_size:
            # Copy, but with the destination size in mind, which should grab only the lower bits of the source.
            compiled += generate_memcpy_unrolled(source_loc, dest_loc, dest_size, stack, clobbers, context)
        else:
            # We need to sign extend the top bit of the top byte for negative numbers, which requires the A register.
            clobbers.add("A")

            # First, go to the high byte and figure out if it needs to be zero or one extended.
            move_amt = stack.diff(source_loc + (source_size - 1))
            compiled += generate_move_by("seeking {source}", move_amt, stack, clobbers, context)
            compiled.append("  LOAD A")
            compiled.append("  SHL")

            set_branch = local_label_name("top_bit_set")
            extend_branch = local_label_name("sign_extend")

            compiled.append(f"  JRIC {set_branch}")
            compiled.append("  LOADI 0")
            compiled.append(f"  JRI {extend_branch}")
            compiled.append(f"{set_branch}:")
            compiled.append("  LOADI -1")
            compiled.append(f"{extend_branch}:")

            for pos in range(dest_size - source_size):
                actual_pos = pos + dest_loc + source_size

                move_amt = stack.diff(actual_pos)
                compiled += generate_move_by("seeking sign extend byte", move_amt, stack, clobbers, context)
                compiled.append("  STORE A")

            # Need to copy the whole thing, and then zero out the top bytes we didn't touch.
            compiled += generate_memcpy_unrolled(source_loc, dest_loc, source_size, stack, clobbers, context)

    return compiled


def generate_unary_expr(
    expression: cst.UnaryOperation,
    destination: str,
    types: Dict[cst.CSTNode, CoreType],
    stack: Stack,
    clobbers: Set[str],
    refs: List[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> List[str]:
    compiled: List[str] = []

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
            if destination in {"register(A)", "uregister(A)"} or stack[-1].name != destination:
                # In order to ensure that it's possible to negate this value, locate the rest of the expression
                # in a temporary location.
                internal_dest = expr_temp_name()
                stack.alloc(StackVar(internal_dest, expr_integer_type(destination_size)))
            else:
                # Safe to put the expression evaluation in our destination because we're just going to negate it.
                internal_dest = destination

            compiled += generate_expr_internal(expression.expression, internal_dest, types, stack, clobbers, refs, local_consts, context.wrap(expression.expression))

            # Negation clobbers the A register, since it is the accumulator.
            clobbers.add("A")

            # Move to the parameter and negate it.
            compiled += generate_move_to(internal_dest, stack, clobbers, context)
            compiled.append("  LOAD A")

            if isinstance(expression.operator, cst.Minus):
                compiled.append("  NEG")
            elif isinstance(expression.operator, cst.BitInvert):
                compiled.append("  INV")
            else:
                raise CompilerError("Unsupported unary operation {expression}", context)

            # This call puts the result in a, so check if that's what we want.
            if destination in {"register(A)", "uregister(A)"}:
                stack.free(internal_dest)
            else:
                compiled += generate_move_to(destination, stack, clobbers, context)
                compiled.append("  STORE A")
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

            compiled += generate_expr_internal(expression.expression, internal_dest, types, stack, clobbers, refs, local_consts, context.wrap(expression.expression))

            if isinstance(expression.operator, cst.Minus):
                # Using the neg16 or neg32 function that's part of our stdlib.
                function = "neg16" if destination_size == 2 else "neg32"
                compiled += generate_function_call(
                    create_call(
                        function,
                        [UnvalidatedName(internal_dest)],
                    ),
                    destination,
                    types,
                    stack,
                    clobbers,
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
                    compiled.append("  LOAD A")
                    compiled.append("  INV")
                    compiled += generate_move_to(destination, stack, clobbers, context, offset=actual_neg_offset(offset))
                    compiled.append("  STORE A")

            else:
                raise CompilerError("Unsupported unary operation {expression}", context)

            if internal_dest != destination:
                stack.free(internal_dest)

        else:
            # We don't support negation of this type.
            raise CompilerError("Cannot negate expression with destination size {destination_size}", context)

    else:
        # TODO: Handle Plus (no-op, just call with the expression value), and Not, for booleans.
        raise CompilerError(f"Unsupported unary operation {expression}", context)

    return compiled


def generate_binary_expr(
    expression: cst.BinaryOperation,
    destination: str,
    types: Dict[cst.CSTNode, CoreType],
    stack: Stack,
    clobbers: Set[str],
    refs: List[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> List[str]:
    compiled: List[str] = []

    destination_size = stack.sizeof(destination)
    if destination_size is None:
        raise Exception("Logic error, could not calculate size of destination!")
    destination_type = stack.typeof(destination)
    if destination_type is None:
        raise Exception("Logic error, could not calculate type of destination!")

    if destination in {"register(A)", "uregister(A)"} or stack[-1].name != destination:
        # In order to ensure that it's possible to do stack math on this value, locate it in
        # a temporary location for the time being if the destination isn't the top of the stack.
        lhs_dest = expr_temp_name()
        stack.alloc(StackVar(lhs_dest, expr_integer_type(destination_size)))
    else:
        # Safe to put first parameter in the top of the stack where it already is useful for math.
        lhs_dest = destination

    compiled += generate_expr_internal(expression.left, lhs_dest, types, stack, clobbers, refs, local_consts, context.wrap(expression.left))

    # Now, get the second parameter onto the stack in the right spot.
    rhs_dest = expr_temp_name()
    stack.alloc(StackVar(rhs_dest, expr_integer_type(destination_size)))
    compiled += generate_expr_internal(expression.right, rhs_dest, types, stack, clobbers, refs, local_consts, context.wrap(expression.right))

    # Now, perform some math of matics!
    if destination_size == 1:
        if isinstance(expression.operator, cst.Subtract):
            if not destination_type.is_integer:
                raise CompilerError(f"Unsupported type {destination_type.type} for integer expression!", context)

            if destination not in {"register(A)", "uregister(A)"}:
                # Subtracting clobbers the A register, since it is the accumulator.
                clobbers.add("A")

            # Move to the second parameter and negate it.
            compiled += generate_move_to(rhs_dest, stack, clobbers, context)
            compiled.append("  LOAD A")
            compiled.append("  NEG")

            # Move to the right spot on the stack to add to the negated right hand side.
            compiled += generate_move_to(lhs_dest, stack, clobbers, context)
            compiled.append("  ADD")

        elif isinstance(expression.operator, (cst.Add, cst.BitAnd, cst.BitOr, cst.BitXor)):
            if not destination_type.is_integer:
                raise CompilerError(f"Unsupported type {destination_type.type} for integer expression!", context)

            if destination not in {"register(A)", "uregister(A)"}:
                # Adding clobbers the A register, since it is the accumulator.
                clobbers.add("A")

            # Move to the right spot on the stack and then add the two numbers.
            compiled += generate_move_to(rhs_dest, stack, clobbers, context)
            compiled.append("  LOAD A")
            compiled += generate_move_to(lhs_dest, stack, clobbers, context)

            if isinstance(expression.operator, cst.Add):
                compiled.append("  ADD")
            elif isinstance(expression.operator, cst.BitAnd):
                compiled.append("  AND")
            elif isinstance(expression.operator, cst.BitOr):
                compiled.append("  OR")
            elif isinstance(expression.operator, cst.BitXor):
                compiled.append("  XOR")
            else:
                raise Exception("Logic error, unexpected operator {expression.operator)}")

        elif isinstance(expression.operator, cst.Multiply):
            if not destination_type.is_integer:
                raise CompilerError(f"Unsupported type {destination_type.type} for integer expression!", context)

            # If we ever fix our argument overlapping in the function call, we should see
            # surprising optimization here with no need to copy parameters around.
            compiled += generate_function_call(
                create_call(
                    "mult",
                    [UnvalidatedName(lhs_dest), UnvalidatedName(rhs_dest)]
                ),
                destination,
                types,
                stack,
                clobbers,
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
            compiled += generate_function_call(
                create_call(
                    "udiv",
                    [UnvalidatedName(lhs_dest), UnvalidatedName(rhs_dest)]
                ),
                None,
                types,
                stack,
                clobbers,
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
            compiled.append("  LOAD A")

        else:
            # TODO: Support other operators such as multiply/divide/modulo.
            raise CompilerError(f"Unsupported run-time computation for {expression.operator}!", context)

        # This call puts the result in a, so check if that's what we want.
        if destination in {"register(A)", "uregister(A)"}:
            # Just make sure we bookkeep things. Both the LHS and RHS need to be unwound.
            stack.free(rhs_dest)
            stack.free(lhs_dest)
        else:
            stack.free(rhs_dest)
            compiled += generate_move_to(destination, stack, clobbers, context)
            compiled.append("  STORE A")
            if lhs_dest != destination:
                stack.free(lhs_dest)

    else:
        if isinstance(expression.operator, cst.Subtract):
            if not destination_type.is_integer:
                raise CompilerError(f"Unsupported type {destination_type.type} for integer expression!", context)

            # Using the neg16 or neg32 fnction that's part of our stdlib.
            negfunc = "neg16" if destination_size == 2 else "neg32"
            compiled += generate_function_call(
                create_call(
                    negfunc,
                    [UnvalidatedName(rhs_dest)],
                ),
                rhs_dest,
                types,
                stack,
                clobbers,
                refs,
                local_consts,
                context.wrap(expression.right, extra="-"),
            )

            # Using the add16 or add32 function that's part of our stdlib.
            addfunc = "add16" if destination_size == 2 else "add32"

            # If we ever fix our argument overlapping in the function call, we should see
            # surprising optimization here with no need to copy parameters around.
            compiled += generate_function_call(
                create_call(
                    addfunc,
                    [UnvalidatedName(lhs_dest), UnvalidatedName(rhs_dest)],
                ),
                destination,
                types,
                stack,
                clobbers,
                refs,
                local_consts,
                context.wrap(expression),
            )

            stack.free(rhs_dest)
            if lhs_dest != destination:
                stack.free(lhs_dest)

        elif isinstance(expression.operator, (cst.Add, cst.Multiply)):
            if not destination_type.is_integer:
                raise CompilerError(f"Unsupported type {destination_type.type} for integer expression!", context)

            if isinstance(expression.operator, cst.Add):
                # Using the add16 or add32 function that's part of our stdlib.
                function = "add16" if destination_size == 2 else "add32"
            elif isinstance(expression.operator, cst.Multiply):
                # Using the mult16 or mult32 function that's part of our stdlib.
                function = "mult16" if destination_size == 2 else "mult32"
            else:
                raise Exception("Logic error, unexpected operator {expression.operator)}")

            # If we ever fix our argument overlapping in the function call, we should see
            # surprising optimization here with no need to copy parameters around.
            compiled += generate_function_call(
                create_call(
                    function,
                    [UnvalidatedName(lhs_dest), UnvalidatedName(rhs_dest)]
                ),
                destination,
                types,
                stack,
                clobbers,
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
            compiled += generate_function_call(
                create_call(
                    function,
                    [UnvalidatedName(lhs_dest), UnvalidatedName(rhs_dest)]
                ),
                None,
                types,
                stack,
                clobbers,
                refs,
                local_consts,
                context.wrap(expression),
            )

            location = rhs_dest if isinstance(expression.operator, cst.Modulo) else lhs_dest
            if location != destination:
                if stack_is_at(location, stack, offset=destination_size - 1):
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
                    compiled += generate_move_to(location, stack, clobbers, context, offset=actual_expr_offset(offset))
                    compiled.append("  LOAD A")
                    compiled += generate_move_to(destination, stack, clobbers, context, offset=actual_expr_offset(offset))
                    compiled.append("  STORE A")

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
                compiled.append("  LOAD A")
                compiled += generate_move_to(lhs_dest, stack, clobbers, context, offset=actual_expr_offset(offset))
                compiled.append(function)
                compiled += generate_move_to(destination, stack, clobbers, context, offset=actual_expr_offset(offset))
                compiled.append("  STORE A")

            stack.free(rhs_dest)
            if lhs_dest != destination:
                stack.free(lhs_dest)

        else:
            # TODO: Support other operators such as multiply/divide/modulo.
            raise CompilerError(f"Unsupported run-time computation for {expression.operator}!", context)

    return compiled


def generate_expr_internal(
    expression: cst.BaseExpression,
    destination: str,
    types: Dict[cst.CSTNode, CoreType],
    stack: Stack,
    clobbers: Set[str],
    refs: List[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> List[str]:
    compiled: List[str] = []

    destination_size = stack.sizeof(destination)
    if destination_size is None:
        raise Exception("Logic error, could not calculate size of destination!")

    try:
        # If we can evaluate this directly, do so!
        value = codegen_eval(expression, local_consts)
        if isinstance(value, int):
            compiled += generate_const_load(value, destination, stack, clobbers, context)
            return compiled

    except NonConstantExpressionException:
        # We must treat this as a non-unrolled expression.
        pass

    if isinstance(expression, cst.Name):
        compiled += generate_variable_lookup(expression.value, destination, stack, clobbers, refs, local_consts, context)

    elif isinstance(expression, cst.UnaryOperation):
        compiled += generate_unary_expr(expression, destination, types, stack, clobbers, refs, local_consts, context)

    elif isinstance(expression, cst.BinaryOperation):
        compiled += generate_binary_expr(expression, destination, types, stack, clobbers, refs, local_consts, context)

    elif isinstance(expression, cst.Call):
        compiled += generate_function_call(expression, destination, types, stack, clobbers, refs, local_consts, context.wrap(expression))

    else:
        # TODO: What other expression types are we missing? Probably array and memory operations.
        # TODO: Looks like also string/character assignments and such, and everything with string manipulation.
        raise CompilerError(f"Unsupported expression type {expression} in expression compiler!", context)

    return compiled


def infer_expr_types(
    expression: cst.BaseExpression,
    stack: Stack,
    refs: List[Union[FunctionPrototype, GlobalVariable]],
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

        raise CompilerError(f"Undefined variable reference to {expression.value!r}", context)

    elif isinstance(expression, cst.Integer):
        inferred[expression] = CoreType("int32")
        return inferred

    elif isinstance(expression, cst.UnaryOperation):
        inferred.update(infer_expr_types(expression.expression, stack, refs, local_consts, context.wrap(expression.expression)))
        inferred_type = inferred[expression.expression]
        inferred[expression] = CoreType(inferred_type.type, inferred_type.pointed_type, inferred_type.const, inferred_type.return_padding)

        if isinstance(expression.operator, (cst.Minus, cst.BitInvert)):
            if not inferred_type.is_integer:
                raise CompilerError(f"Unsupported unary operation for type {inferred_type.type}", context)
        return inferred

    elif isinstance(expression, cst.BinaryOperation):
        inferred.update(infer_expr_types(expression.left, stack, refs, local_consts, context.wrap(expression.left)))
        inferred.update(infer_expr_types(expression.right, stack, refs, local_consts, context.wrap(expression.right)))

        left_inferred = inferred[expression.left]
        right_inferred = inferred[expression.right]

        if isinstance(expression.operator, (cst.Add, cst.Subtract, cst.BitAnd, cst.BitOr, cst.BitXor, cst.Multiply, cst.Divide, cst.FloorDivide, cst.Modulo)):
            if not left_inferred.is_integer:
                raise CompilerError(f"Unsupported binary operation for type {left_inferred.type}", context)
            if not right_inferred.is_integer:
                raise CompilerError(f"Unsupported binary operation for type {right_inferred.type}", context)

            # Any math against two integers will result in an integer. Pick the wider of two types.
            if left_inferred.size > right_inferred.size:
                picked = left_inferred
            else:
                picked = right_inferred
            inferred[expression] = CoreType(picked.type, picked.pointed_type, picked.const, picked.return_padding)

        return inferred

    elif isinstance(expression, cst.Call):
        function_prototype = get_function_prototype(expression, stack, refs, local_consts, context)
        inferred[expression] = function_prototype.return_type
        return inferred

    else:
        raise CompilerError(f"Unsupported expression type {expression} in type inferencer!", context)


def generate_expr(
    expression: cst.BaseExpression,
    destination: str,
    stack: Stack,
    clobbers: Set[str],
    refs: List[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    context: Context,
) -> List[str]:
    compiled: List[str] = [context.comment()]

    dsize = stack.sizeof(destination)
    dtype = stack.typeof(destination)
    if dsize is None:
        raise Exception("Logic error, couldn't determine size of expression destination!")
    if dtype is None:
        raise Exception("Logic error, couldn't determine type of expression destination!")

    types: Dict[cst.CSTNode, CoreType] = infer_expr_types(expression, stack, refs, local_consts, context)

    if dsize == 1:
        # We can potentially keep the math in the A register!
        clobbers.add("A")

        compiled += generate_expr_internal(expression, "uregister(A)" if dtype.is_unsigned else "register(A)", types, stack, clobbers, refs, local_consts, context)
        compiled += generate_move_to(destination, stack, clobbers, context)
        compiled.append("  STORE A")
    else:
        # Just do stack-based operations.
        compiled += generate_expr_internal(expression, destination, types, stack, clobbers, refs, local_consts, context)

    return compiled


def local_variable(
    assign_target: cst.BaseExpression,
    assign_annotation: Optional[cst.Annotation],
    assign_value: Optional[cst.BaseExpression],
    stack: Stack,
    clobbers: Set[str],
    refs: List[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    local_data: List[str],
    context: Context,
) -> List[str]:
    compiled: List[str] = [context.comment()]

    # TODO: We need to support globals as well, not sure if in here, but somewhere, as long as they aren't constants.

    if not isinstance(assign_target, cst.Name):
        # TODO: This is where we would handle memory writes and arrays.
        raise CompilerError("Unsupported name for local variable definition", context)

    assign_name = assign_target.value
    assign_type = get_type(assign_annotation.annotation) if assign_annotation is not None else None

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

        if not assign_type.return_padding:
            raise CompilerError("Unsupported nopad attribute for local variable definition", context)

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

        if assign_type is not None and assign_type.const:
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

        compiled += generate_expr(assign_value, assign_name, stack, clobbers, refs, local_consts, context.wrap(assign_value))

    return compiled


def compile_chunk(
    chunk: cst.BaseSuite,
    stack: Stack,
    clobbers: Set[str],
    function_type: CoreType,
    refs: List[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[Constant],
    local_data: List[str],
    context: Context,
) -> List[str]:
    compiled: List[str] = []

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

                        compiled += generate_expr(simple_statement.value, "builtin(retval)", stack, clobbers, refs, local_consts, context.wrap(simple_statement.value))
                        compiled += generate_return(function_type, stack, clobbers, context.wrap(simple_statement))
                elif isinstance(simple_statement, cst.AnnAssign):
                    compiled += local_variable(
                        simple_statement.target,
                        simple_statement.annotation,
                        simple_statement.value,
                        stack,
                        clobbers,
                        refs,
                        local_consts,
                        local_data,
                        context.wrap(simple_statement),
                    )
                elif isinstance(simple_statement, cst.Assign):
                    if len(simple_statement.targets) != 1:
                        raise CompilerError("Unsupported multi-variable assignment", context.wrap(simple_statement))

                    compiled += local_variable(
                        simple_statement.targets[0].target,
                        None,
                        simple_statement.value,
                        stack,
                        clobbers,
                        refs,
                        local_consts,
                        local_data,
                        context.wrap(simple_statement),
                    )
                else:
                    # TODO: Assignment expressions, function calls, memory assignments.
                    raise CompilerError(f"Unsupported node to compile {simple_statement}", context)
        else:
            # TODO: Control flow statements, etc.
            raise CompilerError(f"Unsupported node to compile {statement}", context)

    return compiled


def function_prototype(func: cst.FunctionDef, context: Context) -> FunctionPrototype:
    function_type = get_type(func.returns)
    function_params = func.params.params

    if function_type is None:
        raise CompilerError("Unsupported return type for function definition", context)

    if func.params.kwonly_params or func.params.posonly_params:
        raise CompilerError("Unsupported parameter definition for function definition", context)

    prototype = FunctionPrototype(func.name.value, function_type)
    stack: Stack = Stack()

    for func_param in function_params:
        if func_param.default is not None:
            # TODO: This wouldn't be terrible to support at some point in the future, so maybe we could?
            raise CompilerError(f"Function parameter {func_param.name.value} has unsupported default", context)

        # Function parameters are passed on the stack, so we must know their locations and types.
        param_type = get_type(func_param.annotation)
        if param_type is None:
            raise CompilerError(f"Expecting type for function parameter {func_param.name.value}", context)

        prototype.params.append(param_type)
        stack.alloc(StackVar(func_param.name.value, param_type))

    if function_type.return_padding and stack.size < function_type.size:
        # We need to request padding out to the return size.
        prototype.params.append(PaddingCoreType(function_type.size - stack.size))

    return prototype


def function(func: cst.FunctionDef, refs: List[Union[FunctionPrototype, GlobalVariable]], context: Context) -> List[str]:
    compiled: List[str] = []
    function_name = func.name.value
    function_type = get_type(func.returns)
    function_params = func.params.params
    stack: Stack = Stack()
    local_data: List[str] = []

    if function_type is None:
        raise CompilerError("Unsupported return type for function definition", context)

    if func.params.kwonly_params or func.params.posonly_params:
        raise CompilerError("Unsupported parameter definition for function definition", context)

    for func_param in function_params:
        if func_param.default is not None:
            raise CompilerError(f"Function parameter {func_param.name.value} has unsupported default", context)

        # Function parameters are passed on the stack, so we must know their locations and types.
        param_type = get_type(func_param.annotation)
        if param_type is None:
            raise CompilerError(f"Expecting type for function parameter {func_param.name.value}", context)

        try:
            stack.alloc(StackVar(func_param.name.value, param_type))
        except NotImplementedError:
            raise CompilerError(f"Unsupported type for function parameter {func_param.name.value}", context)

    if function_type.return_padding and stack.size < function_type.size:
        # We need to account for return type padding.
        for _ in range(function_type.size - stack.size):
            stack.alloc(StackVar("builtin(padding)", CoreType('int8')))

    # Need a spot on the stack for our return pointer that is placed when called.
    stack.alloc(StackVar("builtin(retptr)", CoreType("pointer", CoreType("void"))))
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
    fake_stack: Stack = Stack()
    if function_type is not VoidType:
        fake_stack.alloc(StackVar("builtin(retval)", function_type))
    fake_stack.alloc(StackVar("builtin(retptr)", CoreType("pointer", CoreType("void"))))
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

    # First pass to figure out clobbers
    clobbers: Set[str] = set()
    compile_chunk(func.body, stack.clone(), clobbers, function_type, refs, [], [], context)

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
    compiled += comment_stack(stack)

    if padding_move_amt > 0:
        compiled.append(f"  SUBPCI {padding_move_amt}" + comment_source("allocating padding"))
        stack.move(padding_move_amt)
        compiled += comment_stack(stack)

    # Now, let's save all of our clobbered values.
    if clobbers:
        compiled.append("  ; Save clobbered registers")
    for clobber in sorted(clobbers):
        if clobber == "A":
            stack.alloc(StackVar("builtin(saved_a)", CoreType("uint8")))
            compiled.append("  PUSH A")
            stack.move(1)
            compiled += comment_stack(stack)
        elif clobber == "U":
            stack.alloc(StackVar("builtin(saved_u)", CoreType("uint8")))
            compiled.append("  PUSH U")
            stack.move(1)
            compiled += comment_stack(stack)
        elif clobber == "V":
            stack.alloc(StackVar("builtin(saved_v)", CoreType("uint8")))
            compiled.append("  PUSH V")
            stack.move(1)
            compiled += comment_stack(stack)
        elif clobber == "SPC":
            stack.alloc(StackVar("builtin(saved_spc)", CoreType("uint8")))
            compiled.append("  PUSH SPC")
            stack.move(2)
            compiled += comment_stack(stack)
        else:
            raise Exception(f"Logic error, unexpected clobber {clobber}!")

    # Make sure that we have room on the stack for the return value. Don't move at this point
    # because we might not want to generate instructions to move.
    if function_type is not VoidType:
        stack.alloc(StackVar("builtin(retval)", function_type))

    # Now, second pass to actually compile.
    compiled += compile_chunk(func.body, stack, set(), function_type, refs, [], local_data, context)

    # TODO: Function boundary is where we will end up optimizing redundant stack moves and load/store operations.

    return [
        *local_data,
        f"{function_name}:",
        *preamble,
        *compiled,
    ]


def is_type_definition(assign: cst.Assign) -> bool:
    if len(assign.targets) != 1:
        return False

    target = assign.targets[0]
    if not isinstance(target.target, cst.Name):
        return False

    if target.target.value not in {"uint8", "int8", "uint16", "int16", "uint32", "int32", "pointer", "string"}:
        return False

    if not isinstance(assign.value, cst.Name):
        return False

    if assign.value.value not in {"int", "str"}:
        return False

    return True


def compile_module(module: str, code: str, refs: List[Union[FunctionPrototype, GlobalVariable]]) -> List[str]:
    parsed_module = cst.parse_module(code)

    # Make sure we have access to line/column numbers for errors.
    wrapper = cst.MetadataWrapper(parsed_module)
    metadata = wrapper.resolve(meta.PositionProvider)

    # A deep copy is made by the metadata wrapper, because LibCST is designed around safe mutations. We don't care
    # and only need a read-only copy.
    parsed_module = wrapper.module

    compiled: List[str] = []
    global_consts: List[Constant] = []

    for statement in parsed_module.body:
        context = Context(module, statement, metadata)

        if isinstance(statement, cst.SimpleStatementLine):
            bodylines = statement.body
            if len(bodylines) != 1:
                raise CompilerError("Multi-statement lines are not supported", context)

            body = bodylines[0]
            if isinstance(body, cst.Assign):
                # This could be a mypy type assignment so that the python source files can be typechecked.
                if not is_type_definition(body):
                    raise CompilerError("Global variable declarations must have a type", context)
            elif isinstance(body, cst.AnnAssign):
                compiled += generate_global_variable(body, global_consts, context)
            else:
                raise CompilerError("Arbitrary top-level statements are not supported", context)
        elif isinstance(statement, cst.FunctionDef):
            compiled += function(statement, refs, context)
        else:
            # TODO: What other statement types are we missing here?
            raise CompilerError("Unsupported statement {statement}", context)

        compiled.append("")

    while compiled and compiled[-1] == "":
        compiled = compiled[:-1]

    return compiled


def parse_forward_refs(module: str, code: str) -> List[Union[FunctionPrototype, GlobalVariable]]:
    # TODO: This needs to scan for global variables so we have global type references as well.

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

    return prototypes


def parse_and_compile_module(module: str, code: str) -> List[str]:
    forward_refs: List[Union[FunctionPrototype, GlobalVariable]] = builtin_forward_refs()
    forward_refs += parse_forward_refs(module, code)
    return compile_module(module, code, forward_refs)


def builtin_forward_refs() -> List[Union[FunctionPrototype, GlobalVariable]]:
    prototypes: List[Union[FunctionPrototype, GlobalVariable]] = [
        # STDLIB string functions.
        FunctionPrototype("strcat", VoidType, [PreservedCoreType("string"), PreservedCoreType("string")]),
        FunctionPrototype("strcmp", RegisterCoreType("A"), [PreservedCoreType("string"), PreservedCoreType("string")]),
        FunctionPrototype("strcpy", VoidType, [PreservedCoreType("string"), PreservedCoreType("string")]),
        FunctionPrototype("strlen", RegisterCoreType("A"), [PreservedCoreType("string")]),

        # STDLIB string/integer conversion functions.
        FunctionPrototype("atoi", RegisterCoreType("A"), [InOutCoreType("string")]),
        FunctionPrototype("atoi16", ParamReturnCoreType(1), [InOutCoreType("string"), OutCoreType("int16")]),
        FunctionPrototype("atoi32", ParamReturnCoreType(1), [InOutCoreType("string"), OutCoreType("int32")]),
        FunctionPrototype("itoa", VoidType, [RegisterCoreType("A"), PreservedCoreType("string")]),
        FunctionPrototype("itoa16", VoidType, [PreservedCoreType("int16"), PreservedCoreType("string")]),
        FunctionPrototype("itoa32", VoidType, [PreservedCoreType("int32"), PreservedCoreType("string")]),

        # STDLIB integer math functions.
        FunctionPrototype("abs", RegisterCoreType("A"), [RegisterCoreType("A")]),
        FunctionPrototype("abs16", ParamReturnCoreType(0), [InOutCoreType("int16")]),
        FunctionPrototype("abs32", ParamReturnCoreType(0), [InOutCoreType("int32")]),
        FunctionPrototype("neg", RegisterCoreType("A"), [PreservedCoreType("int8")]),
        FunctionPrototype("neg16", ParamReturnCoreType(0), [InOutCoreType("int16")]),
        FunctionPrototype("neg32", ParamReturnCoreType(0), [InOutCoreType("int32")]),
        FunctionPrototype("add", RegisterCoreType("A"), [PreservedCoreType("int8"), PreservedCoreType("int8")]),
        FunctionPrototype("add16", CoreType("int16"), [CoreType("int16"), CoreType("int16")]),
        FunctionPrototype("add32", CoreType("int32"), [CoreType("int32"), CoreType("int32")]),
        FunctionPrototype("mult", RegisterCoreType("A"), [PreservedCoreType("int8"), PreservedCoreType("int8")]),
        FunctionPrototype("mult16", CoreType("int16"), [CoreType("int16"), CoreType("int16")]),
        FunctionPrototype("mult32", CoreType("int32"), [CoreType("int32"), CoreType("int32")]),
        FunctionPrototype("udiv", VoidType, [InOutCoreType("int8"), InOutCoreType("int8")]),
        FunctionPrototype("udiv16", VoidType, [InOutCoreType("int16"), InOutCoreType("int16")]),
        FunctionPrototype("udiv32", VoidType, [InOutCoreType("int32"), InOutCoreType("int32")]),

        # STDLIB integer comparison functions.
        FunctionPrototype("ucmp", RegisterCoreType("A"), [InOutCoreType("int8"), InOutCoreType("int8")]),
        FunctionPrototype("ucmp16", RegisterCoreType("A"), [InOutCoreType("int16"), InOutCoreType("int16")]),
        FunctionPrototype("ucmp32", RegisterCoreType("A"), [InOutCoreType("int32"), InOutCoreType("int32")]),
        FunctionPrototype("umin", RegisterCoreType("A"), [InOutCoreType("int8"), InOutCoreType("int8")]),
        FunctionPrototype("umin16", CoreType("int16"), [CoreType("int16"), CoreType("int16")]),
        FunctionPrototype("umin32", CoreType("int32"), [CoreType("int32"), CoreType("int32")]),
        FunctionPrototype("umax", RegisterCoreType("A"), [InOutCoreType("int8"), InOutCoreType("int8")]),
        FunctionPrototype("umax16", CoreType("int16"), [CoreType("int16"), CoreType("int16")]),
        FunctionPrototype("umax32", CoreType("int32"), [CoreType("int32"), CoreType("int32")]),
    ]

    return prototypes
