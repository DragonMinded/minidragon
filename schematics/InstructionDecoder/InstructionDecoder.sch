EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 369 374
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text HLabel 1500 1500 0    50   Input ~ 0
INSN_7
Text HLabel 1500 1600 0    50   Input ~ 0
INSN_6
Text HLabel 1500 1700 0    50   Input ~ 0
INSN_5
Text HLabel 1500 1800 0    50   Input ~ 0
INSN_4
Text HLabel 1500 1900 0    50   Input ~ 0
INSN_3
Text HLabel 1500 2000 0    50   Input ~ 0
INSN_2
Text HLabel 1500 2100 0    50   Input ~ 0
INSN_1
Text HLabel 1500 2200 0    50   Input ~ 0
INSN_0
Text HLabel 1500 3000 0    50   Input ~ 0
MCODE_3
Text HLabel 1500 3100 0    50   Input ~ 0
MCODE_2
Text HLabel 1500 3200 0    50   Input ~ 0
MCODE_1
Text HLabel 1500 3300 0    50   Input ~ 0
MCODE_0
Text HLabel 9500 1000 2    50   Output ~ 0
IP_IN
Text HLabel 9500 1100 2    50   Output ~ 0
IR_IN
Text HLabel 9500 1200 2    50   Output ~ 0
A_IN
Text HLabel 9500 1300 2    50   Output ~ 0
B_IN
Text HLabel 9500 1400 2    50   Output ~ 0
C_IN
Text HLabel 9500 1500 2    50   Output ~ 0
D_IN
Text HLabel 9500 1600 2    50   Output ~ 0
P_IN
Text HLabel 9500 1700 2    50   Output ~ 0
SRAM_IN
Text HLabel 9500 1800 2    50   Output ~ 0
FLAGS_IN
Text HLabel 4700 6550 2    50   Output ~ 0
IMM_4_OUT
Text HLabel 9500 2100 2    50   Output ~ 0
ALU_LOW_OUT
Text HLabel 9500 2000 2    50   Output ~ 0
ALU_OUT
Text HLabel 9500 3500 2    50   Output ~ 0
PC_SWAP
Text HLabel 9150 4650 2    50   Output ~ 0
ALU_SRC_A
Text HLabel 9150 4750 2    50   Output ~ 0
ALU_SRC_IP
Text HLabel 9150 4850 2    50   Output ~ 0
ALU_SRC_PC
Text HLabel 6150 5550 2    50   Output ~ 0
ADDR_SRC_IP
Text HLabel 6150 5650 2    50   Output ~ 0
ADDR_SRC_PC
Text HLabel 10150 5650 2    50   Output ~ 0
CARRY_CLEAR
Text HLabel 8150 5650 2    50   Output ~ 0
CARRY_SET
Text HLabel 8150 5750 2    50   Output ~ 0
CARRY_FROM_FLAGS
Text HLabel 9500 3000 2    50   Output ~ 0
ALU_OP_2
Text HLabel 9500 3100 2    50   Output ~ 0
ALU_OP_1
Text HLabel 9500 3200 2    50   Output ~ 0
ALU_OP_0
$Sheet
S 5500 5500 500  500 
U 5ED9FCFC
F0 "Address Src Select" 50
F1 "AddrSrcSel.sch" 50
F2 "EN" I L 5500 5550 50 
F3 "SEL" I L 5500 5750 50 
F4 "EN1" O R 6000 5550 50 
F5 "EN2" O R 6000 5650 50 
$EndSheet
Wire Wire Line
	6000 5550 6150 5550
Wire Wire Line
	6150 5650 6000 5650
$Sheet
S 8500 4500 500  500 
U 5EDAD6F9
F0 "ALU Src Select" 50
F1 "ALUSrcSel.sch" 50
F2 "EN" I L 8500 4550 50 
F3 "D0" I L 8500 4850 50 
F4 "D1" I L 8500 4750 50 
F5 "EN1" O R 9000 4550 50 
F6 "EN2" O R 9000 4650 50 
F7 "EN3" O R 9000 4750 50 
F8 "EN4" O R 9000 4850 50 
$EndSheet
Wire Wire Line
	9000 4650 9150 4650
Wire Wire Line
	9000 4750 9150 4750
Wire Wire Line
	9000 4850 9150 4850
NoConn ~ 9150 4550
Wire Wire Line
	9000 4550 9150 4550
$Sheet
S 7500 5500 500  500 
U 5EDCBD0D
F0 "Carry Src Select" 50
F1 "CarrySrcSel.sch" 50
F2 "EN" I L 7500 5550 50 
F3 "D0" I L 7500 5850 50 
F4 "D1" I L 7500 5750 50 
F5 "EN1" O R 8000 5550 50 
F6 "EN2" O R 8000 5650 50 
F7 "EN3" O R 8000 5750 50 
F8 "EN4" O R 8000 5850 50 
$EndSheet
Wire Wire Line
	8000 5650 8150 5650
Wire Wire Line
	8000 5750 8150 5750
$Sheet
S 9500 5500 500  300 
U 5EDCD804
F0 "Carry Or" 50
F1 "CarryOr.sch" 50
F2 "A" I L 9500 5550 50 
F3 "B" I L 9500 5750 50 
F4 "OUT" O R 10000 5650 50 
$EndSheet
Wire Wire Line
	10000 5650 10150 5650
Wire Wire Line
	8000 5550 9500 5550
Wire Wire Line
	8000 5850 9300 5850
Wire Wire Line
	9300 5850 9300 5750
Wire Wire Line
	9300 5750 9500 5750
Text HLabel 9500 3600 2    50   Output ~ 0
MCODE_RST
$Comp
L power:VCC #PWR?
U 1 1 5E7CCB8B
P 7350 5550
F 0 "#PWR?" H 7350 5400 50  0001 C CNN
F 1 "VCC" H 7367 5723 50  0000 C CNN
F 2 "" H 7350 5550 50  0001 C CNN
F 3 "" H 7350 5550 50  0001 C CNN
	1    7350 5550
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E7CD19A
P 5350 5550
F 0 "#PWR?" H 5350 5400 50  0001 C CNN
F 1 "VCC" H 5367 5723 50  0000 C CNN
F 2 "" H 5350 5550 50  0001 C CNN
F 3 "" H 5350 5550 50  0001 C CNN
	1    5350 5550
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E7CD682
P 8350 4550
F 0 "#PWR?" H 8350 4400 50  0001 C CNN
F 1 "VCC" H 8367 4723 50  0000 C CNN
F 2 "" H 8350 4550 50  0001 C CNN
F 3 "" H 8350 4550 50  0001 C CNN
	1    8350 4550
	1    0    0    -1  
$EndComp
Wire Wire Line
	8350 4550 8500 4550
Wire Wire Line
	7350 5550 7500 5550
Wire Wire Line
	5350 5550 5500 5550
Text HLabel 9500 2200 2    50   Output ~ 0
A_OUT
Text HLabel 9500 2300 2    50   Output ~ 0
A_HIGH_OUT
Text HLabel 9500 2400 2    50   Output ~ 0
D_OUT
Text HLabel 9500 2500 2    50   Output ~ 0
D_HIGH_OUT
Text HLabel 4700 6750 2    50   Output ~ 0
Z_OUT
Text HLabel 9500 2600 2    50   Output ~ 0
SRAM_OUT
Text HLabel 9500 2700 2    50   Output ~ 0
FLAGS_OUT
Text HLabel 4700 6650 2    50   Output ~ 0
IMM_6_OUT
$Sheet
S 4000 6500 500  500 
U 5E860CF4
F0 "Immediate Source Select" 50
F1 "ImmSrcSel.sch" 50
F2 "EN" I L 4000 6550 50 
F3 "D0" I L 4000 6750 50 
F4 "D1" I L 4000 6850 50 
F5 "EN1" O R 4500 6550 50 
F6 "EN2" O R 4500 6650 50 
F7 "EN3" O R 4500 6750 50 
F8 "EN4" O R 4500 6850 50 
$EndSheet
NoConn ~ 4700 6850
Wire Wire Line
	4500 6850 4700 6850
Wire Wire Line
	4700 6750 4500 6750
Wire Wire Line
	4500 6650 4700 6650
Wire Wire Line
	4700 6550 4500 6550
$Comp
L power:VCC #PWR?
U 1 1 5E862AA8
P 3850 6550
F 0 "#PWR?" H 3850 6400 50  0001 C CNN
F 1 "VCC" H 3867 6723 50  0000 C CNN
F 2 "" H 3850 6550 50  0001 C CNN
F 3 "" H 3850 6550 50  0001 C CNN
	1    3850 6550
	1    0    0    -1  
$EndComp
Wire Wire Line
	3850 6550 4000 6550
$EndSCHEMATC
