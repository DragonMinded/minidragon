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
    ; PC + 0  - saved second byte
    ; PC + 1  - saved first byte
    ; PC + 2  - copy of pointer to second
    ; PC + 3  - copy of pointer to second
    ; PC + 4  - copy of pointer to first
    ; PC + 5  - copy of pointer to first
    ; PC + 6  - saved SP
    ; PC + 7  - saved SC
    ; PC + 8  - return address
    ; PC + 9  - return address
    ; PC + 10 - pointer to second
    ; PC + 11 - pointer to second
    ; PC + 12 - pointer to first
    ; PC + 13 - pointer to first

    ; First, save the existing registers.
    PUSH SPC

    ; Now, save copies of the source and destination pointers so we can iterate
    ; over them.
    ADDPCI 4
    LOAD A
    SUBPCI 8
    STORE A
    ADDPCI 9
    LOAD A
    SUBPCI 8
    STORE A
    ADDPCI 10
    LOAD A
    SUBPCI 8
    STORE A
    ADDPCI 7
    LOAD A
    SUBPCI 8
    STORE A

    ; Prime the loop because we assume we're pointing at the second byte when entering.
    SUBPCI 4

    ; We can do an ugly hack, where we don't have to compare
    ; null bytes unless the current character of both strings match.
    ; If they don't match, then a null in one string will necessarily
    ; make it less than/greater than the other string and we will
    ; bail out correctly. If they match, then we either loop or exit
    ; depending on whether it is a null byte.
_strcmp_loop:
    ; Grab a byte from the first
    ADDPCI 4
    POP SPC
    SWAP PC, SPC
    POP A
    SWAP PC, SPC
    PUSH SPC

    ; Store that byte in our temp buffer
    SUBPCI 3
    STORE A
    ADDPCI 1

    ; Grab a byte from the second
    POP SPC
    SWAP PC, SPC
    POP A
    SWAP PC, SPC
    PUSH SPC

    ; Store that byte in our second temp buffer
    SUBPCI 2
    STORE A

    ; Compare the two bytes for equality.
    CALL ucmp8

    ; See if the two bytes equal, if not, then we have our answer!
    ADDI 0
    JRINZ _strcmp_done

    ; They equal, see if we should bail (null hit, strings equal)
    ; or keep going (null not hit).
    LOAD A
    ADDI 0
    JRINZ _strcmp_loop

_strcmp_done:
    ; Restore the SPC register and return the value we already have in A.
    ADDPCI 6
    POP SPC

    ; Now, return to caller
    RET
