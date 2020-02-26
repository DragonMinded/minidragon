    .org 0x8000

stack:
    ; Top of stack for algorithm.

    .org 0x0000

init:
    ; Set up the call stack
    SETPC stack

    ; TODO: Possibly initialize HW registers for support HW.
