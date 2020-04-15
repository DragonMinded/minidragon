strcat:
    ; Given a stack holding a source and destination pointer, copy
    ; a null-terminated string from source to the end of the string
    ; at destination. Does not touch the A register nor the
    ; source/destination pointer on the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to copy a string from 0x1234 to the end of the string
    ; at 0x5678, call like so:
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     CALL strcat
    ;
    ; Stack layout
    ; PC + ? - pointer to end of destination
    ; PC + ? - pointer to end of destination
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

    ; Now, advance the destination pointer until we find the
    ; terminating null byte.
    ADDPCI 6
    POP SPC
    SWAP PC, SPC

    ; We don't need to initialize the count of bytes copied because
    ; we first advance until we find a null pointer. Null is zero,
    ; so this loop below will init our count!

_strcat_advance:
    ; Loop until we find the pointer to the null byte itself.
    LOAD A
    ADDI 0
    JRIZ _strcat_update_dest
    INCPC
    JRI _strcat_advance

_strcat_update_dest:
    SWAP PC, SPC
    SUBPCI 8
    PUSH SPC
    ADDPCI 10

_strcat_loop:
    ; Keep track of number of bytes copied
    INC

    ; Grab a byte from the source
    POP SPC
    SWAP PC, SPC
    POP U
    SWAP PC, SPC
    PUSH SPC

    ; Store that byte in the destination
    SUBPCI 10
    POP SPC
    SWAP PC, SPC
    STORE U
    INCPC
    SWAP PC, SPC
    PUSH SPC
    ADDPCI 10

    ; See if we copied the null termination
    SWAP U, A
    ADDI 0
    SWAP A, U
    JRINZ _strcat_loop

_strcat_done:
    ; Restore the source stack pointer
    NEG
    POP SPC
    SWAP PC, SPC
    ADDPC
    SWAP PC, SPC
    PUSH SPC

    ; Restore the shadow stack and A register
    SUBPCI 8
    POP U
    POP A
    POP SPC

    ; Now, return to caller
    RET
