ucmp:
    ; Given two unsigned integers on the stack, return -1 if the first is less
    ; than the second, 0 if the first equals the second, and 1 if the
    ; first is greater than the second. Returns the value in the A
    ; register. Does not mess with the numbers on the stack.
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
    ; PC + 0 - second number shifted
    ; PC + 1 - first number shifted
    ; PC + 2 - return address
    ; PC + 3 - return address
    ; PC + 4 - second number
    ; PC + 5 - first number

    ; First, do the easy thing and see if they are equal.
    ADDPCI 3
    LOADA
    DECPC
    XOR
    JRINZ _ucmp_ne

    ; Its equal, so lets bail.
    SUBPCI 2
    LOADI 0
    RET

_ucmp_ne:
    ; Make copies so we can mess with the numbers
    LOADA
    SUBPCI 4
    STOREA
    ADDPCI 5
    LOADA
    SUBPCI 4
    STOREA

    ; Technically we should only do this 8 times, for 8 bits,
    ; but given the base case above where they are equal, we
    ; know for a fact we will find a difference here, so no
    ; limit is applied.
_ucmp_loop:
    ; First, grab the first number, shift it left to check
    ; the top bit, and store it temporarily.
    LOADA
    SHL
    STOREA

    ; If the top bit is 1, then A is >= B, so we check for that
    ; in the second if.
    JRIC _ucmp_first_high

    ; If the top bit is 0, then A is <= B, so we check for that
    ; here.
    DECPC
    LOADA
    SHL
    STOREA
    INCPC

    ; If the top bit is 0, then A == B as far as we know, since both
    ; their high bits match.
    JRINC _ucmp_loop

    ; If the top bit is 1, then A < B, since the high bit of B is
    ; set and the high bit of A is not set.
    ADDPCI 1
    LOADI -1
    RET

_ucmp_first_high:
    ; Now, grab the second number.
    DECPC
    LOADA
    SHL
    STOREA
    INCPC

    ; If the top bit is 0, then A is > B, since the high bit of A
    ; is set, and the high bit of B is not set. If the top bit is
    ; 1, then A == B as far as we know.
    JRIC _ucmp_loop

    ADDPCI 1
    LOADI 1
    RET

ucmp16:
    ; Given two 16-bit unsigned integers on the stack, return -1 if the first
    ; is less than the second, 0 if the first equals the second, and 1 if the
    ; first is greater than the second. Returns the value in the A
    ; register. Does not mess with the numbers on the stack.
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
    ; PC + 0 - second number shifted
    ; PC + 1 - first number shifted
    ; PC + 2 - return address
    ; PC + 3 - return address
    ; PC + 4 - second number high byte
    ; PC + 4 - second number low byte
    ; PC + 5 - first number high byte
    ; PC + 5 - first number low byte

    ; First, do the easy thing and see if they are equal, starting with the
    ; first byte.
    ADDPCI 4
    LOADA
    SUBPCI 2
    XOR
    JRINZ _ucmp16_high_ne

    ; Now, check the second byte to see if they're equal.
    ADDPCI 3
    LOADA
    SUBPCI 2
    XOR
    JRINZ _ucmp16_low_ne

    ; Its equal, so lets bail.
    SUBPCI 3
    LOADI 0
    RET

_ucmp16_high_ne:
    ; Make copies so we can mess with the numbers
    LOADA
    SUBPCI 4
    STOREA
    ADDPCI 6
    LOADA
    SUBPCI 5
    STOREA

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

_ucmp16_low_ne:
    ; Make copies so we can mess with the numbers
    LOADA
    SUBPCI 5
    STOREA
    ADDPCI 7
    LOADA
    SUBPCI 6
    STOREA

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

ucmp32:
    ; Given two 32-bit unsigned integers on the stack, return -1 if the first
    ; is less than the second, 0 if the first equals the second, and 1 if the
    ; first is greater than the second. Returns the value in the A
    ; register. Does not mess with the numbers on the stack.
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
    ; PC + 0  - second number shifted
    ; PC + 1  - first number shifted
    ; PC + 2  - return address
    ; PC + 3  - return address
    ; PC + 4  - second number
    ; PC + 5  - second number
    ; PC + 6  - second number
    ; PC + 7  - second number
    ; PC + 8  - first number
    ; PC + 9  - first number
    ; PC + 10 - first number
    ; PC + 11 - first number

    ; First, do the easy thing and see if they are equal, starting with the
    ; first byte.
    ADDPCI 6
    LOADA
    SUBPCI 4
    XOR
    JRINZ _ucmp32_1st_ne

    ; Now, check the second byte to see if they're equal.
    ADDPCI 5
    LOADA
    SUBPCI 4
    XOR
    JRINZ _ucmp32_2nd_ne

    ; Now, check the third byte to see if they're equal.
    ADDPCI 5
    LOADA
    SUBPCI 4
    XOR
    LNGJUMPNZ _ucmp32_3rd_ne

    ; Now, check the final byte to see if they're equal.
    ADDPCI 5
    LOADA
    SUBPCI 4
    XOR
    LNGJUMPNZ _ucmp32_4th_ne

    ; Its equal, so lets bail.
    SUBPCI 5
    LOADI 0
    RET

_ucmp32_1st_ne:
    ; Make copies so we can mess with the numbers
    LOADA
    SUBPCI 4
    STOREA
    ADDPCI 8
    LOADA
    SUBPCI 7
    STOREA

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

_ucmp32_2nd_ne:
    ; Make copies so we can mess with the numbers
    LOADA
    SUBPCI 5
    STOREA
    ADDPCI 8
    INCPC
    LOADA
    SUBPCI 8
    STOREA

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

_ucmp32_3rd_ne:
    ; Make copies so we can mess with the numbers
    LOADA
    SUBPCI 6
    STOREA
    ADDPCI 8
    ADDPCI 2
    LOADA
    SUBPCI 8
    DECPC
    STOREA

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

_ucmp32_4th_ne:
    ; Make copies so we can mess with the numbers
    LOADA
    SUBPCI 7
    STOREA
    ADDPCI 8
    ADDPCI 3
    LOADA
    SUBPCI 8
    SUBPCI 2
    STOREA

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

umin:
    ; Given two unsigned integers on the stack, return the smaller of the
    ; two in the A register. Does not mess with the numbers on the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To get the min of 5 and 7, call it like so:
    ;     PUSH 5
    ;     PUSH 7
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
    LOADA
    SUBPCI 4
    STOREA
    ADDPCI 3
    LOADA
    SUBPCI 4
    STOREA

    ; Now, figure out which is less
    CALL ucmp

    ; Return the first number if 1st < 2nd, otherwise return second.
    SHL
    JRINC _umin_ge

    INCPC
    LOADA
    INCPC
    RET

_umin_ge:
    ; First number is >= second number, return second number.
    LOADA
    ADDPCI 2
    RET

umin16:
    ; Given two unsigned 16-bit integers on the stack, return the smaller
    ; of the two on the stack. Does not mess with the A register.
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
    PUSH

    ; Now, copy the first and second number so we can call ucmp.
    ADDPCI 3
    LOADA
    SUBPCI 7
    STOREA
    ADDPCI 8
    LOADA
    SUBPCI 7
    STOREA
    ADDPCI 8
    LOADA
    SUBPCI 7
    STOREA
    ADDPCI 8
    LOADA
    SUBPCI 7
    STOREA
    SUBPCI 3

    ; Now, figure out which is less
    CALL ucmp16

    ; Return the first number if 1st < 2nd, otherwise return second.
    SHL
    JRINC _umin16_ge

    ; First number is already in the right spot, so just move the return
    ; and let's get out of here.
    ADDPCI 6
    LOADA
    ADDPCI 2
    STOREA
    SUBPCI 3
    LOADA
    ADDPCI 2
    STOREA
    SUBPCI 3

    ; Finally, restore the A register.
    LOADA
    ADDPCI 3

    ; Now, return!
    RET

_umin16_ge:
    ; First number is >= second number, return second number. We do this
    ; by copying the whole stack from the saved A register through the
    ; second number, up by two, and then returning.
    ADDPCI 8
    LOADA
    ADDPCI 2
    STOREA
    SUBPCI 3
    LOADA
    ADDPCI 2
    STOREA
    SUBPCI 3
    LOADA
    ADDPCI 2
    STOREA
    SUBPCI 3
    LOADA
    ADDPCI 2
    STOREA
    SUBPCI 3

    ; Now, restore the A register
    LOADA
    ADDPCI 3

    ; Now, return!
    RET

umin32:
    ; Given two unsigned 32-bit integers on the stack, return the smaller
    ; of the two on the stack. Does not mess with the A register.
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
    PUSH

    ; Now, copy the first and second number so we can call ucmp.
    ADDPCI 3
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    ADDPCI 8
    ADDPCI 4
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    ADDPCI 8
    ADDPCI 4
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    ADDPCI 8
    ADDPCI 4
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    ADDPCI 8
    ADDPCI 4
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    ADDPCI 8
    ADDPCI 4
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    ADDPCI 8
    ADDPCI 4
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    ADDPCI 8
    ADDPCI 4
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    SUBPCI 7

    ; Now, figure out which is less
    CALL ucmp32

    ; Return the first number if 1st < 2nd, otherwise return second.
    SHL
    JRINC _umin32_ge

    ; First number is already in the right spot, so just move the return
    ; and let's get out of here.
    ADDPCI 8
    ADDPCI 2
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5

    ; Finally, restore the A register.
    LOADA
    ADDPCI 5

    ; Now, return!
    RET

_umin32_ge:
    ; First number is >= second number, return second number. We do this
    ; by copying the whole stack from the saved A register through the
    ; second number, up by two, and then returning.
    ADDPCI 8
    ADDPCI 6
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5

    ; Now, restore the A register
    LOADA
    ADDPCI 5

    ; Now, return!
    RET

umax:
    ; Given two unsigned integers on the stack, return the larger of the
    ; two in the A register. Does not mess with the numbers on the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; To get the max of 5 and 7, call it like so:
    ;     PUSH 5
    ;     PUSH 7
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
    LOADA
    SUBPCI 4
    STOREA
    ADDPCI 3
    LOADA
    SUBPCI 4
    STOREA

    ; Now, figure out which is less
    CALL ucmp

    ; Return the first number if 1st > 2nd, otherwise return second.
    SHL
    JRIC _umax_le

    INCPC
    LOADA
    INCPC
    RET

_umax_le:
    ; First number is >= second number, return second number.
    LOADA
    ADDPCI 2
    RET

umax16:
    ; Given two unsigned 16-bit integers on the stack, return the larger
    ; of the two on the stack. Does not mess with the A register.
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
    PUSH

    ; Now, copy the first and second number so we can call ucmp.
    ADDPCI 3
    LOADA
    SUBPCI 7
    STOREA
    ADDPCI 8
    LOADA
    SUBPCI 7
    STOREA
    ADDPCI 8
    LOADA
    SUBPCI 7
    STOREA
    ADDPCI 8
    LOADA
    SUBPCI 7
    STOREA
    SUBPCI 3

    ; Now, figure out which is less
    CALL ucmp16

    ; Return the second number if 1st < 2nd, otherwise return 1st.
    SHL
    JRIC _umax16_le

    ; First number is already in the right spot, so just move the return
    ; and let's get out of here.
    ADDPCI 6
    LOADA
    ADDPCI 2
    STOREA
    SUBPCI 3
    LOADA
    ADDPCI 2
    STOREA
    SUBPCI 3

    ; Finally, restore the A register.
    LOADA
    ADDPCI 3

    ; Now, return!
    RET

_umax16_le:
    ; First number is >= second number, return second number. We do this
    ; by copying the whole stack from the saved A register through the
    ; second number, up by two, and then returning.
    ADDPCI 8
    LOADA
    ADDPCI 2
    STOREA
    SUBPCI 3
    LOADA
    ADDPCI 2
    STOREA
    SUBPCI 3
    LOADA
    ADDPCI 2
    STOREA
    SUBPCI 3
    LOADA
    ADDPCI 2
    STOREA
    SUBPCI 3

    ; Now, restore the A register
    LOADA
    ADDPCI 3

    ; Now, return!
    RET

umax32:
    ; Given two unsigned 32-bit integers on the stack, return the larger
    ; of the two on the stack. Does not mess with the A register.
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
    PUSH

    ; Now, copy the first and second number so we can call ucmp.
    ADDPCI 3
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    ADDPCI 8
    ADDPCI 4
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    ADDPCI 8
    ADDPCI 4
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    ADDPCI 8
    ADDPCI 4
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    ADDPCI 8
    ADDPCI 4
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    ADDPCI 8
    ADDPCI 4
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    ADDPCI 8
    ADDPCI 4
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    ADDPCI 8
    ADDPCI 4
    LOADA
    SUBPCI 8
    SUBPCI 3
    STOREA
    SUBPCI 7

    ; Now, figure out which is less
    CALL ucmp32

    ; Return the second number if 1st < 2nd, otherwise return first.
    SHL
    JRIC _umax32_le

    ; First number is already in the right spot, so just move the return
    ; and let's get out of here.
    ADDPCI 8
    ADDPCI 2
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5

    ; Finally, restore the A register.
    LOADA
    ADDPCI 5

    ; Now, return!
    RET

_umax32_le:
    ; First number is >= second number, return second number. We do this
    ; by copying the whole stack from the saved A register through the
    ; second number, up by two, and then returning.
    ADDPCI 8
    ADDPCI 6
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5
    LOADA
    ADDPCI 4
    STOREA
    SUBPCI 5

    ; Now, restore the A register
    LOADA
    ADDPCI 5

    ; Now, return!
    RET
