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
