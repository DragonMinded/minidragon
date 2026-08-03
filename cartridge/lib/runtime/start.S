    ; Swap our SPC back out from any init routines.
    SWAP PC, SPC
    POP SPC

    ; Jump to our main routine.
    CALL main

    ; Jump back to the boot ROM that called us.
    RET
