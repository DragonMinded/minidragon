add16:
    ; Add two 16-bit numbers on the stack, returning the value on the stack.
    ; Numbers are stored on the stack as big-endian. Does not mess with the
    ; A register.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To add 0x1234 to 0x5678, call like so:
    ;   PUSHI 0x78
    ;   PUSHI 0x56
    ;   PUSHI 0x34
    ;   PUSHI 0x12
    ;   CALL add16
    ;
    ; Stack layout
    ; PC + 0 - saved A register
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - first operand high byte
    ; PC + 4 - first operand low byte
    ; PC + 5 - second operand high byte
    ; PC + 6 - second operand low byte

    ; Save the A register
    PUSH

    ; First, add the low bytes together, possibly setting the carry
    ADDPC 4
    LOAD
    ADDPC 2
    ADD
    STORE

    ; Now, add the high bytes together, including the carry
    SUBPC 3
    LOAD
    ADDPC 2
    ADC
    STORE

    ; Now, copy the return up two in the stack so we can pop and ret
    ; while leaving the return value on the stack. First two are for
    ; the return address, next is for the A register.
    SUBPC 3
    LOAD
    ADDPC 2
    STORE
    SUBPC 3
    LOAD
    ADDPC 2
    STORE

    SUBPC 3
    LOAD
    ADDPC 2
    STORE

    ; Finally, return to caller
    POP
    RET

add32:
    ; Add two 32-bit numbers on the stack, returning the value on the stack.
    ; Numbers are stored on the stack as big-endian. Does not mess with the
    ; A register.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To add 0x12345678 to 0x55555555, call like so:
    ;   PUSHI 0x78
    ;   PUSHI 0x56
    ;   PUSHI 0x34
    ;   PUSHI 0x12
    ;   PUSHI 0x55
    ;   PUSHI 0x55
    ;   PUSHI 0x55
    ;   PUSHI 0x55
    ;   CALL add32
    ;
    ; Stack layout
    ; PC + 0  - saved A register
    ; PC + 1  - return address
    ; PC + 2  - return address
    ; PC + 3  - first operand
    ; PC + 4  - first operand
    ; PC + 5  - first operand
    ; PC + 6  - first operand
    ; PC + 7  - second operand
    ; PC + 8  - second operand
    ; PC + 9  - second operand
    ; PC + 10 - second operand

    ; Save the A register
    PUSH

    ; First, add the low bytes together, possibly setting the carry
    ADDPC 6
    LOAD
    ADDPC 4
    ADD
    STORE

    ; Now, add the next three byte sequenes together, adding in the carry
    SUBPC 5
    LOAD
    ADDPC 4
    ADC
    STORE

    SUBPC 5
    LOAD
    ADDPC 4
    ADC
    STORE

    SUBPC 5
    LOAD
    ADDPC 4
    ADC
    STORE

    ; Now, copy the return up two in the stack so we can pop and ret
    ; while leaving the return value on the stack. First two are for
    ; the return address, next is for the A register.
    SUBPC 5
    LOAD
    ADDPC 4
    STORE
    SUBPC 5
    LOAD
    ADDPC 4
    STORE

    SUBPC 5
    LOAD
    ADDPC 4
    STORE

    ; Finally, return to caller
    POP
    RET
