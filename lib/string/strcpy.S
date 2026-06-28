strcpy:
    ; Given a stack holding a source and destination pointer, copy
    ; a null-terminated string from source to destination. Does not
    ; clobber the A/U/V register nor the source/destination pointer on
    ; the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to copy a string from 0x1234 to 0x5678, call like so:
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     CALL strcpy
    ;
    ; Stack layout
    ; PC + 0  - copy of source pointer
    ; PC + 1  - copy of source pointer
    ; PC + 2  - copy of destination pointer
    ; PC + 3  - copy of destination pointer
    ; PC + 4  - saved A register
    ; PC + 5  - saved SP
    ; PC + 6  - saved SC
    ; PC + 7  - return address
    ; PC + 8  - return address
    ; PC + 9  - pointer to source
    ; PC + 10 - pointer to source
    ; PC + 11 - pointer to destination
    ; PC + 12 - pointer to destination

    ; First, save the existing registers
    PUSH SPC
    PUSH A

    ; Now, copy source and destination pointers so we can safely iterate.
    ADDPCI 8
    LOAD A
    SUBPCI 9
    STORE A
    ADDPCI 8
    LOAD A
    SUBPCI 9
    STORE A
    ADDPCI 8
    LOAD A
    SUBPCI 9
    STORE A
    ADDPCI 8
    LOAD A
    SUBPCI 9
    STORE A

_strcpy_loop:
    ; Grab a byte from the source
    POP SPC
    SWAP PC, SPC
    POP A
    SWAP PC, SPC
    PUSH SPC

    ; Store that byte in the destination
    ADDPCI 2
    POP SPC
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 2

    ; See if we copied the null termination
    ADDI 0
    JRINZ _strcpy_loop

    ; Restore the shadow stack and A register
    ADDPCI 4
    POP A
    POP SPC

    ; Now, return to caller
    RET

strncpy:
    ; Given a stack holding a source and destination pointer as well as the maximum
    ; number of characters to copy, copy a null-terminated string from source to
    ; destination. Always null-terminates. Number of characters to copy does not
    ; include the null termination which is always present. Does not clobber the
    ; A/U/V register nor the source/destination pointer on the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to copy a 5 bytes of a string from 0x1234 to 0x5678, call like so:
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     PUSHI 5
    ;     CALL strncpy
    ;
    ; Stack layout
    ; PC + 0  - copy of source pointer
    ; PC + 1  - copy of source pointer
    ; PC + 2  - copy of destination pointer
    ; PC + 3  - copy of destination pointer
    ; PC + 4  - saved U register
    ; PC + 5  - saved A register
    ; PC + 6  - saved SP
    ; PC + 7  - saved SC
    ; PC + 8  - return address
    ; PC + 9  - return address
    ; PC + 10 - number of characters to copy
    ; PC + 11 - pointer to source
    ; PC + 12 - pointer to source
    ; PC + 13 - pointer to destination
    ; PC + 14 - pointer to destination

    ; First, save the existing registers
    PUSH SPC
    PUSH A
    PUSH U

    ; Copy source and destination pointers so we can iterate safely.
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
    ADDPCI 10
    LOAD A
    SUBPCI 11
    STORE A

    ; Initialize the count of bytes we copied.
    ZERO

_strncpy_loop:
    ; Figure out if we copied the right number of bytes
    ADDPCI 10
    LOAD U
    SWAP A, U
    XORU
    SWAP A, U
    SUBPCI 10
    JRIZ _strncpy_exit_early

    ; Keep track of number of bytes copied
    INC

    ; Grab a byte from the source
    POP SPC
    SWAP PC, SPC
    POP U
    SWAP PC, SPC
    PUSH SPC

    ; Store that byte in the destination
    ADDPCI 2
    POP SPC
    SWAP PC, SPC
    STORE U
    INCPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 2

    ; See if we copied the null termination
    SWAP U, A
    ADDI 0
    SWAP A, U
    SKIPIF !ZF
    JRI _strncpy_done
    JRI _strncpy_loop

_strncpy_exit_early:
    ; Need to null-terminate the destination since we didn't do it normally.
    ZERO

    ADDPCI 2
    POP SPC
    SWAP PC, SPC
    STORE A
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 2

_strncpy_done:
    ; Restore the shadow stack and A register
    ADDPCI 4
    POP U
    POP A
    POP SPC

    ; Now, return to caller
    RET
