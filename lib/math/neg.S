neg:
    ; Given an integer on the stack, assume it is a two's compliment number
    ; and return the negation of it in the A register. This function is
    ; somewhat useless as there's an assembler macro for it, but it keeps
    ; the stdlib orthogonal. Does not clobber the U/V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; Call this similar to:
    ;     PUSHI -32
    ;     CALL neg
    ;
    ; Stack layout:
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - number to negate

    ; Negate the number on the stack.
    ADDPCI 2
    LOAD A
    NEG
    SUBPCI 2

    ; Restore A, return.
    RET

neg16:
    ; Given a 16-bit integer on the stack, assume it is a two's compliment
    ; number and return the negation of the number on the stack. Does not
    ; clobber the A, U, V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To negate an integer 12345, call this similar to:
    ;     PUSHI 0x39
    ;     PUSHI 0x30
    ;     CALL neg16
    ;
    ; Stack layout:
    ; PC + 0 - saved A register
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - number to negate high byte
    ; PC + 4 - number to negate low byte

    ; Save the A register.
    PUSH A
    ADDPCI 3

    ; Negate the number on the stack.
    LOAD A
    INV
    STORE A
    INCPC
    LOAD A
    NEG
    STORE A
    DECPC
    ZERO
    ADC
    STORE A

    ; Restore A, return.
    SUBPCI 3
    POP A
    RET

neg32:
    ; Given a 32-bit integer on the stack, assume it is a two's compliment
    ; number and return the negation of it. Does not clobber the A, U, V
    ; or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To negate an integer 12345678, call this similar to:
    ;     PUSHI 0x4E
    ;     PUSHI 0x61
    ;     PUSHI 0xBC
    ;     PUSHI 0x00
    ;     CALL neg32
    ;
    ; Stack layout:
    ; PC + 0 - saved A register
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - number to negate
    ; PC + 4 - number to negate
    ; PC + 5 - number to negate
    ; PC + 6 - number to negate

    ; Save the A register.
    PUSH A
    ADDPCI 3

    ; Negate the number on the stack.
    LOAD A
    INV
    STORE A
    INCPC
    LOAD A
    INV
    STORE A
    INCPC
    LOAD A
    INV
    STORE A
    INCPC

    LOAD A
    NEG
    STORE A

    DECPC
    ZERO
    ADC
    STORE A
    DECPC
    ZERO
    ADC
    STORE A
    DECPC
    ZERO
    ADC
    STORE A

    ; Restore A, return.
    SUBPCI 3
    POP A
    RET
