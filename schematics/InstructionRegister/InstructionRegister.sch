EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 17 374
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text GLabel 1000 1050 0    50   Input ~ 0
SYS_CLK
Text GLabel 1000 1950 0    50   Input ~ 0
SYS_RST
Wire Wire Line
	1000 1050 1400 1050
Wire Wire Line
	1000 1950 1450 1950
Wire Wire Line
	1450 1950 1450 3450
Wire Wire Line
	1450 3450 1500 3450
Connection ~ 1450 1950
Wire Wire Line
	1450 1950 1500 1950
Wire Wire Line
	1500 2550 1400 2550
Wire Wire Line
	1400 2550 1400 1050
Connection ~ 1400 1050
Wire Wire Line
	1400 1050 1500 1050
Text HLabel 1000 1150 0    50   Input ~ 0
IR_IN
Wire Wire Line
	1000 1150 1350 1150
Wire Wire Line
	1350 1150 1350 2650
Wire Wire Line
	1350 2650 1500 2650
Connection ~ 1350 1150
Wire Wire Line
	1350 1150 1500 1150
Text HLabel 1000 1450 0    50   BiDi ~ 0
BUS_8
Text HLabel 1000 1550 0    50   BiDi ~ 0
BUS_7
Text HLabel 1000 1650 0    50   BiDi ~ 0
BUS_6
Text HLabel 1000 1750 0    50   BiDi ~ 0
BUS_5
Text HLabel 1000 2950 0    50   BiDi ~ 0
BUS_4
Text HLabel 1000 3050 0    50   BiDi ~ 0
BUS_3
Text HLabel 1000 3150 0    50   BiDi ~ 0
BUS_2
Text HLabel 1000 3250 0    50   BiDi ~ 0
BUS_1
Wire Wire Line
	1000 3250 1500 3250
Wire Wire Line
	1500 3150 1000 3150
Wire Wire Line
	1000 3050 1500 3050
Wire Wire Line
	1500 2950 1000 2950
Wire Wire Line
	1000 1750 1500 1750
Wire Wire Line
	1500 1650 1000 1650
Wire Wire Line
	1000 1550 1500 1550
Wire Wire Line
	1500 1450 1000 1450
Text HLabel 2500 1050 2    50   Output ~ 0
INS_7
Text HLabel 2500 1150 2    50   Output ~ 0
INS_6
Text HLabel 2500 1250 2    50   Output ~ 0
INS_5
Text HLabel 2500 1350 2    50   Output ~ 0
INS_4
Text HLabel 2500 2550 2    50   Output ~ 0
INS_3
Text HLabel 2500 2650 2    50   Output ~ 0
INS_2
Text HLabel 2500 2750 2    50   Output ~ 0
INS_1
Text HLabel 2500 2850 2    50   Output ~ 0
INS_0
Wire Wire Line
	2000 1050 2500 1050
Wire Wire Line
	2500 1150 2000 1150
Wire Wire Line
	2000 1250 2500 1250
Wire Wire Line
	2500 1350 2000 1350
Wire Wire Line
	2050 2550 2500 2550
Wire Wire Line
	2500 2650 2050 2650
Wire Wire Line
	2050 2750 2500 2750
Wire Wire Line
	2500 2850 2050 2850
$Sheet
S 1500 1000 500  1000
U 5E5D9419
F0 "Instruction Register Upper Bits" 50
F1 "UpperBits/4BitRegister.sch" 50
F2 "CLK" I L 1500 1050 50 
F3 "EN" I L 1500 1150 50 
F4 "D1" I L 1500 1750 50 
F5 "D2" I L 1500 1650 50 
F6 "D3" I L 1500 1550 50 
F7 "D4" I L 1500 1450 50 
F8 "RST" I L 1500 1950 50 
F9 "Q1" O R 2000 1350 50 
F10 "Q2" O R 2000 1250 50 
F11 "Q3" O R 2000 1150 50 
F12 "Q4" O R 2000 1050 50 
$EndSheet
$Sheet
S 1500 2500 550  1000
U 5E62B79C
F0 "Instruction Register Lower Bits" 50
F1 "LowerBits/4BitRegister.sch" 50
F2 "CLK" I L 1500 2550 50 
F3 "EN" I L 1500 2650 50 
F4 "D1" I L 1500 3250 50 
F5 "D2" I L 1500 3150 50 
F6 "D3" I L 1500 3050 50 
F7 "D4" I L 1500 2950 50 
F8 "RST" I L 1500 3450 50 
F9 "Q1" O R 2050 2850 50 
F10 "Q2" O R 2050 2750 50 
F11 "Q3" O R 2050 2650 50 
F12 "Q4" O R 2050 2550 50 
$EndSheet
$EndSCHEMATC
