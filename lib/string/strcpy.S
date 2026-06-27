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
    ; PC + 0 - saved U register
    ; PC + 1 - saved A register
    ; PC + 2 - saved SP
    ; PC + 3 - saved SC
    ; PC + 4 - return address
    ; PC + 5 - return address
    ; PC + 6 - pointer to source
    ; PC + 7 - pointer to source
    ; PC + 8 - pointer to destination
    ; PC + 9 - pointer to destination

    ; First, save the existing registers
    PUSH SPC
    PUSH A
    PUSH U
    ADDPCI 6

    ; Initialize the count of bytes we copied.
    ZERO

_strcpy_loop:
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
    JRINZ _strcpy_loop

_strcpy_done:
    ; Restore the stack pointers by negating the number of
    ; bytes copied and adding it to the stacks.

    ; If we copied an exactly 255 byte string, we're going to have a
    ; count of zero here due to copying the null byte. We always have
    ; at least one byte copied, so account for that here.
    DEC

    SHL
    JRINC _strcpy_less_than_128

    SWAP A, U

    LOADI -128
    POP SPC
    SWAP PC, SPC
    ADDPC
    SWAP PC, SPC
    PUSH SPC
    ADDPCI 2
    POP SPC
    SWAP PC, SPC
    ADDPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 2

    SWAP U, A

_strcpy_less_than_128:
    SHR
    NEG
    POP SPC
    SWAP PC, SPC
    ADDPC
    DECPC
    SWAP PC, SPC
    PUSH SPC
    ADDPCI 2
    POP SPC
    SWAP PC, SPC
    ADDPC
    DECPC
    SWAP PC, SPC
    PUSH SPC

    ; Restore the shadow stack and A register
    SUBPCI 8
    POP U
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
    ; PC + 0  - saved U register
    ; PC + 1  - saved A register
    ; PC + 2  - saved SP
    ; PC + 3  - saved SC
    ; PC + 4  - return address
    ; PC + 5  - return address
    ; PC + 6  - number of characters to copy
    ; PC + 7  - pointer to source
    ; PC + 8  - pointer to source
    ; PC + 9  - pointer to destination
    ; PC + 10 - pointer to destination

    ; First, save the existing registers
    PUSH SPC
    PUSH A
    PUSH U
    ADDPCI 7

    ; Initialize the count of bytes we copied.
    ZERO

_strncpy_loop:
    ; Figure out if we copied the right number of bytes
    DECPC
    POP U
    SWAP A, U
    XORU
    SWAP A, U
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
    INC
    SWAP A, U
    ZERO

    POP SPC
    SWAP PC, SPC
    INCPC
    SWAP PC, SPC
    PUSH SPC

    ADDPCI 2
    POP SPC
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 2

    SWAP A, U

_strncpy_done:
    ; Restore the stack pointers by negating the number of
    ; bytes copied and adding it to the stacks.

    ; If we copied an exactly 255 byte string, we're going to have a
    ; count of zero here due to copying the null byte. We always have
    ; at least one byte copied, so account for that here.
    DEC

    SHL
    JRINC _strncpy_less_than_128

    SWAP A, U

    LOADI -128
    POP SPC
    SWAP PC, SPC
    ADDPC
    SWAP PC, SPC
    PUSH SPC
    ADDPCI 2
    POP SPC
    SWAP PC, SPC
    ADDPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 2

    SWAP U, A

_strncpy_less_than_128:
    SHR
    NEG
    POP SPC
    SWAP PC, SPC
    ADDPC
    DECPC
    SWAP PC, SPC
    PUSH SPC
    ADDPCI 2
    POP SPC
    SWAP PC, SPC
    ADDPC
    DECPC
    SWAP PC, SPC
    PUSH SPC

    ; Restore the shadow stack and A register
    SUBPCI 9
    POP U
    POP A
    POP SPC

    ; Now, return to caller
    RET
