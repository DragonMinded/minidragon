EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 213 484
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
U 6158BEA2
F0 "IP 3rd Nibble Power" 50
F1 "Power.sch" 50
$EndSheet
$Sheet
S 5100 1000 1000 200 
U 5FAD54F2
F0 "IP 3rd Nibble LED Indicator Bit 1" 50
F1 "LEDIndicator.sch" 50
F2 "D" I L 5100 1100 50 
$EndSheet
$Sheet
S 3450 1000 700  550 
U 5FAD553B
F0 "IP 3rd Nibble D Flip Flop Bit 1" 50
F1 "DFlipFlop.sch" 50
F2 "EN2" I L 3450 1200 50 
F3 "D" I L 3450 1300 50 
F4 "EN1" I L 3450 1100 50 
F5 "Q" O R 4150 1100 50 
F6 "RST" I L 3450 1450 50 
$EndSheet
Wire Wire Line
	4150 1100 4300 1100
Wire Wire Line
	4300 1100 4300 1600
Wire Wire Line
	4300 1600 5100 1600
Connection ~ 4300 1100
Wire Wire Line
	4300 1100 5100 1100
Wire Wire Line
	2700 1650 2700 1200
Wire Wire Line
	2700 1200 3450 1200
$Sheet
S 5100 4500 1000 200 
U 5FAD5454
F0 "IP 3rd Nibble Buffer Out Bit 4" 50
F1 "Buffer_4.sch" 50
F2 "BufOut" O R 6100 4600 50 
F3 "D" I L 5100 4600 50 
$EndSheet
$Sheet
S 5100 2500 1000 200 
U 5FAD54AB
F0 "IP 3rd Nibble Buffer Out Bit 2" 50
F1 "Buffer_2.sch" 50
F2 "BufOut" O R 6100 2600 50 
F3 "D" I L 5100 2600 50 
$EndSheet
$Sheet
S 5100 3000 1000 200 
U 5FAD5490
F0 "IP 3rd Nibble LED Indicator Bit 3" 50
F1 "LEDIndicator_3.sch" 50
F2 "D" I L 5100 3100 50 
$EndSheet
$Sheet
S 5100 1500 1000 200 
U 5FAD5475
F0 "IP 3rd Nibble Buffer Out Bit 1" 50
F1 "Buffer.sch" 50
F2 "BufOut" O R 6100 1600 50 
F3 "D" I L 5100 1600 50 
$EndSheet
Wire Wire Line
	6100 1600 6700 1600
Wire Wire Line
	6700 1600 6700 2000
Wire Wire Line
	6700 2000 6900 2000
Wire Wire Line
	6100 2600 6500 2600
Wire Wire Line
	6500 2600 6500 2100
Wire Wire Line
	6500 2100 6900 2100
Wire Wire Line
	6900 2200 6600 2200
Wire Wire Line
	6600 2200 6600 3600
Wire Wire Line
	6600 3600 6100 3600
Wire Wire Line
	6900 2300 6700 2300
Wire Wire Line
	6700 2300 6700 4600
Wire Wire Line
	6700 4600 6100 4600
Wire Wire Line
	3450 1300 2800 1300
Wire Wire Line
	2800 1300 2800 2000
Wire Wire Line
	2900 2650 2900 2450
Wire Wire Line
	2900 1450 3450 1450
$Sheet
S 3450 2000 700  550 
U 5FAD5457
F0 "IP 3rd Nibble D Flip Flop Bit 2" 50
F1 "DFlipFlop_2.sch" 50
F2 "EN2" I L 3450 2200 50 
F3 "D" I L 3450 2300 50 
F4 "EN1" I L 3450 2100 50 
F5 "Q" O R 4150 2100 50 
F6 "RST" I L 3450 2450 50 
$EndSheet
Wire Wire Line
	4150 2100 4300 2100
Wire Wire Line
	2900 2450 3450 2450
Connection ~ 2900 2450
Wire Wire Line
	2900 2450 2900 1450
Wire Wire Line
	2700 1650 2700 2200
Wire Wire Line
	2700 2200 3450 2200
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
	2600 2100 3450 2100
Connection ~ 2600 1100
Wire Wire Line
	2600 1100 3450 1100
Wire Wire Line
	1200 2100 2500 2100
Wire Wire Line
	2500 2100 2500 2300
Wire Wire Line
	2500 2300 3450 2300
Wire Wire Line
	1200 1100 1400 1100
Wire Wire Line
	4300 2100 4300 2600
Wire Wire Line
	4300 2600 5100 2600
Connection ~ 4300 2100
Wire Wire Line
	4300 2100 5100 2100
Wire Wire Line
	4150 3100 4300 3100
Wire Wire Line
	4300 3100 4300 3600
Wire Wire Line
	4300 3600 5100 3600
Connection ~ 4300 3100
Wire Wire Line
	4300 3100 5100 3100
Wire Wire Line
	2600 2100 2600 3100
Wire Wire Line
	2600 3100 3450 3100
Connection ~ 2600 2100
Wire Wire Line
	2700 2200 2700 3200
Wire Wire Line
	2700 3200 3450 3200
Connection ~ 2700 2200
Wire Wire Line
	1200 2200 2400 2200
Wire Wire Line
	2400 2200 2400 3300
Wire Wire Line
	2400 3300 3450 3300
Wire Wire Line
	2900 2650 2900 3450
Wire Wire Line
	2900 3450 3450 3450
Connection ~ 2900 2650
$Sheet
S 3450 4000 700  600 
U 6158BEDF
F0 "IP 3rd Nibble D Flip Flop Bit 4" 50
F1 "DFlipFlop_4.sch" 50
F2 "EN2" I L 3450 4200 50 
F3 "D" I L 3450 4300 50 
F4 "EN1" I L 3450 4100 50 
F5 "Q" O R 4150 4100 50 
F6 "RST" I L 3450 4500 50 
$EndSheet
Wire Wire Line
	4150 4100 4300 4100
Wire Wire Line
	4300 4100 4300 4600
Wire Wire Line
	4300 4600 5100 4600
Connection ~ 4300 4100
Wire Wire Line
	4300 4100 5100 4100
Wire Wire Line
	2900 3450 2900 4500
Wire Wire Line
	2900 4500 3450 4500
Connection ~ 2900 3450
Wire Wire Line
	2700 3200 2700 4200
Wire Wire Line
	2700 4200 3450 4200
Connection ~ 2700 3200
Wire Wire Line
	2600 3100 2600 4100
Wire Wire Line
	2600 4100 3450 4100
Connection ~ 2600 3100
Wire Wire Line
	1200 2300 2300 2300
Wire Wire Line
	2300 2300 2300 4300
Wire Wire Line
	2300 4300 3450 4300
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
Text HLabel 6900 2000 2    50   Output ~ 0
Q1
Text HLabel 6900 2100 2    50   Output ~ 0
Q2
Text HLabel 6900 2200 2    50   Output ~ 0
Q3
Text HLabel 6900 2300 2    50   Output ~ 0
Q4
$Sheet
S 5100 3500 1000 200 
U 5FAD553D
F0 "IP 3rd Nibble Buffer Out Bit 3" 50
F1 "Buffer_3.sch" 50
F2 "BufOut" O R 6100 3600 50 
F3 "D" I L 5100 3600 50 
$EndSheet
$Sheet
S 5100 4000 1000 200 
U 6158BEF7
F0 "IP 3rd Nibble LED Indicator Bit 4" 50
F1 "LEDIndicator_4.sch" 50
F2 "D" I L 5100 4100 50 
$EndSheet
$Sheet
S 5100 2000 1000 200 
U 5E693BA0
F0 "IP 3rd Nibble LED Indicator Bit 2" 50
F1 "LedIndicator_2.sch" 50
F2 "D" I L 5100 2100 50 
$EndSheet
$Sheet
S 1400 1000 1100 200 
U 6158BE23
F0 "IP 3rd Nibble Clock Edge Detection" 50
F1 "ClockDetect.sch" 50
F2 "ClkIn" I L 1400 1100 50 
F3 "EdgeOut" O R 2500 1100 50 
$EndSheet
$Sheet
S 3450 3000 700  550 
U 5FAD5485
F0 "IP 3rd Nibble D Flip Flop Bit 3" 50
F1 "DFlipFlop_3.sch" 50
F2 "EN2" I L 3450 3200 50 
F3 "D" I L 3450 3300 50 
F4 "EN1" I L 3450 3100 50 
F5 "Q" O R 4150 3100 50 
F6 "RST" I L 3450 3450 50 
$EndSheet
$EndSCHEMATC
