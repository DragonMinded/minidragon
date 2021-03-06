EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 5 484
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
L Device:R R?
U 1 1 6158BE84
P 1300 1300
AR Path="/6158BE84" Ref="R?"  Part="1" 
AR Path="/5E2D242B/6158BE84" Ref="R?"  Part="1" 
AR Path="/5E309F18/6158BE84" Ref="R?"  Part="1" 
AR Path="/5E30A748/6158BE84" Ref="R?"  Part="1" 
AR Path="/5E30A74F/6158BE84" Ref="R?"  Part="1" 
AR Path="/5E24FEBE/6158BE84" Ref="R?"  Part="1" 
AR Path="/5E254933/6158BE84" Ref="R33"  Part="1" 
AR Path="/5FA9B399/6148C469/6158BE2F/6158BE84" Ref="R?"  Part="1" 
F 0 "R?" V 1093 1300 50  0000 C CNN
F 1 "10K" V 1184 1300 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1230 1300 50  0001 C CNN
F 3 "~" H 1300 1300 50  0001 C CNN
	1    1300 1300
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 6158BEAF
P 1700 1300
AR Path="/6158BEAF" Ref="Q?"  Part="1" 
AR Path="/5E2D242B/6158BEAF" Ref="Q?"  Part="1" 
AR Path="/5E309F18/6158BEAF" Ref="Q?"  Part="1" 
AR Path="/5E30A748/6158BEAF" Ref="Q?"  Part="1" 
AR Path="/5E30A74F/6158BEAF" Ref="Q?"  Part="1" 
AR Path="/5E24FEBE/6158BEAF" Ref="Q?"  Part="1" 
AR Path="/5E254933/6158BEAF" Ref="Q24"  Part="1" 
AR Path="/5FA9B399/6148C469/6158BE2F/6158BEAF" Ref="Q?"  Part="1" 
F 0 "Q?" H 1890 1346 50  0000 L CNN
F 1 "2N2222" H 1890 1255 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 1900 1225 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 1700 1300 50  0001 L CNN
	1    1700 1300
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E73FEFC
P 1800 2050
AR Path="/5E73FEFC" Ref="R?"  Part="1" 
AR Path="/5E2D242B/5E73FEFC" Ref="R?"  Part="1" 
AR Path="/5E309F18/5E73FEFC" Ref="R?"  Part="1" 
AR Path="/5E30A748/5E73FEFC" Ref="R?"  Part="1" 
AR Path="/5E30A74F/5E73FEFC" Ref="R?"  Part="1" 
AR Path="/5E24FEBE/5E73FEFC" Ref="R?"  Part="1" 
AR Path="/5E254933/5E73FEFC" Ref="R34"  Part="1" 
AR Path="/5FA9B399/6148C469/6158BE2F/5E73FEFC" Ref="R?"  Part="1" 
F 0 "R?" V 1593 2050 50  0000 C CNN
F 1 "1K" V 1684 2050 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1730 2050 50  0001 C CNN
F 3 "~" H 1800 2050 50  0001 C CNN
	1    1800 2050
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E7945A3
P 1800 2300
AR Path="/5E7945A3" Ref="#PWR?"  Part="1" 
AR Path="/5E2D242B/5E7945A3" Ref="#PWR?"  Part="1" 
AR Path="/5E309F18/5E7945A3" Ref="#PWR?"  Part="1" 
AR Path="/5E30A748/5E7945A3" Ref="#PWR?"  Part="1" 
AR Path="/5E30A74F/5E7945A3" Ref="#PWR?"  Part="1" 
AR Path="/5E24FEBE/5E7945A3" Ref="#PWR?"  Part="1" 
AR Path="/5E254933/5E7945A3" Ref="#PWR049"  Part="1" 
F 0 "#PWR?" H 1800 2050 50  0001 C CNN
F 1 "GND" H 1805 2127 50  0000 C CNN
F 2 "" H 1800 2300 50  0001 C CNN
F 3 "" H 1800 2300 50  0001 C CNN
	1    1800 2300
	1    0    0    -1  
$EndComp
Wire Wire Line
	1500 1300 1450 1300
$Comp
L power:VCC #PWR?
U 1 1 5E794591
P 1800 950
AR Path="/5E794591" Ref="#PWR?"  Part="1" 
AR Path="/5E2D242B/5E794591" Ref="#PWR?"  Part="1" 
AR Path="/5E309F18/5E794591" Ref="#PWR?"  Part="1" 
AR Path="/5E30A748/5E794591" Ref="#PWR?"  Part="1" 
AR Path="/5E30A74F/5E794591" Ref="#PWR?"  Part="1" 
AR Path="/5E24FEBE/5E794591" Ref="#PWR?"  Part="1" 
AR Path="/5E254933/5E794591" Ref="#PWR048"  Part="1" 
F 0 "#PWR?" H 1800 800 50  0001 C CNN
F 1 "VCC" H 1817 1123 50  0000 C CNN
F 2 "" H 1800 950 50  0001 C CNN
F 3 "" H 1800 950 50  0001 C CNN
	1    1800 950 
	1    0    0    -1  
$EndComp
Wire Wire Line
	1800 1100 1800 950 
Text HLabel 1050 1300 0    50   Input ~ 0
D
Wire Wire Line
	1150 1300 1050 1300
$Comp
L Device:LED D?
U 1 1 6158BE9B
P 1800 1700
AR Path="/6158BE9B" Ref="D?"  Part="1" 
AR Path="/5E2D242B/6158BE9B" Ref="D?"  Part="1" 
AR Path="/5E309F18/6158BE9B" Ref="D?"  Part="1" 
AR Path="/5E30A748/6158BE9B" Ref="D?"  Part="1" 
AR Path="/5E30A74F/6158BE9B" Ref="D?"  Part="1" 
AR Path="/5E24FEBE/6158BE9B" Ref="D?"  Part="1" 
AR Path="/5E254933/6158BE9B" Ref="D4"  Part="1" 
AR Path="/5FA9B399/6148C469/6158BE2F/6158BE9B" Ref="D?"  Part="1" 
F 0 "D?" V 1850 1800 50  0000 C CNN
F 1 "LED" V 1850 1550 50  0000 C CNN
F 2 "LED_THT:LED_D5.0mm" H 1800 1700 50  0001 C CNN
F 3 "~" H 1800 1700 50  0001 C CNN
	1    1800 1700
	0    -1   -1   0   
$EndComp
Wire Wire Line
	1800 1500 1800 1550
Wire Wire Line
	1800 1900 1800 1850
Wire Wire Line
	1800 2300 1800 2200
$EndSCHEMATC
