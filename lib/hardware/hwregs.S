    .org 0x7800
    ; This should point to the beginning of the memory mapped peripherals.
peripherals:

    ; Our R6551AP is at slot zero, so occupies this location in the memory.
R6551AP_buffer_reg:

    .org 0x7801
R6551AP_status_reg:

    .org 0x7802
R6551AP_command_reg:

    .org 0x7803
R6551AP_control_reg:

