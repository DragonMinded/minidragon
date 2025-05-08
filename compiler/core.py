import libcst as cst
import libcst.metadata as meta

from typing import List, Mapping, Optional, Set


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
        return f"  ; {self.module} line {self.meta[self.node].start.line}: " + code


class CompilerError(Exception):
    def __init__(self, error: str, context: Context) -> None:
        metaval = context.meta[context.node]
        super().__init__(f"{context.module} line {metaval.start.line}: " + error)
        self.module = context.module
        self.line = metaval.start.line


class CoreType:
    def __init__(self, base_type: str, const: bool = False, return_padding: bool = True) -> None:
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


class InOutCoreType(CoreType):
    def __init__(self, base_type: str) -> None:
        super().__init__(base_type, False)


class OutCoreType(CoreType):
    def __init__(self, base_type: str) -> None:
        super().__init__(base_type, False)


class RegisterCoreType(CoreType):
    def __init__(self, register: str) -> None:
        super().__init__(register, False)


class ParamReturnCoreType(CoreType):
    def __init__(self, position: int) -> None:
        super().__init__("position: " + str(position), False)

    @property
    def position(self) -> int:
        return int(self.type[10:])


class PaddingCoreType(CoreType):
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


class StackVar:
    def __init__(self, name: str, vartype: CoreType, location: Optional[int] = None) -> None:
        self.name = name
        self.type = vartype
        self.location = location

    @property
    def size(self) -> int:
        return self.type.size

    def __repr__(self) -> str:
        return f"{self.type.type} {self.name}: {self.location} size {self.size}"


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

    def at(self, offset: int) -> Optional[str]:
        for entry in self.stack:
            if entry.location == offset:
                # Found it, return the variable we're at.
                return entry.name
        return None

    @property
    def current(self) -> Optional[str]:
        for entry in self.stack:
            if entry.location == self.location:
                # Found it, return the variable we're at.
                return entry.name
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
                cst.Expr(value = expr),
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
    compiled: List[str] = []
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
            compiled.append(f"  .byte 0x00")
        else:
            raise CompilerError("Unsupported type for global variable definition", context)

    else:
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
    compiled: List[str] = []
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

        stack.move((-shuffle_amount) - (size - 1))
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
            clobbers.add("u")
            clobbers.add("v")
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
        if top_spot != "builtin(retval)":
            compiled.append("  ; Moving return value to correct location in stack.")

            # We need to use the A register to move the value, so it's clobbered now.
            clobbers.add("a")

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
            clobbers.add("a")

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
                compiled.append(f"  POP A")
                stack.move(-1)
            elif name == "builtin(saved_u)":
                compiled.append(f"  POP U")
                stack.move(-1)
            elif name == "builtin(saved_v)":
                compiled.append(f"  POP V")
                stack.move(-1)
            elif name == "builtin(saved_spc)":
                compiled.append(f"  POP SPC")
                stack.move(-2)
            else:
                raise Exception(f"Logic error, unexpected saved type {name}!")

        stack.free(name)

    compiled.append(f"  RET")
    return compiled


def generate_const_load(val: int, destination: str, stack: Stack, clobbers: Set[str], context: Context) -> List[str]:
    compiled: List[str] = []

    if destination == "a":
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


__expr_global_count: int = 0


def expr_temp_name() -> str:
    global __expr_global_count
    __expr_global_count += 1
    return f"builtin(expr_temp_{__expr_global_count})"


def expr_integer_type(size: int) -> CoreType:
    if size == 1:
        return CoreType("int8")
    elif size == 2:
        return CoreType("int16")
    elif size == 4:
        return CoreType("int32")
    else:
        raise Exception("Logic error, unrecognized integer size!")


def generate_expr_internal(expression: cst.BaseExpression, destination: str, stack: Stack, clobbers: Set[str], context: Context) -> List[str]:
    compiled: List[str] = []

    destination_size = 1 if destination == "a" else stack.sizeof(destination)
    if destination_size == None:
        raise Exception("Logic error, could not calculate size of destination!")

    if isinstance(expression, cst.Integer):
        intval = int(expression.value)
        compiled += generate_const_load(intval, destination, stack, clobbers, context)

    elif isinstance(expression, cst.Name):
        source = expression.value
        if source != destination:
            if destination == "a":
                # Just need to load A with the value.
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
                if source_size != dest_size:
                    raise CompilerError(f"Unsupported assignment from different variable sizes", context)

                compiled += generate_memcpy_unrolled(source_loc, dest_loc, dest_size, stack, clobbers, context)

    elif isinstance(expression, cst.UnaryOperation):
        if isinstance(expression.operator, cst.Minus):
            if isinstance(expression.expression, cst.Integer):
                # Special case for negative integers.
                intval = -int(expression.expression.value)
                compiled += generate_const_load(intval, destination, stack, clobbers, context)
            else:
                # Need to negate the expression.
                raise CompilerError(f"Unsupported negation operator", context)
        else:
            raise CompilerError(f"Unsupported unary operation {expression}", context)

    elif isinstance(expression, cst.BinaryOperation):
        # Special case for operating on two constants. We could do full evalulation, but meh.
        if isinstance(expression.left, cst.Integer) and isinstance(expression.right, cst.Integer):
            if isinstance(expression.operator, cst.Add):
                intval = int(expression.left.value) + int(expression.right.value)
                compiled += generate_const_load(intval, destination, stack, clobbers, context)
            else:
                raise CompilerError(f"Unsupported compile-time computation for {expression.operator}!", context)

        if destination == "a" or stack.stack[-1].name != destination:
            # In order to ensure that it's possible to do stack math on this value, locate it in
            # a temporary location for the time being if the destination isn't the top of the stack.
            lhs_dest = expr_temp_name()
            stack.alloc(StackVar(lhs_dest, expr_integer_type(destination_size)))
        else:
            # Safe to put first parameter in the top of the stack where it already is useful for math.
            lhs_dest = destination

        compiled += generate_expr_internal(expression.left, lhs_dest, stack, clobbers, context.wrap(expression.left))

        # Now, get the second parameter onto the stack in the right spot.
        rhs_dest = expr_temp_name()
        stack.alloc(StackVar(rhs_dest, expr_integer_type(destination_size)))
        compiled += generate_expr_internal(expression.right, rhs_dest, stack, clobbers, context.wrap(expression.right))

        # Move to the right spot on the stack to math ourselves up.
        amount = stack.diff(stack.size - 1)

        # Now, perform some math of matics!
        if destination_size == 1:
            if isinstance(expression.operator, cst.Add):
                clobbers.add("a")
                compiled += generate_move_by(amount, stack, clobbers, context)
                compiled.append("  CALL add")
            else:
                raise CompilerError(f"Unsupported run-time computation for {expression.operator}!", context)

            # This function puts the result in a, so check if that's what we want.
            if destination == "a":
                # Just make sure we bookkeep things. Both the LHS and RHS need to be unwound.
                stack.free(rhs_dest)
                stack.free(lhs_dest)
            else:
                stack.free(rhs_dest)
                if lhs_dest != destination:
                    # Need to shuffle this parameter into the destination.
                    src_loc = stack.absfind(lhs_dest)
                    dst_loc = stack.absfind(destination)
                    if src_loc is None or dst_loc is None:
                        raise Exception("Logic error, could not find source or destination move location!")

                    compiled += generate_memcpy_unrolled(src_loc, dst_loc, 1, stack, clobbers, context)
                    stack.free(lhs_dest)
        else:
            raise CompilerError(f"Unsupported addition size!", context)

    else:
        print(destination)
        print(expression)
        raise CompilerError(f"Unsupported expression type {expression} in expression compiler!", context)

    return compiled


def generate_expr(expression: cst.BaseExpression, destination: str, stack: Stack, clobbers: Set[str], context: Context) -> List[str]:
    compiled: List[str] = [context.comment()]

    size = stack.sizeof(destination)
    if size == 1:
        # We can potentially keep the math in the A register!
        clobbers.add("a")

        compiled += generate_expr_internal(expression, "a", stack, clobbers, context)
        compiled += generate_move_to(destination, stack, clobbers, context)
        compiled.append("  STORE A")
    else:
        # Just do stack-based operations.
        compiled += generate_expr_internal(expression, destination, stack, clobbers, context)

    return compiled


def compile_chunk(chunk: cst.BaseSuite, stack: Stack, clobbers: Set[str], function_type: CoreType, context: Context) -> List[str]:
    compiled: List[str] = []

    for statement in chunk.body:
        if isinstance(statement, cst.SimpleStatementLine):
            for simple_statement in statement.body:
                if isinstance(simple_statement, cst.Return):
                    if simple_statement.value is None:
                        # Simple return by itself, doesn't update the retval.
                        if function_type is not NoneType:
                            raise CompilerError(f"Returning nothing from a function marked with a return value", context)
                        compiled += generate_return(function_type, stack, clobbers, context.wrap(simple_statement))
                    else:
                        # Return of some sort of expression.
                        if function_type is NoneType:
                            raise CompilerError(f"Returning something from a function marked with no return value", context)

                        compiled += generate_expr(simple_statement.value, "builtin(retval)", stack, clobbers, context.wrap(simple_statement.value))
                        compiled += generate_return(function_type, stack, clobbers, context.wrap(simple_statement))
                else:
                    raise CompilerError(f"Unsupported node to compile {simple_statement}", context)
        else:
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


def function(func: cst.FunctionDef, context: Context) -> List[str]:
    compiled: List[str] = []
    function_name = func.name.value
    function_type = get_type(func.returns)
    function_params = func.params.params
    stack: Stack = Stack()

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
    compile_chunk(func.body, stack.clone(), clobbers, function_type, context)

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
        if clobber == "a":
            stack.alloc(StackVar("builtin(saved_a)", CoreType("int8")))
            compiled.append("  PUSH A")
            stack.move(1)
        elif clobber == "u":
            stack.alloc(StackVar("builtin(saved_u)", CoreType("int8")))
            compiled.append("  PUSH U")
            stack.move(1)
        elif clobber == "v":
            stack.alloc(StackVar("builtin(saved_v)", CoreType("int8")))
            compiled.append("  PUSH V")
            stack.move(1)
        elif clobber == "spc":
            stack.alloc(StackVar("builtin(saved_spc)", CoreType("int8")))
            compiled.append("  PUSH SPC")
            stack.move(2)
        else:
            raise Exception(f"Logic error, unexpected clobber {clobber}!")

    # Make sure that we have room on the stack for the return value. Don't move at this point
    # because we might not want to generate instructions to move.
    if function_type is not NoneType:
        size = stack.alloc(StackVar("builtin(retval)", function_type))

    # Now, second pass to actually compile.
    compiled += compile_chunk(func.body, stack, set(), function_type, context)

    return [
        f"{function_name}:",
        *preamble,
        *compiled,
    ]


def parse_and_compile(module: str, code: str, refs: List[FunctionPrototype]) -> List[str]:
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
                raise CompilerError("Global variable declarations must have a type", context)
            elif isinstance(body, cst.AnnAssign):
                compiled += global_variable(body, context)
            else:
                raise CompilerError("Arbitrary top-level statements are not supported", context)
        elif isinstance(statement, cst.FunctionDef):
            compiled += function(statement, context)
        else:
            print(statement)
            raise CompilerError("Unsupported statement", context)

        compiled.append("")

    while compiled and compiled[-1] == "":
        compiled = compiled[:-1]

    return compiled


def parse_prototypes(module: str, code: str) -> List[FunctionPrototype]:
    parsed_module = cst.parse_module(code)

    # Make sure we have access to line/column numbers for errors.
    wrapper = cst.MetadataWrapper(parsed_module)
    metadata = wrapper.resolve(meta.PositionProvider)

    # A deep copy is made by the metadata wrapper, because LibCST is designed around safe mutations. We don't care
    # and only need a read-only copy.
    parsed_module = wrapper.module

    prototypes: List[FunctionPrototype] = []
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


def builtin_prototypes() -> List[FunctionPrototype]:
    prototypes: List[FunctionPrototype] = [
        FunctionPrototype("strcat", NoneType, [InOutCoreType("string"), InOutCoreType("string")]),
        FunctionPrototype("strcmp", RegisterCoreType("a"), [InOutCoreType("string"), InOutCoreType("string")]),
        FunctionPrototype("strcpy", NoneType, [InOutCoreType("string"), InOutCoreType("string")]),
        FunctionPrototype("strlen", RegisterCoreType("a"), [InOutCoreType("string")]),
        FunctionPrototype("atoi", RegisterCoreType("a"), [InOutCoreType("string")]),
        FunctionPrototype("atoi16", ParamReturnCoreType(1), [InOutCoreType("string"), OutCoreType("int16")]),
        FunctionPrototype("atoi32", ParamReturnCoreType(1), [InOutCoreType("string"), OutCoreType("int32")]),
        FunctionPrototype("itoa", NoneType, [RegisterCoreType("a"), InOutCoreType("string")]),
        FunctionPrototype("itoa16", NoneType, [CoreType("int16"), InOutCoreType("string")]),
        FunctionPrototype("itoa32", NoneType, [CoreType("int32"), InOutCoreType("string")]),
    ]

    # The following are special cases since we will be bridging to them when compiling
    # math expressions. They're kept here for posterity.
    [
        FunctionPrototype("abs", RegisterCoreType("a"), [RegisterCoreType("a")]),
        FunctionPrototype("abs16", ParamReturnCoreType(0), [InOutCoreType("int16")]),
        FunctionPrototype("abs32", ParamReturnCoreType(0), [InOutCoreType("int32")]),
        FunctionPrototype("neg", RegisterCoreType("a"), [InOutCoreType("int8")]),
        FunctionPrototype("neg16", ParamReturnCoreType(0), [InOutCoreType("int16")]),
        FunctionPrototype("neg32", ParamReturnCoreType(0), [InOutCoreType("int32")]),
        FunctionPrototype("add", RegisterCoreType("a"), [InOutCoreType("int8"), InOutCoreType("int8")]),
        FunctionPrototype("add16", CoreType("int16"), [CoreType("int16"), CoreType("int16")]),
        FunctionPrototype("add32", CoreType("int32"), [CoreType("int32"), CoreType("int32")]),
        FunctionPrototype("ucmp", RegisterCoreType("a"), [InOutCoreType("int8"), InOutCoreType("int8")]),
        FunctionPrototype("ucmp16", RegisterCoreType("a"), [InOutCoreType("int16"), InOutCoreType("int16")]),
        FunctionPrototype("ucmp32", RegisterCoreType("a"), [InOutCoreType("int32"), InOutCoreType("int32")]),
        FunctionPrototype("umin", RegisterCoreType("a"), [InOutCoreType("int8"), InOutCoreType("int8")]),
        FunctionPrototype("umin16", CoreType("int16"), [CoreType("int16"), CoreType("int16")]),
        FunctionPrototype("umin32", CoreType("int32"), [CoreType("int32"), CoreType("int32")]),
        FunctionPrototype("umax", RegisterCoreType("a"), [InOutCoreType("int8"), InOutCoreType("int8")]),
        FunctionPrototype("umax16", CoreType("int16"), [CoreType("int16"), CoreType("int16")]),
        FunctionPrototype("umax32", CoreType("int32"), [CoreType("int32"), CoreType("int32")]),
    ]

    return prototypes

