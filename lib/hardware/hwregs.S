    .org 0x7800
    ; This should point to the beginning of the memory mapped peripherals.
peripherals:

    ; Our R6551AP is at slot zero, so occupies this location in the memory.
    .org 0x7800
R6551AP_buffer_reg:

    .org 0x7801
R6551AP_status_reg:

    .org 0x7802
R6551AP_command_reg:

    .org 0x7803
R6551AP_control_reg:

    ; Our CCR is at slot seven, so occupies this location in memory.
    .org 0x7F00
CCR_bank_control_reg:

    .org 0x7F01
CCR_bank_config_reg:

    .org 0x7F02
CCR_expansion_reg:
