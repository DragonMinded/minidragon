EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 448 479
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text HLabel 3750 1350 2    50   BiDi ~ 0
D3
Text HLabel 3750 1250 2    50   BiDi ~ 0
D2
Text HLabel 3750 1150 2    50   BiDi ~ 0
D1
Text HLabel 3750 1050 2    50   BiDi ~ 0
D0
Text HLabel 3750 1750 2    50   BiDi ~ 0
D7
Text HLabel 3750 1650 2    50   BiDi ~ 0
D6
Text HLabel 3750 1550 2    50   BiDi ~ 0
D5
Text HLabel 3750 1450 2    50   BiDi ~ 0
D4
Text HLabel 3750 2150 2    50   BiDi ~ 0
D11
Text HLabel 3750 2050 2    50   BiDi ~ 0
D10
Text HLabel 3750 1950 2    50   BiDi ~ 0
D9
Text HLabel 3750 1850 2    50   BiDi ~ 0
D8
Text HLabel 3750 2550 2    50   BiDi ~ 0
D15
Text HLabel 3750 2450 2    50   BiDi ~ 0
D14
Text HLabel 3750 2350 2    50   BiDi ~ 0
D13
Text HLabel 3750 2250 2    50   BiDi ~ 0
D12
Text HLabel 3750 2950 2    50   BiDi ~ 0
D19
Text HLabel 3750 2850 2    50   BiDi ~ 0
D18
Text HLabel 3750 2750 2    50   BiDi ~ 0
D17
Text HLabel 3750 2650 2    50   BiDi ~ 0
D16
Text HLabel 3750 3350 2    50   BiDi ~ 0
D23
Text HLabel 3750 3250 2    50   BiDi ~ 0
D22
Text HLabel 3750 3150 2    50   BiDi ~ 0
D21
Text HLabel 3750 3050 2    50   BiDi ~ 0
D20
Text HLabel 3750 3750 2    50   BiDi ~ 0
D27
Text HLabel 3750 3650 2    50   BiDi ~ 0
D26
Text HLabel 3750 3550 2    50   BiDi ~ 0
D25
Text HLabel 3750 3450 2    50   BiDi ~ 0
D24
Text HLabel 3750 4150 2    50   BiDi ~ 0
D31
Text HLabel 3750 4050 2    50   BiDi ~ 0
D30
Text HLabel 3750 3950 2    50   BiDi ~ 0
D29
Text HLabel 3750 3850 2    50   BiDi ~ 0
D28
Wire Wire Line
	3500 1050 3750 1050
Wire Wire Line
	3750 1150 3500 1150
Wire Wire Line
	3500 1250 3750 1250
Wire Wire Line
	3750 1350 3500 1350
Wire Wire Line
	3500 1450 3750 1450
Wire Wire Line
	3750 1550 3500 1550
Wire Wire Line
	3500 1650 3750 1650
Wire Wire Line
	3750 1750 3500 1750
Wire Wire Line
	3500 1850 3750 1850
Wire Wire Line
	3750 1950 3500 1950
Wire Wire Line
	3500 2050 3750 2050
Wire Wire Line
	3750 2150 3500 2150
Wire Wire Line
	3500 2250 3750 2250
Wire Wire Line
	3750 2350 3500 2350
Wire Wire Line
	3500 2450 3750 2450
Wire Wire Line
	3750 2550 3500 2550
Wire Wire Line
	3500 2650 3750 2650
Wire Wire Line
	3750 2750 3500 2750
Wire Wire Line
	3500 2850 3750 2850
Wire Wire Line
	3750 2950 3500 2950
Wire Wire Line
	3500 3050 3750 3050
Wire Wire Line
	3750 3150 3500 3150
Wire Wire Line
	3500 3250 3750 3250
Wire Wire Line
	3750 3350 3500 3350
Wire Wire Line
	3500 3450 3750 3450
Wire Wire Line
	3750 3550 3500 3550
Wire Wire Line
	3500 3650 3750 3650
Wire Wire Line
	3750 3750 3500 3750
Wire Wire Line
	3500 3850 3750 3850
Wire Wire Line
	3750 3950 3500 3950
Wire Wire Line
	3500 4050 3750 4050
Wire Wire Line
	3750 4150 3500 4150
Text HLabel 1000 1050 0    50   Input ~ 0
EN
Text HLabel 1000 1250 0    50   Input ~ 0
MCODE0
Text HLabel 1000 1350 0    50   Input ~ 0
MCODE1
Text HLabel 1000 1450 0    50   Input ~ 0
MCODE2
Text HLabel 1000 1550 0    50   Input ~ 0
MCODE3
Wire Wire Line
	1000 1250 2500 1250
Wire Wire Line
	1000 1350 2500 1350
Wire Wire Line
	1000 1050 2500 1050
Wire Wire Line
	1000 1450 1150 1450
Wire Wire Line
	1000 1550 1150 1550
NoConn ~ 1150 1450
NoConn ~ 1150 1550
Text Notes 1000 900  0    50   ~ 0
LOADI Instruction has:\n - 3 microcode entries.\n - 1 terminate early entry.
$Sheet
S 2500 1000 1000 3500
U 5F666EEC
F0 "LOADI ROM 1" 50
F1 "LOADIROM1.sch" 50
F2 "EN" I L 2500 1050 50 
F3 "A0" I L 2500 1250 50 
F4 "A1" I L 2500 1350 50 
F5 "D3" B R 3500 1350 50 
F6 "D2" B R 3500 1250 50 
F7 "D1" B R 3500 1150 50 
F8 "D0" B R 3500 1050 50 
F9 "D7" B R 3500 1750 50 
F10 "D6" B R 3500 1650 50 
F11 "D5" B R 3500 1550 50 
F12 "D4" B R 3500 1450 50 
F13 "D11" B R 3500 2150 50 
F14 "D10" B R 3500 2050 50 
F15 "D9" B R 3500 1950 50 
F16 "D8" B R 3500 1850 50 
F17 "D15" B R 3500 2550 50 
F18 "D14" B R 3500 2450 50 
F19 "D13" B R 3500 2350 50 
F20 "D12" B R 3500 2250 50 
F21 "D19" B R 3500 2950 50 
F22 "D18" B R 3500 2850 50 
F23 "D17" B R 3500 2750 50 
F24 "D16" B R 3500 2650 50 
F25 "D23" B R 3500 3350 50 
F26 "D22" B R 3500 3250 50 
F27 "D21" B R 3500 3150 50 
F28 "D20" B R 3500 3050 50 
F29 "D27" B R 3500 3750 50 
F30 "D26" B R 3500 3650 50 
F31 "D25" B R 3500 3550 50 
F32 "D24" B R 3500 3450 50 
F33 "D31" B R 3500 4150 50 
F34 "D30" B R 3500 4050 50 
F35 "D29" B R 3500 3950 50 
F36 "D28" B R 3500 3850 50 
$EndSheet
$EndSCHEMATC
