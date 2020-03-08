add16:
    ; Add two 16-bit numbers on the stack, returning the value on the stack.
    ; Numbers are stored on the stack as big-endian.
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
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - first operand high byte
    ; PC + ? - first operand low byte
    ; PC + ? - second operand high byte
    ; PC + ? - second operand low byte

    ; First, add the low bytes together, possibly setting the carry
    ADDPC 5
    LOAD
    SUBPC 2
    ADD
    ADDPC 2
    STORE

    ; Now, add the high bytes together, including the carry
    SUBPC 1
    LOAD
    SUBPC 2
    ADC
    ADDPC 2
    STORE

    ; Now, copy the return up two in the stack so we can pop and ret
    ; while leaving the return value on the stack.
    SUBPC 3
    LOAD
    ADDPC 2
    STORE
    SUBPC 3
    LOAD
    ADDPC 2
    STORE

    ; Finally, return to caller
    RET
