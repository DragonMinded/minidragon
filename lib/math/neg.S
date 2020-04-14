neg:
    ; Given an integer on the stack, assume it is a two's compliment
    ; number and return the negation of it. This function is somewhat useless
    ; as there's an assembler macro for it, but it keeps the stdlib orthogonal.
    ; Does not mess with the A register.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; Call this similar to:
    ;     PUSHI -32
    ;     CALL neg
    ;
    ; Stack layout:
    ; PC + 0 - saved A register
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - number to negate

    ; Save the A register.
    PUSH

    ; Negate the number on the stack.
    ADDPCI 3
    LOADA
    NEG
    STOREA
    SUBPCI 3

    ; Restore A, return.
    POP
    RET

neg16:
    ; Given a 16-bit integer on the stack, assume it is a two's compliment
    ; number and return the negation of it. Does not mess with the A register.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To negate an integer 12345, call this similar to:
    ;     PUSH 0x39
    ;     PUSH 0x30
    ;     CALL neg16
    ;
    ; Stack layout:
    ; PC + 0 - saved A register
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - number to negate high byte
    ; PC + 4 - number to negate low byte

    ; Save the A register.
    PUSH
    ADDPCI 3

    ; Negate the number on the stack.
    LOADA
    INV
    STOREA
    INCPC
    LOADA
    INV
    ADDI 1
    STOREA
    DECPC
    ZERO
    ADC
    STOREA

    ; Restore A, return.
    SUBPCI 3
    POP
    RET

neg32:
    ; Given a 32-bit integer on the stack, assume it is a two's compliment
    ; number and return the negation of it. Does not mess with the A register.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To negate an integer 12345678, call this similar to:
    ;     PUSH 0x4E
    ;     PUSH 0x61
    ;     PUSH 0xBC
    ;     PUSH 0x00
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
    PUSH
    ADDPCI 3

    ; Negate the number on the stack.
    LOADA
    INV
    STOREA
    INCPC
    LOADA
    INV
    STOREA
    INCPC
    LOADA
    INV
    STOREA
    INCPC

    LOADA
    INV
    ADDI 1
    STOREA

    DECPC
    ZERO
    ADC
    STOREA
    DECPC
    ZERO
    ADC
    STOREA
    DECPC
    ZERO
    ADC
    STOREA

    ; Restore A, return.
    SUBPCI 3
    POP
    RET
