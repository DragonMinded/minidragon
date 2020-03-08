abs:
    ; Given an integer in the A register, assume it is a two's compliment
    ; number and return the absolute value of the number.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; Call this similar to:
    ;     SETA -32
    ;     CALL abs
    ;
    ; Stack layout:
    ; PC + 0 - return address
    ; PC + 1 - return address

    ; Save the original value of A
    PUSH

    ; Now, check if it is negative.
    SHL
    JRIC _abs_negative

    ; Its already positive, so just return it.
    POP
    RET

_abs_negative:
    ; Gotta two's compliment it.
    POP
    NEG
    RET
