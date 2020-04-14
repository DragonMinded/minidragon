udiv:
    ; Divide an unsigned number by another unsigned number, returning the
    ; quotient in A and the remainder on the stack. Works on unsigned
    ; numbers in the range of 0-127 inclusive.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to divide 15 by 3, call this similar to:
    ;   PUSHI 3
    ;   PUSHI 15
    ;   CALL udiv
    ;
    ; Stack layout at call time
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - dividend
    ; PC + 3 - divisor
    ;
    ; Stack layout during division
    ; PC + 0 - quotient
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - divisor
    ; PC + 4 - remainder

    ; Swap dividend/divisor so we can accumulate the remainder in
    ; the right spot.
    ADDPCI 2
    LOAD A
    SUBPCI 3
    STORE A

    ADDPCI 4
    LOAD A
    DECPC
    STORE A

    SUBPCI 3
    LOAD A
    ADDPCI 4
    STORE A

    ; Now, zero out the quotient
    SUBPCI 4
    SETA 0
    STORE A

_udiv_loop:
    ; Attempt to subtract the divisor from the dividend
    ADDPCI 3
    LOAD A
    NEG
    INCPC
    ADD

    ; If we went negative, then the dividend is the remainder
    ; and we've finished. The accumulated result is the quotient.
    SUBPCI 5
    STORE A
    SHL
    LOAD A
    ADDPCI 5
    JRIC _udiv_finished

    ; Save the last value as the new dividend.
    STORE A

    ; Increment the quotient.
    SUBPCI 4
    LOAD A
    INC
    STORE A

    ; Finally, do it all over again!
    JRI _udiv_loop

_udiv_finished:
    ; Move the return address to the right spot on the stack
    SUBPCI 2
    LOAD A
    INCPC
    STORE A
    SUBPCI 2
    LOAD A
    INCPC
    STORE A

    ; Now, restore the quotient
    SUBPCI 2
    POP A
    INCPC

    ; Finally, return
    RET
