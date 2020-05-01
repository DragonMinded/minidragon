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
    JRIZ _umult_finished

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
    JRI _umult_loop

_umult_finished:
    ; Place accumulated result back into A register (MOV faster than SWAP
    ; in this case).
    MOV V, A

    ; Restore temporary registers.
    POP V
    POP U

    ; And done!
    RET

umult16:
    ; Multiply two unsigned 16-bit numbers on the stack, returning value
    ; on the stack. Does not clobber A, U, V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To multiply 517 and 67, call like so:
    ;   PUSHI 0x05
    ;   PUSHI 0x02
    ;   PUSHI 0x43
    ;   PUSHI 0x00
    ;   CALL umult16
    ;
    ; Stack layout
    ; PC + ? - temporary storage for second operand shifted high byte
    ; PC + ? - temporary storage for second operand shifted low byte
    ; PC + ? - temporary storage for accumulator high byte
    ; PC + ? - temporary storage for accumulator low byte
    ; PC + ? - saved A register
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - second operand high byte
    ; PC + ? - second operand low byte
    ; PC + ? - first operand high byte
    ; PC + ? - first operand low byte

    ; Save the contents of the A register
    PUSH A

    ; Set up the accumulator
    ZERO
    PUSH A
    PUSH A

    ; Stick our stack pointer where we expect it to be when we're
    ; through the loop at least once.
    ADDPCI 7

_umult16_loop:
    ; See if first operand high byte is zero.
    LOAD A
    ADDI 0
    INCPC
    JRINZ _umult16_nz

    ; See if the first operand low byte is zero.
    LOAD A
    ADDI 0
    LNGJUMPZ _umult16_finished

_umult16_nz:
    ; See if first operand's bottom bit set, also perform
    ; first operand >>= 1.
    LOAD A
    SHR
    STORE A
    JRINC _umult16_no_add_first_shift

    ; We need to shift the top byte into the bottom byte,
    ; then we need to add the current second operand to
    ; the accumulator.
    DECPC
    LOAD A
    SHR
    STORE A

    ; If there wasn't a carry, we're done!
    JRINC _umult16_first_shift_copy

    ; There was a carry, so we need to add it into the first.
    INCPC
    LOADI 0x80
    OR
    STORE A
    DECPC

_umult16_first_shift_copy:
    ; Now, copy the second value into our temporary storage, add it to the
    ; current accumulator.
    DECPC
    LOAD A
    SUBPCI 7
    STORE A
    ADDPCI 6
    LOAD A
    SUBPCI 7
    STORE A

    ; This will leave us pointing at the updated accumulator
    ; on the stack, so lets move back up to the first operand
    ; high byte where we would have been if we jumped immediately
    ; to _umult16_second_shift
    CALL add16
    ADDPCI 7
    JRI _umult16_second_shift

_umult16_no_add_first_shift:
    ; We don't need to add, but we do need to shift the
    ; top byte into the bottom byte of the first operand.
    DECPC
    LOAD A
    SHR
    STORE A

    ; If there wasn't a carry, we're done!
    JRINC _umult16_second_shift

    ; There was a carry, so we need to add it into the first.
    INCPC
    LOADI 0x80
    OR
    STORE A
    DECPC

_umult16_second_shift:
    ; Second operand <<= 1. We have to do this in two parts.
    DECPC
    LOAD A
    SHL
    STORE A
    DECPC

    JRIC _umult16_second_shift_carry

    ; We didn't have any carry bit, so its safe to shift the
    ; second.
    LOAD A
    SHL
    STORE A

    ; Back to loop
    ADDPCI 2
    LNGJUMP _umult16_loop

_umult16_second_shift_carry:
    ; We did have a carry bit, so we need to add it in.
    LOAD A
    SHL
    ADDI 1
    STORE A

    ; Back to loop
    ADDPCI 2
    LNGJUMP _umult16_loop

_umult16_finished:
    ; Place the accumulated result back into the spot for the first operand.
    SUBPCI 7
    LOAD A
    ADDPCI 7
    STORE A
    SUBPCI 8
    LOAD A
    ADDPCI 7
    STORE A

    ; Move the return address so we can do a return.
    SUBPCI 3
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 3
    LOAD A
    ADDPCI 2
    STORE A

    ; Restore the A register.
    SUBPCI 3
    LOAD A
    ADDPCI 3

    ; And done!
    RET

umult32:
    ; Multiply two unsigned 32-bit numbers on the stack, returning value
    ; on the stack. Does not clobber A, U, V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To multiply 12345 and 6789, call like so:
    ;   PUSHI 0x39
    ;   PUSHI 0x30
    ;   PUSHI 0x00
    ;   PUSHI 0x00
    ;   PUSHI 0x85
    ;   PUSHI 0x1A
    ;   PUSHI 0x00
    ;   PUSHI 0x00
    ;   CALL umult32
    ;
    ; Stack layout
    ; PC + ? - temporary storage for second operand shifted high byte
    ; PC + ? - temporary storage for second operand shifted third byte
    ; PC + ? - temporary storage for second operand shifted second byte
    ; PC + ? - temporary storage for second operand shifted low byte
    ; PC + ? - temporary storage for accumulator high byte
    ; PC + ? - temporary storage for accumulator third byte
    ; PC + ? - temporary storage for accumulator second byte
    ; PC + ? - temporary storage for accumulator low byte
    ; PC + ? - saved A register
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - second operand high byte
    ; PC + ? - second operand third byte
    ; PC + ? - second operand second byte
    ; PC + ? - second operand low byte
    ; PC + ? - first operand high byte
    ; PC + ? - first operand third byte
    ; PC + ? - first operand second byte
    ; PC + ? - first operand low byte

    ; Save the contents of the A register
    PUSH A

    ; Set up the accumulator
    ZERO
    PUSH A
    PUSH A
    PUSH A
    PUSH A

    ; Stick our stack pointer where we expect it to be when we're
    ; through the loop at least once.
    ADDPCI 11

_umult32_loop:
    ; See if first operand high byte is zero.
    LOAD A
    ADDI 0
    INCPC
    JRINZ _umult32_nz_add_two

    ; See if the third byte is zero.
    LOAD A
    ADDI 0
    INCPC
    JRINZ _umult32_nz_add_one

    ; See if the second byte is zero.
    LOAD A
    ADDI 0
    INCPC
    JRINZ _umult32_nz

    ; See if the first operand low byte is zero.
    LOAD A
    ADDI 0
    LNGJUMPZ _umult32_finished
    JRI _umult32_nz

_umult32_nz_add_two:
    ; Cascading increments is a bit inefficient but we need to be
    ; able to bail out of the above check at any time.
    INCPC
_umult32_nz_add_one:
    INCPC

_umult32_nz:
    ; See if first operand's bottom bit set, also perform
    ; first operand >>= 1.
    LOAD A
    SHR
    STORE A
    LNGJUMPNC _umult32_no_add_first_shift

    ; We need to shift the second byte into the bottom byte.
    DECPC
    LOAD A
    SHR
    STORE A

    ; If there wasn't a carry, we're done!
    JRINC _umult32_first_shift_no_set_1

    ; There was a carry, so we need to add it into the first.
    INCPC
    LOADI 0x80
    OR
    STORE A
    DECPC

_umult32_first_shift_no_set_1:
    ; We need to shift the third byte into the second byte.
    DECPC
    LOAD A
    SHR
    STORE A

    ; If there wasn't a carry, we're done!
    JRINC _umult32_first_shift_no_set_2

    ; There was a carry, so we need to add it into the first.
    INCPC
    LOADI 0x80
    OR
    STORE A
    DECPC

_umult32_first_shift_no_set_2:
    ; We need to shift the high byte into the third byte byte.
    DECPC
    LOAD A
    SHR
    STORE A

    ; If there wasn't a carry, we're done!
    JRINC _umult32_first_shift_copy

    ; There was a carry, so we need to add it into the first.
    INCPC
    LOADI 0x80
    OR
    STORE A
    DECPC

_umult32_first_shift_copy:
    ; Move to the low byte of the second number.
    DECPC

    ; Now, copy the second value into our temporary storage, add it to the
    ; current accumulator.
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 10
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 10
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 10
    LOAD A
    SUBPCI 11
    STORE A

    ; This will leave us pointing at the updated accumulator
    ; on the stack, so lets move back up to the first operand
    ; high byte where we would have been if we jumped immediately
    ; to _umult32_second_shift
    CALL add32
    ADDPCI 11
    LNGJUMP _umult32_second_shift

_umult32_no_add_first_shift:
    ; We don't need to add, but we do need to shift the number right.
    DECPC
    LOAD A
    SHR
    STORE A

    ; If there wasn't a carry, we're done!
    JRINC _umult32_no_add_first_shift_no_set_1

    ; There was a carry, so we need to add it into the first.
    INCPC
    LOADI 0x80
    OR
    STORE A
    DECPC

_umult32_no_add_first_shift_no_set_1:
    ; We need to shift the third byte into the second byte.
    DECPC
    LOAD A
    SHR
    STORE A

    ; If there wasn't a carry, we're done!
    JRINC _umult32_no_add_first_shift_no_set_2

    ; There was a carry, so we need to add it into the first.
    INCPC
    LOADI 0x80
    OR
    STORE A
    DECPC

_umult32_no_add_first_shift_no_set_2:
    ; We need to shift the high byte into the third byte byte.
    DECPC
    LOAD A
    SHR
    STORE A

    ; If there wasn't a carry, we're done!
    JRINC _umult32_second_shift

    ; There was a carry, so we need to add it into the first.
    INCPC
    LOADI 0x80
    OR
    STORE A
    DECPC

_umult32_second_shift:
    ; Second operand <<= 1. We have to do this in four parts.
    ; Do this "backwards", or top byte to bottom byte, so we
    ; don't have to worry about losing the carry flag when we
    ; figure out whether to shift or not.
    SUBPCI 4
    LOAD A
    SHL
    STORE A
    INCPC

    ; Now, do the third byte, and possibly add a bit to the
    ; high byte if we got a carry.
    LOAD A
    SHL
    STORE A

    JRINC _umult32_second_shift_skip_carry_1

    DECPC
    LOAD A
    ADDI 1
    STORE A
    INCPC

_umult32_second_shift_skip_carry_1:
    ; Now, do the second byte, and possibly add a bit to the
    ; third byte if we got a carry.
    INCPC
    LOAD A
    SHL
    STORE A

    JRINC _umult32_second_shift_skip_carry_2

    DECPC
    LOAD A
    ADDI 1
    STORE A
    INCPC

_umult32_second_shift_skip_carry_2:
    ; Now, do the low byte, and possibly add a bit to the
    ; third byte if we got a carry.
    INCPC
    LOAD A
    SHL
    STORE A

    JRINC _umult32_second_shift_skip_carry_3

    DECPC
    LOAD A
    ADDI 1
    STORE A
    INCPC

_umult32_second_shift_skip_carry_3:
    ; Finished shifting, back to loop
    INCPC
    LNGJUMP _umult32_loop

_umult32_finished:
    ; Place the accumulated result back into the spot for the first operand.
    SUBPCI 11
    LOAD A
    ADDPCI 11
    STORE A
    SUBPCI 12
    LOAD A
    ADDPCI 11
    STORE A
    SUBPCI 12
    LOAD A
    ADDPCI 11
    STORE A
    SUBPCI 12
    LOAD A
    ADDPCI 11
    STORE A

    ; Move the return address so we can do a return.
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A

    ; Restore the A register.
    SUBPCI 5
    LOAD A
    ADDPCI 5

    ; And done!
    RET
