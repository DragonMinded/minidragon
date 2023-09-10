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
    ; be used in more complex input scanning. Does not clobber the U/V
    ; registers or the SPC.
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
    PUSH U
    PUSH V

    ; Now, assume that the number is positive for now. U will be
    ; the negation indicator.
    ZERO
    MOV A, U

    ; Now, start with the number itself being zero. V will be the
    ; accumulated number.
    MOV A, V

    ; Advance the stack pointer back to the pointer to the string.
    ADDPCI 6
    POP SPC
    SWAP PC, SPC

_atoi_skip_whitespace:
    ; Stack layout when skipping leading space:
    ; PC + -8 - saved V register.
    ; PC + -7 - saved U register.
    ; PC + -6 - saved SPC.
    ; PC + -5 - saved SPC.
    ; PC + -4 - return address.
    ; PC + -3 - return address.
    ; PC + -2 - pointer to string (will be updated).
    ; PC + -1 - pointer to string (will be updated).

    ; See if the character is a space.
    LOADI " "

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
    JRINZ _atoi_number_loop

    ; Remember that this was negative.
    LOADI 1
    MOV A, U

_atoi_skip_plus_inc:
    ; Increment our string pointer to skip the character.
    INCPC

    ; Now, start consuming digit characters and adding them to our accumulator.
_atoi_number_loop:
    ; Stack layout at start of loop:
    ; PC + -8 - saved V register.
    ; PC + -7 - saved U register.
    ; PC + -6 - saved SPC.
    ; PC + -5 - saved SPC.
    ; PC + -4 - return address.
    ; PC + -3 - return address.
    ; PC + -2 - pointer to string advanced past leading space and +/- (will be updated).
    ; PC + -1 - pointer to string advanced past leading space and +/- (will be updated).

    ; Load with negative value of ascii "0", to subtract it from the number on the stack.
    LOADI -48

    ; Perform the math (ascii digit) - "0"
    ADD

    ; See if it is negative (meaning a value < "0")
    SHL
    JRIC _atoi_number_end

    ; Do the above again, but checking to make sure it is <= "9"
    LOADI -58
    ADD
    SHL

    ; See if it is negative (meaning we are between "0" and "9" inclusive).
    JRINC _atoi_number_end

    ; We know the digit is between "0" and "9" inclusive, so let's multiply our
    ; current accumulated result and add the digit value in.
    SWAP PC, SPC
    SUBPCI 9
    STORE V

    ; Multiply by 10, getting the result in A.
    PUSHI 10
    CALL umult
    ADDPCI 10
    SWAP PC, SPC

    ; Store that accumulated result back into our accumulated result register.
    MOV A, V

    ; Now, load up the digit, subtract it from "0", add it to the current result.
    LOADI -48
    ADD
    INCPC
    ADDV
    MOV A, V

    ; Do it again!
    LNGJUMP _atoi_number_loop

_atoi_number_end:
    ; The stack now points at the end of the string, whether that's a null byte
    ; or the beginning of a non-integer. Save it back so the calling function
    ; can implement things like sscanf().
    SWAP PC, SPC
    PUSH SPC

    ; See if we need to negate the number.
    MOV U, A
    ADDI 0
    MOV V, A
    JRIZ _atoi_return_positive

    ; Load and negate the number, return.
    NEG

_atoi_return_positive:
    ; Restore U/V
    SUBPCI 6
    POP V
    POP U

    ; Restore the saved SPC
    POP SPC

    ; Finally, return.
    RET
