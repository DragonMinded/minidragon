strcpy:
    ; Given a stack holding a source and destination pointer, copy
    ; a null-terminated string from source to destination. Does not
    ; touch the A register.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to copy a string from 0x1234 to 0x5678, call like so:
    ;
    ; Stack layout
    ; PC + ? - saved SP
    ; PC + ? - saved SC
    ; PC + ? - saved A register
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - pointer to destination
    ; PC + ? - pointer to destination
    ; PC + ? - pointer to source
    ; PC + ? - pointer to source

    ; First, save the existing registers
    PUSH
    PUSHSPC

    ; Now, move to the source register
    ADDPC 7

_strcpy_loop:
    ; Grab a byte from the source
    POPSPC
    SWAP
    POP
    SWAP
    PUSHSPC

    ; Store that byte in the destination
    SUBPC 2
    POPSPC
    SWAP
    STORE
    INCPC
    SWAP
    PUSHSPC
    ADDPC 2

    ; See if we copied the null termination
    ADDI 0
    JRINZ _strcpy_loop

_strcpy_done:
    ; Restore the shadow stack and A register
    SUBPC 7
    POPSPC
    POP

    ; Now, return to caller
    RET
