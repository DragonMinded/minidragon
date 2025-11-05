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
