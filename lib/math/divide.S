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
    ; PC + ? - divisor copy
    ; PC + ? - remainder
    ; PC + ? - saved U register
    ; PC + ? - saved V register
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - dividend
    ; PC + ? - divisor

    ; First, save the U/V registers
    PUSH V
    PUSH U

    ; Now, preload U = loop value
    LOADI 8
    MOV A, U

    ; And preload V = quotient
    ZERO
    MOV A, V

    ; Initialize the remainder
    PUSH A

    ; Initialize the divisor copy so we can call ucmp easier.
    ADDPCI 6
    LOAD A
    SUBPCI 7
    STORE A

_udiv_loop:
    ; First, shift out the top bit from the dividend, so we can shift
    ; it into the remainder accumulator.
    ADDPCI 6
    LOAD A
    SHL
    STORE A
    SUBPCI 5

    ; Shift the bit into the remainder to accumulate it.
    LOAD A
    RCL
    STORE A
    DECPC

    ; First, check if the remainder is zero (which it will be in a
    ; LOT of cases). We know if the remainder is zero, that the
    ; divisor will be greater since you aren't allowed to divide
    ; by zero.
    ADDI 0
    JRIZ _udiv_shift_quotient

    ; Now, see if the remainder is larger than the divisor.
    CALL ucmp
    SHL
    JRINC _udiv_sub_divisor

_udiv_shift_quotient:
    ; Remainder is less than the divisor, so just shift our quotient
    ; and loop again.
    MOV V, A
    SHL
    MOV A, V
    JRI _udiv_check_termination

_udiv_sub_divisor:
    ; The divisor fits into the remainder, so we have a single bit
    ; division result. Reflect that in the quotient and then drop
    ; the remainder down by the divisor.
    MOV V, A
    SHL
    ADDI 1
    MOV A, V

    ; Load the divisor, negate it and add it to the remainder.
    LOAD A
    NEG
    INCPC
    ADD
    STORE A
    DECPC

_udiv_check_termination:
    ; Now, see if we need to loop or if we're done here.
    MOV U, A
    ADDI -1
    MOV A, U

    ; If it is zero, we've done all the loops we need.
    LNGJUMPNZ _udiv_loop

    ; We're finished, so restore all the values to their correct place.
    ; Stack layout should look like this once we finish:
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - remainder

    ; First, relocate the remainder where it should go.
    INCPC
    LOAD A
    ADDPCI 6
    STORE A

    ; Now, relocate the return address so we can pop it later.
    SUBPCI 2
    LOAD A
    INCPC
    STORE A
    SUBPCI 2
    LOAD A
    INCPC
    STORE A

    ; Put the quotient in A where we promise it to be.
    MOV V, A

    ; Now, restore the U/V registers.
    SUBPCI 3
    POP U
    POP V

    ; Finally, return the calculated values!
    INCPC
    ret
