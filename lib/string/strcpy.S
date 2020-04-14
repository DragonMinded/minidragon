strcpy:
    ; Given a stack holding a source and destination pointer, copy
    ; a null-terminated string from source to destination. Does not
    ; touch the A register nor the source/destination pointer on the
    ; stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to copy a string from 0x1234 to 0x5678, call like so:
    ;     PUSH 0x78
    ;     PUSH 0x56
    ;     PUSH 0x34
    ;     PUSH 0x12
    ;     CALL strcpy
    ;
    ; Stack layout
    ; PC + ? - number of bytes copied
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
    PUSHSPC
    PUSH
    PUSHI 0

_strcpy_loop:
    ; Keep track of number of bytes copied
    LOADA
    INC
    STOREA
    ADDPCI 8

    ; Grab a byte from the source
    POPSPC
    SWAPPC
    POP
    SWAPPC
    PUSHSPC

    ; Store that byte in the destination
    SUBPCI 2
    POPSPC
    SWAPPC
    STOREA
    INCPC
    SWAPPC
    PUSHSPC
    SUBPCI 6

    ; See if we copied the null termination
    ADDI 0
    JRINZ _strcpy_loop

_strcpy_done:
    ; Restore the stack pointers
    POP
    NEG
    ADDPCI 5
    POPSPC
    SWAPPC
    ADDPC
    SWAPPC
    PUSHSPC
    ADDPCI 2
    POPSPC
    SWAPPC
    ADDPC
    SWAPPC
    PUSHSPC

    ; Restore the shadow stack and A register
    SUBPCI 7
    POP
    POPSPC

    ; Now, return to caller
    RET
