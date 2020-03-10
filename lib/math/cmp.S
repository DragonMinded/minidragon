cmp:
    ; Given two integers on the stack, return -1 is the first is less
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
    ;     CALL abs
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
    JRINZ _cmp_ne

    ; Its equal, so lets bail.
    SUBPCI 2
    LOADI 0
    RET

 _cmp_ne:
    ; Technically we should only do this 8 times, for 8 bits,
    ; but given the base case above where they are equal, we
    ; know for a fact we will find a difference here, so no
    ; limit is applied.

    ; Make copies so we can mess with the numbers
    LOAD
    SUBPCI 4
    STORE
    ADDPCI 5
    LOAD
    SUBPCI 4
    STORE

_cmp_loop:
    ; First, grab the first number, shift it left to check
    ; the top bit, and store it temporarily.
    LOAD
    SHL
    STORE

    ; If the top bit is 1, then A is >= B, so we check for that
    ; in the second if.
    JRIC _cmp_first_high

    ; If the top bit is 0, then A is <= B, so we check for that
    ; here.
    DECPC
    LOAD
    SHL
    STORE
    INCPC

    ; If the top bit is 0, then A == B as far as we know, since both
    ; their high bits match.
    JRINC _cmp_loop

    ; If the top bit is 1, then A < B, since the high bit of B is
    ; set and the high bit of A is not set.
    ADDPCI 1
    LOADI -1
    RET

_cmp_first_high:
    ; Now, grab the second number.
    DECPC
    LOAD
    SHL
    STORE
    INCPC

    ; If the top bit is 0, then A is > B, since the high bit of A
    ; is set, and the high bit of B is not set. If the top bit is
    ; 1, then A == B as far as we know.
    JRIC _cmp_loop

    ADDPCI 1
    LOADI 1
    RET
