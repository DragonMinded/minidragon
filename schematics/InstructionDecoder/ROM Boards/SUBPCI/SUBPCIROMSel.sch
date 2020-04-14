EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 300 478
Title "Transistor 1-to-2 Selector"
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
U 1 1 60DC9A6C
P 2000 1100
AR Path="/5FA9B399/5FBD285E/60DC9A6C" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A6C" Ref="R?"  Part="1" 
F 0 "R?" H 2070 1146 50  0000 L CNN
F 1 "1K" H 2070 1055 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1930 1100 50  0001 C CNN
F 3 "~" H 2000 1100 50  0001 C CNN
	1    2000 1100
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E1B7EC7
P 2000 950
AR Path="/5FA9B399/5FBD285E/5E1B7EC7" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/5E1B7EC7" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 2000 800 50  0001 C CNN
F 1 "VCC" H 2017 1123 50  0000 C CNN
F 2 "" H 2000 950 50  0001 C CNN
F 3 "" H 2000 950 50  0001 C CNN
	1    2000 950 
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 614C66EF
P 1900 1500
AR Path="/5FA9B399/5FBD285E/614C66EF" Ref="Q?"  Part="1" 
AR Path="/5FA9B399/6148C481/614C66EF" Ref="Q?"  Part="1" 
F 0 "Q?" H 2090 1546 50  0000 L CNN
F 1 "2N2222" H 2090 1455 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2100 1425 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 1900 1500 50  0001 L CNN
	1    1900 1500
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60DC9A6D
P 2000 1700
AR Path="/5FA9B399/5FBD285E/60DC9A6D" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A6D" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 2000 1450 50  0001 C CNN
F 1 "GND" H 2005 1527 50  0000 C CNN
F 2 "" H 2000 1700 50  0001 C CNN
F 3 "" H 2000 1700 50  0001 C CNN
	1    2000 1700
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 60DC9A72
P 1550 1500
AR Path="/5FA9B399/5FBD285E/60DC9A72" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A72" Ref="R?"  Part="1" 
F 0 "R?" V 1343 1500 50  0000 C CNN
F 1 "10K" V 1434 1500 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1480 1500 50  0001 C CNN
F 3 "~" H 1550 1500 50  0001 C CNN
	1    1550 1500
	0    1    1    0   
$EndComp
Wire Wire Line
	1000 1500 1200 1500
Wire Wire Line
	2000 1250 2000 1300
$Comp
L Device:R R?
U 1 1 5F3AF20E
P 2600 1250
AR Path="/5FA9B399/5FBD285E/5F3AF20E" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/5F3AF20E" Ref="R?"  Part="1" 
F 0 "R?" V 2393 1250 50  0000 C CNN
F 1 "10K" V 2484 1250 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2530 1250 50  0001 C CNN
F 3 "~" H 2600 1250 50  0001 C CNN
	1    2600 1250
	0    1    1    0   
$EndComp
$Comp
L Device:R R?
U 1 1 5F3AF214
P 3150 2550
AR Path="/5FA9B399/5FBD285E/5F3AF214" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/5F3AF214" Ref="R?"  Part="1" 
F 0 "R?" V 2943 2550 50  0000 C CNN
F 1 "10K" V 3034 2550 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3080 2550 50  0001 C CNN
F 3 "~" H 3150 2550 50  0001 C CNN
	1    3150 2550
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 60DC9A8C
P 2950 1250
AR Path="/5FA9B399/5FBD285E/60DC9A8C" Ref="Q?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A8C" Ref="Q?"  Part="1" 
F 0 "Q?" H 3140 1296 50  0000 L CNN
F 1 "2N2222" H 3140 1205 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3150 1175 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2950 1250 50  0001 L CNN
	1    2950 1250
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 60DC9A8D
P 3500 2550
AR Path="/5FA9B399/5FBD285E/60DC9A8D" Ref="Q?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A8D" Ref="Q?"  Part="1" 
F 0 "Q?" H 3690 2596 50  0000 L CNN
F 1 "2N2222" H 3690 2505 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3700 2475 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3500 2550 50  0001 L CNN
	1    3500 2550
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 60DC9A6F
P 3500 2950
AR Path="/5FA9B399/5FBD285E/60DC9A6F" Ref="Q?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A6F" Ref="Q?"  Part="1" 
F 0 "Q?" H 3690 2996 50  0000 L CNN
F 1 "2N2222" H 3690 2905 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3700 2875 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3500 2950 50  0001 L CNN
	1    3500 2950
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 6030CF3F
P 3150 2950
AR Path="/5FA9B399/5FBD285E/6030CF3F" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/6030CF3F" Ref="R?"  Part="1" 
F 0 "R?" V 2943 2950 50  0000 C CNN
F 1 "10K" V 3034 2950 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3080 2950 50  0001 C CNN
F 3 "~" H 3150 2950 50  0001 C CNN
	1    3150 2950
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60DC9A84
P 3600 3150
AR Path="/5FA9B399/5FBD285E/60DC9A84" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A84" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 3600 2900 50  0001 C CNN
F 1 "GND" H 3605 2977 50  0000 C CNN
F 2 "" H 3600 3150 50  0001 C CNN
F 3 "" H 3600 3150 50  0001 C CNN
	1    3600 3150
	1    0    0    -1  
$EndComp
Wire Wire Line
	2950 2950 3000 2950
$Comp
L power:GND #PWR?
U 1 1 60DC9A61
P 1100 4000
AR Path="/5FA9B399/5FBD285E/60DC9A61" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A61" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 1100 3750 50  0001 C CNN
F 1 "GND" H 1050 3850 50  0000 C CNN
F 2 "" H 1100 4000 50  0001 C CNN
F 3 "" H 1100 4000 50  0001 C CNN
	1    1100 4000
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 60DC9A74
P 1000 4000
AR Path="/5FA9B399/5FBD285E/60DC9A74" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A74" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 1000 3850 50  0001 C CNN
F 1 "VCC" H 950 4150 50  0000 C CNN
F 2 "" H 1000 4000 50  0001 C CNN
F 3 "" H 1000 4000 50  0001 C CNN
	1    1000 4000
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 6030CF36
P 1000 4200
AR Path="/5FA9B399/5FBD285E/6030CF36" Ref="J?"  Part="1" 
AR Path="/5FA9B399/6148C481/6030CF36" Ref="J?"  Part="1" 
F 0 "J?" V 1154 4012 50  0000 R CNN
F 1 "Power" V 1063 4012 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1000 4200 50  0001 C CNN
F 3 "~" H 1000 4200 50  0001 C CNN
	1    1000 4200
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 6030CF45
P 1500 4200
AR Path="/5FA9B399/5FBD285E/6030CF45" Ref="J?"  Part="1" 
AR Path="/5FA9B399/6148C481/6030CF45" Ref="J?"  Part="1" 
F 0 "J?" V 1654 4012 50  0000 R CNN
F 1 "Power" V 1563 4012 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1500 4200 50  0001 C CNN
F 3 "~" H 1500 4200 50  0001 C CNN
	1    1500 4200
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 60DC9A77
P 2000 4200
AR Path="/5FA9B399/5FBD285E/60DC9A77" Ref="J?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A77" Ref="J?"  Part="1" 
F 0 "J?" V 2154 4012 50  0000 R CNN
F 1 "Power" V 2063 4012 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 2000 4200 50  0001 C CNN
F 3 "~" H 2000 4200 50  0001 C CNN
	1    2000 4200
	0    -1   -1   0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 60DC9A89
P 1500 4000
AR Path="/5FA9B399/5FBD285E/60DC9A89" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A89" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 1500 3850 50  0001 C CNN
F 1 "VCC" H 1450 4150 50  0000 C CNN
F 2 "" H 1500 4000 50  0001 C CNN
F 3 "" H 1500 4000 50  0001 C CNN
	1    1500 4000
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 614C6724
P 1600 4000
AR Path="/5FA9B399/5FBD285E/614C6724" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/614C6724" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 1600 3750 50  0001 C CNN
F 1 "GND" H 1550 3850 50  0000 C CNN
F 2 "" H 1600 4000 50  0001 C CNN
F 3 "" H 1600 4000 50  0001 C CNN
	1    1600 4000
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60DC9A8A
P 2100 4000
AR Path="/5FA9B399/5FBD285E/60DC9A8A" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A8A" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 2100 3750 50  0001 C CNN
F 1 "GND" H 2050 3850 50  0000 C CNN
F 2 "" H 2100 4000 50  0001 C CNN
F 3 "" H 2100 4000 50  0001 C CNN
	1    2100 4000
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 6030CF1C
P 2000 4000
AR Path="/5FA9B399/5FBD285E/6030CF1C" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/6030CF1C" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 2000 3850 50  0001 C CNN
F 1 "VCC" H 1950 4150 50  0000 C CNN
F 2 "" H 2000 4000 50  0001 C CNN
F 3 "" H 2000 4000 50  0001 C CNN
	1    2000 4000
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5F3AF215
P 3000 3500
AR Path="/5FA9B399/5FBD285E/5F3AF215" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/5F3AF215" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 3000 3350 50  0001 C CNN
F 1 "VCC" H 2950 3650 50  0000 C CNN
F 2 "" H 3000 3500 50  0001 C CNN
F 3 "" H 3000 3500 50  0001 C CNN
	1    3000 3500
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 614C66F6
P 3000 4000
AR Path="/5FA9B399/5FBD285E/614C66F6" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/614C66F6" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 3000 3750 50  0001 C CNN
F 1 "GND" H 2950 3850 50  0000 C CNN
F 2 "" H 3000 4000 50  0001 C CNN
F 3 "" H 3000 4000 50  0001 C CNN
	1    3000 4000
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 60DC9A8B
P 3000 3750
AR Path="/5FA9B399/5FBD285E/60DC9A8B" Ref="C?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A8B" Ref="C?"  Part="1" 
F 0 "C?" H 3115 3796 50  0000 L CNN
F 1 "0.1uF" H 3115 3705 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 3038 3600 50  0001 C CNN
F 3 "~" H 3000 3750 50  0001 C CNN
	1    3000 3750
	1    0    0    -1  
$EndComp
Wire Wire Line
	3000 4000 3000 3900
Wire Wire Line
	3000 3600 3000 3500
Wire Notes Line
	700  600  700  4350
Wire Notes Line
	700  4350 7200 4350
Wire Notes Line
	7200 4350 7200 600 
Wire Notes Line
	7200 600  700  600 
Text Notes 3850 4300 0    50   ~ 0
1-to-2 Selector\n\n2.32us rise delay\n2.32us fall delay\n32mA current draw
$Comp
L Device:R R?
U 1 1 60DC9A62
P 4600 1950
AR Path="/5FA9B399/5FBD285E/60DC9A62" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A62" Ref="R?"  Part="1" 
F 0 "R?" H 4670 1996 50  0000 L CNN
F 1 "1K" H 4670 1905 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4530 1950 50  0001 C CNN
F 3 "~" H 4600 1950 50  0001 C CNN
	1    4600 1950
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 60DC9A94
P 4600 1800
AR Path="/5FA9B399/5FBD285E/60DC9A94" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A94" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 4600 1650 50  0001 C CNN
F 1 "VCC" H 4617 1973 50  0000 C CNN
F 2 "" H 4600 1800 50  0001 C CNN
F 3 "" H 4600 1800 50  0001 C CNN
	1    4600 1800
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F3AF1EB
P 4500 2350
AR Path="/5FA9B399/5FBD285E/5F3AF1EB" Ref="Q?"  Part="1" 
AR Path="/5FA9B399/6148C481/5F3AF1EB" Ref="Q?"  Part="1" 
F 0 "Q?" H 4690 2396 50  0000 L CNN
F 1 "2N2222" H 4690 2305 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4700 2275 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4500 2350 50  0001 L CNN
	1    4500 2350
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5F3AF1EC
P 4600 2550
AR Path="/5FA9B399/5FBD285E/5F3AF1EC" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/5F3AF1EC" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 4600 2300 50  0001 C CNN
F 1 "GND" H 4605 2377 50  0000 C CNN
F 2 "" H 4600 2550 50  0001 C CNN
F 3 "" H 4600 2550 50  0001 C CNN
	1    4600 2550
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5F3AF1ED
P 4150 2350
AR Path="/5FA9B399/5FBD285E/5F3AF1ED" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/5F3AF1ED" Ref="R?"  Part="1" 
F 0 "R?" V 3943 2350 50  0000 C CNN
F 1 "10K" V 4034 2350 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4080 2350 50  0001 C CNN
F 3 "~" H 4150 2350 50  0001 C CNN
	1    4150 2350
	0    1    1    0   
$EndComp
Wire Wire Line
	3600 2350 4000 2350
Wire Wire Line
	4600 2100 4600 2150
$Comp
L Device:R R?
U 1 1 60DC9A67
P 3600 2150
AR Path="/5FA9B399/5FBD285E/60DC9A67" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A67" Ref="R?"  Part="1" 
F 0 "R?" H 3670 2196 50  0000 L CNN
F 1 "1K" H 3670 2105 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3530 2150 50  0001 C CNN
F 3 "~" H 3600 2150 50  0001 C CNN
	1    3600 2150
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5EDAD8E2
P 3600 2000
AR Path="/5FA9B399/5FBD285E/5EDAD8E2" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/5EDAD8E2" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 3600 1850 50  0001 C CNN
F 1 "VCC" H 3617 2173 50  0000 C CNN
F 2 "" H 3600 2000 50  0001 C CNN
F 3 "" H 3600 2000 50  0001 C CNN
	1    3600 2000
	1    0    0    -1  
$EndComp
Wire Wire Line
	3600 2300 3600 2350
Connection ~ 3600 2350
Wire Wire Line
	2950 2800 2950 2950
Wire Wire Line
	1200 2550 1200 1500
Connection ~ 1200 1500
Wire Wire Line
	1200 1500 1400 1500
Wire Wire Line
	1200 2550 3000 2550
Wire Wire Line
	2450 1250 2000 1250
Connection ~ 2000 1250
$Comp
L power:GND #PWR?
U 1 1 6030CF27
P 3050 1600
AR Path="/5FA9B399/5FBD285E/6030CF27" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/6030CF27" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 3050 1350 50  0001 C CNN
F 1 "GND" H 3055 1427 50  0000 C CNN
F 2 "" H 3050 1600 50  0001 C CNN
F 3 "" H 3050 1600 50  0001 C CNN
	1    3050 1600
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F3AF1F0
P 2400 2150
AR Path="/5FA9B399/5FBD285E/5F3AF1F0" Ref="Q?"  Part="1" 
AR Path="/5FA9B399/6148C481/5F3AF1F0" Ref="Q?"  Part="1" 
F 0 "Q?" H 2590 2196 50  0000 L CNN
F 1 "2N2222" H 2590 2105 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2600 2075 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2400 2150 50  0001 L CNN
	1    2400 2150
	1    0    0    -1  
$EndComp
Wire Wire Line
	1000 2800 1700 2800
$Comp
L Device:R R?
U 1 1 6030CF2A
P 2000 2150
AR Path="/5FA9B399/5FBD285E/6030CF2A" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/6030CF2A" Ref="R?"  Part="1" 
F 0 "R?" V 1900 2150 50  0000 C CNN
F 1 "10K" V 2100 2150 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1930 2150 50  0001 C CNN
F 3 "~" H 2000 2150 50  0001 C CNN
	1    2000 2150
	0    1    1    0   
$EndComp
Wire Wire Line
	2150 2150 2200 2150
Wire Wire Line
	1850 2150 1700 2150
Wire Wire Line
	1700 2150 1700 2800
Connection ~ 1700 2800
Wire Wire Line
	1700 2800 2950 2800
$Comp
L power:GND #PWR?
U 1 1 60DC9A78
P 2750 2350
AR Path="/5FA9B399/5FBD285E/60DC9A78" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A78" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 2750 2100 50  0001 C CNN
F 1 "GND" H 2750 2200 50  0000 C CNN
F 2 "" H 2750 2350 50  0001 C CNN
F 3 "" H 2750 2350 50  0001 C CNN
	1    2750 2350
	1    0    0    -1  
$EndComp
Wire Wire Line
	2500 2350 2750 2350
Wire Wire Line
	3050 1600 3050 1450
Wire Wire Line
	2500 1950 3400 1950
Wire Wire Line
	3400 1950 3400 1500
Wire Wire Line
	3400 1500 3600 1500
Wire Wire Line
	3600 1500 3600 1050
Wire Wire Line
	3600 1050 3050 1050
$Comp
L Device:R R?
U 1 1 6030CF3D
P 3750 1050
AR Path="/5FA9B399/5FBD285E/6030CF3D" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/6030CF3D" Ref="R?"  Part="1" 
F 0 "R?" V 3650 1000 50  0000 L CNN
F 1 "1K" V 3850 1000 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3680 1050 50  0001 C CNN
F 3 "~" H 3750 1050 50  0001 C CNN
	1    3750 1050
	0    1    1    0   
$EndComp
Connection ~ 3600 1050
$Comp
L power:VCC #PWR?
U 1 1 60DC9A87
P 3900 1050
AR Path="/5FA9B399/5FBD285E/60DC9A87" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A87" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 3900 900 50  0001 C CNN
F 1 "VCC" H 3917 1223 50  0000 C CNN
F 2 "" H 3900 1050 50  0001 C CNN
F 3 "" H 3900 1050 50  0001 C CNN
	1    3900 1050
	1    0    0    -1  
$EndComp
Wire Wire Line
	3600 1500 5000 1500
Connection ~ 3600 1500
$Comp
L 2n2222:2N2222 Q?
U 1 1 6030CF22
P 5500 1500
AR Path="/5FA9B399/5FBD285E/6030CF22" Ref="Q?"  Part="1" 
AR Path="/5FA9B399/6148C481/6030CF22" Ref="Q?"  Part="1" 
F 0 "Q?" H 5690 1546 50  0000 L CNN
F 1 "2N2222" H 5690 1455 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5700 1425 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5500 1500 50  0001 L CNN
	1    5500 1500
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 60DC9A8F
P 5600 1300
AR Path="/5FA9B399/5FBD285E/60DC9A8F" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A8F" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 5600 1150 50  0001 C CNN
F 1 "VCC" H 5617 1473 50  0000 C CNN
F 2 "" H 5600 1300 50  0001 C CNN
F 3 "" H 5600 1300 50  0001 C CNN
	1    5600 1300
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 6030CF16
P 5600 1850
AR Path="/5FA9B399/5FBD285E/6030CF16" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/6030CF16" Ref="R?"  Part="1" 
F 0 "R?" H 5670 1896 50  0000 L CNN
F 1 "1K" H 5670 1805 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5530 1850 50  0001 C CNN
F 3 "~" H 5600 1850 50  0001 C CNN
	1    5600 1850
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E24EC4B
P 5600 2000
AR Path="/5FA9B399/5FBD285E/5E24EC4B" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/5E24EC4B" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 5600 1750 50  0001 C CNN
F 1 "GND" H 5605 1827 50  0000 C CNN
F 2 "" H 5600 2000 50  0001 C CNN
F 3 "" H 5600 2000 50  0001 C CNN
	1    5600 2000
	1    0    0    -1  
$EndComp
Wire Wire Line
	6100 1700 5600 1700
Connection ~ 5600 1700
$Comp
L 2n2222:2N2222 Q?
U 1 1 60DC9A7B
P 5500 2700
AR Path="/5FA9B399/5FBD285E/60DC9A7B" Ref="Q?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A7B" Ref="Q?"  Part="1" 
F 0 "Q?" H 5690 2746 50  0000 L CNN
F 1 "2N2222" H 5690 2655 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5700 2625 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5500 2700 50  0001 L CNN
	1    5500 2700
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E250459
P 5600 2500
AR Path="/5FA9B399/5FBD285E/5E250459" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/5E250459" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 5600 2350 50  0001 C CNN
F 1 "VCC" H 5617 2673 50  0000 C CNN
F 2 "" H 5600 2500 50  0001 C CNN
F 3 "" H 5600 2500 50  0001 C CNN
	1    5600 2500
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 60DC9A69
P 5600 3050
AR Path="/5FA9B399/5FBD285E/60DC9A69" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A69" Ref="R?"  Part="1" 
F 0 "R?" H 5670 3096 50  0000 L CNN
F 1 "1K" H 5670 3005 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5530 3050 50  0001 C CNN
F 3 "~" H 5600 3050 50  0001 C CNN
	1    5600 3050
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60DC9A6A
P 5600 3200
AR Path="/5FA9B399/5FBD285E/60DC9A6A" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A6A" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 5600 2950 50  0001 C CNN
F 1 "GND" H 5605 3027 50  0000 C CNN
F 2 "" H 5600 3200 50  0001 C CNN
F 3 "" H 5600 3200 50  0001 C CNN
	1    5600 3200
	1    0    0    -1  
$EndComp
Wire Wire Line
	6100 2900 5600 2900
Connection ~ 5600 2900
Wire Wire Line
	4600 2100 5300 2100
Wire Wire Line
	5300 2100 5300 2700
Connection ~ 4600 2100
$Comp
L Device:R R?
U 1 1 60DC9A81
P 5600 3650
AR Path="/5FA9B399/5FBD285E/60DC9A81" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A81" Ref="R?"  Part="1" 
F 0 "R?" V 5393 3650 50  0000 C CNN
F 1 "10K" V 5484 3650 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5530 3650 50  0001 C CNN
F 3 "~" H 5600 3650 50  0001 C CNN
	1    5600 3650
	0    -1   -1   0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E2550B6
P 6000 3650
AR Path="/5FA9B399/5FBD285E/5E2550B6" Ref="Q?"  Part="1" 
AR Path="/5FA9B399/6148C481/5E2550B6" Ref="Q?"  Part="1" 
F 0 "Q?" H 6200 3700 50  0000 L CNN
F 1 "2N2222" H 6200 3600 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6200 3575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6000 3650 50  0001 L CNN
	1    6000 3650
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 60DC9A7D
P 6100 3450
AR Path="/5FA9B399/5FBD285E/60DC9A7D" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A7D" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 6100 3300 50  0001 C CNN
F 1 "VCC" H 6117 3623 50  0000 C CNN
F 2 "" H 6100 3450 50  0001 C CNN
F 3 "" H 6100 3450 50  0001 C CNN
	1    6100 3450
	1    0    0    -1  
$EndComp
$Comp
L Device:LED D?
U 1 1 60DC9A6B
P 6250 3950
AR Path="/5FA9B399/5FBD285E/60DC9A6B" Ref="D?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A6B" Ref="D?"  Part="1" 
F 0 "D?" H 6250 3850 50  0000 C CNN
F 1 "LED" H 6250 4050 50  0000 C CNN
F 2 "LED_THT:LED_D5.0mm" H 6250 3950 50  0001 C CNN
F 3 "~" H 6250 3950 50  0001 C CNN
	1    6250 3950
	-1   0    0    1   
$EndComp
$Comp
L Device:R R?
U 1 1 60DC9A90
P 6650 3950
AR Path="/5FA9B399/5FBD285E/60DC9A90" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A90" Ref="R?"  Part="1" 
F 0 "R?" V 6550 3900 50  0000 L CNN
F 1 "1K" V 6750 3900 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6580 3950 50  0001 C CNN
F 3 "~" H 6650 3950 50  0001 C CNN
	1    6650 3950
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60DC9A82
P 6900 3950
AR Path="/5FA9B399/5FBD285E/60DC9A82" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A82" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 6900 3700 50  0001 C CNN
F 1 "GND" H 6905 3777 50  0000 C CNN
F 2 "" H 6900 3950 50  0001 C CNN
F 3 "" H 6900 3950 50  0001 C CNN
	1    6900 3950
	1    0    0    -1  
$EndComp
Wire Wire Line
	6900 3950 6800 3950
Wire Wire Line
	6500 3950 6400 3950
Wire Wire Line
	6100 3950 6100 3850
Wire Wire Line
	5300 2700 5300 3650
Wire Wire Line
	5300 3650 5450 3650
Connection ~ 5300 2700
Wire Wire Line
	5750 3650 5800 3650
$Comp
L 2n2222:2N2222 Q?
U 1 1 60DC9A91
P 6150 1050
AR Path="/5FA9B399/5FBD285E/60DC9A91" Ref="Q?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A91" Ref="Q?"  Part="1" 
F 0 "Q?" H 6350 1100 50  0000 L CNN
F 1 "2N2222" H 6350 1000 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6350 975 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6150 1050 50  0001 L CNN
	1    6150 1050
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 6030CF2E
P 6250 850
AR Path="/5FA9B399/5FBD285E/6030CF2E" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/6030CF2E" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 6250 700 50  0001 C CNN
F 1 "VCC" H 6267 1023 50  0000 C CNN
F 2 "" H 6250 850 50  0001 C CNN
F 3 "" H 6250 850 50  0001 C CNN
	1    6250 850 
	1    0    0    -1  
$EndComp
$Comp
L Device:LED D?
U 1 1 60DC9A7F
P 6400 1350
AR Path="/5FA9B399/5FBD285E/60DC9A7F" Ref="D?"  Part="1" 
AR Path="/5FA9B399/6148C481/60DC9A7F" Ref="D?"  Part="1" 
F 0 "D?" H 6400 1250 50  0000 C CNN
F 1 "LED" H 6400 1450 50  0000 C CNN
F 2 "LED_THT:LED_D5.0mm" H 6400 1350 50  0001 C CNN
F 3 "~" H 6400 1350 50  0001 C CNN
	1    6400 1350
	-1   0    0    1   
$EndComp
$Comp
L Device:R R?
U 1 1 6030CF34
P 6800 1350
AR Path="/5FA9B399/5FBD285E/6030CF34" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/6030CF34" Ref="R?"  Part="1" 
F 0 "R?" V 6700 1300 50  0000 L CNN
F 1 "1K" V 6900 1300 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6730 1350 50  0001 C CNN
F 3 "~" H 6800 1350 50  0001 C CNN
	1    6800 1350
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 6030CF30
P 7050 1350
AR Path="/5FA9B399/5FBD285E/6030CF30" Ref="#PWR?"  Part="1" 
AR Path="/5FA9B399/6148C481/6030CF30" Ref="#PWR?"  Part="1" 
F 0 "#PWR?" H 7050 1100 50  0001 C CNN
F 1 "GND" H 7055 1177 50  0000 C CNN
F 2 "" H 7050 1350 50  0001 C CNN
F 3 "" H 7050 1350 50  0001 C CNN
	1    7050 1350
	1    0    0    -1  
$EndComp
Wire Wire Line
	7050 1350 6950 1350
Wire Wire Line
	6650 1350 6550 1350
Wire Wire Line
	6250 1350 6250 1250
$Comp
L Device:R R?
U 1 1 6030CF1E
P 5150 1050
AR Path="/5FA9B399/5FBD285E/6030CF1E" Ref="R?"  Part="1" 
AR Path="/5FA9B399/6148C481/6030CF1E" Ref="R?"  Part="1" 
F 0 "R?" V 4943 1050 50  0000 C CNN
F 1 "10K" V 5034 1050 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5080 1050 50  0001 C CNN
F 3 "~" H 5150 1050 50  0001 C CNN
	1    5150 1050
	0    -1   -1   0   
$EndComp
Wire Wire Line
	5000 1050 5000 1500
Connection ~ 5000 1500
Wire Wire Line
	5000 1500 5300 1500
Wire Wire Line
	5300 1050 5950 1050
Text HLabel 1000 1500 0    50   Input ~ 0
EN
Text HLabel 1000 2800 0    50   Input ~ 0
SEL
Text HLabel 6100 1700 2    50   Output ~ 0
EN1
Text HLabel 6100 2900 2    50   Output ~ 0
EN2
$EndSCHEMATC
