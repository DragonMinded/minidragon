EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 2 374
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text GLabel 1550 1000 0    50   Input ~ 0
SYS_CLK
Text GLabel 1550 1200 0    50   Input ~ 0
SYS_RST
Wire Wire Line
	1550 1000 2000 1000
Wire Wire Line
	2000 1000 2000 1550
Wire Wire Line
	2000 1550 2050 1550
Wire Wire Line
	2000 1550 2000 2550
Wire Wire Line
	2000 2550 2050 2550
Connection ~ 2000 1550
Wire Wire Line
	2000 2550 2000 3550
Wire Wire Line
	2000 3550 2050 3550
Connection ~ 2000 2550
Wire Wire Line
	2050 1750 1950 1750
Wire Wire Line
	1950 1750 1950 1200
Wire Wire Line
	1950 1200 1550 1200
Wire Wire Line
	1950 1750 1950 2850
Wire Wire Line
	1950 2850 2050 2850
Connection ~ 1950 1750
Wire Wire Line
	1950 2850 1950 3850
Wire Wire Line
	1950 3850 2050 3850
Connection ~ 1950 2850
Text HLabel 1550 2750 0    50   Input ~ 0
CARRY_RES
Text HLabel 1550 3750 0    50   Input ~ 0
ZERO_RES
Wire Wire Line
	1550 2750 2050 2750
Wire Wire Line
	1550 3750 2050 3750
Text HLabel 3050 1550 2    50   Output ~ 0
PCF
Text HLabel 3050 2550 2    50   Output ~ 0
CF
Text HLabel 3050 3550 2    50   Output ~ 0
ZF
Wire Wire Line
	2550 1550 3050 1550
Wire Wire Line
	2550 2550 2850 2550
Wire Wire Line
	2550 3550 2850 3550
Text HLabel 6500 3950 0    50   Input ~ 0
CS_FLAGS_OUT
Wire Wire Line
	6500 3950 7000 3950
Text HLabel 1550 1650 0    50   Input ~ 0
CS_PC_SWAP
Text HLabel 1550 2650 0    50   Input ~ 0
CS_FLAGS_IN
Wire Wire Line
	1550 2650 1900 2650
Wire Wire Line
	1550 1650 2050 1650
Wire Wire Line
	2050 3650 1900 3650
Wire Wire Line
	1900 3650 1900 2650
Connection ~ 1900 2650
Wire Wire Line
	1900 2650 2050 2650
$Comp
L power:GND #PWR0137
U 1 1 5E5F5285
P 6900 3750
F 0 "#PWR0137" H 6900 3500 50  0001 C CNN
F 1 "GND" H 6905 3577 50  0000 C CNN
F 2 "" H 6900 3750 50  0001 C CNN
F 3 "" H 6900 3750 50  0001 C CNN
	1    6900 3750
	1    0    0    -1  
$EndComp
Wire Wire Line
	7000 3750 6900 3750
Wire Wire Line
	6900 3750 6900 3650
Wire Wire Line
	6900 3650 7000 3650
Connection ~ 6900 3750
Wire Wire Line
	7000 3550 6900 3550
Wire Wire Line
	6900 3550 6900 3650
Connection ~ 6900 3650
Wire Wire Line
	6900 3550 6900 3450
Wire Wire Line
	6900 3450 7000 3450
Connection ~ 6900 3550
Wire Wire Line
	7000 3350 6900 3350
Wire Wire Line
	6900 3350 6900 3450
Connection ~ 6900 3450
Wire Wire Line
	6900 3350 6900 3250
Wire Wire Line
	6900 3250 7000 3250
Connection ~ 6900 3350
Wire Wire Line
	7000 3150 6900 3150
Wire Wire Line
	6900 3150 6900 3250
Connection ~ 6900 3250
Text HLabel 5100 3450 0    50   Input ~ 0
INS_0
Text HLabel 2900 2900 0    50   Input ~ 0
INS_1
Text HLabel 2850 3900 0    50   Input ~ 0
INS_2
Wire Wire Line
	3050 2800 2850 2800
Wire Wire Line
	2850 2800 2850 2550
Connection ~ 2850 2550
Wire Wire Line
	2850 2550 3050 2550
Wire Wire Line
	2900 2900 3050 2900
Wire Wire Line
	2850 3550 2850 3800
Wire Wire Line
	2850 3800 3050 3800
Connection ~ 2850 3550
Wire Wire Line
	2850 3550 3050 3550
Wire Wire Line
	3050 3900 2850 3900
Wire Wire Line
	3550 2850 3950 2850
Wire Wire Line
	3950 2850 3950 3350
Wire Wire Line
	3950 3350 4050 3350
Wire Wire Line
	3550 3850 3950 3850
Wire Wire Line
	3950 3850 3950 3450
Wire Wire Line
	3950 3450 4050 3450
Wire Wire Line
	5100 3450 5250 3450
Wire Wire Line
	4550 3400 4700 3400
Wire Wire Line
	4700 3400 4700 3350
Wire Wire Line
	4700 3350 5250 3350
Wire Wire Line
	7000 3050 6500 3050
Wire Wire Line
	6500 3050 6500 3400
Wire Wire Line
	6500 3400 5750 3400
Text HLabel 8000 3750 2    50   BiDi ~ 0
BUS_8
Text HLabel 8000 3650 2    50   BiDi ~ 0
BUS_7
Text HLabel 8000 3550 2    50   BiDi ~ 0
BUS_6
Text HLabel 8000 3450 2    50   BiDi ~ 0
BUS_5
Text HLabel 8000 3350 2    50   BiDi ~ 0
BUS_4
Text HLabel 8000 3250 2    50   BiDi ~ 0
BUS_3
Text HLabel 8000 3150 2    50   BiDi ~ 0
BUS_2
Text HLabel 8000 3050 2    50   BiDi ~ 0
BUS_1
Wire Wire Line
	7500 3050 8000 3050
Wire Wire Line
	7500 3150 8000 3150
Wire Wire Line
	7500 3250 8000 3250
Wire Wire Line
	7500 3350 8000 3350
Wire Wire Line
	7500 3450 8000 3450
Wire Wire Line
	7500 3550 8000 3550
Wire Wire Line
	7500 3650 8000 3650
Wire Wire Line
	7500 3750 8000 3750
$Sheet
S 2050 1500 500  500 
U 5E5D6176
F0 "PC Sel" 50
F1 "PCSel.sch" 50
F2 "CLK" I L 2050 1550 50 
F3 "EN" I L 2050 1650 50 
F4 "RST" I L 2050 1750 50 
F5 "OUT" O R 2550 1550 50 
$EndSheet
$Sheet
S 2050 2500 500  500 
U 5E5E8D9B
F0 "Carry" 50
F1 "Carry.sch" 50
F2 "CLK" I L 2050 2550 50 
F3 "EN" I L 2050 2650 50 
F4 "D" I L 2050 2750 50 
F5 "RST" I L 2050 2850 50 
F6 "OUT" O R 2550 2550 50 
$EndSheet
$Sheet
S 2050 3500 500  500 
U 5E5E905D
F0 "Zero" 50
F1 "Zero.sch" 50
F2 "CLK" I L 2050 3550 50 
F3 "EN" I L 2050 3650 50 
F4 "D" I L 2050 3750 50 
F5 "RST" I L 2050 3850 50 
F6 "OUT" O R 2550 3550 50 
$EndSheet
$Sheet
S 3050 2750 500  200 
U 5E5F8488
F0 "NAND 1" 50
F1 "FlagsNand1.sch" 50
F2 "A" I L 3050 2800 50 
F3 "B" I L 3050 2900 50 
F4 "OUT" O R 3550 2850 50 
$EndSheet
$Sheet
S 3050 3750 500  200 
U 5E5FA72C
F0 "NAND 2" 50
F1 "FlagsNand2.sch" 50
F2 "A" I L 3050 3800 50 
F3 "B" I L 3050 3900 50 
F4 "OUT" O R 3550 3850 50 
$EndSheet
$Sheet
S 4050 3300 500  200 
U 5E601697
F0 "NAND 3" 50
F1 "FlagsNand3.sch" 50
F2 "A" I L 4050 3350 50 
F3 "B" I L 4050 3450 50 
F4 "OUT" O R 4550 3400 50 
$EndSheet
$Sheet
S 5250 3300 500  200 
U 5E6074DF
F0 "XOR" 50
F1 "FlagsXor1.sch" 50
F2 "A" I L 5250 3350 50 
F3 "B" I L 5250 3450 50 
F4 "OUT" O R 5750 3400 50 
$EndSheet
$Sheet
S 7000 3000 500  1000
U 5E5E2C07
F0 "Bus Output" 50
F1 "FlagsBusOutputLower.sch" 50
F2 "EN" I L 7000 3950 50 
F3 "D1" I L 7000 3050 50 
F4 "D2" I L 7000 3150 50 
F5 "D3" I L 7000 3250 50 
F6 "D4" I L 7000 3350 50 
F7 "D5" I L 7000 3450 50 
F8 "D6" I L 7000 3550 50 
F9 "D7" I L 7000 3650 50 
F10 "D8" I L 7000 3750 50 
F11 "Q8" O R 7500 3750 50 
F12 "Q7" O R 7500 3650 50 
F13 "Q6" O R 7500 3550 50 
F14 "Q5" O R 7500 3450 50 
F15 "Q4" O R 7500 3350 50 
F16 "Q3" O R 7500 3250 50 
F17 "Q2" O R 7500 3150 50 
F18 "Q1" O R 7500 3050 50 
$EndSheet
$EndSCHEMATC
