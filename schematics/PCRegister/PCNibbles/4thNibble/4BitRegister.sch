EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 270 373
Title "Transistor 4-Bit Register"
Date "2020-01-19"
Rev "1"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Sheet
S 1000 3000 500  500 
U 5FAB0B68
F0 "PC 4th Nibble Power" 50
F1 "Power.sch" 50
$EndSheet
$Sheet
S 5050 1000 1000 200 
U 6158BAC2
F0 "PC 4th Nibble LED Indicator Bit 1" 50
F1 "LEDIndicator.sch" 50
F2 "D" I L 5050 1100 50 
$EndSheet
$Sheet
S 3350 1000 700  550 
U 5E73FFA2
F0 "PC 4th Nibble D Flip Flop Bit 1" 50
F1 "DFlipFlop.sch" 50
F2 "EN2" I L 3350 1200 50 
F3 "D" I L 3350 1300 50 
F4 "EN1" I L 3350 1100 50 
F5 "Q" O R 4050 1100 50 
F6 "RST" I L 3350 1450 50 
$EndSheet
Wire Wire Line
	4050 1100 4200 1100
Wire Wire Line
	4200 1100 4200 1600
Wire Wire Line
	4200 1600 5050 1600
Connection ~ 4200 1100
Wire Wire Line
	4200 1100 5050 1100
Wire Wire Line
	2700 1650 2700 1200
Wire Wire Line
	2700 1200 3350 1200
$Sheet
S 5050 4500 1000 200 
U 5FAB0BAE
F0 "PC 4th Nibble Buffer Out Bit 4" 50
F1 "Buffer_4.sch" 50
F2 "BufOut" O R 6050 4600 50 
F3 "D" I L 5050 4600 50 
$EndSheet
$Sheet
S 5050 2500 1000 200 
U 6158BBA6
F0 "PC 4th Nibble Buffer Out Bit 2" 50
F1 "Buffer_2.sch" 50
F2 "BufOut" O R 6050 2600 50 
F3 "D" I L 5050 2600 50 
$EndSheet
$Sheet
S 5050 3000 1000 200 
U 5FAB0C4B
F0 "PC 4th Nibble LED Indicator Bit 3" 50
F1 "LEDIndicator_3.sch" 50
F2 "D" I L 5050 3100 50 
$EndSheet
$Sheet
S 5050 1500 1000 200 
U 5FAB0BC9
F0 "PC 4th Nibble Buffer Out Bit 1" 50
F1 "Buffer.sch" 50
F2 "BufOut" O R 6050 1600 50 
F3 "D" I L 5050 1600 50 
$EndSheet
Wire Wire Line
	6050 1600 6650 1600
Wire Wire Line
	6650 1600 6650 2000
Wire Wire Line
	6650 2000 6850 2000
Wire Wire Line
	6050 2600 6450 2600
Wire Wire Line
	6450 2600 6450 2100
Wire Wire Line
	6450 2100 6850 2100
Wire Wire Line
	6850 2200 6550 2200
Wire Wire Line
	6550 2200 6550 3600
Wire Wire Line
	6550 3600 6050 3600
Wire Wire Line
	6850 2300 6650 2300
Wire Wire Line
	6650 2300 6650 4600
Wire Wire Line
	6650 4600 6050 4600
Wire Wire Line
	3350 1300 2800 1300
Wire Wire Line
	2800 1300 2800 2000
Wire Wire Line
	2900 2650 2900 2450
Wire Wire Line
	2900 1450 3350 1450
$Sheet
S 3350 2000 700  550 
U 6158BB7A
F0 "PC 4th Nibble D Flip Flop Bit 2" 50
F1 "DFlipFlop_2.sch" 50
F2 "EN2" I L 3350 2200 50 
F3 "D" I L 3350 2300 50 
F4 "EN1" I L 3350 2100 50 
F5 "Q" O R 4050 2100 50 
F6 "RST" I L 3350 2450 50 
$EndSheet
Wire Wire Line
	4050 2100 4200 2100
Wire Wire Line
	2900 2450 3350 2450
Connection ~ 2900 2450
Wire Wire Line
	2900 2450 2900 1450
Wire Wire Line
	2700 1650 2700 2200
Wire Wire Line
	2700 2200 3350 2200
Connection ~ 2700 1650
Wire Wire Line
	2500 1100 2600 1100
Wire Wire Line
	1200 1650 2700 1650
Wire Wire Line
	1200 2000 2800 2000
Wire Wire Line
	1200 2650 2900 2650
Wire Wire Line
	2600 1100 2600 2100
Wire Wire Line
	2600 2100 3350 2100
Connection ~ 2600 1100
Wire Wire Line
	2600 1100 3350 1100
Wire Wire Line
	1200 2100 2500 2100
Wire Wire Line
	2500 2100 2500 2300
Wire Wire Line
	2500 2300 3350 2300
Wire Wire Line
	1200 1100 1400 1100
Wire Wire Line
	4200 2100 4200 2600
Wire Wire Line
	4200 2600 5050 2600
Connection ~ 4200 2100
Wire Wire Line
	4200 2100 5050 2100
Wire Wire Line
	4050 3100 4200 3100
Wire Wire Line
	4200 3100 4200 3600
Wire Wire Line
	4200 3600 5050 3600
Connection ~ 4200 3100
Wire Wire Line
	4200 3100 5050 3100
Wire Wire Line
	2600 2100 2600 3100
Wire Wire Line
	2600 3100 3350 3100
Connection ~ 2600 2100
Wire Wire Line
	2700 2200 2700 3200
Wire Wire Line
	2700 3200 3350 3200
Connection ~ 2700 2200
Wire Wire Line
	1200 2200 2400 2200
Wire Wire Line
	2400 2200 2400 3300
Wire Wire Line
	2400 3300 3350 3300
Wire Wire Line
	2900 2650 2900 3450
Wire Wire Line
	2900 3450 3350 3450
Connection ~ 2900 2650
$Sheet
S 3350 4000 700  600 
U 5FAB0BEA
F0 "PC 4th Nibble D Flip Flop Bit 4" 50
F1 "DFlipFlop_4.sch" 50
F2 "EN2" I L 3350 4200 50 
F3 "D" I L 3350 4300 50 
F4 "EN1" I L 3350 4100 50 
F5 "Q" O R 4050 4100 50 
F6 "RST" I L 3350 4500 50 
$EndSheet
Wire Wire Line
	4050 4100 4200 4100
Wire Wire Line
	4200 4100 4200 4600
Wire Wire Line
	4200 4600 5050 4600
Connection ~ 4200 4100
Wire Wire Line
	4200 4100 5050 4100
Wire Wire Line
	2900 3450 2900 4500
Wire Wire Line
	2900 4500 3350 4500
Connection ~ 2900 3450
Wire Wire Line
	2700 3200 2700 4200
Wire Wire Line
	2700 4200 3350 4200
Connection ~ 2700 3200
Wire Wire Line
	2600 3100 2600 4100
Wire Wire Line
	2600 4100 3350 4100
Connection ~ 2600 3100
Wire Wire Line
	1200 2300 2300 2300
Wire Wire Line
	2300 2300 2300 4300
Wire Wire Line
	2300 4300 3350 4300
Text HLabel 1200 1100 0    50   Input ~ 0
CLK
Text HLabel 1200 1650 0    50   Input ~ 0
EN
Text HLabel 1200 2000 0    50   Input ~ 0
D1
Text HLabel 1200 2100 0    50   Input ~ 0
D2
Text HLabel 1200 2200 0    50   Input ~ 0
D3
Text HLabel 1200 2300 0    50   Input ~ 0
D4
Text HLabel 1200 2650 0    50   Input ~ 0
RST
Text HLabel 6850 2000 2    50   Output ~ 0
Q1
Text HLabel 6850 2100 2    50   Output ~ 0
Q2
Text HLabel 6850 2200 2    50   Output ~ 0
Q3
Text HLabel 6850 2300 2    50   Output ~ 0
Q4
$Sheet
S 5050 3500 1000 200 
U 6158BB61
F0 "PC 4th Nibble Buffer Out Bit 3" 50
F1 "Buffer_3.sch" 50
F2 "BufOut" O R 6050 3600 50 
F3 "D" I L 5050 3600 50 
$EndSheet
$Sheet
S 5050 4000 1000 200 
U 6158BB52
F0 "PC 4th Nibble LED Indicator Bit 4" 50
F1 "LEDIndicator_4.sch" 50
F2 "D" I L 5050 4100 50 
$EndSheet
$Sheet
S 5050 2000 1000 200 
U 5FAB0C3A
F0 "PC 4th Nibble LED Indicator Bit 2" 50
F1 "LedIndicator_2.sch" 50
F2 "D" I L 5050 2100 50 
$EndSheet
$Sheet
S 1400 1000 1100 200 
U 5FAB0BB3
F0 "PC 4th Nibble Clock Edge Detection" 50
F1 "ClockDetect.sch" 50
F2 "ClkIn" I L 1400 1100 50 
F3 "EdgeOut" O R 2500 1100 50 
$EndSheet
$Sheet
S 3350 3000 700  550 
U 5FAB0C46
F0 "PC 4th Nibble D Flip Flop Bit 3" 50
F1 "DFlipFlop_3.sch" 50
F2 "EN2" I L 3350 3200 50 
F3 "D" I L 3350 3300 50 
F4 "EN1" I L 3350 3100 50 
F5 "Q" O R 4050 3100 50 
F6 "RST" I L 3350 3450 50 
$EndSheet
$EndSCHEMATC
