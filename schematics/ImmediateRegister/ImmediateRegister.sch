EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 125 372
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Sheet
S 2500 1500 500  1000
U 5E724688
F0 "Immediate Register Lower Bus Out" 50
F1 "ImmediateRegisterBusOutputLower.sch" 50
F2 "EN" I L 2500 2450 50 
F3 "D1" I L 2500 2250 50 
F4 "D2" I L 2500 2150 50 
F5 "D3" I L 2500 2050 50 
F6 "D4" I L 2500 1950 50 
F7 "D5" I L 2500 1850 50 
F8 "D6" I L 2500 1750 50 
F9 "D7" I L 2500 1650 50 
F10 "D8" I L 2500 1550 50 
F11 "Q8" O R 3000 1550 50 
F12 "Q7" O R 3000 1650 50 
F13 "Q6" O R 3000 1750 50 
F14 "Q5" O R 3000 1850 50 
F15 "Q4" O R 3000 1950 50 
F16 "Q3" O R 3000 2050 50 
F17 "Q2" O R 3000 2150 50 
F18 "Q1" O R 3000 2250 50 
$EndSheet
Text HLabel 2000 2450 0    50   Input ~ 0
IMM_OUT
Wire Wire Line
	2000 2450 2500 2450
Text HLabel 2000 1750 0    50   Input ~ 0
INS_5
Text HLabel 2000 1850 0    50   Input ~ 0
INS_4
Text HLabel 2000 1950 0    50   Input ~ 0
INS_3
Text HLabel 2000 2050 0    50   Input ~ 0
INS_2
Text HLabel 2000 2150 0    50   Input ~ 0
INS_1
Text HLabel 2000 2250 0    50   Input ~ 0
INS_0
Wire Wire Line
	2000 2250 2500 2250
Wire Wire Line
	2500 2150 2000 2150
Wire Wire Line
	2000 2050 2500 2050
Wire Wire Line
	2500 1950 2000 1950
Wire Wire Line
	2000 1850 2500 1850
Wire Wire Line
	2500 1750 2450 1750
Wire Wire Line
	2500 1650 2450 1650
Wire Wire Line
	2450 1650 2450 1750
Connection ~ 2450 1750
Wire Wire Line
	2450 1750 2400 1750
Wire Wire Line
	2500 1550 2400 1550
Wire Wire Line
	2400 1550 2400 1750
Connection ~ 2400 1750
Wire Wire Line
	2400 1750 2000 1750
Text HLabel 3150 1550 2    50   BiDi ~ 0
BUS_8
Text HLabel 3150 1650 2    50   BiDi ~ 0
BUS_7
Text HLabel 3150 1750 2    50   BiDi ~ 0
BUS_6
Text HLabel 3150 1850 2    50   BiDi ~ 0
BUS_5
Text HLabel 3150 1950 2    50   BiDi ~ 0
BUS_4
Text HLabel 3150 2050 2    50   BiDi ~ 0
BUS_3
Text HLabel 3150 2150 2    50   BiDi ~ 0
BUS_2
Text HLabel 3150 2250 2    50   BiDi ~ 0
BUS_1
Wire Wire Line
	3000 1550 3150 1550
Wire Wire Line
	3150 1650 3000 1650
Wire Wire Line
	3000 1750 3150 1750
Wire Wire Line
	3150 1850 3000 1850
Wire Wire Line
	3000 1950 3150 1950
Wire Wire Line
	3150 2050 3000 2050
Wire Wire Line
	3000 2150 3150 2150
Wire Wire Line
	3150 2250 3000 2250
$EndSCHEMATC
