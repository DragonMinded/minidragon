import sys

from hardware.cartridge import (
    cartridge_init,
    cartridge_banks,
    cartridge_select_bank,
    cartridge_run,
    cartridge_title,
    cartridge_author,
)
from hardware.serial import (
    serial_init,
    serial_clear,
    serial_send,
    serial_input,
)


def main() -> void:
    # Initialize hardware.
    cartridge_init()
    serial_init()

    while True:
        # Set up the screen for display.
        serial_clear()

        # Write out version information and system ready prompt.
        serial_send(f"MiniDragon v{sys.version}\n")

        # Figure out how many executable banks are in the inserted cartridge.
        banks: uint8 = cartridge_banks()
        if banks:
            serial_send("Available programs:\n")

            # Print out executable info for each bank, and then let the user choose.
            bank: uint8
            for bank in range(banks):
                cartridge_select_bank(bank)

                title: const[str] = cartridge_title()
                author: const[str] = cartridge_author()

                serial_send(f"{bank + 1} - {title} by {author}\n")

            # Prompt for an input.
            while True:
                selected: str[4] = serial_input("Select a program: ", max_length=3, allow_empty=False)
                bank = int(selected)
                if bank:
                    if bank > banks:
                        serial_send("Invalid selection!\n")
                    else:
                        # Chose a bank.
                        bank -= 1
                        break
                else:
                    serial_send("Invalid selection!\n")

            cartridge_select_bank(bank)
            cartridge_run()

        else:
            serial_send("No cartridge present.\n")

            # Busy loop forever.
            while True:
                pass
