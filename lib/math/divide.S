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
    RET

udiv16:
    ; Divide an unsigned 16-bit number by another unsigned 16-bit number,
    ; returning the quotient and the remainder on the stack. Assumes that
    ; dividend and divisor are unsigned numbers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to divide 15000 by 3, call this similar to:
    ;   PUSHI 0x00
    ;   PUSHI 0x03
    ;   PUSHI 0x3A
    ;   PUSHI 0x98
    ;   CALL udiv16
    ;
    ; Stack layout at call time
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - dividend high byte
    ; PC + ? - dividend low byte
    ; PC + ? - divisor high byte
    ; PC + ? - divisor low byte
    ;
    ; Stack layout after initialization
    ; PC + ? - remainder
    ; PC + ? - remainder
    ; PC + ? - divisor copy
    ; PC + ? - divisor copy
    ; PC + ? - saved U register
    ; PC + ? - saved A register
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - dividend high byte
    ; PC + ? - dividend low byte
    ; PC + ? - quotient high byte
    ; PC + ? - quotient low byte

    ; First, save the A and U registers
    PUSH A
    PUSH U

    ; Now, preload U = loop value
    LOADI 16
    MOV A, U

    ; Initialize the divisor copy so we can call ucmp easier.
    ADDPCI 7
    LOAD A
    SUBPCI 8
    STORE A
    ADDPCI 7
    LOAD A
    SUBPCI 8
    STORE A

    ; Initialize the remainder
    ZERO
    PUSH A
    PUSH A

    ; And preload the quotient.
    ADDPCI 10
    ZERO
    STORE A
    INCPC
    STORE A

    ; Start by pointing at the top of the remainder.
    SUBPCI 11

_udiv16_loop:
    ; First, shift out the top bit from the dividend, so we can shift
    ; it into the remainder accumulator. We finish by pointing at the
    ; high byte of the dividend.
    ADDPCI 9
    LOAD A
    SHL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A

    ; Shift the bit into the remainder to accumulate it. We finish by
    ; pointing at the high byte of the remainder.
    SUBPCI 7
    LOAD A
    RCL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A

    ; First, check if the remainder is zero (which it will be in a
    ; LOT of cases). We know if the remainder is zero, that the
    ; divisor will be greater since you aren't allowed to divide
    ; by zero.
    JRINZ _udiv16_need_ucmp
    INCPC
    LOAD A
    ADDI 0
    DECPC
    JRIZ _udiv16_shift_quotient

_udiv16_need_ucmp:
    ; Now, see if the remainder is larger than the divisor.
    CALL ucmp16
    NEG
    SHL
    JRINC _udiv16_sub_divisor

_udiv16_shift_quotient:
    ; Remainder is less than the divisor, so just shift our quotient
    ; and loop again. Make sure to finish by pointing at the high
    ; byte of the remainder.
    ADDPCI 11
    LOAD A
    SHL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A
    SUBPCI 10

    JRI _udiv16_check_termination

_udiv16_sub_divisor:
    ; The divisor fits into the remainder, so we have a single bit
    ; division result. Reflect that in the quotient and then drop
    ; the remainder down by the divisor.
    ADDPCI 11
    LOAD A
    SHL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A
    INCPC
    LOAD A
    ADDI 1
    STORE A

    ; Copy the divisor to negate.
    SUBPCI 8
    LOAD A
    SUBPCI 4
    STORE A
    ADDPCI 3
    LOAD A
    SUBPCI 4
    STORE A

    ; Negate it.
    CALL neg16

    ; Subtract it from the remainder. This puts our stack pointing
    ; back at the modified remainder high byte, with the divisor
    ; subtracted out.
    CALL add16

_udiv16_check_termination:
    ; Now, see if we need to loop or if we're done here.
    MOV U, A
    ADDI -1
    MOV A, U

    ; If it is zero, we've done all the loops we need.
    LNGJUMPNZ _udiv16_loop

    ; We're finished, so restore all the values to their correct place.
    ; Stack layout should look like this once we finish:
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - remainder high byte
    ; PC + ? - remainder low byte
    ; PC + ? - quotient high byte
    ; PC + ? - quotient low byte

    ; First, relocate the remainder where it should go.
    LOAD A
    ADDPCI 8
    STORE A
    SUBPCI 7
    LOAD A
    ADDPCI 8
    STORE A

    ; Now, restore the U and A registers.
    SUBPCI 5
    POP U
    POP A

    ; Finally, return the calculated values!
    RET

udiv32:
    ; Divide an unsigned 32-bit number by another unsigned 32-bit number,
    ; returning the quotient and the remainder on the stack. Assumes that
    ; dividend and divisor are unsigned numbers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to divide 1500000 by 3, call this similar to:
    ;   PUSHI 0x00
    ;   PUSHI 0x00
    ;   PUSHI 0x00
    ;   PUSHI 0x03
    ;   PUSHI 0x00
    ;   PUSHI 0x16
    ;   PUSHI 0xE3
    ;   PUSHI 0x60
    ;   CALL udiv32
    ;
    ; Stack layout at call time
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - dividend high byte
    ; PC + ? - dividend second byte
    ; PC + ? - dividend third byte
    ; PC + ? - dividend low byte
    ; PC + ? - divisor high byte
    ; PC + ? - divisor second byte
    ; PC + ? - divisor third byte
    ; PC + ? - divisor low byte
    ;
    ; Stack layout after initialization
    ; PC + ? - remainder
    ; PC + ? - remainder
    ; PC + ? - remainder
    ; PC + ? - remainder
    ; PC + ? - divisor copy
    ; PC + ? - divisor copy
    ; PC + ? - divisor copy
    ; PC + ? - divisor copy
    ; PC + ? - saved U register
    ; PC + ? - saved A register
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - dividend high byte
    ; PC + ? - dividend second byte
    ; PC + ? - dividend third byte
    ; PC + ? - dividend low byte
    ; PC + ? - quotient high byte
    ; PC + ? - quotient second byte
    ; PC + ? - quotient third byte
    ; PC + ? - quotient low byte

    ; First, save the A and U registers
    PUSH A
    PUSH U

    ; Now, preload U = loop value
    LOADI 32
    MOV A, U

    ; Initialize the divisor copy so we can call ucmp easier.
    ADDPCI 11
    LOAD A
    SUBPCI 12
    STORE A
    ADDPCI 11
    LOAD A
    SUBPCI 12
    STORE A
    ADDPCI 11
    LOAD A
    SUBPCI 12
    STORE A
    ADDPCI 11
    LOAD A
    SUBPCI 12
    STORE A

    ; Initialize the remainder
    ZERO
    PUSH A
    PUSH A
    PUSH A
    PUSH A

    ; And preload the quotient.
    ADDPCI 16
    ZERO
    STORE A
    INCPC
    STORE A
    INCPC
    STORE A
    INCPC
    STORE A

    ; Start by pointing at the top of the remainder.
    SUBPCI 19

_udiv32_loop:
    ; First, shift out the top bit from the dividend, so we can shift
    ; it into the remainder accumulator. We finish by pointing at the
    ; high byte of the dividend.
    ADDPCI 15
    LOAD A
    SHL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A

    ; Shift the bit into the remainder to accumulate it. We finish by
    ; pointing at the high byte of the remainder.
    SUBPCI 9
    LOAD A
    RCL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A

    ; First, check if the remainder is zero (which it will be in a
    ; LOT of cases). We know if the remainder is zero, that the
    ; divisor will be greater since you aren't allowed to divide
    ; by zero.
    JRINZ _udiv32_need_ucmp
    ADDPCI 3
    LOAD A
    ADDI 0
    JRINZ _udiv32_need_ucmp_sub_3
    DECPC
    LOAD A
    ADDI 0
    JRINZ _udiv32_need_ucmp_sub_2
    DECPC
    LOAD A
    ADDI 0
    DECPC
    JRIZ _udiv32_shift_quotient
    JRI _udiv32_need_ucmp

_udiv32_need_ucmp_sub_3:
    DECPC
_udiv32_need_ucmp_sub_2:
    SUBPCI 2
_udiv32_need_ucmp:
    ; Now, see if the remainder is larger than the divisor.
    CALL ucmp32
    NEG
    SHL
    JRINC _udiv32_sub_divisor

_udiv32_shift_quotient:
    ; Remainder is less than the divisor, so just shift our quotient
    ; and loop again. Make sure to finish by pointing at the high
    ; byte of the remainder.
    ADDPCI 19
    LOAD A
    SHL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A
    SUBPCI 16

    LNGJUMP _udiv32_check_termination

_udiv32_sub_divisor:

    ; The divisor fits into the remainder, so we have a single bit
    ; division result. Reflect that in the quotient. We finish at
    ; the low byte of the quotient.
    ADDPCI 19
    LOAD A
    SHL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A
    ADDPCI 3
    LOAD A
    ADDI 1
    STORE A

    ; Copy the divisor to negate. We end at the high byte of the
    ; divisor, perfect for calling neg32 and add32, which will
    ; stick us back on the high byte of the remainder after adding
    ; the negation of the divisor to the remainder.
    SUBPCI 12
    LOAD A
    SUBPCI 8
    STORE A
    ADDPCI 7
    LOAD A
    SUBPCI 8
    STORE A
    ADDPCI 7
    LOAD A
    SUBPCI 8
    STORE A
    ADDPCI 7
    LOAD A
    SUBPCI 8
    STORE A

    ; Negate it.
    CALL neg32

    ; Subtract it from the remainder. This puts our stack pointing
    ; back at the modified remainder high byte, with the divisor
    ; subtracted out.
    CALL add32

_udiv32_check_termination:
    ; Now, see if we need to loop or if we're done here.
    MOV U, A
    ADDI -1
    MOV A, U

    ; If it is zero, we've done all the loops we need.
    LNGJUMPNZ _udiv32_loop

    ; We're finished, so restore all the values to their correct place.
    ; Stack layout should look like this once we finish:
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - remainder high byte
    ; PC + ? - remainder second byte
    ; PC + ? - remainder third byte
    ; PC + ? - remainder low byte
    ; PC + ? - quotient high byte
    ; PC + ? - quotient second byte
    ; PC + ? - quotient third byte
    ; PC + ? - quotient low byte

    ; First, relocate the remainder where it should go.
    LOAD A
    ADDPCI 12
    STORE A
    SUBPCI 11
    LOAD A
    ADDPCI 12
    STORE A
    SUBPCI 11
    LOAD A
    ADDPCI 12
    STORE A
    SUBPCI 11
    LOAD A
    ADDPCI 12
    STORE A

    ; Now, restore the U and A registers.
    SUBPCI 7
    POP U
    POP A

    ; Finally, return the calculated values!
    RET
