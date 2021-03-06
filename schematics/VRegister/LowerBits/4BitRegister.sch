EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 446 484
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
U 5E73DA0F
F0 "V Lower Power" 50
F1 "Power.sch" 50
$EndSheet
$Sheet
S 1400 1000 1100 200 
U 5E73D956
F0 "V Lower Clock Edge Detection" 50
F1 "ClockDetect.sch" 50
F2 "ClkIn" I L 1400 1100 50 
F3 "EdgeOut" O R 2500 1100 50 
$EndSheet
$Sheet
S 4550 1000 1000 200 
U 5E73D957
F0 "V Lower LED Indicator Bit 1" 50
F1 "LEDIndicator.sch" 50
F2 "D" I L 4550 1100 50 
$EndSheet
$Sheet
S 3000 1000 700  550 
U 5E73D958
F0 "V Lower D Flip Flop Bit 1" 50
F1 "DFlipFlop.sch" 50
F2 "EN2" I L 3000 1200 50 
F3 "D" I L 3000 1300 50 
F4 "EN1" I L 3000 1100 50 
F5 "Q" O R 3700 1100 50 
F6 "RST" I L 3000 1450 50 
$EndSheet
Wire Wire Line
	3700 1100 3850 1100
Wire Wire Line
	3850 1100 3850 1600
Wire Wire Line
	3850 1600 4550 1600
Connection ~ 3850 1100
Wire Wire Line
	3850 1100 4550 1100
Wire Wire Line
	2700 1650 2700 1200
Wire Wire Line
	2700 1200 3000 1200
$Sheet
S 4550 4500 1000 200 
U 5E693C12
F0 "V Lower Buffer Out Bit 4" 50
F1 "Buffer_4.sch" 50
F2 "BufOut" O R 5550 4600 50 
F3 "D" I L 4550 4600 50 
$EndSheet
$Sheet
S 4550 2500 1000 200 
U 5FA68CA7
F0 "V Lower Buffer Out Bit 2" 50
F1 "Buffer_2.sch" 50
F2 "BufOut" O R 5550 2600 50 
F3 "D" I L 4550 2600 50 
$EndSheet
$Sheet
S 4550 3000 1000 200 
U 5FA68B54
F0 "V Lower LED Indicator Bit 3" 50
F1 "LEDIndicator_3.sch" 50
F2 "D" I L 4550 3100 50 
$EndSheet
$Sheet
S 4550 2000 1000 200 
U 5FA68C24
F0 "V Lower LED Indicator Bit 2" 50
F1 "LedIndicator_2.sch" 50
F2 "D" I L 4550 2100 50 
$EndSheet
$Sheet
S 4550 1500 1000 200 
U 5E693C10
F0 "V Lower Buffer Out Bit 1" 50
F1 "Buffer.sch" 50
F2 "BufOut" O R 5550 1600 50 
F3 "D" I L 4550 1600 50 
$EndSheet
Wire Wire Line
	5550 1600 6150 1600
Wire Wire Line
	6150 1600 6150 2000
Wire Wire Line
	6150 2000 6350 2000
Wire Wire Line
	5550 2600 5950 2600
Wire Wire Line
	5950 2600 5950 2100
Wire Wire Line
	5950 2100 6350 2100
Wire Wire Line
	6350 2200 6050 2200
Wire Wire Line
	6050 2200 6050 3600
Wire Wire Line
	6050 3600 5550 3600
Wire Wire Line
	6350 2300 6150 2300
Wire Wire Line
	6150 2300 6150 4600
Wire Wire Line
	6150 4600 5550 4600
Wire Wire Line
	3000 1300 2800 1300
Wire Wire Line
	2800 1300 2800 2000
Wire Wire Line
	2900 2650 2900 2450
Wire Wire Line
	2900 1450 3000 1450
$Sheet
S 3000 2000 700  550 
U 5E693C29
F0 "V Lower D Flip Flop Bit 2" 50
F1 "DFlipFlop_2.sch" 50
F2 "EN2" I L 3000 2200 50 
F3 "D" I L 3000 2300 50 
F4 "EN1" I L 3000 2100 50 
F5 "Q" O R 3700 2100 50 
F6 "RST" I L 3000 2450 50 
$EndSheet
Wire Wire Line
	3700 2100 3850 2100
Wire Wire Line
	2900 2450 3000 2450
Connection ~ 2900 2450
Wire Wire Line
	2900 2450 2900 1450
Wire Wire Line
	2700 1650 2700 2200
Wire Wire Line
	2700 2200 3000 2200
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
	2600 2100 3000 2100
Connection ~ 2600 1100
Wire Wire Line
	2600 1100 3000 1100
Wire Wire Line
	1200 2100 2500 2100
Wire Wire Line
	2500 2100 2500 2300
Wire Wire Line
	2500 2300 3000 2300
Wire Wire Line
	1200 1100 1400 1100
$Sheet
S 3000 3000 700  550 
U 5E73D963
F0 "V Lower D Flip Flop Bit 3" 50
F1 "DFlipFlop_3.sch" 50
F2 "EN2" I L 3000 3200 50 
F3 "D" I L 3000 3300 50 
F4 "EN1" I L 3000 3100 50 
F5 "Q" O R 3700 3100 50 
F6 "RST" I L 3000 3450 50 
$EndSheet
Wire Wire Line
	3850 2100 3850 2600
Wire Wire Line
	3850 2600 4550 2600
Connection ~ 3850 2100
Wire Wire Line
	3850 2100 4550 2100
Wire Wire Line
	3700 3100 3850 3100
Wire Wire Line
	3850 3100 3850 3600
Wire Wire Line
	3850 3600 4550 3600
Connection ~ 3850 3100
Wire Wire Line
	3850 3100 4550 3100
Wire Wire Line
	2600 2100 2600 3100
Wire Wire Line
	2600 3100 3000 3100
Connection ~ 2600 2100
Wire Wire Line
	2700 2200 2700 3200
Wire Wire Line
	2700 3200 3000 3200
Connection ~ 2700 2200
Wire Wire Line
	1200 2200 2400 2200
Wire Wire Line
	2400 2200 2400 3300
Wire Wire Line
	2400 3300 3000 3300
Wire Wire Line
	2900 2650 2900 3450
Wire Wire Line
	2900 3450 3000 3450
Connection ~ 2900 2650
$Sheet
S 3000 4000 700  600 
U 5FA68CD8
F0 "V Lower D Flip Flop Bit 4" 50
F1 "DFlipFlop_4.sch" 50
F2 "EN2" I L 3000 4200 50 
F3 "D" I L 3000 4300 50 
F4 "EN1" I L 3000 4100 50 
F5 "Q" O R 3700 4100 50 
F6 "RST" I L 3000 4500 50 
$EndSheet
Wire Wire Line
	3700 4100 3850 4100
Wire Wire Line
	3850 4100 3850 4600
Wire Wire Line
	3850 4600 4550 4600
Connection ~ 3850 4100
Wire Wire Line
	3850 4100 4550 4100
Wire Wire Line
	2900 3450 2900 4500
Wire Wire Line
	2900 4500 3000 4500
Connection ~ 2900 3450
Wire Wire Line
	2700 3200 2700 4200
Wire Wire Line
	2700 4200 3000 4200
Connection ~ 2700 3200
Wire Wire Line
	2600 3100 2600 4100
Wire Wire Line
	2600 4100 3000 4100
Connection ~ 2600 3100
Wire Wire Line
	1200 2300 2300 2300
Wire Wire Line
	2300 2300 2300 4300
Wire Wire Line
	2300 4300 3000 4300
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
Text HLabel 6350 2000 2    50   Output ~ 0
Q1
Text HLabel 6350 2100 2    50   Output ~ 0
Q2
Text HLabel 6350 2200 2    50   Output ~ 0
Q3
Text HLabel 6350 2300 2    50   Output ~ 0
Q4
$Sheet
S 4550 3500 1000 200 
U 5FA68C95
F0 "V Lower Buffer Out Bit 3" 50
F1 "Buffer_3.sch" 50
F2 "BufOut" O R 5550 3600 50 
F3 "D" I L 4550 3600 50 
$EndSheet
$Sheet
S 4550 4000 1000 200 
U 5E73D9EE
F0 "V Lower LED Indicator Bit 4" 50
F1 "LEDIndicator_4.sch" 50
F2 "D" I L 4550 4100 50 
$EndSheet
$EndSCHEMATC
