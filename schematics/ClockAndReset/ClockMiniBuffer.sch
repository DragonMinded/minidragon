EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 14 484
Title "High Current Mini Buffer"
Date "2020-04-10"
Rev "1"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Device:R R?
U 1 1 5EA288BC
P 3000 1650
F 0 "R?" H 3070 1696 50  0000 L CNN
F 1 "1K" H 3070 1605 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2930 1650 50  0001 C CNN
F 3 "~" H 3000 1650 50  0001 C CNN
	1    3000 1650
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5EB9D3D6
P 3000 1800
F 0 "#PWR?" H 3000 1550 50  0001 C CNN
F 1 "GND" H 3005 1627 50  0000 C CNN
F 2 "" H 3000 1800 50  0001 C CNN
F 3 "" H 3000 1800 50  0001 C CNN
	1    3000 1800
	1    0    0    -1  
$EndComp
Wire Wire Line
	3000 1500 3000 1450
Connection ~ 3000 1500
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5EA288C7
P 1050 2000
F 0 "J?" V 1204 1812 50  0000 R CNN
F 1 "Power" V 1113 1812 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1050 2000 50  0001 C CNN
F 3 "~" H 1050 2000 50  0001 C CNN
	1    1050 2000
	0    -1   -1   0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5EF65150
P 1050 1650
F 0 "#PWR?" H 1050 1500 50  0001 C CNN
F 1 "VCC" H 1000 1800 50  0000 C CNN
F 2 "" H 1050 1650 50  0001 C CNN
F 3 "" H 1050 1650 50  0001 C CNN
	1    1050 1650
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5ED5B7D2
P 1150 1650
F 0 "#PWR?" H 1150 1400 50  0001 C CNN
F 1 "GND" H 1100 1500 50  0000 C CNN
F 2 "" H 1150 1650 50  0001 C CNN
F 3 "" H 1150 1650 50  0001 C CNN
	1    1150 1650
	-1   0    0    1   
$EndComp
Wire Wire Line
	1050 1800 1050 1650
Wire Wire Line
	1150 1800 1150 1650
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5EB9D3D1
P 1550 2000
F 0 "J?" V 1704 1812 50  0000 R CNN
F 1 "Power" V 1613 1812 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1550 2000 50  0001 C CNN
F 3 "~" H 1550 2000 50  0001 C CNN
	1    1550 2000
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5DFF2E7D
P 2000 2000
F 0 "J?" V 2154 1812 50  0000 R CNN
F 1 "Power" V 2063 1812 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 2000 2000 50  0001 C CNN
F 3 "~" H 2000 2000 50  0001 C CNN
	1    2000 2000
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5ED5B7C7
P 1650 1650
F 0 "#PWR?" H 1650 1400 50  0001 C CNN
F 1 "GND" H 1600 1500 50  0000 C CNN
F 2 "" H 1650 1650 50  0001 C CNN
F 3 "" H 1650 1650 50  0001 C CNN
	1    1650 1650
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5EA288BF
P 2100 1650
F 0 "#PWR?" H 2100 1400 50  0001 C CNN
F 1 "GND" H 2050 1500 50  0000 C CNN
F 2 "" H 2100 1650 50  0001 C CNN
F 3 "" H 2100 1650 50  0001 C CNN
	1    2100 1650
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5EA288C1
P 1550 1650
F 0 "#PWR?" H 1550 1500 50  0001 C CNN
F 1 "VCC" H 1500 1800 50  0000 C CNN
F 2 "" H 1550 1650 50  0001 C CNN
F 3 "" H 1550 1650 50  0001 C CNN
	1    1550 1650
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5EF6514A
P 2000 1650
F 0 "#PWR?" H 2000 1500 50  0001 C CNN
F 1 "VCC" H 1950 1800 50  0000 C CNN
F 2 "" H 2000 1650 50  0001 C CNN
F 3 "" H 2000 1650 50  0001 C CNN
	1    2000 1650
	1    0    0    -1  
$EndComp
Wire Wire Line
	1550 1650 1550 1800
Wire Wire Line
	1650 1800 1650 1650
Wire Wire Line
	2000 1650 2000 1800
Wire Wire Line
	2100 1800 2100 1650
$Comp
L power:VCC #PWR?
U 1 1 5EA288C4
P 4800 1450
F 0 "#PWR?" H 4800 1300 50  0001 C CNN
F 1 "VCC" H 4817 1623 50  0000 C CNN
F 2 "" H 4800 1450 50  0001 C CNN
F 3 "" H 4800 1450 50  0001 C CNN
	1    4800 1450
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5EA288C5
P 4800 1950
F 0 "#PWR?" H 4800 1700 50  0001 C CNN
F 1 "GND" H 4805 1777 50  0000 C CNN
F 2 "" H 4800 1950 50  0001 C CNN
F 3 "" H 4800 1950 50  0001 C CNN
	1    4800 1950
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 5EA288C6
P 4800 1700
F 0 "C?" H 4915 1746 50  0000 L CNN
F 1 "0.1uF" H 4915 1655 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 4838 1550 50  0001 C CNN
F 3 "~" H 4800 1700 50  0001 C CNN
	1    4800 1700
	1    0    0    -1  
$EndComp
Wire Wire Line
	4800 1450 4800 1550
Wire Wire Line
	4800 1850 4800 1950
$Comp
L power:VCC #PWR?
U 1 1 5F1746C3
P 3000 1050
F 0 "#PWR?" H 3000 900 50  0001 C CNN
F 1 "VCC" H 3017 1223 50  0000 C CNN
F 2 "" H 3000 1050 50  0001 C CNN
F 3 "" H 3000 1050 50  0001 C CNN
	1    3000 1050
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5EB9D3D0
P 2900 1250
F 0 "Q?" H 3090 1296 50  0000 L CNN
F 1 "2N2222" H 3090 1205 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3100 1175 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2900 1250 50  0001 L CNN
	1    2900 1250
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5EB9D3E0
P 3800 2550
F 0 "R?" H 3870 2596 50  0000 L CNN
F 1 "1K" H 3870 2505 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3730 2550 50  0001 C CNN
F 3 "~" H 3800 2550 50  0001 C CNN
	1    3800 2550
	1    0    0    -1  
$EndComp
Wire Wire Line
	3800 2400 3800 2350
Connection ~ 3800 2400
$Comp
L power:VCC #PWR?
U 1 1 5EB9D3E2
P 3800 1950
F 0 "#PWR?" H 3800 1800 50  0001 C CNN
F 1 "VCC" H 3817 2123 50  0000 C CNN
F 2 "" H 3800 1950 50  0001 C CNN
F 3 "" H 3800 1950 50  0001 C CNN
	1    3800 1950
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5EB9D3E3
P 3700 2150
F 0 "Q?" H 3890 2196 50  0000 L CNN
F 1 "2N2222" H 3890 2105 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3900 2075 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3700 2150 50  0001 L CNN
	1    3700 2150
	1    0    0    -1  
$EndComp
Wire Wire Line
	1050 900  2550 900 
Wire Wire Line
	2550 900  2550 1250
Wire Wire Line
	2550 1250 2700 1250
Wire Wire Line
	3900 1500 3900 650 
Wire Wire Line
	3900 650  5000 650 
Wire Wire Line
	3000 1500 3900 1500
Wire Wire Line
	1050 1000 2500 1000
Wire Wire Line
	2500 1000 2500 2150
Wire Wire Line
	2500 2150 3500 2150
Wire Wire Line
	4500 2400 4500 750 
Wire Wire Line
	4500 750  5000 750 
Wire Wire Line
	3800 2400 4500 2400
$Comp
L power:GND #PWR?
U 1 1 5EB9D3E1
P 3800 2700
F 0 "#PWR?" H 3800 2450 50  0001 C CNN
F 1 "GND" H 3805 2527 50  0000 C CNN
F 2 "" H 3800 2700 50  0001 C CNN
F 3 "" H 3800 2700 50  0001 C CNN
	1    3800 2700
	1    0    0    -1  
$EndComp
Text HLabel 1050 900  0    50   Input ~ 0
IN1
Text HLabel 1050 1000 0    50   Input ~ 0
IN2
Text HLabel 5000 650  2    50   Output ~ 0
OUT1
Text HLabel 5000 750  2    50   Output ~ 0
OUT2
$EndSCHEMATC
