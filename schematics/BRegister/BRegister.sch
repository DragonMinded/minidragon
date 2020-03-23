EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 102 404
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
S 2500 2000 550  1000
U 5EB60C14
F0 "B Register Upper Bits" 50
F1 "UpperBits/4BitRegister.sch" 50
F2 "CLK" I L 2500 2900 50 
F3 "EN" I L 2500 2700 50 
F4 "D1" I L 2500 2400 50 
F5 "D2" I L 2500 2300 50 
F6 "D3" I L 2500 2200 50 
F7 "D4" I L 2500 2100 50 
F8 "RST" I L 2500 2800 50 
F9 "Q1" O R 3050 2400 50 
F10 "Q2" O R 3050 2300 50 
F11 "Q3" O R 3050 2200 50 
F12 "Q4" O R 3050 2100 50 
$EndSheet
$Sheet
S 2500 3500 550  1000
U 5EB6EB79
F0 "B Register Lower Bits" 50
F1 "LowerBits/4BitRegister.sch" 50
F2 "CLK" I L 2500 4400 50 
F3 "EN" I L 2500 4200 50 
F4 "D1" I L 2500 3900 50 
F5 "D2" I L 2500 3800 50 
F6 "D3" I L 2500 3700 50 
F7 "D4" I L 2500 3600 50 
F8 "RST" I L 2500 4300 50 
F9 "Q1" O R 3050 3900 50 
F10 "Q2" O R 3050 3800 50 
F11 "Q3" O R 3050 3700 50 
F12 "Q4" O R 3050 3600 50 
$EndSheet
Text GLabel 2000 2800 0    50   Input ~ 0
SYS_RST
Text GLabel 2000 2900 0    50   Input ~ 0
SYS_CLK
Wire Wire Line
	2500 2800 2350 2800
Wire Wire Line
	2000 2900 2300 2900
Wire Wire Line
	2350 2800 2350 4300
Wire Wire Line
	2350 4300 2500 4300
Connection ~ 2350 2800
Wire Wire Line
	2350 2800 2000 2800
Wire Wire Line
	2500 4400 2300 4400
Wire Wire Line
	2300 4400 2300 2900
Connection ~ 2300 2900
Wire Wire Line
	2300 2900 2500 2900
Text HLabel 2000 2700 0    50   Input ~ 0
B_IN
Wire Wire Line
	2000 2700 2400 2700
Wire Wire Line
	2400 2700 2400 4200
Wire Wire Line
	2400 4200 2500 4200
Connection ~ 2400 2700
Wire Wire Line
	2400 2700 2500 2700
Text HLabel 2000 2100 0    50   Input ~ 0
D_8
Text HLabel 2000 2200 0    50   Input ~ 0
D_7
Text HLabel 2000 2300 0    50   Input ~ 0
D_6
Text HLabel 2000 2400 0    50   Input ~ 0
D_5
Text HLabel 2000 3600 0    50   Input ~ 0
D_4
Text HLabel 2000 3700 0    50   Input ~ 0
D_3
Text HLabel 2000 3800 0    50   Input ~ 0
D_2
Text HLabel 2000 3900 0    50   Input ~ 0
D_1
Wire Wire Line
	2000 3900 2500 3900
Wire Wire Line
	2500 3800 2000 3800
Wire Wire Line
	2000 3700 2500 3700
Wire Wire Line
	2500 3600 2000 3600
Wire Wire Line
	2000 2400 2500 2400
Wire Wire Line
	2500 2300 2000 2300
Wire Wire Line
	2000 2200 2500 2200
Wire Wire Line
	2500 2100 2000 2100
Text HLabel 3500 2100 2    50   Output ~ 0
Q_8
Text HLabel 3500 2200 2    50   Output ~ 0
Q_7
Text HLabel 3500 2300 2    50   Output ~ 0
Q_6
Text HLabel 3500 2400 2    50   Output ~ 0
Q_5
Text HLabel 3500 3600 2    50   Output ~ 0
Q_4
Text HLabel 3500 3700 2    50   Output ~ 0
Q_3
Text HLabel 3500 3800 2    50   Output ~ 0
Q_2
Text HLabel 3500 3900 2    50   Output ~ 0
Q_1
Wire Wire Line
	3050 2100 3500 2100
Wire Wire Line
	3500 2200 3050 2200
Wire Wire Line
	3050 2300 3500 2300
Wire Wire Line
	3500 2400 3050 2400
Wire Wire Line
	3050 3600 3500 3600
Wire Wire Line
	3500 3700 3050 3700
Wire Wire Line
	3050 3800 3500 3800
Wire Wire Line
	3500 3900 3050 3900
$EndSCHEMATC
