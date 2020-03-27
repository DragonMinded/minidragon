    .org 0x8000

stack:
    ; Top of stack for algorithm.

    .org 0x0000

init:
    ; Leave room for the first instruction to be decoded as a NOP.
    ; This is potentially important depending on when we come out of
    ; reset. Since the microcode ticks on the clock high->low transition,
    ; we could end up in a situation where our clock width for the high
    ; portion is not enough to be detected, so we could lose an instruction
    ; load. If this happens, then the instruction will be decoded as a
    ; NOP, and we will lose the first instruction at the entrypoint. So,
    ; adjust for this and add a NOP as the first instruction we run.
    NOP

    ; Set up the call stack
    SETPC stack

    ; TODO: Possibly initialize HW registers for support HW.
