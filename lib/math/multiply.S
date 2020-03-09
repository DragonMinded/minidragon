_multiply_locals:
    .byte 0x01  ; Bottom bit set constant

multiply:
    ; Multiply two 8-bit numbers on the stack, returning value in A.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; Call this similar to:
    ;   PUSHI 5
    ;   PUSHI 7
    ;   CALL multiply
    ;
    ; Stack layout
    ; PC + 0 - SP
    ; PC + 1 - SC
    ; PC + 2 - Accumulated result
    ; PC + 3 - return address
    ; PC + 4 - return address
    ; PC + 5 - first operand
    ; PC + 6 - second operand

    ; Make room on the stack for the accumulated result
    PUSHI 0

    ; Save calling function's local stack.
    PUSHSPC

    ; Skip to first operand
    ADDPCI 5

    ; Initialize our own local stack
    SWAP
    SETPC _multiply_locals
    SWAP

_multiply_loop:
    ; See if first operand is zero
    ZERO
    ADD
    LNGJUMPZ _multiply_finished

    ; See if bottom bit set
    SWAP
    AND
    SWAP
    JRIZ _multiply_shift

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

_multiply_shift:
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
    LNGJUMP _multiply_loop

_multiply_finished:
    ; Restore stack
    SUBPCI 5

    ; Restore locals pointer.
    POPSPC

    ; Grab the accumulated value to return it in A.
    POP

    ; And done!
    RET
