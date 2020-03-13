EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 54 372
Title "AND Gate"
Date "2020-02-19"
Rev "1"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Device:R R?
U 1 1 5E00314A
P 1650 1300
F 0 "R?" V 1443 1300 50  0000 C CNN
F 1 "10K" V 1534 1300 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1580 1300 50  0001 C CNN
F 3 "~" H 1650 1300 50  0001 C CNN
	1    1650 1300
	0    1    1    0   
$EndComp
$Comp
L Device:R R?
U 1 1 5E00386C
P 1650 1800
F 0 "R?" V 1443 1800 50  0000 C CNN
F 1 "10K" V 1534 1800 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1580 1800 50  0001 C CNN
F 3 "~" H 1650 1800 50  0001 C CNN
	1    1650 1800
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E003FCF
P 2050 1300
F 0 "Q?" H 2240 1346 50  0000 L CNN
F 1 "2N2222" H 2240 1255 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2250 1225 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2050 1300 50  0001 L CNN
	1    2050 1300
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E5DB4D8
P 2050 1800
F 0 "Q?" H 2240 1846 50  0000 L CNN
F 1 "2N2222" H 2240 1755 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2250 1725 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2050 1800 50  0001 L CNN
	1    2050 1800
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E004B05
P 2150 2550
F 0 "#PWR?" H 2150 2300 50  0001 C CNN
F 1 "GND" H 2155 2377 50  0000 C CNN
F 2 "" H 2150 2550 50  0001 C CNN
F 3 "" H 2150 2550 50  0001 C CNN
	1    2150 2550
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E5DB4DA
P 2150 950
F 0 "#PWR?" H 2150 800 50  0001 C CNN
F 1 "VCC" H 2167 1123 50  0000 C CNN
F 2 "" H 2150 950 50  0001 C CNN
F 3 "" H 2150 950 50  0001 C CNN
	1    2150 950 
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E0055EF
P 2150 2300
F 0 "R?" H 2220 2346 50  0000 L CNN
F 1 "1K" H 2220 2255 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2080 2300 50  0001 C CNN
F 3 "~" H 2150 2300 50  0001 C CNN
	1    2150 2300
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E5DB4E8
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
U 1 1 5E5DB4E9
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
U 1 1 5E5DB4EA
P 2000 3450
F 0 "J?" V 2154 3262 50  0000 R CNN
F 1 "Power" V 2063 3262 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 2000 3450 50  0001 C CNN
F 3 "~" H 2000 3450 50  0001 C CNN
	1    2000 3450
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E5DB4EB
P 1200 3100
F 0 "#PWR?" H 1200 2850 50  0001 C CNN
F 1 "GND" H 1150 2950 50  0000 C CNN
F 2 "" H 1200 3100 50  0001 C CNN
F 3 "" H 1200 3100 50  0001 C CNN
	1    1200 3100
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E5DB4EC
P 1650 3100
F 0 "#PWR?" H 1650 2850 50  0001 C CNN
F 1 "GND" H 1600 2950 50  0000 C CNN
F 2 "" H 1650 3100 50  0001 C CNN
F 3 "" H 1650 3100 50  0001 C CNN
	1    1650 3100
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E5DB4ED
P 2100 3100
F 0 "#PWR?" H 2100 2850 50  0001 C CNN
F 1 "GND" H 2050 2950 50  0000 C CNN
F 2 "" H 2100 3100 50  0001 C CNN
F 3 "" H 2100 3100 50  0001 C CNN
	1    2100 3100
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E5DB4EE
P 2000 3100
F 0 "#PWR?" H 2000 2950 50  0001 C CNN
F 1 "VCC" H 1950 3250 50  0000 C CNN
F 2 "" H 2000 3100 50  0001 C CNN
F 3 "" H 2000 3100 50  0001 C CNN
	1    2000 3100
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E5DB4EF
P 1550 3100
F 0 "#PWR?" H 1550 2950 50  0001 C CNN
F 1 "VCC" H 1500 3250 50  0000 C CNN
F 2 "" H 1550 3100 50  0001 C CNN
F 3 "" H 1550 3100 50  0001 C CNN
	1    1550 3100
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E00E93A
P 1100 3100
F 0 "#PWR?" H 1100 2950 50  0001 C CNN
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
	2150 1500 2150 1600
Wire Wire Line
	2150 2000 2150 2100
Wire Wire Line
	1800 1300 1850 1300
Wire Wire Line
	1350 1300 1500 1300
Wire Wire Line
	1500 1800 1350 1800
Wire Notes Line
	900  3850 4500 3850
Wire Notes Line
	4500 3850 4500 650 
Wire Notes Line
	4500 650  900  650 
Wire Notes Line
	900  650  900  3850
Text Notes 950  3800 0    50   ~ 0
AND Gate w/Output Indicator
Wire Wire Line
	2150 950  2150 1100
$Comp
L power:GND #PWR?
U 1 1 5E5DB4E3
P 4400 1950
F 0 "#PWR?" H 4400 1700 50  0001 C CNN
F 1 "GND" H 4405 1777 50  0000 C CNN
F 2 "" H 4400 1950 50  0001 C CNN
F 3 "" H 4400 1950 50  0001 C CNN
	1    4400 1950
	1    0    0    -1  
$EndComp
Wire Wire Line
	4400 1800 4400 1950
Wire Wire Line
	3950 1800 4100 1800
Wire Wire Line
	3650 1600 3650 1800
Wire Wire Line
	3650 1200 3650 1050
$Comp
L Device:R R?
U 1 1 5E5DB4E2
P 4250 1800
F 0 "R?" V 4043 1800 50  0000 C CNN
F 1 "1K" V 4134 1800 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4180 1800 50  0001 C CNN
F 3 "~" H 4250 1800 50  0001 C CNN
	1    4250 1800
	0    1    1    0   
$EndComp
$Comp
L Device:LED D?
U 1 1 5E5DB4E1
P 3800 1800
F 0 "D?" H 3800 1700 50  0000 C CNN
F 1 "RED" H 3800 1900 50  0000 C CNN
F 2 "LED_THT:LED_D5.0mm" H 3800 1800 50  0001 C CNN
F 3 "~" H 3800 1800 50  0001 C CNN
	1    3800 1800
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E5DB4E0
P 3650 1050
F 0 "#PWR?" H 3650 900 50  0001 C CNN
F 1 "VCC" H 3667 1223 50  0000 C CNN
F 2 "" H 3650 1050 50  0001 C CNN
F 3 "" H 3650 1050 50  0001 C CNN
	1    3650 1050
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E5DB4DF
P 3550 1400
F 0 "Q?" H 3740 1446 50  0000 L CNN
F 1 "2N2222" H 3740 1355 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3750 1325 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3550 1400 50  0001 L CNN
	1    3550 1400
	1    0    0    -1  
$EndComp
Wire Wire Line
	2850 2100 2850 1400
$Comp
L Device:R R?
U 1 1 5E5DB4DE
P 3000 1400
F 0 "R?" V 2793 1400 50  0000 C CNN
F 1 "10K" V 2884 1400 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2930 1400 50  0001 C CNN
F 3 "~" H 3000 1400 50  0001 C CNN
	1    3000 1400
	0    1    1    0   
$EndComp
Wire Wire Line
	3150 1400 3350 1400
Wire Wire Line
	3150 1900 3150 1750
$Comp
L power:VCC #PWR?
U 1 1 5E5DB4E5
P 3150 1750
F 0 "#PWR?" H 3150 1600 50  0001 C CNN
F 1 "VCC" H 3167 1923 50  0000 C CNN
F 2 "" H 3150 1750 50  0001 C CNN
F 3 "" H 3150 1750 50  0001 C CNN
	1    3150 1750
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E5DB4E4
P 3050 2100
F 0 "Q?" H 3240 2146 50  0000 L CNN
F 1 "2N2222" H 3240 2055 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3250 2025 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3050 2100 50  0001 L CNN
	1    3050 2100
	1    0    0    -1  
$EndComp
Connection ~ 3150 2500
Wire Wire Line
	3150 2500 3150 2300
Wire Wire Line
	3150 2500 3450 2500
Wire Wire Line
	3150 3000 3150 2800
$Comp
L power:GND #PWR?
U 1 1 5E5DB4E7
P 3150 3000
F 0 "#PWR?" H 3150 2750 50  0001 C CNN
F 1 "GND" H 3155 2827 50  0000 C CNN
F 2 "" H 3150 3000 50  0001 C CNN
F 3 "" H 3150 3000 50  0001 C CNN
	1    3150 3000
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E5DB4E6
P 3150 2650
F 0 "R?" H 3220 2696 50  0000 L CNN
F 1 "1K" H 3220 2605 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3080 2650 50  0001 C CNN
F 3 "~" H 3150 2650 50  0001 C CNN
	1    3150 2650
	1    0    0    -1  
$EndComp
Wire Wire Line
	4100 2900 4100 3000
Wire Wire Line
	4100 2500 4100 2600
$Comp
L power:GND #PWR?
U 1 1 5E005518
P 4100 3000
F 0 "#PWR?" H 4100 2750 50  0001 C CNN
F 1 "GND" H 4105 2827 50  0000 C CNN
F 2 "" H 4100 3000 50  0001 C CNN
F 3 "" H 4100 3000 50  0001 C CNN
	1    4100 3000
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 5E5DB4DB
P 4100 2750
F 0 "C?" H 4215 2796 50  0000 L CNN
F 1 "0.1uF" H 4215 2705 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 4138 2600 50  0001 C CNN
F 3 "~" H 4100 2750 50  0001 C CNN
	1    4100 2750
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E5DB4D7
P 4100 2500
F 0 "#PWR?" H 4100 2350 50  0001 C CNN
F 1 "VCC" H 4117 2673 50  0000 C CNN
F 2 "" H 4100 2500 50  0001 C CNN
F 3 "" H 4100 2500 50  0001 C CNN
	1    4100 2500
	1    0    0    -1  
$EndComp
Wire Wire Line
	1800 1800 1850 1800
Wire Wire Line
	2150 2550 2150 2450
Wire Wire Line
	2850 2100 2150 2100
Connection ~ 2850 2100
Connection ~ 2150 2100
Wire Wire Line
	2150 2100 2150 2150
Text HLabel 3450 2500 2    50   Output ~ 0
Q
Text HLabel 1350 1300 0    50   Input ~ 0
A
Text HLabel 1350 1800 0    50   Input ~ 0
B
$EndSCHEMATC
