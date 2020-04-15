udiv:
    ; Divide an unsigned number by another unsigned number, returning the
    ; quotient in A and the remainder on the stack. Assumes that dividend
    ; and divisor are unsigned numbers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to divide 15 by 3, call this similar to:
    ;   PUSHI 3
    ;   PUSHI 15
    ;   CALL udiv
    ;
    ; Stack layout at call time
    ; PC + 0 - accumulator (partial remainder)
    ; PC + 1 - divisor
    ; PC + 2 - saved U register
    ; PC + 3 - saved V register
    ; PC + 4 - return address
    ; PC + 5 - return address
    ; PC + 6 - dividend
    ; PC + 7 - divisor

    ; First, save the U/V registers
    PUSH V
    PUSH U

    ; Now, preload, with U = quotient (starts at zero)
    ZERO
    SWAP A, U

    ; Preload A = divisor
    ADDPCI 5
    LOAD A

    ; Preload V = remainder
    DECPC
    LOAD V

    ; Move so we can call cmp later
    SUBPCI 5
    STORE A
    DECPC

    ; Now, make sure V = -divisor and A = remainder
    NEG
    SWAP A, V

_udiv_loop:
    ; First, see if divisor < remainder
    STORE A
    CALL ucmp

    ; If we returned negative, that means we still have work to do
    NEG
    SHL
    JRIC _udiv_finished

    ; We can subtract the divisor from the accumulated remainder now,
    ; we know that it is less than the remainder.
    LOAD A
    ADDV

    ; Increment the quotient.
    SWAP A, U
    INC
    SWAP U, A

    ; Finally, do it all over again!
    JRI _udiv_loop

_udiv_finished:
    ; First, restore the remainder
    LOAD A
    ADDPCI 7
    STORE A

    ; Move the return address to the right spot on the stack
    SUBPCI 2
    LOAD A
    INCPC
    STORE A
    SUBPCI 2
    LOAD A
    INCPC
    STORE A

    ; Now, move the quotient out of U
    MOV U, A

    ; Restore U/V registers
    SUBPCI 3
    POP U
    POP V

    ; Finally, return
    INCPC
    RET
