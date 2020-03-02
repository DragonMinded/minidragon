EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 10 126
Title "Transistor XOR Gate"
Date "2020-01-12"
Rev "1"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Device:R R?
U 1 1 5E1B738C
P 2000 1100
F 0 "R?" H 2070 1146 50  0000 L CNN
F 1 "1K" H 2070 1055 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1930 1100 50  0001 C CNN
F 3 "~" H 2000 1100 50  0001 C CNN
	1    2000 1100
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0279
U 1 1 5E1B7EC7
P 2000 950
F 0 "#PWR0279" H 2000 800 50  0001 C CNN
F 1 "VCC" H 2017 1123 50  0000 C CNN
F 2 "" H 2000 950 50  0001 C CNN
F 3 "" H 2000 950 50  0001 C CNN
	1    2000 950 
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E1B865C
P 1900 1500
F 0 "Q?" H 2090 1546 50  0000 L CNN
F 1 "2N2222" H 2090 1455 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2100 1425 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 1900 1500 50  0001 L CNN
	1    1900 1500
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0280
U 1 1 5E1B8ECE
P 2000 1700
F 0 "#PWR0280" H 2000 1450 50  0001 C CNN
F 1 "GND" H 2005 1527 50  0000 C CNN
F 2 "" H 2000 1700 50  0001 C CNN
F 3 "" H 2000 1700 50  0001 C CNN
	1    2000 1700
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E1B9499
P 1550 1500
F 0 "R?" V 1343 1500 50  0000 C CNN
F 1 "10K" V 1434 1500 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1480 1500 50  0001 C CNN
F 3 "~" H 1550 1500 50  0001 C CNN
	1    1550 1500
	0    1    1    0   
$EndComp
$Comp
L power:VCC #PWR0281
U 1 1 5E1BD953
P 2000 2250
F 0 "#PWR0281" H 2000 2100 50  0001 C CNN
F 1 "VCC" H 2017 2423 50  0000 C CNN
F 2 "" H 2000 2250 50  0001 C CNN
F 3 "" H 2000 2250 50  0001 C CNN
	1    2000 2250
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E1BDBCA
P 2000 2400
F 0 "R?" H 2070 2446 50  0000 L CNN
F 1 "1K" H 2070 2355 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1930 2400 50  0001 C CNN
F 3 "~" H 2000 2400 50  0001 C CNN
	1    2000 2400
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E1BDE6C
P 1900 2800
F 0 "Q?" H 2090 2846 50  0000 L CNN
F 1 "2N2222" H 2090 2755 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2100 2725 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 1900 2800 50  0001 L CNN
	1    1900 2800
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E1BE2F3
P 1550 2800
F 0 "R?" V 1343 2800 50  0000 C CNN
F 1 "10K" V 1434 2800 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1480 2800 50  0001 C CNN
F 3 "~" H 1550 2800 50  0001 C CNN
	1    1550 2800
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR0282
U 1 1 5E1BE4FB
P 2000 3000
F 0 "#PWR0282" H 2000 2750 50  0001 C CNN
F 1 "GND" H 2005 2827 50  0000 C CNN
F 2 "" H 2000 3000 50  0001 C CNN
F 3 "" H 2000 3000 50  0001 C CNN
	1    2000 3000
	1    0    0    -1  
$EndComp
Wire Wire Line
	1000 1500 1400 1500
Wire Wire Line
	1000 2800 1400 2800
Wire Wire Line
	2000 1250 2000 1300
Wire Wire Line
	2000 2550 2000 2600
$Comp
L Device:R R?
U 1 1 5E1C27F5
P 3150 1250
F 0 "R?" V 2943 1250 50  0000 C CNN
F 1 "10K" V 3034 1250 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3080 1250 50  0001 C CNN
F 3 "~" H 3150 1250 50  0001 C CNN
	1    3150 1250
	0    1    1    0   
$EndComp
$Comp
L Device:R R?
U 1 1 5E1C2FB6
P 3150 2550
F 0 "R?" V 2943 2550 50  0000 C CNN
F 1 "10K" V 3034 2550 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3080 2550 50  0001 C CNN
F 3 "~" H 3150 2550 50  0001 C CNN
	1    3150 2550
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E1C34FA
P 3500 1250
F 0 "Q?" H 3690 1296 50  0000 L CNN
F 1 "2N2222" H 3690 1205 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3700 1175 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3500 1250 50  0001 L CNN
	1    3500 1250
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E1C392D
P 3500 1650
F 0 "Q?" H 3690 1696 50  0000 L CNN
F 1 "2N2222" H 3690 1605 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3700 1575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3500 1650 50  0001 L CNN
	1    3500 1650
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E1C3DA4
P 3150 1650
F 0 "R?" V 2943 1650 50  0000 C CNN
F 1 "10K" V 3034 1650 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3080 1650 50  0001 C CNN
F 3 "~" H 3150 1650 50  0001 C CNN
	1    3150 1650
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E1C4457
P 3500 2550
F 0 "Q?" H 3690 2596 50  0000 L CNN
F 1 "2N2222" H 3690 2505 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3700 2475 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3500 2550 50  0001 L CNN
	1    3500 2550
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E1C46DB
P 3500 2950
F 0 "Q?" H 3690 2996 50  0000 L CNN
F 1 "2N2222" H 3690 2905 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3700 2875 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3500 2950 50  0001 L CNN
	1    3500 2950
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E1C4B18
P 3150 2950
F 0 "R?" V 2943 2950 50  0000 C CNN
F 1 "10K" V 3034 2950 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3080 2950 50  0001 C CNN
F 3 "~" H 3150 2950 50  0001 C CNN
	1    3150 2950
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR0283
U 1 1 5E1C4EA1
P 3600 1850
F 0 "#PWR0283" H 3600 1600 50  0001 C CNN
F 1 "GND" H 3605 1677 50  0000 C CNN
F 2 "" H 3600 1850 50  0001 C CNN
F 3 "" H 3600 1850 50  0001 C CNN
	1    3600 1850
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0284
U 1 1 5E1C5237
P 3600 3150
F 0 "#PWR0284" H 3600 2900 50  0001 C CNN
F 1 "GND" H 3605 2977 50  0000 C CNN
F 2 "" H 3600 3150 50  0001 C CNN
F 3 "" H 3600 3150 50  0001 C CNN
	1    3600 3150
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E1C558D
P 4650 1050
F 0 "R?" V 4443 1050 50  0000 C CNN
F 1 "1K" V 4534 1050 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4580 1050 50  0001 C CNN
F 3 "~" H 4650 1050 50  0001 C CNN
	1    4650 1050
	0    1    1    0   
$EndComp
$Comp
L power:VCC #PWR0285
U 1 1 5E1C5BF8
P 4800 900
F 0 "#PWR0285" H 4800 750 50  0001 C CNN
F 1 "VCC" H 4817 1073 50  0000 C CNN
F 2 "" H 4800 900 50  0001 C CNN
F 3 "" H 4800 900 50  0001 C CNN
	1    4800 900 
	1    0    0    -1  
$EndComp
Wire Wire Line
	4800 1050 4800 900 
Wire Wire Line
	3600 2350 4200 2350
Wire Wire Line
	2000 1250 3000 1250
Connection ~ 2000 1250
Wire Wire Line
	3600 1050 4200 1050
Wire Wire Line
	4200 1050 4200 2350
Connection ~ 4200 1050
Wire Wire Line
	4200 1050 4500 1050
Wire Wire Line
	3000 2550 2000 2550
Connection ~ 2000 2550
Wire Wire Line
	1400 2800 1400 2000
Wire Wire Line
	1400 2000 3000 2000
Wire Wire Line
	3000 2000 3000 1650
Connection ~ 1400 2800
Wire Wire Line
	1400 1500 1400 1950
Wire Wire Line
	1400 1950 2950 1950
Wire Wire Line
	2950 1950 2950 2950
Wire Wire Line
	2950 2950 3000 2950
Connection ~ 1400 1500
$Comp
L Device:R R?
U 1 1 5E1C956C
P 4350 2350
F 0 "R?" V 4143 2350 50  0000 C CNN
F 1 "10K" V 4234 2350 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4280 2350 50  0001 C CNN
F 3 "~" H 4350 2350 50  0001 C CNN
	1    4350 2350
	0    1    1    0   
$EndComp
Connection ~ 4200 2350
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E1C98A6
P 4700 2350
F 0 "Q?" H 4890 2396 50  0000 L CNN
F 1 "2N2222" H 4890 2305 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4900 2275 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4700 2350 50  0001 L CNN
	1    4700 2350
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0286
U 1 1 5E1C9D14
P 4800 2550
F 0 "#PWR0286" H 4800 2300 50  0001 C CNN
F 1 "GND" H 4805 2377 50  0000 C CNN
F 2 "" H 4800 2550 50  0001 C CNN
F 3 "" H 4800 2550 50  0001 C CNN
	1    4800 2550
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E1CB0F0
P 5500 1950
F 0 "R?" H 5700 1900 50  0000 R CNN
F 1 "1K" H 5650 2000 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5430 1950 50  0001 C CNN
F 3 "~" H 5500 1950 50  0001 C CNN
	1    5500 1950
	-1   0    0    1   
$EndComp
$Comp
L Device:R R?
U 1 1 5E1CB463
P 5500 2350
F 0 "R?" H 5430 2304 50  0000 R CNN
F 1 "10K" H 5430 2395 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5430 2350 50  0001 C CNN
F 3 "~" H 5500 2350 50  0001 C CNN
	1    5500 2350
	-1   0    0    1   
$EndComp
Wire Wire Line
	5500 2200 5500 2150
Wire Wire Line
	5500 2150 4800 2150
Connection ~ 5500 2150
Wire Wire Line
	5500 2150 5500 2100
$Comp
L power:VCC #PWR0287
U 1 1 5E1CBEE5
P 5500 1800
F 0 "#PWR0287" H 5500 1650 50  0001 C CNN
F 1 "VCC" H 5517 1973 50  0000 C CNN
F 2 "" H 5500 1800 50  0001 C CNN
F 3 "" H 5500 1800 50  0001 C CNN
	1    5500 1800
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E1CC225
P 5950 2150
F 0 "Q?" H 6140 2196 50  0000 L CNN
F 1 "2N2222" H 6140 2105 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6150 2075 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5950 2150 50  0001 L CNN
	1    5950 2150
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0288
U 1 1 5E1CC831
P 6050 1950
F 0 "#PWR0288" H 6050 1800 50  0001 C CNN
F 1 "VCC" H 6067 2123 50  0000 C CNN
F 2 "" H 6050 1950 50  0001 C CNN
F 3 "" H 6050 1950 50  0001 C CNN
	1    6050 1950
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E1CCAB5
P 6050 2550
F 0 "R?" H 5980 2504 50  0000 R CNN
F 1 "1K" H 5980 2595 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5980 2550 50  0001 C CNN
F 3 "~" H 6050 2550 50  0001 C CNN
	1    6050 2550
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR0289
U 1 1 5E1CCD9D
P 6050 2700
F 0 "#PWR0289" H 6050 2450 50  0001 C CNN
F 1 "GND" H 6055 2527 50  0000 C CNN
F 2 "" H 6050 2700 50  0001 C CNN
F 3 "" H 6050 2700 50  0001 C CNN
	1    6050 2700
	1    0    0    -1  
$EndComp
Wire Wire Line
	6050 2400 6050 2350
Wire Wire Line
	6050 2400 6700 2400
Connection ~ 6050 2400
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E1CF546
P 5500 3000
F 0 "Q?" V 5735 3000 50  0000 C CNN
F 1 "2N2222" V 5826 3000 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5700 2925 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5500 3000 50  0001 L CNN
	1    5500 3000
	0    1    1    0   
$EndComp
Wire Wire Line
	5500 2500 5500 2800
$Comp
L power:VCC #PWR0290
U 1 1 5E1D0273
P 5700 3100
F 0 "#PWR0290" H 5700 2950 50  0001 C CNN
F 1 "VCC" V 5717 3228 50  0000 L CNN
F 2 "" H 5700 3100 50  0001 C CNN
F 3 "" H 5700 3100 50  0001 C CNN
	1    5700 3100
	0    1    1    0   
$EndComp
$Comp
L Device:LED D?
U 1 1 5E1D0C33
P 5150 3100
F 0 "D?" H 5143 3316 50  0000 C CNN
F 1 "LED" H 5143 3225 50  0000 C CNN
F 2 "LED_THT:LED_D5.0mm" H 5150 3100 50  0001 C CNN
F 3 "~" H 5150 3100 50  0001 C CNN
	1    5150 3100
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E1D1352
P 4850 3100
F 0 "R?" V 4643 3100 50  0000 C CNN
F 1 "1K" V 4734 3100 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4780 3100 50  0001 C CNN
F 3 "~" H 4850 3100 50  0001 C CNN
	1    4850 3100
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR0291
U 1 1 5E1D16C4
P 4700 3100
F 0 "#PWR0291" H 4700 2850 50  0001 C CNN
F 1 "GND" V 4705 2972 50  0000 R CNN
F 2 "" H 4700 3100 50  0001 C CNN
F 3 "" H 4700 3100 50  0001 C CNN
	1    4700 3100
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR0292
U 1 1 5E1D3F5E
P 1100 4000
F 0 "#PWR0292" H 1100 3750 50  0001 C CNN
F 1 "GND" H 1050 3850 50  0000 C CNN
F 2 "" H 1100 4000 50  0001 C CNN
F 3 "" H 1100 4000 50  0001 C CNN
	1    1100 4000
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR0293
U 1 1 5E1D48C5
P 1000 4000
F 0 "#PWR0293" H 1000 3850 50  0001 C CNN
F 1 "VCC" H 950 4150 50  0000 C CNN
F 2 "" H 1000 4000 50  0001 C CNN
F 3 "" H 1000 4000 50  0001 C CNN
	1    1000 4000
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E1D4E8F
P 1000 4200
F 0 "J?" V 1154 4012 50  0000 R CNN
F 1 "Power" V 1063 4012 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1000 4200 50  0001 C CNN
F 3 "~" H 1000 4200 50  0001 C CNN
	1    1000 4200
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E1D5DCC
P 1500 4200
F 0 "J?" V 1654 4012 50  0000 R CNN
F 1 "Power" V 1563 4012 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1500 4200 50  0001 C CNN
F 3 "~" H 1500 4200 50  0001 C CNN
	1    1500 4200
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E1D6106
P 2000 4200
F 0 "J?" V 2154 4012 50  0000 R CNN
F 1 "Power" V 2063 4012 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 2000 4200 50  0001 C CNN
F 3 "~" H 2000 4200 50  0001 C CNN
	1    2000 4200
	0    -1   -1   0   
$EndComp
$Comp
L power:VCC #PWR0294
U 1 1 5E1D634F
P 1500 4000
F 0 "#PWR0294" H 1500 3850 50  0001 C CNN
F 1 "VCC" H 1450 4150 50  0000 C CNN
F 2 "" H 1500 4000 50  0001 C CNN
F 3 "" H 1500 4000 50  0001 C CNN
	1    1500 4000
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0295
U 1 1 5E1D6548
P 1600 4000
F 0 "#PWR0295" H 1600 3750 50  0001 C CNN
F 1 "GND" H 1550 3850 50  0000 C CNN
F 2 "" H 1600 4000 50  0001 C CNN
F 3 "" H 1600 4000 50  0001 C CNN
	1    1600 4000
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR0296
U 1 1 5E1D66BE
P 2100 4000
F 0 "#PWR0296" H 2100 3750 50  0001 C CNN
F 1 "GND" H 2050 3850 50  0000 C CNN
F 2 "" H 2100 4000 50  0001 C CNN
F 3 "" H 2100 4000 50  0001 C CNN
	1    2100 4000
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR0297
U 1 1 5E1D6874
P 2000 4000
F 0 "#PWR0297" H 2000 3850 50  0001 C CNN
F 1 "VCC" H 1950 4150 50  0000 C CNN
F 2 "" H 2000 4000 50  0001 C CNN
F 3 "" H 2000 4000 50  0001 C CNN
	1    2000 4000
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0298
U 1 1 5E1D6AC5
P 3000 3500
F 0 "#PWR0298" H 3000 3350 50  0001 C CNN
F 1 "VCC" H 2950 3650 50  0000 C CNN
F 2 "" H 3000 3500 50  0001 C CNN
F 3 "" H 3000 3500 50  0001 C CNN
	1    3000 3500
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0299
U 1 1 5E1D6ED3
P 3000 4000
F 0 "#PWR0299" H 3000 3750 50  0001 C CNN
F 1 "GND" H 2950 3850 50  0000 C CNN
F 2 "" H 3000 4000 50  0001 C CNN
F 3 "" H 3000 4000 50  0001 C CNN
	1    3000 4000
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 5E1D72BB
P 3000 3750
F 0 "C?" H 3115 3796 50  0000 L CNN
F 1 "0.1uF" H 3115 3705 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 3038 3600 50  0001 C CNN
F 3 "~" H 3000 3750 50  0001 C CNN
	1    3000 3750
	1    0    0    -1  
$EndComp
Wire Wire Line
	3000 4000 3000 3900
Wire Wire Line
	3000 3600 3000 3500
Wire Wire Line
	5500 2150 5750 2150
Wire Notes Line
	700  600  700  4350
Wire Notes Line
	700  4350 7200 4350
Wire Notes Line
	7200 4350 7200 600 
Wire Notes Line
	7200 600  700  600 
Text Notes 4800 4300 0    50   ~ 0
XOR Gate w/Output Indicator\n\n2.36us rise delay\n2.36us fall delay\n26mA current draw
Text HLabel 1000 1500 0    50   Input ~ 0
A
Text HLabel 1000 2800 0    50   Input ~ 0
B
Text HLabel 6700 2400 2    50   Output ~ 0
OUT
$EndSCHEMATC
