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
    ;     PUSH 0x78
    ;     PUSH 0x56
    ;     PUSH 0x34
    ;     PUSH 0x12
    ;     CALL strmp
    ;
    ; Stack layout
    ; PC + ? - saved destination byte
    ; PC + ? - saved source byte
    ; PC + ? - number of bytes compared
    ; PC + ? - saved SP
    ; PC + ? - saved SC
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - pointer to destination
    ; PC + ? - pointer to destination
    ; PC + ? - pointer to source
    ; PC + ? - pointer to source

    ; First, save the existing registers.
    PUSHSPC

    ; Keep track of how many bytes we compared so we can rewind.
    PUSHI 0

    ; Make room for source/destination byte.
    SUBPCI 2

    ; We can do an ugly hack, where we don't have to compare
    ; null bytes unless the current character of both strings match.
    ; If they don't match, then a null in one string will necessarily
    ; make it less than/greater than the other string and we will
    ; bail out correctly. If they match, then we either loop or exit
    ; depending on whether it is a null byte.
_strcmp_loop:
    ; Keep track of number of bytes compared
    ADDPCI 2
    LOAD
    INC
    STORE
    ADDPCI 7

    ; Grab a byte from the source
    POPSPC
    SWAP
    POP
    SWAP
    PUSHSPC

    ; Store that byte in our temp buffer
    SUBPCI 8
    STORE
    ADDPCI 6

    ; Grab a byte from the destination
    POPSPC
    SWAP
    POP
    SWAP
    PUSHSPC

    ; Store that byte in our second temp buffer
    SUBPCI 7
    STORE

    ; Compare the two bytes for equality.
    CALL ucmp

    ; See if the two bytes equal, if not, then we have our answer!
    ADDI 0
    JRINZ _strcmp_save_answer

    ; They equal, see if we should bail (null hit, strings equal)
    ; or keep going (null not hit).
    LOAD
    ADDI 0
    LNGJUMPNZ _strcmp_loop

_strcmp_save_answer:
    ; A holds the comparison value at this point, so save it to
    ; the stack.
    INCPC
    STORE

_strcmp_done:
    ; Restore the stack pointers
    INCPC
    LOAD
    NEG
    ADDPCI 5
    POPSPC
    SWAP
    ADDPC
    SWAP
    PUSHSPC
    ADDPCI 2
    POPSPC
    SWAP
    ADDPC
    SWAP
    PUSHSPC

    ; Restore the A register to the answer we calculated.
    SUBPCI 8
    POP
    INCPC
    POPSPC

    ; Now, return to caller
    RET
