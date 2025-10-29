    ; Set up the stack based on init.S
    SETPC stack

    ; Jump to our main routine.
    CALL main

    ; Loop forever.
    HALT
