# Read how many executable banks are configured on the cartridge.
def cartridge_banks() -> extern[uint8]: ...


# Select the desired bank in the cartridge.
def cartridge_select_bank(bank: uint8) -> extern[void]: ...


# Read the 4 bit input value that the cartridge can assert.
def cartridge_input() -> extern[uint8]: ...


# Read the 8 bit expansion bus value at the time of probing.
def cartridge_expansion() -> extern[uint8]: ...
