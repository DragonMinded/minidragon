_mult_locals:
    .byte 0x01  ; Bottom bit set constant

umult:
    ; Multiply two unsigned 8-bit numbers on the stack, returning value
    ; in A.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; Call this similar to:
    ;   PUSHI 5
    ;   PUSHI 7
    ;   CALL umult
    ;
    ; Stack layout
    ; PC + 0 - SP
    ; PC + 1 - SC
    ; PC + 2 - Accumulated result
    ; PC + 3 - return address
    ; PC + 4 - return address
    ; PC + 5 - second operand
    ; PC + 6 - first operand

    ; Make room on the stack for the accumulated result
    PUSHI 0

    ; Save calling function's local stack.
    PUSH SPC

    ; Skip to first operand
    ADDPCI 5

    ; Initialize our own local stack
    SWAP PC, SPC
    SETPC _mult_locals
    SWAP PC, SPC

_umult_loop:
    ; See if first operand is zero
    ZERO
    ADD
    LNGJUMPZ _umult_finished

    ; See if bottom bit set
    SWAP PC, SPC
    AND
    SWAP PC, SPC
    JRIZ _umult_shift

    ; Grab the second operand so we can add it to the
    ; accumulated result.
    INCPC
    LOAD A
    DECPC

    ; Add it to the accumulated result in our local stack.
    SUBPCI 3
    ADD
    STORE A
    ADDPCI 3

_umult_shift:
    ; First operand >>= 1
    LOAD A
    SHR
    STORE A

    ; Second operand <<= 1
    INCPC
    LOAD A
    SHL
    STORE A
    DECPC

    ; Back to loop
    LNGJUMP _umult_loop

_umult_finished:
    ; Restore stack
    SUBPCI 5

    ; Restore locals pointer.
    POP SPC

    ; Grab the accumulated value to return it in A.
    POP A

    ; And done!
    RET
