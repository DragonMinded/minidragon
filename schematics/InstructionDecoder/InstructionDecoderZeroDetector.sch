EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 375 479
Title "Zero Detector"
Date "2020-03-21"
Rev "1"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L power:VCC #PWR?
U 1 1 5E7690A7
P 1000 1000
F 0 "#PWR?" H 1000 850 50  0001 C CNN
F 1 "VCC" H 1017 1173 50  0000 C CNN
F 2 "" H 1000 1000 50  0001 C CNN
F 3 "" H 1000 1000 50  0001 C CNN
	1    1000 1000
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E76964D
P 1000 1500
F 0 "#PWR?" H 1000 1250 50  0001 C CNN
F 1 "GND" H 1005 1327 50  0000 C CNN
F 2 "" H 1000 1500 50  0001 C CNN
F 3 "" H 1000 1500 50  0001 C CNN
	1    1000 1500
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 5E7699E3
P 1000 1250
F 0 "C?" H 1115 1296 50  0000 L CNN
F 1 "0.1uF" H 1115 1205 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 1038 1100 50  0001 C CNN
F 3 "~" H 1000 1250 50  0001 C CNN
	1    1000 1250
	1    0    0    -1  
$EndComp
Wire Wire Line
	1000 1100 1000 1000
Wire Wire Line
	1000 1500 1000 1400
$Comp
L power:VCC #PWR?
U 1 1 5E769F4F
P 1500 1000
F 0 "#PWR?" H 1500 850 50  0001 C CNN
F 1 "VCC" H 1450 1150 50  0000 C CNN
F 2 "" H 1500 1000 50  0001 C CNN
F 3 "" H 1500 1000 50  0001 C CNN
	1    1500 1000
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E76A24B
P 1600 1000
F 0 "#PWR?" H 1600 750 50  0001 C CNN
F 1 "GND" H 1550 850 50  0000 C CNN
F 2 "" H 1600 1000 50  0001 C CNN
F 3 "" H 1600 1000 50  0001 C CNN
	1    1600 1000
	-1   0    0    1   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E76AA08
P 1500 1700
F 0 "J?" V 1654 1512 50  0000 R CNN
F 1 "POWER" V 1563 1512 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1500 1700 50  0001 C CNN
F 3 "~" H 1500 1700 50  0001 C CNN
	1    1500 1700
	0    -1   -1   0   
$EndComp
Wire Wire Line
	1500 1500 1500 1000
Wire Wire Line
	1600 1000 1600 1500
$Comp
L power:VCC #PWR?
U 1 1 5E76B5FA
P 2050 1000
F 0 "#PWR?" H 2050 850 50  0001 C CNN
F 1 "VCC" H 2000 1150 50  0000 C CNN
F 2 "" H 2050 1000 50  0001 C CNN
F 3 "" H 2050 1000 50  0001 C CNN
	1    2050 1000
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E76B604
P 2150 1000
F 0 "#PWR?" H 2150 750 50  0001 C CNN
F 1 "GND" H 2100 850 50  0000 C CNN
F 2 "" H 2150 1000 50  0001 C CNN
F 3 "" H 2150 1000 50  0001 C CNN
	1    2150 1000
	-1   0    0    1   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E76B60E
P 2050 1700
F 0 "J?" V 2204 1512 50  0000 R CNN
F 1 "POWER" V 2113 1512 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 2050 1700 50  0001 C CNN
F 3 "~" H 2050 1700 50  0001 C CNN
	1    2050 1700
	0    -1   -1   0   
$EndComp
Wire Wire Line
	2050 1500 2050 1000
Wire Wire Line
	2150 1000 2150 1500
$Comp
L power:VCC #PWR?
U 1 1 5E76E224
P 2600 1000
F 0 "#PWR?" H 2600 850 50  0001 C CNN
F 1 "VCC" H 2550 1150 50  0000 C CNN
F 2 "" H 2600 1000 50  0001 C CNN
F 3 "" H 2600 1000 50  0001 C CNN
	1    2600 1000
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E76E22A
P 2700 1000
F 0 "#PWR?" H 2700 750 50  0001 C CNN
F 1 "GND" H 2650 850 50  0000 C CNN
F 2 "" H 2700 1000 50  0001 C CNN
F 3 "" H 2700 1000 50  0001 C CNN
	1    2700 1000
	-1   0    0    1   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 5E76E230
P 2600 1700
F 0 "J?" V 2754 1512 50  0000 R CNN
F 1 "POWER" V 2663 1512 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 2600 1700 50  0001 C CNN
F 3 "~" H 2600 1700 50  0001 C CNN
	1    2600 1700
	0    -1   -1   0   
$EndComp
Wire Wire Line
	2600 1500 2600 1000
Wire Wire Line
	2700 1000 2700 1500
$Comp
L Device:R R?
U 1 1 5E76F827
P 1950 2500
F 0 "R?" V 1743 2500 50  0000 C CNN
F 1 "10K" V 1834 2500 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1880 2500 50  0001 C CNN
F 3 "~" H 1950 2500 50  0001 C CNN
	1    1950 2500
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E77017F
P 3000 3650
F 0 "Q?" V 3235 3650 50  0000 C CNN
F 1 "2N2222" V 3326 3650 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3200 3575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3000 3650 50  0001 L CNN
	1    3000 3650
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E770C6F
P 2800 4250
F 0 "#PWR?" H 2800 4000 50  0001 C CNN
F 1 "GND" H 2805 4077 50  0000 C CNN
F 2 "" H 2800 4250 50  0001 C CNN
F 3 "" H 2800 4250 50  0001 C CNN
	1    2800 4250
	1    0    0    -1  
$EndComp
Wire Wire Line
	2800 3750 2800 4250
Wire Wire Line
	1150 2500 1800 2500
$Comp
L Device:R R?
U 1 1 5E773F2A
P 1350 5000
F 0 "R?" V 1143 5000 50  0000 C CNN
F 1 "1K" V 1234 5000 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 1280 5000 50  0001 C CNN
F 3 "~" H 1350 5000 50  0001 C CNN
	1    1350 5000
	0    1    1    0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E774EFA
P 1100 4800
F 0 "#PWR?" H 1100 4650 50  0001 C CNN
F 1 "VCC" H 1050 4950 50  0000 C CNN
F 2 "" H 1100 4800 50  0001 C CNN
F 3 "" H 1100 4800 50  0001 C CNN
	1    1100 4800
	1    0    0    -1  
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E77AA8D
P 9000 5000
F 0 "Q?" H 9190 5046 50  0000 L CNN
F 1 "2N2222" H 9190 4955 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 9200 4925 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 9000 5000 50  0001 L CNN
	1    9000 5000
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E77B5E8
P 9100 5650
F 0 "R?" H 9170 5696 50  0000 L CNN
F 1 "1K" H 9170 5605 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 9030 5650 50  0001 C CNN
F 3 "~" H 9100 5650 50  0001 C CNN
	1    9100 5650
	1    0    0    -1  
$EndComp
Wire Wire Line
	9100 5500 9100 5300
$Comp
L power:GND #PWR?
U 1 1 5E77C0A7
P 9100 5800
F 0 "#PWR?" H 9100 5550 50  0001 C CNN
F 1 "GND" H 9105 5627 50  0000 C CNN
F 2 "" H 9100 5800 50  0001 C CNN
F 3 "" H 9100 5800 50  0001 C CNN
	1    9100 5800
	1    0    0    -1  
$EndComp
Wire Wire Line
	9100 5300 9500 5300
Connection ~ 9100 5300
Wire Wire Line
	9100 5300 9100 5200
$Comp
L power:VCC #PWR?
U 1 1 5E77D0C6
P 9100 4800
F 0 "#PWR?" H 9100 4650 50  0001 C CNN
F 1 "VCC" H 9050 4950 50  0000 C CNN
F 2 "" H 9100 4800 50  0001 C CNN
F 3 "" H 9100 4800 50  0001 C CNN
	1    9100 4800
	1    0    0    -1  
$EndComp
Wire Wire Line
	3900 5000 4000 5000
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E77D9AD
P 4700 6000
F 0 "Q?" H 4890 6046 50  0000 L CNN
F 1 "2N2222" H 4890 5955 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4900 5925 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4700 6000 50  0001 L CNN
	1    4700 6000
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E77E488
P 4800 5800
F 0 "#PWR?" H 4800 5650 50  0001 C CNN
F 1 "VCC" H 4750 5950 50  0000 C CNN
F 2 "" H 4800 5800 50  0001 C CNN
F 3 "" H 4800 5800 50  0001 C CNN
	1    4800 5800
	1    0    0    -1  
$EndComp
Wire Wire Line
	4500 6000 3900 6000
Wire Wire Line
	3900 6000 3900 5000
Connection ~ 3900 5000
Wire Wire Line
	3900 5000 3350 5000
Wire Wire Line
	3350 5000 3350 3750
Wire Wire Line
	3200 3750 3350 3750
$Comp
L Device:R R?
U 1 1 5E780DD7
P 4800 6900
F 0 "R?" H 4870 6946 50  0000 L CNN
F 1 "1K" H 4870 6855 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4730 6900 50  0001 C CNN
F 3 "~" H 4800 6900 50  0001 C CNN
	1    4800 6900
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E781560
P 4800 7150
F 0 "#PWR?" H 4800 6900 50  0001 C CNN
F 1 "GND" H 4805 6977 50  0000 C CNN
F 2 "" H 4800 7150 50  0001 C CNN
F 3 "" H 4800 7150 50  0001 C CNN
	1    4800 7150
	1    0    0    -1  
$EndComp
Wire Wire Line
	4800 7150 4800 7050
$Comp
L Device:LED D?
U 1 1 5E781DD4
P 4800 6450
F 0 "D?" V 4839 6333 50  0000 R CNN
F 1 "LED" V 4748 6333 50  0000 R CNN
F 2 "LED_THT:LED_D5.0mm" H 4800 6450 50  0001 C CNN
F 3 "~" H 4800 6450 50  0001 C CNN
	1    4800 6450
	0    -1   -1   0   
$EndComp
Wire Wire Line
	4800 6750 4800 6600
Wire Wire Line
	4800 6300 4800 6200
Wire Wire Line
	1100 4800 1100 5000
Wire Wire Line
	1100 5000 1200 5000
Wire Wire Line
	1500 5000 2650 5000
Connection ~ 3350 5000
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E7865BA
P 10050 3300
F 0 "Q?" H 10240 3346 50  0000 L CNN
F 1 "2N2222" H 10240 3255 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 10250 3225 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 10050 3300 50  0001 L CNN
	1    10050 3300
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E7865C4
P 10150 3950
F 0 "R?" H 10220 3996 50  0000 L CNN
F 1 "1K" H 10220 3905 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 10080 3950 50  0001 C CNN
F 3 "~" H 10150 3950 50  0001 C CNN
	1    10150 3950
	1    0    0    -1  
$EndComp
Wire Wire Line
	10150 3800 10150 3600
$Comp
L power:GND #PWR?
U 1 1 5E7865CF
P 10150 4100
F 0 "#PWR?" H 10150 3850 50  0001 C CNN
F 1 "GND" H 10155 3927 50  0000 C CNN
F 2 "" H 10150 4100 50  0001 C CNN
F 3 "" H 10150 4100 50  0001 C CNN
	1    10150 4100
	1    0    0    -1  
$EndComp
Wire Wire Line
	10150 3600 10550 3600
Connection ~ 10150 3600
Wire Wire Line
	10150 3600 10150 3500
$Comp
L power:VCC #PWR?
U 1 1 5E7865E0
P 10150 3100
F 0 "#PWR?" H 10150 2950 50  0001 C CNN
F 1 "VCC" H 10100 3250 50  0000 C CNN
F 2 "" H 10150 3100 50  0001 C CNN
F 3 "" H 10150 3100 50  0001 C CNN
	1    10150 3100
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E791B58
P 8550 5000
F 0 "R?" V 8343 5000 50  0000 C CNN
F 1 "10K" V 8434 5000 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 8480 5000 50  0001 C CNN
F 3 "~" H 8550 5000 50  0001 C CNN
	1    8550 5000
	0    1    1    0   
$EndComp
Wire Wire Line
	8700 5000 8800 5000
$Comp
L Device:R R?
U 1 1 5E792416
P 9600 3300
F 0 "R?" V 9393 3300 50  0000 C CNN
F 1 "10K" V 9484 3300 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 9530 3300 50  0001 C CNN
F 3 "~" H 9600 3300 50  0001 C CNN
	1    9600 3300
	0    1    1    0   
$EndComp
Wire Wire Line
	9750 3300 9850 3300
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E793112
P 8750 3700
F 0 "Q?" H 8940 3746 50  0000 L CNN
F 1 "2N2222" H 8940 3655 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 8950 3625 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 8750 3700 50  0001 L CNN
	1    8750 3700
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E793803
P 8850 3000
F 0 "R?" H 8920 3046 50  0000 L CNN
F 1 "1K" H 8920 2955 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 8780 3000 50  0001 C CNN
F 3 "~" H 8850 3000 50  0001 C CNN
	1    8850 3000
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 5E793A81
P 8850 2700
F 0 "#PWR?" H 8850 2550 50  0001 C CNN
F 1 "VCC" H 8800 2850 50  0000 C CNN
F 2 "" H 8850 2700 50  0001 C CNN
F 3 "" H 8850 2700 50  0001 C CNN
	1    8850 2700
	1    0    0    -1  
$EndComp
Wire Wire Line
	8850 2700 8850 2850
Wire Wire Line
	8850 3150 8850 3300
Wire Wire Line
	9450 3300 8850 3300
Connection ~ 8850 3300
Wire Wire Line
	8850 3300 8850 3500
$Comp
L power:GND #PWR?
U 1 1 5E795677
P 8850 4000
F 0 "#PWR?" H 8850 3750 50  0001 C CNN
F 1 "GND" H 8855 3827 50  0000 C CNN
F 2 "" H 8850 4000 50  0001 C CNN
F 3 "" H 8850 4000 50  0001 C CNN
	1    8850 4000
	1    0    0    -1  
$EndComp
Wire Wire Line
	8850 4000 8850 3900
$Comp
L Device:R R?
U 1 1 5E79623F
P 8250 3700
F 0 "R?" V 8043 3700 50  0000 C CNN
F 1 "10K" V 8134 3700 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 8180 3700 50  0001 C CNN
F 3 "~" H 8250 3700 50  0001 C CNN
	1    8250 3700
	0    1    1    0   
$EndComp
Wire Wire Line
	8400 3700 8550 3700
Wire Wire Line
	8100 3700 8000 3700
Wire Wire Line
	8000 3700 8000 5000
Connection ~ 8000 5000
Wire Wire Line
	8000 5000 8400 5000
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E798480
P 3650 3650
F 0 "Q?" V 3885 3650 50  0000 C CNN
F 1 "2N2222" V 3976 3650 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3850 3575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 3650 3650 50  0001 L CNN
	1    3650 3650
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E798486
P 3450 4250
F 0 "#PWR?" H 3450 4000 50  0001 C CNN
F 1 "GND" H 3455 4077 50  0000 C CNN
F 2 "" H 3450 4250 50  0001 C CNN
F 3 "" H 3450 4250 50  0001 C CNN
	1    3450 4250
	1    0    0    -1  
$EndComp
Wire Wire Line
	3450 3750 3450 4250
Wire Wire Line
	4000 5000 4000 3750
Wire Wire Line
	3850 3750 4000 3750
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E7996C6
P 4300 3650
F 0 "Q?" V 4535 3650 50  0000 C CNN
F 1 "2N2222" V 4626 3650 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4500 3575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4300 3650 50  0001 L CNN
	1    4300 3650
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E7996CC
P 4100 4250
F 0 "#PWR?" H 4100 4000 50  0001 C CNN
F 1 "GND" H 4105 4077 50  0000 C CNN
F 2 "" H 4100 4250 50  0001 C CNN
F 3 "" H 4100 4250 50  0001 C CNN
	1    4100 4250
	1    0    0    -1  
$EndComp
Wire Wire Line
	4100 3750 4100 4250
Wire Wire Line
	4650 5000 4650 3750
Wire Wire Line
	4500 3750 4650 3750
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E79A5B1
P 5000 3650
F 0 "Q?" V 5235 3650 50  0000 C CNN
F 1 "2N2222" V 5326 3650 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5200 3575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5000 3650 50  0001 L CNN
	1    5000 3650
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E79A5B7
P 4800 4250
F 0 "#PWR?" H 4800 4000 50  0001 C CNN
F 1 "GND" H 4805 4077 50  0000 C CNN
F 2 "" H 4800 4250 50  0001 C CNN
F 3 "" H 4800 4250 50  0001 C CNN
	1    4800 4250
	1    0    0    -1  
$EndComp
Wire Wire Line
	4800 3750 4800 4250
Wire Wire Line
	5350 5000 5350 3750
Wire Wire Line
	5200 3750 5350 3750
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E79B622
P 5650 3650
F 0 "Q?" V 5885 3650 50  0000 C CNN
F 1 "2N2222" V 5976 3650 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5850 3575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5650 3650 50  0001 L CNN
	1    5650 3650
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E79B628
P 5450 4250
F 0 "#PWR?" H 5450 4000 50  0001 C CNN
F 1 "GND" H 5455 4077 50  0000 C CNN
F 2 "" H 5450 4250 50  0001 C CNN
F 3 "" H 5450 4250 50  0001 C CNN
	1    5450 4250
	1    0    0    -1  
$EndComp
Wire Wire Line
	5450 3750 5450 4250
Wire Wire Line
	6000 5000 6000 3750
Wire Wire Line
	5850 3750 6000 3750
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E79C94B
P 6300 3650
F 0 "Q?" V 6535 3650 50  0000 C CNN
F 1 "2N2222" V 6626 3650 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6500 3575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6300 3650 50  0001 L CNN
	1    6300 3650
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E79C951
P 6100 4250
F 0 "#PWR?" H 6100 4000 50  0001 C CNN
F 1 "GND" H 6105 4077 50  0000 C CNN
F 2 "" H 6100 4250 50  0001 C CNN
F 3 "" H 6100 4250 50  0001 C CNN
	1    6100 4250
	1    0    0    -1  
$EndComp
Wire Wire Line
	6100 3750 6100 4250
Wire Wire Line
	6650 5000 6650 3750
Wire Wire Line
	6500 3750 6650 3750
Connection ~ 4000 5000
Wire Wire Line
	4000 5000 4650 5000
Connection ~ 4650 5000
Wire Wire Line
	4650 5000 5350 5000
Connection ~ 5350 5000
Wire Wire Line
	5350 5000 6000 5000
Connection ~ 6000 5000
Wire Wire Line
	6000 5000 6650 5000
Connection ~ 6650 5000
Wire Wire Line
	6650 5000 7300 5000
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E7A1C2A
P 6950 3650
F 0 "Q?" V 7185 3650 50  0000 C CNN
F 1 "2N2222" V 7276 3650 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7150 3575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6950 3650 50  0001 L CNN
	1    6950 3650
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E7A1C30
P 6750 4250
F 0 "#PWR?" H 6750 4000 50  0001 C CNN
F 1 "GND" H 6755 4077 50  0000 C CNN
F 2 "" H 6750 4250 50  0001 C CNN
F 3 "" H 6750 4250 50  0001 C CNN
	1    6750 4250
	1    0    0    -1  
$EndComp
Wire Wire Line
	6750 3750 6750 4250
Wire Wire Line
	7150 3750 7300 3750
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E7A6EB1
P 2300 3650
F 0 "Q?" V 2535 3650 50  0000 C CNN
F 1 "2N2222" V 2626 3650 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2500 3575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2300 3650 50  0001 L CNN
	1    2300 3650
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E7A6EB7
P 2100 4250
F 0 "#PWR?" H 2100 4000 50  0001 C CNN
F 1 "GND" H 2105 4077 50  0000 C CNN
F 2 "" H 2100 4250 50  0001 C CNN
F 3 "" H 2100 4250 50  0001 C CNN
	1    2100 4250
	1    0    0    -1  
$EndComp
Wire Wire Line
	2100 3750 2100 4250
Wire Wire Line
	2500 3750 2650 3750
Wire Wire Line
	2100 2500 2300 2500
Wire Wire Line
	2300 2500 2300 3450
$Comp
L Device:R R?
U 1 1 5E7A9C59
P 2600 2600
F 0 "R?" V 2393 2600 50  0000 C CNN
F 1 "10K" V 2484 2600 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2530 2600 50  0001 C CNN
F 3 "~" H 2600 2600 50  0001 C CNN
	1    2600 2600
	0    1    1    0   
$EndComp
Wire Wire Line
	1150 2600 2450 2600
Wire Wire Line
	2750 2600 3000 2600
Wire Wire Line
	3000 2600 3000 3450
$Comp
L Device:R R?
U 1 1 5E7AF422
P 3250 2700
F 0 "R?" V 3043 2700 50  0000 C CNN
F 1 "10K" V 3134 2700 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3180 2700 50  0001 C CNN
F 3 "~" H 3250 2700 50  0001 C CNN
	1    3250 2700
	0    1    1    0   
$EndComp
Wire Wire Line
	1150 2700 3100 2700
Wire Wire Line
	3400 2700 3650 2700
Wire Wire Line
	3650 2700 3650 3450
$Comp
L Device:R R?
U 1 1 5E7B3555
P 3900 2800
F 0 "R?" V 3693 2800 50  0000 C CNN
F 1 "10K" V 3784 2800 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3830 2800 50  0001 C CNN
F 3 "~" H 3900 2800 50  0001 C CNN
	1    3900 2800
	0    1    1    0   
$EndComp
Wire Wire Line
	4050 2800 4300 2800
Wire Wire Line
	4300 2800 4300 3450
Wire Wire Line
	3750 2800 1150 2800
$Comp
L Device:R R?
U 1 1 5E7B7A19
P 4600 2900
F 0 "R?" V 4393 2900 50  0000 C CNN
F 1 "10K" V 4484 2900 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 4530 2900 50  0001 C CNN
F 3 "~" H 4600 2900 50  0001 C CNN
	1    4600 2900
	0    1    1    0   
$EndComp
$Comp
L Device:R R?
U 1 1 5E7B7A26
P 5250 3000
F 0 "R?" V 5043 3000 50  0000 C CNN
F 1 "10K" V 5134 3000 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5180 3000 50  0001 C CNN
F 3 "~" H 5250 3000 50  0001 C CNN
	1    5250 3000
	0    1    1    0   
$EndComp
Wire Wire Line
	5400 3000 5650 3000
$Comp
L Device:R R?
U 1 1 5E7B7A33
P 5900 3100
F 0 "R?" V 5693 3100 50  0000 C CNN
F 1 "10K" V 5784 3100 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 5830 3100 50  0001 C CNN
F 3 "~" H 5900 3100 50  0001 C CNN
	1    5900 3100
	0    1    1    0   
$EndComp
Wire Wire Line
	6050 3100 6300 3100
$Comp
L Device:R R?
U 1 1 5E7B7A40
P 6550 3200
F 0 "R?" V 6343 3200 50  0000 C CNN
F 1 "10K" V 6434 3200 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 6480 3200 50  0001 C CNN
F 3 "~" H 6550 3200 50  0001 C CNN
	1    6550 3200
	0    1    1    0   
$EndComp
Wire Wire Line
	1150 2900 4450 2900
Wire Wire Line
	1150 3000 5100 3000
Wire Wire Line
	1150 3100 5750 3100
Wire Wire Line
	1150 3200 6400 3200
Wire Wire Line
	4750 2900 5000 2900
Wire Wire Line
	5000 2900 5000 3450
Wire Wire Line
	5650 3000 5650 3450
Wire Wire Line
	6300 3450 6300 3100
Wire Wire Line
	6700 3200 6950 3200
Wire Wire Line
	6950 3200 6950 3450
Wire Wire Line
	2650 3750 2650 5000
Connection ~ 2650 5000
Wire Wire Line
	2650 5000 3350 5000
Wire Wire Line
	7300 3750 7300 5000
Connection ~ 7300 5000
Wire Wire Line
	7300 5000 8000 5000
Text Label 2700 1250 1    50   ~ 0
GND
Text Label 2600 1250 1    50   ~ 0
VCC
Text HLabel 1150 2500 0    50   Input ~ 0
D0
Text HLabel 1150 2600 0    50   Input ~ 0
D1
Text HLabel 1150 2700 0    50   Input ~ 0
D2
Text HLabel 1150 2800 0    50   Input ~ 0
D3
Text HLabel 1150 2900 0    50   Input ~ 0
D4
Text HLabel 1150 3000 0    50   Input ~ 0
D5
Text HLabel 1150 3100 0    50   Input ~ 0
D6
Text HLabel 1150 3200 0    50   Input ~ 0
D7
Text HLabel 10550 3600 2    50   Output ~ 0
NZ
Text HLabel 9500 5300 2    50   Output ~ 0
Z
$EndSCHEMATC
