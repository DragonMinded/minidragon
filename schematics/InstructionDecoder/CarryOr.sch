EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 372 372
Title "OR Gate"
Date "2020-03-05"
Rev "2"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Device:R R?
U 1 1 5E00314A
P 1100 1600
F 0 "R?" V 893 1600 50  0000 C CNN
F 1 "10K" V 984 1600 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1030 1600 50  0001 C CNN
F 3 "~" H 1100 1600 50  0001 C CNN
	1    1100 1600
	-1   0    0    1   
$EndComp
$Comp
L Device:R R?
U 1 1 5E00386C
P 1550 1300
F 0 "R?" V 1343 1300 50  0000 C CNN
F 1 "10K" V 1434 1300 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1480 1300 50  0001 C CNN
F 3 "~" H 1550 1300 50  0001 C CNN
	1    1550 1300
	0    -1   -1   0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E003FCF
P 1450 1750
F 0 "Q?" H 1640 1796 50  0000 L CNN
F 1 "2N2222" H 1640 1705 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 1650 1675 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 1450 1750 50  0001 L CNN
	1    1450 1750
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E004750
P 2200 1750
F 0 "Q?" H 2390 1796 50  0000 L CNN
F 1 "2N2222" H 2390 1705 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2400 1675 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2200 1750 50  0001 L CNN
	1    2200 1750
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E004B05
P 2300 2150
F 0 "#PWR?" H 2300 1900 50  0001 C CNN
F 1 "GND" H 2305 1977 50  0000 C CNN
F 2 "" H 2300 2150 50  0001 C CNN
F 3 "" H 2300 2150 50  0001 C CNN
	1    2300 2150
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E004F7F
P 2300 950
F 0 "#PWR?" H 2300 800 50  0001 C CNN
F 1 "VCC" H 2317 1123 50  0000 C CNN
F 2 "" H 2300 950 50  0001 C CNN
F 3 "" H 2300 950 50  0001 C CNN
	1    2300 950 
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E0055EF
P 2300 1200
F 0 "R?" H 2370 1246 50  0000 L CNN
F 1 "1K" H 2370 1155 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2230 1200 50  0001 C CNN
F 3 "~" H 2300 1200 50  0001 C CNN
	1    2300 1200
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E005961
P 3850 1500
F 0 "R?" V 3643 1500 50  0000 C CNN
F 1 "10K" V 3734 1500 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3780 1500 50  0001 C CNN
F 3 "~" H 3850 1500 50  0001 C CNN
	1    3850 1500
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E005EDC
P 4400 1500
F 0 "Q?" H 4590 1546 50  0000 L CNN
F 1 "2N2222" H 4590 1455 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4600 1425 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4400 1500 50  0001 L CNN
	1    4400 1500
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E006BD5
P 4500 1150
F 0 "#PWR?" H 4500 1000 50  0001 C CNN
F 1 "VCC" H 4517 1323 50  0000 C CNN
F 2 "" H 4500 1150 50  0001 C CNN
F 3 "" H 4500 1150 50  0001 C CNN
	1    4500 1150
	1    0    0    -1  
$EndComp
$Comp
L Device:LED D?
U 1 1 5E007338
P 4650 1900
F 0 "D?" H 4650 1800 50  0000 C CNN
F 1 "RED" H 4650 2000 50  0000 C CNN
F 2 "LED_THT:LED_D5.0mm" H 4650 1900 50  0001 C CNN
F 3 "~" H 4650 1900 50  0001 C CNN
	1    4650 1900
	-1   0    0    1   
$EndComp
$Comp
L Device:R R?
U 1 1 5E008365
P 5100 1900
F 0 "R?" V 4893 1900 50  0000 C CNN
F 1 "1K" V 4984 1900 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5030 1900 50  0001 C CNN
F 3 "~" H 5100 1900 50  0001 C CNN
	1    5100 1900
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E0089FD
P 5250 2050
F 0 "#PWR?" H 5250 1800 50  0001 C CNN
F 1 "GND" H 5255 1877 50  0000 C CNN
F 2 "" H 5250 2050 50  0001 C CNN
F 3 "" H 5250 2050 50  0001 C CNN
	1    5250 2050
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E008FC9
P 3900 2200
F 0 "Q?" H 4090 2246 50  0000 L CNN
F 1 "2N2222" H 4090 2155 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4100 2125 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3900 2200 50  0001 L CNN
	1    3900 2200
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E009F64
P 4000 1850
F 0 "#PWR?" H 4000 1700 50  0001 C CNN
F 1 "VCC" H 4017 2023 50  0000 C CNN
F 2 "" H 4000 1850 50  0001 C CNN
F 3 "" H 4000 1850 50  0001 C CNN
	1    4000 1850
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E00A57F
P 4000 2750
F 0 "R?" H 4070 2796 50  0000 L CNN
F 1 "1K" H 4070 2705 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3930 2750 50  0001 C CNN
F 3 "~" H 4000 2750 50  0001 C CNN
	1    4000 2750
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E00A879
P 4000 3100
F 0 "#PWR?" H 4000 2850 50  0001 C CNN
F 1 "GND" H 4005 2927 50  0000 C CNN
F 2 "" H 4000 3100 50  0001 C CNN
F 3 "" H 4000 3100 50  0001 C CNN
	1    4000 3100
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E00BB5D
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
U 1 1 5E00C75D
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
U 1 1 5E00CDF6
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
U 1 1 5E00D9C6
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
U 1 1 5E00DE6D
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
U 1 1 5E00E103
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
U 1 1 5E00E45C
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
U 1 1 5E00E6C4
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
	4000 3100 4000 2900
Wire Wire Line
	4000 2600 4300 2600
Wire Wire Line
	4000 2600 4000 2400
Connection ~ 4000 2600
Wire Wire Line
	4000 2000 4000 1850
Wire Wire Line
	4000 1500 4200 1500
Wire Wire Line
	4500 1300 4500 1150
Wire Wire Line
	4500 1700 4500 1900
Wire Wire Line
	4800 1900 4950 1900
Wire Wire Line
	5250 1900 5250 2050
$Comp
L power:VCC #PWR?
U 1 1 5E004739
P 4950 2600
F 0 "#PWR?" H 4950 2450 50  0001 C CNN
F 1 "VCC" H 4967 2773 50  0000 C CNN
F 2 "" H 4950 2600 50  0001 C CNN
F 3 "" H 4950 2600 50  0001 C CNN
	1    4950 2600
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 5E005056
P 4950 2850
F 0 "C?" H 5065 2896 50  0000 L CNN
F 1 "0.1uF" H 5065 2805 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 4988 2700 50  0001 C CNN
F 3 "~" H 4950 2850 50  0001 C CNN
	1    4950 2850
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E005518
P 4950 3100
F 0 "#PWR?" H 4950 2850 50  0001 C CNN
F 1 "GND" H 4955 2927 50  0000 C CNN
F 2 "" H 4950 3100 50  0001 C CNN
F 3 "" H 4950 3100 50  0001 C CNN
	1    4950 3100
	1    0    0    -1  
$EndComp
Wire Wire Line
	4950 2600 4950 2700
Wire Wire Line
	4950 3000 4950 3100
Wire Notes Line
	900  650  900  3850
Text Notes 950  3800 0    50   ~ 0
OR Gate w/Output Indicator
Connection ~ 2300 1550
Wire Wire Line
	1100 1050 1100 1450
Wire Wire Line
	1100 1750 1250 1750
Wire Wire Line
	1550 1550 2300 1550
Wire Wire Line
	1400 1050 1400 1300
Wire Wire Line
	1700 1300 2000 1300
Wire Wire Line
	2000 1300 2000 1750
Wire Wire Line
	1550 1950 2300 1950
Wire Wire Line
	2300 1950 2300 2150
Connection ~ 2300 1950
Wire Wire Line
	3700 1500 3700 2200
Wire Wire Line
	3700 1500 3250 1500
Connection ~ 3700 1500
Wire Wire Line
	2300 950  2300 1050
Wire Wire Line
	2300 1350 2300 1550
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E622B58
P 3150 1850
F 0 "Q?" H 3340 1896 50  0000 L CNN
F 1 "2N2222" H 3340 1805 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3350 1775 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3150 1850 50  0001 L CNN
	1    3150 1850
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E623672
P 3250 1250
F 0 "R?" H 3320 1296 50  0000 L CNN
F 1 "1K" H 3320 1205 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3180 1250 50  0001 C CNN
F 3 "~" H 3250 1250 50  0001 C CNN
	1    3250 1250
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E6239FE
P 3250 950
F 0 "#PWR?" H 3250 800 50  0001 C CNN
F 1 "VCC" H 3267 1123 50  0000 C CNN
F 2 "" H 3250 950 50  0001 C CNN
F 3 "" H 3250 950 50  0001 C CNN
	1    3250 950 
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E623C5C
P 3250 2200
F 0 "#PWR?" H 3250 1950 50  0001 C CNN
F 1 "GND" H 3255 2027 50  0000 C CNN
F 2 "" H 3250 2200 50  0001 C CNN
F 3 "" H 3250 2200 50  0001 C CNN
	1    3250 2200
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E623F14
P 2700 1550
F 0 "R?" V 2493 1550 50  0000 C CNN
F 1 "10K" V 2584 1550 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2630 1550 50  0001 C CNN
F 3 "~" H 2700 1550 50  0001 C CNN
	1    2700 1550
	0    1    1    0   
$EndComp
Wire Wire Line
	2300 1550 2550 1550
Wire Wire Line
	2850 1550 2950 1550
Wire Wire Line
	2950 1550 2950 1850
Wire Wire Line
	3250 1650 3250 1500
Wire Wire Line
	3250 2200 3250 2050
Wire Wire Line
	3250 1100 3250 950 
Connection ~ 3250 1500
Wire Wire Line
	3250 1500 3250 1400
Wire Notes Line
	5450 3850 5450 650 
Wire Notes Line
	900  3850 5450 3850
Wire Notes Line
	900  650  5450 650 
Text HLabel 1100 1050 1    50   Input ~ 0
A
Text HLabel 1400 1050 1    50   Input ~ 0
B
Text HLabel 4300 2600 2    50   Output ~ 0
OUT
$EndSCHEMATC
