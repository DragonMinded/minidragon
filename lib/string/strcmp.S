strcmp:
    ; Given a stack holding a first and second string pointer, compare
    ; the two strings at the first and second locations. If the first is
    ; alphabetically less than the second, set A to -1 and return. If the
    ; strings are identical, set A to 0 and return. If the first is
    ; alphabetically greater than the second, set A to 1 and return. Does
    ; not touch the first/second pointers on the stack, nor does it clobber
    ; the U/V registers.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to compare two strings at 0x1234 and 0x5678, call like so:
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     CALL strmp
    ;
    ; Stack layout
    ; PC + 0  - copy of pointer to second
    ; PC + 1  - copy of pointer to second
    ; PC + 2  - copy of pointer to first
    ; PC + 3  - copy of pointer to first
    ; PC + 4  - saved U register
    ; PC + 5  - saved SP
    ; PC + 6  - saved SC
    ; PC + 7  - return address
    ; PC + 8  - return address
    ; PC + 9  - pointer to second
    ; PC + 10 - pointer to second
    ; PC + 11 - pointer to first
    ; PC + 12 - pointer to first

    ; First, save the existing registers.
    PUSH SPC
    PUSH U

    ; Now, save copies of the source and destination pointers so we can iterate
    ; over them.
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

    ; We can do an ugly hack, where we don't have to compare
    ; null bytes unless the current character of both strings match.
    ; If they don't match, then a null in one string will necessarily
    ; make it less than/greater than the other string and we will
    ; bail out correctly. If they match, then we either loop or exit
    ; depending on whether it is a null byte.
_strcmp_loop:
    ; Grab a byte from the first
    POP SPC
    SWAP PC, SPC
    POP A
    SWAP PC, SPC
    PUSH SPC

    ; Grab a byte from the second
    SUBPCI 2
    POP SPC
    SWAP PC, SPC
    POP U
    SWAP PC, SPC
    PUSH SPC
    ADDPCI 2

    ; Compare the two bytes for equality.
    CMPU

    ; See if the two bytes equal, if not, then we have to set A accordingly.
    JRINZ _strcmp_set_unequal

    ; If they're equal, check for null termination.
    ADDI 0
    JRINZ _strcmp_loop
    JRI _strcmp_done

_strcmp_set_unequal:
    LOADI -1
    SKIPIF !CF
    NEG

_strcmp_done:
    ; Restore the SPC register and return the value we already have in A.
    ADDPCI 2
    POP U
    POP SPC

    ; Now, return to caller
    RET
