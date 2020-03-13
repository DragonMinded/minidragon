EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 3 372
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L power:GND #PWR?
U 1 1 5E73D962
P 1700 2000
AR Path="/5E73D962" Ref="#PWR?"  Part="1" 
AR Path="/5E2526D5/5E73D962" Ref="#PWR?"  Part="1" 
AR Path="/5E24DFB3/5E73D962" Ref="#PWR016"  Part="1" 
F 0 "#PWR?" H 1700 1750 50  0001 C CNN
F 1 "GND" H 1705 1827 50  0000 C CNN
F 2 "" H 1700 2000 50  0001 C CNN
F 3 "" H 1700 2000 50  0001 C CNN
	1    1700 2000
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E73D9F3
P 1700 1850
AR Path="/5E73D9F3" Ref="R?"  Part="1" 
AR Path="/5E2526D5/5E73D9F3" Ref="R?"  Part="1" 
AR Path="/5E24DFB3/5E73D9F3" Ref="R2"  Part="1" 
AR Path="/5EB55B13/5EB6EB79/5E24DFB3/5E73D9F3" Ref="R?"  Part="1" 
F 0 "R?" H 1770 1896 50  0000 L CNN
F 1 "100" H 1770 1805 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1630 1850 50  0001 C CNN
F 3 "~" H 1700 1850 50  0001 C CNN
	1    1700 1850
	1    0    0    -1  
$EndComp
Wire Wire Line
	1050 1350 950  1350
Wire Wire Line
	1400 1350 1350 1350
Wire Wire Line
	1700 1150 1700 1000
$Comp
L power:VCC #PWR?
U 1 1 5E5F7494
P 1700 1000
AR Path="/5E5F7494" Ref="#PWR?"  Part="1" 
AR Path="/5E2526D5/5E5F7494" Ref="#PWR?"  Part="1" 
AR Path="/5E24DFB3/5E5F7494" Ref="#PWR015"  Part="1" 
F 0 "#PWR?" H 1700 850 50  0001 C CNN
F 1 "VCC" H 1717 1173 50  0000 C CNN
F 2 "" H 1700 1000 50  0001 C CNN
F 3 "" H 1700 1000 50  0001 C CNN
	1    1700 1000
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E73D9A7
P 1600 1350
AR Path="/5E73D9A7" Ref="Q?"  Part="1" 
AR Path="/5E2526D5/5E73D9A7" Ref="Q?"  Part="1" 
AR Path="/5E24DFB3/5E73D9A7" Ref="Q1"  Part="1" 
AR Path="/5EB55B13/5EB6EB79/5E24DFB3/5E73D9A7" Ref="Q?"  Part="1" 
F 0 "Q?" H 1790 1396 50  0000 L CNN
F 1 "2N2222" H 1790 1305 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 1800 1275 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 1600 1350 50  0001 L CNN
	1    1600 1350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E5F7496
P 1200 1350
AR Path="/5E5F7496" Ref="R?"  Part="1" 
AR Path="/5E2526D5/5E5F7496" Ref="R?"  Part="1" 
AR Path="/5E24DFB3/5E5F7496" Ref="R1"  Part="1" 
AR Path="/5EB55B13/5EB6EB79/5E24DFB3/5E5F7496" Ref="R?"  Part="1" 
F 0 "R?" V 993 1350 50  0000 C CNN
F 1 "1K" V 1084 1350 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1130 1350 50  0001 C CNN
F 3 "~" H 1200 1350 50  0001 C CNN
	1    1200 1350
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E693D0F
P 2350 2600
AR Path="/5E693D0F" Ref="#PWR?"  Part="1" 
AR Path="/5E2526D5/5E693D0F" Ref="#PWR?"  Part="1" 
AR Path="/5E24DFB3/5E693D0F" Ref="#PWR017"  Part="1" 
F 0 "#PWR?" H 2350 2350 50  0001 C CNN
F 1 "GND" H 2355 2427 50  0000 C CNN
F 2 "" H 2350 2600 50  0001 C CNN
F 3 "" H 2350 2600 50  0001 C CNN
	1    2350 2600
	1    0    0    -1  
$EndComp
Wire Wire Line
	2350 2150 2350 2050
$Comp
L power:GND #PWR?
U 1 1 5E73D9E5
P 2950 2850
AR Path="/5E73D9E5" Ref="#PWR?"  Part="1" 
AR Path="/5E2526D5/5E73D9E5" Ref="#PWR?"  Part="1" 
AR Path="/5E24DFB3/5E73D9E5" Ref="#PWR019"  Part="1" 
F 0 "#PWR?" H 2950 2600 50  0001 C CNN
F 1 "GND" H 2955 2677 50  0000 C CNN
F 2 "" H 2950 2850 50  0001 C CNN
F 3 "" H 2950 2850 50  0001 C CNN
	1    2950 2850
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E73D9E8
P 2050 2300
AR Path="/5E73D9E8" Ref="R?"  Part="1" 
AR Path="/5E2526D5/5E73D9E8" Ref="R?"  Part="1" 
AR Path="/5E24DFB3/5E73D9E8" Ref="R4"  Part="1" 
AR Path="/5EB55B13/5EB6EB79/5E24DFB3/5E73D9E8" Ref="R?"  Part="1" 
F 0 "R?" H 2120 2346 50  0000 L CNN
F 1 "100" H 2120 2255 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1980 2300 50  0001 C CNN
F 3 "~" H 2050 2300 50  0001 C CNN
	1    2050 2300
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E73DA61
P 2950 1700
AR Path="/5E73DA61" Ref="#PWR?"  Part="1" 
AR Path="/5E2526D5/5E73DA61" Ref="#PWR?"  Part="1" 
AR Path="/5E24DFB3/5E73DA61" Ref="#PWR018"  Part="1" 
F 0 "#PWR?" H 2950 1550 50  0001 C CNN
F 1 "VCC" H 2967 1873 50  0000 C CNN
F 2 "" H 2950 1700 50  0001 C CNN
F 3 "" H 2950 1700 50  0001 C CNN
	1    2950 1700
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E73D9E7
P 2950 2600
AR Path="/5E73D9E7" Ref="R?"  Part="1" 
AR Path="/5E2526D5/5E73D9E7" Ref="R?"  Part="1" 
AR Path="/5E24DFB3/5E73D9E7" Ref="R5"  Part="1" 
F 0 "R?" H 3020 2646 50  0000 L CNN
F 1 "1K" H 3020 2555 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2880 2600 50  0001 C CNN
F 3 "~" H 2950 2600 50  0001 C CNN
	1    2950 2600
	1    0    0    -1  
$EndComp
Connection ~ 2350 2050
Wire Wire Line
	2350 2050 2350 1950
$Comp
L Device:C C?
U 1 1 5E292C20
P 2350 1800
AR Path="/5E292C20" Ref="C?"  Part="1" 
AR Path="/5E2526D5/5E292C20" Ref="C?"  Part="1" 
AR Path="/5E24DFB3/5E292C20" Ref="C5"  Part="1" 
AR Path="/5EB55B13/5EB6EB79/5E24DFB3/5E292C20" Ref="C?"  Part="1" 
F 0 "C?" H 2465 1846 50  0000 L CNN
F 1 "0.1uF" H 2465 1755 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 2388 1650 50  0001 C CNN
F 3 "~" H 2350 1800 50  0001 C CNN
	1    2350 1800
	1    0    0    -1  
$EndComp
Wire Wire Line
	2350 1600 2350 1650
Wire Wire Line
	1700 1600 1700 1550
Wire Wire Line
	1700 1700 1700 1600
Connection ~ 1700 1600
Wire Wire Line
	1700 1600 2350 1600
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E693D0E
P 2850 2050
AR Path="/5E693D0E" Ref="Q?"  Part="1" 
AR Path="/5E2526D5/5E693D0E" Ref="Q?"  Part="1" 
AR Path="/5E24DFB3/5E693D0E" Ref="Q2"  Part="1" 
AR Path="/5EB55B13/5EB6EB79/5E24DFB3/5E693D0E" Ref="Q?"  Part="1" 
F 0 "Q?" H 3040 2096 50  0000 L CNN
F 1 "2N2222" H 3040 2005 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3050 1975 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2850 2050 50  0001 L CNN
	1    2850 2050
	1    0    0    -1  
$EndComp
Wire Wire Line
	2350 2050 2650 2050
Text HLabel 950  1350 0    50   Input ~ 0
ClkIn
Text HLabel 3350 2350 2    50   Output ~ 0
EdgeOut
Wire Wire Line
	2950 2850 2950 2750
Wire Wire Line
	2950 2450 2950 2350
Wire Wire Line
	2950 2350 3350 2350
Connection ~ 2950 2350
Wire Wire Line
	2950 2350 2950 2250
Wire Wire Line
	2950 1850 2950 1700
Wire Wire Line
	2350 2050 2050 2050
Wire Wire Line
	2050 2050 2050 2150
Wire Wire Line
	2050 2450 2050 2500
Wire Wire Line
	2050 2500 2350 2500
Wire Wire Line
	2350 2500 2350 2450
Wire Wire Line
	2350 2500 2350 2600
Connection ~ 2350 2500
$Comp
L Device:R R?
U 1 1 5E73D9E6
P 2350 2300
AR Path="/5E73D9E6" Ref="R?"  Part="1" 
AR Path="/5E2526D5/5E73D9E6" Ref="R?"  Part="1" 
AR Path="/5E24DFB3/5E73D9E6" Ref="R3"  Part="1" 
AR Path="/5EB55B13/5EB6EB79/5E24DFB3/5E73D9E6" Ref="R?"  Part="1" 
F 0 "R?" H 2420 2346 50  0000 L CNN
F 1 "100" H 2420 2255 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2280 2300 50  0001 C CNN
F 3 "~" H 2350 2300 50  0001 C CNN
	1    2350 2300
	1    0    0    -1  
$EndComp
$EndSCHEMATC
