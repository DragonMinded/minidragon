# MiniDragon

Schematics, hardware simulator and software files for the MiniDragon CPU. This is a from-scratch CPU that I designed and am implementing using transistors, capacitors, resistors and diodes. The goal is to make an 8-bit CPU that could be used for general-purpose computing. There are a lot of toy instruction sets floating around on the web. I chose instead to design my own, loosely based off of the PDP and 6502. It is a single accumulator design with a pair of 16-bit stack pointers and a pair of temporary 8-bit registers. Instructions are 8 bits, operands are 8 bits from memory, temporary registers or immediate, and running software can access all 16 bits of memory available to the CPU. Eventually, I want the assembled CPU along with some external RAM, ROM and a serial interface chip to be self-hosting. So, I hope to eventually have a built-in assembler or BASIC interpreter in the ROM.

## Layout

The layout is separated into logical components:

 * Microcode counter. This keeps track of what microcode in the current instruction we are operating on.
 * Instruction decoder logic. This consists of an instruction register and a series of ROM boards made out of jumpers. This uses the microcode counter as well as its own internal combinatorial logic to select one instruction and output control signals to the rest of the CPU.
 * Registers. These exist on various busses, and their input/output is controlled by the instruction decoder logic's control signals.
 * Constant circuits. These can output either a zero or an immediate value sign extended from the current instruction register. Their operation is controlled by the instruction decoder's control signals.
 * ALU. This is built out of a series of smaller components on its own internal bus. Selection of which operation as well as which input is controlled via the instruction decoder logic's control signals.
 * Flags handling. This consists of a few registers to hold flags generated by the ALU and put them on the data bus when appropriate. This is controlled via the control signal lines much like the rest of the non-instruction decoder components.
 * Memory interface. This provides the glue so that the CPU can be seen as having a set of address and data lines as well as an output enable and write enable line, much like a traditional non-SOC CPU.

### Internal Busses

 * 16-bit data bus. Most registers can only read from or write to the lower 8 bits of this bus, but some can also output their value to the upper 8 bits. Various 16-bit registers are able to read the entire 16-bit bus, and this is how the upper bits of the instruction pointer and stack pointers can be read. The lower 8 bits of this will feed the external data IO lines.
 * 16-bit address bus. This feeds the external address requests by the CPU and is driven by both the instruction pointer and stack pointers.
 * 16-bit ALU source bus. This allows the ALU A source to be controlled, so that various 16-bit registers we want to add/subtract from don't need to be placed in a temporary location.

### Registers

 * 16-bit instruction pointer register (IP), holding the address of the current instruction in memory. Its value can be placed on the address bus or ALU input bus and it can read from the data bus. Software can jump relative to the current instruction, as well as pushing the current IP to the stack (controlled by the PC combined register), pop the IP from the stack or jump to an immediate 16 bit address.
 * 8-bit instruction register (IR), holding the current instruction that was fetched from memory. It is write-only and feeds microcode decoding logic, but can read from the data bus. Software cannot directly set this, but memory is modifiable so self-modifying code is possible.
 * 8-bit accumulator register (A), holding the current accumulated result. It can read from and write to the data bus, and it can output to the ALU input bus. Many instructions available to software can directly manipulate this register. Its value can be moved to and from the P and C registers as well as added to the combined PC register, allowing it to be used for indirect memory address modes as well.
 * 8-bit ALU temporary register (B), holding a temporary value from the bus. It can read from and write to the data bus. Its output is also hardcoded to the second input of the ALU. Software has no capability to modify this register and it is used by various microcodes to accomplish virtually all CPU operations. When the ALU is operating on a 16-bit number, the B register will be sign-extended to 16 bits.
 * 8-bit memory page register (P) and 8-bit memory cell register (C), together holding a 16-bit address. The P and C registers can individually read from the data bus, and the combined PC value can be output to the address bus or the ALU input bus. Software can write to the P and C registers from the A register and can use the combined PC register contents to load from and store to memory. Some ALU operations allow the memory address pointed at by the PC register to be used as an operand for ALU operations against the accumulator (A). The current value of the instruction pointer (IP) can be pushed to or popped from memory referred to by this register. The current value of the shadow PC combined register can also be pushed to or popped from memory referred to by this register.
 * 8-bit shadow page register (SP) and 8-bit shadow cell register (SC), together holding a 16-bit address referred to as SPC. This is not directly addressable, but its current value can be pushed to or popped from the location pointed at by the PC register, and a SWAP instruction allows software to swap the PC and SPC registers.
 * 8-bit CPU data register (D), holding temporary values when the CPU is pushing or popping a 16-bit value off of the stack (PC). We could use the A register for this, but I wanted to make sure that the accumulator was not clobbered when performing stack operations. This is not user readable or writeable.
 * 8-bit temporary registers (U and V), available to the programmer for various operations. These can be moved to from A, swapped to from A or each other, loaded from and stored to memory, and can be used as operands for ALU operations against the accumulator (A).
 * 3-bit flags register, containing a carry flag (CF), a zero flag (ZF) and a shadow PC flag (PC). Software cannot directly set or clear the carry or zero flags, but both carry and zero flags are set appropriately when carrying out any ALU-based operation which sources from and stores to the A register. It is not directly readable by software but there exist skip instructions that allow software to conditionally execute a particular instruction if either CF or ZF is set or cleared. Additionally, several ALU operations allow using the carry flag as an input to chain operations together for 16 and 32 bit arithmetic. The PC flag is toggleable using a special SWAP instruction.

### Instructions

 * JRI - Jump relative to immediate sign-extended + 1. Assembler also supports labels. Can jump 32 forward or backward relative to next instruction. Specifically designed such that "JRI 0" jumps to the next instruction and is encoded as all zeros.
 * LOADI - Load immediate stored in next memory cell to A. Can load any 8-bit value. Skips over that value after executing since it is not a valid instruction.
 * ADDI - Add immediate sign-extended to A, no carry. Can add values between -32 and 31. Affects ZF and CF.
 * INV - Bitwise invert A. Affects ZF and CF.
 * SHL - Shift A left by 1, setting the bottom bit to 0, set carry to top bit shifted out. Affects ZF and CF.
 * SHR - Shift A right by 1, setting the top bit to 0, set carry to bottom bit shifted out. Affects ZF and CF.
 * RCL - Shift A left by 1, setting bottom bit to the carry flag, set carry to top bit shifted out. Affects ZF and CF.
 * RCR - Shift A right by 1, setting top bit to the carry flag, set carry to bottom bit shifted out. Affects ZF and CF.
 * ROL - Shift A left by 1, setting the bottom bit to the shifted out top bit, set carry to top bit shifted out. Affects ZF and CF.
 * ROR - Shift A right by 1, setting the top bit to the shifted our bottom bit, set carry to bottom bit shifted out. Affects ZF and CF.
 * ADD - Add contents of memory location PC to A register. Affects ZF and CF.
 * ADC - Add contents of memory location PC to A register, with carry in from flags. Affects ZF and CF.
 * AND - And contents of memory location PC against A register. Affects ZF and CF.
 * OR - Or contents of memory location PC against A register. Affects ZF and CF.
 * XOR - XOR contents of memory location PC against A register. Affects ZF and CF.
 * ADDU - Add contents of U to A register. Affects ZF and CF.
 * ADCU - Add contents of U to A register, with carry in from flags. Affects ZF and CF.
 * ANDU - And contents of U against A register. Affects ZF and CF.
 * ORU - Or contents of U against A register. Affects ZF and CF.
 * XORU - XOR contents of U against A register. Affects ZF and CF.
 * ADDV - Add contents of V to A register. Affects ZF and CF.
 * ADCV - Add contents of V to A register, with carry in from flags. Affects ZF and CF.
 * ANDV - And contents of V against A register. Affects ZF and CF.
 * ORV - Or contents of V against A register. Affects ZF and CF.
 * XORV - XOR contents of V against A register. Affects ZF and CF.
 * ADDPCI - Add immediate to PC. Can add any value between 1 and 32 inclusive. Since we only have the capability of sign-extending the bottom 4 or 6 bits of an instruction to use as an immediate, this intentionally chooses an instruction prefix which sets the 6th bit to 0, in order to simplify decoding logic as well as keep the immediate register simple. This is why there is a separate ADDPCI and SUBPCI instruction.
 * SUBPCI - Subtract immediate from PC. Can subtract any value between 1 and 32 inclusive. Much like ADDPCI, this uses a clever trick where the 6th bit in the instruction prefix is set to 1, in order to correctly sign-extend the immediate.
 * ADDPC - Add A register sign-extended from 8 to 16 bits to the PC register.
 * ATOP - Load contents of A register to P.
 * ATOC - Load contents of A register to C.
 * PTOA - Load contents of P register to A.
 * CTOA - Load contents of C register to A.
 * ATOU - Load contents of A register to U.
 * ATOV - Load contents of A register to V.
 * UTOA - Load contents of U register to A.
 * VTOA - Load contents of V register to A.
 * LOADA - Load contents of memory location pointed at by PC to A register.
 * STOREA - Store contents of A register to memory location pointed at by PC.
 * LOADU - Load contents of memory location pointed at by PC to U register.
 * STOREU - Store contents of U register to memory location pointed at by PC.
 * LOADV - Load contents of memory location pointed at by PC to V register.
 * STOREV - Store contents of V register to memory location pointed at by PC.
 * SKIPIF - Skip next instruction if carry/zero flag set/cleared. To save on decoding logic, the lower 3 bits of the SKIPIF instruction feed combinatorial logic in the flags register. This leaves us with four undefined instructions which would, if executed, choose to operate on either both or neither of the carry and zero flag simultaneously.
 * LNGJUMP - Jumps to address stored in memory location IP + 1 and IP + 2, stored in big-endian.  Skips over the two values after executing since they are not valid instructions.
 * SWAPAU - Swap contents of A and U registers.
 * SWAPAV - Swap contents of A and V registers.
 * SWAPUV - Swap contents of U and V registers.
 * SWAPPC - Swap PC and SPC registers, making the current PC into the shadow PC and vice versa.
 * PUSHIP - Subtracts two from PC, stores IP + immediate into location PC and PC + 1 big endian. Immediate can be a positive integer between 0 and 7 inclusive and is often non-zero in order to store the correct return address of a subroutine call.
 * POPIP - Jumps to data stored in memory location PC and PC + 1 big endian, adds 2 to PC.
 * PUSHSPC - Subtracts two from PC, stores SPC into location PC and PC + 1 big endian.
 * POPSPC - Loads SPC with value stored in memory location PC and PC + 1 big endian, adds 2 to PC.

### Assembler-Provided Macros

For convenience of programming without too much hassle, several assembler macros which are encoded to a series of the above instructions are available:

 * NOP - Perform no operation. Implemented as "JRI 0", which as noted above is encoded as a null byte.
 * HALT - Jump to self, loop forever. Implemented as "JRI -1".
 * ZERO - Zero the contents of A. Implemented as "LOADI 0".
 * SETPC - Set immediate value to PC register, clobbering A register. Sets PC to full 16-bit value. Implemented as a pair of "LOADI" instructions followed by the appropriate "ATOP" and "ATOC".
 * INCPC - Add 1 to PC. Implemented as "ADDPCI 1".
 * DECPC - Subtract 1 from PC. Implemented as "SUBPCI 1".
 * STOREI - Stores immediate value to memory pointed at by PC register, clobbering A register. Stores full 8-bit value to memory. Implemented as a "LOADI" followed by a "STOREA".
 * NEG - Twos compliment negate A register. Implemented as an "INV" followed by an "ADDI 1".
 * INC - Increment A register. Implemented as an "ADDI 1".
 * DEC - Decrement A register. Implemented as an "ADDI -1".
 * RET - Return from subroutine (identical to POPIP).
 * JRIZ - Jump relative if zero flag set. Implemented using "SKIPIF" and "JRI".
 * JRINZ - Jump relative if zero flag not set. Implemented using "SKIPIF" and "JRI".
 * JRIC - Jump relative if carry flag set. Implemented using "SKIPIF" and "JRI".
 * JRINC - Jump relative if carry flag not set. Implemented using "SKIPIF" and "JRI".
 * LNGJUMPZ - Jump to address if zero flag set. Implemented using "SKIPIF", "JRI" and "LNGJUMP".
 * LNGJUMPNZ - Jump to address if zero flag not set. Implemented using "SKIPIF", "JRI" and "LNGJUMP".
 * LNGJUMPC - Jump to address if carry flag set. Implemented using "SKIPIF", "JRI" and "LNGJUMP".
 * LNGJUMPNC - Jump to address if carry flag not set. Implemented using "SKIPIF", "JRI" and "LNGJUMP".
 * CALL - Subtracts two from PC, stores the next instruction after this instruction to PC, then jumps to the immediate address. Return from this using “RET”. Implemented using a "PUSHIP" and a "LNGJUMP".
 * CALLRI - Subtracts two from PC, stores the next instruction after this instruction to PC, then jumps to the relative offset from the next instruction. Return from this using “RET”. Implemented using a "PUSHIP" and a "JRI" instruction, meaning it is only useful for subroutines located close in memory. However, it can save several bytes.
 * PUSH x - Subtracts operand size from PC, stores the value of A/U/V/IP/SPC into the memory location PC. This is simply a virtual instruction that maps to "STOREA", "STOREU", "STOREV", "PUSHIP" or "PUSHSPC", so that the correct instruction doesn't have to be remembered.
 * PUSHI - Subtracts 1 from PC, stores immediate to memory location PC, clobbering A register. Implmented as a "DECPC" followed by a "STOREI" macro.
 * POP x - Loads the value of memory location PC into A/U/V/IP/SPC, adds operand size to PC. Works identically to "PUSH x" as a virtual instruction alias to several concrete instructions.
 * LOAD x - Loads the value pointed at in memory by PC to A/U/V. Alias for the various concrete load instructions, similar to "PUSH x" and "POP x".
 * STORE x - Stores the value in A/U/V into the memory location pointed at by PC. Alias for the various concrete store instructions, similar to "PUSH x" and "POP x".
 * SWAP x, y - Swaps the contents of a pair of registers. Valid pairs are either from A/U/V or PC/SPC. Alias for the various concrete swap instructions, similar to "PUSH x", "POP x", "LOAD x" and "STORE x".
 * MOV x, y - Moves the contents of the x register into the y register. Any register A/U/V/P/C can be moved to or from as long as one of the operands is the A register. Alias for the various concrete load instructions, similar to "SWAP x, y".

### Opcode Layout

The 8-bit space for a single opcode is split up in order to make it possible to decode instructions using the least amount of logic. There are some holes where future instructions might be added. For now, undefined instructions will produce undefined behavior in the CPU. As currently implemented, the control logic will output all 1's for all control signals of undefined or un-mapped instructions. For this layout, the following conventions are used:

 * Register name - Register names listed directly refer to the value of that register. So, `A + 1` would refer to an operation that takes the value of A and adds 1.
 * `>` - Right carat, implies that the result of the operation on the left is stored to register/location on the right.
 * `[` and `]` - Dereference. This implies that the value of what is inside the `[]` is an address where we will store. So `1 > [PC]` implies that the value of "1" would be stored to the 8-bit memory location referenced by the PC combined register.
 * `{` and `}` - Register operand from the opcode itself. Currently, register operands are defined as follows:
   * `00` - Undefined, no register mapping.
   * `01` - U register.
   * `10` - V register.
   * `11` - SRAM pointed at by PC register.

<pre>
opcpde            description                         implementation                 mnemonic        alias
----------------------------------------------------------------------------------------------------------

<b>y y y y y y y y   immediate op</b>
0 0 x x x x x x   jump to immediate offset            IP + imm + 1 > IP              JRI x
0 1 x x x x x x   add immediate to A                  A + imm -> A                   ADDI x

<b>1 0 0 y y y y y   stack immediate op</b> †1
1 0 0 0 0 x x x   push IP + immediate                 PC - 2 > PC, IP + imm > [PC]   PUSHIP x        PUSH IP + x

<b>1 0 0 s s y y y   arithmetic op with operand</b> †2
1 0 0 s s 0 0 0   invert A                            ~A > A                         INV
1 0 0 s s 0 0 1   add from [PC]/U/V                   A + {ss} > A                   ADD/ADDU/ADDV
1 0 0 s s 0 1 0   add with carry from [PC]/U/V        A + {ss} + CF > A              ADC/ADCU/ADCV
1 0 0 s s 0 1 1   and from [PC]/U/V                   A & {ss} > A                   AND/ANDU/ANDV
1 0 0 s s 1 0 0   or from [PC]/U/V                    A | {ss} > A                   OR/ORU/ORV
1 0 0 s s 1 0 1   xor from [PC]/U/V                   A ^ {ss} > A                   XOR/XORU/XORV
1 0 0 s s 1 1 0   <i>see tables below</i>
1 0 0 s s 1 1 1   <i>see tables below</i>

<b>1 0 0 s s y y y   arithmetic op against U</b>
1 0 0 0 1 0 0 0   <i>invert A</i>
1 0 0 0 1 0 0 1   <i>add from U</i>
1 0 0 0 1 0 1 0   <i>add with carry from U</i>
1 0 0 0 1 0 1 1   <i>and from U</i>
1 0 0 0 1 1 0 0   <i>or from U</i>
1 0 0 0 1 1 0 1   <i>xor from U</i>
1 0 0 0 1 1 1 0   rotate left A                       A << 1 + ((A >> 7) & 0x01) > A ROL
1 0 0 0 1 1 1 1   rotate right A                      A >> 1 + ((A << 7) & 0x80) > A ROR

<b>1 0 0 s s y y y   arithmetic op against V</b>
1 0 0 1 0 0 0 0   <i>invert A</i>
1 0 0 1 0 0 0 1   <i>add from V</i>
1 0 0 1 0 0 1 0   <i>add with carry from V</i>
1 0 0 1 0 0 1 1   <i>and from V</i>
1 0 0 1 0 1 0 0   <i>or from V</i>
1 0 0 1 0 1 0 1   <i>xor from V</i>
1 0 0 1 0 1 1 0   rotate left with carry A            A << 1 + CF > A                RCL
1 0 0 1 0 1 1 1   rotate right with carry A           A >> 1 + (CF << 7) > A         RCR

<b>1 0 0 s s y y y   arithmetic op against [PC]</b>
1 0 0 1 1 0 0 0   <i>invert A</i>
1 0 0 1 1 0 0 1   <i>add from [PC]</i>
1 0 0 1 1 0 1 0   <i>add with carry from [PC]</i>
1 0 0 1 1 0 1 1   <i>and from [PC]</i>
1 0 0 1 1 1 0 0   <i>or from [PC]</i>
1 0 0 1 1 1 0 1   <i>xor from [PC]</i>
1 0 0 1 1 1 1 0   shift left A                        A << 1 > A                     SHL
1 0 0 1 1 1 1 1   shift right A                       A >> 1 > A                     SHR

<b>1 0 1 y y y y y   pc subtract op</b> †3
1 0 1 x x x x x   Subtract immediate from PC          PC - imm - 1 > PC              SUBPCI x

<b>1 1 0 y y y y y   pc add op</b> †4
1 1 0 x x x x x   Add immediate to PC                 PC + imm + 1 > PC              ADDPCI x

<b>1 1 1 0 0 y y y   register op</b>
1 1 1 0 0 0 0 0   load from address P + C to U        [P | C] > U                    LOADU           LOAD U
1 1 1 0 0 0 0 1   store to address P + C from U       U > [P | C]                    STOREU          STORE U
1 1 1 0 0 0 1 0   load from address P + C to V        [P | C] > V                    LOADV           LOAD V
1 1 1 0 0 0 1 1   store to address P + C from V       V > [P | C]                    STOREV          STORE V
1 1 1 0 0 1 0 0   swap A and U                        A > U, U > A                   SWAPAU          SWAP A, U/SWAP U, A
1 1 1 0 0 1 0 1   swap A and V                        A > V, V > A                   SWAPAV          SWAP A, V/SWAP V, A
1 1 1 0 0 1 1 0   swap U and V                        U > V, V > U                   SWAPUV          SWAP U, V/SWAP V, U
1 1 1 0 0 1 1 1   swap PC and SPC                     PC > SPC, SPC > PC             SWAPPC          SWAP PC, SPC/SWAP SPC, PC

<b>1 1 1 0 1 y y y   memory op</b>
1 1 1 0 1 0 0 0   load page register from A           A > P                          ATOP            MOV A, P
1 1 1 0 1 0 0 1   load cell register from A           A > C                          ATOC            MOV A, C
1 1 1 0 1 0 1 0   store page register to A            P > A                          PTOA            MOV P, A
1 1 1 0 1 0 1 1   store cell register to A            C > A                          CTOA            MOV C, A
1 1 1 0 1 1 0 0   load U register from A              A > U                          ATOU            MOV A, U
1 1 1 0 1 1 0 1   load V register from A              A > V                          ATOV            MOV A, V
1 1 1 0 1 1 1 0   store U register to A               U > A                          UTOA            MOV U, A
1 1 1 0 1 1 1 1   store V register to A               V > A                          VTOA            MOV V, A

<b>1 1 1 1 0 y y y   status op</b> †5
1 1 1 1 0 0 0 0
1 1 1 1 0 0 0 1
1 1 1 1 0 0 1 0   skip next instruction if CF         IP + 1 + CF > IP               SKIPIF CF
1 1 1 1 0 0 1 1   skip next instruction if !CF        IP + 1 + !CF > IP              SKIPIF !CF
1 1 1 1 0 1 0 0   skip next instruction if ZF         IP + 1 + ZF > IP               SKIPIF ZF
1 1 1 1 0 1 0 1   skip next instruction if !ZF        IP + 1 + !ZF > IP              SKIPIF !ZF
1 1 1 1 0 1 1 0
1 1 1 1 0 1 1 1

<b>1 1 1 1 1 y y y   stack op</b>
1 1 1 1 1 0 0 0   jump to immediate                   [IP + 1] > IP                  LNGJUMP x
1 1 1 1 1 0 0 1   load immediate                      [IP + 1] -> A                  LOADI x
1 1 1 1 1 0 1 0   add to PC                           PC + A > PC                    ADDPC
1 1 1 1 1 0 1 1   pop IP                              [PC] > IP, PC + 2 > PC         POPIP           POP IP
1 1 1 1 1 1 0 0   push SPC                            PC - 2 > PC, SPC > [PC]        PUSHSPC         PUSH SPC
1 1 1 1 1 1 0 1   pop SPC                             [PC] > SPC, PC + 2 > PC        POPSPC          POP SPC
1 1 1 1 1 1 1 0   load from address P + C             [P | C] > A                    LOADA           LOAD A
1 1 1 1 1 1 1 1   store to address P + C              A > [P | C]                    STOREA          STORE A
</pre>

 * †1 This instruction occupies the same space as the ALU operations. This is why register operand {00} is undefined. The instruction decoder will not select the ALU operation decoder board when "PUSHIP" is detected.
 * †2 This might be slightly misleading, given that the register operand {00} is not only undefined but also not mapped to ALU operations. See †1 for details.
 * †3 Due to only being able to sign-extend the lower 4 or 6 bits of an instruction, this cleverly puts itself into an instuction slot where the 6th bit is 1.
 * †4 Due to only being able to sign-extend the lower 4 or 6 bits of an instruction, this cleverly puts itself into an instuction slot where the 6th bit is 0.
 * †5 Even though there are four undefined instructions here, attempting to specify one will decode to a SKIPIF instruction. However, the behavior is still undefined due to how we use the lower 3 bits as selector signals for combinatorial logic. The lowest bit is used as an "invert selected flags signal" bit, and the next two bits are used as "CF select" and "ZF select".

## Design Concessions

As was the case with many 8-bit CPUs in the last century, this CPU does not have included memory, either volatile or non-volatile. It instead will assume an external chip or set of chips present on its external address and data bus. These chips, in the interest of practicality, will be standard TTL DIP package chips providing 32kb of SRAM, 16KB of ROM and 16KB of IO address space in which I am currently planning to place an 8-bit serial chip. Other plans include an LCD output and PS2 keyboard input and possibly a cartridge space to load external programs.

Due to the sheer number of parts involved in making a register as well as the control logic needed in order to select registers for ALU operations, there are only two scratch registers. Most intermediate values must therefore be stored on the stack. Various core library operations were sped up significantly when adding the U and V registers as slower stack manipulation operations could be dropped. Additional speedups as well as easier implementation of core functionality could be realized by adding additional scratch registers. However, this would increase the complexity of the instruction decoding logic and require a necessary juggling of instructions in the above table.

Similarly, due to the complexity of such a circuit, no number comparison instructions are present. Instead, comparison functions are implemented in the stdlib by bitwise comparing two numbers from top to bottom bit. This makes a lot of functions such as integer conversion and division functions much slower than they need to be. Due to this, I'm considering possibly adding a compare function to the ALU and placing it in place of the INV instruction. INV would move to the unused opcode in the status op block, at which case I would have room to implement a hardware NEG. I've experimented with this on a separate branch and the gains are significant. Alternatively, its possible to design an external math coprocessor. This is similar to contemporary CPUs with a floating point or math coprocessor so would not be out of the question. If this happens, the standard library should be updated to call the coprocessor instead of perofrming comparisons, multiplication and division on-CPU.

Because of the complexity of designing such a system from scratch, there are a lot of inefficiencies in how the various circuits are assembled. In many cases, buffers are not actually necessary and add to propagation delay. In order to make the project manageable by a single creature, I've decided to sacrifice any sort of speed for modularity. This will result in a CPU that can theoretically only operate at a clock cycle of ~100KHz. If I was to be a lot more dilligent I could probably get this up into the several hundered or even megahertz level, but it isn't worth it. Perhaps in a second TTL-only iteration?

## Build Progress

As I continue with both the physical and virtual implementations of MiniDragon its been useful to break down the work into more manageable tasks. A side benefit is that I get to see things moving closer to completion at a much smaller scale. As of last calculation, I am 43% finished with the whole project.

### Hardware

As a whole, the hardware side of MiniDragon is 43% complete.

 - instruction decoder: 4% complete
    - Design work and diagramming for the instruction decoder core, including microcode counting, distribution logic, demultiplexing logic and associated glue is finished. Diagramming for exact connections to various instruction ROM boards is not complete. Of the 53 instructions (52 real intsructions and a microcode board for the shared load instruction step) only one instruction is fully hooked in. The instruction decoder core is fully built and integrated into the physical build.
 - special registers: 100% complete
   - All design work and diagramming for necessry circuits is completed. Registers that can be read in order to perform conditional logic as well as source immediate values are completed and fully integrated onto the physical build.
 - general purpose registers: 38% complete
   - All design work and diagramming for the eight general purpose registers is completed. Three registers (A, B and D) are built and fully integrated into the physical build.
 - ALU: 0% complete
   - I have started on the design of the ALU, but have not begun to document it in the schematics. I have a general idea of the direction I will take, but almost nothing concrete exists. The ALU will be decomposed into seven core functions that each will generate their own output and carry flag and a shared zero flag generator. I am hoping to design a modular ALU which can be built one function at a time for easier integration.
 - memory interface: 0% complete
   - MiniDragon CPU is designed to appear like a standard 80's CPU from external components' perspective. This means 16 output "pins" for address lines, 8 bidirectional "pins" for data lines, and a few crucial control signals brought out. These signals will include a bus enable (which determines when the CPU is attempting to use the address/data bus) and a read/write signal (which dictates whether the data pins should be seen as input or output). Its possible that I will instead bring out write enable and read enable bits which dictate that the bus should be active and either a read or a write should occur. It should be noted that all of these signals are asynchronous. System clock and reset lines may be brought out as external pins should that be necessary, but this was not normally done for period-accurate CPUs.
   - Additional circuitry that is not technically part of MiniDragon but will be necessary for its execution include a serial chip for IO, glue logic to support address decoding, a ROM chip and an SRAM chip to provide nonvolatile and volatile storage. These will likely be built using off-the-shelf TTL-compatible 7400 logic since they aren't part of the CPU itself.
 - power distribution: 100% complete
   - I went with an adjustable 5V switching mode power supply that can supply the necessary amperage (5+ amps estimated at this point) along with a digital voltmeter to make fine adjustments. The circuits are fairly sensitive to core voltage being at or slightly above 5V the integrated digital voltmeter necessary to accurately monitor the system.
 - debugging boards: 50% complete
   - Various debugging boards, used mostly for setting hand-selected values on various busses are designed and prototyped on breadboards. They are not laid out for fabrication. I am still weighing whether or not this will be necessary.

### Software

As a whole, the software side of MiniDragon is 74% complete.

 - assembler and disassembler: 100% completed.
 - simulator: 100% completed.
 - stdlib: 97% completed.
   - The standard library sits at 33 of 34 desired functions. I am not currently targetting signed math so I have limited the math library to unsigned integers only. Remaining functions to implement include: itoa32.
 - BIOS: 0% completed.
   - Because I have not yet solidified my decision on the serial chip for MiniDragon I have not bothered to start with a BIOS. Plans include basic startup and memory access tests followed by some sort of assembler or interpreter and possibly an executable format and loader.
   - I am currently leaning towards supporting VT-100 over serial, giving me input and output that can be paired with a modern terminal emulator or a physical terminal device.
