ucmp:
    ; Given two unsigned integers on the stack, return -1 if the first is less
    ; than the second, 0 if the first equals the second, and 1 if the
    ; first is greater than the second. Returns the value in the A
    ; register. Does not clobber the U, V or SPC registers. Does not clobber
    ; the numbers on the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to see if 5 is less than, equal to or greater than 7,
    ; call this similar to:
    ;     PUSHI 5
    ;     PUSHI 7
    ;     CALL ucmp
    ;
    ; Stack layout:
    ; PC + 0 - saved U register
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - second number
    ; PC + 4 - first number

    ; First, do the easy thing and see if they are equal.
    ADDPCI 3
    LOAD A
    DECPC
    XOR
    SUBPCI 2
    JRINZ _ucmp_ne

    ; Its equal, so lets bail.
    LOADI 0
    RET

_ucmp_ne:
    ; Make copies so we can mess with the numbers
    PUSH U
    ADDPCI 3
    LOAD A
    INCPC
    LOAD U
    SUBPCI 4

    ; Technically we should only do this 8 times, for 8 bits,
    ; but given the base case above where they are equal, we
    ; know for a fact we will find a difference here, so no
    ; limit is applied.
_ucmp_loop:
    ; First, shift the first number left.
    SWAP A, U
    SHL

    ; If the top bit is 1, then A is >= B, so we check for that
    ; in the second if.
    JRIC _ucmp_first_high

    ; If the top bit is 0, then A is <= B, so we check for that
    ; here.
    SWAP U, A
    SHL

    ; If the top bit is 0, then A == B as far as we know, since both
    ; their high bits match.
    JRINC _ucmp_loop

    ; If the top bit is 1, then A < B, since the high bit of B is
    ; set and the high bit of A is not set.
    POP U
    LOADI -1
    RET

_ucmp_first_high:
    ; Now, grab the second number.
    SWAP A, U
    SHL

    ; If the top bit is 0, then A is > B, since the high bit of A
    ; is set, and the high bit of B is not set. If the top bit is
    ; 1, then A == B as far as we know.
    JRIC _ucmp_loop

    ; We know that A > B here, so lets bail.
    POP U
    LOADI 1
    RET

ucmp16:
    ; Given two 16-bit unsigned integers on the stack, return -1 if the first
    ; is less than the second, 0 if the first equals the second, and 1 if the
    ; first is greater than the second. Returns the value in the A
    ; register. Does not clobber the U, V or SPC registers. Does not clobber
    ; the numbers on the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to see if 0x1234 is less than, equal to or greater than
    ; 0x5678, call this similar to:
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     CALL ucmp16
    ;
    ; Stack layout:
    ; PC + 0 - saved U register
    ; PC + 1 - return address
    ; PC + 2 - return address
    ; PC + 3 - second number high byte
    ; PC + 4 - second number low byte
    ; PC + 5 - first number high byte
    ; PC + 6 - first number low byte

    ; To make it easier to save this register with fewer instructions.
    PUSH U

    ; First, do the easy thing and see if they are equal, starting with the
    ; first byte.
    ADDPCI 5
    LOAD A
    SUBPCI 2
    XOR
    JRINZ _ucmp16_high_ne

    ; Now, check the second byte to see if they're equal.
    ADDPCI 3
    LOAD A
    SUBPCI 2
    XOR
    JRINZ _ucmp16_low_ne

    ; Its equal, so lets bail.
    SUBPCI 3
    LOADI 0
    RET

_ucmp16_high_ne:
    ; Make copies so we can mess with the numbers
    LOAD A
    ADDPCI 2
    LOAD U
    SUBPCI 5

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

_ucmp16_low_ne:
    ; Make copies so we can mess with the numbers
    LOAD A
    ADDPCI 2
    LOAD U
    SUBPCI 6

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

ucmp32:
    ; Given two 32-bit unsigned integers on the stack, return -1 if the first
    ; is less than the second, 0 if the first equals the second, and 1 if the
    ; first is greater than the second. Returns the value in the A
    ; register. Does not clobber the U, V or SPC registers. Does not clobber
    ; the numbers on the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to see if 0x12345678 is less than, equal to or greater than
    ; 0x56789101, call this similar to:
    ;     PUSHI 0x01
    ;     PUSHI 0x91
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     CALL ucmp32
    ;
    ; Stack layout:
    ; PC + 0  - saved U register
    ; PC + 1  - return address
    ; PC + 2  - return address
    ; PC + 3  - second number first byte
    ; PC + 4  - second number
    ; PC + 5  - second number
    ; PC + 6  - second number last byte
    ; PC + 7  - first number first byte
    ; PC + 8  - first number
    ; PC + 9  - first number
    ; PC + 10 - first number last byte

    ; To make it easier to save this register with fewer instructions.
    PUSH U

    ; First, do the easy thing and see if they are equal, starting with the
    ; first byte.
    ADDPCI 7
    LOAD A
    SUBPCI 4
    XOR
    JRINZ _ucmp32_1st_ne

    ; Now, check the second byte to see if they're equal.
    ADDPCI 5
    LOAD A
    SUBPCI 4
    XOR
    JRINZ _ucmp32_2nd_ne

    ; Now, check the third byte to see if they're equal. We do this backwards
    ; from the upper two bytes to put us in range of jumping to the saved U
    ; register from the second number load.
    INCPC
    LOAD A
    ADDPCI 4
    XOR
    JRINZ _ucmp32_3rd_ne

    ; Now, check the final byte to see if they're equal. Same rationale as
    ; above for ordering
    SUBPCI 3
    LOAD A
    ADDPCI 4
    XOR
    JRINZ _ucmp32_4th_ne

    ; Its equal, so lets bail. We unfortunately can't make it back to the
    ; saved return value in 8 or less positions. This is due to the above
    ; optimization, assuming that in general, two 32 bit numbers are going
    ; to be non-equal more than equal.
    SUBPCI 8
    DECPC
    LOADI 0
    RET

_ucmp32_1st_ne:
    ; Make copies so we can mess with the numbers
    LOAD A
    ADDPCI 4
    LOAD U
    SUBPCI 7

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

_ucmp32_2nd_ne:
    ; Make copies so we can mess with the numbers
    LOAD A
    ADDPCI 4
    LOAD U
    SUBPCI 8

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

_ucmp32_3rd_ne:
    ; Make copies so we can mess with the numbers
    LOAD U
    SUBPCI 4
    LOAD A
    SUBPCI 5

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

_ucmp32_4th_ne:
    ; Make copies so we can mess with the numbers
    LOAD U
    SUBPCI 4
    LOAD A
    SUBPCI 6

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

umin:
    ; Given two unsigned integers on the stack, return the smaller of the
    ; two in the A register. Does not clobber the U, V or SPC registers.
    ; Does not clobber the numbers on the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To get the min of 5 and 7, call it like so:
    ;     PUSHI 5
    ;     PUSHI 7
    ;     CALL umin
    ;
    ; Stack layout:
    ; PC + 0 - temporary second number storage
    ; PC + 1 - temporary first number storage
    ; PC + 2 - return address
    ; PC + 3 - return address
    ; PC + 4 - second number
    ; PC + 5 - first number

    ; First, copy the first and second number so we can call ucmp.
    ADDPCI 3
    LOAD A
    SUBPCI 4
    STORE A
    ADDPCI 3
    LOAD A
    SUBPCI 4
    STORE A

    ; Now, figure out which is less
    CALL ucmp

    ; Return the first number if 1st < 2nd, otherwise return second.
    SHL
    JRINC _umin_ge

    INCPC
    LOAD A
    INCPC
    RET

_umin_ge:
    ; First number is >= second number, return second number.
    LOAD A
    ADDPCI 2
    RET

umin16:
    ; Given two unsigned 16-bit integers on the stack, return the smaller
    ; of the two on the stack. Does not clobber the U, V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to get the min of 0x1234 and 0x5678, call this like:
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     CALL umin16
    ;
    ; Stack layout:
    ; PC + 0 - temporary second number storage
    ; PC + 1 - temporary second number storage
    ; PC + 2 - temporary first number storage
    ; PC + 3 - temporary first number storage
    ; PC + 4 - contents of A register preserved
    ; PC + 4 - return address
    ; PC + 5 - return address
    ; PC + 6 - second number
    ; PC + 7 - second number
    ; PC + 8 - first number
    ; PC + 9 - first number

    ; First, save the A register
    PUSH A

    ; Now, copy the first and second number so we can call ucmp.
    ADDPCI 3
    LOAD A
    SUBPCI 7
    STORE A
    ADDPCI 8
    LOAD A
    SUBPCI 7
    STORE A
    ADDPCI 8
    LOAD A
    SUBPCI 7
    STORE A
    ADDPCI 8
    LOAD A
    SUBPCI 7
    STORE A
    SUBPCI 3

    ; Now, figure out which is less
    CALL ucmp16

    ; Return the first number if 1st < 2nd, otherwise return second.
    SHL
    JRINC _umin16_ge

    ; First number is already in the right spot, so just move the return
    ; and let's get out of here.
    ADDPCI 6
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 3
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 3

    ; Finally, restore the A register.
    LOAD A
    ADDPCI 3

    ; Now, return!
    RET

_umin16_ge:
    ; First number is >= second number, return second number. We do this
    ; by copying the whole stack from the saved A register through the
    ; second number, up by two, and then returning.
    ADDPCI 8
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 3
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 3
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 3
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 3

    ; Now, restore the A register
    LOAD A
    ADDPCI 3

    ; Now, return!
    RET

umin32:
    ; Given two unsigned 32-bit integers on the stack, return the smaller
    ; of the two on the stack. Does not clobber the U, V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to get the min of 0x12345678 and 0x56789101, call this
    ; similar to:
    ;     PUSHI 0x01
    ;     PUSHI 0x91
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     CALL umin32
    ;
    ; Stack layout:
    ; PC + 0  - temporary second number storage
    ; PC + 1  - temporary second number storage
    ; PC + 2  - temporary second number storage
    ; PC + 3  - temporary second number storage
    ; PC + 4  - temporary first number storage
    ; PC + 5  - temporary first number storage
    ; PC + 6  - temporary first number storage
    ; PC + 7  - temporary first number storage
    ; PC + 8  - contents of A register preserved
    ; PC + 9  - return address
    ; PC + 10 - return address
    ; PC + 11 - second number
    ; PC + 12 - second number
    ; PC + 13 - second number
    ; PC + 14 - second number
    ; PC + 15 - first number
    ; PC + 16 - first number
    ; PC + 17 - first number
    ; PC + 18 - first number

    ; First, save the A register
    PUSH A

    ; Now, copy the first and second number so we can call ucmp.
    ADDPCI 3
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 12
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 12
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 12
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 12
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 12
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 12
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 12
    LOAD A
    SUBPCI 11
    STORE A
    SUBPCI 7

    ; Now, figure out which is less
    CALL ucmp32

    ; Return the first number if 1st < 2nd, otherwise return second.
    SHL
    JRINC _umin32_ge

    ; First number is already in the right spot, so just move the return
    ; and let's get out of here.
    ADDPCI 10
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5

    ; Finally, restore the A register.
    LOAD A
    ADDPCI 5

    ; Now, return!
    RET

_umin32_ge:
    ; First number is >= second number, return second number. We do this
    ; by copying the whole stack from the saved A register through the
    ; second number, up by two, and then returning.
    ADDPCI 14
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5

    ; Now, restore the A register
    LOAD A
    ADDPCI 5

    ; Now, return!
    RET

umax:
    ; Given two unsigned integers on the stack, return the larger of the
    ; two in the A register. Does not clobber the U, V or SPC registers.
    ; Does not clobber the numbers on the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To get the max of 5 and 7, call it like so:
    ;     PUSHI 5
    ;     PUSHI 7
    ;     CALL umax
    ;
    ; Stack layout:
    ; PC + 0 - temporary second number storage
    ; PC + 1 - temporary first number storage
    ; PC + 2 - return address
    ; PC + 3 - return address
    ; PC + 4 - second number
    ; PC + 5 - first number

    ; First, copy the first and second number so we can call ucmp.
    ADDPCI 3
    LOAD A
    SUBPCI 4
    STORE A
    ADDPCI 3
    LOAD A
    SUBPCI 4
    STORE A

    ; Now, figure out which is less
    CALL ucmp

    ; Return the first number if 1st > 2nd, otherwise return second.
    SHL
    JRIC _umax_le

    INCPC
    LOAD A
    INCPC
    RET

_umax_le:
    ; First number is >= second number, return second number.
    LOAD A
    ADDPCI 2
    RET

umax16:
    ; Given two unsigned 16-bit integers on the stack, return the larger
    ; of the two on the stack. Does not clobber the U, V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to get the max of 0x1234 and 0x5678, call this like:
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     CALL umax16
    ;
    ; Stack layout:
    ; PC + 0  - temporary second number storage
    ; PC + 1  - temporary second number storage
    ; PC + 2  - temporary first number storage
    ; PC + 3  - temporary first number storage
    ; PC + 4  - contents of A register preserved
    ; PC + 5  - return address
    ; PC + 6  - return address
    ; PC + 7  - second number
    ; PC + 8  - second number
    ; PC + 9  - first number
    ; PC + 10 - first number

    ; First, save the A register
    PUSH A

    ; Now, copy the first and second number so we can call ucmp.
    ADDPCI 3
    LOAD A
    SUBPCI 7
    STORE A
    ADDPCI 8
    LOAD A
    SUBPCI 7
    STORE A
    ADDPCI 8
    LOAD A
    SUBPCI 7
    STORE A
    ADDPCI 8
    LOAD A
    SUBPCI 7
    STORE A
    SUBPCI 3

    ; Now, figure out which is less
    CALL ucmp16

    ; Return the second number if 1st < 2nd, otherwise return 1st.
    SHL
    JRIC _umax16_le

    ; First number is already in the right spot, so just move the return
    ; and let's get out of here.
    ADDPCI 6
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 3
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 3

    ; Finally, restore the A register.
    LOAD A
    ADDPCI 3

    ; Now, return!
    RET

_umax16_le:
    ; First number is >= second number, return second number. We do this
    ; by copying the whole stack from the saved A register through the
    ; second number, up by two, and then returning.
    ADDPCI 8
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 3
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 3
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 3
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 3

    ; Now, restore the A register
    LOAD A
    ADDPCI 3

    ; Now, return!
    RET

umax32:
    ; Given two unsigned 32-bit integers on the stack, return the larger
    ; of the two on the stack. Does not clobber the U, V or SPC registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to get the max of 0x12345678 and 0x56789101, call this
    ; similar to:
    ;     PUSHI 0x01
    ;     PUSHI 0x91
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     CALL umax32
    ;
    ; Stack layout:
    ; PC + 0  - temporary second number storage
    ; PC + 1  - temporary second number storage
    ; PC + 2  - temporary second number storage
    ; PC + 3  - temporary second number storage
    ; PC + 4  - temporary first number storage
    ; PC + 5  - temporary first number storage
    ; PC + 6  - temporary first number storage
    ; PC + 7  - temporary first number storage
    ; PC + 8  - contents of A register preserved
    ; PC + 9  - return address
    ; PC + 10 - return address
    ; PC + 11 - second number
    ; PC + 12 - second number
    ; PC + 13 - second number
    ; PC + 14 - second number
    ; PC + 15 - first number
    ; PC + 16 - first number
    ; PC + 17 - first number
    ; PC + 18 - first number

    ; First, save the A register
    PUSH A

    ; Now, copy the first and second number so we can call ucmp.
    ADDPCI 3
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 12
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 12
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 12
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 12
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 12
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 12
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 12
    LOAD A
    SUBPCI 11
    STORE A
    SUBPCI 7

    ; Now, figure out which is less
    CALL ucmp32

    ; Return the second number if 1st < 2nd, otherwise return first.
    SHL
    JRIC _umax32_le

    ; First number is already in the right spot, so just move the return
    ; and let's get out of here.
    ADDPCI 10
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5

    ; Finally, restore the A register.
    LOAD A
    ADDPCI 5

    ; Now, return!
    RET

_umax32_le:
    ; First number is >= second number, return second number. We do this
    ; by copying the whole stack from the saved A register through the
    ; second number, up by two, and then returning.
    ADDPCI 14
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5
    LOAD A
    ADDPCI 4
    STORE A
    SUBPCI 5

    ; Now, restore the A register
    LOAD A
    ADDPCI 5

    ; Now, return!
    RET
