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
    def __init__(self, base_type: str, const: bool = False) -> None:
        self.type = base_type
        self.const = const

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.type == other
        if isinstance(other, CoreType):
            return self.type == other.type
        return False


NoneType = CoreType("None", True)


class InOutCoreType(CoreType):
    def __init__(self, base_type: str) -> None:
        super().__init__(base_type, False)


class OutCoreType(CoreType):
    def __init__(self, base_type: str) -> None:
        super().__init__(base_type, False)


class RegisterCoreType(CoreType):
    def __init__(self, register: str) -> None:
        super().__init__(register, False)


class ParamReturnType(CoreType):
    def __init__(self, position: int) -> None:
        super().__init__(str(position), False)


def get_type(expr: Optional[cst.CSTNode]) -> Optional[CoreType]:
    if expr is None:
        return None
    if isinstance(expr, cst.Annotation):
        expr = expr.annotation
    if not isinstance(expr, cst.BaseExpression):
        return None

    const: bool = False

    if isinstance(expr, cst.Subscript):
        # Might be a const expr.
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

    if isinstance(expr, cst.Name):
        if expr.value == "None":
            return NoneType
        else:
            return CoreType(expr.value, const)

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


class StackVar:
    def __init__(self, name: str, vartype: CoreType, location: Optional[int] = None) -> None:
        self.name = name
        self.type = vartype
        self.location = location

    @property
    def size(self) -> int:
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

    def free(self) -> None:
        if not self.stack:
            raise Exception("Logic error, freeing from empty stack!")

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
            if first_move > 0:
                compiled.append(f"  SUBPCI {first_move}")
            elif first_move < 0:
                compiled.append(f"  ADDPCI {-first_move}")
            stack.move(first_move)

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

            # We need to relocate the retval to this spot.
            first_move = stack.find("builtin(retval)")
            number_of_moves = stack.sizeof("builtin(retval)")

            if first_move is None or number_of_moves is None:
                raise Exception("Logic error, failed to get move amounts for builtin(retval)!")

            retptr_final_loc = number_of_moves

            # Generate code to move from our position to the first byte of the retval.
            if first_move > 0:
                compiled.append(f"  SUBPCI {first_move}")
            elif first_move < 0:
                compiled.append(f"  ADDPCI {-first_move}")
            stack.move(first_move)

            shuffle_amount = stack.location

            for i in range(number_of_moves):
                compiled.append("  LOAD A")
                compiled.append(f"  ADDPCI {shuffle_amount}")
                compiled.append("  STORE A")

                if i < number_of_moves - 1:
                    compiled.append(f"  SUBPCI {shuffle_amount + 1}")

            stack.move(-(shuffle_amount - (number_of_moves - 1)))

    # Now, move the return pointer if needed.
    if retptr_in_uv:
        compiled.append("  ; Restoring the return pointer from U/V to the correct location.")

        # Gotta grab it out of the saved U/V registers.
        restore_move_amt = retptr_final_loc - stack.location
        if restore_move_amt > 0:
            compiled.append(f"  SUBPCI {restore_move_amt}")
        elif restore_move_amt < 0:
            compiled.append(f"  ADDPCI {-restore_move_amt}")
        stack.move(restore_move_amt)

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
            first_move = stack.find("builtin(retptr)")
            number_of_moves = stack.sizeof("builtin(retptr)")

            if first_move is None or number_of_moves is None:
                raise Exception("Logic error, failed to get move amounts for builtin(retptr)!")

            # Generate code to move from our position to the first byte of the retptr.
            if first_move > 0:
                compiled.append(f"  SUBPCI {first_move}")
            elif first_move < 0:
                compiled.append(f"  ADDPCI {-first_move}")
            stack.move(first_move)

            shuffle_amount = stack.location - retptr_final_loc

            for i in range(number_of_moves):
                compiled.append("  LOAD A")
                compiled.append(f"  ADDPCI {shuffle_amount}")
                compiled.append("  STORE A")

                if i < number_of_moves - 1:
                    compiled.append(f"  SUBPCI {shuffle_amount + 1}")

            stack.move(-(shuffle_amount - (number_of_moves - 1)))

    # Now, pop all of our saved registers, and then return.
    if clobbers:
        compiled.append("  ; Restoring all clobbered registers.")
    while stack.size > 0:
        name = stack.stack[-1].name
        if name[:13] == "builtin(saved":
            move_amt = stack.find(name)
            if move_amt is None:
                raise Exception(f"Logic error, failed to get move amounts for {name}!")

            if move_amt > 0:
                compiled.append(f"  SUBPCI {move_amt}")
            elif move_amt < 0:
                compiled.append(f"  ADDPCI {-move_amt}")
            stack.move(move_amt)

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

        stack.free()

    compiled.append(f"  RET")
    return compiled


def generate_expr(expression: cst.BaseExpression, destination: str, stack: Stack, clobbers: Set[str], context: Context) -> List[str]:
    compiled: List[str] = []
    print(expression)

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

    for func_param in function_params:
        if func_param.default is not None:
            raise CompilerError(f"Function parameter {func_param.name.value} has unsupported default", context)

        # Function parameters are passed on the stack, so we must know their locations and types.
        param_type = get_type(func_param.annotation)
        if param_type is None:
            raise CompilerError(f"Expecting type for function parameter {func_param.name.value}", context)

        prototype.params.append(param_type)

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

    # Need a spot on the stack for our return pointer that is placed when called.
    stack.alloc(StackVar("builtin(retptr)", CoreType("pointer")))
    stack.location = stack.size

    # Make sure that we have room on the stack for the return value.
    if function_type is not NoneType:
        size = stack.alloc(StackVar("builtin(retval)", function_type))

        compiled.append("  ; Allocate stack space for return variable")
        compiled.append(f"  SUBPCI {size}")
        stack.move(size)

    # First pass to figure out clobbers
    clobbers: Set[str] = set()
    compile_chunk(func.body, stack.clone(), clobbers, function_type, context)

    # Now, let's save all of our clobbered values.
    if clobbers:
        compiled.append("  ; Save clobbered registers")
    for clobber in clobbers:
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

    # Now, second pass to actually compile.
    compiled += compile_chunk(func.body, stack, set(), function_type, context)

    return [
        f"{function_name}:",
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
        FunctionPrototype("atoi16", ParamReturnType(1), [InOutCoreType("string"), OutCoreType("int16")]),
        FunctionPrototype("atoi32", ParamReturnType(1), [InOutCoreType("string"), OutCoreType("int32")]),
        FunctionPrototype("itoa", NoneType, [RegisterCoreType("a"), InOutCoreType("string")]),
        FunctionPrototype("itoa16", NoneType, [CoreType("int16"), InOutCoreType("string")]),
        FunctionPrototype("itoa32", NoneType, [CoreType("int32"), InOutCoreType("string")]),
    ]

    # The following are special cases since we will be bridging to them when compiling
    # math expressions. They're kept here for posterity.
    [
        FunctionPrototype("abs", RegisterCoreType("a"), [RegisterCoreType("a")]),
        FunctionPrototype("abs16", ParamReturnType(0), [InOutCoreType("int16")]),
        FunctionPrototype("abs32", ParamReturnType(0), [InOutCoreType("int32")]),
        FunctionPrototype("neg", RegisterCoreType("a"), [InOutCoreType("int8")]),
        FunctionPrototype("neg16", ParamReturnType(0), [InOutCoreType("int16")]),
        FunctionPrototype("neg32", ParamReturnType(0), [InOutCoreType("int32")]),
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

