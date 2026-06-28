strlen:
    ; Given a stack holding a pointer to a string, return the
    ; length of the string in the A register. Does not clobber
    ; the U/V registers nor the string pointer on the stack.
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

wstrlen:
    ; Given a stack holding a pointer to a string, return the length of the
    ; string on the stack as a 16 bit integer. Does not clobber the A/U/V
    ; registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you have a string at offset 0x1234, call like this:
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     CALL wstrlen
    ;
    ; Stack layout just after call:
    ; PC + 0 - saved A register
    ; PC + 1 - saved SPC
    ; PC + 2 - saved SPC
    ; PC + 3 - return address
    ; PC + 4 - return address
    ; PC + 5 - pointer to string high byte
    ; PC + 6 - pointer to string low byte
    ;
    ; Stack layout during loop:
    ; PC + 0 - copy of string high byte
    ; PC + 1 - copy of string low byte
    ; PC + 2 - saved A register
    ; PC + 3 - saved SPC
    ; PC + 4 - saved SPC
    ; PC + 5 - return address
    ; PC + 6 - return address
    ; PC + 7 - string length high byte
    ; PC + 8 - string length low byte
    ;
    ; Stack layout just before return:
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - string length high byte
    ; PC + 3 - string length low byte

    ; Save clobbered registers
    PUSH SPC
    PUSH A

    ; Copy our string so we can iterate over it.
    ADDPCI 6
    LOAD A
    SUBPCI 7
    STORE A
    ADDPCI 6
    LOAD A
    SUBPCI 7
    STORE A

    ; Initialize our return value to 0 so we can increment it.
    ZERO
    ADDPCI 7
    STORE A
    INCPC
    STORE A
    SUBPCI 8

_wstrlen_loop:
    ; Grab the next byte from the string so we can check if it is the null terminator.
    POP SPC
    SWAP PC, SPC
    LOAD A
    INCPC
    SWAP PC, SPC
    PUSH SPC

    ; Perform that check here, skip to the end if we encountered the null byte since
    ; we already have the count in the right spot.
    ADDI 0
    JRIZ _wstrlen_done

    ; Add one to our count
    ADDPCI 7
    POP SPC
    SWAP PC, SPC
    INCPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 7

    ; Second verse, same as the first!
    JRI _wstrlen_loop

_wstrlen_done:
    ; We just need to restore SPC and A and we're done!
    ADDPCI 2
    POP A
    POP SPC

    ; Return the answer.
    RET
