strlen:
    ; Given a stack holding a pointer to a string, return the
    ; length of the string in the A register.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you have a string at offset 0x1234, call like this:
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     CALL strlen
    ;
    ; Stack layout
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - pointer to string high byte
    ; PC + 3 - pointer to string low byte

    ; First, save the calling function's local stack
    PUSH SPC

    ; Now, move past the saved stack and set SPC to point at the string.
    ADDPCI 4
    POP SPC
    SUBPCI 7

    ; Set up the count, then point at the string.
    STOREI 0
    SWAP PC, SPC

    ; Now, until a null byte is encountered, add to our counter.
_strlen_loop:
    LOAD A
    ADDI 0
    JRIZ _strlen_done

    SWAP PC, SPC
    LOAD A
    INC
    STORE A
    SWAP PC, SPC
    INCPC

    JRI _strlen_loop

_strlen_done:
    ; Grab the final count into the A register.
    SWAP PC, SPC
    POP A

    ; Restore the SPC to what it was before we clobbered it.
    POP SPC

    ; Finally, return to caller.
    RET
