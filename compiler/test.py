import textwrap
import unittest

from .core import CompilerError, FunctionPrototype, NoneType, parse_prototypes, parse_and_compile


class TestCompiler(unittest.TestCase):
    def test_empty(self) -> None:
        output = parse_and_compile("__test__", "", [])
        assert len(output) == 0

    def test_throw_on_top_level_statement(self) -> None:
        with self.assertRaises(CompilerError) as cm:
            parse_and_compile("__test__", 'print("Hello, world!")', [])
        self.assertEqual("__test__ Line 1: Arbitrary top-level statements are not supported", str(cm.exception))

    def test_allow_global_const_declaration_init(self) -> None:
        output = parse_and_compile("__test__", 'UINT8_CONST: const[int8] = 123', [])
        self.assertEqual(['UINT8_CONST:', '  .byte 0x7b'], output)

        output = parse_and_compile("__test__", 'UINT16_CONST: const[int16] = 0xCAFE', [])
        self.assertEqual(['UINT16_CONST:', '  .byte 0xca', '  .byte 0xfe'], output)

        output = parse_and_compile("__test__", 'UINT32_CONST: const[int32] = 0xDEADBEEF', [])
        self.assertEqual(['UINT32_CONST:', '  .byte 0xde', '  .byte 0xad', '  .byte 0xbe', '  .byte 0xef'], output)

        output = parse_and_compile("__test__", "UINT8_CONST: const[char] = 'c'", [])
        self.assertEqual(['UINT8_CONST:', "  .char 'c'"], output)

        output = parse_and_compile("__test__", 'UINT8_CONST: const[string] = "test"', [])
        self.assertEqual(['UINT8_CONST:', "  .char 't'", "  .char 'e'", "  .char 's'", "  .char 't'", "  .byte 0x00"], output)

    def test_allow_global_const_declaration_init_expr(self) -> None:
        output = parse_and_compile("__test__", 'UINT8_CONST: const[int8] = (7 * 2) + 1', [])
        self.assertEqual(['UINT8_CONST:', '  .byte 0x0f'], output)

    def test_throw_on_global_const_declaration(self) -> None:
        with self.assertRaises(CompilerError) as cm:
            parse_and_compile("__test__", 'UINT8_CONST: const[int8]', [])
        self.assertEqual("__test__ Line 1: Expecting initialization value for global const definition", str(cm.exception))

    def test_throw_on_global_no_type(self) -> None:
        with self.assertRaises(CompilerError) as cm:
            parse_and_compile("__test__", 'SOME_CONST = 123', [])
        self.assertEqual("__test__ Line 1: Global variable declarations must have a type", str(cm.exception))

    def test_define_simple_function(self) -> None:
        func = textwrap.dedent("""
            def simple() -> None:
                return
        """)

        prototypes = parse_prototypes("__test__", func)
        self.assertEqual([FunctionPrototype("simple", NoneType, [])], prototypes)

        output = parse_and_compile("__test__", func, [])
        self.assertEqual([], output)


if __name__ == '__main__':
    unittest.main()
