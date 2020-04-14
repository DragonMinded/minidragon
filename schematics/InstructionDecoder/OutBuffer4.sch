EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 411 478
Title "High Current Buffer"
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
U 1 1 5F52B603
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
U 1 1 5F52B607
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
U 1 1 5F52B60E
P 800 7600
F 0 "J?" V 954 7412 50  0000 R CNN
F 1 "Power" V 863 7412 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 800 7600 50  0001 C CNN
F 3 "~" H 800 7600 50  0001 C CNN
	1    800  7600
	0    -1   -1   0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F52B60F
P 800 7250
F 0 "#PWR?" H 800 7100 50  0001 C CNN
F 1 "VCC" H 750 7400 50  0000 C CNN
F 2 "" H 800 7250 50  0001 C CNN
F 3 "" H 800 7250 50  0001 C CNN
	1    800  7250
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F52B610
P 900 7250
F 0 "#PWR?" H 900 7000 50  0001 C CNN
F 1 "GND" H 850 7100 50  0000 C CNN
F 2 "" H 900 7250 50  0001 C CNN
F 3 "" H 900 7250 50  0001 C CNN
	1    900  7250
	-1   0    0    1   
$EndComp
Wire Wire Line
	800  7400 800  7250
Wire Wire Line
	900  7400 900  7250
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5DFF2116
P 1300 7600
F 0 "J?" V 1454 7412 50  0000 R CNN
F 1 "Power" V 1363 7412 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1300 7600 50  0001 C CNN
F 3 "~" H 1300 7600 50  0001 C CNN
	1    1300 7600
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5F1746BD
P 1750 7600
F 0 "J?" V 1904 7412 50  0000 R CNN
F 1 "Power" V 1813 7412 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1750 7600 50  0001 C CNN
F 3 "~" H 1750 7600 50  0001 C CNN
	1    1750 7600
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F1746BE
P 1400 7250
F 0 "#PWR?" H 1400 7000 50  0001 C CNN
F 1 "GND" H 1350 7100 50  0000 C CNN
F 2 "" H 1400 7250 50  0001 C CNN
F 3 "" H 1400 7250 50  0001 C CNN
	1    1400 7250
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F1746BF
P 1850 7250
F 0 "#PWR?" H 1850 7000 50  0001 C CNN
F 1 "GND" H 1800 7100 50  0000 C CNN
F 2 "" H 1850 7250 50  0001 C CNN
F 3 "" H 1850 7250 50  0001 C CNN
	1    1850 7250
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F52B608
P 1300 7250
F 0 "#PWR?" H 1300 7100 50  0001 C CNN
F 1 "VCC" H 1250 7400 50  0000 C CNN
F 2 "" H 1300 7250 50  0001 C CNN
F 3 "" H 1300 7250 50  0001 C CNN
	1    1300 7250
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F1746C2
P 1750 7250
F 0 "#PWR?" H 1750 7100 50  0001 C CNN
F 1 "VCC" H 1700 7400 50  0000 C CNN
F 2 "" H 1750 7250 50  0001 C CNN
F 3 "" H 1750 7250 50  0001 C CNN
	1    1750 7250
	1    0    0    -1  
$EndComp
Wire Wire Line
	1300 7250 1300 7400
Wire Wire Line
	1400 7400 1400 7250
Wire Wire Line
	1750 7250 1750 7400
Wire Wire Line
	1850 7400 1850 7250
$Comp
L power:VCC #PWR?
U 1 1 5E004479
P 3800 6900
F 0 "#PWR?" H 3800 6750 50  0001 C CNN
F 1 "VCC" H 3817 7073 50  0000 C CNN
F 2 "" H 3800 6900 50  0001 C CNN
F 3 "" H 3800 6900 50  0001 C CNN
	1    3800 6900
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F1746C5
P 3800 7400
F 0 "#PWR?" H 3800 7150 50  0001 C CNN
F 1 "GND" H 3805 7227 50  0000 C CNN
F 2 "" H 3800 7400 50  0001 C CNN
F 3 "" H 3800 7400 50  0001 C CNN
	1    3800 7400
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 5E005357
P 3800 7150
F 0 "C?" H 3915 7196 50  0000 L CNN
F 1 "0.1uF" H 3915 7105 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 3838 7000 50  0001 C CNN
F 3 "~" H 3800 7150 50  0001 C CNN
	1    3800 7150
	1    0    0    -1  
$EndComp
Wire Wire Line
	3800 6900 3800 7000
Wire Wire Line
	3800 7300 3800 7400
$Comp
L power:VCC #PWR?
U 1 1 5DFFB9CB
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
U 1 1 5F1746BA
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
U 1 1 5F1746CA
P 3000 3250
F 0 "R?" H 3070 3296 50  0000 L CNN
F 1 "1K" H 3070 3205 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2930 3250 50  0001 C CNN
F 3 "~" H 3000 3250 50  0001 C CNN
	1    3000 3250
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F1746CB
P 3000 3400
F 0 "#PWR?" H 3000 3150 50  0001 C CNN
F 1 "GND" H 3005 3227 50  0000 C CNN
F 2 "" H 3000 3400 50  0001 C CNN
F 3 "" H 3000 3400 50  0001 C CNN
	1    3000 3400
	1    0    0    -1  
$EndComp
Wire Wire Line
	3000 3100 3000 3050
Connection ~ 3000 3100
$Comp
L power:VCC #PWR?
U 1 1 5F1746CC
P 3000 2650
F 0 "#PWR?" H 3000 2500 50  0001 C CNN
F 1 "VCC" H 3017 2823 50  0000 C CNN
F 2 "" H 3000 2650 50  0001 C CNN
F 3 "" H 3000 2650 50  0001 C CNN
	1    3000 2650
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F1746CD
P 2900 2850
F 0 "Q?" H 3090 2896 50  0000 L CNN
F 1 "2N2222" H 3090 2805 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3100 2775 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2900 2850 50  0001 L CNN
	1    2900 2850
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5F52B615
P 3800 2550
F 0 "R?" H 3870 2596 50  0000 L CNN
F 1 "1K" H 3870 2505 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3730 2550 50  0001 C CNN
F 3 "~" H 3800 2550 50  0001 C CNN
	1    3800 2550
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F52B616
P 3800 2700
F 0 "#PWR?" H 3800 2450 50  0001 C CNN
F 1 "GND" H 3805 2527 50  0000 C CNN
F 2 "" H 3800 2700 50  0001 C CNN
F 3 "" H 3800 2700 50  0001 C CNN
	1    3800 2700
	1    0    0    -1  
$EndComp
Wire Wire Line
	3800 2400 3800 2350
Connection ~ 3800 2400
$Comp
L power:VCC #PWR?
U 1 1 5F1746D0
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
U 1 1 5F52B618
P 3700 2150
F 0 "Q?" H 3890 2196 50  0000 L CNN
F 1 "2N2222" H 3890 2105 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3900 2075 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3700 2150 50  0001 L CNN
	1    3700 2150
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5F52B619
P 3800 4150
F 0 "R?" H 3870 4196 50  0000 L CNN
F 1 "1K" H 3870 4105 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3730 4150 50  0001 C CNN
F 3 "~" H 3800 4150 50  0001 C CNN
	1    3800 4150
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F52B61A
P 3800 4300
F 0 "#PWR?" H 3800 4050 50  0001 C CNN
F 1 "GND" H 3805 4127 50  0000 C CNN
F 2 "" H 3800 4300 50  0001 C CNN
F 3 "" H 3800 4300 50  0001 C CNN
	1    3800 4300
	1    0    0    -1  
$EndComp
Wire Wire Line
	3800 4000 3800 3950
Connection ~ 3800 4000
$Comp
L power:VCC #PWR?
U 1 1 5F52B61B
P 3800 3550
F 0 "#PWR?" H 3800 3400 50  0001 C CNN
F 1 "VCC" H 3817 3723 50  0000 C CNN
F 2 "" H 3800 3550 50  0001 C CNN
F 3 "" H 3800 3550 50  0001 C CNN
	1    3800 3550
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E92B20B
P 3700 3750
F 0 "Q?" H 3890 3796 50  0000 L CNN
F 1 "2N2222" H 3890 3705 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3900 3675 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3700 3750 50  0001 L CNN
	1    3700 3750
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5F1746D6
P 5150 1900
F 0 "R?" H 5220 1946 50  0000 L CNN
F 1 "1K" H 5220 1855 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5080 1900 50  0001 C CNN
F 3 "~" H 5150 1900 50  0001 C CNN
	1    5150 1900
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E93A5B9
P 5150 2050
F 0 "#PWR?" H 5150 1800 50  0001 C CNN
F 1 "GND" H 5155 1877 50  0000 C CNN
F 2 "" H 5150 2050 50  0001 C CNN
F 3 "" H 5150 2050 50  0001 C CNN
	1    5150 2050
	1    0    0    -1  
$EndComp
Wire Wire Line
	5150 1750 5150 1700
Connection ~ 5150 1750
$Comp
L power:VCC #PWR?
U 1 1 5F1746D8
P 5150 1300
F 0 "#PWR?" H 5150 1150 50  0001 C CNN
F 1 "VCC" H 5167 1473 50  0000 C CNN
F 2 "" H 5150 1300 50  0001 C CNN
F 3 "" H 5150 1300 50  0001 C CNN
	1    5150 1300
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F52B620
P 5050 1500
F 0 "Q?" H 5240 1546 50  0000 L CNN
F 1 "2N2222" H 5240 1455 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5250 1425 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5050 1500 50  0001 L CNN
	1    5050 1500
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5F1746DA
P 5600 3600
F 0 "R?" H 5670 3646 50  0000 L CNN
F 1 "1K" H 5670 3555 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5530 3600 50  0001 C CNN
F 3 "~" H 5600 3600 50  0001 C CNN
	1    5600 3600
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E93A5D4
P 5600 3750
F 0 "#PWR?" H 5600 3500 50  0001 C CNN
F 1 "GND" H 5605 3577 50  0000 C CNN
F 2 "" H 5600 3750 50  0001 C CNN
F 3 "" H 5600 3750 50  0001 C CNN
	1    5600 3750
	1    0    0    -1  
$EndComp
Wire Wire Line
	5600 3450 5600 3400
Connection ~ 5600 3450
$Comp
L power:VCC #PWR?
U 1 1 5F1746DC
P 5600 3000
F 0 "#PWR?" H 5600 2850 50  0001 C CNN
F 1 "VCC" H 5617 3173 50  0000 C CNN
F 2 "" H 5600 3000 50  0001 C CNN
F 3 "" H 5600 3000 50  0001 C CNN
	1    5600 3000
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F52B624
P 5500 3200
F 0 "Q?" H 5690 3246 50  0000 L CNN
F 1 "2N2222" H 5690 3155 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5700 3125 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5500 3200 50  0001 L CNN
	1    5500 3200
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E93A5E9
P 6400 2900
F 0 "R?" H 6470 2946 50  0000 L CNN
F 1 "1K" H 6470 2855 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6330 2900 50  0001 C CNN
F 3 "~" H 6400 2900 50  0001 C CNN
	1    6400 2900
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F52B626
P 6400 3050
F 0 "#PWR?" H 6400 2800 50  0001 C CNN
F 1 "GND" H 6405 2877 50  0000 C CNN
F 2 "" H 6400 3050 50  0001 C CNN
F 3 "" H 6400 3050 50  0001 C CNN
	1    6400 3050
	1    0    0    -1  
$EndComp
Wire Wire Line
	6400 2750 6400 2700
Connection ~ 6400 2750
$Comp
L power:VCC #PWR?
U 1 1 5F1746E0
P 6400 2300
F 0 "#PWR?" H 6400 2150 50  0001 C CNN
F 1 "VCC" H 6417 2473 50  0000 C CNN
F 2 "" H 6400 2300 50  0001 C CNN
F 3 "" H 6400 2300 50  0001 C CNN
	1    6400 2300
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F1746E1
P 6300 2500
F 0 "Q?" H 6490 2546 50  0000 L CNN
F 1 "2N2222" H 6490 2455 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6500 2425 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6300 2500 50  0001 L CNN
	1    6300 2500
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5F52B629
P 6400 4500
F 0 "R?" H 6470 4546 50  0000 L CNN
F 1 "1K" H 6470 4455 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6330 4500 50  0001 C CNN
F 3 "~" H 6400 4500 50  0001 C CNN
	1    6400 4500
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E93A60A
P 6400 4650
F 0 "#PWR?" H 6400 4400 50  0001 C CNN
F 1 "GND" H 6405 4477 50  0000 C CNN
F 2 "" H 6400 4650 50  0001 C CNN
F 3 "" H 6400 4650 50  0001 C CNN
	1    6400 4650
	1    0    0    -1  
$EndComp
Wire Wire Line
	6400 4350 6400 4300
Connection ~ 6400 4350
$Comp
L power:VCC #PWR?
U 1 1 5E93A613
P 6400 3900
F 0 "#PWR?" H 6400 3750 50  0001 C CNN
F 1 "VCC" H 6417 4073 50  0000 C CNN
F 2 "" H 6400 3900 50  0001 C CNN
F 3 "" H 6400 3900 50  0001 C CNN
	1    6400 3900
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F1746E5
P 6300 4100
F 0 "Q?" H 6490 4146 50  0000 L CNN
F 1 "2N2222" H 6490 4055 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6500 4025 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6300 4100 50  0001 L CNN
	1    6300 4100
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
	3900 650  7400 650 
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
	4500 750  7400 750 
Wire Wire Line
	3800 2400 4500 2400
Wire Wire Line
	1050 1100 2450 1100
Wire Wire Line
	2450 1100 2450 2850
Wire Wire Line
	2450 2850 2700 2850
Wire Wire Line
	4600 3100 4600 850 
Wire Wire Line
	4600 850  7400 850 
Wire Wire Line
	3000 3100 4600 3100
Wire Wire Line
	1050 1200 2400 1200
Wire Wire Line
	2400 1200 2400 3750
Wire Wire Line
	2400 3750 3500 3750
Wire Wire Line
	4700 4000 4700 950 
Wire Wire Line
	4700 950  7400 950 
Wire Wire Line
	3800 4000 4700 4000
Wire Wire Line
	1050 1300 2350 1300
Wire Wire Line
	2350 1300 2350 4650
Wire Wire Line
	2350 4650 4800 4650
Wire Wire Line
	4800 4650 4800 1500
Wire Wire Line
	4800 1500 4850 1500
Wire Wire Line
	5700 1750 5700 1050
Wire Wire Line
	5700 1050 7400 1050
Wire Wire Line
	5150 1750 5700 1750
Wire Wire Line
	1050 1400 2300 1400
Wire Wire Line
	2300 1400 2300 4700
Wire Wire Line
	2300 4700 4900 4700
Wire Wire Line
	4900 4700 4900 2500
Wire Wire Line
	4900 2500 6100 2500
Wire Wire Line
	6950 2750 6950 1150
Wire Wire Line
	6950 1150 7400 1150
Wire Wire Line
	6400 2750 6950 2750
Wire Wire Line
	2250 1500 2250 4750
Wire Wire Line
	2250 4750 5000 4750
Wire Wire Line
	5000 4750 5000 3200
Wire Wire Line
	5000 3200 5300 3200
Wire Wire Line
	1050 1500 2250 1500
Wire Wire Line
	7050 3450 7050 1250
Wire Wire Line
	7050 1250 7400 1250
Wire Wire Line
	5600 3450 7050 3450
Wire Wire Line
	1050 1600 2200 1600
Wire Wire Line
	2200 1600 2200 4800
Wire Wire Line
	2200 4800 5100 4800
Wire Wire Line
	5100 4800 5100 4100
Wire Wire Line
	5100 4100 6100 4100
Wire Wire Line
	7150 4350 7150 1350
Wire Wire Line
	7150 1350 7400 1350
Wire Wire Line
	6400 4350 7150 4350
Text HLabel 7400 650  2    50   Output ~ 0
OUT1
Text HLabel 7400 750  2    50   Output ~ 0
OUT2
Text HLabel 7400 850  2    50   Output ~ 0
OUT3
Text HLabel 7400 950  2    50   Output ~ 0
OUT4
Text HLabel 7400 1050 2    50   Output ~ 0
OUT5
Text HLabel 7400 1150 2    50   Output ~ 0
OUT6
Text HLabel 7400 1250 2    50   Output ~ 0
OUT7
Text HLabel 7400 1350 2    50   Output ~ 0
OUT8
Text HLabel 1050 900  0    50   Input ~ 0
IN1
Text HLabel 1050 1000 0    50   Input ~ 0
IN2
Text HLabel 1050 1100 0    50   Input ~ 0
IN3
Text HLabel 1050 1200 0    50   Input ~ 0
IN4
Text HLabel 1050 1300 0    50   Input ~ 0
IN5
Text HLabel 1050 1400 0    50   Input ~ 0
IN6
Text HLabel 1050 1500 0    50   Input ~ 0
IN7
Text HLabel 1050 1600 0    50   Input ~ 0
IN8
$EndSCHEMATC
