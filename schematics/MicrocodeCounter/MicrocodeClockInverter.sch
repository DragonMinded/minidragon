EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 53 126
Title "NOT Gate"
Date "2019-12-22"
Rev "2"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Device:R R?
U 1 1 5DFE9DA1
P 1850 1750
F 0 "R?" V 1643 1750 50  0000 C CNN
F 1 "10K" V 1734 1750 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1780 1750 50  0001 C CNN
F 3 "~" H 1850 1750 50  0001 C CNN
	1    1850 1750
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5DFF02F8
P 2400 1750
F 0 "Q?" H 2590 1796 50  0000 L CNN
F 1 "2N2222" H 2590 1705 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2600 1675 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2400 1750 50  0001 L CNN
	1    2400 1750
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5DFF0877
P 4000 1550
F 0 "Q?" H 4190 1596 50  0000 L CNN
F 1 "2N2222" H 4190 1505 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4200 1475 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4000 1550 50  0001 L CNN
	1    4000 1550
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5DFF0FDB
P 3200 2500
F 0 "Q?" H 3390 2546 50  0000 L CNN
F 1 "2N2222" H 3390 2455 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3400 2425 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3200 2500 50  0001 L CNN
	1    3200 2500
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5DFF1C55
P 3450 1550
F 0 "R?" V 3243 1550 50  0000 C CNN
F 1 "10K" V 3334 1550 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3380 1550 50  0001 C CNN
F 3 "~" H 3450 1550 50  0001 C CNN
	1    3450 1550
	0    1    1    0   
$EndComp
$Comp
L Device:R R?
U 1 1 5DFF216E
P 4750 2050
F 0 "R?" V 4957 2050 50  0000 C CNN
F 1 "1K" V 4866 2050 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4680 2050 50  0001 C CNN
F 3 "~" H 4750 2050 50  0001 C CNN
	1    4750 2050
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 5DFF26F6
P 3300 3050
F 0 "R?" H 3370 3096 50  0000 L CNN
F 1 "1K" H 3370 3005 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3230 3050 50  0001 C CNN
F 3 "~" H 3300 3050 50  0001 C CNN
	1    3300 3050
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5DFF2C2A
P 2500 1200
F 0 "R?" H 2570 1246 50  0000 L CNN
F 1 "1K" H 2570 1155 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2430 1200 50  0001 C CNN
F 3 "~" H 2500 1200 50  0001 C CNN
	1    2500 1200
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5DFF329B
P 2500 850
F 0 "#PWR?" H 2500 700 50  0001 C CNN
F 1 "VCC" H 2517 1023 50  0000 C CNN
F 2 "" H 2500 850 50  0001 C CNN
F 3 "" H 2500 850 50  0001 C CNN
	1    2500 850 
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5DFF37A8
P 4100 1150
F 0 "#PWR?" H 4100 1000 50  0001 C CNN
F 1 "VCC" H 4117 1323 50  0000 C CNN
F 2 "" H 4100 1150 50  0001 C CNN
F 3 "" H 4100 1150 50  0001 C CNN
	1    4100 1150
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5DFF408B
P 2500 2150
F 0 "#PWR?" H 2500 1900 50  0001 C CNN
F 1 "GND" H 2505 1977 50  0000 C CNN
F 2 "" H 2500 2150 50  0001 C CNN
F 3 "" H 2500 2150 50  0001 C CNN
	1    2500 2150
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5DFF4633
P 4900 2300
F 0 "#PWR?" H 4900 2050 50  0001 C CNN
F 1 "GND" H 4905 2127 50  0000 C CNN
F 2 "" H 4900 2300 50  0001 C CNN
F 3 "" H 4900 2300 50  0001 C CNN
	1    4900 2300
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5DFF4A3D
P 3300 3400
F 0 "#PWR?" H 3300 3150 50  0001 C CNN
F 1 "GND" H 3305 3227 50  0000 C CNN
F 2 "" H 3300 3400 50  0001 C CNN
F 3 "" H 3300 3400 50  0001 C CNN
	1    3300 3400
	1    0    0    -1  
$EndComp
$Comp
L Device:LED D?
U 1 1 5DFF937B
P 4250 2050
F 0 "D?" H 4250 1950 50  0000 C CNN
F 1 "RED" H 4250 2150 50  0000 C CNN
F 2 "LED_THT:LED_D5.0mm" H 4250 2050 50  0001 C CNN
F 3 "~" H 4250 2050 50  0001 C CNN
	1    4250 2050
	-1   0    0    1   
$EndComp
Wire Wire Line
	1500 1750 1700 1750
Wire Wire Line
	2000 1750 2200 1750
Wire Wire Line
	2500 1950 2500 2150
Wire Wire Line
	2500 1550 2500 1350
Wire Wire Line
	2500 1050 2500 850 
Wire Wire Line
	3300 1550 3000 1550
Connection ~ 2500 1550
Wire Wire Line
	3600 1550 3800 1550
Wire Wire Line
	4100 1350 4100 1150
Wire Wire Line
	3300 3200 3300 3400
Wire Wire Line
	3300 2900 3300 2700
Connection ~ 3300 2900
$Comp
L power:VCC #PWR?
U 1 1 5DFFB9CB
P 3300 2100
F 0 "#PWR?" H 3300 1950 50  0001 C CNN
F 1 "VCC" H 3317 2273 50  0000 C CNN
F 2 "" H 3300 2100 50  0001 C CNN
F 3 "" H 3300 2100 50  0001 C CNN
	1    3300 2100
	1    0    0    -1  
$EndComp
Wire Wire Line
	3300 2300 3300 2100
Wire Wire Line
	3000 2500 3000 1550
Connection ~ 3000 1550
Wire Wire Line
	3000 1550 2500 1550
Wire Wire Line
	4100 1750 4100 2050
Wire Wire Line
	4400 2050 4600 2050
Wire Notes Line
	1250 550  1250 3700
Wire Notes Line
	1250 3700 5050 3700
Wire Notes Line
	5050 3700 5050 550 
Wire Notes Line
	5050 550  1250 550 
Text Notes 1300 3650 0    50   ~ 0
NOT Gate w/Output Indicator
Text Notes 4250 3650 0    50   ~ 0
284ns rise delay\n2.4us fall delay\n10mA current draw
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E010D1B
P 1500 3350
F 0 "J?" V 1654 3162 50  0000 R CNN
F 1 "Power" V 1563 3162 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1500 3350 50  0001 C CNN
F 3 "~" H 1500 3350 50  0001 C CNN
	1    1500 3350
	0    -1   -1   0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E0120BA
P 1500 3000
F 0 "#PWR?" H 1500 2850 50  0001 C CNN
F 1 "VCC" H 1450 3150 50  0000 C CNN
F 2 "" H 1500 3000 50  0001 C CNN
F 3 "" H 1500 3000 50  0001 C CNN
	1    1500 3000
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E012766
P 1600 3000
F 0 "#PWR?" H 1600 2750 50  0001 C CNN
F 1 "GND" H 1550 2850 50  0000 C CNN
F 2 "" H 1600 3000 50  0001 C CNN
F 3 "" H 1600 3000 50  0001 C CNN
	1    1600 3000
	-1   0    0    1   
$EndComp
Wire Wire Line
	1500 3150 1500 3000
Wire Wire Line
	1600 3150 1600 3000
Wire Wire Line
	3300 2900 3650 2900
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5DFF2116
P 2000 3350
F 0 "J?" V 2154 3162 50  0000 R CNN
F 1 "Power" V 2063 3162 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 2000 3350 50  0001 C CNN
F 3 "~" H 2000 3350 50  0001 C CNN
	1    2000 3350
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5DFF2E7D
P 2450 3350
F 0 "J?" V 2604 3162 50  0000 R CNN
F 1 "Power" V 2513 3162 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 2450 3350 50  0001 C CNN
F 3 "~" H 2450 3350 50  0001 C CNN
	1    2450 3350
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5DFF3B4A
P 2100 3000
F 0 "#PWR?" H 2100 2750 50  0001 C CNN
F 1 "GND" H 2050 2850 50  0000 C CNN
F 2 "" H 2100 3000 50  0001 C CNN
F 3 "" H 2100 3000 50  0001 C CNN
	1    2100 3000
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5DFF434B
P 2550 3000
F 0 "#PWR?" H 2550 2750 50  0001 C CNN
F 1 "GND" H 2500 2850 50  0000 C CNN
F 2 "" H 2550 3000 50  0001 C CNN
F 3 "" H 2550 3000 50  0001 C CNN
	1    2550 3000
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5DFF4A43
P 2000 3000
F 0 "#PWR?" H 2000 2850 50  0001 C CNN
F 1 "VCC" H 1950 3150 50  0000 C CNN
F 2 "" H 2000 3000 50  0001 C CNN
F 3 "" H 2000 3000 50  0001 C CNN
	1    2000 3000
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5DFF5116
P 2450 3000
F 0 "#PWR?" H 2450 2850 50  0001 C CNN
F 1 "VCC" H 2400 3150 50  0000 C CNN
F 2 "" H 2450 3000 50  0001 C CNN
F 3 "" H 2450 3000 50  0001 C CNN
	1    2450 3000
	1    0    0    -1  
$EndComp
Wire Wire Line
	2000 3000 2000 3150
Wire Wire Line
	2100 3150 2100 3000
Wire Wire Line
	2450 3000 2450 3150
Wire Wire Line
	2550 3150 2550 3000
Wire Wire Line
	4900 2050 4900 2300
$Comp
L power:VCC #PWR?
U 1 1 5E004479
P 4500 2650
F 0 "#PWR?" H 4500 2500 50  0001 C CNN
F 1 "VCC" H 4517 2823 50  0000 C CNN
F 2 "" H 4500 2650 50  0001 C CNN
F 3 "" H 4500 2650 50  0001 C CNN
	1    4500 2650
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E004D93
P 4500 3150
F 0 "#PWR?" H 4500 2900 50  0001 C CNN
F 1 "GND" H 4505 2977 50  0000 C CNN
F 2 "" H 4500 3150 50  0001 C CNN
F 3 "" H 4500 3150 50  0001 C CNN
	1    4500 3150
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 5E005357
P 4500 2900
F 0 "C?" H 4615 2946 50  0000 L CNN
F 1 "0.1uF" H 4615 2855 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 4538 2750 50  0001 C CNN
F 3 "~" H 4500 2900 50  0001 C CNN
	1    4500 2900
	1    0    0    -1  
$EndComp
Wire Wire Line
	4500 2650 4500 2750
Wire Wire Line
	4500 3050 4500 3150
Text HLabel 1500 1750 0    50   Input ~ 0
D
Text HLabel 3650 2900 2    50   Output ~ 0
Q
$EndSCHEMATC
