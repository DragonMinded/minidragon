strcpy:
    ; Given a stack holding a source and destination pointer, copy
    ; a null-terminated string from source to destination. Does not
    ; touch the A register nor the source/destination pointer on the
    ; stack.
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
    ; PC + ? - saved U register
    ; PC + ? - saved A register
    ; PC + ? - saved SP
    ; PC + ? - saved SC
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - pointer to destination
    ; PC + ? - pointer to destination
    ; PC + ? - pointer to source
    ; PC + ? - pointer to source

    ; First, save the existing registers
    PUSH SPC
    PUSH A
    PUSH U
    ADDPCI 8

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
    SUBPCI 2
    POP SPC
    SWAP PC, SPC
    STORE U
    INCPC
    SWAP PC, SPC
    PUSH SPC
    ADDPCI 2

    ; See if we copied the null termination
    SWAP U, A
    ADDI 0
    SWAP A, U
    JRINZ _strcpy_loop

_strcpy_done:
    ; Restore the stack pointers by negating the number of
    ; bytes copied and adding it to the stacks.
    NEG
    POP SPC
    SWAP PC, SPC
    ADDPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 2
    POP SPC
    SWAP PC, SPC
    ADDPC
    SWAP PC, SPC
    PUSH SPC

    ; Restore the shadow stack and A register
    SUBPCI 6
    POP U
    POP A
    POP SPC

    ; Now, return to caller
    RET
