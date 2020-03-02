EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 7 126
Title "NAND Gate"
Date "2019-12-22"
Rev "1"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Device:R R?
U 1 1 5E6220BA
P 1650 1750
F 0 "R?" V 1443 1750 50  0000 C CNN
F 1 "10K" V 1534 1750 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1580 1750 50  0001 C CNN
F 3 "~" H 1650 1750 50  0001 C CNN
	1    1650 1750
	0    1    1    0   
$EndComp
$Comp
L Device:R R?
U 1 1 5E6220BB
P 1650 2250
F 0 "R?" V 1443 2250 50  0000 C CNN
F 1 "10K" V 1534 2250 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1580 2250 50  0001 C CNN
F 3 "~" H 1650 2250 50  0001 C CNN
	1    1650 2250
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E60769F
P 2200 1750
F 0 "Q?" H 2390 1796 50  0000 L CNN
F 1 "2N2222" H 2390 1705 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2400 1675 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2200 1750 50  0001 L CNN
	1    2200 1750
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E6220BE
P 2200 2250
F 0 "Q?" H 2390 2296 50  0000 L CNN
F 1 "2N2222" H 2390 2205 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2400 2175 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2200 2250 50  0001 L CNN
	1    2200 2250
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0265
U 1 1 5E6076A2
P 2300 2600
F 0 "#PWR0265" H 2300 2350 50  0001 C CNN
F 1 "GND" H 2305 2427 50  0000 C CNN
F 2 "" H 2300 2600 50  0001 C CNN
F 3 "" H 2300 2600 50  0001 C CNN
	1    2300 2600
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0266
U 1 1 5E6220C0
P 2300 950
F 0 "#PWR0266" H 2300 800 50  0001 C CNN
F 1 "VCC" H 2317 1123 50  0000 C CNN
F 2 "" H 2300 950 50  0001 C CNN
F 3 "" H 2300 950 50  0001 C CNN
	1    2300 950 
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E6076A6
P 2300 1250
F 0 "R?" H 2370 1296 50  0000 L CNN
F 1 "1K" H 2370 1205 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2230 1250 50  0001 C CNN
F 3 "~" H 2300 1250 50  0001 C CNN
	1    2300 1250
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E62A43A
P 3000 1550
F 0 "R?" V 2793 1550 50  0000 C CNN
F 1 "10K" V 2884 1550 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2930 1550 50  0001 C CNN
F 3 "~" H 3000 1550 50  0001 C CNN
	1    3000 1550
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E6076A8
P 3550 1550
F 0 "Q?" H 3740 1596 50  0000 L CNN
F 1 "2N2222" H 3740 1505 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3750 1475 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3550 1550 50  0001 L CNN
	1    3550 1550
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0267
U 1 1 5E6076A9
P 3650 1200
F 0 "#PWR0267" H 3650 1050 50  0001 C CNN
F 1 "VCC" H 3667 1373 50  0000 C CNN
F 2 "" H 3650 1200 50  0001 C CNN
F 3 "" H 3650 1200 50  0001 C CNN
	1    3650 1200
	1    0    0    -1  
$EndComp
$Comp
L Device:LED D?
U 1 1 5E6076AA
P 3800 1950
F 0 "D?" H 3800 1850 50  0000 C CNN
F 1 "RED" H 3800 2050 50  0000 C CNN
F 2 "LED_THT:LED_D5.0mm" H 3800 1950 50  0001 C CNN
F 3 "~" H 3800 1950 50  0001 C CNN
	1    3800 1950
	-1   0    0    1   
$EndComp
$Comp
L Device:R R?
U 1 1 5E6076AB
P 4250 1950
F 0 "R?" V 4043 1950 50  0000 C CNN
F 1 "1K" V 4134 1950 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4180 1950 50  0001 C CNN
F 3 "~" H 4250 1950 50  0001 C CNN
	1    4250 1950
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR0268
U 1 1 5E6076AC
P 4400 2100
F 0 "#PWR0268" H 4400 1850 50  0001 C CNN
F 1 "GND" H 4405 1927 50  0000 C CNN
F 2 "" H 4400 2100 50  0001 C CNN
F 3 "" H 4400 2100 50  0001 C CNN
	1    4400 2100
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E6076AD
P 3050 2250
F 0 "Q?" H 3240 2296 50  0000 L CNN
F 1 "2N2222" H 3240 2205 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3250 2175 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3050 2250 50  0001 L CNN
	1    3050 2250
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0269
U 1 1 5E62A441
P 3150 1900
F 0 "#PWR0269" H 3150 1750 50  0001 C CNN
F 1 "VCC" H 3167 2073 50  0000 C CNN
F 2 "" H 3150 1900 50  0001 C CNN
F 3 "" H 3150 1900 50  0001 C CNN
	1    3150 1900
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E62A442
P 3150 2800
F 0 "R?" H 3220 2846 50  0000 L CNN
F 1 "1K" H 3220 2755 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3080 2800 50  0001 C CNN
F 3 "~" H 3150 2800 50  0001 C CNN
	1    3150 2800
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0270
U 1 1 5E62A443
P 3150 3150
F 0 "#PWR0270" H 3150 2900 50  0001 C CNN
F 1 "GND" H 3155 2977 50  0000 C CNN
F 2 "" H 3150 3150 50  0001 C CNN
F 3 "" H 3150 3150 50  0001 C CNN
	1    3150 3150
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E62A444
P 1100 3450
F 0 "J?" V 1254 3262 50  0000 R CNN
F 1 "Power" V 1163 3262 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1100 3450 50  0001 C CNN
F 3 "~" H 1100 3450 50  0001 C CNN
	1    1100 3450
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E62A445
P 1550 3450
F 0 "J?" V 1704 3262 50  0000 R CNN
F 1 "Power" V 1613 3262 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1550 3450 50  0001 C CNN
F 3 "~" H 1550 3450 50  0001 C CNN
	1    1550 3450
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E6076B3
P 2000 3450
F 0 "J?" V 2154 3262 50  0000 R CNN
F 1 "Power" V 2063 3262 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 2000 3450 50  0001 C CNN
F 3 "~" H 2000 3450 50  0001 C CNN
	1    2000 3450
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR0271
U 1 1 5E6076B4
P 1200 3100
F 0 "#PWR0271" H 1200 2850 50  0001 C CNN
F 1 "GND" H 1150 2950 50  0000 C CNN
F 2 "" H 1200 3100 50  0001 C CNN
F 3 "" H 1200 3100 50  0001 C CNN
	1    1200 3100
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR0272
U 1 1 5E6220D2
P 1650 3100
F 0 "#PWR0272" H 1650 2850 50  0001 C CNN
F 1 "GND" H 1600 2950 50  0000 C CNN
F 2 "" H 1650 3100 50  0001 C CNN
F 3 "" H 1650 3100 50  0001 C CNN
	1    1650 3100
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR0273
U 1 1 5E6220D3
P 2100 3100
F 0 "#PWR0273" H 2100 2850 50  0001 C CNN
F 1 "GND" H 2050 2950 50  0000 C CNN
F 2 "" H 2100 3100 50  0001 C CNN
F 3 "" H 2100 3100 50  0001 C CNN
	1    2100 3100
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR0274
U 1 1 5E6220D4
P 2000 3100
F 0 "#PWR0274" H 2000 2950 50  0001 C CNN
F 1 "VCC" H 1950 3250 50  0000 C CNN
F 2 "" H 2000 3100 50  0001 C CNN
F 3 "" H 2000 3100 50  0001 C CNN
	1    2000 3100
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0275
U 1 1 5E6220D5
P 1550 3100
F 0 "#PWR0275" H 1550 2950 50  0001 C CNN
F 1 "VCC" H 1500 3250 50  0000 C CNN
F 2 "" H 1550 3100 50  0001 C CNN
F 3 "" H 1550 3100 50  0001 C CNN
	1    1550 3100
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0276
U 1 1 5E5DB4F0
P 1100 3100
F 0 "#PWR0276" H 1100 2950 50  0001 C CNN
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
	3150 3150 3150 2950
Wire Wire Line
	3150 2650 3450 2650
Wire Wire Line
	3150 2650 3150 2450
Connection ~ 3150 2650
Wire Wire Line
	3150 2050 3150 1900
Wire Wire Line
	3150 1550 3350 1550
Wire Wire Line
	3650 1350 3650 1200
Wire Wire Line
	3650 1750 3650 1950
Wire Wire Line
	3950 1950 4100 1950
Wire Wire Line
	4400 1950 4400 2100
Wire Wire Line
	2850 2250 2850 1550
Wire Wire Line
	2850 1550 2300 1550
Connection ~ 2850 1550
Wire Wire Line
	2300 1400 2300 1550
Connection ~ 2300 1550
Wire Wire Line
	2300 1100 2300 950 
Wire Wire Line
	2300 1950 2300 2050
Wire Wire Line
	2300 2450 2300 2600
Wire Wire Line
	1800 2250 2000 2250
Wire Wire Line
	1800 1750 2000 1750
Wire Wire Line
	1350 1750 1500 1750
Wire Wire Line
	1500 2250 1350 2250
$Comp
L power:VCC #PWR0277
U 1 1 5E6076A0
P 4100 2650
F 0 "#PWR0277" H 4100 2500 50  0001 C CNN
F 1 "VCC" H 4117 2823 50  0000 C CNN
F 2 "" H 4100 2650 50  0001 C CNN
F 3 "" H 4100 2650 50  0001 C CNN
	1    4100 2650
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 5E6220C1
P 4100 2900
F 0 "C?" H 4215 2946 50  0000 L CNN
F 1 "0.1uF" H 4215 2855 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 4138 2750 50  0001 C CNN
F 3 "~" H 4100 2900 50  0001 C CNN
	1    4100 2900
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0278
U 1 1 5E6076A5
P 4100 3150
F 0 "#PWR0278" H 4100 2900 50  0001 C CNN
F 1 "GND" H 4105 2977 50  0000 C CNN
F 2 "" H 4100 3150 50  0001 C CNN
F 3 "" H 4100 3150 50  0001 C CNN
	1    4100 3150
	1    0    0    -1  
$EndComp
Wire Wire Line
	4100 2650 4100 2750
Wire Wire Line
	4100 3050 4100 3150
Wire Notes Line
	900  3850 4500 3850
Wire Notes Line
	4500 3850 4500 650 
Wire Notes Line
	4500 650  900  650 
Wire Notes Line
	900  650  900  3850
Text Notes 950  3800 0    50   ~ 0
NAND Gate w/Output Indicator
Text Notes 3700 3800 0    50   ~ 0
330ns rise delay\n2.6us fall delay\n16mA current draw
Text HLabel 1350 1750 0    50   Input ~ 0
A
Text HLabel 1350 2250 0    50   Input ~ 0
B
Text HLabel 3450 2650 2    50   Output ~ 0
OUT
$EndSCHEMATC
