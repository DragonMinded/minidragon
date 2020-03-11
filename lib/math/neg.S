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
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - number to negate

    ; Save the A register.
    PUSH

    ; Negate the number on the stack.
    ADDPCI 3
    LOAD
    NEG
    STORE
    SUBPCI 3

    ; Restore A, return.
    POP
    RET
