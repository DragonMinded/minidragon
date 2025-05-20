import libcst as cst
import libcst.metadata as meta

from typing import Dict, List, Mapping, Optional, Set, Union


class Context:
    def __init__(self, module: str, node: cst.CSTNode, meta: Mapping[cst.CSTNode, meta.CodeRange]) -> None:
        self.module = module
        self.node = node
        self.meta = meta

    def wrap(self, node: cst.CSTNode) -> "Context":
        return Context(self.module, node, self.meta)

    def comment(self) -> str:
        fresh_module = cst.parse_module("")
        code = fresh_module.code_for_node(self.node)
        while code[-1] == "\n":
            code = code[:-1]
        return f"  ; {self.module} line {self.meta[self.node].start.line}: " + code


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

    def __init__(self, base_type: str, const: bool = False, return_padding: bool = True) -> None:
        # TODO: Need to allow pointers to have a base type of the memory location pointed at.
        self.type = base_type
        self.const = const
        self.return_padding = return_padding

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.type == other
        if isinstance(other, CoreType):
            return self.type == other.type
        return False

    def __repr__(self) -> str:
        pre = ""
        post = ""
        if self.const:
            pre = "const[" + pre
            post = post + "]"
        if not self.return_padding:
            pre = "nopad[" + pre
            post = post + "]"

        return pre + self.type + post

    @property
    def size(self) -> int:
        if self.type == "None":
            return 0
        if self.type == "int8":
            return 1
        if self.type == "int16":
            return 2
        if self.type == "int32":
            return 4
        if self.type == "char":
            return 1
        # Strings are passed by reference pointer.
        if self.type == "string":
            return 2
        # Pointers are 16 bit due to CPU arch.
        if self.type == "pointer":
            return 2
        raise NotImplementedError(f"Type {self.type} not implemented!")


NoneType = CoreType("None", True, False)


class PreservedCoreType(CoreType):
    """
    A function call parmeter type that implies the called function will not clean this reference
    off of the stack, but instead that the stack will still contain this value upon return from
    the function. This does not imply that the values change, only that the values are not removed
    from the stack upon function call.
    """
    def __init__(self, base_type: str) -> None:
        super().__init__(base_type, True)


class InOutCoreType(CoreType):
    """
    A function call parameter type that implies the value is not just referenced when calling
    the function, but also that the function updates this value and it should be copied back
    to any calling code's variable references if needed.
    """

    def __init__(self, base_type: str) -> None:
        super().__init__(base_type, False)


class OutCoreType(CoreType):
    """
    A function call parameter type that implies that the called function places an output parameter
    here, but that the caller does not need to specify a value for calling. This should be paired
    with a ParamReturnCoreType as the function return to specify that this is where to find the
    output value.
    """

    def __init__(self, base_type: str) -> None:
        super().__init__(base_type, False)


class RegisterCoreType(CoreType):
    """
    A function call parameter type that implies that the called function requests its input or
    places its output in a particular register instead of on the stack.
    """

    def __init__(self, register: str) -> None:
        super().__init__(register, False)


class ParamReturnCoreType(CoreType):
    """
    A function call return parameter that works in tandem with OutCoreType to specify which out
    argument contains the result of the function call.
    """

    def __init__(self, position: int) -> None:
        super().__init__("position: " + str(position), False)

    @property
    def position(self) -> int:
        return int(self.type[10:])


class PaddingCoreType(CoreType):
    """
    A function call parameter that does not need to be provided by the code itself, but instead
    implies that the called function needs a certain amount of padding in the stack before calling.
    """

    def __init__(self, padbytes: int) -> None:
        super().__init__("padding: " + str(padbytes), False)

    @property
    def padbytes(self) -> int:
        return int(self.type[9:])


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

        elif isinstance(expr, cst.Name):
            if expr.value == "None":
                return NoneType
            else:
                return CoreType(expr.value, const, not nopad)

        else:
            return None


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
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"Global variable {self.name!r}"


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
        for entry in self.stack:
            if entry.name == name:
                return entry.size
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


def codegen_eval(expr: cst.BaseExpression) -> object:
    fresh_module = cst.parse_module("")
    code = fresh_module.code_for_node(
        cst.SimpleStatementLine(
            body=[
                cst.Expr(value=expr),
            ],
        )
    )
    return eval(code)


def _hex(val: int, pad: int) -> str:
    hexval = hex(val)[2:]
    while len(hexval) < pad:
        hexval = "0" + hexval

    return "0x" + hexval


def global_variable(assign: cst.AnnAssign, context: Context) -> List[str]:
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
        value = codegen_eval(assign_value)
        compiled.append(f"{assign_name}:")

        if assign_type == "int8":
            if not isinstance(value, int):
                raise CompilerError("Unsupported initialization value for global const definition", context)
            if value < -128 or value > 255:
                raise CompilerError("Initialization out of bounds", context)

            value = value & 0xFF
            compiled.append(f"  .byte {_hex((value >> 0) & 0xFF, 2)}")
        elif assign_type == "int16":
            if not isinstance(value, int):
                raise CompilerError("Unsupported initialization value for global const definition", context)
            if value < -32768 or value > 65535:
                raise CompilerError("Initialization out of bounds", context)

            value = value & 0xFFFF
            compiled.append(f"  .byte {_hex((value >> 8) & 0xFF, 2)}")
            compiled.append(f"  .byte {_hex((value >> 0) & 0xFF, 2)}")
        elif assign_type == "int32":
            if not isinstance(value, int):
                raise CompilerError("Unsupported initialization value for global const definition", context)
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

    else:
        # TODO: Support allocating variables in main RAM instead of constants in ROM.
        raise CompilerError("Unsupported type for global variable definition", context)
    return compiled


def generate_move_by(move_amt: int, stack: Stack, clobbers: Set[str], context: Context) -> List[str]:
    compiled: List[str] = []
    if move_amt > 0:
        compiled.append(f"  SUBPCI {move_amt}")
    elif move_amt < 0:
        compiled.append(f"  ADDPCI {-move_amt}")
    stack.move(move_amt)
    return compiled


def generate_move_to(destination: str, stack: Stack, clobbers: Set[str], context: Context) -> List[str]:
    move_amt = stack.find(destination)
    if move_amt is None:
        raise Exception(f"Logic error, could not find {destination} on stack to move to!")
    return generate_move_by(move_amt, stack, clobbers, context)


def generate_memcpy_unrolled(src_loc: int, dst_loc: int, size: int, stack: Stack, clobbers: Set[str], context: Context) -> List[str]:
    compiled: List[str] = []

    from_rel = stack.diff(src_loc)
    compiled += generate_move_by(from_rel, stack, clobbers, context)
    shuffle_amount = stack.location - dst_loc
    if shuffle_amount == 0:
        return compiled

    if shuffle_amount < 0:
        for i in range(size):
            compiled.append("  LOAD A")
            compiled.append(f"  SUBPCI {-shuffle_amount}")
            compiled.append("  STORE A")

            if i < size - 1:
                compiled.append(f"  ADDPCI {(-shuffle_amount) - 1}")

        stack.move((-shuffle_amount) + (size - 1))
    else:
        for i in range(size):
            compiled.append("  LOAD A")
            compiled.append(f"  ADDPCI {shuffle_amount}")
            compiled.append("  STORE A")

            if i < size - 1:
                compiled.append(f"  SUBPCI {shuffle_amount + 1}")

        stack.move(-(shuffle_amount - (size - 1)))
    return compiled


def generate_return(function_type: CoreType, stack: Stack, clobbers: Set[str], context: Context) -> List[str]:
    compiled: List[str] = [context.comment()]

    # Because we could have more than one return, make sure we clone the stack to not mess with the rest of the function.
    stack = stack.clone()

    # We need to ensure that our stack only contains the return value and the return pointer.
    # Make sure to move the return value, the return pointer, and then pop all of our saved builtins.
    retptr_in_uv = False
    retptr_final_loc = 0
    if function_type is not NoneType:
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
            compiled += generate_move_by(first_move, stack, clobbers, context)
            compiled.append("  LOAD U")
            compiled.append("  DECPC")
            compiled.append("  LOAD V")
            stack.move(1)

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
        compiled += generate_move_by(restore_move_amt, stack, clobbers, context)
        compiled.append("  STORE U")
        compiled.append("  DECPC")
        compiled.append("  STORE V")
        stack.move(1)
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
        name = stack.stack[-1].name
        if name[:13] == "builtin(saved":
            move_amt = stack.find(name)
            if move_amt is None:
                raise Exception(f"Logic error, failed to get move amounts for {name}!")

            compiled += generate_move_by(move_amt, stack, clobbers, context)

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
    compiled += generate_move_by(final_move_to_ret, stack, clobbers, context)
    compiled.append("  RET")

    return compiled


def generate_const_load(val: int, destination: str, stack: Stack, clobbers: Set[str], context: Context) -> List[str]:
    compiled: List[str] = []

    if destination == "register(A)":
        compiled.append(f"  LOADI {_hex((val >> 0) & 0xFF, 2)}")
    else:
        dest_loc = stack.find(destination)
        dest_size = stack.sizeof(destination)
        if dest_loc is None or dest_size is None:
            raise Exception("Logic error, cannot find destination to load constant to!")

        compiled += generate_move_by(dest_loc, stack, clobbers, context)
        if dest_size == 1:
            compiled.append(f"  LOADI {_hex((val >> 0) & 0xFF, 2)}")
            compiled.append("  STORE A")
        elif dest_size == 2:
            compiled.append(f"  LOADI {_hex((val >> 8) & 0xFF, 2)}")
            compiled.append("  STORE A")
            compiled.append("  DECPC")
            compiled.append(f"  LOADI {_hex((val >> 0) & 0xFF, 2)}")
            compiled.append("  STORE A")
            stack.move(1)
        elif dest_size == 4:
            compiled.append(f"  LOADI {_hex((val >> 24) & 0xFF, 2)}")
            compiled.append("  STORE A")
            compiled.append("  DECPC")
            compiled.append(f"  LOADI {_hex((val >> 16) & 0xFF, 2)}")
            compiled.append("  STORE A")
            compiled.append("  DECPC")
            compiled.append(f"  LOADI {_hex((val >> 8) & 0xFF, 2)}")
            compiled.append("  STORE A")
            compiled.append("  DECPC")
            compiled.append(f"  LOADI {_hex((val >> 0) & 0xFF, 2)}")
            compiled.append("  STORE A")
            stack.move(3)
        else:
            raise CompilerError(f"Unsupported destination {destination} for const load", context)

    return compiled


def generate_function_call(
    call: cst.Call,
    destination: str,
    stack: Stack,
    clobbers: Set[str],
    refs: List[Union[FunctionPrototype, GlobalVariable]],
    context: Context,
) -> List[str]:
    compiled: List[str] = [context.comment()]

    function_prototype: Optional[FunctionPrototype] = None

    if isinstance(call.func, cst.Name):
        # Simple reference to a function on the refs list. If it isn't in the refs list, then it could be
        # a function pointer which needs to be supported but is not for now.
        func_ref = call.func.value
        for ref in refs:
            if isinstance(ref, FunctionPrototype) and ref.name == func_ref:
                function_prototype = ref
                break
        else:
            raise CompilerError(f"Unknown function {func_ref} in call", context)

    else:
        # TODO: Support function pointers here at some point. Maybe even objects or structs?
        raise CompilerError(f"Unsupported function call with expression node {call.func}", context)

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
        raise CompilerError(f"Function call to {func_ref} expects {param_count} args but {len(args)} were given", context)

    # Now, go through the requested parameters and set up the stack.
    copy_mapping: Dict[str, str] = {}
    out_mapping: Dict[int, str] = {}
    delayed_params: List[RegisterCoreType] = []
    delayed_args: List[cst.Arg] = []
    temporary_stack_entries: List[str] = []
    which_arg: int = 0
    stack_on_exit: int = stack.size - 1
    normal_return_loc: int = stack.size

    for pos, needed_arg in enumerate(function_prototype.params):
        # Special case for if the return location is already the top of the stack, and our first parameter is an out
        # parameter, so we can skip copying the value after calling the function.
        if pos == 0 and stack.stack[-1].name == destination:
            stack_type = stack.stack[-1]

            if isinstance(needed_arg, OutCoreType) and isinstance(function_prototype.return_type, ParamReturnCoreType):
                # We need to allocate space on the stack for the return value, but that's already our function call
                # destination, so it's already allocated. Make sure the sizes match so we don't have to do anything else.
                if function_prototype.return_type.position == pos and needed_arg.type == stack_type.type:
                    continue

        # Special case for if the first argument is already the top of the stack, and it's a preserved or in-out
        # argument. In this case, we don't have to do anything, because the function will do what it should do with
        # that stack location. In theory we should be able to do this with as many elements on the stack as possible
        # for in-out and preserved params but that's a lot of work to think through so we're not doing it for now.
        if pos == 0 and args and isinstance(args[0].value, cst.Name):
            stack_type = stack.stack[-1]

            if stack_type.name == args[0].value.value:
                if isinstance(needed_arg, PreservedCoreType):
                    # We have an argument that is preserved as-is, so we don't have to worry about making a temporary
                    # copy on the stack. So, do nothing with it.
                    if needed_arg.type == stack_type.type:
                        continue

                if isinstance(needed_arg, InOutCoreType):
                    # We have an argument that gets modified by the function, but it's already on the top of the stack,
                    # so no need to do nothing with it.
                    if needed_arg.type == stack_type.type:
                        out_mapping[pos] = stack_type.name
                        continue

        if isinstance(needed_arg, ParamReturnCoreType):
            raise Exception(f"Logic error, not expecting a return-only type for param {pos + 1} in {func_ref}")

        elif isinstance(needed_arg, PaddingCoreType):
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
            compiled += generate_expr_internal(arg_in_question, expr_dest, stack, clobbers, refs, context.wrap(arg_in_question))
            which_arg += 1

        elif isinstance(needed_arg, PreservedCoreType):
            # This is just preserved, so we don't have to worry about copy it out, but we do need to allocate it.
            expr_dest = expr_temp_name()
            stack_on_exit += stack.alloc(StackVar(expr_dest, needed_arg))
            temporary_stack_entries.append(expr_dest)
            compiled += generate_expr_internal(args[which_arg].value, expr_dest, stack, clobbers, refs, context.wrap(args[which_arg].value))
            which_arg += 1

        else:
            # This is just a normal core type, so we put it on the stack, and the function takes it back off again.
            # So we don't need to fix up the stack any when we come back from the function call.
            expr_dest = expr_temp_name()
            stack.alloc(StackVar(expr_dest, needed_arg))
            temporary_stack_entries.append(expr_dest)
            compiled += generate_expr_internal(args[which_arg].value, expr_dest, stack, clobbers, refs, context.wrap(args[which_arg].value))
            which_arg += 1

    # Now, load our registers up with any register parameters.
    for i in range(len(delayed_params)):
        reg_dest = expr_temp_name()
        needed_arg = delayed_params[i]
        provided_arg = delayed_args[i]

        reg_to_type = {
            "A": "int8",
        }
        if needed_arg.type not in reg_to_type:
            raise Exception(f"Logic error, tried to assign a param to unsupported register {needed_arg.type} in function {func_ref}")

        stack.alloc(StackVar(reg_dest, CoreType(reg_to_type[needed_arg.type])))
        compiled += generate_expr_internal(provided_arg.value, reg_dest, stack, clobbers, refs, context.wrap(provided_arg.value))
        compiled += generate_move_to(reg_dest, stack, clobbers, context)
        compiled += f"POP {needed_arg.type}"
        stack.free(reg_dest)

    # Now, we're ready to actually call the function. Move to the last byte of the last parameter on the stack.
    move_amount = stack.diff(stack.size - 1)
    compiled += generate_move_by(move_amount, stack, clobbers, context)
    compiled.append(f"  CALL {func_ref}")

    # Track whether we captured the return value or not.
    return_handled = False

    # Now, if the return type is a register type, put it in the destination.
    if isinstance(function_prototype.return_type, RegisterCoreType):
        return_handled = True
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
    if (not return_handled) and (not (function_prototype.return_type is NoneType)):
        # We need to understand where we actually are on the stack, so add to the
        # location where this would have been put on the stack.
        stack_on_exit += function_prototype.return_type.size
        stack.location = stack_on_exit

        if destination == "register(A)":
            # Pop the value from the stack, instead of copying.
            src_loc = normal_return_loc
            src_size = function_prototype.return_type.size
            if src_size != 1:
                raise Exception(f"Logic error, trying to assign value of size {src_size} to A register")

            move_amt = stack.diff(src_loc)
            compiled += generate_move_by(move_amt, stack, clobbers, context)
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
    else:
        # Finally, calculate the true position of the stack after calling the function, so future
        # manipulations of the stack know where we really are.
        # when we were called.
        stack.location = stack_on_exit

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
    context: Context,
) -> List[str]:
    compiled: List[str] = []

    # TODO: This needs to support looking up global variables, for any variable that is defined globally and
    # then locally marked with the "global" keyword.

    if destination == "register(A)":
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
            compiled += generate_move_by(move_amt, stack, clobbers, context)
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
                compiled += generate_move_by(move_amt, stack, clobbers, context)
                compiled.append("  STORE A")

            # Need to copy the whole thing, and then zero out the top bytes we didn't touch.
            compiled += generate_memcpy_unrolled(source_loc, dest_loc, source_size, stack, clobbers, context)

    return compiled


def generate_expr_internal(
    expression: cst.BaseExpression,
    destination: str,
    stack: Stack,
    clobbers: Set[str],
    refs: List[Union[FunctionPrototype, GlobalVariable]],
    context: Context,
) -> List[str]:
    compiled: List[str] = []

    destination_size = 1 if destination == "register(A)" else stack.sizeof(destination)
    if destination_size is None:
        raise Exception("Logic error, could not calculate size of destination!")

    if isinstance(expression, cst.Integer):
        compiled += generate_const_load(int(expression.value), destination, stack, clobbers, context)

    elif isinstance(expression, cst.Name):
        compiled += generate_variable_lookup(expression.value, destination, stack, clobbers, refs, context)

    elif isinstance(expression, cst.UnaryOperation):
        if isinstance(expression.operator, cst.Minus):
            if isinstance(expression.expression, cst.Integer):
                # Special case for negative integers.
                intval = -int(expression.expression.value)
                compiled += generate_const_load(intval, destination, stack, clobbers, context)
            else:
                # TODO: Need to negate the expression.
                raise CompilerError("Unsupported negation operator", context)
        else:
            # TODO: What other expressions are there, NOT perhaps?
            raise CompilerError(f"Unsupported unary operation {expression}", context)

    elif isinstance(expression, cst.BinaryOperation):
        # Special case for operating on two constants. We could do full evalulation, but meh.
        if isinstance(expression.left, cst.Integer) and isinstance(expression.right, cst.Integer):
            if isinstance(expression.operator, cst.Add):
                intval = int(expression.left.value) + int(expression.right.value)
                compiled += generate_const_load(intval, destination, stack, clobbers, context)
            elif isinstance(expression.operator, cst.Subtract):
                intval = int(expression.left.value) - int(expression.right.value)
                compiled += generate_const_load(intval, destination, stack, clobbers, context)
            else:
                # TODO: Support other operators than add/subtract.
                raise CompilerError(f"Unsupported compile-time computation for {expression.operator}!", context)

        if destination == "register(A)" or stack.stack[-1].name != destination:
            # In order to ensure that it's possible to do stack math on this value, locate it in
            # a temporary location for the time being if the destination isn't the top of the stack.
            lhs_dest = expr_temp_name()
            stack.alloc(StackVar(lhs_dest, expr_integer_type(destination_size)))
        else:
            # Safe to put first parameter in the top of the stack where it already is useful for math.
            lhs_dest = destination

        compiled += generate_expr_internal(expression.left, lhs_dest, stack, clobbers, refs, context.wrap(expression.left))

        # Now, get the second parameter onto the stack in the right spot.
        rhs_dest = expr_temp_name()
        stack.alloc(StackVar(rhs_dest, expr_integer_type(destination_size)))
        compiled += generate_expr_internal(expression.right, rhs_dest, stack, clobbers, refs, context.wrap(expression.right))

        # Now, perform some math of matics!
        if destination_size == 1:
            if isinstance(expression.operator, cst.Add):
                # The stdlib for add clobbers the A register
                clobbers.add("A")

                # Move to the right spot on the stack to call the add function, then call it.
                compiled += generate_move_to(rhs_dest, stack, clobbers, context)
                compiled.append("  CALL add")

                # This function puts the result in a, so check if that's what we want.
                if destination == "register(A)":
                    # Just make sure we bookkeep things. Both the LHS and RHS need to be unwound.
                    stack.free(rhs_dest)
                    stack.free(lhs_dest)
                else:
                    stack.free(rhs_dest)
                    compiled += generate_move_to(destination, stack, clobbers, context)
                    compiled.append("  STORE A")
                    if lhs_dest != destination:
                        stack.free(lhs_dest)
            elif isinstance(expression.operator, cst.Subtract):
                # The stdlib for add clobbers the A register. We also clobber by negating the second param.
                clobbers.add("A")

                # Move to the second parameter.
                compiled += generate_move_to(rhs_dest, stack, clobbers, context)
                compiled.append("  LOAD A")
                compiled.append("  NEG")
                compiled.append("  STORE A")

                # Move to the right spot on the stack to call the add function, then call it.
                compiled += generate_move_to(rhs_dest, stack, clobbers, context)
                compiled.append("  CALL add")

                # This function puts the result in a, so check if that's what we want.
                if destination == "register(A)":
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
                # TODO: Support other operators than add/subtract.
                raise CompilerError(f"Unsupported run-time computation for {expression.operator}!", context)

        else:
            # TODO: Support other bit sizes than 8.
            raise CompilerError("Unsupported addition size!", context)

    elif isinstance(expression, cst.Call):
        compiled += generate_function_call(expression, destination, stack, clobbers, refs, context.wrap(expression))

    else:
        # TODO: What other expression types are we missing? Probably function calls and memory read operations.
        # TODO: Looks like also string/character assignments and such.
        raise CompilerError(f"Unsupported expression type {expression} in expression compiler!", context)

    return compiled


def generate_expr(
    expression: cst.BaseExpression,
    destination: str,
    stack: Stack,
    clobbers: Set[str],
    refs: List[Union[FunctionPrototype, GlobalVariable]],
    context: Context
) -> List[str]:
    compiled: List[str] = [context.comment()]

    size = stack.sizeof(destination)
    if size == 1:
        # We can potentially keep the math in the A register!
        clobbers.add("A")

        compiled += generate_expr_internal(expression, "register(A)", stack, clobbers, refs, context)
        compiled += generate_move_to(destination, stack, clobbers, context)
        compiled.append("  STORE A")
    else:
        # Just do stack-based operations.
        compiled += generate_expr_internal(expression, destination, stack, clobbers, refs, context)

    return compiled


def local_variable(
    assign_target: cst.BaseExpression,
    assign_annotation: Optional[cst.Annotation],
    assign_value: Optional[cst.BaseExpression],
    stack: Stack,
    clobbers: Set[str],
    refs: List[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[str],
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

    if orig_loc is None:
        # For definitions, we need a type. For constants, we need an initial value.
        if assign_type is None:
            raise CompilerError("Unsupported type for local variable definition", context)

        if assign_type.const and assign_value is None:
            raise CompilerError("Expecting initialization value for local const definition", context)

        if not assign_type.return_padding:
            raise CompilerError("Unsupported nopad attribute for local variable definition", context)

        # Allocate space on the stack for this local variable.
        stack.alloc(StackVar(assign_name, assign_type))
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

        compiled += generate_expr(assign_value, assign_name, stack, clobbers, refs, context.wrap(assign_value))

    return compiled


def compile_chunk(
    chunk: cst.BaseSuite,
    stack: Stack,
    clobbers: Set[str],
    function_type: CoreType,
    refs: List[Union[FunctionPrototype, GlobalVariable]],
    local_consts: List[str],
    context: Context,
) -> List[str]:
    compiled: List[str] = []

    for statement in chunk.body:
        if isinstance(statement, cst.SimpleStatementLine):
            for simple_statement in statement.body:
                if isinstance(simple_statement, cst.Return):
                    if simple_statement.value is None:
                        # Simple return by itself, doesn't update the retval.
                        if function_type is not NoneType:
                            raise CompilerError("Returning nothing from a function marked with a return value", context)
                        compiled += generate_return(function_type, stack, clobbers, context.wrap(simple_statement))
                    else:
                        # Return of some sort of expression.
                        if function_type is NoneType:
                            raise CompilerError("Returning something from a function marked with no return value", context)

                        compiled += generate_expr(simple_statement.value, "builtin(retval)", stack, clobbers, refs, context.wrap(simple_statement.value))
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
    local_consts: List[str] = []

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
    stack.alloc(StackVar("builtin(retptr)", CoreType("pointer")))
    stack.location = stack.size - 1

    # Generate before and after call stack documentation.
    preamble: List[str] = []
    if stack.size > 0:
        preamble.append("  ; Stack layout just after call:")
    prevals: List[str] = []
    for entry in stack.stack:
        for i in range(entry.size):
            if entry.location is None:
                raise Exception("Logic error, expected stack entry to have location!")
            prevals.append(f"  ; PC + {stack.size - (entry.location + i + 1)} - {entry.name}")
    preamble += reversed(prevals)
    if preamble:
        preamble.append("  ;")

    preamble.append("  ; Stack layout just before return:")
    fake_stack: Stack = Stack()
    if function_type is not NoneType:
        fake_stack.alloc(StackVar("builtin(retval)", function_type))
    fake_stack.alloc(StackVar("builtin(retptr)", CoreType("pointer")))
    prevals = []
    for entry in fake_stack.stack:
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
    if function_type is not NoneType:
        temp_size = stack.alloc(StackVar("builtin(retval)", function_type))
        stack.move(temp_size)

    # First pass to figure out clobbers
    clobbers: Set[str] = set()
    compile_chunk(func.body, stack.clone(), clobbers, function_type, refs, [], context)

    # Unwind our temporary return value location.
    if temp_size > 0:
        if stack.stack[-1].name != "builtin(retval)":
            raise Exception("Logic error, top of stack isn't the retval temporary!")
        stack.move(-temp_size)
        stack.free("builtin(retval)")

    # Stick some padding between the retval and the saved retptr if we need to so
    # unwinding on return doesn't clobber part of the stack.
    padding_move_amt = 0
    while stack.size < (function_type.size + 2):
        stack.alloc(StackVar("builtin(padding)", CoreType('int8')))
        padding_move_amt += 1

    if padding_move_amt > 0:
        compiled.append(f"  SUBPCI {padding_move_amt}")
        stack.move(padding_move_amt)

    # Now, let's save all of our clobbered values.
    if clobbers:
        compiled.append("  ; Save clobbered registers")
    for clobber in sorted(clobbers):
        if clobber == "A":
            stack.alloc(StackVar("builtin(saved_a)", CoreType("int8")))
            compiled.append("  PUSH A")
            stack.move(1)
        elif clobber == "U":
            stack.alloc(StackVar("builtin(saved_u)", CoreType("int8")))
            compiled.append("  PUSH U")
            stack.move(1)
        elif clobber == "V":
            stack.alloc(StackVar("builtin(saved_v)", CoreType("int8")))
            compiled.append("  PUSH V")
            stack.move(1)
        elif clobber == "SPC":
            stack.alloc(StackVar("builtin(saved_spc)", CoreType("int8")))
            compiled.append("  PUSH SPC")
            stack.move(2)
        else:
            raise Exception(f"Logic error, unexpected clobber {clobber}!")

    # Make sure that we have room on the stack for the return value. Don't move at this point
    # because we might not want to generate instructions to move.
    if function_type is not NoneType:
        stack.alloc(StackVar("builtin(retval)", function_type))

    # Now, second pass to actually compile.
    compiled += compile_chunk(func.body, stack, set(), function_type, refs, local_consts, context)

    # TODO: Function boundary is where we will end up optimizing redundant stack moves and load/store operations.

    return [
        *local_consts,
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

    if target.target.value not in {"int8", "int16", "int32", "pointer", "string"}:
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
                compiled += global_variable(body, context)
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
    # TODO: This needs renaming and to also scan for globals so we have global types as well.

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
        FunctionPrototype("strcat", NoneType, [PreservedCoreType("string"), PreservedCoreType("string")]),
        FunctionPrototype("strcmp", RegisterCoreType("A"), [PreservedCoreType("string"), PreservedCoreType("string")]),
        FunctionPrototype("strcpy", NoneType, [PreservedCoreType("string"), PreservedCoreType("string")]),
        FunctionPrototype("strlen", RegisterCoreType("A"), [PreservedCoreType("string")]),

        # STDLIB string/integer conversion functions.
        FunctionPrototype("atoi", RegisterCoreType("A"), [InOutCoreType("string")]),
        FunctionPrototype("atoi16", ParamReturnCoreType(1), [InOutCoreType("string"), OutCoreType("int16")]),
        FunctionPrototype("atoi32", ParamReturnCoreType(1), [InOutCoreType("string"), OutCoreType("int32")]),
        FunctionPrototype("itoa", NoneType, [RegisterCoreType("A"), PreservedCoreType("string")]),
        FunctionPrototype("itoa16", NoneType, [PreservedCoreType("int16"), PreservedCoreType("string")]),
        FunctionPrototype("itoa32", NoneType, [PreservedCoreType("int32"), PreservedCoreType("string")]),

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

        # STDLIB integer comparison functions.
    ]

    # The following are special cases since we will be bridging to them when compiling
    # math expressions. They're kept here for posterity.
    [
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
