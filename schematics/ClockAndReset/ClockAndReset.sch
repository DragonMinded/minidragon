EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 11 478
Title "Clock and Reset Generator"
Date "2020-01-06"
Rev "1"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Connector:Conn_01x02_Male J1
U 1 1 5E13DBD6
P 1350 5700
F 0 "J1" V 1504 5512 50  0000 R CNN
F 1 "Power" V 1413 5512 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1350 5700 50  0001 C CNN
F 3 "~" H 1350 5700 50  0001 C CNN
	1    1350 5700
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J2
U 1 1 5E13E667
P 1800 5700
F 0 "J2" V 1954 5512 50  0000 R CNN
F 1 "Power" V 1863 5512 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1800 5700 50  0001 C CNN
F 3 "~" H 1800 5700 50  0001 C CNN
	1    1800 5700
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J3
U 1 1 5E13EB22
P 2250 5700
F 0 "J3" V 2404 5512 50  0000 R CNN
F 1 "Power" V 2313 5512 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 2250 5700 50  0001 C CNN
F 3 "~" H 2250 5700 50  0001 C CNN
	1    2250 5700
	0    -1   -1   0   
$EndComp
$Comp
L power:VCC #PWR0101
U 1 1 5E13F3C0
P 1350 5500
F 0 "#PWR0101" H 1350 5350 50  0001 C CNN
F 1 "VCC" H 1300 5650 50  0000 C CNN
F 2 "" H 1350 5500 50  0001 C CNN
F 3 "" H 1350 5500 50  0001 C CNN
	1    1350 5500
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0102
U 1 1 5E13F93D
P 1800 5500
F 0 "#PWR0102" H 1800 5350 50  0001 C CNN
F 1 "VCC" H 1750 5650 50  0000 C CNN
F 2 "" H 1800 5500 50  0001 C CNN
F 3 "" H 1800 5500 50  0001 C CNN
	1    1800 5500
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0103
U 1 1 5E13FC20
P 2250 5500
F 0 "#PWR0103" H 2250 5350 50  0001 C CNN
F 1 "VCC" H 2200 5650 50  0000 C CNN
F 2 "" H 2250 5500 50  0001 C CNN
F 3 "" H 2250 5500 50  0001 C CNN
	1    2250 5500
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0104
U 1 1 5E13FE4C
P 1450 5500
F 0 "#PWR0104" H 1450 5250 50  0001 C CNN
F 1 "GND" H 1400 5350 50  0000 C CNN
F 2 "" H 1450 5500 50  0001 C CNN
F 3 "" H 1450 5500 50  0001 C CNN
	1    1450 5500
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR0105
U 1 1 5E14024A
P 1900 5500
F 0 "#PWR0105" H 1900 5250 50  0001 C CNN
F 1 "GND" H 1850 5350 50  0000 C CNN
F 2 "" H 1900 5500 50  0001 C CNN
F 3 "" H 1900 5500 50  0001 C CNN
	1    1900 5500
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR0106
U 1 1 5E14035B
P 2350 5500
F 0 "#PWR0106" H 2350 5250 50  0001 C CNN
F 1 "GND" H 2300 5350 50  0000 C CNN
F 2 "" H 2350 5500 50  0001 C CNN
F 3 "" H 2350 5500 50  0001 C CNN
	1    2350 5500
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR0107
U 1 1 5E140602
P 3350 5700
F 0 "#PWR0107" H 3350 5450 50  0001 C CNN
F 1 "GND" H 3355 5527 50  0000 C CNN
F 2 "" H 3350 5700 50  0001 C CNN
F 3 "" H 3350 5700 50  0001 C CNN
	1    3350 5700
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0108
U 1 1 5E140A9B
P 3350 5200
F 0 "#PWR0108" H 3350 5050 50  0001 C CNN
F 1 "VCC" H 3367 5373 50  0000 C CNN
F 2 "" H 3350 5200 50  0001 C CNN
F 3 "" H 3350 5200 50  0001 C CNN
	1    3350 5200
	1    0    0    -1  
$EndComp
$Comp
L Device:C C4
U 1 1 5E1411B1
P 3350 5450
F 0 "C4" H 3465 5496 50  0000 L CNN
F 1 "0.1uF" H 3465 5405 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 3388 5300 50  0001 C CNN
F 3 "~" H 3350 5450 50  0001 C CNN
	1    3350 5450
	1    0    0    -1  
$EndComp
Wire Wire Line
	3350 5700 3350 5600
Wire Wire Line
	3350 5300 3350 5200
$Comp
L Switch:SW_DIP_x02 SW1
U 1 1 5E154306
P 3150 2700
F 0 "SW1" V 3196 2570 50  0000 R CNN
F 1 "Clock Sel" V 3105 2570 50  0000 R CNN
F 2 "Button_Switch_THT:SW_DIP_SPSTx02_Slide_9.78x7.26mm_W7.62mm_P2.54mm" H 3150 2700 50  0001 C CNN
F 3 "~" H 3150 2700 50  0001 C CNN
	1    3150 2700
	0    -1   -1   0   
$EndComp
Wire Wire Line
	3050 3000 3150 3000
$Comp
L Device:C C3
U 1 1 5E1565B0
P 3350 2200
F 0 "C3" V 3098 2200 50  0000 C CNN
F 1 "0.1uF" V 3189 2200 50  0000 C CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 3388 2050 50  0001 C CNN
F 3 "~" H 3350 2200 50  0001 C CNN
	1    3350 2200
	0    1    1    0   
$EndComp
$Comp
L Switch:SW_SPST SW2
U 1 1 5E156ECE
P 3350 1850
F 0 "SW2" H 3350 2085 50  0000 C CNN
F 1 "Pulse" H 3350 1994 50  0000 C CNN
F 2 "Button_Switch_THT:SW_PUSH_6mm_H5mm" H 3350 1850 50  0001 C CNN
F 3 "~" H 3350 1850 50  0001 C CNN
	1    3350 1850
	1    0    0    -1  
$EndComp
Wire Wire Line
	3150 2400 3150 2200
Wire Wire Line
	3150 2200 3200 2200
Connection ~ 3150 2200
Wire Wire Line
	3150 2200 3150 1850
Wire Wire Line
	3500 2200 3550 2200
Wire Wire Line
	3550 1850 3550 2200
$Comp
L power:VCC #PWR0116
U 1 1 5E15957A
P 3550 1500
F 0 "#PWR0116" H 3550 1350 50  0001 C CNN
F 1 "VCC" H 3567 1673 50  0000 C CNN
F 2 "" H 3550 1500 50  0001 C CNN
F 3 "" H 3550 1500 50  0001 C CNN
	1    3550 1500
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0117
U 1 1 5E159F2D
P 3150 1050
F 0 "#PWR0117" H 3150 800 50  0001 C CNN
F 1 "GND" H 3155 877 50  0000 C CNN
F 2 "" H 3150 1050 50  0001 C CNN
F 3 "" H 3150 1050 50  0001 C CNN
	1    3150 1050
	-1   0    0    1   
$EndComp
$Comp
L Device:R R8
U 1 1 5E15AA2B
P 3150 1350
F 0 "R8" H 3050 1400 50  0000 C CNN
F 1 "1K" H 3050 1300 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3080 1350 50  0001 C CNN
F 3 "~" H 3150 1350 50  0001 C CNN
	1    3150 1350
	-1   0    0    1   
$EndComp
Wire Wire Line
	3150 1500 3150 1850
Connection ~ 3150 1850
Wire Wire Line
	3550 1850 3550 1500
Connection ~ 3550 1850
$Comp
L Device:R R9
U 1 1 5E15E2AC
P 3900 3000
F 0 "R9" V 3693 3000 50  0000 C CNN
F 1 "1K" V 3784 3000 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3830 3000 50  0001 C CNN
F 3 "~" H 3900 3000 50  0001 C CNN
	1    3900 3000
	0    1    1    0   
$EndComp
$Comp
L Device:R R10
U 1 1 5E15EC29
P 4700 2500
F 0 "R10" V 4493 2500 50  0000 C CNN
F 1 "1K" V 4584 2500 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4630 2500 50  0001 C CNN
F 3 "~" H 4700 2500 50  0001 C CNN
	1    4700 2500
	0    1    1    0   
$EndComp
$Comp
L Device:R R11
U 1 1 5E15F08C
P 5700 2500
F 0 "R11" V 5493 2500 50  0000 C CNN
F 1 "1K" V 5584 2500 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5630 2500 50  0001 C CNN
F 3 "~" H 5700 2500 50  0001 C CNN
	1    5700 2500
	0    1    1    0   
$EndComp
$Comp
L power:VCC #PWR0118
U 1 1 5E15F68B
P 5050 2300
F 0 "#PWR0118" H 5050 2150 50  0001 C CNN
F 1 "VCC" H 5067 2473 50  0000 C CNN
F 2 "" H 5050 2300 50  0001 C CNN
F 3 "" H 5050 2300 50  0001 C CNN
	1    5050 2300
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0119
U 1 1 5E15FA64
P 6050 2300
F 0 "#PWR0119" H 6050 2150 50  0001 C CNN
F 1 "VCC" H 6067 2473 50  0000 C CNN
F 2 "" H 6050 2300 50  0001 C CNN
F 3 "" H 6050 2300 50  0001 C CNN
	1    6050 2300
	1    0    0    -1  
$EndComp
Wire Wire Line
	4850 2500 5050 2500
Wire Wire Line
	5050 2500 5050 2300
Wire Wire Line
	5850 2500 6050 2500
Wire Wire Line
	6050 2500 6050 2300
$Comp
L power:GND #PWR0120
U 1 1 5E1618D6
P 4550 3700
F 0 "#PWR0120" H 4550 3450 50  0001 C CNN
F 1 "GND" H 4555 3527 50  0000 C CNN
F 2 "" H 4550 3700 50  0001 C CNN
F 3 "" H 4550 3700 50  0001 C CNN
	1    4550 3700
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0121
U 1 1 5E161C34
P 5550 3200
F 0 "#PWR0121" H 5550 2950 50  0001 C CNN
F 1 "GND" H 5555 3027 50  0000 C CNN
F 2 "" H 5550 3200 50  0001 C CNN
F 3 "" H 5550 3200 50  0001 C CNN
	1    5550 3200
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q3
U 1 1 5E162279
P 4450 3000
F 0 "Q3" H 4640 3046 50  0000 L CNN
F 1 "2N2222" H 4640 2955 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4650 2925 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4450 3000 50  0001 L CNN
	1    4450 3000
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q4
U 1 1 5E162888
P 5450 3000
F 0 "Q4" H 5640 3046 50  0000 L CNN
F 1 "2N2222" H 5640 2955 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5650 2925 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5450 3000 50  0001 L CNN
	1    5450 3000
	1    0    0    -1  
$EndComp
Wire Wire Line
	3150 3000 3750 3000
Connection ~ 3150 3000
Wire Wire Line
	4050 3000 4250 3000
Wire Wire Line
	4550 2800 4550 2700
Wire Wire Line
	4550 2700 5250 2700
Wire Wire Line
	5250 2700 5250 3000
Connection ~ 4550 2700
Wire Wire Line
	4550 2700 4550 2500
Wire Wire Line
	5550 2800 5550 2700
Connection ~ 5550 2700
Wire Wire Line
	5550 2700 5550 2500
Text Notes 1000 6850 0    50   ~ 0
Automatic/Manual Clock Generator
Text Notes 1000 7250 0    50   ~ 0
~~700Hz to ~~5KHz automatic\nSingle-pulse debounced manual\nBuffered output
Wire Wire Line
	3150 1200 3150 1050
$Sheet
S 1500 1300 1100 200 
U 5E35B13C
F0 "Astable Multivibrator" 50
F1 "Astable Multivibrator.sch" 50
F2 "Clk" O R 2600 1400 50 
$EndSheet
Wire Wire Line
	2600 1400 3050 1400
Wire Wire Line
	3050 1400 3050 2400
$Comp
L 2n2222:2N2222 Q1
U 1 1 5E3720B0
P 4450 3450
F 0 "Q1" H 4640 3496 50  0000 L CNN
F 1 "2N2222" H 4640 3405 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4650 3375 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4450 3450 50  0001 L CNN
	1    4450 3450
	1    0    0    -1  
$EndComp
Wire Wire Line
	4550 3200 4550 3250
Wire Wire Line
	4550 3700 4550 3650
$Comp
L Device:R R2
U 1 1 5E374440
P 3900 3450
F 0 "R2" V 3693 3450 50  0000 C CNN
F 1 "10K" V 3784 3450 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3830 3450 50  0001 C CNN
F 3 "~" H 3900 3450 50  0001 C CNN
	1    3900 3450
	0    1    1    0   
$EndComp
Wire Wire Line
	4050 3450 4250 3450
$Sheet
S 1850 3350 1150 350 
U 5E375930
F0 "Reset Pulse Generator" 50
F1 "Reset Pulse Generator.sch" 50
F2 "RST_REQ" I L 1850 3450 50 
F3 "CLK_EN" O R 3000 3450 50 
F4 "~RST" O R 3000 3600 50 
$EndSheet
Wire Wire Line
	3000 3450 3750 3450
$Comp
L Device:C C1
U 1 1 5E3780B2
P 1250 3150
F 0 "C1" V 998 3150 50  0000 C CNN
F 1 "0.1uF" V 1089 3150 50  0000 C CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 1288 3000 50  0001 C CNN
F 3 "~" H 1250 3150 50  0001 C CNN
	1    1250 3150
	0    1    1    0   
$EndComp
$Comp
L Switch:SW_SPST SW3
U 1 1 5E3780BC
P 1250 2800
F 0 "SW3" H 1250 3035 50  0000 C CNN
F 1 "Reset" H 1250 2944 50  0000 C CNN
F 2 "Button_Switch_THT:SW_PUSH_6mm_H5mm" H 1250 2800 50  0001 C CNN
F 3 "~" H 1250 2800 50  0001 C CNN
	1    1250 2800
	1    0    0    -1  
$EndComp
Wire Wire Line
	1050 3150 1100 3150
Connection ~ 1050 3150
Wire Wire Line
	1050 3150 1050 2800
Wire Wire Line
	1400 3150 1450 3150
Wire Wire Line
	1450 2800 1450 3150
$Comp
L power:VCC #PWR0109
U 1 1 5E3780CC
P 1450 2450
F 0 "#PWR0109" H 1450 2300 50  0001 C CNN
F 1 "VCC" H 1467 2623 50  0000 C CNN
F 2 "" H 1450 2450 50  0001 C CNN
F 3 "" H 1450 2450 50  0001 C CNN
	1    1450 2450
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0110
U 1 1 5E3780D6
P 1050 2000
F 0 "#PWR0110" H 1050 1750 50  0001 C CNN
F 1 "GND" H 1055 1827 50  0000 C CNN
F 2 "" H 1050 2000 50  0001 C CNN
F 3 "" H 1050 2000 50  0001 C CNN
	1    1050 2000
	-1   0    0    1   
$EndComp
$Comp
L Device:R R1
U 1 1 5E3780E0
P 1050 2300
F 0 "R1" H 950 2350 50  0000 C CNN
F 1 "1K" H 950 2250 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 980 2300 50  0001 C CNN
F 3 "~" H 1050 2300 50  0001 C CNN
	1    1050 2300
	-1   0    0    1   
$EndComp
Wire Wire Line
	1050 2450 1050 2800
Connection ~ 1050 2800
Wire Wire Line
	1450 2800 1450 2450
Connection ~ 1450 2800
Wire Wire Line
	1050 2150 1050 2000
Wire Wire Line
	1850 3450 1050 3450
Wire Wire Line
	1050 3150 1050 3450
$Comp
L Device:R R4
U 1 1 5E37E2C4
P 5250 4000
F 0 "R4" V 5043 4000 50  0000 C CNN
F 1 "1K" V 5134 4000 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5180 4000 50  0001 C CNN
F 3 "~" H 5250 4000 50  0001 C CNN
	1    5250 4000
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR0111
U 1 1 5E37E2D8
P 5250 3700
F 0 "#PWR0111" H 5250 3550 50  0001 C CNN
F 1 "VCC" H 5267 3873 50  0000 C CNN
F 2 "" H 5250 3700 50  0001 C CNN
F 3 "" H 5250 3700 50  0001 C CNN
	1    5250 3700
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q2
U 1 1 5E37E2F0
P 5150 4500
F 0 "Q2" H 5340 4546 50  0000 L CNN
F 1 "2N2222" H 5340 4455 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5350 4425 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5150 4500 50  0001 L CNN
	1    5150 4500
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0112
U 1 1 5E383B35
P 5250 4800
F 0 "#PWR0112" H 5250 4550 50  0001 C CNN
F 1 "GND" H 5255 4627 50  0000 C CNN
F 2 "" H 5250 4800 50  0001 C CNN
F 3 "" H 5250 4800 50  0001 C CNN
	1    5250 4800
	1    0    0    -1  
$EndComp
Wire Wire Line
	5250 4800 5250 4700
$Comp
L Device:R R3
U 1 1 5E387EE6
P 4250 4050
F 0 "R3" H 4100 4100 50  0000 C CNN
F 1 "10K" H 4100 4000 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4180 4050 50  0001 C CNN
F 3 "~" H 4250 4050 50  0001 C CNN
	1    4250 4050
	-1   0    0    1   
$EndComp
Wire Wire Line
	4250 3600 3000 3600
Wire Wire Line
	4250 3600 4250 3900
Wire Wire Line
	4250 4200 4250 4500
Wire Wire Line
	4250 4500 4950 4500
Wire Wire Line
	5250 3850 5250 3700
Text GLabel 7650 2600 2    50   Output ~ 0
SYS_CLK
Wire Wire Line
	5250 4200 5250 4150
Wire Wire Line
	5250 4300 5250 4200
Connection ~ 5250 4200
Wire Wire Line
	5250 4200 6700 4200
Text GLabel 7650 2900 2    50   Output ~ 0
SYS_RST
$Sheet
S 7000 2500 500  500 
U 5E9E3170
F0 "Clock Mini Buffer" 50
F1 "ClockMiniBuffer.sch" 50
F2 "IN1" I L 7000 2600 50 
F3 "IN2" I L 7000 2900 50 
F4 "OUT1" O R 7500 2600 50 
F5 "OUT2" O R 7500 2900 50 
$EndSheet
Wire Wire Line
	7500 2600 7650 2600
Wire Wire Line
	7650 2900 7500 2900
Wire Wire Line
	6700 2700 6700 2600
Wire Wire Line
	6700 2600 7000 2600
Wire Wire Line
	5550 2700 6700 2700
Wire Wire Line
	7000 2900 6700 2900
Wire Wire Line
	6700 2900 6700 4200
$EndSCHEMATC
