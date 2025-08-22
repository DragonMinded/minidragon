_hex_chars:
    ; Characters used to convert a nibble to hexadecimal.
    .char '0'
    .char '1'
    .char '2'
    .char '3'
    .char '4'
    .char '5'
    .char '6'
    .char '7'
    .char '8'
    .char '9'
    .char 'A'
    .char 'B'
    .char 'C'
    .char 'D'
    .char 'E'
    .char 'F'

itohex8:
    ; Given an integer in the A register and a pointer on the stack to output a
    ; string to, converts the value in the A register to a hexadecimal string.
    ; Works on unsigned or signed 8 bit integers only. Does not clobber the
    ; A/U/V register or the string pointer input.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you have a string buffer at 0x1234, and want to convert the integer
    ; 123 to a hexadecimal string, call this similar to:
    ;   PUSHI 0x34
    ;   PUSHI 0x12
    ;   LOADI 123
    ;   CALL itohex8
    ;
    ; Stack layout at call and return time.
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - pointer to string
    ; PC + 3 - pointer to string
    ;
    ; Stack layout during execution.
    ; PC + 0  - Temporary storage for string output.
    ; PC + 1  - Temporary storage for string output.
    ; PC + 2  - Saved SP
    ; PC + 3  - Saved SC
    ; PC + 4  - Original V register value.
    ; PC + 5  - Original U register value.
    ; PC + 6  - Original A register value.
    ; PC + 7  - return address
    ; PC + 8  - return address
    ; PC + 9  - pointer to string
    ; PC + 10 - pointer to string

    ; Save the A register.
    PUSH A

    ; Save the U register.
    PUSH U
    PUSH V

    ; Now, save the calling function's local stack.
    PUSH SPC

    ; Save the A value in the U register, start outputting.
    MOV A, U

    SWAP PC, SPC
    SETPC _hex_chars
    SWAP PC, SPC

    ; First digit
    MOV U, A
    SHR
    SHR
    SHR
    SHR

    SWAP PC, SPC
    ADDPC
    LOAD V
    NEG
    ADDPC
    SWAP PC, SPC

    PUSH V

    ; Second digit
    LOADI 0x0F
    ANDU

    SWAP PC, SPC
    ADDPC
    LOAD V
    SWAP PC, SPC

    PUSH V

    ; Gotta copy to the output string.
    ADDPCI 9
    POP SPC
    SUBPCI 10

    ; Copy the 0x to the destination.
    SWAP PC, SPC
    LOADI '0'
    STORE A
    INCPC
    LOADI 'x'
    STORE A
    INCPC
    SWAP PC, SPC

    ; Third of four copied.
    LOAD A
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC

    ; Fourth of four copied.
    DECPC
    LOAD A
    SWAP PC, SPC
    STORE A
    INCPC

    ; Null copied.
    LOADI 0
    STORE A
    SWAP PC, SPC

    ; Now, restore the stack.
    ADDPCI 2

    POP SPC
    POP V
    POP U
    POP A

    RET

itohex16:
    ; Given an integer on the stack and a pointer on the stack to output a string
    ; to, converts the value on the stack to a hexadecimal string. Works on unsigned
    ; or signed 16 bit integers only. Does not clobber the A/U/V register or the
    ; string pointer input.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you have a string buffer at 0x1234, and want to convert the integer
    ; 12345 to a hexadecimal string, call this similar to:
    ;   PUSHI 0x39
    ;   PUSHI 0x30
    ;   PUSHI 0x34
    ;   PUSHI 0x12
    ;   CALL itohex16
    ;
    ; Stack layout at call and return time.
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - pointer to string
    ; PC + 3 - pointer to string
    ; PC + 4 - integer high byte
    ; PC + 5 - integer low byte
    ;
    ; Stack layout during execution.
    ; PC + 0  - Temporary storage for string output.
    ; PC + 1  - Temporary storage for string output.
    ; PC + 2  - Temporary storage for string output.
    ; PC + 3  - Temporary storage for string output.
    ; PC + 4  - Saved SP
    ; PC + 5  - Saved SC
    ; PC + 6  - Original V register value.
    ; PC + 7  - Original U register value.
    ; PC + 8  - Original A register value.
    ; PC + 9  - return address
    ; PC + 10 - return address
    ; PC + 11 - pointer to string
    ; PC + 12 - pointer to string
    ; PC + 13 - integer high byte
    ; PC + 14 - integer low byte

    ; Save the A register.
    PUSH A

    ; Save the U register.
    PUSH U
    PUSH V

    ; Now, save the calling function's local stack.
    PUSH SPC

    SWAP PC, SPC
    SETPC _hex_chars
    SWAP PC, SPC

    ; First byte
    ADDPCI 9
    LOAD U
    SUBPCI 9

    ; First digit
    MOV U, A
    SHR
    SHR
    SHR
    SHR

    SWAP PC, SPC
    ADDPC
    LOAD V
    NEG
    ADDPC
    SWAP PC, SPC

    PUSH V

    ; Second digit
    LOADI 0x0F
    ANDU

    SWAP PC, SPC
    ADDPC
    LOAD V
    NEG
    ADDPC
    SWAP PC, SPC

    PUSH V

    ; Second byte
    ADDPCI 12
    LOAD U
    SUBPCI 12

    ; First digit
    MOV U, A
    SHR
    SHR
    SHR
    SHR

    SWAP PC, SPC
    ADDPC
    LOAD V
    NEG
    ADDPC
    SWAP PC, SPC

    PUSH V

    ; Second digit
    LOADI 0x0F
    ANDU

    SWAP PC, SPC
    ADDPC
    LOAD V
    SWAP PC, SPC

    PUSH V

    ; Gotta copy to the output string.
    ADDPCI 11
    POP SPC
    SUBPCI 10

    ; Copy the 0x to the destination.
    SWAP PC, SPC
    LOADI '0'
    STORE A
    INCPC
    LOADI 'x'
    STORE A
    INCPC
    SWAP PC, SPC

    ; Third of six copied.
    LOAD A
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC

    ; Fourth of six copied.
    DECPC
    LOAD A
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC

    ; Fifth of six copied.
    DECPC
    LOAD A
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC

    ; Sixth of six copied.
    DECPC
    LOAD A
    SWAP PC, SPC
    STORE A
    INCPC

    ; Null copied.
    LOADI 0
    STORE A
    SWAP PC, SPC

    ; Now, restore the stack.
    ADDPCI 4

    POP SPC
    POP V
    POP U
    POP A

    RET

itohex32:
    ; Given an integer on the stack and a pointer on the stack to output a string
    ; to, converts the value on the stack to a hexadecimal string. Works on unsigned
    ; or signed 32 bit integers only. Does not clobber the A/U/V register or the
    ; string pointer input.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you have a string buffer at 0x1234, and want to convert the integer
    ; 123456789 to a hexadecimal string, call this similar to:
    ;   PUSHI 0x15
    ;   PUSHI 0xCD
    ;   PUSHI 0x5B
    ;   PUSHI 0x07
    ;   PUSHI 0x34
    ;   PUSHI 0x12
    ;   CALL itohex32
    ;
    ; Stack layout at call and return time.
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
    ; PC + 0  - Temporary storage for string output.
    ; PC + 1  - Temporary storage for string output.
    ; PC + 2  - Temporary storage for string output.
    ; PC + 3  - Temporary storage for string output.
    ; PC + 4  - Temporary storage for string output.
    ; PC + 5  - Temporary storage for string output.
    ; PC + 6  - Temporary storage for string output.
    ; PC + 7  - Temporary storage for string output.
    ; PC + 8  - Saved SP
    ; PC + 9  - Saved SC
    ; PC + 10 - Original V register value.
    ; PC + 11 - Original U register value.
    ; PC + 12 - Original A register value.
    ; PC + 13 - return address
    ; PC + 14 - return address
    ; PC + 15 - pointer to string
    ; PC + 16 - pointer to string
    ; PC + 17 - integer high byte
    ; PC + 18 - integer third byte
    ; PC + 19 - integer second byte
    ; PC + 20 - integer low byte

    ; Save the A register.
    PUSH A

    ; Save the U register.
    PUSH U
    PUSH V

    ; Now, save the calling function's local stack.
    PUSH SPC

    SWAP PC, SPC
    SETPC _hex_chars
    SWAP PC, SPC

    ; First byte
    ADDPCI 9
    LOAD U
    SUBPCI 9

    ; First digit
    MOV U, A
    SHR
    SHR
    SHR
    SHR

    SWAP PC, SPC
    ADDPC
    LOAD V
    NEG
    ADDPC
    SWAP PC, SPC

    PUSH V

    ; Second digit
    LOADI 0x0F
    ANDU

    SWAP PC, SPC
    ADDPC
    LOAD V
    NEG
    ADDPC
    SWAP PC, SPC

    PUSH V

    ; Second byte
    ADDPCI 12
    LOAD U
    SUBPCI 12

    ; First digit
    MOV U, A
    SHR
    SHR
    SHR
    SHR

    SWAP PC, SPC
    ADDPC
    LOAD V
    NEG
    ADDPC
    SWAP PC, SPC

    PUSH V

    ; Second digit
    LOADI 0x0F
    ANDU

    SWAP PC, SPC
    ADDPC
    LOAD V
    NEG
    ADDPC
    SWAP PC, SPC

    PUSH V

    ; Third byte
    ADDPCI 15
    LOAD U
    SUBPCI 15

    ; First digit
    MOV U, A
    SHR
    SHR
    SHR
    SHR

    SWAP PC, SPC
    ADDPC
    LOAD V
    NEG
    ADDPC
    SWAP PC, SPC

    PUSH V

    ; Second digit
    LOADI 0x0F
    ANDU

    SWAP PC, SPC
    ADDPC
    LOAD V
    NEG
    ADDPC
    SWAP PC, SPC

    PUSH V

    ; Fourth byte
    ADDPCI 18
    LOAD U
    SUBPCI 18

    ; First digit
    MOV U, A
    SHR
    SHR
    SHR
    SHR

    SWAP PC, SPC
    ADDPC
    LOAD V
    NEG
    ADDPC
    SWAP PC, SPC

    PUSH V

    ; Second digit
    LOADI 0x0F
    ANDU

    SWAP PC, SPC
    ADDPC
    LOAD V
    SWAP PC, SPC

    PUSH V

    ; Gotta copy to the output string.
    ADDPCI 15
    POP SPC
    SUBPCI 10

    ; Copy the 0x to the destination.
    SWAP PC, SPC
    LOADI '0'
    STORE A
    INCPC
    LOADI 'x'
    STORE A
    INCPC
    SWAP PC, SPC

    ; Third of ten copied.
    LOAD A
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC

    ; Fourth of ten copied.
    DECPC
    LOAD A
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC

    ; Fifth of ten copied.
    DECPC
    LOAD A
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC

    ; Sixth of ten copied.
    DECPC
    LOAD A
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC

    ; Seventh of ten copied.
    DECPC
    LOAD A
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC

    ; Eighth of ten copied.
    DECPC
    LOAD A
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC

    ; Ninth of ten copied.
    DECPC
    LOAD A
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC

    ; Tenth of ten copied.
    DECPC
    LOAD A
    SWAP PC, SPC
    STORE A
    INCPC

    ; Null copied.
    LOADI 0
    STORE A
    SWAP PC, SPC

    ; Now, restore the stack.
    ADDPCI 8

    POP SPC
    POP V
    POP U
    POP A

    RET
