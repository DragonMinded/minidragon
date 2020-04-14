EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 413 478
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text GLabel 2400 1600 0    50   Input ~ 0
SYS_CLK
Text GLabel 2400 2500 0    50   Input ~ 0
SYS_RST
Wire Wire Line
	2400 1600 2800 1600
Wire Wire Line
	2400 2500 2850 2500
Wire Wire Line
	2850 2500 2850 4000
Wire Wire Line
	2850 4000 2900 4000
Connection ~ 2850 2500
Wire Wire Line
	2850 2500 2900 2500
Wire Wire Line
	2900 3100 2800 3100
Wire Wire Line
	2800 3100 2800 1600
Connection ~ 2800 1600
Wire Wire Line
	2800 1600 2900 1600
Text HLabel 2400 1700 0    50   Input ~ 0
U_IN
Wire Wire Line
	2400 1700 2750 1700
Wire Wire Line
	2750 1700 2750 3200
Wire Wire Line
	2750 3200 2900 3200
Connection ~ 2750 1700
Wire Wire Line
	2750 1700 2900 1700
Text HLabel 2400 2000 0    50   BiDi ~ 0
BUS_8
Text HLabel 2400 2100 0    50   BiDi ~ 0
BUS_7
Text HLabel 2400 2200 0    50   BiDi ~ 0
BUS_6
Text HLabel 2400 2300 0    50   BiDi ~ 0
BUS_5
Text HLabel 2400 3500 0    50   BiDi ~ 0
BUS_4
Text HLabel 2400 3600 0    50   BiDi ~ 0
BUS_3
Text HLabel 2400 3700 0    50   BiDi ~ 0
BUS_2
Text HLabel 2400 3800 0    50   BiDi ~ 0
BUS_1
Wire Wire Line
	2400 3800 2900 3800
Wire Wire Line
	2900 3700 2400 3700
Wire Wire Line
	2400 3600 2900 3600
Wire Wire Line
	2900 3500 2400 3500
Wire Wire Line
	2400 2300 2900 2300
Wire Wire Line
	2900 2200 2400 2200
Wire Wire Line
	2400 2100 2900 2100
Wire Wire Line
	2900 2000 2400 2000
$Sheet
S 2900 3050 550  1000
U 5E693D15
F0 "U Register Lower Bits" 50
F1 "LowerBits/4BitRegister.sch" 50
F2 "CLK" I L 2900 3100 50 
F3 "EN" I L 2900 3200 50 
F4 "D1" I L 2900 3800 50 
F5 "D2" I L 2900 3700 50 
F6 "D3" I L 2900 3600 50 
F7 "D4" I L 2900 3500 50 
F8 "RST" I L 2900 4000 50 
F9 "Q1" O R 3450 3400 50 
F10 "Q2" O R 3450 3300 50 
F11 "Q3" O R 3450 3200 50 
F12 "Q4" O R 3450 3100 50 
$EndSheet
$Sheet
S 2900 1550 500  1000
U 5FA68BB5
F0 "U Register Upper Bits" 50
F1 "UpperBits/4BitRegister.sch" 50
F2 "CLK" I L 2900 1600 50 
F3 "EN" I L 2900 1700 50 
F4 "D1" I L 2900 2300 50 
F5 "D2" I L 2900 2200 50 
F6 "D3" I L 2900 2100 50 
F7 "D4" I L 2900 2000 50 
F8 "RST" I L 2900 2500 50 
F9 "Q1" O R 3400 1900 50 
F10 "Q2" O R 3400 1800 50 
F11 "Q3" O R 3400 1700 50 
F12 "Q4" O R 3400 1600 50 
$EndSheet
Text HLabel 5600 1550 2    50   BiDi ~ 0
BUS_8
Text HLabel 5600 1650 2    50   BiDi ~ 0
BUS_7
Text HLabel 5600 1750 2    50   BiDi ~ 0
BUS_6
Text HLabel 5600 1850 2    50   BiDi ~ 0
BUS_5
Text HLabel 5600 1950 2    50   BiDi ~ 0
BUS_4
Text HLabel 5600 2050 2    50   BiDi ~ 0
BUS_3
Text HLabel 5600 2150 2    50   BiDi ~ 0
BUS_2
Text HLabel 5600 2250 2    50   BiDi ~ 0
BUS_1
Wire Wire Line
	5500 1550 5600 1550
Wire Wire Line
	5500 1650 5600 1650
Wire Wire Line
	5500 1750 5600 1750
Wire Wire Line
	5500 1850 5600 1850
Wire Wire Line
	5500 1950 5600 1950
Wire Wire Line
	5500 2050 5600 2050
Wire Wire Line
	5500 2150 5600 2150
Wire Wire Line
	5500 2250 5600 2250
Wire Wire Line
	5000 1950 4950 1950
Wire Wire Line
	4950 1950 4950 3100
Wire Wire Line
	3450 3100 4950 3100
Wire Wire Line
	5000 2050 4900 2050
Wire Wire Line
	4900 2050 4900 3200
Wire Wire Line
	3450 3200 4900 3200
Wire Wire Line
	5000 2150 4850 2150
Wire Wire Line
	4850 2150 4850 3300
Wire Wire Line
	3450 3300 4850 3300
Wire Wire Line
	4800 3400 4800 2250
Wire Wire Line
	4800 2250 5000 2250
Wire Wire Line
	3450 3400 4800 3400
Wire Wire Line
	5000 1850 4750 1850
Wire Wire Line
	4750 1850 4750 1900
Wire Wire Line
	4750 1900 3400 1900
Wire Wire Line
	5000 1750 4700 1750
Wire Wire Line
	4700 1750 4700 1800
Wire Wire Line
	4700 1800 3400 1800
Wire Wire Line
	5000 1650 4650 1650
Wire Wire Line
	4650 1650 4650 1700
Wire Wire Line
	4650 1700 3400 1700
Wire Wire Line
	3400 1600 4600 1600
Wire Wire Line
	4600 1600 4600 1550
Wire Wire Line
	4600 1550 5000 1550
Text HLabel 4500 2400 0    50   Input ~ 0
U_OUT
Wire Wire Line
	4500 2400 5000 2400
$Sheet
S 5000 1500 500  950 
U 5E693F85
F0 "U Register Bus Out" 50
F1 "URegisterBusOutput.sch" 50
F2 "EN" I L 5000 2400 50 
F3 "D1" I L 5000 2250 50 
F4 "D2" I L 5000 2150 50 
F5 "D3" I L 5000 2050 50 
F6 "D4" I L 5000 1950 50 
F7 "D5" I L 5000 1850 50 
F8 "D6" I L 5000 1750 50 
F9 "D7" I L 5000 1650 50 
F10 "D8" I L 5000 1550 50 
F11 "Q8" O R 5500 1550 50 
F12 "Q7" O R 5500 1650 50 
F13 "Q6" O R 5500 1750 50 
F14 "Q5" O R 5500 1850 50 
F15 "Q4" O R 5500 1950 50 
F16 "Q3" O R 5500 2050 50 
F17 "Q2" O R 5500 2150 50 
F18 "Q1" O R 5500 2250 50 
$EndSheet
$EndSCHEMATC
