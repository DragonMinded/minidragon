strlen:
    ; Given a stack holding a pointer to a string, return the
    ; length of the string in the A register. Does not clobber
    ; the U/V registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you have a string at offset 0x1234, call like this:
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     CALL strlen
    ;
    ; Stack layout
    ; PC + 0 - saved U register
    ; PC + 1 - saved SPC
    ; PC + 2 - saved SPC
    ; PC + 3 - return address
    ; PC + 4 - return address
    ; PC + 5 - pointer to string high byte
    ; PC + 6 - pointer to string low byte

    ; First, save the calling function's local stack
    PUSH SPC

    ; Now save the temporary U register.
    PUSH U

    ; Now, move past the saved stack and set SPC to point at the string.
    ADDPCI 5
    POP SPC
    SUBPCI 7

    ; Set up the count, then point at the string.
    ZERO
    MOV A, U
    SWAP PC, SPC

    ; Now, until a null byte is encountered, add to our counter.
_strlen_loop:
    LOAD A
    ADDI 0
    JRIZ _strlen_done

    ; Move to next character.
    INCPC

    ; Add one to our counter.
    SWAP A, U
    INC
    SWAP U, A

    JRI _strlen_loop

_strlen_done:
    ; Grab the final count into the A register.
    SWAP PC, SPC
    MOV U, A

    ; Restore the U register.
    POP U

    ; Restore the SPC to what it was before we clobbered it.
    POP SPC

    ; Finally, return to caller.
    RET
