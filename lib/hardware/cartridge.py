# The bank control register for any attached cartridge.
CCR_bank_control_reg: extern[uint8]

# The bank configuration register from any attached cartridge.
CCR_bank_config_reg: extern[uint8]

# Read-only expansion bus peek register.
CCR_expansion_reg: extern[uint8]

# Constants for finding various bits of info about a cartridge.
CARTRIDGE_HEADER_TITLE: const[uint16] = 0x8000
CARTRIDGE_HEADER_AUTHOR: const[uint16] = 0x8040


def cartridge_init() -> void:
    """
    Initialize the CCR by configuring it to talk to the cartridge.
    """

    global CCR_bank_control_reg
    CCR_bank_control_reg = 0


def cartridge_banks() -> uint8:
    """
    Read how many executable banks are configured on the cartridge.
    """

    return CCR_bank_config_reg & 0xF


def cartridge_select_bank(bank: uint8) -> void:
    """
    Select the desired bank in the cartridge.
    """

    global CCR_bank_control_reg
    CCR_bank_control_reg = bank & 0xF


def cartridge_input() -> uint8:
    """
    Read the 4 bit input value that the cartridge can assert.
    """

    return (CCR_bank_config_reg >> 4) & 0xF


def cartridge_expansion() -> uint8:
    """
    Read the 8 bit expansion bus value at the time of probing.
    """

    return CCR_expansion_reg


def cartridge_run() -> extern[void]: ...
    # Runs the executable in the currently selected cartridge bank.


def cartridge_author() -> str[64]:
    """
    Read and return the author of the cartridge.
    """
    return peek(CARTRIDGE_HEADER_AUTHOR, 63)


def cartridge_title() -> str[64]:
    """
    Read and return the title of the cartridge.
    """
    return peek(CARTRIDGE_HEADER_TITLE, 63)
