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
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - second number
    ; PC + 3 - first number

    ; Simply use hardware comparison instruction.
    ADDPCI 3
    LOAD A
    DECPC
    CMP
    SUBPCI 2

    ; CF will be set if first > second, ZF will be set if first == second.
    JRIZ _ucmp_eq
    JRIC _ucmp_gr

    LOADI -1
    RET

_ucmp_eq:
    LOADI 0
    RET

_ucmp_gr:
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
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - second number high byte
    ; PC + 3 - second number low byte
    ; PC + 4 - first number high byte
    ; PC + 5 - first number low byte

    ; First, do the easy thing and see if they are equal, starting with the
    ; first byte.
    ADDPCI 4
    LOAD A
    SUBPCI 2
    CMP

    JRIZ _ucmp16_high_eq
    JRIC _ucmp16_high_gr

    ; First is less than second, return accordingly.
    SUBPCI 2
    LOADI -1
    RET

_ucmp16_high_gr:
    ; First is greater than second, return accordingly.
    SUBPCI 2
    LOADI 1
    RET

_ucmp16_high_eq:
    ; Now, check the second byte to see if they're equal.
    ADDPCI 3
    LOAD A
    SUBPCI 2
    CMP

    JRIZ _ucmp16_low_eq
    JRIC _ucmp16_low_gr

    ; First is less than second, return accordingly.
    SUBPCI 3
    LOADI -1
    RET

_ucmp16_low_gr:
    ; First is greater than second, return accordingly.
    SUBPCI 3
    LOADI 1
    RET

_ucmp16_low_eq:
    ; First is greater than second, return accordingly.
    SUBPCI 3
    LOADI 0
    RET



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
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - second number first byte
    ; PC + 3 - second number
    ; PC + 4 - second number
    ; PC + 5 - second number last byte
    ; PC + 6 - first number first byte
    ; PC + 7 - first number
    ; PC + 8 - first number
    ; PC + 9 - first number last byte

    ; First, do the easy thing and see if they are equal, starting with the
    ; first byte.
    ADDPCI 6
    LOAD A
    SUBPCI 4
    CMP

    JRIZ _ucmp32_1st_eq
    JRIC _ucmp32_1st_gr

    ; First is less than second, return accordingly.
    SUBPCI 2
    LOADI -1
    RET

_ucmp32_1st_gr:
    ; First is greater than second, return accordingly.
    SUBPCI 2
    LOADI 1
    RET

_ucmp32_1st_eq:
    ; Now, check the second byte to see if they're equal.
    ADDPCI 5
    LOAD A
    SUBPCI 4
    CMP

    JRIZ _ucmp32_2nd_eq
    JRIC _ucmp32_2nd_gr

    ; First is less than second, return accordingly.
    SUBPCI 3
    LOADI -1
    RET

_ucmp32_2nd_gr:
    ; First is greater than second, return accordingly.
    SUBPCI 3
    LOADI 1
    RET

_ucmp32_2nd_eq:
    ; Now, check the third byte to see if they're equal.
    ADDPCI 5
    LOAD A
    SUBPCI 4
    CMP

    JRIZ _ucmp32_3rd_eq
    JRIC _ucmp32_3rd_gr

    ; First is less than second, return accordingly.
    SUBPCI 4
    LOADI -1
    RET

_ucmp32_3rd_gr:
    ; First is greater than second, return accordingly.
    SUBPCI 4
    LOADI 1
    RET

_ucmp32_3rd_eq:
    ; Now, check the final number and see if they're equal.
    ADDPCI 5
    LOAD A
    SUBPCI 4
    CMP

    JRIZ _ucmp32_4th_eq
    JRIC _ucmp32_4th_gr

    ; First is less than second, return accordingly.
    SUBPCI 5
    LOADI -1
    RET

_ucmp32_4th_gr:
    ; First is greater than second, return accordingly.
    SUBPCI 5
    LOADI 1
    RET

_ucmp32_4th_eq:
    ; First is greater than second, return accordingly.
    SUBPCI 5
    LOADI 0
    RET



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
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - second number
    ; PC + 3 - first number

    ; First, figure out which number is actually bigger.
    ADDPCI 2
    LOAD A
    INCPC
    CMP

    JRIC _umin_ge

    ; Second number is bigger or equal.
    DECPC
    LOAD A
    SUBPCI 2
    RET
 
 _umin_ge:
    LOAD A
    SUBPCI 3
    RET


umin16:
    ; Given two unsigned 16-bit integers on the stack, return the smaller
    ; of the two on the stack. Does not clobber the A, U, V or SPC registers.
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
    ; of the two on the stack. Does not clobber the A, U, V or SPC registers.
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
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - second number
    ; PC + 3 - first number

    ; First, figure out which number is actually bigger.
    ADDPCI 2
    LOAD A
    INCPC
    CMP

    JRINC _umax_ge

    ; Second number is bigger or equal.
    DECPC
    LOAD A
    SUBPCI 2
    RET
 
 _umax_ge:
    LOAD A
    SUBPCI 3
    RET


umax16:
    ; Given two unsigned 16-bit integers on the stack, return the larger
    ; of the two on the stack. Does not clobber the A, U, V or SPC registers.
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
    ; of the two on the stack. Does not clobber the A, U, V or SPC registers.
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
