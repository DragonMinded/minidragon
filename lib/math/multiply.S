umult:
    ; Multiply two unsigned 8-bit numbers on the stack, returning value
    ; in A. Does not clobber U, V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; Call this similar to:
    ;   PUSHI 5
    ;   PUSHI 7
    ;   CALL umult
    ;
    ; Stack layout
    ; PC + 0 - Saved V register
    ; PC + 1 - Saved U register
    ; PC + 2 - return address
    ; PC + 3 - return address
    ; PC + 4 - second operand
    ; PC + 5 - first operand

    ; Save temporary registers.
    PUSH U
    PUSH V

    ; Initialize the accumulator.
    ZERO

    ; Load our first operand into V register...
    ADDPCI 5
    LOAD V

    ; ...and our second operand into the U register.
    DECPC
    LOAD U
    SUBPCI 4

_umult_loop:
    ; See if first operand is zero
    SWAP A, V
    ADDI 0
    LNGJUMPZ _umult_finished

    ; See if first operand's bottom bit set, also perform
    ; first operand >>= 1.
    SHR
    SWAP V, A
    JRINC _umult_shift

    ; Add the second operand to the accumulated result.
    ADDU

_umult_shift:
    ; Second operand <<= 1
    SWAP A, U
    SHL
    SWAP U, A

    ; Back to loop
    LNGJUMP _umult_loop

_umult_finished:
    ; Place accumulated result back into A register (MOV faster than SWAP
    ; in this case).
    MOV V, A

    ; Restore temporary registers.
    POP V
    POP U

    ; And done!
    RET
