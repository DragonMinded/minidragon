atoi:
    ; Given a string pointed to on the stack, as long as it represents an
    ; integer either in the range of [-128, 127] or [0, 255], convert that
    ; string to an integer. Skips all leading whitespace, and allows for
    ; an optional preceeding +/- indicator. Stops at the first non-integer
    ; character it finds, returning the integer value in the A register.
    ;
    ; Note that unlike most of the other functions, this does modify the
    ; pointer to the string on the stack. The pointer will point to the
    ; first non-integer character (or null byte) found, so that atoi can
    ; be used in more complex input scanning.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you have a string buffer at 0x1234, call this similar to:
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     CALL atoi
    ;
    ; Stack layout at start:
    ; PC + 0 - return address.
    ; PC + 1 - return address.
    ; PC + 2 - pointer to string (will be updated).
    ; PC + 3 - pointer to string (will be updated).

    ; First, save the calling function's locals.
    PUSH SPC

    ; Now, assume that the number is positive for now.
    PUSHI 0

    ; Start with the number at zero as well.
    PUSHI 0

    ; Advance the stack pointer back to the pointer to the string.
    ADDPCI 6

_atoi_skip_whitespace:
    ; Stack layout when skipping leading space:
    ; PC + -6 - current accumulated result.
    ; PC + -5 - whether the number is negative (1) or not (0).
    ; PC + -4 - saved SPC.
    ; PC + -3 - saved SPC.
    ; PC + -2 - return address.
    ; PC + -1 - return address.
    ; PC + 0  - pointer to string (will be updated).
    ; PC + 1  - pointer to string (will be updated).

    ; See if the character is a space.
    LOADI " "

    ; Set the SPC to point at our string.
    POP SPC
    SWAP PC, SPC

    ; XOR the byte in the string against the space to check if they equal.
    XOR
    JRIZ _atoi_skip_ws_inc

    ; See if the character is a tab.
    LOADI "\t"
    XOR
    JRIZ _atoi_skip_ws_inc

    ; It is none of the characters we want to skip.
    JRI _atoi_check_positive

_atoi_skip_ws_inc:
    ; Increment our string pointer to skip the character.
    INCPC
    SWAP PC, SPC
    PUSH SPC

    ; Do it again!
    jri _atoi_skip_whitespace

_atoi_check_positive:
    ; Compare current pointed to byte against a "+"
    LOADI "+"
    XOR
    JRIZ _atoi_skip_plus_inc

    ; Check for a - sign, consume it if found.
    LOADI "-"
    XOR
    JRINZ _atoi_no_prefix

    ; Increment our string pointer to skip the character.
    INCPC
    SWAP PC, SPC
    PUSH SPC

    ; Remember that this was negative.
    SUBPCI 5
    STOREI 1
    ADDPCI 5
    JRI _atoi_number_loop

_atoi_no_prefix:
    ; Reset our stack pointer.
    SWAP PC, SPC
    SUBPCI 2
    JRI _atoi_number_loop

_atoi_skip_plus_inc:
    ; Increment our string pointer to skip the character.
    INCPC
    SWAP PC, SPC
    PUSH SPC

    ; Now, start consuming digit characters and adding them to our accumulator.
_atoi_number_loop:
    ; Stack layout at start of loop:
    ; PC + -6 - current accumulated result.
    ; PC + -5 - whether the number is negative (1) or not (0).
    ; PC + -4 - saved SPC.
    ; PC + -3 - saved SPC.
    ; PC + -2 - return address.
    ; PC + -1 - return address.
    ; PC + 0  - pointer to string advanced past leading space and +/- (will be updated).
    ; PC + 1  - pointer to string advanced past leading space and +/- (will be updated).

    ; Load with negative value of ascii "0", to subtract it from the number on the stack.
    LOADI -48

    ; Perform the math (ascii digit) - "0"
    POP SPC
    SWAP PC, SPC
    ADD

    ; See if it is negative (meaning a value < "0")
    SHL
    LNGJUMPC _atoi_number_end

    ; Do the above again, but checking to make sure it is <= "9"
    LOADI -58
    ADD
    SHL

    ; See if it is negative (meaning we are between "0" and "9" inclusive).
    JRINC _atoi_number_end

    ; We know the digit is between "0" and "9" inclusive, so let's multiply our
    ; current accumulated result and add the digit value in.
    SWAP PC, SPC
    SUBPCI 8

    ; Multiply by 10, getting the result in A.
    PUSHI 10
    CALL umult
    ADDPCI 2

    ; Store that accumulated result back in the same spot.
    PUSH A

    ; Now, load up the digit, subtract it from "0", add it to the current result.
    LOADI -48
    SWAP PC, SPC
    ADD
    INCPC
    SWAP PC, SPC
    ADD
    STORE A

    ; Update our pointer.
    ADDPCI 8
    PUSH SPC

    ; Do it again!
    LNGJUMP _atoi_number_loop

_atoi_number_end:
    ; The stack now points at the end of the string, whether that's a null byte
    ; or the beginning of a non-integer.

    SWAP PC, SPC

    ; See if we need to negate the number.
    SUBPCI 7
    LOAD A
    ADDI 0
    JRIZ _atoi_return_positive

    ; Load and negate the number, return.
    DECPC
    POP A
    NEG

    ; Restore the saved SPC
    INCPC
    POP SPC

    ; Finally, return.
    RET

_atoi_return_positive:
    ; Grab the number we accumulated, restore the stack.
    DECPC
    POP A
    INCPC
    POP SPC

    ; Finally, return.
    RET
