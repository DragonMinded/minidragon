EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 232 484
Title "Transistor 8-bit Bus"
Date "2020-01-12"
Rev "1"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L power:VCC #PWR?
U 1 1 5F6D018A
P 1000 1000
F 0 "#PWR?" H 1000 850 50  0001 C CNN
F 1 "VCC" H 950 1150 50  0000 C CNN
F 2 "" H 1000 1000 50  0001 C CNN
F 3 "" H 1000 1000 50  0001 C CNN
	1    1000 1000
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D015D
P 1100 1000
F 0 "#PWR?" H 1100 750 50  0001 C CNN
F 1 "GND" H 1050 850 50  0000 C CNN
F 2 "" H 1100 1000 50  0001 C CNN
F 3 "" H 1100 1000 50  0001 C CNN
	1    1100 1000
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E769C77
P 1500 1000
F 0 "#PWR?" H 1500 850 50  0001 C CNN
F 1 "VCC" H 1450 1150 50  0000 C CNN
F 2 "" H 1500 1000 50  0001 C CNN
F 3 "" H 1500 1000 50  0001 C CNN
	1    1500 1000
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D016E
P 1600 1000
F 0 "#PWR?" H 1600 750 50  0001 C CNN
F 1 "GND" H 1550 850 50  0000 C CNN
F 2 "" H 1600 1000 50  0001 C CNN
F 3 "" H 1600 1000 50  0001 C CNN
	1    1600 1000
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D016F
P 2000 1000
F 0 "#PWR?" H 2000 850 50  0001 C CNN
F 1 "VCC" H 1950 1150 50  0000 C CNN
F 2 "" H 2000 1000 50  0001 C CNN
F 3 "" H 2000 1000 50  0001 C CNN
	1    2000 1000
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D019D
P 2100 1000
F 0 "#PWR?" H 2100 750 50  0001 C CNN
F 1 "GND" H 2050 850 50  0000 C CNN
F 2 "" H 2100 1000 50  0001 C CNN
F 3 "" H 2100 1000 50  0001 C CNN
	1    2100 1000
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D019E
P 3000 700
F 0 "#PWR?" H 3000 550 50  0001 C CNN
F 1 "VCC" H 2950 850 50  0000 C CNN
F 2 "" H 3000 700 50  0001 C CNN
F 3 "" H 3000 700 50  0001 C CNN
	1    3000 700 
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D0170
P 3000 1200
F 0 "#PWR?" H 3000 950 50  0001 C CNN
F 1 "GND" H 2950 1050 50  0000 C CNN
F 2 "" H 3000 1200 50  0001 C CNN
F 3 "" H 3000 1200 50  0001 C CNN
	1    3000 1200
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 5F6D019F
P 3000 950
F 0 "C?" H 3115 996 50  0000 L CNN
F 1 "0.1uF" H 3115 905 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 3038 800 50  0001 C CNN
F 3 "~" H 3000 950 50  0001 C CNN
	1    3000 950 
	1    0    0    -1  
$EndComp
Wire Wire Line
	3000 800  3000 700 
Wire Wire Line
	3000 1200 3000 1100
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E769C56
P 1000 1200
F 0 "J?" V 1154 1012 50  0000 R CNN
F 1 "Power" V 1063 1012 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1000 1200 50  0001 C CNN
F 3 "~" H 1000 1200 50  0001 C CNN
	1    1000 1200
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E769C7E
P 1500 1200
F 0 "J?" V 1654 1012 50  0000 R CNN
F 1 "Power" V 1563 1012 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1500 1200 50  0001 C CNN
F 3 "~" H 1500 1200 50  0001 C CNN
	1    1500 1200
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5F6D018C
P 2000 1200
F 0 "J?" V 2154 1012 50  0000 R CNN
F 1 "Power" V 2063 1012 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 2000 1200 50  0001 C CNN
F 3 "~" H 2000 1200 50  0001 C CNN
	1    2000 1200
	0    -1   -1   0   
$EndComp
Entry Wire Line
	1800 4000 1900 4100
Entry Wire Line
	1900 4000 2000 4100
Entry Wire Line
	2000 4000 2100 4100
Entry Wire Line
	2100 4000 2200 4100
Entry Wire Line
	2200 4000 2300 4100
Entry Wire Line
	2300 4000 2400 4100
Entry Wire Line
	2400 4000 2500 4100
Entry Wire Line
	2500 4000 2600 4100
Wire Wire Line
	1900 4200 1900 4100
Wire Wire Line
	2000 4100 2000 4200
Wire Wire Line
	2100 4100 2100 4200
Wire Wire Line
	2200 4100 2200 4200
Wire Wire Line
	2300 4100 2300 4200
Wire Wire Line
	2400 4100 2400 4200
Wire Wire Line
	2500 4100 2500 4200
Wire Wire Line
	2600 4100 2600 4200
Text Label 1900 4200 0    50   ~ 0
1
Text Label 2000 4200 0    50   ~ 0
2
Text Label 2100 4200 0    50   ~ 0
3
Text Label 2200 4200 0    50   ~ 0
4
Text Label 2300 4200 0    50   ~ 0
5
Text Label 2400 4200 0    50   ~ 0
6
Text Label 2500 4200 0    50   ~ 0
7
Text Label 2600 4200 0    50   ~ 0
8
Entry Wire Line
	2500 4000 2400 3900
Entry Wire Line
	2400 4000 2300 3900
Entry Wire Line
	2300 4000 2200 3900
Entry Wire Line
	2200 4000 2100 3900
Entry Wire Line
	2100 4000 2000 3900
Entry Wire Line
	2000 4000 1900 3900
Entry Wire Line
	1900 4000 1800 3900
Entry Wire Line
	1800 4000 1700 3900
Text Label 2400 3800 2    50   ~ 0
1
Text Label 2300 3800 2    50   ~ 0
2
Text Label 2200 3800 2    50   ~ 0
3
Text Label 2100 3800 2    50   ~ 0
4
Text Label 2000 3800 2    50   ~ 0
5
Text Label 1900 3800 2    50   ~ 0
6
Text Label 1800 3800 2    50   ~ 0
7
Text Label 1700 3800 2    50   ~ 0
8
$Comp
L power:VCC #PWR?
U 1 1 5F6D0172
P 2400 3350
F 0 "#PWR?" H 2400 3200 50  0001 C CNN
F 1 "VCC" V 2400 3550 50  0000 C CNN
F 2 "" H 2400 3350 50  0001 C CNN
F 3 "" H 2400 3350 50  0001 C CNN
	1    2400 3350
	1    0    0    -1  
$EndComp
Wire Wire Line
	2400 3650 2400 3900
$Comp
L Device:R R?
U 1 1 5F6D0171
P 2400 3500
F 0 "R?" H 2470 3546 50  0001 L CNN
F 1 "1K" V 2400 3450 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2330 3500 50  0001 C CNN
F 3 "~" H 2400 3500 50  0001 C CNN
	1    2400 3500
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E769C83
P 2300 3350
F 0 "#PWR?" H 2300 3200 50  0001 C CNN
F 1 "VCC" V 2300 3550 50  0000 C CNN
F 2 "" H 2300 3350 50  0001 C CNN
F 3 "" H 2300 3350 50  0001 C CNN
	1    2300 3350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E62BF47
P 2300 3500
F 0 "R?" H 2370 3546 50  0001 L CNN
F 1 "1K" V 2300 3450 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2230 3500 50  0001 C CNN
F 3 "~" H 2300 3500 50  0001 C CNN
	1    2300 3500
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D018E
P 2200 3350
F 0 "#PWR?" H 2200 3200 50  0001 C CNN
F 1 "VCC" V 2200 3550 50  0000 C CNN
F 2 "" H 2200 3350 50  0001 C CNN
F 3 "" H 2200 3350 50  0001 C CNN
	1    2200 3350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E62BF49
P 2200 3500
F 0 "R?" H 2270 3546 50  0001 L CNN
F 1 "1K" V 2200 3450 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2130 3500 50  0001 C CNN
F 3 "~" H 2200 3500 50  0001 C CNN
	1    2200 3500
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D0175
P 2100 3350
F 0 "#PWR?" H 2100 3200 50  0001 C CNN
F 1 "VCC" V 2100 3550 50  0000 C CNN
F 2 "" H 2100 3350 50  0001 C CNN
F 3 "" H 2100 3350 50  0001 C CNN
	1    2100 3350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5F6D018F
P 2100 3500
F 0 "R?" H 2170 3546 50  0001 L CNN
F 1 "1K" V 2100 3450 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2030 3500 50  0001 C CNN
F 3 "~" H 2100 3500 50  0001 C CNN
	1    2100 3500
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D015E
P 2000 3350
F 0 "#PWR?" H 2000 3200 50  0001 C CNN
F 1 "VCC" V 2000 3550 50  0000 C CNN
F 2 "" H 2000 3350 50  0001 C CNN
F 3 "" H 2000 3350 50  0001 C CNN
	1    2000 3350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5F6D0190
P 2000 3500
F 0 "R?" H 2070 3546 50  0001 L CNN
F 1 "1K" V 2000 3450 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1930 3500 50  0001 C CNN
F 3 "~" H 2000 3500 50  0001 C CNN
	1    2000 3500
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E769C87
P 1900 3350
F 0 "#PWR?" H 1900 3200 50  0001 C CNN
F 1 "VCC" V 1900 3550 50  0000 C CNN
F 2 "" H 1900 3350 50  0001 C CNN
F 3 "" H 1900 3350 50  0001 C CNN
	1    1900 3350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5F6D01A5
P 1900 3500
F 0 "R?" H 1970 3546 50  0001 L CNN
F 1 "1K" V 1900 3450 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1830 3500 50  0001 C CNN
F 3 "~" H 1900 3500 50  0001 C CNN
	1    1900 3500
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E769C5D
P 1800 3350
F 0 "#PWR?" H 1800 3200 50  0001 C CNN
F 1 "VCC" V 1800 3550 50  0000 C CNN
F 2 "" H 1800 3350 50  0001 C CNN
F 3 "" H 1800 3350 50  0001 C CNN
	1    1800 3350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E769C5E
P 1800 3500
F 0 "R?" H 1870 3546 50  0001 L CNN
F 1 "1K" V 1800 3450 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1730 3500 50  0001 C CNN
F 3 "~" H 1800 3500 50  0001 C CNN
	1    1800 3500
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D0193
P 1700 3350
F 0 "#PWR?" H 1700 3200 50  0001 C CNN
F 1 "VCC" V 1700 3550 50  0000 C CNN
F 2 "" H 1700 3350 50  0001 C CNN
F 3 "" H 1700 3350 50  0001 C CNN
	1    1700 3350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5F6D0194
P 1700 3500
F 0 "R?" H 1770 3546 50  0001 L CNN
F 1 "1K" V 1700 3450 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1630 3500 50  0001 C CNN
F 3 "~" H 1700 3500 50  0001 C CNN
	1    1700 3500
	1    0    0    -1  
$EndComp
Wire Wire Line
	1700 3650 1700 3900
Wire Wire Line
	1800 3650 1800 3900
Wire Wire Line
	1900 3650 1900 3900
Wire Wire Line
	2000 3650 2000 3900
Wire Wire Line
	2100 3650 2100 3900
Wire Wire Line
	2200 3650 2200 3900
Wire Wire Line
	2300 3650 2300 3900
$Comp
L Device:R R?
U 1 1 5F6D0176
P 3000 4350
F 0 "R?" H 3070 4396 50  0000 L CNN
F 1 "10K" H 3070 4305 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2930 4350 50  0001 C CNN
F 3 "~" H 3000 4350 50  0001 C CNN
	1    3000 4350
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E62BF55
P 3000 4700
F 0 "Q?" V 3235 4700 50  0000 C CNN
F 1 "2N2222" V 3326 4700 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3200 4625 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3000 4700 50  0001 L CNN
	1    3000 4700
	0    1    1    0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D0178
P 3300 4800
F 0 "#PWR?" H 3300 4650 50  0001 C CNN
F 1 "VCC" V 3317 4928 50  0000 L CNN
F 2 "" H 3300 4800 50  0001 C CNN
F 3 "" H 3300 4800 50  0001 C CNN
	1    3300 4800
	0    1    1    0   
$EndComp
$Comp
L Device:LED D?
U 1 1 5E769C61
P 2700 4950
F 0 "D?" V 2750 5150 50  0000 R CNN
F 1 "LED" V 2650 5150 50  0000 R CNN
F 2 "LED_THT:LED_D5.0mm" H 2700 4950 50  0001 C CNN
F 3 "~" H 2700 4950 50  0001 C CNN
	1    2700 4950
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 5F6D015F
P 2700 5350
F 0 "R?" H 2770 5396 50  0000 L CNN
F 1 "1K" H 2770 5305 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2630 5350 50  0001 C CNN
F 3 "~" H 2700 5350 50  0001 C CNN
	1    2700 5350
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D0160
P 2700 5600
F 0 "#PWR?" H 2700 5350 50  0001 C CNN
F 1 "GND" H 2705 5427 50  0000 C CNN
F 2 "" H 2700 5600 50  0001 C CNN
F 3 "" H 2700 5600 50  0001 C CNN
	1    2700 5600
	1    0    0    -1  
$EndComp
Wire Wire Line
	2700 5600 2700 5500
Wire Wire Line
	2700 5200 2700 5100
Wire Wire Line
	2700 4800 2800 4800
Wire Wire Line
	3200 4800 3300 4800
$Comp
L Device:R R?
U 1 1 5E769C64
P 3700 4600
F 0 "R?" H 3770 4646 50  0000 L CNN
F 1 "10K" H 3770 4555 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3630 4600 50  0001 C CNN
F 3 "~" H 3700 4600 50  0001 C CNN
	1    3700 4600
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D0161
P 3700 4950
F 0 "Q?" V 3935 4950 50  0000 C CNN
F 1 "2N2222" V 4026 4950 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3900 4875 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3700 4950 50  0001 L CNN
	1    3700 4950
	0    1    1    0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D0162
P 4000 5050
F 0 "#PWR?" H 4000 4900 50  0001 C CNN
F 1 "VCC" V 4017 5178 50  0000 L CNN
F 2 "" H 4000 5050 50  0001 C CNN
F 3 "" H 4000 5050 50  0001 C CNN
	1    4000 5050
	0    1    1    0   
$EndComp
$Comp
L Device:LED D?
U 1 1 5E32C239
P 3400 5200
F 0 "D?" V 3450 5400 50  0000 R CNN
F 1 "LED" V 3350 5400 50  0000 R CNN
F 2 "LED_THT:LED_D5.0mm" H 3400 5200 50  0001 C CNN
F 3 "~" H 3400 5200 50  0001 C CNN
	1    3400 5200
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 5E32C243
P 3400 5600
F 0 "R?" H 3470 5646 50  0000 L CNN
F 1 "1K" H 3470 5555 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3330 5600 50  0001 C CNN
F 3 "~" H 3400 5600 50  0001 C CNN
	1    3400 5600
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D0179
P 3400 5850
F 0 "#PWR?" H 3400 5600 50  0001 C CNN
F 1 "GND" H 3405 5677 50  0000 C CNN
F 2 "" H 3400 5850 50  0001 C CNN
F 3 "" H 3400 5850 50  0001 C CNN
	1    3400 5850
	1    0    0    -1  
$EndComp
Wire Wire Line
	3400 5850 3400 5750
Wire Wire Line
	3400 5450 3400 5350
Wire Wire Line
	3400 5050 3500 5050
Wire Wire Line
	3900 5050 4000 5050
$Comp
L Device:R R?
U 1 1 5F6D01A6
P 4850 4350
F 0 "R?" H 4920 4396 50  0000 L CNN
F 1 "10K" H 4920 4305 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4780 4350 50  0001 C CNN
F 3 "~" H 4850 4350 50  0001 C CNN
	1    4850 4350
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E62BF61
P 4850 4700
F 0 "Q?" V 5085 4700 50  0000 C CNN
F 1 "2N2222" V 5176 4700 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5050 4625 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4850 4700 50  0001 L CNN
	1    4850 4700
	0    1    1    0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D017B
P 5150 4800
F 0 "#PWR?" H 5150 4650 50  0001 C CNN
F 1 "VCC" V 5167 4928 50  0000 L CNN
F 2 "" H 5150 4800 50  0001 C CNN
F 3 "" H 5150 4800 50  0001 C CNN
	1    5150 4800
	0    1    1    0   
$EndComp
$Comp
L Device:LED D?
U 1 1 5E62BF63
P 4550 4950
F 0 "D?" V 4600 5150 50  0000 R CNN
F 1 "LED" V 4500 5150 50  0000 R CNN
F 2 "LED_THT:LED_D5.0mm" H 4550 4950 50  0001 C CNN
F 3 "~" H 4550 4950 50  0001 C CNN
	1    4550 4950
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 5F6D01A7
P 4550 5350
F 0 "R?" H 4620 5396 50  0000 L CNN
F 1 "1K" H 4620 5305 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4480 5350 50  0001 C CNN
F 3 "~" H 4550 5350 50  0001 C CNN
	1    4550 5350
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D0165
P 4550 5600
F 0 "#PWR?" H 4550 5350 50  0001 C CNN
F 1 "GND" H 4555 5427 50  0000 C CNN
F 2 "" H 4550 5600 50  0001 C CNN
F 3 "" H 4550 5600 50  0001 C CNN
	1    4550 5600
	1    0    0    -1  
$EndComp
Wire Wire Line
	4550 5600 4550 5500
Wire Wire Line
	4550 5200 4550 5100
Wire Wire Line
	4550 4800 4650 4800
Wire Wire Line
	5050 4800 5150 4800
$Comp
L Device:R R?
U 1 1 5E33C5FE
P 5550 4600
F 0 "R?" H 5620 4646 50  0000 L CNN
F 1 "10K" H 5620 4555 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5480 4600 50  0001 C CNN
F 3 "~" H 5550 4600 50  0001 C CNN
	1    5550 4600
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E62BF67
P 5550 4950
F 0 "Q?" V 5785 4950 50  0000 C CNN
F 1 "2N2222" V 5876 4950 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5750 4875 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5550 4950 50  0001 L CNN
	1    5550 4950
	0    1    1    0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D017E
P 5850 5050
F 0 "#PWR?" H 5850 4900 50  0001 C CNN
F 1 "VCC" V 5867 5178 50  0000 L CNN
F 2 "" H 5850 5050 50  0001 C CNN
F 3 "" H 5850 5050 50  0001 C CNN
	1    5850 5050
	0    1    1    0   
$EndComp
$Comp
L Device:LED D?
U 1 1 5F6D0197
P 5250 5200
F 0 "D?" V 5300 5400 50  0000 R CNN
F 1 "LED" V 5200 5400 50  0000 R CNN
F 2 "LED_THT:LED_D5.0mm" H 5250 5200 50  0001 C CNN
F 3 "~" H 5250 5200 50  0001 C CNN
	1    5250 5200
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 5F6D0167
P 5250 5600
F 0 "R?" H 5320 5646 50  0000 L CNN
F 1 "1K" H 5320 5555 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5180 5600 50  0001 C CNN
F 3 "~" H 5250 5600 50  0001 C CNN
	1    5250 5600
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E33C630
P 5250 5850
F 0 "#PWR?" H 5250 5600 50  0001 C CNN
F 1 "GND" H 5255 5677 50  0000 C CNN
F 2 "" H 5250 5850 50  0001 C CNN
F 3 "" H 5250 5850 50  0001 C CNN
	1    5250 5850
	1    0    0    -1  
$EndComp
Wire Wire Line
	5250 5850 5250 5750
Wire Wire Line
	5250 5450 5250 5350
Wire Wire Line
	5250 5050 5350 5050
Wire Wire Line
	5750 5050 5850 5050
$Comp
L Device:R R?
U 1 1 5E62BF6C
P 6700 4300
F 0 "R?" H 6770 4346 50  0000 L CNN
F 1 "10K" H 6770 4255 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6630 4300 50  0001 C CNN
F 3 "~" H 6700 4300 50  0001 C CNN
	1    6700 4300
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E62BF6D
P 6700 4650
F 0 "Q?" V 6935 4650 50  0000 C CNN
F 1 "2N2222" V 7026 4650 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6900 4575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6700 4650 50  0001 L CNN
	1    6700 4650
	0    1    1    0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E769C96
P 7000 4750
F 0 "#PWR?" H 7000 4600 50  0001 C CNN
F 1 "VCC" V 7017 4878 50  0000 L CNN
F 2 "" H 7000 4750 50  0001 C CNN
F 3 "" H 7000 4750 50  0001 C CNN
	1    7000 4750
	0    1    1    0   
$EndComp
$Comp
L Device:LED D?
U 1 1 5E769C97
P 6400 4900
F 0 "D?" V 6450 5100 50  0000 R CNN
F 1 "LED" V 6350 5100 50  0000 R CNN
F 2 "LED_THT:LED_D5.0mm" H 6400 4900 50  0001 C CNN
F 3 "~" H 6400 4900 50  0001 C CNN
	1    6400 4900
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 5F6D0198
P 6400 5300
F 0 "R?" H 6470 5346 50  0000 L CNN
F 1 "1K" H 6470 5255 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6330 5300 50  0001 C CNN
F 3 "~" H 6400 5300 50  0001 C CNN
	1    6400 5300
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E3509F5
P 6400 5550
F 0 "#PWR?" H 6400 5300 50  0001 C CNN
F 1 "GND" H 6405 5377 50  0000 C CNN
F 2 "" H 6400 5550 50  0001 C CNN
F 3 "" H 6400 5550 50  0001 C CNN
	1    6400 5550
	1    0    0    -1  
$EndComp
Wire Wire Line
	6400 5550 6400 5450
Wire Wire Line
	6400 5150 6400 5050
Wire Wire Line
	6400 4750 6500 4750
Wire Wire Line
	6900 4750 7000 4750
$Comp
L Device:R R?
U 1 1 5E350A03
P 7400 4550
F 0 "R?" H 7470 4596 50  0000 L CNN
F 1 "10K" H 7470 4505 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 7330 4550 50  0001 C CNN
F 3 "~" H 7400 4550 50  0001 C CNN
	1    7400 4550
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E769C71
P 7400 4900
F 0 "Q?" V 7635 4900 50  0000 C CNN
F 1 "2N2222" V 7726 4900 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7600 4825 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 7400 4900 50  0001 L CNN
	1    7400 4900
	0    1    1    0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E62BF74
P 7700 5000
F 0 "#PWR?" H 7700 4850 50  0001 C CNN
F 1 "VCC" V 7717 5128 50  0000 L CNN
F 2 "" H 7700 5000 50  0001 C CNN
F 3 "" H 7700 5000 50  0001 C CNN
	1    7700 5000
	0    1    1    0   
$EndComp
$Comp
L Device:LED D?
U 1 1 5E350A21
P 7100 5150
F 0 "D?" V 7150 5350 50  0000 R CNN
F 1 "LED" V 7050 5350 50  0000 R CNN
F 2 "LED_THT:LED_D5.0mm" H 7100 5150 50  0001 C CNN
F 3 "~" H 7100 5150 50  0001 C CNN
	1    7100 5150
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 5E350A2B
P 7100 5550
F 0 "R?" H 7170 5596 50  0000 L CNN
F 1 "1K" H 7170 5505 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 7030 5550 50  0001 C CNN
F 3 "~" H 7100 5550 50  0001 C CNN
	1    7100 5550
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D0182
P 7100 5800
F 0 "#PWR?" H 7100 5550 50  0001 C CNN
F 1 "GND" H 7105 5627 50  0000 C CNN
F 2 "" H 7100 5800 50  0001 C CNN
F 3 "" H 7100 5800 50  0001 C CNN
	1    7100 5800
	1    0    0    -1  
$EndComp
Wire Wire Line
	7100 5800 7100 5700
Wire Wire Line
	7100 5400 7100 5300
Wire Wire Line
	7100 5000 7200 5000
Wire Wire Line
	7600 5000 7700 5000
$Comp
L Device:R R?
U 1 1 5F6D01AA
P 8550 4300
F 0 "R?" H 8620 4346 50  0000 L CNN
F 1 "10K" H 8620 4255 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 8480 4300 50  0001 C CNN
F 3 "~" H 8550 4300 50  0001 C CNN
	1    8550 4300
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E62BF79
P 8550 4650
F 0 "Q?" V 8785 4650 50  0000 C CNN
F 1 "2N2222" V 8876 4650 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 8750 4575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 8550 4650 50  0001 L CNN
	1    8550 4650
	0    1    1    0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D0184
P 8850 4750
F 0 "#PWR?" H 8850 4600 50  0001 C CNN
F 1 "VCC" V 8867 4878 50  0000 L CNN
F 2 "" H 8850 4750 50  0001 C CNN
F 3 "" H 8850 4750 50  0001 C CNN
	1    8850 4750
	0    1    1    0   
$EndComp
$Comp
L Device:LED D?
U 1 1 5F6D0185
P 8250 4900
F 0 "D?" V 8300 5100 50  0000 R CNN
F 1 "LED" V 8200 5100 50  0000 R CNN
F 2 "LED_THT:LED_D5.0mm" H 8250 4900 50  0001 C CNN
F 3 "~" H 8250 4900 50  0001 C CNN
	1    8250 4900
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 5E62BF7C
P 8250 5300
F 0 "R?" H 8320 5346 50  0000 L CNN
F 1 "1K" H 8320 5255 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 8180 5300 50  0001 C CNN
F 3 "~" H 8250 5300 50  0001 C CNN
	1    8250 5300
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D01AB
P 8250 5550
F 0 "#PWR?" H 8250 5300 50  0001 C CNN
F 1 "GND" H 8255 5377 50  0000 C CNN
F 2 "" H 8250 5550 50  0001 C CNN
F 3 "" H 8250 5550 50  0001 C CNN
	1    8250 5550
	1    0    0    -1  
$EndComp
Wire Wire Line
	8250 5550 8250 5450
Wire Wire Line
	8250 5150 8250 5050
Wire Wire Line
	8250 4750 8350 4750
Wire Wire Line
	8750 4750 8850 4750
$Comp
L Device:R R?
U 1 1 5F6D019A
P 9250 4550
F 0 "R?" H 9320 4596 50  0000 L CNN
F 1 "10K" H 9320 4505 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 9180 4550 50  0001 C CNN
F 3 "~" H 9250 4550 50  0001 C CNN
	1    9250 4550
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E350A8D
P 9250 4900
F 0 "Q?" V 9485 4900 50  0000 C CNN
F 1 "2N2222" V 9576 4900 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 9450 4825 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 9250 4900 50  0001 L CNN
	1    9250 4900
	0    1    1    0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E62BF80
P 9550 5000
F 0 "#PWR?" H 9550 4850 50  0001 C CNN
F 1 "VCC" V 9567 5128 50  0000 L CNN
F 2 "" H 9550 5000 50  0001 C CNN
F 3 "" H 9550 5000 50  0001 C CNN
	1    9550 5000
	0    1    1    0   
$EndComp
$Comp
L Device:LED D?
U 1 1 5E62BF81
P 8950 5150
F 0 "D?" V 9000 5350 50  0000 R CNN
F 1 "LED" V 8900 5350 50  0000 R CNN
F 2 "LED_THT:LED_D5.0mm" H 8950 5150 50  0001 C CNN
F 3 "~" H 8950 5150 50  0001 C CNN
	1    8950 5150
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 5F6D0189
P 8950 5550
F 0 "R?" H 9020 5596 50  0000 L CNN
F 1 "1K" H 9020 5505 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 8880 5550 50  0001 C CNN
F 3 "~" H 8950 5550 50  0001 C CNN
	1    8950 5550
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D019B
P 8950 5800
F 0 "#PWR?" H 8950 5550 50  0001 C CNN
F 1 "GND" H 8955 5627 50  0000 C CNN
F 2 "" H 8950 5800 50  0001 C CNN
F 3 "" H 8950 5800 50  0001 C CNN
	1    8950 5800
	1    0    0    -1  
$EndComp
Wire Wire Line
	8950 5800 8950 5700
Wire Wire Line
	8950 5400 8950 5300
Wire Wire Line
	8950 5000 9050 5000
Wire Wire Line
	9450 5000 9550 5000
Entry Wire Line
	2900 4000 3000 4100
Entry Wire Line
	3600 4000 3700 4100
Entry Wire Line
	4750 4000 4850 4100
Entry Wire Line
	5450 4000 5550 4100
Entry Wire Line
	6600 4000 6700 4100
Entry Wire Line
	7300 4000 7400 4100
Entry Wire Line
	8450 4000 8550 4100
Entry Wire Line
	9150 4000 9250 4100
Wire Wire Line
	9250 4400 9250 4100
Wire Wire Line
	8550 4150 8550 4100
Wire Wire Line
	7400 4400 7400 4100
Wire Wire Line
	6700 4150 6700 4100
Wire Wire Line
	5550 4450 5550 4100
Wire Wire Line
	4850 4200 4850 4100
Wire Wire Line
	3700 4450 3700 4100
Wire Wire Line
	3000 4200 3000 4100
Text Label 3000 4100 0    50   ~ 0
1
Text Label 3700 4100 0    50   ~ 0
2
Text Label 4850 4100 0    50   ~ 0
3
Text Label 5550 4100 0    50   ~ 0
4
Text Label 6700 4100 0    50   ~ 0
5
Text Label 7400 4100 0    50   ~ 0
6
Text Label 8550 4100 0    50   ~ 0
7
Text Label 9250 4100 0    50   ~ 0
8
$Comp
L power:VCC #PWR?
U 1 1 5E769C7F
P 3500 700
F 0 "#PWR?" H 3500 550 50  0001 C CNN
F 1 "VCC" H 3450 850 50  0000 C CNN
F 2 "" H 3500 700 50  0001 C CNN
F 3 "" H 3500 700 50  0001 C CNN
	1    3500 700 
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E769C80
P 3500 1200
F 0 "#PWR?" H 3500 950 50  0001 C CNN
F 1 "GND" H 3450 1050 50  0000 C CNN
F 2 "" H 3500 1200 50  0001 C CNN
F 3 "" H 3500 1200 50  0001 C CNN
	1    3500 1200
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 5F6D018D
P 3500 950
F 0 "C?" H 3615 996 50  0000 L CNN
F 1 "0.1uF" H 3615 905 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 3538 800 50  0001 C CNN
F 3 "~" H 3500 950 50  0001 C CNN
	1    3500 950 
	1    0    0    -1  
$EndComp
Wire Wire Line
	3500 800  3500 700 
Wire Wire Line
	3500 1200 3500 1100
Text HLabel 1900 4200 3    50   BiDi ~ 0
BUS_1
Text HLabel 2000 4200 3    50   BiDi ~ 0
BUS_2
Text HLabel 2100 4200 3    50   BiDi ~ 0
BUS_3
Text HLabel 2200 4200 3    50   BiDi ~ 0
BUS_4
Text HLabel 2300 4200 3    50   BiDi ~ 0
BUS_5
Text HLabel 2400 4200 3    50   BiDi ~ 0
BUS_6
Text HLabel 2500 4200 3    50   BiDi ~ 0
BUS_7
Text HLabel 2600 4200 3    50   BiDi ~ 0
BUS_8
Wire Bus Line
	1800 4000 9150 4000
$EndSCHEMATC
