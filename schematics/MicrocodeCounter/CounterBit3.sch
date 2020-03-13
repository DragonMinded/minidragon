EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 49 372
Title "D Flip Flop"
Date "2020-02-03"
Rev "2"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 "Also doubles as a T flip-fop if desired"
$EndDescr
$Comp
L Device:R R?
U 1 1 5E5E9341
P 2300 3250
F 0 "R?" V 2400 3250 50  0000 C CNN
F 1 "10K" V 2184 3250 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2230 3250 50  0001 C CNN
F 3 "~" H 2300 3250 50  0001 C CNN
	1    2300 3250
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E5DAAE2
P 2850 3250
F 0 "Q?" H 3040 3296 50  0000 L CNN
F 1 "2N2222" H 3040 3205 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3050 3175 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2850 3250 50  0001 L CNN
	1    2850 3250
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E5E9343
P 2950 2750
F 0 "R?" H 3020 2796 50  0000 L CNN
F 1 "1K" H 3020 2705 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2880 2750 50  0001 C CNN
F 3 "~" H 2950 2750 50  0001 C CNN
	1    2950 2750
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E5E9344
P 2950 2450
F 0 "#PWR?" H 2950 2300 50  0001 C CNN
F 1 "VCC" H 2967 2623 50  0000 C CNN
F 2 "" H 2950 2450 50  0001 C CNN
F 3 "" H 2950 2450 50  0001 C CNN
	1    2950 2450
	1    0    0    -1  
$EndComp
Wire Wire Line
	2950 2600 2950 2450
Wire Wire Line
	2950 3050 2950 2950
$Comp
L Device:R R?
U 1 1 5E610B37
P 3300 2950
F 0 "R?" V 3093 2950 50  0000 C CNN
F 1 "10K" V 3184 2950 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3230 2950 50  0001 C CNN
F 3 "~" H 3300 2950 50  0001 C CNN
	1    3300 2950
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E610B38
P 3850 2950
F 0 "Q?" H 4040 2996 50  0000 L CNN
F 1 "2N2222" H 4040 2905 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4050 2875 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3850 2950 50  0001 L CNN
	1    3850 2950
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E610B39
P 3950 2450
F 0 "R?" H 4020 2496 50  0000 L CNN
F 1 "1K" H 4020 2405 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3880 2450 50  0001 C CNN
F 3 "~" H 3950 2450 50  0001 C CNN
	1    3950 2450
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E610B3A
P 3950 2150
F 0 "#PWR?" H 3950 2000 50  0001 C CNN
F 1 "VCC" H 3967 2323 50  0000 C CNN
F 2 "" H 3950 2150 50  0001 C CNN
F 3 "" H 3950 2150 50  0001 C CNN
	1    3950 2150
	1    0    0    -1  
$EndComp
Wire Wire Line
	3950 2150 3950 2300
Wire Wire Line
	3950 2600 3950 2700
Wire Wire Line
	3150 2950 2950 2950
Connection ~ 2950 2950
Wire Wire Line
	2950 2950 2950 2900
Wire Wire Line
	3450 2950 3650 2950
$Comp
L power:GND #PWR?
U 1 1 5E5E9349
P 3950 3300
F 0 "#PWR?" H 3950 3050 50  0001 C CNN
F 1 "GND" H 3955 3127 50  0000 C CNN
F 2 "" H 3950 3300 50  0001 C CNN
F 3 "" H 3950 3300 50  0001 C CNN
	1    3950 3300
	1    0    0    -1  
$EndComp
Wire Wire Line
	3950 3150 3950 3300
$Comp
L Device:R R?
U 1 1 5E610B0F
P 2500 4000
F 0 "R?" H 2570 4046 50  0000 L CNN
F 1 "10K" H 2570 3955 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2430 4000 50  0001 C CNN
F 3 "~" H 2500 4000 50  0001 C CNN
	1    2500 4000
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E043E3D
P 2100 4350
F 0 "Q?" H 2290 4396 50  0000 L CNN
F 1 "2N2222" H 2290 4305 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2300 4275 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2100 4350 50  0001 L CNN
	1    2100 4350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E610B11
P 1600 4350
F 0 "R?" V 1393 4350 50  0000 C CNN
F 1 "10K" V 1484 4350 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1530 4350 50  0001 C CNN
F 3 "~" H 1600 4350 50  0001 C CNN
	1    1600 4350
	0    1    1    0   
$EndComp
Wire Wire Line
	1750 4350 1900 4350
$Comp
L power:GND #PWR?
U 1 1 5E610B12
P 2200 4700
F 0 "#PWR?" H 2200 4450 50  0001 C CNN
F 1 "GND" H 2205 4527 50  0000 C CNN
F 2 "" H 2200 4700 50  0001 C CNN
F 3 "" H 2200 4700 50  0001 C CNN
	1    2200 4700
	1    0    0    -1  
$EndComp
Wire Wire Line
	2200 4700 2200 4550
$Comp
L power:VCC #PWR?
U 1 1 5E610B3D
P 2200 3700
F 0 "#PWR?" H 2200 3550 50  0001 C CNN
F 1 "VCC" H 2217 3873 50  0000 C CNN
F 2 "" H 2200 3700 50  0001 C CNN
F 3 "" H 2200 3700 50  0001 C CNN
	1    2200 3700
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E5E9351
P 2200 4000
F 0 "R?" H 2270 4046 50  0000 L CNN
F 1 "1K" H 2270 3955 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2130 4000 50  0001 C CNN
F 3 "~" H 2200 4000 50  0001 C CNN
	1    2200 4000
	1    0    0    -1  
$EndComp
Wire Wire Line
	2200 3850 2200 3700
Wire Wire Line
	2500 4150 2200 4150
Connection ~ 2200 4150
Wire Wire Line
	2450 3250 2650 3250
$Comp
L power:GND #PWR?
U 1 1 5E5E9352
P 3500 4000
F 0 "#PWR?" H 3500 3750 50  0001 C CNN
F 1 "GND" H 3505 3827 50  0000 C CNN
F 2 "" H 3500 4000 50  0001 C CNN
F 3 "" H 3500 4000 50  0001 C CNN
	1    3500 4000
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E610B0E
P 2850 3650
F 0 "Q?" H 3040 3696 50  0000 L CNN
F 1 "2N2222" H 3040 3605 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3050 3575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2850 3650 50  0001 L CNN
	1    2850 3650
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E5E9353
P 2850 5150
F 0 "Q?" H 3040 5196 50  0000 L CNN
F 1 "2N2222" H 3040 5105 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3050 5075 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2850 5150 50  0001 L CNN
	1    2850 5150
	1    0    0    -1  
$EndComp
Wire Wire Line
	2950 5350 2950 5550
Wire Wire Line
	2500 5750 2650 5750
Wire Wire Line
	2450 5150 2650 5150
Wire Wire Line
	2950 6100 2950 5950
$Comp
L power:GND #PWR?
U 1 1 5E5E9354
P 2950 6500
F 0 "#PWR?" H 2950 6250 50  0001 C CNN
F 1 "GND" H 2955 6327 50  0000 C CNN
F 2 "" H 2950 6500 50  0001 C CNN
F 3 "" H 2950 6500 50  0001 C CNN
	1    2950 6500
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E610B42
P 2850 5750
F 0 "Q?" H 3040 5796 50  0000 L CNN
F 1 "2N2222" H 3040 5705 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3050 5675 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2850 5750 50  0001 L CNN
	1    2850 5750
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E610B43
P 2350 5750
F 0 "R?" V 2143 5750 50  0000 C CNN
F 1 "10K" V 2234 5750 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2280 5750 50  0001 C CNN
F 3 "~" H 2350 5750 50  0001 C CNN
	1    2350 5750
	0    1    1    0   
$EndComp
$Comp
L Device:R R?
U 1 1 5E610B44
P 2300 5150
F 0 "R?" V 2093 5150 50  0000 C CNN
F 1 "10K" V 2184 5150 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2230 5150 50  0001 C CNN
F 3 "~" H 2300 5150 50  0001 C CNN
	1    2300 5150
	0    1    1    0   
$EndComp
Wire Wire Line
	2050 3250 2050 4150
Wire Wire Line
	2050 4150 1900 4150
Wire Wire Line
	1900 5150 2150 5150
Wire Wire Line
	2050 3250 2150 3250
Wire Wire Line
	1400 5750 2200 5750
Wire Wire Line
	1400 4350 1450 4350
$Comp
L Device:R R?
U 1 1 5E610B45
P 3100 4650
F 0 "R?" V 3000 4650 50  0000 C CNN
F 1 "1K" V 3200 4650 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3030 4650 50  0001 C CNN
F 3 "~" H 3100 4650 50  0001 C CNN
	1    3100 4650
	0    1    1    0   
$EndComp
$Comp
L Device:R R?
U 1 1 5E610B46
P 3400 4850
F 0 "R?" V 3300 4850 50  0000 C CNN
F 1 "10K" V 3500 4850 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3330 4850 50  0001 C CNN
F 3 "~" H 3400 4850 50  0001 C CNN
	1    3400 4850
	0    1    1    0   
$EndComp
Wire Wire Line
	2950 4650 2950 4850
Wire Wire Line
	3250 4850 2950 4850
Connection ~ 2950 4850
Wire Wire Line
	2950 4850 2950 4950
$Comp
L power:VCC #PWR?
U 1 1 5E610B47
P 3250 4500
F 0 "#PWR?" H 3250 4350 50  0001 C CNN
F 1 "VCC" H 3267 4673 50  0000 C CNN
F 2 "" H 3250 4500 50  0001 C CNN
F 3 "" H 3250 4500 50  0001 C CNN
	1    3250 4500
	1    0    0    -1  
$EndComp
Wire Wire Line
	3250 4650 3250 4500
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E5DAAFA
P 3950 4850
F 0 "Q?" H 4140 4896 50  0000 L CNN
F 1 "2N2222" H 4140 4805 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4150 4775 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3950 4850 50  0001 L CNN
	1    3950 4850
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E610B2D
P 4050 4350
F 0 "R?" H 4120 4396 50  0000 L CNN
F 1 "1K" H 4120 4305 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3980 4350 50  0001 C CNN
F 3 "~" H 4050 4350 50  0001 C CNN
	1    4050 4350
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E0553B0
P 4050 4050
F 0 "#PWR?" H 4050 3900 50  0001 C CNN
F 1 "VCC" H 4067 4223 50  0000 C CNN
F 2 "" H 4050 4050 50  0001 C CNN
F 3 "" H 4050 4050 50  0001 C CNN
	1    4050 4050
	1    0    0    -1  
$EndComp
Wire Wire Line
	4050 4050 4050 4200
Wire Wire Line
	4050 4500 4050 4550
Wire Wire Line
	3550 4850 3750 4850
$Comp
L power:GND #PWR?
U 1 1 5E5E935F
P 4050 5200
F 0 "#PWR?" H 4050 4950 50  0001 C CNN
F 1 "GND" H 4055 5027 50  0000 C CNN
F 2 "" H 4050 5200 50  0001 C CNN
F 3 "" H 4050 5200 50  0001 C CNN
	1    4050 5200
	1    0    0    -1  
$EndComp
Wire Wire Line
	4050 5050 4050 5200
$Comp
L Device:R R?
U 1 1 5E5E9362
P 4550 2700
F 0 "R?" V 4343 2700 50  0000 C CNN
F 1 "10K" V 4434 2700 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4480 2700 50  0001 C CNN
F 3 "~" H 4550 2700 50  0001 C CNN
	1    4550 2700
	0    1    1    0   
$EndComp
Wire Wire Line
	4400 2700 3950 2700
Connection ~ 3950 2700
Wire Wire Line
	3950 2700 3950 2750
$Comp
L Device:R R?
U 1 1 5E5E9363
P 4550 4550
F 0 "R?" V 4343 4550 50  0000 C CNN
F 1 "10K" V 4434 4550 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4480 4550 50  0001 C CNN
F 3 "~" H 4550 4550 50  0001 C CNN
	1    4550 4550
	0    1    1    0   
$EndComp
Wire Wire Line
	4400 4550 4050 4550
Connection ~ 4050 4550
Wire Wire Line
	4050 4550 4050 4650
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E610B4B
P 5100 2700
F 0 "Q?" H 5290 2746 50  0000 L CNN
F 1 "2N2222" H 5290 2655 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5300 2625 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5100 2700 50  0001 L CNN
	1    5100 2700
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E05C3F3
P 5950 2700
F 0 "Q?" H 6140 2746 50  0000 L CNN
F 1 "2N2222" H 6140 2655 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6150 2625 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5950 2700 50  0001 L CNN
	1    5950 2700
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E5DAB04
P 6800 2700
F 0 "Q?" H 6990 2746 50  0000 L CNN
F 1 "2N2222" H 6990 2655 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7000 2625 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6800 2700 50  0001 L CNN
	1    6800 2700
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E5DAB05
P 6050 3050
F 0 "#PWR?" H 6050 2800 50  0001 C CNN
F 1 "GND" H 6055 2877 50  0000 C CNN
F 2 "" H 6050 3050 50  0001 C CNN
F 3 "" H 6050 3050 50  0001 C CNN
	1    6050 3050
	1    0    0    -1  
$EndComp
Wire Wire Line
	5200 2900 5200 3050
Wire Wire Line
	5200 3050 6050 3050
Wire Wire Line
	6050 2900 6050 3050
Connection ~ 6050 3050
Wire Wire Line
	6050 3050 6900 3050
Wire Wire Line
	6900 3050 6900 2900
$Comp
L Device:R R?
U 1 1 5E5DAB06
P 6050 2350
F 0 "R?" H 5980 2304 50  0000 R CNN
F 1 "1K" H 5980 2395 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5980 2350 50  0001 C CNN
F 3 "~" H 6050 2350 50  0001 C CNN
	1    6050 2350
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E06276A
P 6050 2100
F 0 "#PWR?" H 6050 1950 50  0001 C CNN
F 1 "VCC" H 6067 2273 50  0000 C CNN
F 2 "" H 6050 2100 50  0001 C CNN
F 3 "" H 6050 2100 50  0001 C CNN
	1    6050 2100
	1    0    0    -1  
$EndComp
Wire Wire Line
	6050 2500 5650 2500
Connection ~ 6050 2500
Wire Wire Line
	6050 2500 6900 2500
Wire Wire Line
	6050 2200 6050 2100
$Comp
L Device:R R?
U 1 1 5E06AA77
P 5450 2050
F 0 "R?" V 5243 2050 50  0000 C CNN
F 1 "10K" V 5334 2050 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5380 2050 50  0001 C CNN
F 3 "~" H 5450 2050 50  0001 C CNN
	1    5450 2050
	0    1    1    0   
$EndComp
Wire Wire Line
	5150 2050 5300 2050
Wire Wire Line
	5600 2050 5750 2050
Wire Wire Line
	5750 2050 5750 2700
Wire Wire Line
	4700 2700 4900 2700
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E610B4C
P 5100 4550
F 0 "Q?" H 5290 4596 50  0000 L CNN
F 1 "2N2222" H 5290 4505 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5300 4475 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5100 4550 50  0001 L CNN
	1    5100 4550
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E5E936C
P 5950 4550
F 0 "Q?" H 6140 4596 50  0000 L CNN
F 1 "2N2222" H 6140 4505 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6150 4475 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5950 4550 50  0001 L CNN
	1    5950 4550
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E610B33
P 6050 4900
F 0 "#PWR?" H 6050 4650 50  0001 C CNN
F 1 "GND" H 6055 4727 50  0000 C CNN
F 2 "" H 6050 4900 50  0001 C CNN
F 3 "" H 6050 4900 50  0001 C CNN
	1    6050 4900
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E610B4E
P 6050 4050
F 0 "R?" H 6120 4096 50  0000 L CNN
F 1 "1K" H 6120 4005 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5980 4050 50  0001 C CNN
F 3 "~" H 6050 4050 50  0001 C CNN
	1    6050 4050
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E610B18
P 6050 3750
F 0 "#PWR?" H 6050 3600 50  0001 C CNN
F 1 "VCC" H 6067 3923 50  0000 C CNN
F 2 "" H 6050 3750 50  0001 C CNN
F 3 "" H 6050 3750 50  0001 C CNN
	1    6050 3750
	1    0    0    -1  
$EndComp
Wire Wire Line
	6050 4350 6050 4200
Wire Wire Line
	6050 3900 6050 3750
Wire Wire Line
	5200 4350 6050 4350
Connection ~ 6050 4350
Wire Wire Line
	5200 4750 6050 4750
Wire Wire Line
	6050 4900 6050 4750
Connection ~ 6050 4750
Wire Wire Line
	4700 4550 4900 4550
$Comp
L Device:R R?
U 1 1 5E077B80
P 5750 3450
F 0 "R?" H 5820 3496 50  0000 L CNN
F 1 "10K" H 5820 3405 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5680 3450 50  0001 C CNN
F 3 "~" H 5750 3450 50  0001 C CNN
	1    5750 3450
	1    0    0    -1  
$EndComp
Wire Wire Line
	5750 2900 5650 2900
Wire Wire Line
	5650 2900 5650 2500
Connection ~ 5650 2500
Wire Wire Line
	5650 2500 5200 2500
Wire Wire Line
	6050 4350 6600 4350
$Comp
L Device:R R?
U 1 1 5E610B1A
P 6600 3450
F 0 "R?" H 6670 3496 50  0000 L CNN
F 1 "10K" H 6670 3405 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6530 3450 50  0001 C CNN
F 3 "~" H 6600 3450 50  0001 C CNN
	1    6600 3450
	1    0    0    -1  
$EndComp
Wire Wire Line
	6600 4350 6600 3600
Wire Wire Line
	6600 3300 6600 2700
Wire Wire Line
	5750 3600 5750 4550
Wire Wire Line
	5750 3300 5750 2900
$Comp
L Device:R R?
U 1 1 5E083831
P 7450 2500
F 0 "R?" V 7243 2500 50  0000 C CNN
F 1 "10K" V 7334 2500 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 7380 2500 50  0001 C CNN
F 3 "~" H 7450 2500 50  0001 C CNN
	1    7450 2500
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E610B1C
P 8000 2500
F 0 "Q?" H 8190 2546 50  0000 L CNN
F 1 "2N2222" H 8190 2455 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 8200 2425 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 8000 2500 50  0001 L CNN
	1    8000 2500
	1    0    0    -1  
$EndComp
$Comp
L Device:LED D?
U 1 1 5E610B1D
P 8250 2900
F 0 "D?" H 8243 2645 50  0000 C CNN
F 1 "LED" H 8243 2736 50  0000 C CNN
F 2 "LED_THT:LED_D5.0mm" H 8250 2900 50  0001 C CNN
F 3 "~" H 8250 2900 50  0001 C CNN
	1    8250 2900
	-1   0    0    1   
$EndComp
$Comp
L Device:R R?
U 1 1 5E5E9375
P 8750 2900
F 0 "R?" V 8543 2900 50  0000 C CNN
F 1 "1K" V 8634 2900 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 8680 2900 50  0001 C CNN
F 3 "~" H 8750 2900 50  0001 C CNN
	1    8750 2900
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E5E9376
P 8900 3050
F 0 "#PWR?" H 8900 2800 50  0001 C CNN
F 1 "GND" H 8905 2877 50  0000 C CNN
F 2 "" H 8900 3050 50  0001 C CNN
F 3 "" H 8900 3050 50  0001 C CNN
	1    8900 3050
	1    0    0    -1  
$EndComp
Wire Wire Line
	8100 2700 8100 2900
Wire Wire Line
	8400 2900 8600 2900
Wire Wire Line
	8900 2900 8900 3050
Wire Wire Line
	7800 2500 7600 2500
Wire Wire Line
	7300 2500 7200 2500
Connection ~ 6900 2500
$Comp
L power:VCC #PWR?
U 1 1 5E610B51
P 8100 2150
F 0 "#PWR?" H 8100 2000 50  0001 C CNN
F 1 "VCC" H 8117 2323 50  0000 C CNN
F 2 "" H 8100 2150 50  0001 C CNN
F 3 "" H 8100 2150 50  0001 C CNN
	1    8100 2150
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E08F0BC
P 7700 3250
F 0 "Q?" H 7890 3296 50  0000 L CNN
F 1 "2N2222" H 7890 3205 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7900 3175 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 7700 3250 50  0001 L CNN
	1    7700 3250
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E5E9379
P 7800 2900
F 0 "#PWR?" H 7800 2750 50  0001 C CNN
F 1 "VCC" H 7817 3073 50  0000 C CNN
F 2 "" H 7800 2900 50  0001 C CNN
F 3 "" H 7800 2900 50  0001 C CNN
	1    7800 2900
	1    0    0    -1  
$EndComp
Wire Wire Line
	7800 2900 7800 3050
$Comp
L Device:R R?
U 1 1 5E5E937A
P 7800 3750
F 0 "R?" H 7730 3704 50  0000 R CNN
F 1 "1K" H 7730 3795 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 7730 3750 50  0001 C CNN
F 3 "~" H 7800 3750 50  0001 C CNN
	1    7800 3750
	-1   0    0    1   
$EndComp
Wire Wire Line
	7800 3600 7800 3550
Wire Wire Line
	7200 2500 7200 2650
Wire Wire Line
	7200 2650 7500 2650
Wire Wire Line
	7500 2650 7500 3250
Connection ~ 7200 2500
Wire Wire Line
	7200 2500 6900 2500
$Comp
L power:GND #PWR?
U 1 1 5E610B54
P 7800 4050
F 0 "#PWR?" H 7800 3800 50  0001 C CNN
F 1 "GND" H 7805 3877 50  0000 C CNN
F 2 "" H 7800 4050 50  0001 C CNN
F 3 "" H 7800 4050 50  0001 C CNN
	1    7800 4050
	1    0    0    -1  
$EndComp
Wire Wire Line
	7800 4050 7800 3900
Wire Wire Line
	7800 3550 8400 3550
Connection ~ 7800 3550
Wire Wire Line
	7800 3550 7800 3450
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E610B55
P 6800 5600
F 0 "J?" V 6954 5412 50  0000 R CNN
F 1 "Power" V 6863 5412 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 6800 5600 50  0001 C CNN
F 3 "~" H 6800 5600 50  0001 C CNN
	1    6800 5600
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E610B56
P 7300 5600
F 0 "J?" V 7454 5412 50  0000 R CNN
F 1 "Power" V 7363 5412 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 7300 5600 50  0001 C CNN
F 3 "~" H 7300 5600 50  0001 C CNN
	1    7300 5600
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E610B57
P 7800 5600
F 0 "J?" V 7954 5412 50  0000 R CNN
F 1 "Power" V 7863 5412 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 7800 5600 50  0001 C CNN
F 3 "~" H 7800 5600 50  0001 C CNN
	1    7800 5600
	0    -1   -1   0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E610B58
P 6800 5250
F 0 "#PWR?" H 6800 5100 50  0001 C CNN
F 1 "VCC" H 6750 5400 50  0000 C CNN
F 2 "" H 6800 5250 50  0001 C CNN
F 3 "" H 6800 5250 50  0001 C CNN
	1    6800 5250
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E0A82EF
P 7300 5250
F 0 "#PWR?" H 7300 5100 50  0001 C CNN
F 1 "VCC" H 7250 5400 50  0000 C CNN
F 2 "" H 7300 5250 50  0001 C CNN
F 3 "" H 7300 5250 50  0001 C CNN
	1    7300 5250
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E0A8832
P 7800 5250
F 0 "#PWR?" H 7800 5100 50  0001 C CNN
F 1 "VCC" H 7750 5400 50  0000 C CNN
F 2 "" H 7800 5250 50  0001 C CNN
F 3 "" H 7800 5250 50  0001 C CNN
	1    7800 5250
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E0A8DF1
P 6900 5250
F 0 "#PWR?" H 6900 5000 50  0001 C CNN
F 1 "GND" H 6850 5100 50  0000 C CNN
F 2 "" H 6900 5250 50  0001 C CNN
F 3 "" H 6900 5250 50  0001 C CNN
	1    6900 5250
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E0A9377
P 7400 5250
F 0 "#PWR?" H 7400 5000 50  0001 C CNN
F 1 "GND" H 7350 5100 50  0000 C CNN
F 2 "" H 7400 5250 50  0001 C CNN
F 3 "" H 7400 5250 50  0001 C CNN
	1    7400 5250
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E610B59
P 7900 5250
F 0 "#PWR?" H 7900 5000 50  0001 C CNN
F 1 "GND" H 7850 5100 50  0000 C CNN
F 2 "" H 7900 5250 50  0001 C CNN
F 3 "" H 7900 5250 50  0001 C CNN
	1    7900 5250
	-1   0    0    1   
$EndComp
Wire Wire Line
	6800 5400 6800 5250
Wire Wire Line
	6900 5250 6900 5400
Wire Wire Line
	7300 5250 7300 5400
Wire Wire Line
	7400 5250 7400 5400
Wire Wire Line
	7800 5250 7800 5400
Wire Wire Line
	7900 5250 7900 5400
$Comp
L Device:C C?
U 1 1 5E5E9385
P 7150 4100
F 0 "C?" V 6898 4100 50  0000 C CNN
F 1 "0.1uF" V 7000 4150 50  0000 C CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 7188 3950 50  0001 C CNN
F 3 "~" H 7150 4100 50  0001 C CNN
	1    7150 4100
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E610B5B
P 7300 4100
F 0 "#PWR?" H 7300 3850 50  0001 C CNN
F 1 "GND" H 7350 3950 50  0000 C CNN
F 2 "" H 7300 4100 50  0001 C CNN
F 3 "" H 7300 4100 50  0001 C CNN
	1    7300 4100
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E610B23
P 7000 4100
F 0 "#PWR?" H 7000 3950 50  0001 C CNN
F 1 "VCC" H 6950 4250 50  0000 C CNN
F 2 "" H 7000 4100 50  0001 C CNN
F 3 "" H 7000 4100 50  0001 C CNN
	1    7000 4100
	1    0    0    -1  
$EndComp
Wire Wire Line
	8100 2300 8100 2150
Connection ~ 6600 4350
Wire Wire Line
	1400 4350 1400 5500
Wire Wire Line
	6600 4350 6600 5500
Connection ~ 1400 5500
Wire Wire Line
	1400 5500 1400 5750
Wire Wire Line
	2500 3850 2500 3650
Wire Wire Line
	2500 3650 2650 3650
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E610B3C
P 3150 4100
F 0 "Q?" V 3478 4100 50  0000 C CNN
F 1 "2N2222" V 3387 4100 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3350 4025 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3150 4100 50  0001 L CNN
	1    3150 4100
	0    -1   -1   0   
$EndComp
Wire Wire Line
	2950 3850 2950 4000
Wire Wire Line
	3350 4000 3500 4000
$Comp
L Device:R R?
U 1 1 5E04CBC6
P 2750 4450
F 0 "R?" H 2820 4496 50  0000 L CNN
F 1 "10K" H 2820 4405 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2680 4450 50  0001 C CNN
F 3 "~" H 2750 4450 50  0001 C CNN
	1    2750 4450
	1    0    0    -1  
$EndComp
Wire Wire Line
	3150 4300 2750 4300
Wire Wire Line
	2750 4600 1800 4600
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E5DAAFE
P 2850 6300
F 0 "Q?" H 3040 6346 50  0000 L CNN
F 1 "2N2222" H 3040 6255 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3050 6225 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2850 6300 50  0001 L CNN
	1    2850 6300
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E5DAAFF
P 2350 6300
F 0 "R?" V 2143 6300 50  0000 C CNN
F 1 "10K" V 2234 6300 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2280 6300 50  0001 C CNN
F 3 "~" H 2350 6300 50  0001 C CNN
	1    2350 6300
	0    1    1    0   
$EndComp
Wire Wire Line
	2500 6300 2650 6300
Wire Wire Line
	2200 6300 1300 6300
Wire Wire Line
	1300 3850 1800 3850
Wire Wire Line
	1800 3850 1800 4600
Text Notes 800  7500 0    50   ~ 0
D/T Flip Flop w/Output Indicator\n\n4.46us rise delay\n2.54us fall delay\n40mA current draw
$Comp
L Device:R R?
U 1 1 5E5E9388
P 1100 1150
F 0 "R?" V 893 1150 50  0000 C CNN
F 1 "1K" V 984 1150 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1030 1150 50  0001 C CNN
F 3 "~" H 1100 1150 50  0001 C CNN
	1    1100 1150
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E5E9389
P 1550 1150
F 0 "Q?" H 1740 1196 50  0000 L CNN
F 1 "2N2222" H 1740 1105 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 1750 1075 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 1550 1150 50  0001 L CNN
	1    1550 1150
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E5E938A
P 1650 800
F 0 "#PWR?" H 1650 650 50  0001 C CNN
F 1 "VCC" H 1667 973 50  0000 C CNN
F 2 "" H 1650 800 50  0001 C CNN
F 3 "" H 1650 800 50  0001 C CNN
	1    1650 800 
	1    0    0    -1  
$EndComp
Wire Wire Line
	1650 950  1650 800 
Wire Wire Line
	1350 1150 1250 1150
Wire Wire Line
	950  1150 850  1150
$Comp
L Device:R R?
U 1 1 5E610B24
P 1650 1600
F 0 "R?" H 1720 1646 50  0000 L CNN
F 1 "100" H 1720 1555 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1580 1600 50  0001 C CNN
F 3 "~" H 1650 1600 50  0001 C CNN
	1    1650 1600
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E5E938C
P 1650 1850
F 0 "#PWR?" H 1650 1600 50  0001 C CNN
F 1 "GND" H 1655 1677 50  0000 C CNN
F 2 "" H 1650 1850 50  0001 C CNN
F 3 "" H 1650 1850 50  0001 C CNN
	1    1650 1850
	1    0    0    -1  
$EndComp
Wire Wire Line
	1650 1850 1650 1750
Wire Wire Line
	1650 1450 1650 1400
$Comp
L Device:C C?
U 1 1 5E5E938D
P 1000 1650
F 0 "C?" H 1115 1696 50  0000 L CNN
F 1 "0.1uF" H 1115 1605 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 1038 1500 50  0001 C CNN
F 3 "~" H 1000 1650 50  0001 C CNN
	1    1000 1650
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E610B25
P 1000 2100
F 0 "R?" H 1070 2146 50  0000 L CNN
F 1 "100" H 1070 2055 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 930 2100 50  0001 C CNN
F 3 "~" H 1000 2100 50  0001 C CNN
	1    1000 2100
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E610B26
P 1000 2400
F 0 "#PWR?" H 1000 2150 50  0001 C CNN
F 1 "GND" H 1005 2227 50  0000 C CNN
F 2 "" H 1000 2400 50  0001 C CNN
F 3 "" H 1000 2400 50  0001 C CNN
	1    1000 2400
	1    0    0    -1  
$EndComp
Wire Wire Line
	1650 1400 1000 1400
Wire Wire Line
	1000 1400 1000 1500
Connection ~ 1650 1400
Wire Wire Line
	1650 1400 1650 1350
Wire Wire Line
	1000 1950 1000 1850
Wire Wire Line
	1000 2400 1000 2350
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E1835E1
P 1550 2800
F 0 "Q?" H 1740 2846 50  0000 L CNN
F 1 "2N2222" H 1740 2755 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 1750 2725 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 1550 2800 50  0001 L CNN
	1    1550 2800
	1    0    0    -1  
$EndComp
Wire Wire Line
	1000 1850 1300 1850
Connection ~ 1000 1850
Wire Wire Line
	1000 1850 1000 1800
$Comp
L power:GND #PWR?
U 1 1 5E610B28
P 1650 3500
F 0 "#PWR?" H 1650 3250 50  0001 C CNN
F 1 "GND" H 1655 3327 50  0000 C CNN
F 2 "" H 1650 3500 50  0001 C CNN
F 3 "" H 1650 3500 50  0001 C CNN
	1    1650 3500
	1    0    0    -1  
$EndComp
Wire Wire Line
	1900 4150 1900 5150
Wire Wire Line
	1300 3850 1300 6300
Wire Wire Line
	2050 3050 2050 3250
Connection ~ 2050 3250
$Comp
L Device:R R?
U 1 1 5E5E9392
P 1650 3250
F 0 "R?" H 1720 3296 50  0000 L CNN
F 1 "1K" H 1720 3205 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1580 3250 50  0001 C CNN
F 3 "~" H 1650 3250 50  0001 C CNN
	1    1650 3250
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E5E9393
P 1650 2500
F 0 "#PWR?" H 1650 2350 50  0001 C CNN
F 1 "VCC" H 1667 2673 50  0000 C CNN
F 2 "" H 1650 2500 50  0001 C CNN
F 3 "" H 1650 2500 50  0001 C CNN
	1    1650 2500
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E610B29
P 7000 4650
F 0 "#PWR?" H 7000 4500 50  0001 C CNN
F 1 "VCC" H 6950 4800 50  0000 C CNN
F 2 "" H 7000 4650 50  0001 C CNN
F 3 "" H 7000 4650 50  0001 C CNN
	1    7000 4650
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 5E5E9395
P 7150 4650
F 0 "C?" V 6898 4650 50  0000 C CNN
F 1 "0.1uF" V 7000 4700 50  0000 C CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 7188 4500 50  0001 C CNN
F 3 "~" H 7150 4650 50  0001 C CNN
	1    7150 4650
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E610B64
P 7300 4650
F 0 "#PWR?" H 7300 4400 50  0001 C CNN
F 1 "GND" H 7350 4500 50  0000 C CNN
F 2 "" H 7300 4650 50  0001 C CNN
F 3 "" H 7300 4650 50  0001 C CNN
	1    7300 4650
	1    0    0    -1  
$EndComp
Wire Wire Line
	1300 2800 1350 2800
Wire Wire Line
	1300 1850 1300 2800
Wire Wire Line
	1650 2600 1650 2500
Wire Wire Line
	1650 3100 1650 3050
Wire Wire Line
	1650 3500 1650 3400
Wire Wire Line
	2050 3050 1650 3050
Connection ~ 1650 3050
Wire Wire Line
	1650 3050 1650 3000
$Comp
L Device:R R?
U 1 1 5E610B2A
P 700 2100
F 0 "R?" H 770 2146 50  0000 L CNN
F 1 "100" H 770 2055 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 630 2100 50  0001 C CNN
F 3 "~" H 700 2100 50  0001 C CNN
	1    700  2100
	1    0    0    -1  
$EndComp
Wire Wire Line
	700  1950 700  1850
Wire Wire Line
	700  1850 1000 1850
Wire Wire Line
	700  2250 700  2350
Wire Wire Line
	700  2350 1000 2350
Connection ~ 1000 2350
Wire Wire Line
	1000 2350 1000 2250
Wire Wire Line
	1400 5500 6600 5500
Text HLabel 850  1150 0    50   Input ~ 0
CLK
Text HLabel 1150 3850 0    50   Input ~ 0
EN
Wire Wire Line
	1150 3850 1300 3850
Connection ~ 1300 3850
Text HLabel 5150 2050 0    50   Input ~ 0
RST
Text HLabel 8400 3550 2    50   Output ~ 0
OUT
$EndSCHEMATC
