EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 48 373
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
S 4000 4000 500  500 
U 5E60AAF1
F0 "Microcode Counter Bit 3" 50
F1 "CounterBit3.sch" 50
F2 "CLK" I L 4000 4050 50 
F3 "EN" I L 4000 4150 50 
F4 "RST" I L 4000 4450 50 
F5 "OUT" O R 4500 4050 50 
$EndSheet
Text HLabel 3500 1150 0    50   Input ~ 0
EN
$Sheet
S 4000 3000 500  500 
U 5E60A7F3
F0 "Microcode Counter Bit 2" 50
F1 "CounterBit2.sch" 50
F2 "CLK" I L 4000 3050 50 
F3 "EN" I L 4000 3150 50 
F4 "RST" I L 4000 3450 50 
F5 "OUT" O R 4500 3050 50 
$EndSheet
$Sheet
S 4000 2000 500  500 
U 5E60A4DF
F0 "Microcode Counter Bit 1" 50
F1 "CounterBit1.sch" 50
F2 "CLK" I L 4000 2050 50 
F3 "EN" I L 4000 2150 50 
F4 "RST" I L 4000 2450 50 
F5 "OUT" O R 4500 2050 50 
$EndSheet
$Sheet
S 4000 1000 500  500 
U 5E6032DD
F0 "Microcode Counter Bit 0" 50
F1 "CounterBit0.sch" 50
F2 "CLK" I L 4000 1050 50 
F3 "EN" I L 4000 1150 50 
F4 "RST" I L 4000 1450 50 
F5 "OUT" O R 4500 1050 50 
$EndSheet
Wire Wire Line
	3500 1150 3750 1150
Text GLabel 1500 1100 0    50   Input ~ 0
SYS_CLK
$Sheet
S 1650 1000 550  200 
U 5E6109D7
F0 "Clock Inverter Not" 50
F1 "MicrocodeClockInverter.sch" 50
F2 "D" I L 1650 1100 50 
F3 "Q" O R 2200 1100 50 
$EndSheet
Wire Wire Line
	1500 1100 1650 1100
Wire Wire Line
	2200 1100 3000 1100
Wire Wire Line
	3000 1100 3000 1050
Wire Wire Line
	3000 1050 4000 1050
Wire Wire Line
	3000 1100 3000 2050
Wire Wire Line
	3000 2050 4000 2050
Connection ~ 3000 1100
Wire Wire Line
	4000 3050 3000 3050
Wire Wire Line
	3000 3050 3000 2050
Connection ~ 3000 2050
Wire Wire Line
	4000 4050 3000 4050
Wire Wire Line
	3000 4050 3000 3050
Connection ~ 3000 3050
Text GLabel 1500 1500 0    50   Input ~ 0
SYS_RST
Wire Wire Line
	3950 1450 3950 2450
Wire Wire Line
	3950 2450 4000 2450
Wire Wire Line
	3950 1450 4000 1450
Wire Wire Line
	3950 2450 3950 3450
Wire Wire Line
	3950 3450 4000 3450
Connection ~ 3950 2450
Wire Wire Line
	3950 3450 3950 4450
Wire Wire Line
	3950 4450 4000 4450
Connection ~ 3950 3450
Text HLabel 4650 1050 2    50   Output ~ 0
Q0
Text HLabel 4650 2050 2    50   Output ~ 0
Q1
Text HLabel 4650 3050 2    50   Output ~ 0
Q2
Text HLabel 4650 4050 2    50   Output ~ 0
Q3
Wire Wire Line
	4500 4050 4650 4050
Wire Wire Line
	4500 3050 4550 3050
Wire Wire Line
	4500 2050 4550 2050
Wire Wire Line
	4500 1050 4550 1050
$Sheet
S 4950 1350 550  300 
U 5E61EAAB
F0 "AND 1" 50
F1 "MicrocodeAnd1.sch" 50
F2 "Q" O R 5500 1500 50 
F3 "A" I L 4950 1400 50 
F4 "B" I L 4950 1600 50 
$EndSheet
$Sheet
S 5450 2150 550  300 
U 5E621FBF
F0 "AND 2" 50
F1 "MicrocodeAnd2.sch" 50
F2 "Q" O R 6000 2300 50 
F3 "A" I L 5450 2200 50 
F4 "B" I L 5450 2400 50 
$EndSheet
Wire Wire Line
	3750 1150 3750 1600
Wire Wire Line
	3750 1600 4950 1600
Connection ~ 3750 1150
Wire Wire Line
	3750 1150 4000 1150
Wire Wire Line
	4550 1050 4550 1400
Wire Wire Line
	4550 1400 4950 1400
Connection ~ 4550 1050
Wire Wire Line
	4550 1050 4650 1050
Wire Wire Line
	4000 2150 3750 2150
Wire Wire Line
	3750 2150 3750 1800
Wire Wire Line
	3750 1800 5350 1800
Wire Wire Line
	6000 1800 6000 1500
Wire Wire Line
	6000 1500 5500 1500
Wire Wire Line
	4550 2050 4550 2200
Connection ~ 4550 2050
Wire Wire Line
	4550 2050 4650 2050
Wire Wire Line
	4550 2200 5450 2200
Wire Wire Line
	5350 1800 5350 2400
Wire Wire Line
	5350 2400 5450 2400
Connection ~ 5350 1800
Wire Wire Line
	5350 1800 6000 1800
Wire Wire Line
	6000 2300 6500 2300
Wire Wire Line
	6500 2300 6500 2700
Wire Wire Line
	6500 2700 5350 2700
Wire Wire Line
	3750 2700 3750 3150
Wire Wire Line
	3750 3150 4000 3150
$Sheet
S 5500 3200 550  300 
U 5E62A307
F0 "AND 3" 50
F1 "MicrocodeAnd3.sch" 50
F2 "Q" O R 6050 3350 50 
F3 "A" I L 5500 3250 50 
F4 "B" I L 5500 3450 50 
$EndSheet
Wire Wire Line
	5500 3250 4550 3250
Wire Wire Line
	4550 3250 4550 3050
Connection ~ 4550 3050
Wire Wire Line
	4550 3050 4650 3050
Wire Wire Line
	5350 2700 5350 3450
Wire Wire Line
	5350 3450 5500 3450
Connection ~ 5350 2700
Wire Wire Line
	5350 2700 3750 2700
Wire Wire Line
	6050 3350 6500 3350
Wire Wire Line
	6500 3350 6500 3750
Wire Wire Line
	6500 3750 3750 3750
Wire Wire Line
	3750 3750 3750 4150
Wire Wire Line
	3750 4150 4000 4150
$Sheet
S 1650 1450 550  300 
U 5E7B6B6E
F0 "Reset Combiner Or" 50
F1 "MicrocodeOr1.sch" 50
F2 "A" I L 1650 1500 50 
F3 "B" I L 1650 1700 50 
F4 "OUT" O R 2200 1600 50 
$EndSheet
Wire Wire Line
	1500 1500 1650 1500
Wire Wire Line
	2200 1600 3500 1600
Wire Wire Line
	3500 1600 3500 1450
Wire Wire Line
	3500 1450 3950 1450
Connection ~ 3950 1450
Text HLabel 1500 1700 0    50   Input ~ 0
MCODE_RST
Wire Wire Line
	1500 1700 1650 1700
$EndSCHEMATC
