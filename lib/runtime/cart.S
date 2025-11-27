    .org 0x8000
cart:
    ; This should point to the beginning of cartridge space.

    .org 0x8080
cart_entrypoint:
    ; This should point at the entrypoint for any given cartridge.
