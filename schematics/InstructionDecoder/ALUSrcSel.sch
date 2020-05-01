EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 370 484
Title "Transistor 2-to-4 Selector"
Date "2020-01-18"
Rev "1"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Device:R R?
U 1 1 5E96BB5E
P 1900 3250
F 0 "R?" V 1693 3250 50  0000 C CNN
F 1 "10K" V 1784 3250 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1830 3250 50  0001 C CNN
F 3 "~" H 1900 3250 50  0001 C CNN
	1    1900 3250
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E96BB4C
P 2250 3250
F 0 "Q?" H 2440 3296 50  0000 L CNN
F 1 "2N2222" H 2440 3205 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2450 3175 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2250 3250 50  0001 L CNN
	1    2250 3250
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5EE6ACC9
P 2350 2900
F 0 "R?" H 2420 2946 50  0000 L CNN
F 1 "1K" H 2420 2855 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2280 2900 50  0001 C CNN
F 3 "~" H 2350 2900 50  0001 C CNN
	1    2350 2900
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E96BB4E
P 2350 2750
F 0 "#PWR?" H 2350 2600 50  0001 C CNN
F 1 "VCC" H 2367 2923 50  0000 C CNN
F 2 "" H 2350 2750 50  0001 C CNN
F 3 "" H 2350 2750 50  0001 C CNN
	1    2350 2750
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5EE6ACCC
P 2350 3450
F 0 "#PWR?" H 2350 3200 50  0001 C CNN
F 1 "GND" H 2355 3277 50  0000 C CNN
F 2 "" H 2350 3450 50  0001 C CNN
F 3 "" H 2350 3450 50  0001 C CNN
	1    2350 3450
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E96BB52
P 1000 7400
F 0 "J?" V 1154 7212 50  0000 R CNN
F 1 "Power" V 1063 7212 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1000 7400 50  0001 C CNN
F 3 "~" H 1000 7400 50  0001 C CNN
	1    1000 7400
	0    -1   -1   0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E96BB51
P 1000 7050
F 0 "#PWR?" H 1000 6900 50  0001 C CNN
F 1 "VCC" H 950 7200 50  0000 C CNN
F 2 "" H 1000 7050 50  0001 C CNN
F 3 "" H 1000 7050 50  0001 C CNN
	1    1000 7050
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E96BB3B
P 1100 7050
F 0 "#PWR?" H 1100 6800 50  0001 C CNN
F 1 "GND" H 1050 6900 50  0000 C CNN
F 2 "" H 1100 7050 50  0001 C CNN
F 3 "" H 1100 7050 50  0001 C CNN
	1    1100 7050
	-1   0    0    1   
$EndComp
Wire Wire Line
	1000 7200 1000 7050
Wire Wire Line
	1100 7200 1100 7050
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5EDCBE9C
P 1500 7400
F 0 "J?" V 1654 7212 50  0000 R CNN
F 1 "Power" V 1563 7212 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1500 7400 50  0001 C CNN
F 3 "~" H 1500 7400 50  0001 C CNN
	1    1500 7400
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E96BB45
P 1950 7400
F 0 "J?" V 2104 7212 50  0000 R CNN
F 1 "Power" V 2013 7212 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1950 7400 50  0001 C CNN
F 3 "~" H 1950 7400 50  0001 C CNN
	1    1950 7400
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5EDCBEA0
P 1600 7050
F 0 "#PWR?" H 1600 6800 50  0001 C CNN
F 1 "GND" H 1550 6900 50  0000 C CNN
F 2 "" H 1600 7050 50  0001 C CNN
F 3 "" H 1600 7050 50  0001 C CNN
	1    1600 7050
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5EDCBEA2
P 2050 7050
F 0 "#PWR?" H 2050 6800 50  0001 C CNN
F 1 "GND" H 2000 6900 50  0000 C CNN
F 2 "" H 2050 7050 50  0001 C CNN
F 3 "" H 2050 7050 50  0001 C CNN
	1    2050 7050
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5EE6ACCE
P 1500 7050
F 0 "#PWR?" H 1500 6900 50  0001 C CNN
F 1 "VCC" H 1450 7200 50  0000 C CNN
F 2 "" H 1500 7050 50  0001 C CNN
F 3 "" H 1500 7050 50  0001 C CNN
	1    1500 7050
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5EDCBEA4
P 1950 7050
F 0 "#PWR?" H 1950 6900 50  0001 C CNN
F 1 "VCC" H 1900 7200 50  0000 C CNN
F 2 "" H 1950 7050 50  0001 C CNN
F 3 "" H 1950 7050 50  0001 C CNN
	1    1950 7050
	1    0    0    -1  
$EndComp
Wire Wire Line
	1500 7050 1500 7200
Wire Wire Line
	1600 7200 1600 7050
Wire Wire Line
	1950 7050 1950 7200
Wire Wire Line
	2050 7200 2050 7050
$Comp
L power:VCC #PWR?
U 1 1 5EDCBEA5
P 1000 5750
F 0 "#PWR?" H 1000 5600 50  0001 C CNN
F 1 "VCC" H 1017 5923 50  0000 C CNN
F 2 "" H 1000 5750 50  0001 C CNN
F 3 "" H 1000 5750 50  0001 C CNN
	1    1000 5750
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5EE6ACB6
P 1000 6250
F 0 "#PWR?" H 1000 6000 50  0001 C CNN
F 1 "GND" H 1005 6077 50  0000 C CNN
F 2 "" H 1000 6250 50  0001 C CNN
F 3 "" H 1000 6250 50  0001 C CNN
	1    1000 6250
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 5EDCBEA7
P 1000 6000
F 0 "C?" H 1115 6046 50  0000 L CNN
F 1 "0.1uF" H 1115 5955 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 1038 5850 50  0001 C CNN
F 3 "~" H 1000 6000 50  0001 C CNN
	1    1000 6000
	1    0    0    -1  
$EndComp
Wire Wire Line
	1000 5750 1000 5850
Wire Wire Line
	1000 6150 1000 6250
Wire Wire Line
	1100 3250 1600 3250
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E96BB53
P 4050 2950
F 0 "Q?" H 4240 2996 50  0000 L CNN
F 1 "2N2222" H 4240 2905 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4250 2875 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4050 2950 50  0001 L CNN
	1    4050 2950
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E96BB3C
P 3050 2950
F 0 "Q?" H 3240 2996 50  0000 L CNN
F 1 "2N2222" H 3240 2905 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3250 2875 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3050 2950 50  0001 L CNN
	1    3050 2950
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E96BB47
P 1900 2500
F 0 "R?" V 1693 2500 50  0000 C CNN
F 1 "10K" V 1784 2500 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1830 2500 50  0001 C CNN
F 3 "~" H 1900 2500 50  0001 C CNN
	1    1900 2500
	0    1    1    0   
$EndComp
Wire Wire Line
	1750 2500 1600 2500
Wire Wire Line
	1600 2500 1600 3250
Connection ~ 1600 3250
Wire Wire Line
	1600 3250 1750 3250
$Comp
L power:GND #PWR?
U 1 1 5E96BB54
P 4150 3150
F 0 "#PWR?" H 4150 2900 50  0001 C CNN
F 1 "GND" H 4155 2977 50  0000 C CNN
F 2 "" H 4150 3150 50  0001 C CNN
F 3 "" H 4150 3150 50  0001 C CNN
	1    4150 3150
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E96BB3D
P 1900 4800
F 0 "R?" V 1693 4800 50  0000 C CNN
F 1 "10K" V 1784 4800 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1830 4800 50  0001 C CNN
F 3 "~" H 1900 4800 50  0001 C CNN
	1    1900 4800
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E96BB3E
P 2250 4800
F 0 "Q?" H 2440 4846 50  0000 L CNN
F 1 "2N2222" H 2440 4755 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2450 4725 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2250 4800 50  0001 L CNN
	1    2250 4800
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 611A61AD
P 2350 4450
F 0 "R?" H 2420 4496 50  0000 L CNN
F 1 "1K" H 2420 4405 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2280 4450 50  0001 C CNN
F 3 "~" H 2350 4450 50  0001 C CNN
	1    2350 4450
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E96BB5F
P 2350 4300
F 0 "#PWR?" H 2350 4150 50  0001 C CNN
F 1 "VCC" H 2367 4473 50  0000 C CNN
F 2 "" H 2350 4300 50  0001 C CNN
F 3 "" H 2350 4300 50  0001 C CNN
	1    2350 4300
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 611A61AF
P 2350 5000
F 0 "#PWR?" H 2350 4750 50  0001 C CNN
F 1 "GND" H 2355 4827 50  0000 C CNN
F 2 "" H 2350 5000 50  0001 C CNN
F 3 "" H 2350 5000 50  0001 C CNN
	1    2350 5000
	1    0    0    -1  
$EndComp
Wire Wire Line
	1100 4800 1600 4800
Wire Wire Line
	3150 2750 3150 2550
Wire Wire Line
	4150 2750 4150 2550
Wire Wire Line
	1600 3900 1600 4800
Connection ~ 1600 4800
Wire Wire Line
	1600 4800 1750 4800
$Comp
L Device:R R?
U 1 1 5EE6ACBB
P 1950 3900
F 0 "R?" V 1743 3900 50  0000 C CNN
F 1 "10K" V 1834 3900 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1880 3900 50  0001 C CNN
F 3 "~" H 1950 3900 50  0001 C CNN
	1    1950 3900
	0    1    1    0   
$EndComp
Wire Wire Line
	1600 3900 1800 3900
Wire Wire Line
	2050 2500 2850 2500
Wire Wire Line
	3150 3150 4150 3150
Connection ~ 4150 3150
Wire Wire Line
	2850 2500 2850 2950
Connection ~ 4150 2550
Wire Wire Line
	3150 2550 4150 2550
$Comp
L Device:R R?
U 1 1 5E96BB3F
P 1900 1800
F 0 "R?" V 1693 1800 50  0000 C CNN
F 1 "10K" V 1784 1800 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1830 1800 50  0001 C CNN
F 3 "~" H 1900 1800 50  0001 C CNN
	1    1900 1800
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E96BB55
P 2250 1800
F 0 "Q?" H 2440 1846 50  0000 L CNN
F 1 "2N2222" H 2440 1755 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2450 1725 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2250 1800 50  0001 L CNN
	1    2250 1800
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5EE6ACDC
P 2350 1450
F 0 "R?" H 2420 1496 50  0000 L CNN
F 1 "1K" H 2420 1405 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2280 1450 50  0001 C CNN
F 3 "~" H 2350 1450 50  0001 C CNN
	1    2350 1450
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E96BB60
P 2350 1300
F 0 "#PWR?" H 2350 1150 50  0001 C CNN
F 1 "VCC" H 2367 1473 50  0000 C CNN
F 2 "" H 2350 1300 50  0001 C CNN
F 3 "" H 2350 1300 50  0001 C CNN
	1    2350 1300
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E96BB49
P 2350 2000
F 0 "#PWR?" H 2350 1750 50  0001 C CNN
F 1 "GND" H 2355 1827 50  0000 C CNN
F 2 "" H 2350 2000 50  0001 C CNN
F 3 "" H 2350 2000 50  0001 C CNN
	1    2350 2000
	1    0    0    -1  
$EndComp
Wire Wire Line
	1100 1800 1750 1800
$Comp
L 2n2222:2N2222 Q?
U 1 1 5EE6ACBE
P 5000 2950
F 0 "Q?" H 5190 2996 50  0000 L CNN
F 1 "2N2222" H 5190 2905 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5200 2875 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5000 2950 50  0001 L CNN
	1    5000 2950
	1    0    0    -1  
$EndComp
Wire Wire Line
	4150 3150 5100 3150
Wire Wire Line
	4150 2550 5100 2550
Connection ~ 5100 2550
Wire Wire Line
	5100 2550 5650 2550
Wire Wire Line
	5100 2550 5100 2750
$Comp
L Device:R R?
U 1 1 5EE6ACDD
P 5100 2400
F 0 "R?" H 5170 2446 50  0000 L CNN
F 1 "1K" H 5170 2355 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5030 2400 50  0001 C CNN
F 3 "~" H 5100 2400 50  0001 C CNN
	1    5100 2400
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E96BB58
P 5100 2250
F 0 "#PWR?" H 5100 2100 50  0001 C CNN
F 1 "VCC" H 5117 2423 50  0000 C CNN
F 2 "" H 5100 2250 50  0001 C CNN
F 3 "" H 5100 2250 50  0001 C CNN
	1    5100 2250
	1    0    0    -1  
$EndComp
Wire Wire Line
	4800 1600 2350 1600
Connection ~ 2350 1600
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E96BB40
P 4050 4150
F 0 "Q?" H 4240 4196 50  0000 L CNN
F 1 "2N2222" H 4240 4105 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4250 4075 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4050 4150 50  0001 L CNN
	1    4050 4150
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5EDCD94D
P 3050 4150
F 0 "Q?" H 3240 4196 50  0000 L CNN
F 1 "2N2222" H 3240 4105 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3250 4075 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3050 4150 50  0001 L CNN
	1    3050 4150
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E2772AF
P 4150 4350
F 0 "#PWR?" H 4150 4100 50  0001 C CNN
F 1 "GND" H 4155 4177 50  0000 C CNN
F 2 "" H 4150 4350 50  0001 C CNN
F 3 "" H 4150 4350 50  0001 C CNN
	1    4150 4350
	1    0    0    -1  
$EndComp
Wire Wire Line
	3150 3950 3150 3750
Wire Wire Line
	4150 3950 4150 3750
Wire Wire Line
	3150 4350 4150 4350
Connection ~ 4150 4350
Connection ~ 4150 3750
Wire Wire Line
	3150 3750 4150 3750
$Comp
L 2n2222:2N2222 Q?
U 1 1 60BE22AF
P 5000 4150
F 0 "Q?" H 5190 4196 50  0000 L CNN
F 1 "2N2222" H 5190 4105 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5200 4075 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5000 4150 50  0001 L CNN
	1    5000 4150
	1    0    0    -1  
$EndComp
Wire Wire Line
	4150 4350 5100 4350
Wire Wire Line
	4150 3750 5100 3750
Connection ~ 5100 3750
Wire Wire Line
	5100 3750 5650 3750
Wire Wire Line
	5100 3750 5100 3950
$Comp
L Device:R R?
U 1 1 60BE22B0
P 5100 3600
F 0 "R?" H 5170 3646 50  0000 L CNN
F 1 "1K" H 5170 3555 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5030 3600 50  0001 C CNN
F 3 "~" H 5100 3600 50  0001 C CNN
	1    5100 3600
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5EE6ACE1
P 5100 3450
F 0 "#PWR?" H 5100 3300 50  0001 C CNN
F 1 "VCC" H 5117 3623 50  0000 C CNN
F 2 "" H 5100 3450 50  0001 C CNN
F 3 "" H 5100 3450 50  0001 C CNN
	1    5100 3450
	1    0    0    -1  
$EndComp
Wire Wire Line
	4800 1600 4800 2950
Wire Wire Line
	4800 2950 4800 4150
Connection ~ 4800 2950
Wire Wire Line
	2350 3050 2750 3050
Wire Wire Line
	2750 4150 2850 4150
Connection ~ 2350 3050
Wire Wire Line
	3850 3900 3850 4150
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E96BB5A
P 4050 5500
F 0 "Q?" H 4240 5546 50  0000 L CNN
F 1 "2N2222" H 4240 5455 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4250 5425 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4050 5500 50  0001 L CNN
	1    4050 5500
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E96BB63
P 3050 5500
F 0 "Q?" H 3240 5546 50  0000 L CNN
F 1 "2N2222" H 3240 5455 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3250 5425 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3050 5500 50  0001 L CNN
	1    3050 5500
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5EE6ACE3
P 4150 5700
F 0 "#PWR?" H 4150 5450 50  0001 C CNN
F 1 "GND" H 4155 5527 50  0000 C CNN
F 2 "" H 4150 5700 50  0001 C CNN
F 3 "" H 4150 5700 50  0001 C CNN
	1    4150 5700
	1    0    0    -1  
$EndComp
Wire Wire Line
	3150 5300 3150 5100
Wire Wire Line
	4150 5300 4150 5100
Wire Wire Line
	3150 5700 4150 5700
Connection ~ 4150 5700
Connection ~ 4150 5100
Wire Wire Line
	3150 5100 4150 5100
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E96BB4B
P 5000 5500
F 0 "Q?" H 5190 5546 50  0000 L CNN
F 1 "2N2222" H 5190 5455 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5200 5425 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5000 5500 50  0001 L CNN
	1    5000 5500
	1    0    0    -1  
$EndComp
Wire Wire Line
	4150 5700 5100 5700
Wire Wire Line
	4150 5100 5100 5100
Connection ~ 5100 5100
Wire Wire Line
	5100 5100 5650 5100
Wire Wire Line
	5100 5100 5100 5300
$Comp
L Device:R R?
U 1 1 5EDCD956
P 5100 4950
F 0 "R?" H 5170 4996 50  0000 L CNN
F 1 "1K" H 5170 4905 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5030 4950 50  0001 C CNN
F 3 "~" H 5100 4950 50  0001 C CNN
	1    5100 4950
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5EDCD957
P 5100 4800
F 0 "#PWR?" H 5100 4650 50  0001 C CNN
F 1 "VCC" H 5117 4973 50  0000 C CNN
F 2 "" H 5100 4800 50  0001 C CNN
F 3 "" H 5100 4800 50  0001 C CNN
	1    5100 4800
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5EDCD958
P 4050 6700
F 0 "Q?" H 4240 6746 50  0000 L CNN
F 1 "2N2222" H 4240 6655 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4250 6625 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4050 6700 50  0001 L CNN
	1    4050 6700
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E96BB5C
P 3050 6700
F 0 "Q?" H 3240 6746 50  0000 L CNN
F 1 "2N2222" H 3240 6655 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3250 6625 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3050 6700 50  0001 L CNN
	1    3050 6700
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E96BB64
P 4150 6900
F 0 "#PWR?" H 4150 6650 50  0001 C CNN
F 1 "GND" H 4155 6727 50  0000 C CNN
F 2 "" H 4150 6900 50  0001 C CNN
F 3 "" H 4150 6900 50  0001 C CNN
	1    4150 6900
	1    0    0    -1  
$EndComp
Wire Wire Line
	3150 6500 3150 6300
Wire Wire Line
	4150 6500 4150 6300
Wire Wire Line
	3150 6900 4150 6900
Connection ~ 4150 6900
Connection ~ 4150 6300
Wire Wire Line
	3150 6300 4150 6300
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E96BB5D
P 5000 6700
F 0 "Q?" H 5190 6746 50  0000 L CNN
F 1 "2N2222" H 5190 6655 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5200 6625 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5000 6700 50  0001 L CNN
	1    5000 6700
	1    0    0    -1  
$EndComp
Wire Wire Line
	4150 6900 5100 6900
Wire Wire Line
	4150 6300 5100 6300
Connection ~ 5100 6300
Wire Wire Line
	5100 6300 5650 6300
Wire Wire Line
	5100 6300 5100 6500
$Comp
L Device:R R?
U 1 1 5E96BB67
P 5100 6150
F 0 "R?" H 5170 6196 50  0000 L CNN
F 1 "1K" H 5170 6105 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5030 6150 50  0001 C CNN
F 3 "~" H 5100 6150 50  0001 C CNN
	1    5100 6150
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 611A61CA
P 5100 6000
F 0 "#PWR?" H 5100 5850 50  0001 C CNN
F 1 "VCC" H 5117 6173 50  0000 C CNN
F 2 "" H 5100 6000 50  0001 C CNN
F 3 "" H 5100 6000 50  0001 C CNN
	1    5100 6000
	1    0    0    -1  
$EndComp
Wire Wire Line
	4800 4150 4800 5500
Wire Wire Line
	4800 5500 4800 6700
Connection ~ 4800 5500
Connection ~ 4800 4150
Wire Wire Line
	3850 5500 3850 6700
Wire Wire Line
	2100 3900 3850 3900
Wire Wire Line
	3850 2950 3850 3900
Connection ~ 3850 3900
Connection ~ 2850 2950
Wire Wire Line
	2850 2950 2850 5500
Wire Wire Line
	2750 6700 2850 6700
Wire Wire Line
	2750 3050 2750 4150
Connection ~ 2750 4150
Wire Wire Line
	2750 4150 2750 6700
Wire Wire Line
	3850 4600 2350 4600
Connection ~ 2350 4600
Wire Wire Line
	3850 4600 3850 5500
Connection ~ 3850 5500
Text HLabel 1100 1800 0    50   Input ~ 0
EN
Text HLabel 1100 3250 0    50   Input ~ 0
D0
Text HLabel 1100 4800 0    50   Input ~ 0
D1
Text HLabel 5650 2550 2    50   Output ~ 0
EN1
Text HLabel 5650 3750 2    50   Output ~ 0
EN2
Text HLabel 5650 5100 2    50   Output ~ 0
EN3
Text HLabel 5650 6300 2    50   Output ~ 0
EN4
$EndSCHEMATC
