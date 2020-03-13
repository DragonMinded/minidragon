EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 123 372
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
S 3500 1500 500  1000
U 5E6EC9B7
F0 "Zero Register Lower Bus Out" 50
F1 "ZeroRegisterBusOutputLower.sch" 50
F2 "EN" I L 3500 2450 50 
F3 "D1" I L 3500 2250 50 
F4 "D2" I L 3500 2150 50 
F5 "D3" I L 3500 2050 50 
F6 "D4" I L 3500 1950 50 
F7 "D5" I L 3500 1850 50 
F8 "D6" I L 3500 1750 50 
F9 "D7" I L 3500 1650 50 
F10 "D8" I L 3500 1550 50 
F11 "Q8" O R 4000 1550 50 
F12 "Q7" O R 4000 1650 50 
F13 "Q6" O R 4000 1750 50 
F14 "Q5" O R 4000 1850 50 
F15 "Q4" O R 4000 1950 50 
F16 "Q3" O R 4000 2050 50 
F17 "Q2" O R 4000 2150 50 
F18 "Q1" O R 4000 2250 50 
$EndSheet
Wire Wire Line
	3000 2450 3500 2450
Text HLabel 3000 2450 0    50   Input ~ 0
Z_OUT
Text HLabel 4150 1550 2    50   BiDi ~ 0
BUS_8
Text HLabel 4150 1650 2    50   BiDi ~ 0
BUS_7
Text HLabel 4150 1750 2    50   BiDi ~ 0
BUS_6
Text HLabel 4150 1850 2    50   BiDi ~ 0
BUS_5
Text HLabel 4150 1950 2    50   BiDi ~ 0
BUS_4
Text HLabel 4150 2050 2    50   BiDi ~ 0
BUS_3
Text HLabel 4150 2150 2    50   BiDi ~ 0
BUS_2
Text HLabel 4150 2250 2    50   BiDi ~ 0
BUS_1
Wire Wire Line
	4000 1550 4150 1550
Wire Wire Line
	4150 1650 4000 1650
Wire Wire Line
	4000 1750 4150 1750
Wire Wire Line
	4150 1850 4000 1850
Wire Wire Line
	4000 1950 4150 1950
Wire Wire Line
	4150 2050 4000 2050
Wire Wire Line
	4000 2150 4150 2150
Wire Wire Line
	4150 2250 4000 2250
$Comp
L power:GND #PWR?
U 1 1 5E6F83A9
P 3400 2250
F 0 "#PWR?" H 3400 2000 50  0001 C CNN
F 1 "GND" H 3405 2077 50  0000 C CNN
F 2 "" H 3400 2250 50  0001 C CNN
F 3 "" H 3400 2250 50  0001 C CNN
	1    3400 2250
	1    0    0    -1  
$EndComp
Wire Wire Line
	3500 2250 3400 2250
Wire Wire Line
	3400 2250 3400 2150
Wire Wire Line
	3400 2150 3500 2150
Connection ~ 3400 2250
Wire Wire Line
	3500 2050 3400 2050
Wire Wire Line
	3400 2050 3400 2150
Connection ~ 3400 2150
Wire Wire Line
	3400 2050 3400 1950
Wire Wire Line
	3400 1950 3500 1950
Connection ~ 3400 2050
Wire Wire Line
	3500 1850 3400 1850
Wire Wire Line
	3400 1850 3400 1950
Connection ~ 3400 1950
Wire Wire Line
	3400 1850 3400 1750
Wire Wire Line
	3400 1750 3500 1750
Connection ~ 3400 1850
Wire Wire Line
	3500 1650 3400 1650
Wire Wire Line
	3400 1650 3400 1750
Connection ~ 3400 1750
Wire Wire Line
	3400 1650 3400 1550
Wire Wire Line
	3400 1550 3500 1550
Connection ~ 3400 1650
$EndSCHEMATC
