strcat:
    ; Given a stack holding a source and destination pointer, copy
    ; a null-terminated string from source to the end of the string
    ; at destination. Does not clobber the A/U/V register nor the
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
    ; PC + 0  - copy of pointer to source
    ; PC + 1  - copy of pointer to source
    ; PC + 2  - pointer to end of destination
    ; PC + 3  - pointer to end of destination
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

    ; Now, save copies of the source and destination pointers so we can iterate
    ; over them. Copy in a weird pattern so we end on the byte we need to be on
    ; for the advance loop.
    ADDPCI 5
    LOAD A
    SUBPCI 9
    STORE A
    ADDPCI 10
    LOAD A
    SUBPCI 9
    STORE A
    ADDPCI 11
    LOAD A
    SUBPCI 9
    STORE A
    ADDPCI 8
    LOAD A
    SUBPCI 9
    STORE A

    ; Now, advance the destination pointer until we find the terminating null byte.
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
    PUSH SPC
    SUBPCI 2

_strcat_loop:
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
    JRINZ _strcat_loop

_strcat_done:
    ; Restore the shadow stack and A register
    ADDPCI 4
    POP A
    POP SPC

    ; Now, return to caller
    RET
