    .org 0xC800
data:
    ; This should point to the beginning of our allowed RAM. This is further than
    ; the beginning of RAM to give room for the boot ROM to have working RAM for
    ; libraries that it provides to us.
