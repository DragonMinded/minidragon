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
    ; PC + 0 - Saved V.
    ; PC + 1 - Saved U.
    ; PC + 2 - Saved SPC.
    ; PC + 3 - Saved SPC.
    ; PC + 4 - return address.
    ; PC + 5 - return address.
    ; PC + 6 - pointer to string (will be updated).
    ; PC + 7 - pointer to string (will be updated).

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


atoi16:
    ; Given a string pointed to on the stack, as long as it represents an
    ; integer either in the range of [-32768, 32767] or [0, 65535], convert
    ; that string to an integer. Skips all leading whitespace, and allows
    ; for an optional preceeding +/- indicator. Stops at the first non-integer
    ; character it finds, returning the integer value on the stack. Note that
    ; the caller is responsible for allocating stack space for the response.
    ;
    ; Note that unlike most of the other functions, this does modify the
    ; pointer to the string on the stack. The pointer will point to the
    ; first non-integer character (or null byte) found, so that atoi can
    ; be used in more complex input scanning. Does not clobber the A/U/V
    ; registers or the SPC.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you have a string buffer at 0x1234, call this similar to:
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     SUBPCI 2
    ;     CALL atoi16
    ;
    ; Stack layout at start:
    ; PC + 0  - temporary converted integer.
    ; PC + 1  - temporary converted integer.
    ; PC + 2  - Saved A.
    ; PC + 3  - Saved V.
    ; PC + 4  - Saved U.
    ; PC + 5  - Saved SPC.
    ; PC + 6  - Saved SPC.
    ; PC + 7  - return address.
    ; PC + 8  - return address.
    ; PC + 9  - final converted integer.
    ; PC + 10 - final converted integer.
    ; PC + 11 - pointer to string (will be updated).
    ; PC + 12 - pointer to string (will be updated).

    ; First, save the calling function's locals.
    PUSH SPC
    PUSH U
    PUSH V
    PUSH A

    ; Now, assume that the number is positive for now. U will be
    ; the negation indicator.
    ZERO
    MOV A, U

    ; Now, start with the number itself being zero. The stack location
    ; will be the accumulated number.
    PUSH A
    PUSH A

    ; Advance the stack pointer back to the pointer to the string.
    ADDPCI 11
    POP SPC
    SUBPCI 13
    SWAP PC, SPC

_atoi16_skip_whitespace:
    ; See if the character is a space.
    LOADI " "

    ; XOR the byte in the string against the space to check if they equal.
    XOR
    JRIZ _atoi16_skip_ws_inc

    ; See if the character is a tab.
    LOADI "\t"
    XOR
    JRIZ _atoi16_skip_ws_inc

    ; It is none of the characters we want to skip.
    JRI _atoi16_check_positive

_atoi16_skip_ws_inc:
    ; Increment our string pointer to skip the character.
    INCPC

    ; Do it again!
    jri _atoi16_skip_whitespace

_atoi16_check_positive:
    ; Compare current pointed to byte against a "+"
    LOADI "+"
    XOR
    JRIZ _atoi16_skip_plus_inc

    ; Check for a - sign, consume it if found.
    LOADI "-"
    XOR
    JRINZ _atoi16_number_loop

    ; Remember that this was negative.
    LOADI 1
    MOV A, U

_atoi16_skip_plus_inc:
    ; Increment our string pointer to skip the character.
    INCPC

    ; Now, start consuming digit characters and adding them to our accumulator.
_atoi16_number_loop:
    ; Load with negative value of ascii "0", to subtract it from the number on the stack.
    LOADI -48

    ; Perform the math (ascii digit) - "0"
    ADD

    ; See if it is negative (meaning a value < "0")
    SHL
    LNGJUMPC _atoi16_number_end

    ; Do the above again, but checking to make sure it is <= "9"
    LOADI -58
    ADD
    SHL

    ; See if it is negative (meaning we are between "0" and "9" inclusive).
    LNGJUMPNC _atoi16_number_end

    ; We know the digit is between "0" and "9" inclusive, so let's multiply our
    ; current accumulated result and add the digit value in. But first, save the
    ; current value as an integer to A so we don't have to move around to get it again.
    LOADI -48
    ADD
    MOV A, V

    ; Swap back to our stack, which should point at the temporary number.
    SWAP PC, SPC

    ; It's worth juggling the umult param order here since umult uses a looping multiply.
    LOAD A
    SUBPCI 2
    STORE A
    ADDPCI 3
    LOAD A
    SUBPCI 2
    STORE A
    INCPC
    STOREI 0
    INCPC
    STOREI 10
    SUBPCI 3

    ; Multiply by 10, getting the result in our temporary location.
    CALL umult16

    ; Add lower 8 bits together.
    MOV V, A
    INCPC
    ADD
    STORE A
    DECPC

    ; Don't bother doing next three instructions if carry unset, as an optimization.
    JRINC _atoi16_skip_add

    ; Add higher 8 bits together.
    LOADI 0
    ADC
    STORE A
_atoi16_skip_add:
    SWAP PC, SPC

    ; Do it again!
    INCPC
    LNGJUMP _atoi16_number_loop

_atoi16_number_end:
    ; The stack now points at the end of the string, whether that's a null byte
    ; or the beginning of a non-integer. Save it back so the calling function
    ; can implement things like sscanf().
    SWAP PC, SPC
    ADDPCI 13
    PUSH SPC

    ; See if we need to negate the number.
    MOV U, A
    ADDI 0

    ; Move to the temporary number itself on the stack.
    SUBPCI 11
    JRIZ _atoi16_return_positive

    ; Need to negate it, so do that negation.
    CALL neg16

_atoi16_return_positive:
    ; First, copy the temporary value to its final position in the stack.
    LOAD A
    ADDPCI 9
    STORE A
    SUBPCI 8
    LOAD A
    ADDPCI 9
    STORE A

    ; Restore A/U/SPC registers so we don't clobber them.
    SUBPCI 8
    POP A
    POP V
    POP U
    POP SPC

    ; Finally, return.
    RET


atoi32:
    ; Given a string pointed to on the stack, as long as it represents an
    ; integer either in the range of [-2147483648, 2147483647] or [0, 4294967295],
    ; convert that string to an integer. Skips all leading whitespace, and allows
    ; for an optional preceeding +/- indicator. Stops at the first non-integer
    ; character it finds, returning the integer value on the stack. Note that
    ; the caller is responsible for allocating stack space for the response.
    ;
    ; Note that unlike most of the other functions, this does modify the
    ; pointer to the string on the stack. The pointer will point to the
    ; first non-integer character (or null byte) found, so that atoi can
    ; be used in more complex input scanning. Does not clobber the A/U/V
    ; registers or the SPC.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you have a string buffer at 0x1234, call this similar to:
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     SUBPCI 4
    ;     CALL atoi32
    ;
    ; Stack layout at start:
    ; PC + 0  - temporary converted integer.
    ; PC + 1  - temporary converted integer.
    ; PC + 2  - temporary converted integer.
    ; PC + 3  - temporary converted integer.
    ; PC + 4  - Saved A.
    ; PC + 5  - Saved V.
    ; PC + 6  - Saved U.
    ; PC + 7  - Saved SPC.
    ; PC + 8  - Saved SPC.
    ; PC + 9  - return address.
    ; PC + 10 - return address.
    ; PC + 11 - final converted integer.
    ; PC + 12 - final converted integer.
    ; PC + 13 - final converted integer.
    ; PC + 14 - final converted integer.
    ; PC + 15 - pointer to string (will be updated).
    ; PC + 16 - pointer to string (will be updated).

    ; First, save the calling function's locals.
    PUSH SPC
    PUSH U
    PUSH V
    PUSH A

    ; Now, assume that the number is positive for now. U will be
    ; the negation indicator.
    ZERO
    MOV A, U

    ; Now, start with the number itself being zero. The stack location
    ; will be the accumulated number.
    PUSH A
    PUSH A
    PUSH A
    PUSH A

    ; Advance the stack pointer back to the pointer to the string.
    ADDPCI 15
    POP SPC
    SUBPCI 17
    SWAP PC, SPC

_atoi32_skip_whitespace:
    ; See if the character is a space.
    LOADI " "

    ; XOR the byte in the string against the space to check if they equal.
    XOR
    JRIZ _atoi32_skip_ws_inc

    ; See if the character is a tab.
    LOADI "\t"
    XOR
    JRIZ _atoi32_skip_ws_inc

    ; It is none of the characters we want to skip.
    JRI _atoi32_check_positive

_atoi32_skip_ws_inc:
    ; Increment our string pointer to skip the character.
    INCPC

    ; Do it again!
    jri _atoi32_skip_whitespace

_atoi32_check_positive:
    ; Compare current pointed to byte against a "+"
    LOADI "+"
    XOR
    JRIZ _atoi32_skip_plus_inc

    ; Check for a - sign, consume it if found.
    LOADI "-"
    XOR
    JRINZ _atoi32_number_loop

    ; Remember that this was negative.
    LOADI 1
    MOV A, U

_atoi32_skip_plus_inc:
    ; Increment our string pointer to skip the character.
    INCPC

    ; Now, start consuming digit characters and adding them to our accumulator.
_atoi32_number_loop:
    ; Load with negative value of ascii "0", to subtract it from the number on the stack.
    LOADI -48

    ; Perform the math (ascii digit) - "0"
    ADD

    ; See if it is negative (meaning a value < "0")
    SHL
    LNGJUMPC _atoi32_number_end

    ; Do the above again, but checking to make sure it is <= "9"
    LOADI -58
    ADD
    SHL

    ; See if it is negative (meaning we are between "0" and "9" inclusive).
    LNGJUMPNC _atoi32_number_end

    ; We know the digit is between "0" and "9" inclusive, so let's multiply our
    ; current accumulated result and add the digit value in. But first, save the
    ; current value as an integer to A so we don't have to move around to get it again.
    LOADI -48
    ADD
    MOV A, V

    ; Swap back to our stack, which should point at the temporary number.
    SWAP PC, SPC

    ; It's worth juggling the umult param order here since umult uses a looping multiply.
    LOAD A
    SUBPCI 4
    STORE A
    ADDPCI 5
    LOAD A
    SUBPCI 4
    STORE A
    ADDPCI 5
    LOAD A
    SUBPCI 4
    STORE A
    ADDPCI 5
    LOAD A
    SUBPCI 4
    STORE A

    INCPC
    STOREI 0
    INCPC
    STOREI 0
    INCPC
    STOREI 0
    INCPC
    STOREI 10
    SUBPCI 7

    ; Multiply by 10, getting the result in our temporary location.
    CALL umult32

    ; Add lower 8 bits together.
    MOV V, A
    ADDPCI 3
    ADD
    STORE A

    JRIC _atoi32_add_2
    SUBPCI 3
    JRI _atoi32_skip_add

_atoi32_add_2:
    ; Add next 8 bits together.
    DECPC
    LOADI 0
    ADC
    STORE A

    JRIC _atoi32_add_3
    SUBPCI 2
    JRI _atoi32_skip_add

_atoi32_add_3:
    ; Add next 8 bits together.
    DECPC
    LOADI 0
    ADC
    STORE A
    DECPC

    ; Don't bother doing next three instructions if carry unset, as an optimization.
    JRINC _atoi32_skip_add

    ; Add high 8 bits together.
    LOADI 0
    ADC
    STORE A

_atoi32_skip_add:
    ; Swap back now that we've added.
    SWAP PC, SPC

    ; Do it again!
    INCPC
    LNGJUMP _atoi32_number_loop

_atoi32_number_end:
    ; The stack now points at the end of the string, whether that's a null byte
    ; or the beginning of a non-integer. Save it back so the calling function
    ; can implement things like sscanf().
    SWAP PC, SPC
    ADDPCI 17
    PUSH SPC

    ; See if we need to negate the number.
    MOV U, A
    ADDI 0

    ; Move to the temporary number itself on the stack.
    SUBPCI 15
    JRIZ _atoi32_return_positive

    ; Need to negate it, so do that negation.
    CALL neg32

_atoi32_return_positive:
    ; First, copy the temporary value to its final position in the stack.
    LOAD A
    ADDPCI 11
    STORE A
    SUBPCI 10
    LOAD A
    ADDPCI 11
    STORE A
    SUBPCI 10
    LOAD A
    ADDPCI 11
    STORE A
    SUBPCI 10
    LOAD A
    ADDPCI 11
    STORE A
    SUBPCI 10

    ; Restore A/U/SPC registers so we don't clobber them.
    POP A
    POP V
    POP U
    POP SPC

    ; Finally, return.
    RET
