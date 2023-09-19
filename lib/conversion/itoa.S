itoa:
    ; Given an integer on the stack and a pointer on the stack to output a
    ; string to, converts the value in the A register to a decimal string.
    ; Works on signed 8 bit integers only. Does not clobber the A/U/V register
    ; or the string pointer input.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you have a string buffer at 0x1234, and want to convert the integer
    ; 123 to a string, call this similar to:
    ;   PUSHI 0x34
    ;   PUSHI 0x12
    ;   LOADI 123
    ;   CALL itoa
    ;
    ; Stack layout at call and return time
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - pointer to string
    ; PC + 3 - pointer to string
    ;
    ; Stack layout during execution.
    ; PC + 0  - Remainder of last division.
    ; PC + 1  - stored A temporary value (absolute).
    ; PC + 2  - Whether the A value is negative or not (1 for negative, 0 for positive).
    ; PC + 3  - Safe buffer area for temporary output.
    ; PC + 4  - Safe buffer area for temporary output.
    ; PC + 5  - Safe buffer area for temporary output.
    ; PC + 6  - Safe buffer area for temporary output.
    ; PC + 7  - Safe buffer area for temporary output.
    ; PC + 8  - Saved P to safe buffer area.
    ; PC + 9  - Saved C to safe buffer area.
    ; PC + 10 - Saved SP
    ; PC + 11 - Saved SC
    ; PC + 12 - Original U register value.
    ; PC + 13 - Original A register value.
    ; PC + 14 - return address
    ; PC + 15 - return address
    ; PC + 16 - pointer to string
    ; PC + 17 - pointer to string
    ; PC + 18 - integer to save

    ; Save the A register.
    PUSH A

    ; Save the U register.
    PUSH U

    ; Now, save the calling function's local stack.
    PUSH SPC

    ; Initialize the output length (starts with 1, due to always having a null).
    LOADI 1
    MOV A, U

    ; Save a few spaces for our temporary storage, get the
    ; address of our current stack position. We pre-fill
    ; a null byte in the first position.
    SUBPCI 3
    STOREI 0

    ; Do the actual dance to copy our PC pointer to SPC.
    MOV P, A
    SWAP PC, SPC
    MOV A, P
    SWAP PC, SPC
    MOV C, A
    SWAP PC, SPC
    MOV A, C
    SWAP PC, SPC

    ; SPC = PC now, save that address.
    ADDPCI 3
    PUSH SPC

    ; Retrieve the original A value, skip past our buffer.
    ADDPCI 10
    LOAD A
    SUBPCI 16

    ; Assume the integer is positive.
    PUSH A

    ; Now, figure out if A is negative.
    SHL
    JRIC _itoa_neg

    ; Its already positive, we don't need to fix anything.
    INCPC
    STOREI 0
    DECPC

    JRI _itoa_loop

_itoa_neg:
    ; Negate it
    LOAD A
    NEG
    STORE A

    ; Store that it is negative
    INCPC
    STOREI 1
    DECPC

    ; Also, update our output characters to reflect a negative sign.
    LOADI 2
    MOV A, U

_itoa_loop:
    ; Divide A by 10
    PUSHI 10
    CALL udiv

    ; Now, load the zero character constant so we can change the
    ; raw integer value to a character.
    LOADI "0"

    ; Update the remainder to be a character.
    ADD

    ; Now, grab where we're going to output this from the stack.
    ADDPCI 8
    POP SPC
    SWAP PC, SPC
    PUSH A
    SWAP PC, SPC
    PUSH SPC

    ; Count how many output bytes so we can rewind the pointer.
    MOV U, A
    INC
    MOV A, U

    ; Now, see if we're finished (the quotient is zero).
    SUBPCI 7
    LOAD A
    ADDI 0
    JRIZ _itoa_negative_check

    ; We got more work to do
    JRI _itoa_loop

_itoa_negative_check:
    ; See if the number was negative.
    INCPC
    LOAD A
    ADDPCI 6
    ADDI 0
    JRIZ _itoa_copy

    ; It is negative, output a '-' sign.
    LOADI "-"

    ; We already advanced to our output buffer location above.
    POP SPC
    SWAP PC, SPC
    PUSH A
    SWAP PC, SPC
    PUSH SPC

_itoa_copy:
    ; Now, copy bytes one at a time to the output buffer. We
    ; output backwards in this routine because we do the low
    ; digits first, so we can now copy until we hit the null
    ; byte and the integer will be forward.
    POP SPC
    SWAP PC, SPC
    POP A
    SWAP PC, SPC
    PUSH SPC

    ADDPCI 8
    POP SPC
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 8

    ; See if we copied a null
    ADDI 0
    JRINZ _itoa_copy

_itoa_done:
    ; Now, restore the pointer on the stack, by loading how many
    ; bytes we output and advancing backwards that much.
    ADDPCI 8
    POP SPC
    MOV U, A
    SWAP PC, SPC
    NEG
    ADDPC
    SWAP PC, SPC
    PUSH SPC

    ; Finally, we need to restore the clobbered registers and stack and return.
    SUBPCI 6
    POP SPC
    POP U
    POP A
    RET


itoa16:
    ; Given an integer on the stack and a pointer on the stack to output
    ; a string to, converts the value on the stack to a decimal string.
    ; Works on signed 16 bit integers only. Does not clobber the A/U/V
    ; register or the string pointer input.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you have a string buffer at 0x1234, and want to convert the integer
    ; 12345 to a string, call this similar to:
    ;   PUSHI 0x39
    ;   PUSHI 0x30
    ;   PUSHI 0x34
    ;   PUSHI 0x12
    ;   CALL itoa16
    ;
    ; Stack layout at call and return time
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - pointer to string
    ; PC + 3 - pointer to string
    ; PC + 4 - integer high byte
    ; PC + 5 - integer low byte
    ;
    ; Stack layout during execution
    ; PC + 0  - last remainder high byte.
    ; PC + 1  - last remainder low byte.
    ; PC + 2  - stored integer temporary value high byte (absolute).
    ; PC + 3  - stored integer temporary value low byte (absolute).
    ; PC + 4  - Whether the integer is negative or not (1 for negative, 0 for positive).
    ; PC + 5  - Safe buffer area for temporary output.
    ; PC + 6  - Safe buffer area for temporary output.
    ; PC + 7  - Safe buffer area for temporary output.
    ; PC + 8  - Safe buffer area for temporary output.
    ; PC + 9  - Safe buffer area for temporary output.
    ; PC + 10 - Safe buffer area for temporary output.
    ; PC + 11 - Safe buffer area for temporary output.
    ; PC + 12 - Saved P to safe buffer area.
    ; PC + 13 - Saved C to safe buffer area.
    ; PC + 14 - Saved SP
    ; PC + 15 - Saved SC
    ; PC + 16 - Original U register value.
    ; PC + 17 - Original A register value.
    ; PC + 18 - return address
    ; PC + 19 - return address
    ; PC + 20 - pointer to string
    ; PC + 21 - pointer to string
    ; PC + 22 - integer high byte
    ; PC + 23 - integer low byte

    ; Save the A/U register.
    PUSH A
    PUSH U

    ; Save the calling function's local stack.
    PUSH SPC

    ; Initialize the output length (starts with 1, due to always having a null).
    LOADI 1
    MOV A, U

    ; Save a few spaces for our temporary storage, get the
    ; address of our current stack position. We pre-fill
    ; a null byte in the first position.
    SUBPCI 3
    STOREI 0

    ; Do the actual dance to copy our PC pointer to SPC.
    MOV P, A
    SWAP PC, SPC
    MOV A, P
    SWAP PC, SPC
    MOV C, A
    SWAP PC, SPC
    MOV A, C
    SWAP PC, SPC

    ; SPC = PC now, save that address.
    ADDPCI 3
    PUSH SPC

    ; Copy the integer over to the temporary location where we can safely negate it.
    ADDPCI 11
    LOAD A
    SUBPCI 20
    STORE A
    ADDPCI 19
    LOAD A
    SUBPCI 20
    STORE A

    ; Figure out whether the integer is negative or not. We copied low byte first and
    ; high byte second so we could simply look at the top bit of the top byte here.
    SHL
    JRIC _itoa16_neg

    ; Its already positive, we don't need to fix anything.
    ADDPCI 2
    STOREI 0
    SUBPCI 2

    JRI _itoa16_loop

_itoa16_neg:
    ; Negate it
    CALL neg16

    ; Store that it is negative
    ADDPCI 2
    STOREI 1
    SUBPCI 2

    ; Also, update our output characters to reflect a negative sign.
    LOADI 2
    MOV A, U

_itoa16_loop:
    ; Divide A by 10
    PUSHI 10
    PUSHI 0
    CALL udiv16

    ; Quotient is in the location where we store our temp value, remainder is above that.
    ; Remainder will only ever be [0,9] due to division working, you know, as intended.
    ; Skip past the always-zero high byte.
    INCPC

    ; Now, load the zero character constant so we can change the
    ; raw integer value to a character.
    LOADI "0"

    ; Update the remainder to be a character.
    ADD

    ; Now, grab where we're going to output this from the stack.
    ADDPCI 11
    POP SPC
    SWAP PC, SPC
    PUSH A
    SWAP PC, SPC
    PUSH SPC

    ; Count how many output bytes so we can rewind the pointer.
    MOV U, A
    INC
    MOV A, U

    ; Now, see if we're finished (the quotient is zero).
    SUBPCI 9
    LOAD A
    ADDI 0
    DECPC
    JRINZ _itoa16_loop

    LOAD A
    ADDI 0
    JRIZ _itoa16_negative_check

    ; We got more work to do
    LNGJUMP _itoa16_loop

_itoa16_negative_check:
    ; See if the number was negative.
    ADDPCI 2
    LOAD A
    ADDPCI 8
    ADDI 0
    JRIZ _itoa16_copy

    ; It is negative, output a '-' sign.
    LOADI "-"

    ; We already advanced to our output buffer location above.
    POP SPC
    SWAP PC, SPC
    PUSH A
    SWAP PC, SPC
    PUSH SPC

_itoa16_copy:
    ; Now, copy bytes one at a time to the output buffer. We
    ; output backwards in this routine because we do the low
    ; digits first, so we can now copy until we hit the null
    ; byte and the integer will be forward.
    POP SPC
    SWAP PC, SPC
    POP A
    SWAP PC, SPC
    PUSH SPC

    ADDPCI 8
    POP SPC
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 8

    ; See if we copied a null
    ADDI 0
    JRINZ _itoa16_copy

_itoa16_done:
    ; Now, restore the pointer on the stack, by loading how many
    ; bytes we output and advancing backwards that much.
    ADDPCI 8
    POP SPC
    MOV U, A
    SWAP PC, SPC
    NEG
    ADDPC
    SWAP PC, SPC
    PUSH SPC

    ; Finally, we need to restore the clobbered registers and stack and return.
    SUBPCI 6
    POP SPC
    POP U
    POP A
    RET


itoa32:
    ; Given an integer on the stack and a pointer on the stack to output
    ; a string to, converts the value on the stack to a decimal string.
    ; Works on signed 32 bit integers only. Does not clobber the A/U/V
    ; register or the string pointer input.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you have a string buffer at 0x1234, and want to convert the integer
    ; 123456789 to a string, call this similar to:
    ;   PUSHI 0x15
    ;   PUSHI 0xCD
    ;   PUSHI 0x5B
    ;   PUSHI 0x07
    ;   PUSHI 0x34
    ;   PUSHI 0x12
    ;   CALL itoa32
    ;
    ; Stack layout at call and return time
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - pointer to string
    ; PC + 3 - pointer to string
    ; PC + 4 - integer high byte
    ; PC + 5 - integer third byte
    ; PC + 6 - integer second byte
    ; PC + 7 - integer low byte
    ;
    ; Stack layout during execution.
    ; PC + 0  - last remainder high byte.
    ; PC + 1  - last remainder third byte.
    ; PC + 2  - last remainder second byte.
    ; PC + 3  - last remainder low byte.
    ; PC + 4  - stored integer temporary value high byte (absolute).
    ; PC + 5  - stored integer temporary value third (absolute).
    ; PC + 6  - stored integer temporary value second (absolute).
    ; PC + 7  - stored integer temporary value low byte (absolute).
    ; PC + 8  - Whether the integer is negative or not (1 for negative, 0 for positive).
    ; PC + 9  - Safe buffer area for temporary output.
    ; PC + 10 - Safe buffer area for temporary output.
    ; PC + 11 - Safe buffer area for temporary output.
    ; PC + 12 - Safe buffer area for temporary output.
    ; PC + 13 - Safe buffer area for temporary output.
    ; PC + 14 - Safe buffer area for temporary output.
    ; PC + 15 - Safe buffer area for temporary output.
    ; PC + 16 - Safe buffer area for temporary output.
    ; PC + 17 - Safe buffer area for temporary output.
    ; PC + 18 - Safe buffer area for temporary output.
    ; PC + 19 - Safe buffer area for temporary output.
    ; PC + 20 - Safe buffer area for temporary output.
    ; PC + 21 - Saved P to safe buffer area.
    ; PC + 22 - Saved C to safe buffer area.
    ; PC + 23 - Saved SP
    ; PC + 24 - Saved SC
    ; PC + 25 - Original U register value.
    ; PC + 26 - Original A register value.
    ; PC + 27 - return address
    ; PC + 28 - return address
    ; PC + 29 - pointer to string
    ; PC + 30 - pointer to string
    ; PC + 31 - integer high byte
    ; PC + 32 - integer third byte
    ; PC + 33 - integer second byte
    ; PC + 34 - integer low byte

    ; Save the A/U register.
    PUSH A
    PUSH U

    ; Save the calling function's local stack.
    PUSH SPC

    ; Initialize the output length (starts with 1, due to always having a null).
    LOADI 1
    MOV A, U

    ; Save a few spaces for our temporary storage, get the
    ; address of our current stack position. We pre-fill
    ; a null byte in the first position.
    SUBPCI 3
    STOREI 0

    ; Do the actual dance to copy our PC pointer to SPC.
    MOV P, A
    SWAP PC, SPC
    MOV A, P
    SWAP PC, SPC
    MOV C, A
    SWAP PC, SPC
    MOV A, C
    SWAP PC, SPC

    ; SPC = PC now, save that address.
    ADDPCI 3
    PUSH SPC

    ; Copy the integer over to the temporary location where we can safely negate it.
    ADDPCI 13
    LOAD A
    SUBPCI 27
    STORE A
    ADDPCI 26
    LOAD A
    SUBPCI 27
    STORE A
    ADDPCI 26
    LOAD A
    SUBPCI 27
    STORE A
    ADDPCI 26
    LOAD A
    SUBPCI 27
    STORE A

    ; Figure out whether the integer is negative or not. We copied low byte first and
    ; high byte second so we could simply look at the top bit of the top byte here.
    SHL
    JRIC _itoa32_neg

    ; Its already positive, we don't need to fix anything.
    ADDPCI 4
    STOREI 0
    SUBPCI 4

    JRI _itoa32_loop

_itoa32_neg:
    ; Negate it
    CALL neg32

    ; Store that it is negative
    ADDPCI 4
    STOREI 1
    SUBPCI 4

    ; Also, update our output characters to reflect a negative sign.
    LOADI 2
    MOV A, U

_itoa32_loop:
    ; Divide A by 10
    PUSHI 10
    PUSHI 0
    PUSHI 0
    PUSHI 0
    CALL udiv32

    ; Quotient is in the location where we store our temp value, remainder is above that.
    ; Remainder will only ever be [0,9] due to division working, you know, as intended.
    ; Skip past the always-zero high byte.
    ADDPCI 3

    ; Now, load the zero character constant so we can change the
    ; raw integer value to a character.
    LOADI "0"

    ; Update the remainder to be a character.
    ADD

    ; Now, grab where we're going to output this from the stack.
    ADDPCI 18
    POP SPC
    SWAP PC, SPC
    PUSH A
    SWAP PC, SPC
    PUSH SPC

    ; Count how many output bytes so we can rewind the pointer.
    MOV U, A
    INC
    MOV A, U

    ; Now, see if we're finished (the quotient is zero).
    SUBPCI 14
    LOAD A
    ADDI 0
    JRIZ _itoa32_check_second_zero

    ; Not zero, have work to do.
    SUBPCI 3
    LNGJUMP _itoa32_loop

_itoa32_check_second_zero:
    DECPC
    LOAD A
    ADDI 0
    JRIZ _itoa32_check_third_zero

    ; Not zero, have work to do.
    SUBPCI 2
    LNGJUMP _itoa32_loop

_itoa32_check_third_zero:
    DECPC
    LOAD A
    ADDI 0
    DECPC

    ; Not zero, have work to do.
    LNGJUMPNZ _itoa32_loop

_itoa32_check_fourth_zero:
    LOAD A
    ADDI 0
    JRIZ _itoa32_negative_check

    ; We got more work to do
    LNGJUMP _itoa32_loop

_itoa32_negative_check:
    ; See if the number was negative.
    ADDPCI 4
    LOAD A
    ADDPCI 13
    ADDI 0
    JRIZ _itoa32_copy

    ; It is negative, output a '-' sign.
    LOADI "-"

    ; We already advanced to our output buffer location above.
    POP SPC
    SWAP PC, SPC
    PUSH A
    SWAP PC, SPC
    PUSH SPC

_itoa32_copy:
    ; Now, copy bytes one at a time to the output buffer. We
    ; output backwards in this routine because we do the low
    ; digits first, so we can now copy until we hit the null
    ; byte and the integer will be forward.
    POP SPC
    SWAP PC, SPC
    POP A
    SWAP PC, SPC
    PUSH SPC

    ADDPCI 8
    POP SPC
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 8

    ; See if we copied a null
    ADDI 0
    JRINZ _itoa32_copy

_itoa32_done:
    ; Now, restore the pointer on the stack, by loading how many
    ; bytes we output and advancing backwards that much.
    ADDPCI 8
    POP SPC
    MOV U, A
    SWAP PC, SPC
    NEG
    ADDPC
    SWAP PC, SPC
    PUSH SPC

    ; Finally, we need to restore the clobbered registers and stack and return.
    SUBPCI 6
    POP SPC
    POP U
    POP A
    RET
