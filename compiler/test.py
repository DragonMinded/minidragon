import textwrap
import unittest

from .core import CompilerError, FunctionPrototype, CoreType, PaddingCoreType, NoneType, parse_prototypes, parse_and_compile


class TestCompiler(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.maxDiff = None

    def test_empty(self) -> None:
        output = parse_and_compile("__test__", "", [])
        assert len(output) == 0

    def test_throw_on_top_level_statement(self) -> None:
        with self.assertRaises(CompilerError) as cm:
            parse_and_compile("__test__", 'print("Hello, world!")', [])
        self.assertEqual("__test__ line 1: Arbitrary top-level statements are not supported", str(cm.exception))

    def test_allow_global_const_declaration_init(self) -> None:
        output = parse_and_compile("__test__", 'UINT8_CONST: const[int8] = 123', [])
        self.assertEqual([
            '  ; __test__ line 1: UINT8_CONST: const[int8] = 123',
            'UINT8_CONST:',
            '  .byte 0x7b',
        ], output)

        output = parse_and_compile("__test__", 'UINT16_CONST: const[int16] = 0xCAFE', [])
        self.assertEqual([
            '  ; __test__ line 1: UINT16_CONST: const[int16] = 0xCAFE',
            'UINT16_CONST:',
            '  .byte 0xca',
            '  .byte 0xfe',
        ], output)

        output = parse_and_compile("__test__", 'UINT32_CONST: const[int32] = 0xDEADBEEF', [])
        self.assertEqual([
            '  ; __test__ line 1: UINT32_CONST: const[int32] = 0xDEADBEEF',
            'UINT32_CONST:',
            '  .byte 0xde',
            '  .byte 0xad',
            '  .byte 0xbe',
            '  .byte 0xef',
        ], output)

        output = parse_and_compile("__test__", "UINT8_CONST: const[char] = 'c'", [])
        self.assertEqual([
            "  ; __test__ line 1: UINT8_CONST: const[char] = 'c'",
            "UINT8_CONST:",
            "  .char 'c'",
        ], output)

        output = parse_and_compile("__test__", 'UINT8_CONST: const[string] = "test"', [])
        self.assertEqual([
            '  ; __test__ line 1: UINT8_CONST: const[string] = "test"',
            'UINT8_CONST:',
            "  .char 't'",
            "  .char 'e'",
            "  .char 's'",
            "  .char 't'",
            "  .byte 0x00",
        ], output)

    def test_allow_global_const_declaration_init_expr(self) -> None:
        output = parse_and_compile("__test__", 'UINT8_CONST: const[int8] = (7 * 2) + 1', [])
        self.assertEqual([
            '  ; __test__ line 1: UINT8_CONST: const[int8] = (7 * 2) + 1',
            'UINT8_CONST:',
            '  .byte 0x0f'
        ], output)

    def test_throw_on_global_const_declaration(self) -> None:
        with self.assertRaises(CompilerError) as cm:
            parse_and_compile("__test__", 'UINT8_CONST: const[int8]', [])
        self.assertEqual("__test__ line 1: Expecting initialization value for global const definition", str(cm.exception))

    def test_throw_on_global_no_type(self) -> None:
        with self.assertRaises(CompilerError) as cm:
            parse_and_compile("__test__", 'SOME_CONST = 123', [])
        self.assertEqual("__test__ line 1: Global variable declarations must have a type", str(cm.exception))

    def test_define_simple_function(self) -> None:
        func = textwrap.dedent("""
            def simple() -> None:
                return
        """)

        prototypes = parse_prototypes("__test__", func)
        self.assertEqual([FunctionPrototype("simple", NoneType, [])], prototypes)

        output = parse_and_compile("__test__", func, [])
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
        ], output)

    def test_define_simple_return_function(self) -> None:
        func = textwrap.dedent("""
            def simple() -> int8:
                return 15
        """)

        prototypes = parse_prototypes("__test__", func)
        self.assertEqual([FunctionPrototype("simple", CoreType("int8"), [PaddingCoreType(1)])], prototypes)

        output = parse_and_compile("__test__", func, [])
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
            '  SUBPCI 1',
            '  STORE A',
            '  ; __test__ line 3: return 15',
            '  ; Moving return value to correct location in stack.',
            '  LOAD A',
            '  ADDPCI 4',
            '  STORE A',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 3',
            '  POP A',
            '  RET',
        ], output)

    def test_define_simple_unpadded_return_function(self) -> None:
        func = textwrap.dedent("""
            def simple() -> nopad[int8]:
                return 15
        """)

        prototypes = parse_prototypes("__test__", func)
        self.assertEqual([FunctionPrototype("simple", CoreType("int8"), [])], prototypes)

        output = parse_and_compile("__test__", func, [])
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
        ], output)

    def test_define_simple_input_and_return_function(self) -> None:
        func = textwrap.dedent("""
            def simple(param: int8) -> int8:
                return param + 15
        """)

        prototypes = parse_prototypes("__test__", func)
        self.assertEqual([FunctionPrototype("simple", CoreType("int8"), [CoreType("int8")])], prototypes)

        output = parse_and_compile("__test__", func, [])
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
            '  CALL add',
            '  ADDPCI 2',
            '  STORE A',
            '  ; __test__ line 3: return param + 15',
            '  ; Moving return value to correct location in stack.',
            '  LOAD A',
            '  ADDPCI 4',
            '  STORE A',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 3',
            '  POP A',
            '  RET'
        ], output)

    def test_define_use_const(self) -> None:
        func = textwrap.dedent("""
            def defineconst(param: int8) -> int8:
                SOME_CONST: const[int8] = 5
                return param + SOME_CONST
        """)

        prototypes = parse_prototypes("__test__", func)
        self.assertEqual([FunctionPrototype("defineconst", CoreType("int8"), [CoreType("int8")])], prototypes)

        output = parse_and_compile("__test__", func, [])
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
            '  ; __test__ line 3: 5',
            '  LOADI 0x05',
            '  SUBPCI 2',
            '  STORE A',
            '  ; __test__ line 4: param + SOME_CONST',
            '  ADDPCI 5',
            '  LOAD A',
            '  SUBPCI 6',
            '  STORE A',
            '  ADDPCI 1',
            '  LOAD A',
            '  SUBPCI 2',
            '  STORE A',
            '  CALL add',
            '  ADDPCI 3',
            '  STORE A',
            '  ; __test__ line 4: return param + SOME_CONST',
            '  ; Moving return value to correct location in stack.',
            '  LOAD A',
            '  ADDPCI 4',
            '  STORE A',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 3',
            '  POP A',
            '  RET'
        ], output)

    def test_define_use_variable(self) -> None:
        func = textwrap.dedent("""
            def defineconst(param: int8) -> int8:
                some_var: int8 = 5
                some_var = param + some_var
                return some_var
        """)

        prototypes = parse_prototypes("__test__", func)
        self.assertEqual([FunctionPrototype("defineconst", CoreType("int8"), [CoreType("int8")])], prototypes)

        output = parse_and_compile("__test__", func, [])
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
            '  CALL add',
            '  ADDPCI 2',
            '  STORE A',
            '  ; __test__ line 5: some_var',
            '  LOAD A',
            '  ADDPCI 1',
            '  STORE A',
            '  ; __test__ line 5: return some_var',
            '  ; Moving return value to correct location in stack.',
            '  LOAD A',
            '  ADDPCI 4',
            '  STORE A',
            '  ; Restoring all clobbered registers.',
            '  SUBPCI 3',
            '  POP A',
            '  RET'
        ], output)

    def test_throw_on_local_definition_no_type(self) -> None:
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var = 5
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile("__test__", func, [])
        self.assertEqual("__test__ line 3: Unsupported type for local variable definition", str(cm.exception))

    def test_throw_on_local_const_no_assign(self) -> None:
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                SOME_VAR: const[int8]
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile("__test__", func, [])
        self.assertEqual("__test__ line 3: Expecting initialization value for local const definition", str(cm.exception))

    def test_throw_on_local_type_redefinition(self) -> None:
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                some_var: int8 = 5
                some_var: int8 = 10
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile("__test__", func, [])
        self.assertEqual("__test__ line 4: Unsupported type redefinition for local variable assignment", str(cm.exception))

    def test_throw_on_undefined_local(self) -> None:
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                return some_var
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile("__test__", func, [])
        self.assertEqual("__test__ line 3: Undefined variable reference to 'some_var'", str(cm.exception))

    def test_throw_on_local_const_reassign(self) -> None:
        func = textwrap.dedent("""
            def localvar(param: int8) -> int8:
                SOME_VAR: const[int8] = 10
                SOME_VAR = 5
                return SOME_VAR
        """)

        with self.assertRaises(CompilerError) as cm:
            parse_and_compile("__test__", func, [])
        self.assertEqual("__test__ line 4: Cannot assign to variable 'SOME_VAR' declared const", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
