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
    ; PC + ? - number of bytes copied
    ; PC + ? - pointer to end of destination
    ; PC + ? - pointer to end of destination
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

    ; Now, advance the destination pointer until we find the
    ; terminating null byte.
    ADDPCI 5
    POP SPC
    SWAP PC, SPC

_strcat_advance:
    ; Loop until we find the pointer to the null byte itself.
    LOAD A
    ADDI 0
    JRIZ _strcat_update_dest
    INCPC
    JRI _strcat_advance

_strcat_update_dest:
    SWAP PC, SPC
    SUBPCI 7
    PUSH SPC
    PUSHI 0

_strcat_loop:
    ; Keep track of number of bytes copied
    LOAD A
    INC
    STORE A
    ADDPCI 8
    ADDPCI 2

    ; Grab a byte from the source
    POP SPC
    SWAP PC, SPC
    POP A
    SWAP PC, SPC
    PUSH SPC

    ; Store that byte in the destination
    SUBPCI 8
    SUBPCI 1
    POP SPC
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 1

    ; See if we copied the null termination
    ADDI 0
    JRINZ _strcat_loop

_strcat_done:
    ; Restore the source stack pointer
    POP A
    NEG
    ADDPCI 8
    ADDPCI 1
    POP SPC
    SWAP PC, SPC
    ADDPC
    SWAP PC, SPC
    PUSH SPC

    ; Restore the shadow stack and A register
    SUBPCI 7
    POP A
    POP SPC

    ; Now, return to caller
    RET
