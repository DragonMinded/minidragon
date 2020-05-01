EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 49 484
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Wire Wire Line
	1500 3200 1650 3200
Text HLabel 1500 5000 0    50   Input ~ 0
~MCODE_RST
Connection ~ 3950 2950
Wire Wire Line
	3500 2950 3950 2950
Wire Wire Line
	3500 3100 3500 2950
Wire Wire Line
	2200 3100 3500 3100
Wire Wire Line
	1500 3000 1650 3000
$Sheet
S 1650 2950 550  300 
U 5E7B6B6E
F0 "Reset Combiner Or" 50
F1 "MicrocodeOr1.sch" 50
F2 "A" I L 1650 3000 50 
F3 "B" I L 1650 3200 50 
F4 "OUT" O R 2200 3100 50 
$EndSheet
Wire Wire Line
	3750 5650 4000 5650
Wire Wire Line
	3750 5250 3750 5650
Wire Wire Line
	6500 5250 3750 5250
Wire Wire Line
	6500 4850 6500 5250
Wire Wire Line
	6050 4850 6500 4850
Wire Wire Line
	5350 4200 3750 4200
Connection ~ 5350 4200
Wire Wire Line
	5350 4950 5500 4950
Wire Wire Line
	5350 4200 5350 4950
Wire Wire Line
	4550 4550 4650 4550
Connection ~ 4550 4550
Wire Wire Line
	4550 4750 4550 4550
Wire Wire Line
	5500 4750 4550 4750
$Sheet
S 5500 4700 550  300 
U 5E62A307
F0 "AND 3" 50
F1 "MicrocodeAnd3.sch" 50
F2 "Q" O R 6050 4850 50 
F3 "A" I L 5500 4750 50 
F4 "B" I L 5500 4950 50 
$EndSheet
Wire Wire Line
	3750 4650 4000 4650
Wire Wire Line
	3750 4200 3750 4650
Wire Wire Line
	6500 4200 5350 4200
Wire Wire Line
	6500 3800 6500 4200
Wire Wire Line
	6000 3800 6500 3800
Wire Wire Line
	5350 3900 5450 3900
Wire Wire Line
	5350 3300 5350 3900
Wire Wire Line
	4550 3700 5450 3700
Wire Wire Line
	4550 3550 4650 3550
Connection ~ 4550 3550
Wire Wire Line
	4550 3550 4550 3700
Wire Wire Line
	3750 3300 5350 3300
Wire Wire Line
	3750 3650 3750 3300
Wire Wire Line
	4000 3650 3750 3650
Wire Wire Line
	4550 2550 4650 2550
Connection ~ 4550 2550
Wire Wire Line
	4550 2550 4550 2900
Wire Wire Line
	3750 2650 4000 2650
$Sheet
S 5450 3650 550  300 
U 5E621FBF
F0 "AND 2" 50
F1 "MicrocodeAnd2.sch" 50
F2 "Q" O R 6000 3800 50 
F3 "A" I L 5450 3700 50 
F4 "B" I L 5450 3900 50 
$EndSheet
Wire Wire Line
	4500 2550 4550 2550
Wire Wire Line
	4500 3550 4550 3550
Wire Wire Line
	4500 4550 4550 4550
Wire Wire Line
	4500 5550 4650 5550
Text HLabel 4650 5550 2    50   Output ~ 0
Q3
Text HLabel 4650 4550 2    50   Output ~ 0
Q2
Text HLabel 4650 3550 2    50   Output ~ 0
Q1
Text HLabel 4650 2550 2    50   Output ~ 0
Q0
Connection ~ 3950 4950
Wire Wire Line
	3950 5950 4000 5950
Wire Wire Line
	3950 4950 3950 5950
Connection ~ 3950 3950
Wire Wire Line
	3950 4950 4000 4950
Wire Wire Line
	3950 3950 3950 4950
Wire Wire Line
	3950 2950 4000 2950
Wire Wire Line
	3950 3950 4000 3950
Wire Wire Line
	3950 2950 3950 3950
Text GLabel 1500 3000 0    50   Input ~ 0
SYS_RST
Connection ~ 3000 4550
Wire Wire Line
	3000 5550 3000 4550
Wire Wire Line
	4000 5550 3000 5550
Connection ~ 3000 3550
Wire Wire Line
	3000 4550 3000 3550
Wire Wire Line
	4000 4550 3000 4550
Connection ~ 3000 2600
Wire Wire Line
	3000 3550 4000 3550
Wire Wire Line
	3000 2600 3000 3550
Wire Wire Line
	3000 2550 4000 2550
Wire Wire Line
	3000 2600 3000 2550
Wire Wire Line
	2200 2600 3000 2600
Wire Wire Line
	1500 2600 1650 2600
$Sheet
S 1650 2500 550  200 
U 5E6109D7
F0 "Clock Inverter Not" 50
F1 "MicrocodeClockInverter.sch" 50
F2 "D" I L 1650 2600 50 
F3 "Q" O R 2200 2600 50 
$EndSheet
Text GLabel 1500 2600 0    50   Input ~ 0
SYS_CLK
$Sheet
S 4000 2500 500  500 
U 5E6032DD
F0 "Microcode Counter Bit 0" 50
F1 "CounterBit0.sch" 50
F2 "CLK" I L 4000 2550 50 
F3 "EN" I L 4000 2650 50 
F4 "RST" I L 4000 2950 50 
F5 "OUT" O R 4500 2550 50 
$EndSheet
$Sheet
S 4000 3500 500  500 
U 5E60A4DF
F0 "Microcode Counter Bit 1" 50
F1 "CounterBit1.sch" 50
F2 "CLK" I L 4000 3550 50 
F3 "EN" I L 4000 3650 50 
F4 "RST" I L 4000 3950 50 
F5 "OUT" O R 4500 3550 50 
$EndSheet
$Sheet
S 4000 4500 500  500 
U 5E60A7F3
F0 "Microcode Counter Bit 2" 50
F1 "CounterBit2.sch" 50
F2 "CLK" I L 4000 4550 50 
F3 "EN" I L 4000 4650 50 
F4 "RST" I L 4000 4950 50 
F5 "OUT" O R 4500 4550 50 
$EndSheet
$Sheet
S 4000 5500 500  500 
U 5E60AAF1
F0 "Microcode Counter Bit 3" 50
F1 "CounterBit3.sch" 50
F2 "CLK" I L 4000 5550 50 
F3 "EN" I L 4000 5650 50 
F4 "RST" I L 4000 5950 50 
F5 "OUT" O R 4500 5550 50 
$EndSheet
Wire Wire Line
	4550 2900 4950 2900
Wire Wire Line
	6000 3000 5500 3000
Wire Wire Line
	6000 3300 6000 3000
Connection ~ 5350 3300
Wire Wire Line
	5350 3300 6000 3300
Wire Wire Line
	3750 3100 4950 3100
$Sheet
S 4950 2850 550  300 
U 5E61EAAB
F0 "AND 1" 50
F1 "MicrocodeAnd1.sch" 50
F2 "Q" O R 5500 3000 50 
F3 "A" I L 4950 2900 50 
F4 "B" I L 4950 3100 50 
$EndSheet
Wire Wire Line
	3750 2650 3750 3100
$Sheet
S 4000 1500 500  500 
U 5E96BB99
F0 "Load Instruction Counter" 50
F1 "LoadInstructionCounter.sch" 50
F2 "CLK" I L 4000 1550 50 
F3 "EN" I L 4000 1650 50 
F4 "D" I L 4000 1850 50 
F5 "RST" I L 4000 1950 50 
F6 "OUT" O R 4500 1550 50 
$EndSheet
Wire Wire Line
	3000 2550 3000 1550
Wire Wire Line
	3000 1550 4000 1550
Connection ~ 3000 2550
$Comp
L power:VCC #PWR?
U 1 1 5E96D1B4
P 3750 1350
F 0 "#PWR?" H 3750 1200 50  0001 C CNN
F 1 "VCC" H 3767 1523 50  0000 C CNN
F 2 "" H 3750 1350 50  0001 C CNN
F 3 "" H 3750 1350 50  0001 C CNN
	1    3750 1350
	1    0    0    -1  
$EndComp
Wire Wire Line
	3750 1350 3750 1650
Wire Wire Line
	3750 1650 4000 1650
Wire Wire Line
	3750 1650 3750 1850
Wire Wire Line
	3750 1850 4000 1850
Connection ~ 3750 1650
Wire Wire Line
	3500 2950 3500 1950
Wire Wire Line
	3500 1950 4000 1950
Connection ~ 3500 2950
Wire Wire Line
	5500 1550 5500 2250
Wire Wire Line
	5500 2250 3750 2250
Wire Wire Line
	3750 2250 3750 2650
Connection ~ 3750 2650
Wire Wire Line
	4500 1550 5500 1550
Text HLabel 5600 1550 2    50   Output ~ 0
~ILOAD
Wire Wire Line
	5500 1550 5600 1550
Connection ~ 5500 1550
$Sheet
S 1900 4250 200  550 
U 620B502D
F0 "Reset Inverter Not" 50
F1 "MicrocodeResetInverter.sch" 50
F2 "D" I B 2000 4800 50 
F3 "Q" O T 2000 4250 50 
$EndSheet
Wire Wire Line
	1500 5000 2000 5000
Wire Wire Line
	2000 5000 2000 4800
Wire Wire Line
	2000 4250 2000 3500
Wire Wire Line
	2000 3500 1500 3500
Wire Wire Line
	1500 3500 1500 3200
$EndSCHEMATC
