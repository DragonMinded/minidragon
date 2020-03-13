EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 4 372
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
L 2n2222:2N2222 Q?
U 1 1 5E73FEDA
P 1150 1350
AR Path="/5E73FEDA" Ref="Q?"  Part="1" 
AR Path="/5E2DE646/5E73FEDA" Ref="Q?"  Part="1" 
AR Path="/5E309F1C/5E73FEDA" Ref="Q?"  Part="1" 
AR Path="/5E30A74C/5E73FEDA" Ref="Q?"  Part="1" 
AR Path="/5E30A753/5E73FEDA" Ref="Q?"  Part="1" 
AR Path="/5E24E63C/5E73FEDA" Ref="Q?"  Part="1" 
AR Path="/5E251FF1/5E73FEDA" Ref="Q20"  Part="1" 
AR Path="/5E73CA75/5E693C75/5E73FF84/5E73FEDA" Ref="Q?"  Part="1" 
AR Path="/5E73CA75/5E77319C/5E73FF84/5E73FEDA" Ref="Q?"  Part="1" 
F 0 "Q?" H 1340 1396 50  0000 L CNN
F 1 "2N2222" H 1340 1305 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 1350 1275 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 1150 1350 50  0001 L CNN
	1    1150 1350
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E73FFC1
P 1250 1000
AR Path="/5E73FFC1" Ref="#PWR?"  Part="1" 
AR Path="/5E2DE646/5E73FFC1" Ref="#PWR?"  Part="1" 
AR Path="/5E309F1C/5E73FFC1" Ref="#PWR?"  Part="1" 
AR Path="/5E30A74C/5E73FFC1" Ref="#PWR?"  Part="1" 
AR Path="/5E30A753/5E73FFC1" Ref="#PWR?"  Part="1" 
AR Path="/5E24E63C/5E73FFC1" Ref="#PWR?"  Part="1" 
AR Path="/5E251FF1/5E73FFC1" Ref="#PWR040"  Part="1" 
AR Path="/5E73CA75/5E693C75/5E73FF84/5E73FFC1" Ref="#PWR?"  Part="1" 
AR Path="/5E73CA75/5E77319C/5E73FF84/5E73FFC1" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 1250 850 50  0001 C CNN
F 1 "VCC" H 1267 1173 50  0000 C CNN
F 2 "" H 1250 1000 50  0001 C CNN
F 3 "" H 1250 1000 50  0001 C CNN
	1    1250 1000
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 614C6E6E
P 1250 1850
AR Path="/614C6E6E" Ref="R?"  Part="1" 
AR Path="/5E2DE646/614C6E6E" Ref="R?"  Part="1" 
AR Path="/5E309F1C/614C6E6E" Ref="R?"  Part="1" 
AR Path="/5E30A74C/614C6E6E" Ref="R?"  Part="1" 
AR Path="/5E30A753/614C6E6E" Ref="R?"  Part="1" 
AR Path="/5E24E63C/614C6E6E" Ref="R?"  Part="1" 
AR Path="/5E251FF1/614C6E6E" Ref="R27"  Part="1" 
AR Path="/5E73CA75/5E693C75/5E73FF84/614C6E6E" Ref="R?"  Part="1" 
AR Path="/5E73CA75/5E77319C/5E73FF84/614C6E6E" Ref="R?"  Part="1" 
F 0 "R?" H 1180 1804 50  0000 R CNN
F 1 "1K" H 1180 1895 50  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1180 1850 50  0001 C CNN
F 3 "~" H 1250 1850 50  0001 C CNN
	1    1250 1850
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E77E2E2
P 1250 2150
AR Path="/5E77E2E2" Ref="#PWR?"  Part="1" 
AR Path="/5E2DE646/5E77E2E2" Ref="#PWR?"  Part="1" 
AR Path="/5E309F1C/5E77E2E2" Ref="#PWR?"  Part="1" 
AR Path="/5E30A74C/5E77E2E2" Ref="#PWR?"  Part="1" 
AR Path="/5E30A753/5E77E2E2" Ref="#PWR?"  Part="1" 
AR Path="/5E24E63C/5E77E2E2" Ref="#PWR?"  Part="1" 
AR Path="/5E251FF1/5E77E2E2" Ref="#PWR041"  Part="1" 
AR Path="/5E73CA75/5E693C75/5E73FF84/5E77E2E2" Ref="#PWR?"  Part="1" 
AR Path="/5E73CA75/5E77319C/5E73FF84/5E77E2E2" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 1250 1900 50  0001 C CNN
F 1 "GND" H 1255 1977 50  0000 C CNN
F 2 "" H 1250 2150 50  0001 C CNN
F 3 "" H 1250 2150 50  0001 C CNN
	1    1250 2150
	1    0    0    -1  
$EndComp
Text HLabel 1550 1650 2    50   Output ~ 0
BufOut
Wire Wire Line
	1250 2150 1250 2000
Wire Wire Line
	1250 1700 1250 1650
Wire Wire Line
	1550 1650 1250 1650
Connection ~ 1250 1650
Wire Wire Line
	1250 1650 1250 1550
Wire Wire Line
	1250 1150 1250 1000
Wire Wire Line
	850  1350 950  1350
Text HLabel 850  1350 0    50   Input ~ 0
D
$EndSCHEMATC
