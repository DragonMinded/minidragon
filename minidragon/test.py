import libcst as cst
import os
import textwrap
import unittest
from typing import Any, Dict, Optional

from .util import (
    signextend,
    hexstr,
    binstr,
    bintoint,
    sanitize,
)
from .core import _splitparams
from .compiler import (
    Compiler,
    CompilerError,
    CompilerSettings,
    FunctionPrototype,
    CoreType,
    PaddingCoreType,
    Stack,
    StackVar,
    Context,
    unescape_literal,
)


class TestAssembler(unittest.TestCase):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.maxDiff = None

    def test_signextend(self) -> None:
        self.assertEqual(0, signextend(0, 7))
        self.assertEqual(0x007F, signextend(0x7F, 7))
        self.assertEqual(0xFFFF, signextend(0xFF, 7))
        self.assertEqual(0xFFFF, signextend(0x1F, 4))
        self.assertEqual(0x000F, signextend(0x0F, 4))

    def test_hexstr(self) -> None:
        self.assertEqual("00", hexstr(0, 2))
        self.assertEqual("01", hexstr(1, 2))
        self.assertEqual("1234", hexstr(0x1234, 4))
        self.assertEqual("0037", hexstr(0x37, 4))

    def test_binstr(self) -> None:
        self.assertEqual("00000000", binstr(0, 8))
        self.assertEqual("10100101", binstr(0xA5, 8))
        self.assertEqual("00001111", binstr(0xF, 8))

    def test_bintoint(self) -> None:
        self.assertEqual(0, bintoint(0))
        self.assertEqual(1, bintoint(1))
        self.assertEqual(0x7F, bintoint(0x7F))
        self.assertEqual(-1, bintoint(0xFF))
        self.assertEqual(-128, bintoint(0x80))

    def test_sanitize(self) -> None:
        self.assertEqual("", sanitize(""))
        self.assertEqual("", sanitize("   "))
        self.assertEqual("NOP", sanitize("NOP"))
        self.assertEqual("NOP", sanitize("  NOP"))
        self.assertEqual("NOP", sanitize("NOP ; comment here"))
        self.assertEqual("NOP", sanitize("  NOP ; comment here"))
        self.assertEqual("LOADI 55", sanitize("  LOADI 55 ; some comment"))
        self.assertEqual(r"LOADI '\n'", sanitize(r"LOADI '\n'"))
        self.assertEqual(r"LOADI '\n'", sanitize(r"  LOADI '\n'"))
        self.assertEqual(r"LOADI '\n'", sanitize(r"LOADI '\n' ; comment here"))
        self.assertEqual(r"LOADI '\n'", sanitize(r"  LOADI '\n' ; comment here"))
        self.assertEqual(r"LOADI ';'", sanitize(r"LOADI ';'"))
        self.assertEqual(r"LOADI ';'", sanitize(r"  LOADI ';'"))
        self.assertEqual(r"LOADI ';'", sanitize(r"LOADI ';' ; comment here"))
        self.assertEqual(r"LOADI ';'", sanitize(r"  LOADI ';' ; comment here"))
        self.assertEqual(r'LOADI ";"', sanitize(r'LOADI ";"'))
        self.assertEqual(r'LOADI ";"', sanitize(r'  LOADI ";"'))
        self.assertEqual(r'LOADI ";"', sanitize(r'LOADI ";" ; comment here'))
        self.assertEqual(r'LOADI ";"', sanitize(r'  LOADI ";" ; comment here'))

    def test_splitparams(self) -> None:
        self.assertEqual((), _splitparams(""))
        self.assertEqual(("5", ), _splitparams("5"))
        self.assertEqual(("5", "5"), _splitparams("5, 5"))
        self.assertEqual(("'5'", "'5'"), _splitparams("'5', '5'"))
        self.assertEqual(("','", '","'), _splitparams("',', \",\""))
        self.assertEqual(("';'", ), _splitparams("';'"))


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
        compiler = Compiler(CompilerSettings())

        # First check for None handling.
        self.assertEqual(CoreType("void", const=True), compiler.get_type(self.__get_expr("void"), []))
        void_type = compiler.get_type(self.__get_expr("void"), [])
        assert void_type is not None
        self.assertTrue(void_type.is_void)

        # Now, simple parsing.
        self.assertEqual(CoreType("str"), compiler.get_type(self.__get_expr("str"), []))
        self.assertEqual(CoreType("char"), compiler.get_type(self.__get_expr("char"), []))
        self.assertEqual(CoreType("int8"), compiler.get_type(self.__get_expr("int8"), []))
        self.assertEqual(CoreType("int16"), compiler.get_type(self.__get_expr("int16"), []))
        self.assertEqual(CoreType("int32"), compiler.get_type(self.__get_expr("int32"), []))

        # Now, test length/array syntax.
        self.assertIsNone(compiler.get_type(self.__get_expr("str[16]"), []))
        self.assertEqual(CoreType("str", length=16), compiler.get_type(self.__get_expr("str[16]"), [], allow_array=True))

        # Now, make sure that constant parsing works.
        self.assertEqual(CoreType("str", const=True), compiler.get_type(self.__get_expr("const[str]"), []))
        self.assertEqual(CoreType("char", const=True), compiler.get_type(self.__get_expr("const[char]"), []))
        self.assertEqual(CoreType("int8", const=True), compiler.get_type(self.__get_expr("const[int8]"), []))
        self.assertEqual(CoreType("int16", const=True), compiler.get_type(self.__get_expr("const[int16]"), []))
        self.assertEqual(CoreType("int32", const=True), compiler.get_type(self.__get_expr("const[int32]"), []))

        # Now, make sure that pointers work.
        self.assertEqual(CoreType("pointer", CoreType("char")), compiler.get_type(self.__get_expr("pointer[char]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int8")), compiler.get_type(self.__get_expr("pointer[int8]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int16")), compiler.get_type(self.__get_expr("pointer[int16]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int32")), compiler.get_type(self.__get_expr("pointer[int32]"), []))

        # Pointers to constants should work.
        self.assertEqual(CoreType("pointer", CoreType("char", const=True)), compiler.get_type(self.__get_expr("pointer[const[char]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int8", const=True)), compiler.get_type(self.__get_expr("pointer[const[int8]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int16", const=True)), compiler.get_type(self.__get_expr("pointer[const[int16]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int32", const=True)), compiler.get_type(self.__get_expr("pointer[const[int32]]"), []))

        # Constant pointers to non-constant types should work.
        self.assertEqual(CoreType("pointer", CoreType("char"), const=True), compiler.get_type(self.__get_expr("const[pointer[char]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int8"), const=True), compiler.get_type(self.__get_expr("const[pointer[int8]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int16"), const=True), compiler.get_type(self.__get_expr("const[pointer[int16]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int32"), const=True), compiler.get_type(self.__get_expr("const[pointer[int32]]"), []))

        # Constant pointers to constant types should work.
        self.assertEqual(CoreType("pointer", CoreType("char", const=True), const=True), compiler.get_type(self.__get_expr("const[pointer[const[char]]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int8", const=True), const=True), compiler.get_type(self.__get_expr("const[pointer[const[int8]]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int16", const=True), const=True), compiler.get_type(self.__get_expr("const[pointer[const[int16]]]"), []))
        self.assertEqual(CoreType("pointer", CoreType("int32", const=True), const=True), compiler.get_type(self.__get_expr("const[pointer[const[int32]]]"), []))

        # Now, make sure pointers of pointers work. Hopefully I don't need these but it should be possible to use them.
        self.assertEqual(CoreType("pointer", CoreType("pointer", CoreType("int8"))), compiler.get_type(self.__get_expr("pointer[pointer[int8]]"), []))

    def assertTypesValid(self, types: Dict[cst.CSTNode, CoreType]) -> None:
        for node, ctype in types.items():
            if ctype.type not in {"void", "int8", "uint8", "int16", "uint16", "int32", "uint32", "char", "bool", "str", "pointer"}:
                self.fail(f"Unexpected type {ctype.type} for node {node}")

    def test_infer_types_const(self) -> None:
        compiler = Compiler(CompilerSettings())

        # Verify that we can infer a normal expression with just two variables.
        expr = self.__get_expr("15")
        stack = Stack("__test__")
        types = compiler.infer_expr_types(expr, CoreType("int8"), stack, [], [], Context("__test__", CompilerSettings(), expr, {}))
        self.assertEqual(CoreType("int8"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_simple(self) -> None:
        compiler = Compiler(CompilerSettings())

        # Verify that we can infer a normal expression with just two variables.
        expr = self.__get_expr("x + y")
        stack = Stack("__test__")
        stack.alloc(StackVar("x", CoreType("int8")))
        stack.alloc(StackVar("y", CoreType("int8")))
        types = compiler.infer_expr_types(expr, CoreType("int8"), stack, [], [], Context("__test__", CompilerSettings(), expr, {}))
        self.assertEqual(CoreType("int8"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_simple_const(self) -> None:
        compiler = Compiler(CompilerSettings())

        # Verify that we can infer a normal expression with just two variables.
        expr = self.__get_expr("x + 12345")
        stack = Stack("__test__")
        stack.alloc(StackVar("x", CoreType("int16")))
        types = compiler.infer_expr_types(expr, CoreType("int16"), stack, [], [], Context("__test__", CompilerSettings(), expr, {}))
        self.assertEqual(CoreType("int16"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_different_types(self) -> None:
        compiler = Compiler(CompilerSettings())

        # Verify that we can infer an expression with different sized variables.
        expr = self.__get_expr("x + y")
        stack = Stack("__test__")
        stack.alloc(StackVar("x", CoreType("int16")))
        stack.alloc(StackVar("y", CoreType("int32")))
        types = compiler.infer_expr_types(expr, CoreType("int8"), stack, [], [], Context("__test__", CompilerSettings(), expr, {}))
        self.assertEqual(CoreType("int32"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_comparison(self) -> None:
        compiler = Compiler(CompilerSettings())

        # Verify that we can infer a comparison expression type.
        expr = self.__get_expr("x == y")
        stack = Stack("__test__")
        stack.alloc(StackVar("x", CoreType("int16")))
        stack.alloc(StackVar("y", CoreType("int32")))
        types = compiler.infer_expr_types(expr, CoreType("bool"), stack, [], [], Context("__test__", CompilerSettings(), expr, {}))
        self.assertEqual(CoreType("bool"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_comparison_const(self) -> None:
        compiler = Compiler(CompilerSettings())

        # Verify that we can infer a comparison expression with a constant.
        expr = self.__get_expr("x == 12345")
        stack = Stack("__test__")
        stack.alloc(StackVar("x", CoreType("int16")))
        types = compiler.infer_expr_types(expr, CoreType("bool"), stack, [], [], Context("__test__", CompilerSettings(), expr, {}))
        self.assertEqual(CoreType("bool"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_ifexpr(self) -> None:
        compiler = Compiler(CompilerSettings())

        # Verify that we can infer a comparison expression type.
        expr = self.__get_expr("x if z else y")
        stack = Stack("__test__")
        stack.alloc(StackVar("x", CoreType("int16")))
        stack.alloc(StackVar("y", CoreType("int32")))
        stack.alloc(StackVar("z", CoreType("bool")))
        types = compiler.infer_expr_types(expr, CoreType("int32"), stack, [], [], Context("__test__", CompilerSettings(), expr, {}))
        self.assertEqual(CoreType("int32"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_ifexpr_const(self) -> None:
        compiler = Compiler(CompilerSettings())

        # Verify that we can infer a comparison expression type.
        expr = self.__get_expr("x if z else 12345")
        stack = Stack("__test__")
        stack.alloc(StackVar("x", CoreType("int16")))
        stack.alloc(StackVar("z", CoreType("bool")))
        types = compiler.infer_expr_types(expr, CoreType("int16"), stack, [], [], Context("__test__", CompilerSettings(), expr, {}))
        self.assertEqual(CoreType("int16"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_function(self) -> None:
        compiler = Compiler(CompilerSettings())

        # Verify that we can infer a function call type.
        expr = self.__get_expr("func(x, y)")
        stack = Stack("__test__")
        stack.alloc(StackVar("x", CoreType("int16")))
        stack.alloc(StackVar("y", CoreType("int32")))
        refs = [FunctionPrototype("func", CoreType("int8"), [CoreType("int16"), CoreType("int32")])]
        types = compiler.infer_expr_types(expr, CoreType("int8"), stack, refs, [], Context("__test__", CompilerSettings(), expr, {}))
        self.assertEqual(CoreType("int8"), types[expr])
        self.assertTypesValid(types)

    def test_infer_types_function_const(self) -> None:
        compiler = Compiler(CompilerSettings())

        # Verify that we can infer a function call type with constants.
        expr = self.__get_expr("func(5, 15)")
        stack = Stack("__test__")
        refs = [FunctionPrototype("func", CoreType("int8"), [CoreType("int16"), CoreType("int32")])]
        types = compiler.infer_expr_types(expr, CoreType("int8"), stack, refs, [], Context("__test__", CompilerSettings(), expr, {}))
        self.assertEqual(CoreType("int8"), types[expr])
        self.assertTypesValid(types)

    def test_empty(self) -> None:
        compiler = Compiler(CompilerSettings())
        output = compiler.parse_and_compile_module("__test__", "")
        self.assertTrue(len(output.code) == 0)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_throw_on_top_level_statement(self) -> None:
        compiler = Compiler(CompilerSettings())
        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", 'print("Hello, world!")')
        self.assertEqual("__test__ line 1: Arbitrary top-level statements are not supported", str(cm.exception))

    def test_allow_global_const_declaration_init(self) -> None:
        compiler = Compiler(CompilerSettings())
        output = compiler.parse_and_compile_module("__test__", 'UINT8_CONST: const[int8] = 123')
        self.assertEqual([
            '  ; __test__ line 1: UINT8_CONST: const[int8] = 123',
            'UINT8_CONST:',
            '  .byte 0x7b',
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

        output = compiler.parse_and_compile_module("__test__", 'UINT16_CONST: const[int16] = 0xCAFE')
        self.assertEqual([
            '  ; __test__ line 1: UINT16_CONST: const[int16] = 0xCAFE',
            'UINT16_CONST:',
            '  .byte 0xca',
            '  .byte 0xfe',
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

        output = compiler.parse_and_compile_module("__test__", 'UINT32_CONST: const[int32] = 0xDEADBEEF')
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

        output = compiler.parse_and_compile_module("__test__", "UINT8_CONST: const[char] = 'c'")
        self.assertEqual([
            "  ; __test__ line 1: UINT8_CONST: const[char] = 'c'",
            "UINT8_CONST:",
            "  .char 'c'",
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

        output = compiler.parse_and_compile_module("__test__", 'UINT8_CONST: const[str] = "test"')
        self.assertEqual([
            '  ; __test__ line 1: UINT8_CONST: const[str] = "test"',
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
        compiler = Compiler(CompilerSettings())
        output = compiler.parse_and_compile_module("__test__", 'UINT8_CONST: const[int8] = (7 * 2) + 1')
        self.assertEqual([
            '  ; __test__ line 1: UINT8_CONST: const[int8] = (7 * 2) + 1',
            'UINT8_CONST:',
            '  .byte 0x0f'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_throw_on_global_const_declaration(self) -> None:
        compiler = Compiler(CompilerSettings())
        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", 'UINT8_CONST: const[int8]')
        self.assertEqual("__test__ line 1: Expecting initialization value for global const definition", str(cm.exception))

    def test_throw_on_global_no_type(self) -> None:
        compiler = Compiler(CompilerSettings())
        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", 'SOME_CONST = 123')
        self.assertEqual("__test__ line 1: Global variable declarations must have a type", str(cm.exception))

    def test_global_string_declaration_simple(self) -> None:
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent(r"""
            const_str: const[str] = "This is a test.\n"
        """)
        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            r'  ; __test__ line 2: const_str: const[str] = "This is a test.\n"',
            'const_str:',
            "  .char 'T'",
            "  .char 'h'",
            "  .char 'i'",
            "  .char 's'",
            "  .char ' '",
            "  .char 'i'",
            "  .char 's'",
            "  .char ' '",
            "  .char 'a'",
            "  .char ' '",
            "  .char 't'",
            "  .char 'e'",
            "  .char 's'",
            "  .char 't'",
            "  .char '.'",
            r"  .char '\n'",
            '  .byte 0x00'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_global_string_declaration_unicode(self) -> None:
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent(r"""
            const_str: const[str] = u"This is a test.\n"
        """)
        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            r'  ; __test__ line 2: const_str: const[str] = u"This is a test.\n"',
            'const_str:',
            "  .char 'T'",
            "  .char 'h'",
            "  .char 'i'",
            "  .char 's'",
            "  .char ' '",
            "  .char 'i'",
            "  .char 's'",
            "  .char ' '",
            "  .char 'a'",
            "  .char ' '",
            "  .char 't'",
            "  .char 'e'",
            "  .char 's'",
            "  .char 't'",
            "  .char '.'",
            r"  .char '\n'",
            '  .byte 0x00'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_global_string_declaration_bytes(self) -> None:
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent(r"""
            const_str: const[str] = b"This is a test.\n"
        """)
        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            r'  ; __test__ line 2: const_str: const[str] = b"This is a test.\n"',
            'const_str:',
            "  .char 'T'",
            "  .char 'h'",
            "  .char 'i'",
            "  .char 's'",
            "  .char ' '",
            "  .char 'i'",
            "  .char 's'",
            "  .char ' '",
            "  .char 'a'",
            "  .char ' '",
            "  .char 't'",
            "  .char 'e'",
            "  .char 's'",
            "  .char 't'",
            "  .char '.'",
            r"  .char '\n'",
            '  .byte 0x00'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_global_string_declaration_raw(self) -> None:
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent(r"""
            const_str: const[str] = r"This is a test.\n"
        """)
        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            r'  ; __test__ line 2: const_str: const[str] = r"This is a test.\n"',
            'const_str:',
            "  .char 'T'",
            "  .char 'h'",
            "  .char 'i'",
            "  .char 's'",
            "  .char ' '",
            "  .char 'i'",
            "  .char 's'",
            "  .char ' '",
            "  .char 'a'",
            "  .char ' '",
            "  .char 't'",
            "  .char 'e'",
            "  .char 's'",
            "  .char 't'",
            "  .char '.'",
            r"  .char '\\'",
            "  .char 'n'",
            '  .byte 0x00'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_define_simple_function(self) -> None:
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def simple() -> void:
                return
        """)

        prototypes = compiler.parse_forward_refs("__test__", func)
        self.assertEqual([FunctionPrototype("simple", CoreType("void", const=True))], prototypes)

        output = compiler.parse_and_compile_module("__test__", func)
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
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def simple() -> int8:
                return 15
        """)

        prototypes = compiler.parse_forward_refs("__test__", func)
        self.assertEqual([FunctionPrototype("simple", CoreType("int8"), [PaddingCoreType(1)])], prototypes)

        output = compiler.parse_and_compile_module("__test__", func)
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
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def simple() -> nopad[int8]:
                return 15
        """)

        prototypes = compiler.parse_forward_refs("__test__", func)
        self.assertEqual([FunctionPrototype("simple", CoreType("int8"))], prototypes)

        output = compiler.parse_and_compile_module("__test__", func)
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
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def simple(param: int8) -> int8:
                return param + 15
        """)

        prototypes = compiler.parse_forward_refs("__test__", func)
        self.assertEqual([FunctionPrototype("simple", CoreType("int8"), [CoreType("int8")], ["param"], [None])], prototypes)

        output = compiler.parse_and_compile_module("__test__", func)
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
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def defineconst(param: int8) -> int8:
                SOME_CONST: const[int8] = 5
                return param + SOME_CONST
        """)

        prototypes = compiler.parse_forward_refs("__test__", func)
        self.assertEqual([FunctionPrototype("defineconst", CoreType("int8"), [CoreType("int8")], ["param"], [None])], prototypes)

        output = compiler.parse_and_compile_module("__test__", func)
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
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def defineconst(param: int8) -> int8:
                some_var: int8 = 5
                some_var = param + some_var
                return some_var
        """)

        prototypes = compiler.parse_forward_refs("__test__", func)
        self.assertEqual([FunctionPrototype("defineconst", CoreType("int8"), [CoreType("int8")], ["param"], [None])], prototypes)

        output = compiler.parse_and_compile_module("__test__", func)
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
            '  LOADI 0x05',
            '  SUBPCI 2',
            '  STORE A',
            '  ; __test__ line 4: some_var = param + some_var',
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
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var = 5
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 3: Unsupported type for local variable definition", str(cm.exception))

    def test_throw_on_local_const_no_assign(self) -> None:
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                SOME_VAR: const[int8]
        """)

        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 3: Expecting initialization value for local const definition", str(cm.exception))

    def test_throw_on_local_type_redefinition(self) -> None:
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8 = 5
                some_var: int8 = 10
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 4: Unsupported type redefinition for local variable assignment", str(cm.exception))

    def test_throw_on_undefined_local(self) -> None:
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 3: Undefined variable reference to 'some_var'", str(cm.exception))

    def test_throw_on_local_const_reassign(self) -> None:
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                SOME_VAR: const[int8] = 10
                SOME_VAR = 5
                return SOME_VAR
        """)

        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 4: Cannot assign to variable 'SOME_VAR' declared const", str(cm.exception))

    def test_throw_on_var_use_before_init(self) -> None:
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                return param + some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 4: Use of uninitialized variable 'some_var'", str(cm.exception))

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                if param > 0:
                    some_var = 5
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", func)
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
            compiler.parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 8: Use of uninitialized variable 'some_var'", str(cm.exception))

        func = textwrap.dedent("""
            def somefunc(param: int8) -> int8:
                return param

            def localvar(param: int8) -> int8:
                some_var: int8
                return somefunc(some_var)
        """)

        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 7: Use of uninitialized variable 'some_var'", str(cm.exception))

        func = textwrap.dedent("""
            def localvar() -> void:
                some_var: int8
                some_var = some_var + 1
        """)

        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", func)
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
            compiler.parse_and_compile_module("__test__", func)
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
            compiler.parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 12: Use of uninitialized variable 'some_var'", str(cm.exception))

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                while param > 10:
                    some_var = 1
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", func)
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
            compiler.parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 8: Use of uninitialized variable 'some_var'", str(cm.exception))

    def test_doesnt_throw_on_var_use(self) -> None:
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                if param > 0:
                    some_var = 5
                else:
                    some_var = 7
                return some_var
        """)
        compiler.parse_and_compile_module("__test__", func)

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
        compiler.parse_and_compile_module("__test__", func)

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
        compiler.parse_and_compile_module("__test__", func)

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8 = 2
                if param == 1:
                    some_var = 1
                return some_var
        """)
        compiler.parse_and_compile_module("__test__", func)

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                while param > 10:
                    some_var = 1
                    some_var += 1
                return 0
        """)
        compiler.parse_and_compile_module("__test__", func)

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8
                x: int8
                for x in range(10):
                    some_var = 1
                    some_var += 1
                return 0
        """)
        compiler.parse_and_compile_module("__test__", func)

        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                x: int8
                for x in range(10):
                    pass
                return x
        """)
        compiler.parse_and_compile_module("__test__", func)

    def __loader(self, filename: str) -> Optional[str]:
        filename = os.path.basename(filename)

        if filename == "good.py":
            return textwrap.dedent("""
                from lib import math

                def func(a: int8, b: int8) -> int8:
                    return math(a, b)
            """)
        if filename == "bad.py":
            return textwrap.dedent("""
                from unk import math

                def func(a: int8, b: int8) -> int8:
                    return math(a, b)
            """)
        if filename == "wrong.py":
            return textwrap.dedent("""
                from lib import some_func

                def func(a: int8, b: int8) -> int8:
                    return some_func(a, b)
            """)
        if filename == "shadow.py":
            return textwrap.dedent("""
                from lib import *

                def math(a: int8, b: int8) -> int8:
                    return a + b
            """)
        elif filename == "lib.py":
            return textwrap.dedent("""
                def math(a: int8, b: int8) -> int8:
                    return a - b
            """)
        else:
            return None

    def test_no_error_on_import_found(self) -> None:
        compiler = Compiler(CompilerSettings(), file_loader=self.__loader, working_directory="/")
        compiler.parse_and_compile_module("good.py", self.__loader("good.py") or "")

    def test_error_on_import_not_found(self) -> None:
        compiler = Compiler(CompilerSettings(), file_loader=self.__loader, working_directory="/")
        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("bad.py", self.__loader("bad.py") or "")
        self.assertEqual("bad.py line 2: File ./unk.py not found when attempting import", str(cm.exception))

    def test_error_on_import_not_existing(self) -> None:
        compiler = Compiler(CompilerSettings(), file_loader=self.__loader, working_directory="/")
        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("wrong.py", self.__loader("wrong.py") or "")
        self.assertEqual("wrong.py line 2: File ./lib.py does not export importable some_func", str(cm.exception))

    def test_error_on_import_shadow(self) -> None:
        compiler = Compiler(CompilerSettings(), file_loader=self.__loader, working_directory="/")
        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("shadow.py", self.__loader("shadow.py") or "")
        self.assertEqual("shadow.py line 2: Import of math shadows local definitions", str(cm.exception))

    def test_unescape_literal(self) -> None:
        self.assertEqual("testing\n", unescape_literal("testing\\n"))
        self.assertEqual("testing\t", unescape_literal("testing\\t"))
        self.assertEqual("testing\\", unescape_literal("testing\\\\"))
        self.assertEqual("testing\x01", unescape_literal("testing\\x01"))
        self.assertEqual("testing\001", unescape_literal("testing\\001"))

    def test_intrinsic_simple(self) -> None:
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def simple() -> int32:
                return fixed(3.14159)
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            "simple:",
            "  ; Stack layout just after call:",
            "  ; PC + 0 - builtin(retptr)",
            "  ; PC + 1 - builtin(retptr)",
            "  ; PC + 2 - builtin(padding)",
            "  ; PC + 3 - builtin(padding)",
            "  ; PC + 4 - builtin(padding)",
            "  ; PC + 5 - builtin(padding)",
            "  ;",
            "  ; Stack layout just before return:",
            "  ; PC + 0 - builtin(retptr)",
            "  ; PC + 1 - builtin(retptr)",
            "  ; PC + 2 - builtin(retval)",
            "  ; PC + 3 - builtin(retval)",
            "  ; PC + 4 - builtin(retval)",
            "  ; PC + 5 - builtin(retval)",
            "  ;",
            "  ; Save clobbered registers",
            "  PUSH A",
            "  ; __test__ line 3: fixed(3.14159)",
            "  ADDPCI 6",
            "  LOADI 0x24",
            "  STORE A",
            "  DECPC",
            "  LOADI 0x03",
            "  STORE A",
            "  DECPC",
            "  LOADI 0x00",
            "  STORE A",
            "  DECPC",
            "  LOADI 0x00",
            "  STORE A",
            "  ; __test__ line 3: return fixed(3.14159)",
            "  ; Restoring all clobbered registers.",
            "  SUBPCI 3",
            "  POP A",
            "  RET",
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_intrinsic_positional(self) -> None:
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def simple() -> int32:
                return fixed(3.14159, 8)
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            "simple:",
            "  ; Stack layout just after call:",
            "  ; PC + 0 - builtin(retptr)",
            "  ; PC + 1 - builtin(retptr)",
            "  ; PC + 2 - builtin(padding)",
            "  ; PC + 3 - builtin(padding)",
            "  ; PC + 4 - builtin(padding)",
            "  ; PC + 5 - builtin(padding)",
            "  ;",
            "  ; Stack layout just before return:",
            "  ; PC + 0 - builtin(retptr)",
            "  ; PC + 1 - builtin(retptr)",
            "  ; PC + 2 - builtin(retval)",
            "  ; PC + 3 - builtin(retval)",
            "  ; PC + 4 - builtin(retval)",
            "  ; PC + 5 - builtin(retval)",
            "  ;",
            "  ; Save clobbered registers",
            "  PUSH A",
            "  ; __test__ line 3: fixed(3.14159, 8)",
            "  ADDPCI 6",
            "  LOADI 0x24",
            "  STORE A",
            "  DECPC",
            "  LOADI 0x03",
            "  STORE A",
            "  DECPC",
            "  LOADI 0x00",
            "  STORE A",
            "  DECPC",
            "  LOADI 0x00",
            "  STORE A",
            "  ; __test__ line 3: return fixed(3.14159, 8)",
            "  ; Restoring all clobbered registers.",
            "  SUBPCI 3",
            "  POP A",
            "  RET",
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_intrinsic_keyword(self) -> None:
        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def simple() -> int32:
                return fixed(3.14159, fracbits=8)
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            "simple:",
            "  ; Stack layout just after call:",
            "  ; PC + 0 - builtin(retptr)",
            "  ; PC + 1 - builtin(retptr)",
            "  ; PC + 2 - builtin(padding)",
            "  ; PC + 3 - builtin(padding)",
            "  ; PC + 4 - builtin(padding)",
            "  ; PC + 5 - builtin(padding)",
            "  ;",
            "  ; Stack layout just before return:",
            "  ; PC + 0 - builtin(retptr)",
            "  ; PC + 1 - builtin(retptr)",
            "  ; PC + 2 - builtin(retval)",
            "  ; PC + 3 - builtin(retval)",
            "  ; PC + 4 - builtin(retval)",
            "  ; PC + 5 - builtin(retval)",
            "  ;",
            "  ; Save clobbered registers",
            "  PUSH A",
            "  ; __test__ line 3: fixed(3.14159, fracbits=8)",
            "  ADDPCI 6",
            "  LOADI 0x24",
            "  STORE A",
            "  DECPC",
            "  LOADI 0x03",
            "  STORE A",
            "  DECPC",
            "  LOADI 0x00",
            "  STORE A",
            "  DECPC",
            "  LOADI 0x00",
            "  STORE A",
            "  ; __test__ line 3: return fixed(3.14159, fracbits=8)",
            "  ; Restoring all clobbered registers.",
            "  SUBPCI 3",
            "  POP A",
            "  RET",
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_incorrect_str_const_function(self) -> None:
        """
        Verifies that if you claim to return a const[str] from a function, you are returning a safe reference. It can't
        work that a local const that uses local storage is returned from a function, because otherwise assigning from
        that function to another const will keep a reference to that local memory that could be modified by another call
        to that function. So, test various scenarios for this here.
        """

        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def func() -> const[str]:
                some_str: str[12] = "hello"
                return some_str
        """)

        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 4: Cannot return a locally-computed constant value from a function marked as const.", str(cm.exception))

        func = textwrap.dedent("""
            GLOBAL: const[str] = "abcde"

            def func() -> const[str]:
                return GLOBAL[:3]
        """)

        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 5: Cannot return a locally-computed constant value from a function marked as const.", str(cm.exception))

        func = textwrap.dedent("""
            def func() -> const[str]:
                some_nonconst_str: str[12] = "abcde"
                some_str: const[str] = some_nonconst_str
                return some_str
        """)

        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 5: Cannot return a locally-computed constant value from a function marked as const.", str(cm.exception))

        # This might seem confusing, but we allow an optimization where we don't strcpy to local parameter storage for
        # const[str] function parameters. So, if we allow that, we cannot trust that the const[str] given to the function
        # is truly a safe reference.
        func = textwrap.dedent("""
            def func(param: const[str]) -> const[str]:
                return param
        """)

        with self.assertRaises(CompilerError) as cm:
            compiler.parse_and_compile_module("__test__", func)
        self.assertEqual("__test__ line 3: Cannot return a locally-computed constant value from a function marked as const.", str(cm.exception))

    def test_correct_str_const_function(self) -> None:
        """
        Verify that in the few cases where you're allowed to return a constant string from a function, they work.
        """

        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def func() -> const[str]:
                return "abcde"
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            '_test_local_function_string_data_1:',
            "  .char 'a'",
            "  .char 'b'",
            "  .char 'c'",
            "  .char 'd'",
            "  .char 'e'",
            '  .byte 0x00',
            '',
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(padding)',
            '  ; PC + 3 - builtin(padding)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(retval)',
            '  ; PC + 3 - builtin(retval)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 3: "abcde"',
            '  ADDPCI 5',
            '  PUSHADDR _test_local_function_string_data_1',
            '  ; __test__ line 3: return "abcde"',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 3',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

        func = textwrap.dedent("""
            def func() -> const[str]:
                some_const: const[str] = "abcde"
                return some_const
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            '_test_local_function_string_data_2:',
            "  .char 'a'",
            "  .char 'b'",
            "  .char 'c'",
            "  .char 'd'",
            "  .char 'e'",
            '  .byte 0x00',
            '',
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(padding)',
            '  ; PC + 3 - builtin(padding)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(retval)',
            '  ; PC + 3 - builtin(retval)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 3: some_const: const[str] = "abcde"',
            '  SUBPCI 2',
            '  PUSHADDR _test_local_function_string_data_2',
            '  ; __test__ line 4: some_const',
            '  LOAD A',
            '  ADDPCI 7',
            '  STORE A',
            '  SUBPCI 6',
            '  LOAD A',
            '  ADDPCI 7',
            '  STORE A',
            '  ; __test__ line 4: return some_const',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 4',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

        func = textwrap.dedent("""
            def func() -> const[str]:
                some_const: const[str] = "abcde"
                other_const: const[str] = some_const
                return other_const
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            '_test_local_function_string_data_3:',
            "  .char 'a'",
            "  .char 'b'",
            "  .char 'c'",
            "  .char 'd'",
            "  .char 'e'",
            '  .byte 0x00',
            '',
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(padding)',
            '  ; PC + 3 - builtin(padding)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(retval)',
            '  ; PC + 3 - builtin(retval)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 3: some_const: const[str] = "abcde"',
            '  SUBPCI 2',
            '  PUSHADDR _test_local_function_string_data_3',
            '  ; __test__ line 4: other_const: const[str] = some_const',
            '  LOAD A',
            '  SUBPCI 2',
            '  STORE A',
            '  ADDPCI 3',
            '  LOAD A',
            '  SUBPCI 2',
            '  STORE A',
            '  ; __test__ line 5: other_const',
            '  LOAD A',
            '  ADDPCI 9',
            '  STORE A',
            '  SUBPCI 10',
            '  LOAD A',
            '  ADDPCI 9',
            '  STORE A',
            '  ; __test__ line 5: return other_const',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 3',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

        func = textwrap.dedent("""
            GLOBAL_CONST: const[str] = "abcde"
            def func() -> const[str]:
                return GLOBAL_CONST
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            '  ; __test__ line 2: GLOBAL_CONST: const[str] = "abcde"',
            'GLOBAL_CONST:',
            "  .char 'a'",
            "  .char 'b'",
            "  .char 'c'",
            "  .char 'd'",
            "  .char 'e'",
            '  .byte 0x00',
            '',
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(padding)',
            '  ; PC + 3 - builtin(padding)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(retval)',
            '  ; PC + 3 - builtin(retval)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 4: GLOBAL_CONST',
            '  ADDPCI 5',
            '  PUSHADDR GLOBAL_CONST',
            '  ; __test__ line 4: return GLOBAL_CONST',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 3',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

        func = textwrap.dedent("""
            def other() -> extern[const[str]]: ...

            def func() -> const[str]:
                return other()
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(padding)',
            '  ; PC + 3 - builtin(padding)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(retval)',
            '  ; PC + 3 - builtin(retval)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 5: other()',
            '  SUBPCI 4',
            '  CALL other',
            '  LOAD A',
            '  ADDPCI 7',
            '  STORE A',
            '  SUBPCI 6',
            '  LOAD A',
            '  ADDPCI 7',
            '  STORE A',
            '  ; __test__ line 5: return other()',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 4',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

    def test_correct_strcpy_generation(self) -> None:
        """
        Make sure that we generate a strcpy in all assignment scenarios that matter so that we don't end up
        with variable aliasing which is extremely hard to debug.
        """

        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def func() -> void:
                some_str: str[12] = "abcde"
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            '_test_local_function_string_data_1:',
            "  .char 'a'",
            "  .char 'b'",
            "  .char 'c'",
            "  .char 'd'",
            "  .char 'e'",
            '  .byte 0x00',
            '',
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 3: some_str: str[12] = "abcde"',
            '  PUSHADDR _test_func_some_str',
            '  PUSHADDR _test_local_function_string_data_1',
            '  ; __test__ line 3: "abcde"',
            '  CALL strcpy',
            '  ; __test__ line 2: def func() -> void:',
            '  ; Restoring all clobbered registers.',
            '  ADDPCI 4',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertEqual([
            '_test_func_some_str:',
            '  .pad 12'
        ], output.data)
        self.assertTrue(len(output.init) == 0)

        func = textwrap.dedent("""
            def func() -> void:
                other_str: str[12] = "abcde"
                some_str: str[12] = other_str
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            '_test_local_function_string_data_2:',
            "  .char 'a'",
            "  .char 'b'",
            "  .char 'c'",
            "  .char 'd'",
            "  .char 'e'",
            '  .byte 0x00',
            '',
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 3: other_str: str[12] = "abcde"',
            '  PUSHADDR _test_func_other_str',
            '  PUSHADDR _test_local_function_string_data_2',
            '  ; __test__ line 3: "abcde"',
            '  CALL strcpy',
            '  ; __test__ line 4: some_str: str[12] = other_str',
            '  ADDPCI 2',
            '  PUSHADDR _test_func_some_str',
            '  ADDPCI 3',
            '  LOAD A',
            '  SUBPCI 4',
            '  STORE A',
            '  ADDPCI 3',
            '  LOAD A',
            '  SUBPCI 4',
            '  STORE A',
            '  ; __test__ line 4: other_str',
            '  CALL strcpy',
            '  ; __test__ line 2: def func() -> void:',
            '  ; Restoring all clobbered registers.',
            '  ADDPCI 6',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertEqual([
            '_test_func_other_str:',
            '  .pad 12',
            '_test_func_some_str:',
            '  .pad 12'
        ], output.data)
        self.assertTrue(len(output.init) == 0)

        func = textwrap.dedent("""
            def func() -> void:
                other_str: const[str] = "abcde"
                some_str: str[12] = other_str
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            '_test_local_function_string_data_3:',
            "  .char 'a'",
            "  .char 'b'",
            "  .char 'c'",
            "  .char 'd'",
            "  .char 'e'",
            '  .byte 0x00',
            '',
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 3: other_str: const[str] = "abcde"',
            '  PUSHADDR _test_local_function_string_data_3',
            '  ; __test__ line 4: some_str: str[12] = other_str',
            '  PUSHADDR _test_func_some_str',
            '  ADDPCI 3',
            '  LOAD A',
            '  SUBPCI 4',
            '  STORE A',
            '  ADDPCI 3',
            '  LOAD A',
            '  SUBPCI 4',
            '  STORE A',
            '  ; __test__ line 4: other_str',
            '  CALL strcpy',
            '  ; __test__ line 2: def func() -> void:',
            '  ; Restoring all clobbered registers.',
            '  ADDPCI 6',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertEqual([
            '_test_func_some_str:',
            '  .pad 12'
        ], output.data)
        self.assertTrue(len(output.init) == 0)

        func = textwrap.dedent("""
            def func() -> void:
                other_str: str[12] = "abcde"
                some_str: const[str] = other_str
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            '_test_local_function_string_data_4:',
            "  .char 'a'",
            "  .char 'b'",
            "  .char 'c'",
            "  .char 'd'",
            "  .char 'e'",
            '  .byte 0x00',
            '',
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 3: other_str: str[12] = "abcde"',
            '  PUSHADDR _test_func_other_str',
            '  PUSHADDR _test_local_function_string_data_4',
            '  ; __test__ line 3: "abcde"',
            '  CALL strcpy',
            '  ; __test__ line 4: some_str: const[str] = other_str',
            '  ADDPCI 2',
            '  PUSHADDR _test_func_some_str',
            '  ADDPCI 3',
            '  LOAD A',
            '  SUBPCI 4',
            '  STORE A',
            '  ADDPCI 3',
            '  LOAD A',
            '  SUBPCI 4',
            '  STORE A',
            '  ; __test__ line 4: other_str',
            '  CALL strcpy',
            '  ; __test__ line 2: def func() -> void:',
            '  ; Restoring all clobbered registers.',
            '  ADDPCI 6',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertEqual([
            '_test_func_other_str:',
            '  .pad 12',
            '_test_func_some_str:',
            '  .pad 127'
        ], output.data)
        self.assertTrue(len(output.init) == 0)

        # This one should not perform a second strcpy on return.
        func = textwrap.dedent("""
            def func() -> str:
                some_str: str[12] = "abcde"
                return some_str
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            '_test_local_function_string_data_5:',
            "  .char 'a'",
            "  .char 'b'",
            "  .char 'c'",
            "  .char 'd'",
            "  .char 'e'",
            '  .byte 0x00',
            '',
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(padding)',
            '  ; PC + 3 - builtin(padding)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ; PC + 2 - builtin(retval)',
            '  ; PC + 3 - builtin(retval)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 3: some_str: str[12] = "abcde"',
            '  SUBPCI 2',
            '  PUSHADDR _test_func_some_str',
            '  PUSHADDR _test_local_function_string_data_5',
            '  ; __test__ line 3: "abcde"',
            '  CALL strcpy',
            '  ; __test__ line 4: some_str',
            '  ADDPCI 3',
            '  LOAD A',
            '  ADDPCI 7',
            '  STORE A',
            '  SUBPCI 8',
            '  LOAD A',
            '  ADDPCI 7',
            '  STORE A',
            '  ; __test__ line 4: return some_str',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 3',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertEqual([
            '_test_func_some_str:',
            '  .pad 12'
        ], output.data)
        self.assertTrue(len(output.init) == 0)

    def test_correct_str_parameters(self) -> None:
        """
        Verify that we generate a strcpy into the local function parameter storage for any non-const
        parameter to a function, so that the function is free to modify that string without messing
        with our copy.
        """

        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def other(param: str[12]) -> extern[void]: ...

            def func() -> void:
                other("12345")
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            '_test_local_function_string_data_1:',
            "  .char '1'",
            "  .char '2'",
            "  .char '3'",
            "  .char '4'",
            "  .char '5'",
            '  .byte 0x00',
            '',
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 5: other("12345")',
            '  PUSHADDR other_param_param',
            '  PUSHADDR _test_local_function_string_data_1',
            '  ; __test__ line 5: "12345"',
            '  CALL strcpy',
            '  ADDPCI 2',
            '  CALL other',
            '  ; __test__ line 4: def func() -> void:',
            '  ; Restoring all clobbered registers.',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

        func = textwrap.dedent("""
            def other(param: str[12]) -> extern[void]: ...

            def func() -> void:
                some_str: str[12] = "12345"
                other(some_str)
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            '_test_local_function_string_data_2:',
            "  .char '1'",
            "  .char '2'",
            "  .char '3'",
            "  .char '4'",
            "  .char '5'",
            '  .byte 0x00',
            '',
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 5: some_str: str[12] = "12345"',
            '  PUSHADDR _test_func_some_str',
            '  PUSHADDR _test_local_function_string_data_2',
            '  ; __test__ line 5: "12345"',
            '  CALL strcpy',
            '  ; __test__ line 6: other(some_str)',
            '  ADDPCI 2',
            '  PUSHADDR other_param_param',
            '  ADDPCI 3',
            '  LOAD A',
            '  SUBPCI 4',
            '  STORE A',
            '  ADDPCI 3',
            '  LOAD A',
            '  SUBPCI 4',
            '  STORE A',
            '  ; __test__ line 6: some_str',
            '  CALL strcpy',
            '  ADDPCI 2',
            '  CALL other',
            '  ; __test__ line 4: def func() -> void:',
            '  ; Restoring all clobbered registers.',
            '  ADDPCI 2',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertEqual([
            '_test_func_some_str:',
            '  .pad 12'
        ], output.data)
        self.assertTrue(len(output.init) == 0)

    def test_correct_const_str_parameters(self) -> None:
        """
        Verify that we do not generate a strcpy for safe expressions to a const[str] function parameter. Since
        we know the function isn't going to modify the const, we can safely allow this optimization.
        """

        compiler = Compiler(CompilerSettings())
        func = textwrap.dedent("""
            def other(param: const[str]) -> extern[void]: ...

            def func() -> void:
                other("12345")
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            '_test_local_function_string_data_1:',
            "  .char '1'",
            "  .char '2'",
            "  .char '3'",
            "  .char '4'",
            "  .char '5'",
            '  .byte 0x00',
            '',
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 5: other("12345")',
            '  PUSHADDR _test_local_function_string_data_1',
            '  CALL other',
            '  ; __test__ line 4: def func() -> void:',
            '  ; Restoring all clobbered registers.',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

        func = textwrap.dedent("""
            def other(param: const[str]) -> extern[void]: ...

            def func() -> void:
                some_const: const[str] = "12345"
                other(some_const)
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            '_test_local_function_string_data_2:',
            "  .char '1'",
            "  .char '2'",
            "  .char '3'",
            "  .char '4'",
            "  .char '5'",
            '  .byte 0x00',
            '',
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 5: some_const: const[str] = "12345"',
            '  PUSHADDR _test_local_function_string_data_2',
            '  ; __test__ line 6: other(some_const)',
            '  LOAD A',
            '  SUBPCI 2',
            '  STORE A',
            '  ADDPCI 3',
            '  LOAD A',
            '  SUBPCI 2',
            '  STORE A',
            '  SUBPCI 1',
            '  CALL other',
            '  ; __test__ line 4: def func() -> void:',
            '  ; Restoring all clobbered registers.',
            '  ADDPCI 2',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertTrue(len(output.data) == 0)
        self.assertTrue(len(output.init) == 0)

        func = textwrap.dedent("""
            def other(param: const[str]) -> extern[void]: ...

            def func() -> void:
                some_str: str[12] = "12345"
                other(some_str)
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            '_test_local_function_string_data_3:',
            "  .char '1'",
            "  .char '2'",
            "  .char '3'",
            "  .char '4'",
            "  .char '5'",
            '  .byte 0x00',
            '',
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 5: some_str: str[12] = "12345"',
            '  PUSHADDR _test_func_some_str',
            '  PUSHADDR _test_local_function_string_data_3',
            '  ; __test__ line 5: "12345"',
            '  CALL strcpy',
            '  ; __test__ line 6: other(some_str)',
            '  ADDPCI 3',
            '  LOAD A',
            '  SUBPCI 2',
            '  STORE A',
            '  ADDPCI 1',
            '  LOAD A',
            '  SUBPCI 2',
            '  STORE A',
            '  CALL other',
            '  ; __test__ line 4: def func() -> void:',
            '  ; Restoring all clobbered registers.',
            '  ADDPCI 2',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertEqual([
            '_test_func_some_str:',
            '  .pad 12'
        ], output.data)
        self.assertTrue(len(output.init) == 0)

        # This is non-trivial so it needs a strcpy to a local expression temp.
        func = textwrap.dedent("""
            def other(param: const[str]) -> extern[void]: ...

            def ret() -> extern[str]: ...

            def func() -> void:
                other(ret())
        """)

        output = compiler.parse_and_compile_module("__test__", func)
        self.assertEqual([
            'func:',
            '  ; Stack layout just after call:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Stack layout just before return:',
            '  ; PC + 0 - builtin(retptr)',
            '  ; PC + 1 - builtin(retptr)',
            '  ;',
            '  ; Save clobbered registers',
            '  PUSH A',
            '  ; __test__ line 7: other(ret())',
            '  SUBPCI 4',
            '  CALL ret',
            '  ADDPCI 4',
            '  PUSHADDR _test_func_builtin_expr_temp_5',
            '  LOAD A',
            '  SUBPCI 4',
            '  STORE A',
            '  ADDPCI 5',
            '  LOAD A',
            '  SUBPCI 4',
            '  STORE A',
            '  ADDPCI 2',
            '  LOAD A',
            '  SUBPCI 4',
            '  STORE A',
            '  ADDPCI 3',
            '  LOAD A',
            '  SUBPCI 4',
            '  STORE A',
            '  ; __test__ line 7: ret()',
            '  CALL strcpy',
            '  ADDPCI 6',
            '  CALL other',
            '  ; __test__ line 6: def func() -> void:',
            '  ; Restoring all clobbered registers.',
            '  POP A',
            '  RET'
        ], output.code)
        self.assertEqual([
            '_test_func_builtin_expr_temp_5:',
            '  .pad 127'
        ], output.data)
        self.assertTrue(len(output.init) == 0)
