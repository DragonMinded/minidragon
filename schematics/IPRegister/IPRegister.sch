EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 167 374
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text GLabel 1500 1050 0    50   Input ~ 0
SYS_CLK
Text GLabel 1500 1950 0    50   Input ~ 0
SYS_RST
Wire Wire Line
	1500 1050 1900 1050
Wire Wire Line
	1500 1950 1950 1950
Wire Wire Line
	1950 1950 1950 3450
Wire Wire Line
	1950 3450 2000 3450
Connection ~ 1950 1950
Wire Wire Line
	1950 1950 2000 1950
Wire Wire Line
	2000 2550 1900 2550
Wire Wire Line
	1900 2550 1900 1050
Connection ~ 1900 1050
Wire Wire Line
	1900 1050 2000 1050
Text HLabel 1500 1150 0    50   Input ~ 0
IP_IN
Wire Wire Line
	1500 1150 1850 1150
Wire Wire Line
	1850 1150 1850 2650
Wire Wire Line
	1850 2650 2000 2650
Connection ~ 1850 1150
Wire Wire Line
	1850 1150 2000 1150
Text HLabel 1500 1450 0    50   BiDi ~ 0
IN_8
Text HLabel 1500 1550 0    50   BiDi ~ 0
IN_7
Text HLabel 1500 1650 0    50   BiDi ~ 0
IN_6
Text HLabel 1500 1750 0    50   BiDi ~ 0
IN_5
Text HLabel 1500 2950 0    50   BiDi ~ 0
IN_4
Text HLabel 1500 3050 0    50   BiDi ~ 0
IN_3
Text HLabel 1500 3150 0    50   BiDi ~ 0
IN_2
Text HLabel 1500 3250 0    50   BiDi ~ 0
IN_1
Wire Wire Line
	1500 3250 2000 3250
Wire Wire Line
	2000 3150 1500 3150
Wire Wire Line
	1500 3050 2000 3050
Wire Wire Line
	2000 2950 1500 2950
Wire Wire Line
	1500 1750 2000 1750
Wire Wire Line
	2000 1650 1500 1650
Wire Wire Line
	1500 1550 2000 1550
Wire Wire Line
	2000 1450 1500 1450
Text HLabel 9150 1550 2    50   BiDi ~ 0
OUT_ALU_8
Text HLabel 9150 1650 2    50   BiDi ~ 0
OUT_ALU_7
Text HLabel 9150 1750 2    50   BiDi ~ 0
OUT_ALU_6
Text HLabel 9150 1850 2    50   BiDi ~ 0
OUT_ALU_5
Text HLabel 9150 1950 2    50   BiDi ~ 0
OUT_ALU_4
Text HLabel 9150 2050 2    50   BiDi ~ 0
OUT_ALU_3
Text HLabel 9150 2150 2    50   BiDi ~ 0
OUT_ALU_2
Text HLabel 9150 2250 2    50   BiDi ~ 0
OUT_ALU_1
Wire Wire Line
	9050 1550 9150 1550
Wire Wire Line
	9050 1650 9150 1650
Wire Wire Line
	9050 1750 9150 1750
Wire Wire Line
	9050 1850 9150 1850
Wire Wire Line
	9050 1950 9150 1950
Wire Wire Line
	9050 2050 9150 2050
Wire Wire Line
	9050 2150 9150 2150
Wire Wire Line
	9050 2250 9150 2250
Text HLabel 8400 2400 0    50   Input ~ 0
IP_ALU_OUT
Wire Wire Line
	8400 2400 8500 2400
Text HLabel 9250 3550 2    50   BiDi ~ 0
OUT_ALU_16
Text HLabel 9250 3650 2    50   BiDi ~ 0
OUT_ALU_15
Text HLabel 9250 3750 2    50   BiDi ~ 0
OUT_ALU_14
Text HLabel 9250 3850 2    50   BiDi ~ 0
OUT_ALU_13
Text HLabel 9250 3950 2    50   BiDi ~ 0
OUT_ALU_12
Text HLabel 9250 4050 2    50   BiDi ~ 0
OUT_ALU_11
Text HLabel 9250 4150 2    50   BiDi ~ 0
OUT_ALU_10
Text HLabel 9250 4250 2    50   BiDi ~ 0
OUT_ALU_9
Wire Wire Line
	9100 4250 9250 4250
Wire Wire Line
	9250 4150 9100 4150
Wire Wire Line
	9100 4050 9250 4050
Wire Wire Line
	9250 3950 9100 3950
Wire Wire Line
	9100 3850 9250 3850
Wire Wire Line
	9250 3750 9100 3750
Wire Wire Line
	9100 3650 9250 3650
Wire Wire Line
	9250 3550 9100 3550
Wire Wire Line
	8500 2400 8500 4400
Wire Wire Line
	8500 4400 8550 4400
Connection ~ 8500 2400
Wire Wire Line
	8500 2400 8550 2400
$Sheet
S 2000 1000 500  1000
U 5E693C75
F0 "IP Register 2nd Nibble" 50
F1 "2ndNibble/4BitRegister.sch" 50
F2 "CLK" I L 2000 1050 50 
F3 "EN" I L 2000 1150 50 
F4 "D1" I L 2000 1750 50 
F5 "D2" I L 2000 1650 50 
F6 "D3" I L 2000 1550 50 
F7 "D4" I L 2000 1450 50 
F8 "RST" I L 2000 1950 50 
F9 "Q1" O R 2500 1350 50 
F10 "Q2" O R 2500 1250 50 
F11 "Q3" O R 2500 1150 50 
F12 "Q4" O R 2500 1050 50 
$EndSheet
$Sheet
S 2000 2500 550  1000
U 5E740283
F0 "IP Register 1st Nibble" 50
F1 "1stNibble/4BitRegister.sch" 50
F2 "CLK" I L 2000 2550 50 
F3 "EN" I L 2000 2650 50 
F4 "D1" I L 2000 3250 50 
F5 "D2" I L 2000 3150 50 
F6 "D3" I L 2000 3050 50 
F7 "D4" I L 2000 2950 50 
F8 "RST" I L 2000 3450 50 
F9 "Q1" O R 2550 2850 50 
F10 "Q2" O R 2550 2750 50 
F11 "Q3" O R 2550 2650 50 
F12 "Q4" O R 2550 2550 50 
$EndSheet
Text GLabel 1500 4050 0    50   Input ~ 0
SYS_CLK
Text GLabel 1500 4950 0    50   Input ~ 0
SYS_RST
Wire Wire Line
	1500 4050 1900 4050
Wire Wire Line
	1500 4950 1950 4950
Wire Wire Line
	1950 4950 1950 6450
Wire Wire Line
	1950 6450 2000 6450
Connection ~ 1950 4950
Wire Wire Line
	1950 4950 2000 4950
Wire Wire Line
	2000 5550 1900 5550
Wire Wire Line
	1900 5550 1900 4050
Connection ~ 1900 4050
Wire Wire Line
	1900 4050 2000 4050
Text HLabel 1500 4150 0    50   Input ~ 0
IP_IN
Wire Wire Line
	1500 4150 1850 4150
Wire Wire Line
	1850 4150 1850 5650
Wire Wire Line
	1850 5650 2000 5650
Connection ~ 1850 4150
Wire Wire Line
	1850 4150 2000 4150
Text HLabel 1500 4450 0    50   BiDi ~ 0
IN_16
Text HLabel 1500 4550 0    50   BiDi ~ 0
IN_15
Text HLabel 1500 4650 0    50   BiDi ~ 0
IN_14
Text HLabel 1500 4750 0    50   BiDi ~ 0
IN_13
Text HLabel 1500 5950 0    50   BiDi ~ 0
IN_12
Text HLabel 1500 6050 0    50   BiDi ~ 0
IN_11
Text HLabel 1500 6150 0    50   BiDi ~ 0
IN_10
Text HLabel 1500 6250 0    50   BiDi ~ 0
IN_9
Wire Wire Line
	1500 6250 2000 6250
Wire Wire Line
	2000 6150 1500 6150
Wire Wire Line
	1500 6050 2000 6050
Wire Wire Line
	2000 5950 1500 5950
Wire Wire Line
	1500 4750 2000 4750
Wire Wire Line
	2000 4650 1500 4650
Wire Wire Line
	1500 4550 2000 4550
Wire Wire Line
	2000 4450 1500 4450
$Sheet
S 2000 4000 500  1000
U 5E77319C
F0 "IP Register 4th Nibble" 50
F1 "4thNibble/4BitRegister.sch" 50
F2 "CLK" I L 2000 4050 50 
F3 "EN" I L 2000 4150 50 
F4 "D1" I L 2000 4750 50 
F5 "D2" I L 2000 4650 50 
F6 "D3" I L 2000 4550 50 
F7 "D4" I L 2000 4450 50 
F8 "RST" I L 2000 4950 50 
F9 "Q1" O R 2500 4350 50 
F10 "Q2" O R 2500 4250 50 
F11 "Q3" O R 2500 4150 50 
F12 "Q4" O R 2500 4050 50 
$EndSheet
$Sheet
S 2000 5500 550  1000
U 5FAAE93B
F0 "IP Register 3rd Nibble" 50
F1 "3rdNibble/4BitRegister.sch" 50
F2 "CLK" I L 2000 5550 50 
F3 "EN" I L 2000 5650 50 
F4 "D1" I L 2000 6250 50 
F5 "D2" I L 2000 6150 50 
F6 "D3" I L 2000 6050 50 
F7 "D4" I L 2000 5950 50 
F8 "RST" I L 2000 6450 50 
F9 "Q1" O R 2550 5850 50 
F10 "Q2" O R 2550 5750 50 
F11 "Q3" O R 2550 5650 50 
F12 "Q4" O R 2550 5550 50 
$EndSheet
Wire Wire Line
	2500 1050 4750 1050
Wire Wire Line
	4750 1050 4750 1550
Wire Wire Line
	4750 1550 5900 1550
Wire Wire Line
	8550 1650 5850 1650
Wire Wire Line
	4700 1650 4700 1150
Wire Wire Line
	4700 1150 2500 1150
Wire Wire Line
	2500 1250 4650 1250
Wire Wire Line
	4650 1250 4650 1750
Wire Wire Line
	4650 1750 5800 1750
Wire Wire Line
	2500 1350 4600 1350
Wire Wire Line
	4600 1350 4600 1850
Wire Wire Line
	4600 1850 5750 1850
Wire Wire Line
	2550 2550 3500 2550
Wire Wire Line
	3500 2550 3500 1950
Wire Wire Line
	3500 1950 5700 1950
Wire Wire Line
	8550 2050 5650 2050
Wire Wire Line
	3550 2050 3550 2650
Wire Wire Line
	3550 2650 2550 2650
Wire Wire Line
	2550 2750 3600 2750
Wire Wire Line
	3600 2750 3600 2150
Wire Wire Line
	3600 2150 5600 2150
Wire Wire Line
	8550 2250 5550 2250
Wire Wire Line
	3650 2250 3650 2850
Wire Wire Line
	3650 2850 2550 2850
Wire Wire Line
	2500 4050 4000 4050
Wire Wire Line
	4000 4050 4000 3550
Wire Wire Line
	4000 3550 5750 3550
Wire Wire Line
	2500 4150 4050 4150
Wire Wire Line
	4050 4150 4050 3650
Wire Wire Line
	4050 3650 5700 3650
Wire Wire Line
	2500 4250 4100 4250
Wire Wire Line
	4100 4250 4100 3750
Wire Wire Line
	4100 3750 5650 3750
Wire Wire Line
	2500 4350 4150 4350
Wire Wire Line
	4150 4350 4150 3850
Wire Wire Line
	4150 3850 5600 3850
Wire Wire Line
	2550 5550 4200 5550
Wire Wire Line
	4200 5550 4200 3950
Wire Wire Line
	4200 3950 5550 3950
Wire Wire Line
	4250 4050 4250 5650
Wire Wire Line
	4250 5650 2550 5650
Wire Wire Line
	2550 5750 4300 5750
Wire Wire Line
	4300 5750 4300 4150
Wire Wire Line
	4300 4150 5450 4150
Wire Wire Line
	8550 4250 5400 4250
Wire Wire Line
	4350 4250 4350 5850
Wire Wire Line
	4350 5850 2550 5850
$Sheet
S 8550 1500 500  950 
U 5FAAE937
F0 "IP Register ALU Lower Bus Out" 50
F1 "IPRegisterALUBusOutputLower.sch" 50
F2 "EN" I L 8550 2400 50 
F3 "D1" I L 8550 2250 50 
F4 "D2" I L 8550 2150 50 
F5 "D3" I L 8550 2050 50 
F6 "D4" I L 8550 1950 50 
F7 "D5" I L 8550 1850 50 
F8 "D6" I L 8550 1750 50 
F9 "D7" I L 8550 1650 50 
F10 "D8" I L 8550 1550 50 
F11 "Q8" O R 9050 1550 50 
F12 "Q7" O R 9050 1650 50 
F13 "Q6" O R 9050 1750 50 
F14 "Q5" O R 9050 1850 50 
F15 "Q4" O R 9050 1950 50 
F16 "Q3" O R 9050 2050 50 
F17 "Q2" O R 9050 2150 50 
F18 "Q1" O R 9050 2250 50 
$EndSheet
$Sheet
S 8550 3500 550  950 
U 5FAAE938
F0 "IP Register ALU Upper Bus Output" 50
F1 "IPRegisterALUBusOutputUpper.sch" 50
F2 "EN" I L 8550 4400 50 
F3 "D1" I L 8550 4250 50 
F4 "D2" I L 8550 4150 50 
F5 "D3" I L 8550 4050 50 
F6 "D4" I L 8550 3950 50 
F7 "D5" I L 8550 3850 50 
F8 "D6" I L 8550 3750 50 
F9 "D7" I L 8550 3650 50 
F10 "D8" I L 8550 3550 50 
F11 "Q8" O R 9100 3550 50 
F12 "Q7" O R 9100 3650 50 
F13 "Q6" O R 9100 3750 50 
F14 "Q5" O R 9100 3850 50 
F15 "Q4" O R 9100 3950 50 
F16 "Q3" O R 9100 4050 50 
F17 "Q2" O R 9100 4150 50 
F18 "Q1" O R 9100 4250 50 
$EndSheet
$Sheet
S 6100 2450 500  950 
U 5ED1CC06
F0 "IP Register Address Lower Bus Out" 50
F1 "IPRegisterAddressBusOutputLower.sch" 50
F2 "EN" I L 6100 3350 50 
F3 "D1" I L 6100 3200 50 
F4 "D2" I L 6100 3100 50 
F5 "D3" I L 6100 3000 50 
F6 "D4" I L 6100 2900 50 
F7 "D5" I L 6100 2800 50 
F8 "D6" I L 6100 2700 50 
F9 "D7" I L 6100 2600 50 
F10 "D8" I L 6100 2500 50 
F11 "Q8" O R 6600 2500 50 
F12 "Q7" O R 6600 2600 50 
F13 "Q6" O R 6600 2700 50 
F14 "Q5" O R 6600 2800 50 
F15 "Q4" O R 6600 2900 50 
F16 "Q3" O R 6600 3000 50 
F17 "Q2" O R 6600 3100 50 
F18 "Q1" O R 6600 3200 50 
$EndSheet
$Sheet
S 6100 4400 500  950 
U 5ED2344E
F0 "IP Register Address Upper Bus Out" 50
F1 "IPRegisterAddressBusOutputUpper.sch" 50
F2 "EN" I L 6100 5300 50 
F3 "D1" I L 6100 5150 50 
F4 "D2" I L 6100 5050 50 
F5 "D3" I L 6100 4950 50 
F6 "D4" I L 6100 4850 50 
F7 "D5" I L 6100 4750 50 
F8 "D6" I L 6100 4650 50 
F9 "D7" I L 6100 4550 50 
F10 "D8" I L 6100 4450 50 
F11 "Q8" O R 6600 4450 50 
F12 "Q7" O R 6600 4550 50 
F13 "Q6" O R 6600 4650 50 
F14 "Q5" O R 6600 4750 50 
F15 "Q4" O R 6600 4850 50 
F16 "Q3" O R 6600 4950 50 
F17 "Q2" O R 6600 5050 50 
F18 "Q1" O R 6600 5150 50 
$EndSheet
Text HLabel 5850 3350 0    50   Input ~ 0
IP_ADDR_OUT
Wire Wire Line
	5850 3350 6000 3350
Wire Wire Line
	6000 3350 6000 5300
Wire Wire Line
	6000 5300 6100 5300
Connection ~ 6000 3350
Wire Wire Line
	6000 3350 6100 3350
Wire Wire Line
	6100 2500 5900 2500
Wire Wire Line
	5900 2500 5900 1550
Connection ~ 5900 1550
Wire Wire Line
	5900 1550 8550 1550
Wire Wire Line
	5850 1650 5850 2600
Wire Wire Line
	5850 2600 6100 2600
Connection ~ 5850 1650
Wire Wire Line
	5850 1650 4700 1650
Wire Wire Line
	6100 2700 5800 2700
Wire Wire Line
	5800 2700 5800 1750
Connection ~ 5800 1750
Wire Wire Line
	5800 1750 8550 1750
Wire Wire Line
	5750 1850 5750 2800
Wire Wire Line
	5750 2800 6100 2800
Connection ~ 5750 1850
Wire Wire Line
	5750 1850 8550 1850
Wire Wire Line
	6100 2900 5700 2900
Wire Wire Line
	5700 2900 5700 1950
Connection ~ 5700 1950
Wire Wire Line
	5700 1950 8550 1950
Wire Wire Line
	5650 2050 5650 3000
Wire Wire Line
	5650 3000 6100 3000
Connection ~ 5650 2050
Wire Wire Line
	5650 2050 3550 2050
Wire Wire Line
	6100 3100 5600 3100
Wire Wire Line
	5600 3100 5600 2150
Connection ~ 5600 2150
Wire Wire Line
	5600 2150 8550 2150
Wire Wire Line
	5550 2250 5550 3200
Wire Wire Line
	5550 3200 6100 3200
Connection ~ 5550 2250
Wire Wire Line
	5550 2250 3650 2250
Wire Wire Line
	6100 4450 5750 4450
Wire Wire Line
	5750 4450 5750 3550
Connection ~ 5750 3550
Wire Wire Line
	5750 3550 8550 3550
Wire Wire Line
	5700 3650 5700 4550
Wire Wire Line
	5700 4550 6100 4550
Connection ~ 5700 3650
Wire Wire Line
	5700 3650 8550 3650
Wire Wire Line
	6100 4650 5650 4650
Wire Wire Line
	5650 4650 5650 3750
Connection ~ 5650 3750
Wire Wire Line
	5650 3750 8550 3750
Wire Wire Line
	5600 3850 5600 4750
Wire Wire Line
	5600 4750 6100 4750
Connection ~ 5600 3850
Wire Wire Line
	5600 3850 8550 3850
Wire Wire Line
	8550 4050 5500 4050
Wire Wire Line
	6100 4850 5550 4850
Wire Wire Line
	5550 4850 5550 3950
Connection ~ 5550 3950
Wire Wire Line
	5550 3950 8550 3950
Wire Wire Line
	5500 4050 5500 4950
Wire Wire Line
	5500 4950 6100 4950
Connection ~ 5500 4050
Wire Wire Line
	5500 4050 4250 4050
Wire Wire Line
	6100 5050 5450 5050
Wire Wire Line
	5450 5050 5450 4150
Connection ~ 5450 4150
Wire Wire Line
	5450 4150 8550 4150
Wire Wire Line
	5400 4250 5400 5150
Wire Wire Line
	5400 5150 6100 5150
Connection ~ 5400 4250
Wire Wire Line
	5400 4250 4350 4250
Text HLabel 6750 4450 2    50   BiDi ~ 0
OUT_ADDR_16
Text HLabel 6750 4550 2    50   BiDi ~ 0
OUT_ADDR_15
Text HLabel 6750 4650 2    50   BiDi ~ 0
OUT_ADDR_14
Text HLabel 6750 4750 2    50   BiDi ~ 0
OUT_ADDR_13
Text HLabel 6750 4850 2    50   BiDi ~ 0
OUT_ADDR_12
Text HLabel 6750 4950 2    50   BiDi ~ 0
OUT_ADDR_11
Text HLabel 6750 5050 2    50   BiDi ~ 0
OUT_ADDR_10
Text HLabel 6750 5150 2    50   BiDi ~ 0
OUT_ADDR_9
Wire Wire Line
	6600 4450 6750 4450
Wire Wire Line
	6750 4550 6600 4550
Wire Wire Line
	6600 4650 6750 4650
Wire Wire Line
	6750 4750 6600 4750
Wire Wire Line
	6600 4850 6750 4850
Wire Wire Line
	6750 4950 6600 4950
Wire Wire Line
	6600 5050 6750 5050
Wire Wire Line
	6750 5150 6600 5150
Text HLabel 6750 2500 2    50   BiDi ~ 0
OUT_ADDR_8
Text HLabel 6750 2600 2    50   BiDi ~ 0
OUT_ADDR_7
Text HLabel 6750 2700 2    50   BiDi ~ 0
OUT_ADDR_6
Text HLabel 6750 2800 2    50   BiDi ~ 0
OUT_ADDR_5
Text HLabel 6750 2900 2    50   BiDi ~ 0
OUT_ADDR_4
Text HLabel 6750 3000 2    50   BiDi ~ 0
OUT_ADDR_3
Text HLabel 6750 3100 2    50   BiDi ~ 0
OUT_ADDR_2
Text HLabel 6750 3200 2    50   BiDi ~ 0
OUT_ADDR_1
Wire Wire Line
	6600 2500 6750 2500
Wire Wire Line
	6750 2600 6600 2600
Wire Wire Line
	6600 2700 6750 2700
Wire Wire Line
	6750 2800 6600 2800
Wire Wire Line
	6600 2900 6750 2900
Wire Wire Line
	6750 3000 6600 3000
Wire Wire Line
	6600 3100 6750 3100
Wire Wire Line
	6750 3200 6600 3200
$EndSCHEMATC
