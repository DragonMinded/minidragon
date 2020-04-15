strcmp:
    ; Given a stack holding a source and destination pointer, compare
    ; the two strings at the source and destination. If the source is
    ; alphabetically less than the destination, set A to -1 and return.
    ; If the strings are identical, set A to 0 and return. If the source
    ; is alphabetically greater than the destination, set A to 1 and
    ; return. Does not touch the source/destination pointers on the
    ; stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to compare two strings at 0x1234 and 0x5678, call like so:
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     CALL strmp
    ;
    ; Stack layout
    ; PC + 0  - saved destination byte
    ; PC + 1  - saved source byte
    ; PC + 2  - saved U register
    ; PC + 3  - saved SP
    ; PC + 4  - saved SC
    ; PC + 5  - return address
    ; PC + 6  - return address
    ; PC + 7  - pointer to destination
    ; PC + 8  - pointer to destination
    ; PC + 9  - pointer to source
    ; PC + 10 - pointer to source

    ; First, save the existing registers.
    PUSH SPC

    ; Save the U register so we can use it for copies.
    PUSH U
    ZERO
    MOV A, U

    ; Move to the tip of the saved bytes to prime the loop
    ; below.
    SUBPCI 2

    ; We can do an ugly hack, where we don't have to compare
    ; null bytes unless the current character of both strings match.
    ; If they don't match, then a null in one string will necessarily
    ; make it less than/greater than the other string and we will
    ; bail out correctly. If they match, then we either loop or exit
    ; depending on whether it is a null byte.
_strcmp_loop:
    ; Keep track of number of bytes compared
    SWAP U, A
    INC
    SWAP A, U

    ; Grab a byte from the source
    ADDPCI 9
    POP SPC
    SWAP PC, SPC
    POP A
    SWAP PC, SPC
    PUSH SPC

    ; Store that byte in our temp buffer
    SUBPCI 8
    STORE A
    ADDPCI 6

    ; Grab a byte from the destination
    POP SPC
    SWAP PC, SPC
    POP A
    SWAP PC, SPC
    PUSH SPC

    ; Store that byte in our second temp buffer
    SUBPCI 7
    STORE A

    ; Compare the two bytes for equality.
    CALL ucmp

    ; See if the two bytes equal, if not, then we have our answer!
    ADDI 0
    JRINZ _strcmp_save_answer

    ; They equal, see if we should bail (null hit, strings equal)
    ; or keep going (null not hit).
    LOAD A
    ADDI 0
    LNGJUMPNZ _strcmp_loop

_strcmp_save_answer:
    ; A holds the comparison value at this point, so save it to
    ; the U register, and pop out the U register to A so we can
    ; fix up the stack pointers.
    SWAP U, A

_strcmp_done:
    ; Restore the stack pointers
    NEG
    ADDPCI 7
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

    ; Restore the A register to the answer we calculated.
    SUBPCI 7
    SWAP A, U
    POP U
    POP SPC

    ; Now, return to caller
    RET
