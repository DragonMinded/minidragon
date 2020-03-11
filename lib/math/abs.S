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

abs16:
    ; Given a 16-bit integer on the stack, assume it is a two's compliment
    ; number and return the absolute value of the number. Does not mess with
    ; the A register.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To take the abs of an integer 12345, call this similar to:
    ;     PUSH 0x39
    ;     PUSH 0x30
    ;     CALL abs16
    ;
    ; Stack layout:
    ; PC + 0 - saved A register
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - integer high byte
    ; PC + 4 - integer low byte

    ; Save the original value of A
    PUSH

    ; Now, check if it is negative.
    ADDPCI 3
    LOAD
    SUBPCI 3
    SHL
    JRIC _abs16_negative

    ; Its already positive, so just return it.
    POP
    RET

_abs16_negative:
    ; Gotta two's compliment it. Lets use the neg16 function, and trick
    ; it into jumping to our own return. Restore the A register so neg16
    ; can save it again.
    POP
    LNGJUMP neg16

abs32:
    ; Given a 32-bit integer on the stack, assume it is a two's compliment
    ; number and return the absolute value of the number. Does not mess with
    ; the A register.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To take the abs of an integer 12345678, call this similar to:
    ;     PUSH 0x4E
    ;     PUSH 0x61
    ;     PUSH 0xBC
    ;     PUSH 0x00
    ;     CALL abs32
    ;
    ; Stack layout:
    ; PC + 0 - saved A register
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - integer
    ; PC + 4 - integer
    ; PC + 5 - integer
    ; PC + 6 - integer

    ; Save the original value of A
    PUSH

    ; Now, check if it is negative.
    ADDPCI 3
    LOAD
    SUBPCI 3
    SHL
    JRIC _abs32_negative

    ; Its already positive, so just return it.
    POP
    RET

_abs32_negative:
    ; Gotta two's compliment it. Lets use the neg32 function, and trick
    ; it into jumping to our own return. Restore the A register so neg32
    ; can save it again.
    POP
    LNGJUMP neg32
