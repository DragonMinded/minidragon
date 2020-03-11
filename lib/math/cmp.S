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
    LOAD
    DECPC
    XOR
    JRINZ _ucmp_ne

    ; Its equal, so lets bail.
    SUBPCI 2
    LOADI 0
    RET

 _ucmp_ne:
    ; Make copies so we can mess with the numbers
    LOAD
    SUBPCI 4
    STORE
    ADDPCI 5
    LOAD
    SUBPCI 4
    STORE

    ; Technically we should only do this 8 times, for 8 bits,
    ; but given the base case above where they are equal, we
    ; know for a fact we will find a difference here, so no
    ; limit is applied.
_ucmp_loop:
    ; First, grab the first number, shift it left to check
    ; the top bit, and store it temporarily.
    LOAD
    SHL
    STORE

    ; If the top bit is 1, then A is >= B, so we check for that
    ; in the second if.
    JRIC _ucmp_first_high

    ; If the top bit is 0, then A is <= B, so we check for that
    ; here.
    DECPC
    LOAD
    SHL
    STORE
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
    LOAD
    SHL
    STORE
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
    LOAD
    SUBPCI 2
    XOR
    JRINZ _ucmp16_high_ne

    ; Now, check the second byte to see if they're equal.
    ADDPCI 3
    LOAD
    SUBPCI 2
    XOR
    JRINZ _ucmp16_low_ne

    ; Its equal, so lets bail.
    SUBPCI 3
    LOADI 0
    RET

 _ucmp16_high_ne:
    ; Make copies so we can mess with the numbers
    LOAD
    SUBPCI 4
    STORE
    ADDPCI 6
    LOAD
    SUBPCI 5
    STORE

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

 _ucmp16_low_ne:
    ; Make copies so we can mess with the numbers
    LOAD
    SUBPCI 5
    STORE
    ADDPCI 7
    LOAD
    SUBPCI 6
    STORE

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
    LOAD
    SUBPCI 4
    XOR
    JRINZ _ucmp32_1st_ne

    ; Now, check the second byte to see if they're equal.
    ADDPCI 5
    LOAD
    SUBPCI 4
    XOR
    JRINZ _ucmp32_2nd_ne

    ; Now, check the third byte to see if they're equal.
    ADDPCI 5
    LOAD
    SUBPCI 4
    XOR
    LNGJUMPNZ _ucmp32_3rd_ne

    ; Now, check the final byte to see if they're equal.
    ADDPCI 5
    LOAD
    SUBPCI 4
    XOR
    LNGJUMPNZ _ucmp32_4th_ne

    ; Its equal, so lets bail.
    SUBPCI 5
    LOADI 0
    RET

 _ucmp32_1st_ne:
    ; Make copies so we can mess with the numbers
    LOAD
    SUBPCI 4
    STORE
    ADDPCI 8
    LOAD
    SUBPCI 7
    STORE

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

 _ucmp32_2nd_ne:
    ; Make copies so we can mess with the numbers
    LOAD
    SUBPCI 5
    STORE
    ADDPCI 8
    INCPC
    LOAD
    SUBPCI 8
    STORE

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

 _ucmp32_3rd_ne:
    ; Make copies so we can mess with the numbers
    LOAD
    SUBPCI 6
    STORE
    ADDPCI 8
    ADDPCI 2
    LOAD
    SUBPCI 8
    DECPC
    STORE

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop

 _ucmp32_4th_ne:
    ; Make copies so we can mess with the numbers
    LOAD
    SUBPCI 7
    STORE
    ADDPCI 8
    ADDPCI 3
    LOAD
    SUBPCI 8
    SUBPCI 2
    STORE

    ; The rest of this algorithm is identical to other versions, since we
    ; know the bytes don't equal and we are just shifting out of stack.
    LNGJUMP _ucmp_loop
