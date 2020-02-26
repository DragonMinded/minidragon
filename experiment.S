    .org 0x8000

stack:
    ; Top of stack for algorithm.

    .org 0x0000

init:
    ; Set up the call stack
    SETPC stack

play:
    ; Lets see if we can multiply.
    PUSHI 12
    PUSHI 12
    CALL multiply

    ; Infinite loop
    HALT

multiply_locals:
    .byte 0x01  ; Bottom bit set constant

multiply:
    ; Multiply two 8-bit numbers on the stack, returning value in A.
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; Stack layout
    ; PC + 0 - SP
    ; PC + 1 - SC
    ; PC + 2 - Accumulated result
    ; PC + 3 - return
    ; PC + 4 - return
    ; PC + 5 - first operand
    ; PC + 6 - second operand

    ; Make room on the stack for the accumulated result
    PUSHI 0

    ; Save calling function's local stack.
    PUSHSPC

    ; Skip to first operand
    ADDPC 5

    ; Initialize our own local stack
    SWAP
    SETPC multiply_locals
    SWAP

multiply_loop:
    ; See if first operand is zero
    ZERO
    ADD
    LNGJUMPZ multiply_finished

    ; See if bottom bit set
    SWAP
    AND
    SWAP
    JRIZ multiply_shift

    ; Grab the second operand so we can add it to the
    ; accumulated result.
    INCPC
    LOAD
    DECPC

    ; Add it to the accumulated result in our local stack.
    SUBPC 3
    ADD
    STORE
    ADDPC 3

multiply_shift:
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
    LNGJUMP multiply_loop

multiply_finished:
    ; Restore stack
    SUBPC 5

    ; Restore locals pointer.
    POPSPC

    ; Grab the accumulated value to return it in A.
    POP

    ; And done!
    RET
