EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 97 373
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text HLabel 1500 1000 0    50   Input ~ 0
A_16
Text HLabel 1500 1100 0    50   Input ~ 0
A_15
Text HLabel 1500 1200 0    50   Input ~ 0
A_14
Text HLabel 1500 1300 0    50   Input ~ 0
A_13
Text HLabel 1500 1400 0    50   Input ~ 0
A_12
Text HLabel 1500 1500 0    50   Input ~ 0
A_11
Text HLabel 1500 1600 0    50   Input ~ 0
A_10
Text HLabel 1500 1700 0    50   Input ~ 0
A_9
Text HLabel 1500 1800 0    50   Input ~ 0
A_8
Text HLabel 1500 1900 0    50   Input ~ 0
A_7
Text HLabel 1500 2000 0    50   Input ~ 0
A_6
Text HLabel 1500 2100 0    50   Input ~ 0
A_5
Text HLabel 1500 2200 0    50   Input ~ 0
A_4
Text HLabel 1500 2300 0    50   Input ~ 0
A_3
Text HLabel 1500 2400 0    50   Input ~ 0
A_2
Text HLabel 1500 2500 0    50   Input ~ 0
A_1
Text HLabel 1500 3000 0    50   Input ~ 0
B_16
Text HLabel 1500 3100 0    50   Input ~ 0
B_15
Text HLabel 1500 3200 0    50   Input ~ 0
B_14
Text HLabel 1500 3300 0    50   Input ~ 0
B_13
Text HLabel 1500 3400 0    50   Input ~ 0
B_12
Text HLabel 1500 3500 0    50   Input ~ 0
B_11
Text HLabel 1500 3600 0    50   Input ~ 0
B_10
Text HLabel 1500 3700 0    50   Input ~ 0
B_9
Text HLabel 1500 3800 0    50   Input ~ 0
B_8
Text HLabel 1500 3900 0    50   Input ~ 0
B_7
Text HLabel 1500 4000 0    50   Input ~ 0
B_6
Text HLabel 1500 4100 0    50   Input ~ 0
B_5
Text HLabel 1500 4200 0    50   Input ~ 0
B_4
Text HLabel 1500 4300 0    50   Input ~ 0
B_3
Text HLabel 1500 4400 0    50   Input ~ 0
B_2
Text HLabel 1500 4500 0    50   Input ~ 0
B_1
$Sheet
S 8000 1000 500  1000
U 5E764A00
F0 "ALU High Bits Out" 50
F1 "ALUBusOutputUpper.sch" 50
F2 "EN" I L 8000 1950 50 
F3 "D1" I L 8000 1750 50 
F4 "D2" I L 8000 1650 50 
F5 "D3" I L 8000 1550 50 
F6 "D4" I L 8000 1450 50 
F7 "D5" I L 8000 1350 50 
F8 "D6" I L 8000 1250 50 
F9 "D7" I L 8000 1150 50 
F10 "D8" I L 8000 1050 50 
F11 "Q8" O R 8500 1050 50 
F12 "Q7" O R 8500 1150 50 
F13 "Q6" O R 8500 1250 50 
F14 "Q5" O R 8500 1350 50 
F15 "Q4" O R 8500 1450 50 
F16 "Q3" O R 8500 1550 50 
F17 "Q2" O R 8500 1650 50 
F18 "Q1" O R 8500 1750 50 
$EndSheet
$Sheet
S 8000 2500 500  1000
U 5E764A33
F0 "ALU Low Bits Output" 50
F1 "ALUBusOutputLower.sch" 50
F2 "EN" I L 8000 3450 50 
F3 "D1" I L 8000 3250 50 
F4 "D2" I L 8000 3150 50 
F5 "D3" I L 8000 3050 50 
F6 "D4" I L 8000 2950 50 
F7 "D5" I L 8000 2850 50 
F8 "D6" I L 8000 2750 50 
F9 "D7" I L 8000 2650 50 
F10 "D8" I L 8000 2550 50 
F11 "Q8" O R 8500 2550 50 
F12 "Q7" O R 8500 2650 50 
F13 "Q6" O R 8500 2750 50 
F14 "Q5" O R 8500 2850 50 
F15 "Q4" O R 8500 2950 50 
F16 "Q3" O R 8500 3050 50 
F17 "Q2" O R 8500 3150 50 
F18 "Q1" O R 8500 3250 50 
$EndSheet
Text HLabel 7500 1950 0    50   Input ~ 0
ALU_OUT
Wire Wire Line
	7500 1950 7950 1950
Wire Wire Line
	7950 1950 7950 3450
Wire Wire Line
	7950 3450 8000 3450
Connection ~ 7950 1950
Wire Wire Line
	7950 1950 8000 1950
Text HLabel 10000 1050 2    50   Output ~ 0
Q_16
Text HLabel 10000 1150 2    50   Output ~ 0
Q_15
Text HLabel 10000 1250 2    50   Output ~ 0
Q_14
Text HLabel 10000 1350 2    50   Output ~ 0
Q_13
Text HLabel 10000 1450 2    50   Output ~ 0
Q_12
Text HLabel 10000 1550 2    50   Output ~ 0
Q_11
Text HLabel 10000 1650 2    50   Output ~ 0
Q_10
Text HLabel 10000 1750 2    50   Output ~ 0
Q_9
Wire Wire Line
	8500 1050 10000 1050
Wire Wire Line
	8500 1150 10000 1150
Wire Wire Line
	10000 1250 8500 1250
Wire Wire Line
	8500 1350 10000 1350
Wire Wire Line
	10000 1450 8500 1450
Wire Wire Line
	8500 1550 10000 1550
Wire Wire Line
	10000 1650 8500 1650
Wire Wire Line
	8500 1750 10000 1750
Text HLabel 10000 2550 2    50   Output ~ 0
Q_8
Text HLabel 10000 2650 2    50   Output ~ 0
Q_7
Text HLabel 10000 2750 2    50   Output ~ 0
Q_6
Text HLabel 10000 2850 2    50   Output ~ 0
Q_5
Text HLabel 10000 2950 2    50   Output ~ 0
Q_4
Text HLabel 10000 3050 2    50   Output ~ 0
Q_3
Text HLabel 10000 3150 2    50   Output ~ 0
Q_2
Text HLabel 10000 3250 2    50   Output ~ 0
Q_1
Wire Wire Line
	8500 2550 9500 2550
Wire Wire Line
	10000 2650 9550 2650
Wire Wire Line
	8500 2750 9600 2750
Wire Wire Line
	10000 2850 9650 2850
Wire Wire Line
	8500 2950 9700 2950
Wire Wire Line
	10000 3050 9750 3050
Wire Wire Line
	8500 3150 9800 3150
Wire Wire Line
	10000 3250 9850 3250
$Sheet
S 8000 4000 500  1000
U 5E7A11F5
F0 "ALU High To Low Output" 50
F1 "ALULowBusOutput.sch" 50
F2 "EN" I L 8000 4950 50 
F3 "D1" I L 8000 4750 50 
F4 "D2" I L 8000 4650 50 
F5 "D3" I L 8000 4550 50 
F6 "D4" I L 8000 4450 50 
F7 "D5" I L 8000 4350 50 
F8 "D6" I L 8000 4250 50 
F9 "D7" I L 8000 4150 50 
F10 "D8" I L 8000 4050 50 
F11 "Q8" O R 8500 4050 50 
F12 "Q7" O R 8500 4150 50 
F13 "Q6" O R 8500 4250 50 
F14 "Q5" O R 8500 4350 50 
F15 "Q4" O R 8500 4450 50 
F16 "Q3" O R 8500 4550 50 
F17 "Q2" O R 8500 4650 50 
F18 "Q1" O R 8500 4750 50 
$EndSheet
Wire Wire Line
	8500 4050 9500 4050
Wire Wire Line
	9500 4050 9500 2550
Connection ~ 9500 2550
Wire Wire Line
	9500 2550 10000 2550
Wire Wire Line
	9550 2650 9550 4150
Wire Wire Line
	9550 4150 8500 4150
Connection ~ 9550 2650
Wire Wire Line
	9550 2650 8500 2650
Wire Wire Line
	8500 4250 9600 4250
Wire Wire Line
	9600 4250 9600 2750
Connection ~ 9600 2750
Wire Wire Line
	9600 2750 10000 2750
Wire Wire Line
	9650 2850 9650 4350
Wire Wire Line
	9650 4350 8500 4350
Connection ~ 9650 2850
Wire Wire Line
	9650 2850 8500 2850
Wire Wire Line
	8500 4450 9700 4450
Wire Wire Line
	9700 4450 9700 2950
Connection ~ 9700 2950
Wire Wire Line
	9700 2950 10000 2950
Wire Wire Line
	9750 3050 9750 4550
Wire Wire Line
	9750 4550 8500 4550
Connection ~ 9750 3050
Wire Wire Line
	9750 3050 8500 3050
Wire Wire Line
	8500 4650 9800 4650
Wire Wire Line
	9800 4650 9800 3150
Connection ~ 9800 3150
Wire Wire Line
	9800 3150 10000 3150
Wire Wire Line
	9850 3250 9850 4750
Wire Wire Line
	9850 4750 8500 4750
Connection ~ 9850 3250
Wire Wire Line
	9850 3250 8500 3250
Text HLabel 7500 4950 0    50   Input ~ 0
ALU_LOW_OUT
Wire Wire Line
	7500 4950 8000 4950
Text HLabel 1500 5000 0    50   Input ~ 0
CF
Text HLabel 1500 5100 0    50   Input ~ 0
ALU_OP_2
Text HLabel 1500 5200 0    50   Input ~ 0
ALU_OP_1
Text HLabel 1500 5300 0    50   Input ~ 0
ALU_OP_0
Text HLabel 1500 6000 0    50   Input ~ 0
CARRY_SET
Text HLabel 1500 6100 0    50   Input ~ 0
CARRY_CLEAR
Text HLabel 1500 6200 0    50   Input ~ 0
CARRY_FROM_FLAGS
Text HLabel 10000 5500 2    50   Output ~ 0
CARRY_RES
Text HLabel 10000 5600 2    50   Output ~ 0
ZERO_RES
$EndSCHEMATC
