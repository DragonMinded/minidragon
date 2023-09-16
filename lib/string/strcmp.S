strcmp:
    ; Given a stack holding a source and destination pointer, compare
    ; the two strings at the source and destination. If the source is
    ; alphabetically less than the destination, set A to -1 and return.
    ; If the strings are identical, set A to 0 and return. If the source
    ; is alphabetically greater than the destination, set A to 1 and
    ; return. Does not touch the source/destination pointers on the
    ; stack, nor does it clobber the U/V registers.
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
    ; PC + 0 - saved U register
    ; PC + 1 - saved V register
    ; PC + 2 - saved SP
    ; PC + 3 - saved SC
    ; PC + 4 - return address
    ; PC + 5 - return address
    ; PC + 6 - pointer to destination
    ; PC + 7 - pointer to destination
    ; PC + 8 - pointer to source
    ; PC + 9 - pointer to source

    ; First, save the existing registers.
    PUSH SPC

    ; Save the U register so we can use it for copies.
    PUSH V
    PUSH U
    ZERO
    MOV A, U

    ; Prime our stack location, point at the source.
    ADDPCI 8

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
    POP SPC
    SWAP PC, SPC
    POP A
    SWAP PC, SPC
    PUSH SPC

    ; Grab a byte from the destination
    SUBPCI 2
    POP SPC
    SWAP PC, SPC
    POP V
    SWAP PC, SPC
    PUSH SPC
    ADDPCI 2

    ; Compare the two bytes for equality.
    CMPV
    JRIZ _strcmp_check_null_term
    JRIC _strcmp_dest_later
    
    ; At this point, we know that the dest comes later than the source.
    LOADI -1
    JRI _strcmp_done

_strcmp_dest_later:
    ; At this point, we know that the dest comes earlier than the source.
    LOADI 1
    JRI _strcmp_done

_strcmp_check_null_term:
    ; They equal, see if we should bail (null hit, strings equal)
    ; or keep going (null not hit).
    ADDI 0
    JRINZ _strcmp_loop

_strcmp_done:
    ; A holds the comparison value at this point, including in the equal
    ; case where we bailed out (because adding 0 to 0 means we still have
    ; 0 in the A register).
    SWAP A, U

    ; Restore the stack pointers by subtracting the amount of bytes we compared.
    NEG
    POP SPC
    SWAP PC, SPC
    ADDPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 2
    POP SPC
    SWAP PC, SPC
    ADDPC
    SWAP PC, SPC
    PUSH SPC

    ; Restore the A register to the answer we calculated.
    SUBPCI 6
    SWAP A, U
    POP U
    POP V
    POP SPC

    ; Now, return to caller
    RET
