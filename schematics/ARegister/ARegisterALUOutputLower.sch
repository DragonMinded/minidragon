EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 123 484
Title "8-bit Bus Output Circuit"
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
U 1 1 5E74056D
P 1650 1500
F 0 "R?" V 1443 1500 50  0000 C CNN
F 1 "10K" V 1534 1500 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1580 1500 50  0001 C CNN
F 3 "~" H 1650 1500 50  0001 C CNN
	1    1650 1500
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D042D
P 2000 1500
F 0 "Q?" H 2190 1546 50  0000 L CNN
F 1 "2N2222" H 2190 1455 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2200 1425 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2000 1500 50  0001 L CNN
	1    2000 1500
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E693F5B
P 2100 1100
F 0 "R?" H 2030 1054 50  0000 R CNN
F 1 "1K" H 2030 1145 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2030 1100 50  0001 C CNN
F 3 "~" H 2100 1100 50  0001 C CNN
	1    2100 1100
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D0452
P 2100 950
F 0 "#PWR?" H 2100 800 50  0001 C CNN
F 1 "VCC" H 2117 1123 50  0000 C CNN
F 2 "" H 2100 950 50  0001 C CNN
F 3 "" H 2100 950 50  0001 C CNN
	1    2100 950 
	1    0    0    -1  
$EndComp
Wire Wire Line
	2100 1300 2100 1250
$Comp
L Device:R R?
U 1 1 5F6D0425
P 2650 1250
F 0 "R?" V 2443 1250 50  0000 C CNN
F 1 "1K" V 2534 1250 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2580 1250 50  0001 C CNN
F 3 "~" H 2650 1250 50  0001 C CNN
	1    2650 1250
	0    1    1    0   
$EndComp
Wire Wire Line
	2100 1250 2500 1250
Connection ~ 2100 1250
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E74056A
P 3700 2650
F 0 "Q?" H 3890 2696 50  0000 L CNN
F 1 "2N2222" H 3890 2605 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3900 2575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3700 2650 50  0001 L CNN
	1    3700 2650
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D043D
P 4400 2950
F 0 "Q?" H 4590 2996 50  0000 L CNN
F 1 "2N2222" H 4590 2905 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4600 2875 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4400 2950 50  0001 L CNN
	1    4400 2950
	1    0    0    -1  
$EndComp
Wire Wire Line
	3800 2850 3800 3150
Wire Wire Line
	3800 3150 4500 3150
$Comp
L power:GND #PWR?
U 1 1 5F6D0434
P 3800 3150
F 0 "#PWR?" H 3800 2900 50  0001 C CNN
F 1 "GND" H 3805 2977 50  0000 C CNN
F 2 "" H 3800 3150 50  0001 C CNN
F 3 "" H 3800 3150 50  0001 C CNN
	1    3800 3150
	1    0    0    -1  
$EndComp
Connection ~ 3800 3150
$Comp
L Device:R R?
U 1 1 5F6D0446
P 4500 2300
F 0 "R?" H 4430 2254 50  0000 R CNN
F 1 "1K" H 4430 2345 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4430 2300 50  0001 C CNN
F 3 "~" H 4500 2300 50  0001 C CNN
	1    4500 2300
	-1   0    0    1   
$EndComp
Wire Wire Line
	3800 2450 4500 2450
Wire Wire Line
	4500 2750 4500 2450
Connection ~ 4500 2450
$Comp
L power:VCC #PWR?
U 1 1 5F6D043F
P 4500 2150
F 0 "#PWR?" H 4500 2000 50  0001 C CNN
F 1 "VCC" H 4517 2323 50  0000 C CNN
F 2 "" H 4500 2150 50  0001 C CNN
F 3 "" H 4500 2150 50  0001 C CNN
	1    4500 2150
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D0465
P 4850 2450
F 0 "Q?" H 5040 2496 50  0000 L CNN
F 1 "2N2222" H 5040 2405 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5050 2375 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4850 2450 50  0001 L CNN
	1    4850 2450
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E7A14E4
P 4950 2650
F 0 "#PWR?" H 4950 2400 50  0001 C CNN
F 1 "GND" H 4955 2477 50  0000 C CNN
F 2 "" H 4950 2650 50  0001 C CNN
F 3 "" H 4950 2650 50  0001 C CNN
	1    4950 2650
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5F6D0428
P 4000 2950
F 0 "R?" V 4100 2950 50  0000 C CNN
F 1 "10K" V 3900 2950 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3930 2950 50  0001 C CNN
F 3 "~" H 4000 2950 50  0001 C CNN
	1    4000 2950
	0    1    1    0   
$EndComp
Wire Wire Line
	4150 2950 4200 2950
Wire Wire Line
	4500 2450 4650 2450
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D044B
P 3700 1250
F 0 "Q?" H 3890 1296 50  0000 L CNN
F 1 "2N2222" H 3890 1205 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3900 1175 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3700 1250 50  0001 L CNN
	1    3700 1250
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E7A14F3
P 4400 1550
F 0 "Q?" H 4590 1596 50  0000 L CNN
F 1 "2N2222" H 4590 1505 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4600 1475 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4400 1550 50  0001 L CNN
	1    4400 1550
	1    0    0    -1  
$EndComp
Wire Wire Line
	3800 1450 3800 1750
Wire Wire Line
	3800 1750 4500 1750
$Comp
L power:GND #PWR?
U 1 1 5F6D042E
P 3800 1750
F 0 "#PWR?" H 3800 1500 50  0001 C CNN
F 1 "GND" H 3805 1577 50  0000 C CNN
F 2 "" H 3800 1750 50  0001 C CNN
F 3 "" H 3800 1750 50  0001 C CNN
	1    3800 1750
	1    0    0    -1  
$EndComp
Connection ~ 3800 1750
$Comp
L Device:R R?
U 1 1 5F6D0442
P 4500 900
F 0 "R?" H 4430 854 50  0000 R CNN
F 1 "1K" H 4430 945 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4430 900 50  0001 C CNN
F 3 "~" H 4500 900 50  0001 C CNN
	1    4500 900 
	-1   0    0    1   
$EndComp
Wire Wire Line
	3800 1050 4500 1050
Wire Wire Line
	4500 1350 4500 1050
Connection ~ 4500 1050
$Comp
L power:VCC #PWR?
U 1 1 5F6D0420
P 4500 750
F 0 "#PWR?" H 4500 600 50  0001 C CNN
F 1 "VCC" H 4517 923 50  0000 C CNN
F 2 "" H 4500 750 50  0001 C CNN
F 3 "" H 4500 750 50  0001 C CNN
	1    4500 750 
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E74057E
P 4850 1050
F 0 "Q?" H 5040 1096 50  0000 L CNN
F 1 "2N2222" H 5040 1005 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5050 975 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4850 1050 50  0001 L CNN
	1    4850 1050
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E7A14CF
P 4950 1250
F 0 "#PWR?" H 4950 1000 50  0001 C CNN
F 1 "GND" H 4955 1077 50  0000 C CNN
F 2 "" H 4950 1250 50  0001 C CNN
F 3 "" H 4950 1250 50  0001 C CNN
	1    4950 1250
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E7A14D0
P 4000 1550
F 0 "R?" V 4100 1550 50  0000 C CNN
F 1 "10K" V 3900 1550 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3930 1550 50  0001 C CNN
F 3 "~" H 4000 1550 50  0001 C CNN
	1    4000 1550
	0    1    1    0   
$EndComp
Wire Wire Line
	4150 1550 4200 1550
Wire Wire Line
	4500 1050 4650 1050
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E7A14B7
P 3700 5450
F 0 "Q?" H 3890 5496 50  0000 L CNN
F 1 "2N2222" H 3890 5405 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3900 5375 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3700 5450 50  0001 L CNN
	1    3700 5450
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D045E
P 4400 5750
F 0 "Q?" H 4590 5796 50  0000 L CNN
F 1 "2N2222" H 4590 5705 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4600 5675 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4400 5750 50  0001 L CNN
	1    4400 5750
	1    0    0    -1  
$EndComp
Wire Wire Line
	3800 5650 3800 5950
Wire Wire Line
	3800 5950 4500 5950
$Comp
L power:GND #PWR?
U 1 1 5E7405A7
P 3800 5950
F 0 "#PWR?" H 3800 5700 50  0001 C CNN
F 1 "GND" H 3805 5777 50  0000 C CNN
F 2 "" H 3800 5950 50  0001 C CNN
F 3 "" H 3800 5950 50  0001 C CNN
	1    3800 5950
	1    0    0    -1  
$EndComp
Connection ~ 3800 5950
$Comp
L Device:R R?
U 1 1 5F6D044D
P 4500 5100
F 0 "R?" H 4430 5054 50  0000 R CNN
F 1 "1K" H 4430 5145 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4430 5100 50  0001 C CNN
F 3 "~" H 4500 5100 50  0001 C CNN
	1    4500 5100
	-1   0    0    1   
$EndComp
Wire Wire Line
	3800 5250 4500 5250
Wire Wire Line
	4500 5550 4500 5250
Connection ~ 4500 5250
$Comp
L power:VCC #PWR?
U 1 1 5F6D044E
P 4500 4950
F 0 "#PWR?" H 4500 4800 50  0001 C CNN
F 1 "VCC" H 4517 5123 50  0000 C CNN
F 2 "" H 4500 4950 50  0001 C CNN
F 3 "" H 4500 4950 50  0001 C CNN
	1    4500 4950
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D044F
P 4850 5250
F 0 "Q?" H 5040 5296 50  0000 L CNN
F 1 "2N2222" H 5040 5205 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5050 5175 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4850 5250 50  0001 L CNN
	1    4850 5250
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D0448
P 4950 5450
F 0 "#PWR?" H 4950 5200 50  0001 C CNN
F 1 "GND" H 4955 5277 50  0000 C CNN
F 2 "" H 4950 5450 50  0001 C CNN
F 3 "" H 4950 5450 50  0001 C CNN
	1    4950 5450
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E693F6A
P 4000 5750
F 0 "R?" V 4100 5750 50  0000 C CNN
F 1 "10K" V 3900 5750 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3930 5750 50  0001 C CNN
F 3 "~" H 4000 5750 50  0001 C CNN
	1    4000 5750
	0    1    1    0   
$EndComp
Wire Wire Line
	4150 5750 4200 5750
Wire Wire Line
	4500 5250 4650 5250
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D0421
P 3700 4050
F 0 "Q?" H 3890 4096 50  0000 L CNN
F 1 "2N2222" H 3890 4005 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3900 3975 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3700 4050 50  0001 L CNN
	1    3700 4050
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D044A
P 4400 4350
F 0 "Q?" H 4590 4396 50  0000 L CNN
F 1 "2N2222" H 4590 4305 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4600 4275 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4400 4350 50  0001 L CNN
	1    4400 4350
	1    0    0    -1  
$EndComp
Wire Wire Line
	3800 4250 3800 4550
Wire Wire Line
	3800 4550 4500 4550
$Comp
L power:GND #PWR?
U 1 1 5F6D041F
P 3800 4550
F 0 "#PWR?" H 3800 4300 50  0001 C CNN
F 1 "GND" H 3805 4377 50  0000 C CNN
F 2 "" H 3800 4550 50  0001 C CNN
F 3 "" H 3800 4550 50  0001 C CNN
	1    3800 4550
	1    0    0    -1  
$EndComp
Connection ~ 3800 4550
$Comp
L Device:R R?
U 1 1 5F6D045F
P 4500 3700
F 0 "R?" H 4430 3654 50  0000 R CNN
F 1 "1K" H 4430 3745 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4430 3700 50  0001 C CNN
F 3 "~" H 4500 3700 50  0001 C CNN
	1    4500 3700
	-1   0    0    1   
$EndComp
Wire Wire Line
	3800 3850 4500 3850
Wire Wire Line
	4500 4150 4500 3850
Connection ~ 4500 3850
$Comp
L power:VCC #PWR?
U 1 1 5F6D043E
P 4500 3550
F 0 "#PWR?" H 4500 3400 50  0001 C CNN
F 1 "VCC" H 4517 3723 50  0000 C CNN
F 2 "" H 4500 3550 50  0001 C CNN
F 3 "" H 4500 3550 50  0001 C CNN
	1    4500 3550
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E7A14D2
P 4850 3850
F 0 "Q?" H 5040 3896 50  0000 L CNN
F 1 "2N2222" H 5040 3805 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5050 3775 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4850 3850 50  0001 L CNN
	1    4850 3850
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5EB613A7
P 4950 4050
F 0 "#PWR?" H 4950 3800 50  0001 C CNN
F 1 "GND" H 4955 3877 50  0000 C CNN
F 2 "" H 4950 4050 50  0001 C CNN
F 3 "" H 4950 4050 50  0001 C CNN
	1    4950 4050
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5F6D0456
P 4000 4350
F 0 "R?" V 4100 4350 50  0000 C CNN
F 1 "10K" V 3900 4350 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3930 4350 50  0001 C CNN
F 3 "~" H 4000 4350 50  0001 C CNN
	1    4000 4350
	0    1    1    0   
$EndComp
Wire Wire Line
	4150 4350 4200 4350
Wire Wire Line
	4500 3850 4650 3850
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E740575
P 5800 2950
F 0 "Q?" H 5990 2996 50  0000 L CNN
F 1 "2N2222" H 5990 2905 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6000 2875 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5800 2950 50  0001 L CNN
	1    5800 2950
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D0436
P 6500 3250
F 0 "Q?" H 6690 3296 50  0000 L CNN
F 1 "2N2222" H 6690 3205 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6700 3175 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6500 3250 50  0001 L CNN
	1    6500 3250
	1    0    0    -1  
$EndComp
Wire Wire Line
	5900 3150 5900 3450
Wire Wire Line
	5900 3450 6600 3450
$Comp
L power:GND #PWR?
U 1 1 5E740596
P 5900 3450
F 0 "#PWR?" H 5900 3200 50  0001 C CNN
F 1 "GND" H 5905 3277 50  0000 C CNN
F 2 "" H 5900 3450 50  0001 C CNN
F 3 "" H 5900 3450 50  0001 C CNN
	1    5900 3450
	1    0    0    -1  
$EndComp
Connection ~ 5900 3450
$Comp
L Device:R R?
U 1 1 5E7A14FA
P 6600 2600
F 0 "R?" H 6530 2554 50  0000 R CNN
F 1 "1K" H 6530 2645 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6530 2600 50  0001 C CNN
F 3 "~" H 6600 2600 50  0001 C CNN
	1    6600 2600
	-1   0    0    1   
$EndComp
Wire Wire Line
	5900 2750 6600 2750
Wire Wire Line
	6600 3050 6600 2750
Connection ~ 6600 2750
$Comp
L power:VCC #PWR?
U 1 1 5F6D0437
P 6600 2450
F 0 "#PWR?" H 6600 2300 50  0001 C CNN
F 1 "VCC" H 6617 2623 50  0000 C CNN
F 2 "" H 6600 2450 50  0001 C CNN
F 3 "" H 6600 2450 50  0001 C CNN
	1    6600 2450
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E74059F
P 6950 2750
F 0 "Q?" H 7140 2796 50  0000 L CNN
F 1 "2N2222" H 7140 2705 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7150 2675 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6950 2750 50  0001 L CNN
	1    6950 2750
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D0438
P 7050 2950
F 0 "#PWR?" H 7050 2700 50  0001 C CNN
F 1 "GND" H 7055 2777 50  0000 C CNN
F 2 "" H 7050 2950 50  0001 C CNN
F 3 "" H 7050 2950 50  0001 C CNN
	1    7050 2950
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E601191
P 6100 3250
F 0 "R?" V 6200 3250 50  0000 C CNN
F 1 "10K" V 6000 3250 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6030 3250 50  0001 C CNN
F 3 "~" H 6100 3250 50  0001 C CNN
	1    6100 3250
	0    1    1    0   
$EndComp
Wire Wire Line
	6250 3250 6300 3250
Wire Wire Line
	6600 2750 6750 2750
$Comp
L 2n2222:2N2222 Q?
U 1 1 5EB613AA
P 5800 1550
F 0 "Q?" H 5990 1596 50  0000 L CNN
F 1 "2N2222" H 5990 1505 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6000 1475 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5800 1550 50  0001 L CNN
	1    5800 1550
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D045A
P 6500 1850
F 0 "Q?" H 6690 1896 50  0000 L CNN
F 1 "2N2222" H 6690 1805 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6700 1775 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6500 1850 50  0001 L CNN
	1    6500 1850
	1    0    0    -1  
$EndComp
Wire Wire Line
	5900 1750 5900 2050
Wire Wire Line
	5900 2050 6600 2050
$Comp
L power:GND #PWR?
U 1 1 5EB613D3
P 5900 2050
F 0 "#PWR?" H 5900 1800 50  0001 C CNN
F 1 "GND" H 5905 1877 50  0000 C CNN
F 2 "" H 5900 2050 50  0001 C CNN
F 3 "" H 5900 2050 50  0001 C CNN
	1    5900 2050
	1    0    0    -1  
$EndComp
Connection ~ 5900 2050
$Comp
L Device:R R?
U 1 1 5F6D0439
P 6600 1200
F 0 "R?" H 6530 1154 50  0000 R CNN
F 1 "1K" H 6530 1245 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6530 1200 50  0001 C CNN
F 3 "~" H 6600 1200 50  0001 C CNN
	1    6600 1200
	-1   0    0    1   
$EndComp
Wire Wire Line
	5900 1350 6600 1350
Wire Wire Line
	6600 1650 6600 1350
Connection ~ 6600 1350
$Comp
L power:VCC #PWR?
U 1 1 5E740587
P 6600 1050
F 0 "#PWR?" H 6600 900 50  0001 C CNN
F 1 "VCC" H 6617 1223 50  0000 C CNN
F 2 "" H 6600 1050 50  0001 C CNN
F 3 "" H 6600 1050 50  0001 C CNN
	1    6600 1050
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D043B
P 6950 1350
F 0 "Q?" H 7140 1396 50  0000 L CNN
F 1 "2N2222" H 7140 1305 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7150 1275 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6950 1350 50  0001 L CNN
	1    6950 1350
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D045B
P 7050 1550
F 0 "#PWR?" H 7050 1300 50  0001 C CNN
F 1 "GND" H 7055 1377 50  0000 C CNN
F 2 "" H 7050 1550 50  0001 C CNN
F 3 "" H 7050 1550 50  0001 C CNN
	1    7050 1550
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E7A14BF
P 6100 1850
F 0 "R?" V 6200 1850 50  0000 C CNN
F 1 "10K" V 6000 1850 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6030 1850 50  0001 C CNN
F 3 "~" H 6100 1850 50  0001 C CNN
	1    6100 1850
	0    1    1    0   
$EndComp
Wire Wire Line
	6250 1850 6300 1850
Wire Wire Line
	6600 1350 6750 1350
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E60119A
P 5800 5750
F 0 "Q?" H 5990 5796 50  0000 L CNN
F 1 "2N2222" H 5990 5705 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6000 5675 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5800 5750 50  0001 L CNN
	1    5800 5750
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D0467
P 6500 6050
F 0 "Q?" H 6690 6096 50  0000 L CNN
F 1 "2N2222" H 6690 6005 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6700 5975 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6500 6050 50  0001 L CNN
	1    6500 6050
	1    0    0    -1  
$EndComp
Wire Wire Line
	5900 5950 5900 6250
Wire Wire Line
	5900 6250 6600 6250
$Comp
L power:GND #PWR?
U 1 1 5F6D0468
P 5900 6250
F 0 "#PWR?" H 5900 6000 50  0001 C CNN
F 1 "GND" H 5905 6077 50  0000 C CNN
F 2 "" H 5900 6250 50  0001 C CNN
F 3 "" H 5900 6250 50  0001 C CNN
	1    5900 6250
	1    0    0    -1  
$EndComp
Connection ~ 5900 6250
$Comp
L Device:R R?
U 1 1 5EB613AD
P 6600 5400
F 0 "R?" H 6530 5354 50  0000 R CNN
F 1 "1K" H 6530 5445 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6530 5400 50  0001 C CNN
F 3 "~" H 6600 5400 50  0001 C CNN
	1    6600 5400
	-1   0    0    1   
$EndComp
Wire Wire Line
	5900 5550 6600 5550
Wire Wire Line
	6600 5850 6600 5550
Connection ~ 6600 5550
$Comp
L power:VCC #PWR?
U 1 1 5F6D0430
P 6600 5250
F 0 "#PWR?" H 6600 5100 50  0001 C CNN
F 1 "VCC" H 6617 5423 50  0000 C CNN
F 2 "" H 6600 5250 50  0001 C CNN
F 3 "" H 6600 5250 50  0001 C CNN
	1    6600 5250
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D0451
P 6950 5550
F 0 "Q?" H 7140 5596 50  0000 L CNN
F 1 "2N2222" H 7140 5505 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7150 5475 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6950 5550 50  0001 L CNN
	1    6950 5550
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E7A14FB
P 7050 5750
F 0 "#PWR?" H 7050 5500 50  0001 C CNN
F 1 "GND" H 7055 5577 50  0000 C CNN
F 2 "" H 7050 5750 50  0001 C CNN
F 3 "" H 7050 5750 50  0001 C CNN
	1    7050 5750
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5F6D0429
P 6100 6050
F 0 "R?" V 6200 6050 50  0000 C CNN
F 1 "10K" V 6000 6050 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6030 6050 50  0001 C CNN
F 3 "~" H 6100 6050 50  0001 C CNN
	1    6100 6050
	0    1    1    0   
$EndComp
Wire Wire Line
	6250 6050 6300 6050
Wire Wire Line
	6600 5550 6750 5550
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D0424
P 5800 4350
F 0 "Q?" H 5990 4396 50  0000 L CNN
F 1 "2N2222" H 5990 4305 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6000 4275 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5800 4350 50  0001 L CNN
	1    5800 4350
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E6011A3
P 6500 4650
F 0 "Q?" H 6690 4696 50  0000 L CNN
F 1 "2N2222" H 6690 4605 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6700 4575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6500 4650 50  0001 L CNN
	1    6500 4650
	1    0    0    -1  
$EndComp
Wire Wire Line
	5900 4550 5900 4850
Wire Wire Line
	5900 4850 6600 4850
$Comp
L power:GND #PWR?
U 1 1 5E740579
P 5900 4850
F 0 "#PWR?" H 5900 4600 50  0001 C CNN
F 1 "GND" H 5905 4677 50  0000 C CNN
F 2 "" H 5900 4850 50  0001 C CNN
F 3 "" H 5900 4850 50  0001 C CNN
	1    5900 4850
	1    0    0    -1  
$EndComp
Connection ~ 5900 4850
$Comp
L Device:R R?
U 1 1 5F6D0469
P 6600 4000
F 0 "R?" H 6530 3954 50  0000 R CNN
F 1 "1K" H 6530 4045 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6530 4000 50  0001 C CNN
F 3 "~" H 6600 4000 50  0001 C CNN
	1    6600 4000
	-1   0    0    1   
$EndComp
Wire Wire Line
	5900 4150 6600 4150
Wire Wire Line
	6600 4450 6600 4150
Connection ~ 6600 4150
$Comp
L power:VCC #PWR?
U 1 1 5E740599
P 6600 3850
F 0 "#PWR?" H 6600 3700 50  0001 C CNN
F 1 "VCC" H 6617 4023 50  0000 C CNN
F 2 "" H 6600 3850 50  0001 C CNN
F 3 "" H 6600 3850 50  0001 C CNN
	1    6600 3850
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F6D0457
P 6950 4150
F 0 "Q?" H 7140 4196 50  0000 L CNN
F 1 "2N2222" H 7140 4105 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7150 4075 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6950 4150 50  0001 L CNN
	1    6950 4150
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D0458
P 7050 4350
F 0 "#PWR?" H 7050 4100 50  0001 C CNN
F 1 "GND" H 7055 4177 50  0000 C CNN
F 2 "" H 7050 4350 50  0001 C CNN
F 3 "" H 7050 4350 50  0001 C CNN
	1    7050 4350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E7A14EC
P 6100 4650
F 0 "R?" V 6200 4650 50  0000 C CNN
F 1 "10K" V 6000 4650 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6030 4650 50  0001 C CNN
F 3 "~" H 6100 4650 50  0001 C CNN
	1    6100 4650
	0    1    1    0   
$EndComp
Wire Wire Line
	6250 4650 6300 4650
Wire Wire Line
	6600 4150 6750 4150
Wire Wire Line
	2800 1250 3300 1250
Wire Wire Line
	3500 2650 3300 2650
Wire Wire Line
	3300 2650 3300 2150
Connection ~ 3300 1250
Wire Wire Line
	3300 1250 3500 1250
Wire Wire Line
	3300 2650 3300 4050
Wire Wire Line
	3300 4050 3500 4050
Connection ~ 3300 2650
Wire Wire Line
	3300 4050 3300 5450
Wire Wire Line
	3300 5450 3500 5450
Connection ~ 3300 4050
Wire Wire Line
	3300 2150 4200 2150
Wire Wire Line
	4200 2150 4200 1850
Wire Wire Line
	4200 1850 5050 1850
Wire Wire Line
	5050 1850 5050 1550
Wire Wire Line
	5050 1550 5450 1550
Connection ~ 3300 2150
Wire Wire Line
	3300 2150 3300 1250
Wire Wire Line
	5600 2950 5450 2950
Wire Wire Line
	5450 2950 5450 1550
Connection ~ 5450 1550
Wire Wire Line
	5450 1550 5600 1550
Wire Wire Line
	5450 2950 5450 4350
Wire Wire Line
	5450 4350 5600 4350
Connection ~ 5450 2950
Wire Wire Line
	5450 4350 5450 5750
Wire Wire Line
	5450 5750 5600 5750
Connection ~ 5450 4350
$Comp
L power:GND #PWR?
U 1 1 5E74057A
P 2100 1700
F 0 "#PWR?" H 2100 1450 50  0001 C CNN
F 1 "GND" H 2105 1527 50  0000 C CNN
F 2 "" H 2100 1700 50  0001 C CNN
F 3 "" H 2100 1700 50  0001 C CNN
	1    2100 1700
	1    0    0    -1  
$EndComp
Wire Wire Line
	2700 1550 2700 2500
Wire Wire Line
	2700 2500 1500 2500
Wire Wire Line
	2700 1550 3850 1550
Wire Wire Line
	1500 2600 2700 2600
Wire Wire Line
	2700 2600 2700 2950
Wire Wire Line
	2700 2950 3850 2950
Wire Wire Line
	2650 4350 2650 2700
Wire Wire Line
	2650 2700 1500 2700
Wire Wire Line
	2650 4350 3850 4350
Wire Wire Line
	1500 2800 2600 2800
Wire Wire Line
	2600 2800 2600 5750
Wire Wire Line
	2600 5750 3850 5750
Wire Wire Line
	5100 1850 5100 1900
Wire Wire Line
	5100 1900 4250 1900
Wire Wire Line
	4250 1900 4250 2200
Wire Wire Line
	2500 2200 2500 2900
Wire Wire Line
	2500 2900 1500 2900
Wire Wire Line
	5100 1850 5950 1850
Wire Wire Line
	2500 2200 4250 2200
Wire Wire Line
	4100 3250 4100 3500
Wire Wire Line
	4100 3500 2500 3500
Wire Wire Line
	2500 3500 2500 3000
Wire Wire Line
	2500 3000 1500 3000
Wire Wire Line
	4100 3250 5950 3250
Wire Wire Line
	4050 4650 4050 5000
Wire Wire Line
	4050 5000 2400 5000
Wire Wire Line
	2400 5000 2400 3100
Wire Wire Line
	2400 3100 1500 3100
Wire Wire Line
	4050 4650 5950 4650
Wire Wire Line
	4150 6050 4150 6300
Wire Wire Line
	4150 6300 2350 6300
Wire Wire Line
	2350 6300 2350 3200
Wire Wire Line
	2350 3200 1500 3200
Wire Wire Line
	4150 6050 5950 6050
Text Notes 5900 5500 0    50   ~ 0
Bit 1
Text Notes 5900 4100 0    50   ~ 0
Bit 2
Text Notes 5900 2700 0    50   ~ 0
Bit 3
Text Notes 5900 1300 0    50   ~ 0
Bit 4
Text Notes 3800 5200 0    50   ~ 0
Bit 5
Text Notes 3800 3800 0    50   ~ 0
Bit 6
Text Notes 3800 2400 0    50   ~ 0
Bit 7
Text Notes 3800 1000 0    50   ~ 0
Bit 8
Wire Wire Line
	7050 1150 7500 1150
Wire Wire Line
	7500 1150 7500 1450
Wire Wire Line
	7500 1450 8500 1450
Wire Wire Line
	7050 2550 7550 2550
Wire Wire Line
	7550 2550 7550 1350
Wire Wire Line
	7550 1350 8500 1350
Wire Wire Line
	7050 3950 7600 3950
Wire Wire Line
	7600 3950 7600 1250
Wire Wire Line
	7600 1250 8500 1250
Wire Wire Line
	7050 5350 7650 5350
Wire Wire Line
	7650 5350 7650 1150
Wire Wire Line
	7650 1150 8500 1150
Wire Wire Line
	4950 850  6250 850 
Wire Wire Line
	6250 850  6250 700 
Wire Wire Line
	8100 700  8100 1850
Wire Wire Line
	8100 1850 8500 1850
Wire Wire Line
	6250 700  8100 700 
Wire Wire Line
	4950 2250 5700 2250
Wire Wire Line
	5700 2250 5700 2400
Wire Wire Line
	5700 2400 6250 2400
Wire Wire Line
	6250 2400 6250 2150
Wire Wire Line
	6250 2150 8050 2150
Wire Wire Line
	8050 2150 8050 1750
Wire Wire Line
	8050 1750 8500 1750
Wire Wire Line
	4950 3650 5750 3650
Wire Wire Line
	5750 3650 5750 3700
Wire Wire Line
	5750 3700 6350 3700
Wire Wire Line
	6350 3700 6350 3550
Wire Wire Line
	6350 3550 7700 3550
Wire Wire Line
	7700 3550 7700 1650
Wire Wire Line
	7700 1650 8500 1650
Wire Wire Line
	4950 5050 5700 5050
Wire Wire Line
	5700 5050 5700 5100
Wire Wire Line
	5700 5100 6350 5100
Wire Wire Line
	6350 5100 6350 4950
Wire Wire Line
	6350 4950 7800 4950
Wire Wire Line
	7800 4950 7800 1550
Wire Wire Line
	7800 1550 8500 1550
$Comp
L power:GND #PWR?
U 1 1 5F6D0443
P 1850 4150
F 0 "#PWR?" H 1850 3900 50  0001 C CNN
F 1 "GND" H 1800 4000 50  0000 C CNN
F 2 "" H 1850 4150 50  0001 C CNN
F 3 "" H 1850 4150 50  0001 C CNN
	1    1850 4150
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D0445
P 1750 4150
F 0 "#PWR?" H 1750 4000 50  0001 C CNN
F 1 "VCC" H 1700 4300 50  0000 C CNN
F 2 "" H 1750 4150 50  0001 C CNN
F 3 "" H 1750 4150 50  0001 C CNN
	1    1750 4150
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x02_Female J?
U 1 1 5F6D041E
P 1850 4350
F 0 "J?" V 1696 4398 50  0000 L CNN
F 1 "Power" V 1787 4398 50  0000 L CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1850 4350 50  0001 C CNN
F 3 "~" H 1850 4350 50  0001 C CNN
	1    1850 4350
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D0426
P 1850 3650
F 0 "#PWR?" H 1850 3400 50  0001 C CNN
F 1 "GND" H 1800 3500 50  0000 C CNN
F 2 "" H 1850 3650 50  0001 C CNN
F 3 "" H 1850 3650 50  0001 C CNN
	1    1850 3650
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E740566
P 1750 3650
F 0 "#PWR?" H 1750 3500 50  0001 C CNN
F 1 "VCC" H 1700 3800 50  0000 C CNN
F 2 "" H 1750 3650 50  0001 C CNN
F 3 "" H 1750 3650 50  0001 C CNN
	1    1750 3650
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x02_Female J?
U 1 1 5F6D041D
P 1850 3850
F 0 "J?" V 1696 3898 50  0000 L CNN
F 1 "Power" V 1787 3898 50  0000 L CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1850 3850 50  0001 C CNN
F 3 "~" H 1850 3850 50  0001 C CNN
	1    1850 3850
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D0449
P 1850 4650
F 0 "#PWR?" H 1850 4400 50  0001 C CNN
F 1 "GND" H 1800 4500 50  0000 C CNN
F 2 "" H 1850 4650 50  0001 C CNN
F 3 "" H 1850 4650 50  0001 C CNN
	1    1850 4650
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D0422
P 1750 4650
F 0 "#PWR?" H 1750 4500 50  0001 C CNN
F 1 "VCC" H 1700 4800 50  0000 C CNN
F 2 "" H 1750 4650 50  0001 C CNN
F 3 "" H 1750 4650 50  0001 C CNN
	1    1750 4650
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x02_Female J?
U 1 1 5F6D042B
P 1850 4850
F 0 "J?" V 1696 4898 50  0000 L CNN
F 1 "Power" V 1787 4898 50  0000 L CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1850 4850 50  0001 C CNN
F 3 "~" H 1850 4850 50  0001 C CNN
	1    1850 4850
	0    1    1    0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F6D0433
P 1800 5450
F 0 "#PWR?" H 1800 5300 50  0001 C CNN
F 1 "VCC" H 1750 5600 50  0000 C CNN
F 2 "" H 1800 5450 50  0001 C CNN
F 3 "" H 1800 5450 50  0001 C CNN
	1    1800 5450
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F6D043C
P 1800 5750
F 0 "#PWR?" H 1800 5500 50  0001 C CNN
F 1 "GND" H 1750 5600 50  0000 C CNN
F 2 "" H 1800 5750 50  0001 C CNN
F 3 "" H 1800 5750 50  0001 C CNN
	1    1800 5750
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 5E74055E
P 1800 5600
F 0 "C?" H 1915 5646 50  0000 L CNN
F 1 "0.1uF" H 1915 5555 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 1838 5450 50  0001 C CNN
F 3 "~" H 1800 5600 50  0001 C CNN
	1    1800 5600
	1    0    0    -1  
$EndComp
Text Notes 1000 6900 0    50   ~ 0
8-bit Bus Output, to be used with a pull-high bus\n\n2.12us rise delay\n2.66us fall delay\n27mA per bit
Text HLabel 1500 1500 0    50   Input ~ 0
EN
Text HLabel 1500 3200 0    50   Input ~ 0
D1
Text HLabel 1500 3100 0    50   Input ~ 0
D2
Text HLabel 1500 3000 0    50   Input ~ 0
D3
Text HLabel 1500 2900 0    50   Input ~ 0
D4
Text HLabel 1500 2800 0    50   Input ~ 0
D5
Text HLabel 1500 2700 0    50   Input ~ 0
D6
Text HLabel 1500 2600 0    50   Input ~ 0
D7
Text HLabel 1500 2500 0    50   Input ~ 0
D8
Text HLabel 8500 1850 2    50   Output ~ 0
Q8
Text HLabel 8500 1750 2    50   Output ~ 0
Q7
Text HLabel 8500 1650 2    50   Output ~ 0
Q6
Text HLabel 8500 1550 2    50   Output ~ 0
Q5
Text HLabel 8500 1450 2    50   Output ~ 0
Q4
Text HLabel 8500 1350 2    50   Output ~ 0
Q3
Text HLabel 8500 1250 2    50   Output ~ 0
Q2
Text HLabel 8500 1150 2    50   Output ~ 0
Q1
$EndSCHEMATC
