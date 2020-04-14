EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 478
Title "AND Gate"
Date "2020-03-05"
Rev "2"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Device:R R1
U 1 1 5E860EB0
P 1650 1750
F 0 "R1" V 1443 1750 50  0000 C CNN
F 1 "10K" V 1534 1750 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1580 1750 50  0001 C CNN
F 3 "~" H 1650 1750 50  0001 C CNN
	1    1650 1750
	0    1    1    0   
$EndComp
$Comp
L Device:R R2
U 1 1 5E00386C
P 1650 2250
F 0 "R2" V 1443 2250 50  0000 C CNN
F 1 "10K" V 1534 2250 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1580 2250 50  0001 C CNN
F 3 "~" H 1650 2250 50  0001 C CNN
	1    1650 2250
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q1
U 1 1 5E860EB8
P 2050 1750
F 0 "Q1" H 2240 1796 50  0000 L CNN
F 1 "2N2222" H 2240 1705 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2250 1675 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2050 1750 50  0001 L CNN
	1    2050 1750
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q2
U 1 1 5E860EC0
P 2050 2250
F 0 "Q2" H 2240 2296 50  0000 L CNN
F 1 "2N2222" H 2240 2205 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2250 2175 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2050 2250 50  0001 L CNN
	1    2050 2250
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0101
U 1 1 5E860EC2
P 2150 2550
F 0 "#PWR0101" H 2150 2300 50  0001 C CNN
F 1 "GND" H 2155 2377 50  0000 C CNN
F 2 "" H 2150 2550 50  0001 C CNN
F 3 "" H 2150 2550 50  0001 C CNN
	1    2150 2550
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0102
U 1 1 5E860EC8
P 2150 950
F 0 "#PWR0102" H 2150 800 50  0001 C CNN
F 1 "VCC" H 2167 1123 50  0000 C CNN
F 2 "" H 2150 950 50  0001 C CNN
F 3 "" H 2150 950 50  0001 C CNN
	1    2150 950 
	1    0    0    -1  
$EndComp
$Comp
L Device:R R3
U 1 1 5E860ED4
P 2150 1200
F 0 "R3" H 2220 1246 50  0000 L CNN
F 1 "1K" H 2220 1155 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2080 1200 50  0001 C CNN
F 3 "~" H 2150 1200 50  0001 C CNN
	1    2150 1200
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x02_Male J1
U 1 1 5E00BB5D
P 1100 3450
F 0 "J1" V 1254 3262 50  0000 R CNN
F 1 "Power" V 1163 3262 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1100 3450 50  0001 C CNN
F 3 "~" H 1100 3450 50  0001 C CNN
	1    1100 3450
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J4
U 1 1 5E860F05
P 1550 3450
F 0 "J4" V 1704 3262 50  0000 R CNN
F 1 "Power" V 1613 3262 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1550 3450 50  0001 C CNN
F 3 "~" H 1550 3450 50  0001 C CNN
	1    1550 3450
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J5
U 1 1 5E00CDF6
P 2000 3450
F 0 "J5" V 2154 3262 50  0000 R CNN
F 1 "Power" V 2063 3262 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 2000 3450 50  0001 C CNN
F 3 "~" H 2000 3450 50  0001 C CNN
	1    2000 3450
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR0107
U 1 1 5E860F0B
P 1200 3100
F 0 "#PWR0107" H 1200 2850 50  0001 C CNN
F 1 "GND" H 1150 2950 50  0000 C CNN
F 2 "" H 1200 3100 50  0001 C CNN
F 3 "" H 1200 3100 50  0001 C CNN
	1    1200 3100
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR0108
U 1 1 5E860F10
P 1650 3100
F 0 "#PWR0108" H 1650 2850 50  0001 C CNN
F 1 "GND" H 1600 2950 50  0000 C CNN
F 2 "" H 1650 3100 50  0001 C CNN
F 3 "" H 1650 3100 50  0001 C CNN
	1    1650 3100
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR0109
U 1 1 5E860F14
P 2100 3100
F 0 "#PWR0109" H 2100 2850 50  0001 C CNN
F 1 "GND" H 2050 2950 50  0000 C CNN
F 2 "" H 2100 3100 50  0001 C CNN
F 3 "" H 2100 3100 50  0001 C CNN
	1    2100 3100
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR0110
U 1 1 5E860F19
P 2000 3100
F 0 "#PWR0110" H 2000 2950 50  0001 C CNN
F 1 "VCC" H 1950 3250 50  0000 C CNN
F 2 "" H 2000 3100 50  0001 C CNN
F 3 "" H 2000 3100 50  0001 C CNN
	1    2000 3100
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0111
U 1 1 5E860F1B
P 1550 3100
F 0 "#PWR0111" H 1550 2950 50  0001 C CNN
F 1 "VCC" H 1500 3250 50  0000 C CNN
F 2 "" H 1550 3100 50  0001 C CNN
F 3 "" H 1550 3100 50  0001 C CNN
	1    1550 3100
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0112
U 1 1 5E860F1E
P 1100 3100
F 0 "#PWR0112" H 1100 2950 50  0001 C CNN
F 1 "VCC" H 1050 3250 50  0000 C CNN
F 2 "" H 1100 3100 50  0001 C CNN
F 3 "" H 1100 3100 50  0001 C CNN
	1    1100 3100
	1    0    0    -1  
$EndComp
Wire Wire Line
	1100 3250 1100 3100
Wire Wire Line
	1200 3250 1200 3100
Wire Wire Line
	1550 3100 1550 3250
Wire Wire Line
	1650 3250 1650 3100
Wire Wire Line
	2000 3100 2000 3250
Wire Wire Line
	2100 3250 2100 3100
Wire Wire Line
	1800 1750 1850 1750
Wire Wire Line
	1350 1750 1500 1750
Wire Wire Line
	1500 2250 1350 2250
Wire Notes Line
	900  650  900  3850
Text Notes 950  3800 0    50   ~ 0
AND Gate w/Output Indicator
$Comp
L power:GND #PWR0104
U 1 1 5E860EEC
P 5200 1950
F 0 "#PWR0104" H 5200 1700 50  0001 C CNN
F 1 "GND" H 5205 1777 50  0000 C CNN
F 2 "" H 5200 1950 50  0001 C CNN
F 3 "" H 5200 1950 50  0001 C CNN
	1    5200 1950
	1    0    0    -1  
$EndComp
Wire Wire Line
	5200 1800 5200 1950
Wire Wire Line
	4750 1800 4900 1800
Wire Wire Line
	4450 1600 4450 1800
Wire Wire Line
	4450 1200 4450 1050
$Comp
L Device:R R6
U 1 1 5E860EE9
P 5050 1800
F 0 "R6" V 4843 1800 50  0000 C CNN
F 1 "1K" V 4934 1800 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4980 1800 50  0001 C CNN
F 3 "~" H 5050 1800 50  0001 C CNN
	1    5050 1800
	0    1    1    0   
$EndComp
$Comp
L Device:LED D1
U 1 1 5E860EE2
P 4600 1800
F 0 "D1" H 4600 1700 50  0000 C CNN
F 1 "RED" H 4600 1900 50  0000 C CNN
F 2 "LED_THT:LED_D5.0mm" H 4600 1800 50  0001 C CNN
F 3 "~" H 4600 1800 50  0001 C CNN
	1    4600 1800
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR0103
U 1 1 5E860EDF
P 4450 1050
F 0 "#PWR0103" H 4450 900 50  0001 C CNN
F 1 "VCC" H 4467 1223 50  0000 C CNN
F 2 "" H 4450 1050 50  0001 C CNN
F 3 "" H 4450 1050 50  0001 C CNN
	1    4450 1050
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q4
U 1 1 5E860EDD
P 4350 1400
F 0 "Q4" H 4540 1446 50  0000 L CNN
F 1 "2N2222" H 4540 1355 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4550 1325 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4350 1400 50  0001 L CNN
	1    4350 1400
	1    0    0    -1  
$EndComp
Wire Wire Line
	3650 2100 3650 1400
$Comp
L Device:R R4
U 1 1 5E005961
P 3800 1400
F 0 "R4" V 3593 1400 50  0000 C CNN
F 1 "10K" V 3684 1400 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3730 1400 50  0001 C CNN
F 3 "~" H 3800 1400 50  0001 C CNN
	1    3800 1400
	0    1    1    0   
$EndComp
Wire Wire Line
	3950 1400 4150 1400
Wire Wire Line
	3950 1900 3950 1750
$Comp
L power:VCC #PWR0105
U 1 1 5E009F64
P 3950 1750
F 0 "#PWR0105" H 3950 1600 50  0001 C CNN
F 1 "VCC" H 3967 1923 50  0000 C CNN
F 2 "" H 3950 1750 50  0001 C CNN
F 3 "" H 3950 1750 50  0001 C CNN
	1    3950 1750
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q3
U 1 1 5E860EF0
P 3850 2100
F 0 "Q3" H 4040 2146 50  0000 L CNN
F 1 "2N2222" H 4040 2055 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4050 2025 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3850 2100 50  0001 L CNN
	1    3850 2100
	1    0    0    -1  
$EndComp
Connection ~ 3950 2500
Wire Wire Line
	3950 2500 3950 2300
Wire Wire Line
	3950 2500 4250 2500
Wire Wire Line
	3950 3000 3950 2800
$Comp
L power:GND #PWR0106
U 1 1 5E860EFC
P 3950 3000
F 0 "#PWR0106" H 3950 2750 50  0001 C CNN
F 1 "GND" H 3955 2827 50  0000 C CNN
F 2 "" H 3950 3000 50  0001 C CNN
F 3 "" H 3950 3000 50  0001 C CNN
	1    3950 3000
	1    0    0    -1  
$EndComp
$Comp
L Device:R R5
U 1 1 5E860EF9
P 3950 2650
F 0 "R5" H 4020 2696 50  0000 L CNN
F 1 "1K" H 4020 2605 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3880 2650 50  0001 C CNN
F 3 "~" H 3950 2650 50  0001 C CNN
	1    3950 2650
	1    0    0    -1  
$EndComp
Wire Wire Line
	4900 2900 4900 3000
Wire Wire Line
	4900 2500 4900 2600
$Comp
L power:GND #PWR02
U 1 1 5E860ECF
P 4900 3000
F 0 "#PWR02" H 4900 2750 50  0001 C CNN
F 1 "GND" H 4905 2827 50  0000 C CNN
F 2 "" H 4900 3000 50  0001 C CNN
F 3 "" H 4900 3000 50  0001 C CNN
	1    4900 3000
	1    0    0    -1  
$EndComp
$Comp
L Device:C C1
U 1 1 5E860ECD
P 4900 2750
F 0 "C1" H 5015 2796 50  0000 L CNN
F 1 "0.1uF" H 5015 2705 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 4938 2600 50  0001 C CNN
F 3 "~" H 4900 2750 50  0001 C CNN
	1    4900 2750
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR01
U 1 1 5E860EBC
P 4900 2500
F 0 "#PWR01" H 4900 2350 50  0001 C CNN
F 1 "VCC" H 4917 2673 50  0000 C CNN
F 2 "" H 4900 2500 50  0001 C CNN
F 3 "" H 4900 2500 50  0001 C CNN
	1    4900 2500
	1    0    0    -1  
$EndComp
Wire Wire Line
	1800 2250 1850 2250
Wire Wire Line
	2150 2550 2150 2450
Wire Wire Line
	2150 950  2150 1050
Wire Wire Line
	2150 2050 2150 1950
$Comp
L 2n2222:2N2222 Q5
U 1 1 5E860F27
P 3000 1750
F 0 "Q5" H 3190 1796 50  0000 L CNN
F 1 "2N2222" H 3190 1705 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3200 1675 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3000 1750 50  0001 L CNN
	1    3000 1750
	1    0    0    -1  
$EndComp
$Comp
L Device:R R8
U 1 1 5E860F2A
P 3100 1150
F 0 "R8" H 3170 1196 50  0000 L CNN
F 1 "1K" H 3170 1105 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3030 1150 50  0001 C CNN
F 3 "~" H 3100 1150 50  0001 C CNN
	1    3100 1150
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR03
U 1 1 5E860F2C
P 3100 900
F 0 "#PWR03" H 3100 750 50  0001 C CNN
F 1 "VCC" H 3117 1073 50  0000 C CNN
F 2 "" H 3100 900 50  0001 C CNN
F 3 "" H 3100 900 50  0001 C CNN
	1    3100 900 
	1    0    0    -1  
$EndComp
Wire Wire Line
	3100 1000 3100 900 
Wire Wire Line
	2800 1450 2800 1750
$Comp
L power:GND #PWR04
U 1 1 5E629F0D
P 3100 2050
F 0 "#PWR04" H 3100 1800 50  0001 C CNN
F 1 "GND" H 3105 1877 50  0000 C CNN
F 2 "" H 3100 2050 50  0001 C CNN
F 3 "" H 3100 2050 50  0001 C CNN
	1    3100 2050
	1    0    0    -1  
$EndComp
Wire Wire Line
	3100 1950 3100 2050
Wire Wire Line
	2150 1350 2150 1450
$Comp
L Device:R R7
U 1 1 5E860F2F
P 2500 1450
F 0 "R7" V 2293 1450 50  0000 C CNN
F 1 "10K" V 2384 1450 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2430 1450 50  0001 C CNN
F 3 "~" H 2500 1450 50  0001 C CNN
	1    2500 1450
	0    1    1    0   
$EndComp
Wire Wire Line
	2150 1450 2350 1450
Connection ~ 2150 1450
Wire Wire Line
	2150 1450 2150 1550
Wire Wire Line
	2650 1450 2800 1450
Wire Wire Line
	3100 1300 3100 1400
Wire Wire Line
	3650 1400 3100 1400
Connection ~ 3650 1400
Connection ~ 3100 1400
Wire Wire Line
	3100 1400 3100 1550
Wire Notes Line
	5350 650  5350 3850
Wire Notes Line
	900  3850 5350 3850
Wire Notes Line
	900  650  5350 650 
Text HLabel 4250 2500 2    50   Output ~ 0
OUT
Text HLabel 1350 1750 0    50   Input ~ 0
A
Text HLabel 1350 2250 0    50   Input ~ 0
B
$EndSCHEMATC
