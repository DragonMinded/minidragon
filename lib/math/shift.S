lshift:
    ; Given an integer value on the stack and an integer shift amount in the A
    ; register, shift the integer value left by the number of times specified in
    ; the shift amount. A negative shift amount is not supported, so negative
    ; integers are interpreted as large positive integers. Returns the shifted
    ; amount in the A register. Does not clobber the U/V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To shift the number 33 left by two positions, call like so:
    ;     PUSHI 33
    ;     LOADI 2
    ;     CALL lshift
    ;
    ; Stack layout:
    ; PC + 0 - saved U
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - number to shift

    ; Save the U register so we can use it without stack shenanigans.
    PUSH U

    ; Load the number to shift in U and the count in A.
    ADDPCI 3
    LOAD U

_lshift_finish_check:
    ADDI 0
    JRIZ _lshift_finished

    ; Count that we're about to shift left by 1.
    DEC

    ; Actually perform the left shift.
    SWAP A, U
    SHL
    SWAP A, U

    ; Done with the loop, check for termination again.
    JRI _lshift_finish_check

_lshift_finished:
    ; The number is in U, so move it to A.
    MOV U, A

    ; Restore the clobbered U register.
    SUBPCI 3
    POP U

    ; And we're done!
    RET


lshift16:
    ; Given an integer value on the stack and an integer shift amount in the A
    ; register, shift the integer value left by the number of times specified in
    ; the shift amount. A negative shift amount is not supported, so negative
    ; integers are interpreted as large positive integers. Returns the shifted
    ; amount on the stack. Does not clobber the U/V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To shift the number 0x1234 left by two positions, call like so:
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     LOADI 2
    ;     CALL lshift16
    ;
    ; Stack layout:
    ; PC + 0 - saved U
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - number to shift high byte
    ; PC + 4 - number to shift low byte

    ; Save the U register so we can use it without stack shenanigans.
    PUSH U

    ; Prime our spot for shifting left to the low byte so we can shift digits into
    ; higher bytes.
    ADDPCI 4

_lshift16_finish_check:
    ADDI 0
    JRIZ _lshift16_finished

    ; Count that we're about to shift left by 1.
    DEC

    ; Actually perform the left shift.
    MOV A, U
    LOAD A
    SHL
    STORE A
    DECPC
    LOAD A
    RCL
    STORE A
    INCPC
    MOV U, A

    ; Done with the loop, check for termination again.
    JRI _lshift16_finish_check

_lshift16_finished:
    ; Restore the clobbered U register.
    SUBPCI 4
    POP U

    ; And we're done!
    RET


lshift32:
    ; Given an integer value on the stack and an integer shift amount in the A
    ; register, shift the integer value left by the number of times specified in
    ; the shift amount. A negative shift amount is not supported, so negative
    ; integers are interpreted as large positive integers. Returns the shifted
    ; amount on the stack. Does not clobber the U/V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To shift the number 0x12345678 left by two positions, call like so:
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     LOADI 2
    ;     CALL lshift32
    ;
    ; Stack layout:
    ; PC + 0 - saved U
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - number to shift high byte
    ; PC + 4 - number to shift
    ; PC + 5 - number to shift
    ; PC + 6 - number to shift low byte

    ; Save the U register so we can use it without stack shenanigans.
    PUSH U

    ; Prime our spot for shifting left to the low byte so we can shift digits into
    ; higher bytes.
    ADDPCI 6

_lshift32_finish_check:
    ADDI 0
    JRIZ _lshift32_finished

    ; Count that we're about to shift left by 1.
    DEC

    ; Actually perform the left shift.
    MOV A, U
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
    MOV U, A

    ; Done with the loop, check for termination again.
    JRI _lshift32_finish_check

_lshift32_finished:
    ; Restore the clobbered U register.
    SUBPCI 6
    POP U

    ; And we're done!
    RET


rshift:
    ; Given an integer value on the stack and an integer shift amount in the A
    ; register, shift the integer value right by the number of times specified in
    ; the shift amount. A negative shift amount is not supported, so negative
    ; integers are interpreted as large positive integers. Returns the shifted
    ; amount in the A register. Does not clobber the U/V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To shift the number 33 right by two positions, call like so:
    ;     PUSHI 33
    ;     LOADI 2
    ;     CALL rshift
    ;
    ; Stack layout:
    ; PC + 0 - saved U
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - number to shift

    ; Save the U register so we can use it without stack shenanigans.
    PUSH U

    ; Load the number to shift in U and the count in A.
    ADDPCI 3
    LOAD U

_rshift_finish_check:
    ADDI 0
    JRIZ _rshift_finished

    ; Count that we're about to shift right by 1.
    DEC

    ; Actually perform the right shift.
    SWAP A, U
    SHR
    SWAP A, U

    ; Done with the loop, check for termination again.
    JRI _rshift_finish_check

_rshift_finished:
    ; The number is in U, so move it to A.
    MOV U, A

    ; Restore the clobbered U register.
    SUBPCI 3
    POP U

    ; And we're done!
    RET


rshift16:
    ; Given an integer value on the stack and an integer shift amount in the A
    ; register, shift the integer value right by the number of times specified in
    ; the shift amount. A negative shift amount is not supported, so negative
    ; integers are interpreted as large positive integers. Returns the shifted
    ; amount on the stack. Does not clobber the U/V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To shift the number 0x1234 right by two positions, call like so:
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     LOADI 2
    ;     CALL rshift16
    ;
    ; Stack layout:
    ; PC + 0 - saved U
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - number to shift high byte
    ; PC + 4 - number to shift low byte

    ; Save the U register so we can use it without stack shenanigans.
    PUSH U

    ; Prime our spot for shifting right to the high byte so we can shift digits into
    ; lower bytes.
    ADDPCI 3

_rshift16_finish_check:
    ADDI 0
    JRIZ _rshift16_finished

    ; Count that we're about to shift right by 1.
    DEC

    ; Actually perform the right shift.
    MOV A, U
    LOAD A
    SHR
    STORE A
    INCPC
    LOAD A
    RCR
    STORE A
    DECPC
    MOV U, A

    ; Done with the loop, check for termination again.
    JRI _rshift16_finish_check

_rshift16_finished:
    ; Restore the clobbered U register.
    SUBPCI 3
    POP U

    ; And we're done!
    RET


rshift32:
    ; Given an integer value on the stack and an integer shift amount in the A
    ; register, shift the integer value right by the number of times specified in
    ; the shift amount. A negative shift amount is not supported, so negative
    ; integers are interpreted as large positive integers. Returns the shifted
    ; amount on the stack. Does not clobber the U/V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To shift the number 0x12345678 right by two positions, call like so:
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     LOADI 2
    ;     CALL rshift32
    ;
    ; Stack layout:
    ; PC + 0 - saved U
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - number to shift high byte
    ; PC + 4 - number to shift
    ; PC + 5 - number to shift
    ; PC + 6 - number to shift low byte

    ; Save the U register so we can use it without stack shenanigans.
    PUSH U

    ; Prime our spot for shifting right to the high byte so we can shift digits into
    ; lower bytes.
    ADDPCI 3

_rshift32_finish_check:
    ADDI 0
    JRIZ _rshift32_finished

    ; Count that we're about to shift right by 1.
    DEC

    ; Actually perform the right shift.
    MOV A, U
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
    SUBPCI 3
    MOV U, A

    ; Done with the loop, check for termination again.
    JRI _rshift32_finish_check

_rshift32_finished:
    ; Restore the clobbered U register.
    SUBPCI 3
    POP U

    ; And we're done!
    RET
