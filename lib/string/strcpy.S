strcpy:
    ; Given a stack holding a source and destination pointer, copy
    ; a null-terminated string from source to destination. Does not
    ; clobber the A/U/V register nor the source/destination pointer on
    ; the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to copy a string from 0x1234 to 0x5678, call like so:
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     CALL strcpy
    ;
    ; Stack layout
    ; PC + 0  - copy of source pointer
    ; PC + 1  - copy of source pointer
    ; PC + 2  - copy of destination pointer
    ; PC + 3  - copy of destination pointer
    ; PC + 4  - saved A register
    ; PC + 5  - saved SP
    ; PC + 6  - saved SC
    ; PC + 7  - return address
    ; PC + 8  - return address
    ; PC + 9  - pointer to source
    ; PC + 10 - pointer to source
    ; PC + 11 - pointer to destination
    ; PC + 12 - pointer to destination

    ; First, save the existing registers
    PUSH SPC
    PUSH A

    ; Now, copy source and destination pointers so we can safely iterate.
    ADDPCI 8
    LOAD A
    SUBPCI 9
    STORE A
    ADDPCI 8
    LOAD A
    SUBPCI 9
    STORE A
    ADDPCI 8
    LOAD A
    SUBPCI 9
    STORE A
    ADDPCI 8
    LOAD A
    SUBPCI 9
    STORE A

_strcpy_loop:
    ; Grab a byte from the source
    POP SPC
    SWAP PC, SPC
    POP A
    SWAP PC, SPC
    PUSH SPC

    ; Store that byte in the destination
    ADDPCI 2
    POP SPC
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 2

    ; See if we copied the null termination
    ADDI 0
    JRINZ _strcpy_loop

    ; Restore the shadow stack and A register
    ADDPCI 4
    POP A
    POP SPC

    ; Now, return to caller
    RET

strncpy:
    ; Given a stack holding a source and destination pointer as well as the maximum
    ; number of characters to copy as a byte, copy a null-terminated string from
    ; source to destination. Always null-terminates. Number of characters to copy
    ; does not include the null termination which is always present. Does not
    ; clobber the A/U/V register nor the source/destination pointer on the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to copy a 5 bytes of a string from 0x1234 to 0x5678, call like so:
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     PUSHI 5
    ;     CALL strncpy
    ;
    ; Stack layout
    ; PC + 0  - copy of source pointer
    ; PC + 1  - copy of source pointer
    ; PC + 2  - copy of destination pointer
    ; PC + 3  - copy of destination pointer
    ; PC + 4  - saved U register
    ; PC + 5  - saved A register
    ; PC + 6  - saved SP
    ; PC + 7  - saved SC
    ; PC + 8  - return address
    ; PC + 9  - return address
    ; PC + 10 - number of characters to copy
    ; PC + 11 - pointer to source
    ; PC + 12 - pointer to source
    ; PC + 13 - pointer to destination
    ; PC + 14 - pointer to destination

    ; First, save the existing registers
    PUSH SPC
    PUSH A
    PUSH U

    ; Copy source and destination pointers so we can iterate safely.
    ADDPCI 10
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 10
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 10
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 10
    LOAD A
    SUBPCI 11
    STORE A

    ; Initialize the count of bytes we copied.
    ZERO

_strncpy_loop:
    ; Figure out if we copied the right number of bytes
    ADDPCI 10
    LOAD U
    SWAP A, U
    XORU
    SWAP A, U
    SUBPCI 10
    JRIZ _strncpy_exit_early

    ; Keep track of number of bytes copied
    INC

    ; Grab a byte from the source
    POP SPC
    SWAP PC, SPC
    POP U
    SWAP PC, SPC
    PUSH SPC

    ; Store that byte in the destination
    ADDPCI 2
    POP SPC
    SWAP PC, SPC
    STORE U
    INCPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 2

    ; See if we copied the null termination
    SWAP U, A
    ADDI 0
    SWAP A, U
    SKIPIF !ZF
    JRI _strncpy_done
    JRI _strncpy_loop

_strncpy_exit_early:
    ; Need to null-terminate the destination since we didn't do it normally.
    ZERO

    ADDPCI 2
    POP SPC
    SWAP PC, SPC
    STORE A
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 2

_strncpy_done:
    ; Restore the shadow stack and A register
    ADDPCI 4
    POP U
    POP A
    POP SPC

    ; Now, return to caller
    RET

wstrncpy:
    ; Given a stack holding a source and destination pointer as well as the maximum
    ; number of characters to copy as a 16-bit integer, copy a null-terminated string
    ; from source to destination. Always null-terminates. Number of characters to
    ; copy does not include the null termination which is always present. Does not
    ; clobber the A/U/V register nor the source/destination pointer on the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to copy a 500 bytes of a string from 0x1234 to 0x5678, call like so:
    ;     PUSHI 0x78
    ;     PUSHI 0x56
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     PuSHI 0xF4
    ;     PUSHI 0x01
    ;     CALL wstrncpy
    ;
    ; Stack layout after call:
    ; PC + 0  - copy of source pointer <-- beginning of loop here, normal exit here
    ; PC + 1  - copy of source pointer
    ; PC + 2  - copy of destination pointer
    ; PC + 3  - copy of destination pointer
    ; PC + 4  - saved A register
    ; PC + 5  - saved SP
    ; PC + 6  - saved SC
    ; PC + 7  - return address
    ; PC + 8  - return address
    ; PC + 9  - number of characters to copy <-- exit early
    ; PC + 10 - number of characters to copy
    ; PC + 11 - pointer to source
    ; PC + 12 - pointer to source
    ; PC + 13 - pointer to destination
    ; PC + 14 - pointer to destination
    ;
    ; Stack layout just before return:
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - pointer to source
    ; PC + 3 - pointer to source
    ; PC + 4 - pointer to destination
    ; PC + 5 - pointer to destination

    ; First, save the existing registers
    PUSH SPC
    PUSH A

    ; Copy source and destination pointers so we can iterate safely.
    ADDPCI 10
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 10
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 10
    LOAD A
    SUBPCI 11
    STORE A
    ADDPCI 10
    LOAD A
    SUBPCI 11
    STORE A

_wstrncpy_loop_check:
    ; Figure out if we copied the right number of bytes (is our countdown zero).
    ADDPCI 10
    LOAD A
    DECPC

    ADDI 0
    JRINZ _wstrncpy_loop

    ; Check second byte now that we know the first is zero.
    LOAD A
    ADDI 0
    JRIZ _wstrncpy_exit_early

_wstrncpy_loop:
    ; Decrement the number of bytes we have left to copy.
    POP SPC
    SWAP PC, SPC
    DECPC
    SWAP SPC, PC
    PUSH SPC

    ; Grab a byte from the source
    SUBPCI 9
    POP SPC
    SWAP PC, SPC
    POP A
    SWAP PC, SPC
    PUSH SPC

    ; Store that byte in the destination
    ADDPCI 2
    POP SPC
    SWAP PC, SPC
    STORE A
    INCPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 2

    ; See if we copied the null termination
    ADDI 0
    SKIPIF !ZF
    JRI _wstrncpy_done
    LNGJUMP _wstrncpy_loop_check

_wstrncpy_exit_early:
    ; Need to null-terminate the destination since we didn't do it normally.
    ZERO

    SUBPCI 7
    POP SPC
    SWAP PC, SPC
    STORE A
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 2

_wstrncpy_done:
    ; Copy the return pointer where it needs to go.
    ADDPCI 7
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 1
    LOAD A
    ADDPCI 2
    STORE A

    ; Restore the shadow stack and A register
    SUBPCI 6
    POP A
    POP SPC
    ADDPCI 2

    ; Now, return to caller
    RET

wstrtrunc:
    ; Given a stack holding a string pointer as well as the maximum number of
    ; characters the string should have as a 16-bit integer, truncate the string
    ; to that number of characters. If the string is already shorter, has no effect.
    ; If the string is longer, it will be truncated to the specified size. Does not
    ; clobber the A/U/V register nor the source/destination pointer on the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to truncate a string at 0x1234 to 500 bytes, call like so:
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     PuSHI 0xF4
    ;     PUSHI 0x01
    ;     CALL wstrtrunc
    ;
    ; Stack layout after call:
    ; PC + 0  - copy of string pointer <-- beginning of loop here, normal exit here
    ; PC + 1  - copy of string pointer
    ; PC + 2  - saved A register
    ; PC + 3  - saved SP
    ; PC + 4  - saved SC
    ; PC + 5  - return address
    ; PC + 6  - return address
    ; PC + 7  - number of characters to truncate to <-- exit early
    ; PC + 8  - number of characters to truncate to
    ; PC + 9  - pointer to string
    ; PC + 10 - pointer to string
    ;
    ; Stack layout just before return:
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - pointer to string
    ; PC + 3 - pointer to string

    ; First, save the existing registers
    PUSH SPC
    PUSH A

    ; Copy string pointer so we can iterate safely.
    ADDPCI 8
    LOAD A
    SUBPCI 9
    STORE A
    ADDPCI 8
    LOAD A
    SUBPCI 9
    STORE A

_wstrtrunc_loop_check:
    ; Figure out if we advanced past the right number of bytes (is our countdown zero).
    ADDPCI 8
    LOAD A
    DECPC

    ADDI 0
    JRINZ _wstrtrunc_loop

    ; Check second byte now that we know the first is zero.
    LOAD A
    ADDI 0
    JRIZ _wstrtrunc_exit_early

_wstrtrunc_loop:
    ; Decrement the number of bytes we have left to advance past to get to our truncation byte.
    POP SPC
    SWAP PC, SPC
    DECPC
    SWAP SPC, PC
    PUSH SPC

    ; Grab a byte from the string
    SUBPCI 7
    POP SPC
    SWAP PC, SPC
    POP A
    SWAP PC, SPC
    PUSH SPC

    ; See if we encountered a null terminator, meaning the string is already short enough.
    ADDI 0
    SKIPIF !ZF
    JRI _wstrtrunc_done
    LNGJUMP _wstrtrunc_loop_check

_wstrtrunc_exit_early:
    ; Need to null-terminate to truncate the string.
    ZERO

    SUBPCI 7
    POP SPC
    SWAP PC, SPC
    STORE A
    SWAP PC, SPC
    PUSH SPC

_wstrtrunc_done:
    ; Copy the return pointer where it needs to go.
    ADDPCI 5
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 1
    LOAD A
    ADDPCI 2
    STORE A

    ; Restore the shadow stack and A register
    SUBPCI 6
    POP A
    POP SPC
    ADDPCI 2

    ; Now, return to caller
    RET

wstradv:
    ; Given a stack holding a string pointer as well as the maximum number of
    ; characters the string to advance past as a 16-bit integer, return a pointer to
    ; the character we advanced to in the string. If the string is shorter, instead
    ; returns a pointer to the null byte, which behaves as if the string was
    ; zero-length. If the string is longer, the returned pointer will point at the
    ; position in the string that was requested. Does not clobber the A/U/V register
    ; nor the source/destination pointer on the stack.
    ;
    ; Safe to run out of ROM, uses initialized stack for locals only.
    ;
    ; If you want to advance a string at 0x1234 by 500 bytes, call like so:
    ;     PUSHI 0x34
    ;     PUSHI 0x12
    ;     PuSHI 0xF4
    ;     PUSHI 0x01
    ;     CALL wstradv
    ;
    ; Stack layout after call:
    ; PC + 0 - saved A register
    ; PC + 1 - saved SP
    ; PC + 2 - saved SC
    ; PC + 3 - return address
    ; PC + 4 - return address
    ; PC + 5 - number of characters to advance past
    ; PC + 6 - number of characters to advance past
    ; PC + 7 - pointer to string
    ; PC + 8 - pointer to string
    ;
    ; Stack layout just before return:
    ; PC + 0 - return address
    ; PC + 1 - return address
    ; PC + 2 - pointer to advanced string
    ; PC + 3 - pointer to advanced string

    ; First, save the existing registers
    PUSH SPC
    PUSH A

    ; Prime the loop by sitting atop the string pointer.
    ADDPCI 6

_wstradv_loop_check:
    ; Figure out if we advanced past the right number of bytes (is our countdown zero).
    LOAD A
    DECPC

    ADDI 0
    JRINZ _wstradv_loop

    ; Check second byte now that we know the first is zero.
    LOAD A
    ADDI 0
    JRIZ _wstradv_exit_early

_wstradv_loop:
    ; Decrement the number of bytes we have left to advance past to get to our truncation byte.
    POP SPC
    SWAP PC, SPC
    DECPC
    SWAP SPC, PC
    PUSH SPC

    ; Grab a byte from the string and advance our pointer.
    ADDPCI 2
    POP SPC
    SWAP PC, SPC
    LOAD A
    ADDI 0
    SKIPIF ZF
    INCPC
    SWAP PC, SPC
    PUSH SPC
    SUBPCI 1

    ; See if we encountered a null terminator, meaning the string is already short enough.
    JRINZ _wstradv_loop_check

_wstradv_done:
    ; Move to where we expect to be on the exit early case.
    SUBPCI 1

_wstradv_exit_early:
    ; Copy the return pointer where it needs to go.
    SUBPCI 2
    LOAD A
    ADDPCI 2
    STORE A
    SUBPCI 1
    LOAD A
    ADDPCI 2
    STORE A

    ; Restore the shadow stack and A register
    SUBPCI 6
    POP A
    POP SPC
    ADDPCI 2

    ; Now, return to caller
    RET
