import libcst as cst
import textwrap
import unittest
from typing import Any, Dict

from .compiler import (
    CompilerError,
    FunctionPrototype,
    CoreType,
    PaddingCoreType,
    Stack,
    StackVar,
    Context,
    VoidType,
    get_type,
    infer_expr_types,
    parse_forward_refs,
    parse_and_compile_module,
)


class TestCompiler(unittest.TestCase):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.maxDiff = None

    def __get_expr(self, expr: str) -> cst.BaseExpression:
        module = cst.parse_module(expr)
        first_statement = module.body[0]
        if not isinstance(first_statement, cst.SimpleStatementLine):
            raise Exception(f"Logic error, expected SimpleStatementLine, got {type(first_statement)}!")
        expr_node = first_statement.body[0]
        if not isinstance(expr_node, cst.Expr):
            raise Exception(f"Logic error, expected BaseExpression, got {type(expr_node)}!")
        return expr_node.value

    def test_get_type(self) -> None:
        # First check for None handling.
        self.assertEqual(CoreType("void", const=True), get_type(self.__get_expr("void"), []))
        self.assertTrue(get_type(self.__get_expr("void"), []) is VoidType)

        # Now, simple parsing.
        self.assertEqual(CoreType("string"), get_type(self.__get_expr("string"), []))
        self.assertEqual(CoreType("char"), get_type(self.__get_expr("char"), []))
        self.assertEqual(CoreType("int8"), get_type(self.__get_expr("int8"), []))
        self.assertEqual(CoreType("int16"), get_type(self.__get_expr("int16"), []))
        self.assertEqual(CoreType("int32"), get_type(self.__get_expr("int32"), []))

        # Now, test length/array syntax.
        self.assertIsNone(get_type(self.__get_expr("string[16]"), []))
        self.assertEqual(CoreType("string", length=16), get_type(self.__get_expr("string[16]"), [], allow_array=True))

        # Now, make sure that constant parsing works.
        self.assertEqual(CoreType("string", const=True), get_type(self.__get_expr("const[string]"), []))
        self.assertEqual(CoreType("char", const=True), get_type(self.__get_expr("const[char]"), []))
        self.assertEqual(CoreType("int8", const=True), get_type(self.__get_expr("const[int8]"), []))
        self.assertEqual(CoreType("int16", const=True), get_type(self.__get_expr("const[int16]"), []))
        self.assertEqual(CoreType("int32", const=True), get_type(self.__get_expr("const[int32]"), []))

        # Now, make sure that pointers work.
        self.assertEqual(CoreType("pointer", CoreType("char")), get_type(self.__get_expr("pointer[char]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int8")), get_type(self.__get_expr("pointer[int8]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int16")), get_type(self.__get_expr("pointer[int16]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int32")), get_type(self.__get_expr("pointer[int32]"), []))

        # Pointers to constants should work.
        self.assertEqual(CoreType("pointer", CoreType("char", const=True)), get_type(self.__get_expr("pointer[const[char]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int8", const=True)), get_type(self.__get_expr("pointer[const[int8]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int16", const=True)), get_type(self.__get_expr("pointer[const[int16]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int32", const=True)), get_type(self.__get_expr("pointer[const[int32]]"), []))

        # Constant pointers to non-constant types should work.
        self.assertEqual(CoreType("pointer", CoreType("char"), const=True), get_type(self.__get_expr("const[pointer[char]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int8"), const=True), get_type(self.__get_expr("const[pointer[int8]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int16"), const=True), get_type(self.__get_expr("const[pointer[int16]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int32"), const=True), get_type(self.__get_expr("const[pointer[int32]]"), []))

        # Constant pointers to constant types should work.
        self.assertEqual(CoreType("pointer", CoreType("char", const=True), const=True), get_type(self.__get_expr("const[pointer[const[char]]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int8", const=True), const=True), get_type(self.__get_expr("const[pointer[const[int8]]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int16", const=True), const=True), get_type(self.__get_expr("const[pointer[const[int16]]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int32", const=True), const=True), get_type(self.__get_expr("const[pointer[const[int32]]]"), []))

        # Now, make sure pointers of pointers work. Hopefully I don't need these but it should be possible to use them.
        self.assertEqual(CoreType("pointer", CoreType("pointer", CoreType("int8"))), get_type(self.__get_expr("pointer[pointer[int8]]"), []))

    def assertTypesValid(self, types: Dict[cst.CSTNode, CoreType]) -> None:
        for node, ctype in types.items():
            if ctype.type not in {"void", "int8", "uint8", "int16", "uint16", "int32", "uint32", "char", "bool", "string", "pointer"}:
                self.fail(f"Unexpected type {ctype.type} for node {node}")

    def test_infer_types_const(self) -> None:
        # Verify that we can infer a normal expression with just two variables.
        expr = self.__get_expr("15")
        stack = Stack()
        types = infer_expr_types(expr, CoreType("int8"), stack, [], [], Context("__test__", expr, {}))
        self.assertEqual(CoreType("int8"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_simple(self) -> None:
        # Verify that we can infer a normal expression with just two variables.
        expr = self.__get_expr("x + y")
        stack = Stack()
        stack.alloc(StackVar("x", CoreType("int8")))
        stack.alloc(StackVar("y", CoreType("int8")))
        types = infer_expr_types(expr, CoreType("int8"), stack, [], [], Context("__test__", expr, {}))
        self.assertEqual(CoreType("int8"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_simple_const(self) -> None:
        # Verify that we can infer a normal expression with just two variables.
        expr = self.__get_expr("x + 12345")
        stack = Stack()
        stack.alloc(StackVar("x", CoreType("int16")))
        types = infer_expr_types(expr, CoreType("int16"), stack, [], [], Context("__test__", expr, {}))
        self.assertEqual(CoreType("int16"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_different_types(self) -> None:
        # Verify that we can infer an expression with different sized variables.
        expr = self.__get_expr("x + y")
        stack = Stack()
        stack.alloc(StackVar("x", CoreType("int16")))
        stack.alloc(StackVar("y", CoreType("int32")))
        types = infer_expr_types(expr, CoreType("int8"), stack, [], [], Context("__test__", expr, {}))
        self.assertEqual(CoreType("int32"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_comparison(self) -> None:
        # Verify that we can infer a comparison expression type.
        expr = self.__get_expr("x == y")
        stack = Stack()
        stack.alloc(StackVar("x", CoreType("int16")))
        stack.alloc(StackVar("y", CoreType("int32")))
        types = infer_expr_types(expr, CoreType("bool"), stack, [], [], Context("__test__", expr, {}))
        self.assertEqual(CoreType("bool"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_comparison_const(self) -> None:
        # Verify that we can infer a comparison expression with a constant.
        expr = self.__get_expr("x == 12345")
        stack = Stack()
        stack.alloc(StackVar("x", CoreType("int16")))
        types = infer_expr_types(expr, CoreType("bool"), stack, [], [], Context("__test__", expr, {}))
        self.assertEqual(CoreType("bool"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_ifexpr(self) -> None:
        # Verify that we can infer a comparison expression type.
        expr = self.__get_expr("x if z else y")
        stack = Stack()
        stack.alloc(StackVar("x", CoreType("int16")))
        stack.alloc(StackVar("y", CoreType("int32")))
        stack.alloc(StackVar("z", CoreType("bool")))
        types = infer_expr_types(expr, CoreType("int32"), stack, [], [], Context("__test__", expr, {}))
        self.assertEqual(CoreType("int32"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_ifexpr_const(self) -> None:
        # Verify that we can infer a comparison expression type.
        expr = self.__get_expr("x if z else 12345")
        stack = Stack()
        stack.alloc(StackVar("x", CoreType("int16")))
        stack.alloc(StackVar("z", CoreType("bool")))
        types = infer_expr_types(expr, CoreType("int16"), stack, [], [], Context("__test__", expr, {}))
        self.assertEqual(CoreType("int16"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_function(self) -> None:
        # Verify that we can infer a function call type.
        expr = self.__get_expr("func(x, y)")
        stack = Stack()
        stack.alloc(StackVar("x", CoreType("int16")))
        stack.alloc(StackVar("y", CoreType("int32")))
        refs = [FunctionPrototype("func", CoreType("int8"), [CoreType("int16"), CoreType("int32")])]
        types = infer_expr_types(expr, CoreType("int8"), stack, refs, [], Context("__test__", expr, {}))
        self.assertEqual(CoreType("int8"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_function_const(self) -> None:
        # Verify that we can infer a function call type with constants.
        expr = self.__get_expr("func(5, 15)")
        stack = Stack()
        refs = [FunctionPrototype("func", CoreType("int8"), [CoreType("int16"), CoreType("int32")])]
        types = infer_expr_types(expr, CoreType("int8"), stack, refs, [], Context("__test__", expr, {}))
        self.assertEqual(CoreType("int8"), types[expr])
        self.assertTypesValid(types)

    def test_empty(self) -> None:
        output = parse_and_compile_module("__test__", "")
        self.assertTrue(len(output.code) == 0)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_throw_on_top_level_statement(self) -> None:
        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", 'print("Hello, world!")')
        self.assertEqual("__test__ line 1: Arbitrary top-level statements are not supported", str(cm.exception))

    def test_allow_global_const_declaration_init(self) -> None:
        output = parse_and_compile_module("__test__", 'UINT8_CONST: const[int8] = 123')
        self.assertEqual([
            '  ; __test__ line 1: UINT8_CONST: const[int8] = 123',
            'UINT8_CONST:',
            '  .byte 0x7b',
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

        output = parse_and_compile_module("__test__", 'UINT16_CONST: const[int16] = 0xCAFE')
        self.assertEqual([
            '  ; __test__ line 1: UINT16_CONST: const[int16] = 0xCAFE',
            'UINT16_CONST:',
            '  .byte 0xca',
            '  .byte 0xfe',
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

        output = parse_and_compile_module("__test__", 'UINT32_CONST: const[int32] = 0xDEADBEEF')
        self.assertEqual([
            '  ; __test__ line 1: UINT32_CONST: const[int32] = 0xDEADBEEF',
            'UINT32_CONST:',
            '  .byte 0xde',
            '  .byte 0xad',
            '  .byte 0xbe',
            '  .byte 0xef',
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

        output = parse_and_compile_module("__test__", "UINT8_CONST: const[char] = 'c'")
        self.assertEqual([
            "  ; __test__ line 1: UINT8_CONST: const[char] = 'c'",
            "UINT8_CONST:",
            "  .char 'c'",
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

        output = parse_and_compile_module("__test__", 'UINT8_CONST: const[string] = "test"')
        self.assertEqual([
            '  ; __test__ line 1: UINT8_CONST: const[string] = "test"',
            'UINT8_CONST:',
            "  .char 't'",
            "  .char 'e'",
            "  .char 's'",
            "  .char 't'",
            "  .byte 0x00",
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_allow_global_const_declaration_init_expr(self) -> None:
        output = parse_and_compile_module("__test__", 'UINT8_CONST: const[int8] = (7 * 2) + 1')
        self.assertEqual([
            '  ; __test__ line 1: UINT8_CONST: const[int8] = (7 * 2) + 1',
            'UINT8_CONST:',
            '  .byte 0x0f'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_throw_on_global_const_declaration(self) -> None:
        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", 'UINT8_CONST: const[int8]')
        self.assertEqual("__test__ line 1: Expecting initialization value for global const definition", str(cm.exception))

    def test_throw_on_global_no_type(self) -> None:
        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", 'SOME_CONST = 123')
        self.assertEqual("__test__ line 1: Global variable declarations must have a type", str(cm.exception))

    def test_define_simple_function(self) -> None:
        func = textwrap.dedent("""
            def simple() -> void:
                return
        """)

        prototypes = parse_forward_refs("__test__", func)
        self.assertEqual([FunctionPrototype("simple", VoidType)], prototypes)

        output = parse_and_compile_module("__test__", func)
        self.assertEqual([
            "simple:",
            "  ; Stack layout just after call:",
            "  ; PC + 0 - builtin(retptr)",
            "  ; PC + 1 - builtin(retptr)",
            "  ;",
            "  ; Stack layout just before return:",
            "  ; PC + 0 - builtin(retptr)",
            "  ; PC + 1 - builtin(retptr)",
            "  ;",
            "  ; __test__ line 3: return",
            "  RET",
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_define_simple_return_function(self) -> None:
        func = textwrap.dedent("""
            def simple() -> int8:
                return 15
        """)

        prototypes = parse_forward_refs("__test__", func)
        self.assertEqual([FunctionPrototype("simple", CoreType("int8"), [PaddingCoreType(1)])], prototypes)

        output = parse_and_compile_module("__test__", func)
        self.assertEqual([
            'simple:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(padding)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(retval)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 3: 15',
            '  LOADI 0x0f',
            '  ADDPCI 3',
            '  STORE A',
            '  ; __test__ line 3: return 15',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 3',
            '  POP A',
            '  RET',
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_define_simple_unpadded_return_function(self) -> None:
        func = textwrap.dedent("""
            def simple() -> nopad[int8]:
                return 15
        """)

        prototypes = parse_forward_refs("__test__", func)
        self.assertEqual([FunctionPrototype("simple", CoreType("int8"))], prototypes)

        output = parse_and_compile_module("__test__", func)
        self.assertEqual([
            'simple:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(retval)',
            '  ;',
            '  SUBPCI 1',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  PUSH U',
            '  PUSH V',
            '  ; __test__ line 3: 15',
            '  LOADI 0x0f',
            '  SUBPCI 1',
            '  STORE A',
            '  ; __test__ line 3: return 15',
            "  ; Saving return pointer to U/V so it isn't overridden by return shuffle.",
            '  ADDPCI 6',
            '  LOAD U',
            '  DECPC',
            '  LOAD V',
            '  ; Moving return value to correct location in stack.',
            '  SUBPCI 5',
            '  LOAD A',
            '  ADDPCI 6',
            '  STORE A',
            '  ; Restoring the return pointer from U/V to the correct location.',
            '  SUBPCI 1',
            '  STORE U',
            '  DECPC',
            '  STORE V',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 3',
            '  POP V',
            '  POP U',
            '  POP A',
            '  RET',
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_define_simple_input_and_return_function(self) -> None:
        func = textwrap.dedent("""
            def simple(param: int8) -> int8:
                return param + 15
        """)

        prototypes = parse_forward_refs("__test__", func)
        self.assertEqual([FunctionPrototype("simple", CoreType("int8"), [CoreType("int8")])], prototypes)

        output = parse_and_compile_module("__test__", func)
        self.assertEqual([
            'simple:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - param',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(retval)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 3: param + 15',
            '  ADDPCI 3',
            '  LOAD A',
            '  SUBPCI 5',
            '  STORE A',
            '  SUBPCI 1',
            '  LOADI 0x0f',
            '  STORE A',
            '  LOAD A',
            '  ADDPCI 1',
            '  ADD',
            '  ADDPCI 5',
            '  STORE A',
            '  ; __test__ line 3: return param + 15',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 3',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_define_use_const(self) -> None:
        func = textwrap.dedent("""
            def defineconst(param: int8) -> int8:
                SOME_CONST: const[int8] = 5
                return param + SOME_CONST
        """)

        prototypes = parse_forward_refs("__test__", func)
        self.assertEqual([FunctionPrototype("defineconst", CoreType("int8"), [CoreType("int8")])], prototypes)

        output = parse_and_compile_module("__test__", func)
        self.assertEqual([
            'defineconst:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - param',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(retval)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 3: SOME_CONST: const[int8] = 5',
            '  ; __test__ line 4: param + SOME_CONST',
            '  ADDPCI 3',
            '  LOAD A',
            '  SUBPCI 5',
            '  STORE A',
            '  SUBPCI 1',
            '  LOADI 0x05',
            '  STORE A',
            '  LOAD A',
            '  ADDPCI 1',
            '  ADD',
            '  ADDPCI 5',
            '  STORE A',
            '  ; __test__ line 4: return param + SOME_CONST',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 3',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_define_use_variable(self) -> None:
        func = textwrap.dedent("""
            def defineconst(param: int8) -> int8:
                some_var: int8 = 5
                some_var = param + some_var
                return some_var
        """)

        prototypes = parse_forward_refs("__test__", func)
        self.assertEqual([FunctionPrototype("defineconst", CoreType("int8"), [CoreType("int8")])], prototypes)

        output = parse_and_compile_module("__test__", func)
        self.assertEqual([
            'defineconst:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - param',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(retval)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 3: some_var: int8 = 5',
            '  ; __test__ line 3: 5',
            '  LOADI 0x05',
            '  SUBPCI 2',
            '  STORE A',
            '  ; __test__ line 4: some_var = param + some_var',
            '  ; __test__ line 4: param + some_var',
            '  ADDPCI 5',
            '  LOAD A',
            '  SUBPCI 6',
            '  STORE A',
            '  ADDPCI 1',
            '  LOAD A',
            '  SUBPCI 2',
            '  STORE A',
            '  LOAD A',
            '  ADDPCI 1',
            '  ADD',
            '  ADDPCI 1',
            '  STORE A',
            '  ; __test__ line 5: some_var',
            '  LOAD A',
            '  ADDPCI 5',
            '  STORE A',
            '  ; __test__ line 5: return some_var',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 3',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_throw_on_local_definition_no_type(self) -> None:
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var = 5
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 3: Unsupported type for local variable definition", str(cm.exception))

    def test_throw_on_local_const_no_assign(self) -> None:
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                SOME_VAR: const[int8]
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 3: Expecting initialization value for local const definition", str(cm.exception))

    def test_throw_on_local_type_redefinition(self) -> None:
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8 = 5
                some_var: int8 = 10
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 4: Unsupported type redefinition for local variable assignment", str(cm.exception))

    def test_throw_on_undefined_local(self) -> None:
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 3: Undefined variable reference to 'some_var'", str(cm.exception))

    def test_throw_on_local_const_reassign(self) -> None:
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                SOME_VAR: const[int8] = 10
                SOME_VAR = 5
                return SOME_VAR
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 4: Cannot assign to variable 'SOME_VAR' declared const", str(cm.exception))

    def test_throw_on_var_use_before_init(self) -> None:
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                return param + some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 4: Use of uninitialized variable 'some_var'", str(cm.exception))

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                if param > 0:
                    some_var = 5
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 6: Use of uninitialized variable 'some_var'", str(cm.exception))

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                if param > 0:
                    pass
                else:
                    some_var = 5
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 8: Use of uninitialized variable 'some_var'", str(cm.exception))

        func = textwrap.dedent("""
            def somefunc(param: int8) -> int8:
                return param

            def localvar(param: int8) -> int8:
                some_var: int8
                return somefunc(some_var)
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 7: Use of uninitialized variable 'some_var'", str(cm.exception))

        func = textwrap.dedent("""
            def localvar() -> void:
                some_var: int8
                some_var = some_var + 1
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 4: Use of uninitialized variable 'some_var'", str(cm.exception))

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                if param == 1:
                    some_var = 1
                elif param == 2:
                    some_var = 2
                elif param == 3:
                    some_var = 3
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 10: Use of uninitialized variable 'some_var'", str(cm.exception))

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                if param == 1:
                    some_var = 1
                else:
                    if param == 2:
                        some_var = 2
                    else:
                        if param == 3:
                            some_var = 3
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 12: Use of uninitialized variable 'some_var'", str(cm.exception))

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                while param > 10:
                    some_var = 1
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 6: Use of uninitialized variable 'some_var'", str(cm.exception))

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8

                x: int8
                for x in range(5):
                    some_var = 1
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 8: Use of uninitialized variable 'some_var'", str(cm.exception))

    def test_doesnt_throw_on_var_use(self) -> None:
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                if param > 0:
                    some_var = 5
                else:
                    some_var = 7
                return some_var
        """)
        parse_and_compile_module("__test__", func)

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                if param > 0:
                    some_var = 5
                elif param < 0:
                    some_var = 7
                else:
                    some_var = 6
                return some_var
        """)
        parse_and_compile_module("__test__", func)

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                if param == 1:
                    some_var = 1
                else:
                    if param == 2:
                        some_var = 2
                    else:
                        if param == 3:
                            some_var = 3
                        else:
                            some_var = 4
                return some_var
        """)
        parse_and_compile_module("__test__", func)

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8 = 2
                if param == 1:
                    some_var = 1
                return some_var
        """)
        parse_and_compile_module("__test__", func)

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                while param > 10:
                    some_var = 1
                    some_var += 1
                return 0
        """)
        parse_and_compile_module("__test__", func)

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                x: int8
                for x in range(10):
                    some_var = 1
                    some_var += 1
                return 0
        """)
        parse_and_compile_module("__test__", func)

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                x: int8
                for x in range(10):
                    pass
                return x
        """)
        parse_and_compile_module("__test__", func)


if __name__ == '__main__':
    unittest.main()
