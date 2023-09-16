itoa:
    ; Given an integer in the A register and a pointer on the stack
    ; to output a string to, converts the value in the A register to
    ; a string. Works on signed 8 bit integers only. Does not clobber
    ; the A/U/V register or the string pointer input.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you have a string buffer at 0x1234, call this similar to:
    ;   PUSHI 0x34
    ;   PUSHI 0x12
    ;   LOADI 123
    ;   CALL itoa
    ;
    ; Stack layout
    ; PC + 0  - stored A temporary value (absolute).
    ; PC + 1  - Remainder of last division.
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

    ; Save the A register.
    PUSH A

    ; Save the U register.
    PUSH U

    ; Initialize the output length (starts with 1, due to always having a null).
    LOADI 1
    MOV A, U

    ; Now, save the calling function's local stack.
    PUSH SPC

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
    ADDPCI 5
    LOAD A
    SUBPCI 12

    ; Assume the integer is positive.
    PUSH A

    ; Now, figure out if A is negative.
    SHL
    JRIC _itoa_neg

    ; Its already positive, we don't need to fix anything.
    ADDPCI 2
    STOREI 0
    SUBPCI 2

    JRI _itoa_loop

_itoa_neg:
    ; Negate it
    LOAD A
    NEG
    STORE A

    ; Store that it is negative
    ADDPCI 2
    STOREI 1
    SUBPCI 2

    ; Also, update our output characters to reflect a negative sign.
    LOADI 2
    MOV A, U

_itoa_loop:
    ; Divide A by 10
    INCPC
    STOREI 10
    DECPC
    CALL udiv

    ; Quotient is in A, remainder is on stack. Save the quotient.
    PUSH A
    INCPC

    ; Now, load the zero character constant so we can change the
    ; raw integer value to a character.
    LOADI "0"

    ; Update the remainder to be a character.
    ADD

    ; Now, grab where we're going to output this from the stack.
    ADDPCI 7
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
    SUBPCI 8
    LOAD A
    ADDI 0
    JRIZ _itoa_negative_check

    ; We got more work to do
    JRI _itoa_loop

_itoa_negative_check:
    ; See if the number was negative.
    ADDPCI 2
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

    ; Finally, we need to restore the A register and stack and return.
    SUBPCI 3
    POP A
    RET
