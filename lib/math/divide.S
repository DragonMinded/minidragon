divide:
    ; Divide a number by another number, returning the quotient in A and
    ; the remainder on the stack. Works on unsigned numbers in the range
    ; of 0-127 inclusive.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to divide 15 by 3, call this similar to:
    ;   PUSHI 3
    ;   PUSHI 15
    ;   CALL divide
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
    LOAD
    SUBPCI 2
    PUSH

    ADDPCI 4
    LOAD
    DECPC
    STORE

    SUBPCI 3
    LOAD
    ADDPCI 4
    STORE

    ; Now, zero out the quotient
    SUBPCI 4
    SETA 0
    STORE

_div_loop:
    ; Attempt to subtract the divisor from the dividend
    ADDPCI 3
    LOAD
    NEG
    INCPC
    ADD

    ; If we went negative, then the dividend is the remainder
    ; and we've finished. The accumulated result is the quotient.
    SUBPCI 4
    PUSH
    SHL
    POP
    ADDPCI 4
    JRIC _div_finished

    ; Save the last value as the new dividend.
    STORE

    ; Increment the quotient.
    SUBPCI 4
    LOAD
    INC
    STORE

    ; Finally, do it all over again!
    JRI _div_loop

_div_finished:
    ; Move the return address to the right spot on the stack
    SUBPCI 2
    LOAD
    INCPC
    STORE
    SUBPCI 2
    LOAD
    INCPC
    STORE

    ; Now, restore the quotient
    SUBPCI 2
    POP
    INCPC

    ; Finally, return
    RET
