EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 13 479
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text HLabel 4450 3950 3    50   Input ~ 0
RST_REQ
Text HLabel 5500 2900 2    50   Output ~ 0
~RST
Text HLabel 5500 2150 2    50   Output ~ 0
CLK_EN
$Comp
L Device:R R17
U 1 1 5E362ED7
P 2350 1300
F 0 "R17" H 2250 1350 50  0000 C CNN
F 1 "1K" H 2250 1250 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2280 1300 50  0001 C CNN
F 3 "~" H 2350 1300 50  0001 C CNN
	1    2350 1300
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR0126
U 1 1 5E362EDD
P 2350 1050
F 0 "#PWR0126" H 2350 900 50  0001 C CNN
F 1 "VCC" H 2367 1223 50  0000 C CNN
F 2 "" H 2350 1050 50  0001 C CNN
F 3 "" H 2350 1050 50  0001 C CNN
	1    2350 1050
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0127
U 1 1 5E362EE5
P 2350 2150
F 0 "#PWR0127" H 2350 1900 50  0001 C CNN
F 1 "GND" H 2355 1977 50  0000 C CNN
F 2 "" H 2350 2150 50  0001 C CNN
F 3 "" H 2350 2150 50  0001 C CNN
	1    2350 2150
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q7
U 1 1 5E362EEB
P 2250 1950
F 0 "Q7" H 2440 1996 50  0000 L CNN
F 1 "2N2222" H 2440 1905 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2450 1875 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2250 1950 50  0001 L CNN
	1    2250 1950
	1    0    0    -1  
$EndComp
Wire Wire Line
	2350 1150 2350 1050
Wire Wire Line
	2350 1450 2350 1600
$Comp
L Device:R R16
U 1 1 5E365638
P 1800 1950
F 0 "R16" V 1900 2000 50  0000 C CNN
F 1 "10K" V 1700 2000 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1730 1950 50  0001 C CNN
F 3 "~" H 1800 1950 50  0001 C CNN
	1    1800 1950
	0    -1   -1   0   
$EndComp
Wire Wire Line
	1950 1950 2050 1950
$Comp
L power:VCC #PWR0128
U 1 1 5E365D4E
P 1000 1750
F 0 "#PWR0128" H 1000 1600 50  0001 C CNN
F 1 "VCC" H 1017 1923 50  0000 C CNN
F 2 "" H 1000 1750 50  0001 C CNN
F 3 "" H 1000 1750 50  0001 C CNN
	1    1000 1750
	1    0    0    -1  
$EndComp
$Comp
L Device:D_Zener D3
U 1 1 5E3662B7
P 1400 1950
F 0 "D3" H 1400 2166 50  0000 C CNN
F 1 "4.7V" H 1400 2075 50  0000 C CNN
F 2 "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal" H 1400 1950 50  0001 C CNN
F 3 "~" H 1400 1950 50  0001 C CNN
	1    1400 1950
	1    0    0    -1  
$EndComp
Wire Wire Line
	1250 1950 1000 1950
Wire Wire Line
	1000 1750 1000 1950
Wire Wire Line
	1550 1950 1650 1950
$Comp
L Device:R R18
U 1 1 5E366C33
P 2750 1600
F 0 "R18" V 2850 1650 50  0000 C CNN
F 1 "10K" V 2650 1650 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2680 1600 50  0001 C CNN
F 3 "~" H 2750 1600 50  0001 C CNN
	1    2750 1600
	0    -1   -1   0   
$EndComp
Wire Wire Line
	2600 1600 2350 1600
Connection ~ 2350 1600
Wire Wire Line
	2350 1600 2350 1750
$Comp
L 2n2222:2N2222 Q8
U 1 1 5E367055
P 3250 1600
F 0 "Q8" H 3440 1646 50  0000 L CNN
F 1 "2N2222" H 3440 1555 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3450 1525 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3250 1600 50  0001 L CNN
	1    3250 1600
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0129
U 1 1 5E367487
P 3350 1900
F 0 "#PWR0129" H 3350 1650 50  0001 C CNN
F 1 "GND" H 3355 1727 50  0000 C CNN
F 2 "" H 3350 1900 50  0001 C CNN
F 3 "" H 3350 1900 50  0001 C CNN
	1    3350 1900
	1    0    0    -1  
$EndComp
Wire Wire Line
	2900 1600 3050 1600
Wire Wire Line
	3350 1800 3350 1900
$Comp
L Device:R R19
U 1 1 5E36793D
P 3350 1150
F 0 "R19" H 3250 1200 50  0000 C CNN
F 1 "1K" H 3250 1100 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3280 1150 50  0001 C CNN
F 3 "~" H 3350 1150 50  0001 C CNN
	1    3350 1150
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR0130
U 1 1 5E367C86
P 3350 900
F 0 "#PWR0130" H 3350 750 50  0001 C CNN
F 1 "VCC" H 3367 1073 50  0000 C CNN
F 2 "" H 3350 900 50  0001 C CNN
F 3 "" H 3350 900 50  0001 C CNN
	1    3350 900 
	1    0    0    -1  
$EndComp
Wire Wire Line
	3350 1400 3350 1350
Wire Wire Line
	3350 1000 3350 900 
$Comp
L Device:C C?
U 1 1 5E369A6F
P 4150 1500
AR Path="/5E369A6F" Ref="C?"  Part="1" 
AR Path="/5E375930/5E369A6F" Ref="C6"  Part="1" 
AR Path="/5E5DE44B/5E375930/5E369A6F" Ref="C6"  Part="1" 
F 0 "C6" H 4000 1500 50  0000 C CNN
F 1 "10uF" H 4050 1400 50  0000 C CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 4188 1350 50  0001 C CNN
F 3 "~" H 4150 1500 50  0001 C CNN
	1    4150 1500
	1    0    0    -1  
$EndComp
Wire Wire Line
	4150 1350 3350 1350
Connection ~ 3350 1350
Wire Wire Line
	3350 1350 3350 1300
$Comp
L Device:R R22
U 1 1 5E369E72
P 4150 1950
F 0 "R22" H 4300 2000 50  0000 C CNN
F 1 "10K" H 4300 1900 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4080 1950 50  0001 C CNN
F 3 "~" H 4150 1950 50  0001 C CNN
	1    4150 1950
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0131
U 1 1 5E36A464
P 4150 2200
F 0 "#PWR0131" H 4150 1950 50  0001 C CNN
F 1 "GND" H 4155 2027 50  0000 C CNN
F 2 "" H 4150 2200 50  0001 C CNN
F 3 "" H 4150 2200 50  0001 C CNN
	1    4150 2200
	1    0    0    -1  
$EndComp
Wire Wire Line
	4150 2200 4150 2100
Wire Wire Line
	4150 1800 4150 1750
$Comp
L 2n2222:2N2222 Q11
U 1 1 5E36AC81
P 5050 1350
F 0 "Q11" H 5240 1396 50  0000 L CNN
F 1 "2N2222" H 5240 1305 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5250 1275 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5050 1350 50  0001 L CNN
	1    5050 1350
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q12
U 1 1 5E36B574
P 5050 1900
F 0 "Q12" H 5240 1946 50  0000 L CNN
F 1 "2N2222" H 5240 1855 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5250 1825 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5050 1900 50  0001 L CNN
	1    5050 1900
	1    0    0    -1  
$EndComp
Wire Wire Line
	5150 1700 5150 1550
$Comp
L Device:R R24
U 1 1 5E36BC5C
P 4500 1350
F 0 "R24" V 4400 1300 50  0000 C CNN
F 1 "10K" V 4600 1300 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4430 1350 50  0001 C CNN
F 3 "~" H 4500 1350 50  0001 C CNN
	1    4500 1350
	0    -1   -1   0   
$EndComp
Wire Wire Line
	4150 1350 4350 1350
Connection ~ 4150 1350
Wire Wire Line
	4650 1350 4850 1350
$Comp
L power:VCC #PWR0132
U 1 1 5E36C822
P 5150 1050
F 0 "#PWR0132" H 5150 900 50  0001 C CNN
F 1 "VCC" H 5167 1223 50  0000 C CNN
F 2 "" H 5150 1050 50  0001 C CNN
F 3 "" H 5150 1050 50  0001 C CNN
	1    5150 1050
	1    0    0    -1  
$EndComp
Wire Wire Line
	5150 1150 5150 1050
$Comp
L power:GND #PWR0133
U 1 1 5E36CD92
P 5150 2600
F 0 "#PWR0133" H 5150 2350 50  0001 C CNN
F 1 "GND" H 5155 2427 50  0000 C CNN
F 2 "" H 5150 2600 50  0001 C CNN
F 3 "" H 5150 2600 50  0001 C CNN
	1    5150 2600
	1    0    0    -1  
$EndComp
$Comp
L Device:R R26
U 1 1 5E36CF4E
P 5150 2350
F 0 "R26" H 5050 2400 50  0000 C CNN
F 1 "1K" H 5050 2300 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5080 2350 50  0001 C CNN
F 3 "~" H 5150 2350 50  0001 C CNN
	1    5150 2350
	-1   0    0    1   
$EndComp
Wire Wire Line
	5150 2600 5150 2500
Wire Wire Line
	5150 2200 5150 2150
Wire Wire Line
	5500 2150 5150 2150
Connection ~ 5150 2150
Wire Wire Line
	5150 2150 5150 2100
$Comp
L Device:R R21
U 1 1 5E36EE5A
P 3900 2700
F 0 "R21" H 3800 2750 50  0000 C CNN
F 1 "1K" H 3800 2650 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3830 2700 50  0001 C CNN
F 3 "~" H 3900 2700 50  0001 C CNN
	1    3900 2700
	-1   0    0    1   
$EndComp
$Comp
L 2n2222:2N2222 Q9
U 1 1 5E36F21A
P 3800 3200
F 0 "Q9" H 3990 3246 50  0000 L CNN
F 1 "2N2222" H 3990 3155 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4000 3125 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3800 3200 50  0001 L CNN
	1    3800 3200
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0134
U 1 1 5E36F32B
P 3900 2400
F 0 "#PWR0134" H 3900 2250 50  0001 C CNN
F 1 "VCC" H 3917 2573 50  0000 C CNN
F 2 "" H 3900 2400 50  0001 C CNN
F 3 "" H 3900 2400 50  0001 C CNN
	1    3900 2400
	1    0    0    -1  
$EndComp
Wire Wire Line
	3900 2400 3900 2550
Wire Wire Line
	3900 3000 3900 2900
$Comp
L Device:R R25
U 1 1 5E36FF5E
P 4600 2550
F 0 "R25" H 4750 2600 50  0000 C CNN
F 1 "10K" H 4750 2500 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4530 2550 50  0001 C CNN
F 3 "~" H 4600 2550 50  0001 C CNN
	1    4600 2550
	1    0    0    -1  
$EndComp
Wire Wire Line
	4850 1900 4600 1900
Wire Wire Line
	4600 1900 4600 2400
Wire Wire Line
	3900 2900 4600 2900
Wire Wire Line
	4600 2900 4600 2700
Connection ~ 3900 2900
Wire Wire Line
	3900 2900 3900 2850
$Comp
L power:GND #PWR0135
U 1 1 5E370DB3
P 3900 3500
F 0 "#PWR0135" H 3900 3250 50  0001 C CNN
F 1 "GND" H 3905 3327 50  0000 C CNN
F 2 "" H 3900 3500 50  0001 C CNN
F 3 "" H 3900 3500 50  0001 C CNN
	1    3900 3500
	1    0    0    -1  
$EndComp
Wire Wire Line
	3900 3500 3900 3400
Wire Wire Line
	4600 2900 4850 2900
Connection ~ 4600 2900
$Comp
L Device:R R20
U 1 1 5E371E83
P 3500 2600
F 0 "R20" H 3650 2650 50  0000 C CNN
F 1 "10K" H 3650 2550 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3430 2600 50  0001 C CNN
F 3 "~" H 3500 2600 50  0001 C CNN
	1    3500 2600
	1    0    0    -1  
$EndComp
Wire Wire Line
	3500 2450 3500 1750
Wire Wire Line
	3500 1750 4150 1750
Connection ~ 4150 1750
Wire Wire Line
	4150 1750 4150 1650
Wire Wire Line
	3500 2750 3500 3200
Wire Wire Line
	3500 3200 3600 3200
$Comp
L 2n2222:2N2222 Q10
U 1 1 5E3730FC
P 4750 3200
F 0 "Q10" H 4940 3246 50  0000 L CNN
F 1 "2N2222" H 4940 3155 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4950 3125 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4750 3200 50  0001 L CNN
	1    4750 3200
	1    0    0    -1  
$EndComp
Wire Wire Line
	4850 3000 4850 2900
Connection ~ 4850 2900
Wire Wire Line
	4850 2900 5500 2900
$Comp
L power:GND #PWR0136
U 1 1 5E37411B
P 4850 3500
F 0 "#PWR0136" H 4850 3250 50  0001 C CNN
F 1 "GND" H 4855 3327 50  0000 C CNN
F 2 "" H 4850 3500 50  0001 C CNN
F 3 "" H 4850 3500 50  0001 C CNN
	1    4850 3500
	1    0    0    -1  
$EndComp
Wire Wire Line
	4850 3500 4850 3400
$Comp
L Device:R R23
U 1 1 5E374BC5
P 4450 3650
F 0 "R23" H 4600 3700 50  0000 C CNN
F 1 "10K" H 4600 3600 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4380 3650 50  0001 C CNN
F 3 "~" H 4450 3650 50  0001 C CNN
	1    4450 3650
	1    0    0    -1  
$EndComp
Wire Wire Line
	4550 3200 4450 3200
Wire Wire Line
	4450 3200 4450 3500
Wire Wire Line
	4450 3950 4450 3800
$EndSCHEMATC
