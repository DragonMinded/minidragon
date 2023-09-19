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
    ; First operand >>= 1.
    DECPC
    LOAD A
    SHR
    STORE A

    INCPC
    LOAD A
    RCR
    STORE A

    ; See if first operand's bottom bit was set
    JRINC _umult16_second_shift

_umult16_first_shift_copy:
    ; Now, copy the second value into our temporary storage, add it to the
    ; current accumulator.
    SUBPCI 2
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
    ADDPCI 8

_umult16_second_shift:
    ; Second operand <<= 1. We have to do this in two parts.
    SUBPCI 2
    LOAD A
    SHL
    STORE A
    DECPC

    ; Now, shift in the upper bit into the second half.
    LOAD A
    RCL
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
    ; through the loop at least once, which is pointing at the first
    ; operand low byte.
    ADDPCI 14

_umult32_loop:
    ; See if first operand high byte is zero.
    LOAD A
    ADDI 0
    DECPC
    JRINZ _umult32_nz_add_two

    ; See if the third byte is zero.
    LOAD A
    ADDI 0
    DECPC
    JRINZ _umult32_nz_add_one

    ; See if the second byte is zero.
    LOAD A
    ADDI 0
    DECPC
    JRINZ _umult32_nz

    ; See if the first operand low byte is zero.
    LOAD A
    ADDI 0
    LNGJUMPZ _umult32_finished
    JRI _umult32_nz

_umult32_nz_add_two:
    ; Cascading increments is a bit inefficient but we need to be
    ; able to bail out of the above check at any time.
    DECPC
_umult32_nz_add_one:
    DECPC

_umult32_nz:
    ; See if first operand's bottom bit set, also perform
    ; first operand >>= 1. Ripple this from top to bottom bit.
    LOAD A
    SHR
    STORE A

    INCPC
    LOAD A
    RCR
    STORE A

    INCPC
    LOAD A
    RCR
    STORE A

    INCPC
    LOAD A
    RCR
    STORE A

    SUBPCI 4
    LNGJUMPNC _umult32_second_shift

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
    ADDPCI 10

_umult32_second_shift:
    ; Second operand <<= 1. We have to do this in four parts.
    ; Ripple the bit left as we shift each chunk.
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

    ; Finished shifting, back to loop. Move our stack pointer to the
    ; first operand low byte, where it starts out.
    ADDPCI 7
    LNGJUMP _umult32_loop

_umult32_finished:
    ; Place the accumulated result back into the spot for the first operand.
    SUBPCI 11
    LOAD A
    ADDPCI 11
    STORE A
    SUBPCI 10
    LOAD A
    ADDPCI 11
    STORE A
    SUBPCI 10
    LOAD A
    ADDPCI 11
    STORE A
    SUBPCI 10
    LOAD A
    ADDPCI 11
    STORE A

    ; Move the return address so we can do a return.
    SUBPCI 8
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
