    .org 0x8000
cartridge_title:
    ; The name of your cartridge, can be up to 63 characters long.
    .str "Hello, World"

    .org 0x8040
cartridge_author:
    ; The author of your cartridge, can be up to 63 characters long.
    .str "DragonMinded"
