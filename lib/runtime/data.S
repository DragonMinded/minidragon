    .org 0xC000
data:
    ; This should point to the beginning of RAM.

_memory_exec_trampoline:
    .pad 3

    ; Following this are any global variables that are not constants.
