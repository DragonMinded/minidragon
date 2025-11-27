    ; Direct processor execution past the jump table so we don't try to execute any of it.
    LNGJUMP jumptable_end

    ; A bunch of references to stdlib functions that the compiler will generate jumps to. Must remain in the
    ; order specified or previously-linked cartridges will misbehave. Always add to the end.
jumptable_abs8:
    LNGJUMP abs8
jumptable_abs16:
    LNGJUMP abs16
jumptable_abs32:
    LNGJUMP abs32
jumptable_add8:
    LNGJUMP add8
jumptable_add16:
    LNGJUMP add16
jumptable_add32:
    LNGJUMP add32
jumptable_cmp8:
    LNGJUMP cmp8
jumptable_ucmp8:
    LNGJUMP ucmp8
jumptable_cmp16:
    LNGJUMP cmp16
jumptable_ucmp16:
    LNGJUMP ucmp16
jumptable_cmp32:
    LNGJUMP cmp32
jumptable_ucmp32:
    LNGJUMP ucmp32
jumptable_min8:
    LNGJUMP min8
jumptable_umin8:
    LNGJUMP umin8
jumptable_min16:
    LNGJUMP min16
jumptable_umin16:
    LNGJUMP umin16
jumptable_min32:
    LNGJUMP min32
jumptable_umin32:
    LNGJUMP umin32
jumptable_max8:
    LNGJUMP max8
jumptable_umax8:
    LNGJUMP umax8
jumptable_max16:
    LNGJUMP max16
jumptable_umax16:
    LNGJUMP umax16
jumptable_max32:
    LNGJUMP max32
jumptable_umax32:
    LNGJUMP umax32
jumptable_udiv8:
    LNGJUMP udiv8
jumptable_udiv16:
    LNGJUMP udiv16
jumptable_udiv32:
    LNGJUMP udiv32
jumptable_mult8:
    LNGJUMP mult8
jumptable_mult16:
    LNGJUMP mult16
jumptable_mult32:
    LNGJUMP mult32
jumptable_neg8:
    LNGJUMP neg8
jumptable_neg16:
    LNGJUMP neg16
jumptable_neg32:
    LNGJUMP neg32
jumptable_lshift8:
    LNGJUMP lshift8
jumptable_lshift16:
    LNGJUMP lshift16
jumptable_lshift32:
    LNGJUMP lshift32
jumptable_rshift8:
    LNGJUMP rshift8
jumptable_rshift16:
    LNGJUMP rshift16
jumptable_rshift32:
    LNGJUMP rshift32
jumptable_strcat:
    LNGJUMP strcat
jumptable_strcpy:
    LNGJUMP strcpy
jumptable_strncpy:
    LNGJUMP strncpy
jumptable_strlen:
    LNGJUMP strlen
jumptable_strcmp:
    LNGJUMP strcmp
jumptable_itoa8:
    LNGJUMP itoa8
jumptable_utoa8:
    LNGJUMP utoa8
jumptable_itoa16:
    LNGJUMP itoa16
jumptable_utoa16:
    LNGJUMP utoa16
jumptable_itoa32:
    LNGJUMP itoa32
jumptable_utoa32:
    LNGJUMP utoa32
jumptable_atoi8:
    LNGJUMP atoi8
jumptable_atoi16:
    LNGJUMP atoi16
jumptable_atoi32:
    LNGJUMP atoi32
jumptable_itohex8:
    LNGJUMP itohex8
jumptable_itohex16:
    LNGJUMP itohex16
jumptable_itohex32:
    LNGJUMP itohex32
jumptable_serial_has_byte:
    LNGJUMP serial_has_byte
jumptable_serial_recv_byte:
    LNGJUMP serial_recv_byte
jumptable_serial_send_byte:
    LNGJUMP serial_send_byte
jumptable_serial_clear:
    LNGJUMP serial_clear
jumptable_serial_normal:
    LNGJUMP serial_normal
jumptable_serial_bold:
    LNGJUMP serial_bold
jumptable_serial_underline:
    LNGJUMP serial_underline
jumptable_serial_reverse:
    LNGJUMP serial_reverse
jumptable_serial_send:
    LNGJUMP serial_send
jumptable_serial_recv:
    LNGJUMP serial_recv
jumptable_serial_input:
    LNGJUMP serial_input
jumptable_cartridge_banks:
    LNGJUMP cartridge_banks
jumptable_cartridge_select_bank:
    LNGJUMP cartridge_select_bank
jumptable_cartridge_input:
    LNGJUMP cartridge_input
jumptable_cartridge_expansion:
    LNGJUMP cartridge_expansion
jumptable_strtofixed:
    LNGJUMP strtofixed
jumptable_fixetostr:
    LNGJUMP fixedtostr
jumptable_serial_move:
    LNGJUMP serial_move

    ; Now that we're done defining a jump table, resume execution here.
jumptable_end:
