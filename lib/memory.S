memory_exec:
  ; Stack layout just after call:
  ; PC + 0 - builtin(retptr)
  ; PC + 1 - builtin(retptr)
  ; PC + 2 - loc
  ; PC + 3 - loc
  ;
  ; Stack layout just before return:
  ; PC + 0 - builtin(retptr)
  ; PC + 1 - builtin(retptr)
  ;
  ; Save clobbered registers
  PUSH A
  PUSH SPC

  ; Assign correct values to our trampoline.
  SWAP PC, SPC
  SETPC _memory_exec_trampoline
  LOADI 0xF8
  STORE A
  INCPC
  SWAP PC, SPC
  ADDPCI 5
  LOAD A
  SWAP PC, SPC
  STORE A
  INCPC
  SWAP PC, SPC
  INCPC
  LOAD A
  SWAP PC, SPC
  STORE A
  SWAP PC, SPC

  ; Moving return pointer to correct location in stack.
  SUBPCI 2
  LOAD A
  ADDPCI 2
  STORE A
  SUBPCI 3
  LOAD A
  ADDPCI 2
  STORE A

  ; Restoring all clobbered registers.
  SUBPCI 5
  POP SPC
  POP A
  ADDPCI 2

  ; Executing the pointed at code.
  LNGJUMP _memory_exec_trampoline
