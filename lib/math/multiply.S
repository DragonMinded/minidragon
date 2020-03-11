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
    PUSHSPC

    ; Skip to first operand
    ADDPCI 5

    ; Initialize our own local stack
    SWAP
    SETPC _mult_locals
    SWAP

_umult_loop:
    ; See if first operand is zero
    ZERO
    ADD
    LNGJUMPZ _umult_finished

    ; See if bottom bit set
    SWAP
    AND
    SWAP
    JRIZ _umult_shift

    ; Grab the second operand so we can add it to the
    ; accumulated result.
    INCPC
    LOAD
    DECPC

    ; Add it to the accumulated result in our local stack.
    SUBPCI 3
    ADD
    STORE
    ADDPCI 3

_umult_shift:
    ; First operand >>= 1
    LOAD
    SHR
    STORE

    ; Second operand <<= 1
    INCPC
    LOAD
    SHL
    STORE
    DECPC

    ; Back to loop
    LNGJUMP _umult_loop

_umult_finished:
    ; Restore stack
    SUBPCI 5

    ; Restore locals pointer.
    POPSPC

    ; Grab the accumulated value to return it in A.
    POP

    ; And done!
    RET
