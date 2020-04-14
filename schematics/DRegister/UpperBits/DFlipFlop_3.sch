EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 5 478
Title "D Flip Flop"
Date "2019-12-24"
Rev "1"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 "Also doubles as a T flip-fop if desired"
$EndDescr
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F531AF1
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
U 1 1 5EB6F34C
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
U 1 1 5F531927
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
U 1 1 5E693B3E
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
U 1 1 5F531AED
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
U 1 1 5E03DD20
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
U 1 1 5FA68D38
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
U 1 1 5F531A12
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
U 1 1 5E5DAAEB
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
U 1 1 5F531B09
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
U 1 1 5E693B5E
P 1500 4350
F 0 "R?" V 1293 4350 50  0000 C CNN
F 1 "10K" V 1384 4350 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1430 4350 50  0001 C CNN
F 3 "~" H 1500 4350 50  0001 C CNN
	1    1500 4350
	0    1    1    0   
$EndComp
Wire Wire Line
	1650 4350 1750 4350
$Comp
L power:GND #PWR?
U 1 1 5F531AD5
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
U 1 1 5FA68D47
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
U 1 1 5F5319DB
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
$Comp
L power:GND #PWR?
U 1 1 5EB6F313
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
U 1 1 5E5E4DCF
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
U 1 1 5F531ADA
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
	2950 6100 2950 5950
$Comp
L power:GND #PWR?
U 1 1 5F531ABB
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
U 1 1 5F531AC3
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
U 1 1 5FA68D13
P 1500 5150
F 0 "R?" V 1600 5150 50  0000 C CNN
F 1 "10K" V 1384 5150 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1430 5150 50  0001 C CNN
F 3 "~" H 1500 5150 50  0001 C CNN
	1    1500 5150
	0    1    1    0   
$EndComp
$Comp
L Device:R R?
U 1 1 5F531AC4
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
U 1 1 5F531B11
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
U 1 1 5F5319B6
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
U 1 1 5FA68D52
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
U 1 1 5FA68B6C
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
U 1 1 5F5319C7
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
U 1 1 5E693BCB
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
U 1 1 5FA68D44
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
U 1 1 5F531ADD
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
U 1 1 5FA68D39
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
U 1 1 5F531931
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
U 1 1 5E693C65
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
U 1 1 5FA68D3A
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
U 1 1 5FA68B7D
P 6050 2250
F 0 "R?" H 5980 2204 50  0000 R CNN
F 1 "1K" H 5980 2295 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5980 2250 50  0001 C CNN
F 3 "~" H 6050 2250 50  0001 C CNN
	1    6050 2250
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F53197C
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
$Comp
L Device:R R?
U 1 1 5F53197D
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
U 1 1 5FA68BDB
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
U 1 1 5FA68BF4
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
U 1 1 5FA68BF5
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
U 1 1 5F531976
P 6050 4100
F 0 "R?" H 6120 4146 50  0000 L CNN
F 1 "1K" H 6120 4055 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5980 4100 50  0001 C CNN
F 3 "~" H 6050 4100 50  0001 C CNN
	1    6050 4100
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F531AF5
P 6050 3950
F 0 "#PWR?" H 6050 3800 50  0001 C CNN
F 1 "VCC" H 6067 4123 50  0000 C CNN
F 2 "" H 6050 3950 50  0001 C CNN
F 3 "" H 6050 3950 50  0001 C CNN
	1    6050 3950
	1    0    0    -1  
$EndComp
Wire Wire Line
	6050 4350 6050 4250
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
Connection ~ 5650 2500
Wire Wire Line
	5650 2500 5200 2500
Wire Wire Line
	6050 4350 6600 4350
$Comp
L Device:R R?
U 1 1 5EB6F3F7
P 6600 3400
F 0 "R?" H 6670 3446 50  0000 L CNN
F 1 "10K" H 6670 3355 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6530 3400 50  0001 C CNN
F 3 "~" H 6600 3400 50  0001 C CNN
	1    6600 3400
	1    0    0    -1  
$EndComp
Wire Wire Line
	6600 4350 6600 3550
Wire Wire Line
	6600 3250 6600 2700
Wire Wire Line
	2500 3850 2500 3650
Wire Wire Line
	2500 3650 2650 3650
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F53195A
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
L 2n2222:2N2222 Q?
U 1 1 5F531AD1
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
U 1 1 5F531AEF
P 1500 6300
F 0 "R?" V 1600 6300 50  0000 C CNN
F 1 "10K" V 1384 6300 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1430 6300 50  0001 C CNN
F 3 "~" H 1500 6300 50  0001 C CNN
	1    1500 6300
	0    1    1    0   
$EndComp
Text Notes 800  7500 0    50   ~ 0
D/T Flip Flop\n\n4.46us rise delay\n2.54us fall delay\n40mA current draw
Text HLabel 1200 6300 0    50   Input ~ 0
EN2
Text HLabel 1200 4350 0    50   Input ~ 0
D
Text HLabel 1200 5150 0    50   Input ~ 0
EN1
Wire Wire Line
	6900 2500 7200 2500
Connection ~ 6900 2500
Text HLabel 7200 2500 2    50   Output ~ 0
Q
Text HLabel 5150 2050 0    50   Input ~ 0
RST
Wire Wire Line
	5650 3550 5650 4550
$Comp
L Device:R R?
U 1 1 5F531B13
P 5650 3400
F 0 "R?" H 5720 3446 50  0000 L CNN
F 1 "10K" H 5720 3355 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5580 3400 50  0001 C CNN
F 3 "~" H 5650 3400 50  0001 C CNN
	1    5650 3400
	1    0    0    -1  
$EndComp
Wire Wire Line
	5650 2500 5650 3250
Wire Wire Line
	5650 4550 5750 4550
Wire Wire Line
	6050 2500 6050 2400
Wire Wire Line
	1900 5150 2650 5150
Wire Wire Line
	1900 5150 1650 5150
Connection ~ 1900 5150
Wire Wire Line
	1350 5150 1200 5150
Wire Wire Line
	1900 3250 2650 3250
Wire Wire Line
	1750 4350 1750 5750
Connection ~ 1750 4350
Wire Wire Line
	1750 4350 1900 4350
Wire Wire Line
	1200 4350 1350 4350
Wire Wire Line
	1750 5750 2650 5750
Wire Wire Line
	1900 3250 1900 5150
Wire Wire Line
	1200 6300 1350 6300
Wire Wire Line
	1650 6300 2600 6300
Wire Wire Line
	2600 6300 2650 6300
Wire Wire Line
	2600 4300 3150 4300
Connection ~ 2600 6300
Wire Wire Line
	2600 4300 2600 6300
$EndSCHEMATC
