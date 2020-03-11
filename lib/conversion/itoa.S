_itoa_locals:
    .char "0"
    .char "-"

itoa:
    ; Given an integer in the A register and a pointer on the stack
    ; to output a string to, converts the value in the A register to
    ; a string. Works on signed 8 bit integers only. Does not change
    ; the A register or the string pointer input.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you have a string buffer at 0x1234, call this similar to:
    ;   PUSHI 0x34
    ;   PUSHI 0x12
    ;   SETA 123
    ;   CALL itoa
    ;
    ; Stack layout
    ; PC + ? - stored A temporary value (absolute).
    ; PC + ? - Remainder of last division.
    ; PC + ? - Whether the A value is negative or not (1 for negative, 0 for positive).
    ; PC + ? - Safe buffer area for temporary output.
    ; PC + ? - Safe buffer area for temporary output.
    ; PC + ? - Safe buffer area for temporary output.
    ; PC + ? - Safe buffer area for temporary output.
    ; PC + ? - Safe buffer area for temporary output.
    ; PC + ? - Saved P to safe buffer area.
    ; PC + ? - Saved C to safe buffer area.
    ; PC + ? - Saved SP
    ; PC + ? - Saved SC
    ; PC + ? - Length of output.
    ; PC + ? - Original A register value.
    ; PC + ? - return address
    ; PC + ? - return address
    ; PC + ? - pointer to string
    ; PC + ? - pointer to string

    ; Save the A register.
    PUSH

    ; Save the output length (starts with 1, due to always having a null).
    PUSHI 1

    ; Now, save the calling function's local stack.
    PUSHSPC

    ; Save a few spaces for our temporary storage, get the
    ; address of our current stack position. We pre-fill
    ; a null byte in the first position.
    SUBPCI 2
    PUSHI 0

    ; Do the actual dance to copy our PC pointer to SPC.
    PTOA
    SWAP
    ATOP
    SWAP
    CTOA
    SWAP
    ATOC
    SWAP

    ; SPC = PC now, save that address.
    ADDPCI 3
    PUSHSPC

    ; Retrieve the original A value, skip past our buffer.
    ADDPCI 5
    LOAD
    SUBPCI 8
    SUBPCI 4

    ; Assume the integer is positive.
    PUSH

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
    POP
    NEG
    PUSH

    ; Store that it is negative
    ADDPCI 2
    STOREI 1

    ; Also, update our output characters to reflect a negative sign.
    ADDPCI 8
    ADDPCI 2
    STOREI 2

    SUBPCI 8
    SUBPCI 4

_itoa_loop:
    ; Divide A by 10
    INCPC
    STOREI 10
    DECPC
    CALL udiv

    ; Quotient is in A, remainder is on stack. Save the quotient.
    PUSH
    INCPC

    ; Now, load the zero character constant so we can change the
    ; raw integer value to a character.
    SWAP
    SETPC _itoa_locals
    LOAD
    SWAP

    ; Update the remainder to be a character.
    ADD
    STORE

    ; Now, grab where we're going to output this from the stack.
    ADDPCI 7
    POPSPC
    SWAP
    PUSH
    SWAP
    PUSHSPC

    ; Count how many output bytes so we can rewind the pointer.
    ADDPCI 4
    LOAD
    INC
    STORE
    SUBPCI 4

    ; Now, see if we're finished (the quotient is zero).
    SUBPCI 8
    LOAD
    ADDI 0
    JRIZ _itoa_negative_check

    ; We got more work to do
    LNGJUMP _itoa_loop

_itoa_negative_check:
    ; See if the number was negative.
    ADDPCI 2
    LOAD
    ADDPCI 6
    ADDI 0
    JRIZ _itoa_copy

    ; It is negative, output a '-' sign.
    SWAP
    SETPC _itoa_locals
    INCPC
    LOAD
    SWAP

    ; We already advanced to our output buffer location above.
    POPSPC
    SWAP
    PUSH
    SWAP
    PUSHSPC

_itoa_copy:
    ; Now, copy bytes one at a time to the output buffer. We
    ; output backwards in this routine because we do the low
    ; digits first, so we can now copy until we hit the null
    ; byte and the integer will be forward.
    POPSPC
    SWAP
    POP
    SWAP
    PUSHSPC

    ADDPCI 8
    POPSPC
    SWAP
    STORE
    INCPC
    SWAP
    PUSHSPC
    SUBPCI 8

    ; See if we copied a null
    ADDI 0
    JRINZ _itoa_copy

_itoa_done:
    ; Now, restore the pointer on the stack, by loading how many
    ; bytes we output and advancing backwards that much.
    ADDPCI 8
    POPSPC
    SUBPCI 6
    LOAD
    ADDPCI 6
    SWAP
    NEG
    ADDPC
    SWAP
    PUSHSPC

    ; Finally, we need to restore the A register and stack and return.
    SUBPCI 3
    POP
    RET
