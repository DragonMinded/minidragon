add:
    ; Add two 8-bit numbers on the stack, returning the value on the stack.
    ; This is somewhat useless as we already have add, but it keeps the
    ; stdlib orthogonal. Does not clobber the A, U, V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To add 0x12 to 0x32, call like so:
    ;   PUSHI 0x12
    ;   PUSHI 0x34
    ;   CALL add
    ;
    ; Stack layout
    ; PC + 0 - saved A register
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - second operand
    ; PC + 4 - first operand

    ; Save the A register
    PUSH A

    ; Add two numbers together
    ADDPCI 3
    POP A
    ADD
    STORE A

    ; Now, copy the return up two in the stack so we can pop and ret
    ; while leaving the return value on the stack. First two are for
    ; the return address, next is for the A register.
    SUBPCI 2
    LOAD A
    ADDPCI 1
    STORE A
    SUBPCI 2
    LOAD A
    ADDPCI 1
    STORE A

    ; Now, restore the A register value.
    SUBPCI 2
    LOAD A
    ADDPCI 2

    ; Finally, return to caller
    RET

add16:
    ; Add two 16-bit numbers on the stack, returning the value on the stack.
    ; Numbers are stored on the stack as big-endian. Does not clobber the
    ; A, U, V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To add 0x1234 to 0x5678, call like so:
    ;   PUSHI 0x34
    ;   PUSHI 0x12
    ;   PUSHI 0x78
    ;   PUSHI 0x56
    ;   CALL add16
    ;
    ; Stack layout
    ; PC + 0 - saved A register
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - second operand high byte
    ; PC + 4 - second operand low byte
    ; PC + 5 - first operand high byte
    ; PC + 6 - first operand low byte

    ; Save the A register
    PUSH A

    ; First, add the low bytes together, possibly setting the carry
    ADDPCI 4
    LOAD A
    ADDPCI 2
    ADD
    STORE A

    ; Now, add the high bytes together, including the carry
    SUBPCI 3
    LOAD A
    ADDPCI 2
    ADC
    STORE A

    ; Now, copy the return up two in the stack so we can pop and ret
    ; while leaving the return value on the stack. First two are for
    ; the return address, next is for the A register.
    SUBPCI 3
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 3
    LOAD A
    ADDPCI 2
    STORE A

    ; Restore the A register.
    SUBPCI 3
    LOAD A
    ADDPCI 3

    ; Finally, return to caller
    RET

add32:
    ; Add two 32-bit numbers on the stack, returning the value on the stack.
    ; Numbers are stored on the stack as big-endian. Does not clobber the
    ; A, U, V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To add 0x12345678 to 0x55555555, call like so:
    ;   PUSHI 0x55
    ;   PUSHI 0x55
    ;   PUSHI 0x55
    ;   PUSHI 0x55
    ;   PUSHI 0x78
    ;   PUSHI 0x56
    ;   PUSHI 0x34
    ;   PUSHI 0x12
    ;   CALL add32
    ;
    ; Stack layout
    ; PC + 0  - saved A register
    ; PC + 1  - return address
    ; PC + 2  - return address
    ; PC + 3  - second operand
    ; PC + 4  - second operand
    ; PC + 5  - second operand
    ; PC + 6  - second operand
    ; PC + 7  - first operand
    ; PC + 8  - first operand
    ; PC + 9  - first operand
    ; PC + 10 - first operand

    ; Save the A register
    PUSH A

    ; First, add the low bytes together, possibly setting the carry
    ADDPCI 6
    LOAD A
    ADDPCI 4
    ADD
    STORE A

    ; Now, add the next three byte sequenes together, adding in the carry
    SUBPCI 5
    LOAD A
    ADDPCI 4
    ADC
    STORE A

    SUBPCI 5
    LOAD A
    ADDPCI 4
    ADC
    STORE A

    SUBPCI 5
    LOAD A
    ADDPCI 4
    ADC
    STORE A

    ; Now, copy the return up two in the stack so we can pop and ret
    ; while leaving the return value on the stack. First two are for
    ; the return address, next is for the A register.
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A

    ; Restore the A register.
    SUBPCI 5
    LOAD A
    ADDPCI 5

    ; Finally, return to caller
    RET
