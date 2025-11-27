serial_send_byte:
  ; Stack layout just after call:
  ; PC + 0 - builtin(retptr)
  ; PC + 1 - builtin(retptr)
  ; PC + 2 - byte to send to serial
  ;
  ; Stack layout just before return:
  ; PC + 0 - builtin(retptr)
  ; PC + 1 - builtin(retptr)
  ;
  ; Save clobbered registers
  PUSH A
  PUSH V
  PUSH SPC

  ; Prime loop below to read the status register into a temporary byte.
  SUBPCI 1
  SWAP PC, SPC
  SETPC R6551AP_status_reg, 0
  SWAP PC, SPC

  ; Wait until we are ready to send a byte by checking the transmit empty bit.
_serial_send_byte_wait_tx:
  SWAP PC, SPC
  LOAD A
  SWAP PC, SPC
  STORE A
  LOADI 0x10
  AND
  JRIZ _serial_send_byte_wait_tx

  ; Actually send the byte out.
  ADDPCI 7
  LOAD V
  SWAP PC, SPC
  DECPC
  STORE V
  SWAP PC, SPC

  ; Moving return pointer to correct location in stack.
  SUBPCI 1
  LOAD A
  ADDPCI 1
  STORE A
  SUBPCI 2
  LOAD A
  ADDPCI 1
  STORE A

  ; Restoring all clobbered registers.
  SUBPCI 5
  POP SPC
  POP V
  POP A
  ADDPCI 1
  RET


_serial_lut:
  ; Stack layout just after call:
  ; PC + 0 - builtin(retptr)
  ; PC + 1 - builtin(retptr)
  ; PC + 2 - builtin(padding)
  ; PC + 3 - val
  ;
  ; Stack layout just before return:
  ; PC + 0 - builtin(retptr)
  ; PC + 1 - builtin(retptr)
  ; PC + 2 - builtin(retval)
  ; PC + 3 - builtin(retval)
  ;
  ; Save clobbered registers
  PUSH A
  PUSH SPC
  ; Set the SPC to our unrolled LUT below.
  SWAP PC, SPC
  SETPC _serial_move_str_unrolled
  SWAP PC, SPC
  ADDPCI 6
  ; Load val into A, which is what we want to convert to an integer.
  LOAD A
  SWAP PC, SPC
  ; Need to multiply A by 3. We could add, shift left, and add again, but that
  ; would put some numbers past 127 which would end up subtracting instead of adding.
  ADDPC
  ADDPC
  ADDPC
  SWAP PC, SPC
  ; Now, stick our calculation in the return value.
  ADDPCI 1
  PUSH SPC
  ; Restoring all clobbered registers.
  SUBPCI 5
  POP SPC
  POP A
  RET


_serial_move_str_unrolled:
  .char '1'
  .byte 0x00
  .byte 0x00
  .char '2'
  .byte 0x00
  .byte 0x00
  .char '3'
  .byte 0x00
  .byte 0x00
  .char '4'
  .byte 0x00
  .byte 0x00
  .char '5'
  .byte 0x00
  .byte 0x00
  .char '6'
  .byte 0x00
  .byte 0x00
  .char '7'
  .byte 0x00
  .byte 0x00
  .char '8'
  .byte 0x00
  .byte 0x00
  .char '9'
  .byte 0x00
  .byte 0x00
  .char '1'
  .char '0'
  .byte 0x00
  .char '1'
  .char '1'
  .byte 0x00
  .char '1'
  .char '2'
  .byte 0x00
  .char '1'
  .char '3'
  .byte 0x00
  .char '1'
  .char '4'
  .byte 0x00
  .char '1'
  .char '5'
  .byte 0x00
  .char '1'
  .char '6'
  .byte 0x00
  .char '1'
  .char '7'
  .byte 0x00
  .char '1'
  .char '8'
  .byte 0x00
  .char '1'
  .char '9'
  .byte 0x00
  .char '2'
  .char '0'
  .byte 0x00
  .char '2'
  .char '1'
  .byte 0x00
  .char '2'
  .char '2'
  .byte 0x00
  .char '2'
  .char '3'
  .byte 0x00
  .char '2'
  .char '4'
  .byte 0x00
  .char '2'
  .char '5'
  .byte 0x00
  .char '2'
  .char '6'
  .byte 0x00
  .char '2'
  .char '7'
  .byte 0x00
  .char '2'
  .char '8'
  .byte 0x00
  .char '2'
  .char '9'
  .byte 0x00
  .char '3'
  .char '0'
  .byte 0x00
  .char '3'
  .char '1'
  .byte 0x00
  .char '3'
  .char '2'
  .byte 0x00
  .char '3'
  .char '3'
  .byte 0x00
  .char '3'
  .char '4'
  .byte 0x00
  .char '3'
  .char '5'
  .byte 0x00
  .char '3'
  .char '6'
  .byte 0x00
  .char '3'
  .char '7'
  .byte 0x00
  .char '3'
  .char '8'
  .byte 0x00
  .char '3'
  .char '9'
  .byte 0x00
  .char '4'
  .char '0'
  .byte 0x00
  .char '4'
  .char '1'
  .byte 0x00
  .char '4'
  .char '2'
  .byte 0x00
  .char '4'
  .char '3'
  .byte 0x00
  .char '4'
  .char '4'
  .byte 0x00
  .char '4'
  .char '5'
  .byte 0x00
  .char '4'
  .char '6'
  .byte 0x00
  .char '4'
  .char '7'
  .byte 0x00
  .char '4'
  .char '8'
  .byte 0x00
  .char '4'
  .char '9'
  .byte 0x00
  .char '5'
  .char '0'
  .byte 0x00
  .char '5'
  .char '1'
  .byte 0x00
  .char '5'
  .char '2'
  .byte 0x00
  .char '5'
  .char '3'
  .byte 0x00
  .char '5'
  .char '4'
  .byte 0x00
  .char '5'
  .char '5'
  .byte 0x00
  .char '5'
  .char '6'
  .byte 0x00
  .char '5'
  .char '7'
  .byte 0x00
  .char '5'
  .char '8'
  .byte 0x00
  .char '5'
  .char '9'
  .byte 0x00
  .char '6'
  .char '0'
  .byte 0x00
  .char '6'
  .char '1'
  .byte 0x00
  .char '6'
  .char '2'
  .byte 0x00
  .char '6'
  .char '3'
  .byte 0x00
  .char '6'
  .char '4'
  .byte 0x00
  .char '6'
  .char '5'
  .byte 0x00
  .char '6'
  .char '6'
  .byte 0x00
  .char '6'
  .char '7'
  .byte 0x00
  .char '6'
  .char '8'
  .byte 0x00
  .char '6'
  .char '9'
  .byte 0x00
  .char '7'
  .char '0'
  .byte 0x00
  .char '7'
  .char '1'
  .byte 0x00
  .char '7'
  .char '2'
  .byte 0x00
  .char '7'
  .char '3'
  .byte 0x00
  .char '7'
  .char '4'
  .byte 0x00
  .char '7'
  .char '5'
  .byte 0x00
  .char '7'
  .char '6'
  .byte 0x00
  .char '7'
  .char '7'
  .byte 0x00
  .char '7'
  .char '8'
  .byte 0x00
  .char '7'
  .char '9'
  .byte 0x00
  .char '8'
  .char '0'
  .byte 0x00
