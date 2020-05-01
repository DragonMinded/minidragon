EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A2 23386 16535
encoding utf-8
Sheet 472 484
Title "Instruction Decoder ROM Mini Board"
Date "2020-03-23"
Rev "1"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 606D321A
P 5700 1650
F 0 "J?" V 5854 1462 50  0000 R CNN
F 1 "Power" V 5763 1462 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 5700 1650 50  0001 C CNN
F 3 "~" H 5700 1650 50  0001 C CNN
	1    5700 1650
	0    -1   -1   0   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 606D321B
P 5700 1300
F 0 "#PWR?" H 5700 1150 50  0001 C CNN
F 1 "VCC" H 5650 1450 50  0000 C CNN
F 2 "" H 5700 1300 50  0001 C CNN
F 3 "" H 5700 1300 50  0001 C CNN
	1    5700 1300
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D321C
P 5800 1300
F 0 "#PWR?" H 5800 1050 50  0001 C CNN
F 1 "GND" H 5750 1150 50  0000 C CNN
F 2 "" H 5800 1300 50  0001 C CNN
F 3 "" H 5800 1300 50  0001 C CNN
	1    5800 1300
	-1   0    0    1   
$EndComp
Wire Wire Line
	5700 1450 5700 1300
Wire Wire Line
	5800 1450 5800 1300
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 606D3215
P 6200 1650
F 0 "J?" V 6354 1462 50  0000 R CNN
F 1 "Power" V 6263 1462 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 6200 1650 50  0001 C CNN
F 3 "~" H 6200 1650 50  0001 C CNN
	1    6200 1650
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x02_Male J?
U 1 1 606D3246
P 6650 1650
F 0 "J?" V 6804 1462 50  0000 R CNN
F 1 "Power" V 6713 1462 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 6650 1650 50  0001 C CNN
F 3 "~" H 6650 1650 50  0001 C CNN
	1    6650 1650
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3216
P 6300 1300
F 0 "#PWR?" H 6300 1050 50  0001 C CNN
F 1 "GND" H 6250 1150 50  0000 C CNN
F 2 "" H 6300 1300 50  0001 C CNN
F 3 "" H 6300 1300 50  0001 C CNN
	1    6300 1300
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60DC914B
P 6750 1300
F 0 "#PWR?" H 6750 1050 50  0001 C CNN
F 1 "GND" H 6700 1150 50  0000 C CNN
F 2 "" H 6750 1300 50  0001 C CNN
F 3 "" H 6750 1300 50  0001 C CNN
	1    6750 1300
	-1   0    0    1   
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 60DC914C
P 6200 1300
F 0 "#PWR?" H 6200 1150 50  0001 C CNN
F 1 "VCC" H 6150 1450 50  0000 C CNN
F 2 "" H 6200 1300 50  0001 C CNN
F 3 "" H 6200 1300 50  0001 C CNN
	1    6200 1300
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 601FA32E
P 6650 1300
F 0 "#PWR?" H 6650 1150 50  0001 C CNN
F 1 "VCC" H 6600 1450 50  0000 C CNN
F 2 "" H 6650 1300 50  0001 C CNN
F 3 "" H 6650 1300 50  0001 C CNN
	1    6650 1300
	1    0    0    -1  
$EndComp
Wire Wire Line
	6200 1300 6200 1450
Wire Wire Line
	6300 1450 6300 1300
Wire Wire Line
	6650 1300 6650 1450
Wire Wire Line
	6750 1450 6750 1300
$Comp
L power:VCC #PWR?
U 1 1 606D3247
P 4900 1100
F 0 "#PWR?" H 4900 950 50  0001 C CNN
F 1 "VCC" H 4917 1273 50  0000 C CNN
F 2 "" H 4900 1100 50  0001 C CNN
F 3 "" H 4900 1100 50  0001 C CNN
	1    4900 1100
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3248
P 4900 1600
F 0 "#PWR?" H 4900 1350 50  0001 C CNN
F 1 "GND" H 4905 1427 50  0000 C CNN
F 2 "" H 4900 1600 50  0001 C CNN
F 3 "" H 4900 1600 50  0001 C CNN
	1    4900 1600
	1    0    0    -1  
$EndComp
$Comp
L Device:C C?
U 1 1 60DC914D
P 4900 1350
F 0 "C?" H 5015 1396 50  0000 L CNN
F 1 "0.1uF" H 5015 1305 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" H 4938 1200 50  0001 C CNN
F 3 "~" H 4900 1350 50  0001 C CNN
	1    4900 1350
	1    0    0    -1  
$EndComp
Wire Wire Line
	4900 1100 4900 1200
Wire Wire Line
	4900 1500 4900 1600
$Comp
L Device:R R?
U 1 1 60F05D9E
P 2200 1850
F 0 "R?" V 1993 1850 50  0000 C CNN
F 1 "10K" V 2084 1850 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2130 1850 50  0001 C CNN
F 3 "~" H 2200 1850 50  0001 C CNN
	1    2200 1850
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 60F05D9F
P 2550 1850
F 0 "Q?" H 2740 1896 50  0000 L CNN
F 1 "2N2222" H 2740 1805 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2750 1775 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 2550 1850 50  0001 L CNN
	1    2550 1850
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 606D3265
P 2650 2550
F 0 "R?" H 2720 2596 50  0000 L CNN
F 1 "1K" H 2720 2505 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 2580 2550 50  0001 C CNN
F 3 "~" H 2650 2550 50  0001 C CNN
	1    2650 2550
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR?
U 1 1 606D321F
P 2650 1550
F 0 "#PWR?" H 2650 1400 50  0001 C CNN
F 1 "VCC" H 2667 1723 50  0000 C CNN
F 2 "" H 2650 1550 50  0001 C CNN
F 3 "" H 2650 1550 50  0001 C CNN
	1    2650 1550
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3249
P 2650 2800
F 0 "#PWR?" H 2650 2550 50  0001 C CNN
F 1 "GND" H 2655 2627 50  0000 C CNN
F 2 "" H 2650 2800 50  0001 C CNN
F 3 "" H 2650 2800 50  0001 C CNN
	1    2650 2800
	1    0    0    -1  
$EndComp
Wire Wire Line
	1400 1850 2050 1850
$Comp
L Connector_Generic:Conn_02x32_Odd_Even J?
U 1 1 606D324A
P 3850 5000
F 0 "J?" H 3900 6717 50  0000 C CNN
F 1 "BIT_4_CONFIG" H 3900 6626 50  0000 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_2x32_P2.54mm_Vertical" H 3850 5000 50  0001 C CNN
F 3 "~" H 3850 5000 50  0001 C CNN
	1    3850 5000
	1    0    0    -1  
$EndComp
Wire Wire Line
	3300 6600 3650 6600
Wire Wire Line
	3650 6500 3300 6500
Connection ~ 3300 6500
Wire Wire Line
	3300 6500 3300 6600
Wire Wire Line
	3300 6400 3650 6400
Connection ~ 3300 6400
Wire Wire Line
	3300 6400 3300 6500
Wire Wire Line
	3650 6300 3300 6300
Connection ~ 3300 6300
Wire Wire Line
	3300 6300 3300 6400
Wire Wire Line
	3300 6200 3650 6200
Connection ~ 3300 6200
Wire Wire Line
	3300 6200 3300 6300
Wire Wire Line
	3650 6100 3300 6100
Connection ~ 3300 6100
Wire Wire Line
	3300 6100 3300 6200
Wire Wire Line
	3300 6000 3650 6000
Connection ~ 3300 6000
Wire Wire Line
	3300 6000 3300 6100
Wire Wire Line
	3650 5900 3300 5900
Connection ~ 3300 5900
Wire Wire Line
	3300 5900 3300 6000
Wire Wire Line
	3300 5800 3650 5800
Connection ~ 3300 5800
Wire Wire Line
	3300 5800 3300 5900
Wire Wire Line
	3650 5700 3300 5700
Connection ~ 3300 5700
Wire Wire Line
	3300 5700 3300 5800
Wire Wire Line
	3300 5600 3650 5600
Connection ~ 3300 5600
Wire Wire Line
	3300 5600 3300 5700
Wire Wire Line
	3650 5500 3300 5500
Connection ~ 3300 5500
Wire Wire Line
	3300 5500 3300 5600
Wire Wire Line
	3300 5400 3650 5400
Connection ~ 3300 5400
Wire Wire Line
	3300 5400 3300 5500
Wire Wire Line
	3650 5300 3300 5300
Connection ~ 3300 5300
Wire Wire Line
	3300 5300 3300 5400
Wire Wire Line
	3300 5200 3650 5200
Connection ~ 3300 5200
Wire Wire Line
	3300 5200 3300 5300
Wire Wire Line
	3650 5100 3300 5100
Connection ~ 3300 5100
Wire Wire Line
	3300 5100 3300 5200
Wire Wire Line
	3300 5000 3650 5000
Connection ~ 3300 5000
Wire Wire Line
	3300 5000 3300 5100
Wire Wire Line
	3650 4900 3300 4900
Connection ~ 3300 4900
Wire Wire Line
	3300 4900 3300 5000
Wire Wire Line
	3300 4800 3650 4800
Connection ~ 3300 4800
Wire Wire Line
	3300 4800 3300 4900
Wire Wire Line
	3650 4700 3300 4700
Connection ~ 3300 4700
Wire Wire Line
	3300 4700 3300 4800
Wire Wire Line
	3300 4600 3650 4600
Connection ~ 3300 4600
Wire Wire Line
	3300 4600 3300 4700
Wire Wire Line
	3650 4500 3300 4500
Connection ~ 3300 4500
Wire Wire Line
	3300 4500 3300 4600
Wire Wire Line
	3300 4400 3650 4400
Connection ~ 3300 4400
Wire Wire Line
	3300 4400 3300 4500
Wire Wire Line
	3650 4300 3300 4300
Connection ~ 3300 4300
Wire Wire Line
	3300 4300 3300 4400
Wire Wire Line
	3300 4200 3650 4200
Connection ~ 3300 4200
Wire Wire Line
	3300 4200 3300 4300
Wire Wire Line
	3650 4100 3300 4100
Connection ~ 3300 4100
Wire Wire Line
	3300 4100 3300 4200
Wire Wire Line
	3300 4000 3650 4000
Connection ~ 3300 4000
Wire Wire Line
	3300 4000 3300 4100
Wire Wire Line
	3650 3900 3300 3900
Connection ~ 3300 3900
Wire Wire Line
	3300 3900 3300 4000
Wire Wire Line
	3300 3800 3650 3800
Connection ~ 3300 3800
Wire Wire Line
	3300 3800 3300 3900
Wire Wire Line
	3650 3700 3300 3700
Connection ~ 3300 3700
Wire Wire Line
	3300 3700 3300 3800
Wire Wire Line
	3300 3600 3650 3600
Connection ~ 3300 3600
Wire Wire Line
	3300 3600 3300 3700
Wire Wire Line
	3650 3500 3300 3500
Wire Wire Line
	3300 3500 3300 3600
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D324B
P 4250 9800
F 0 "Q?" H 4440 9846 50  0000 L CNN
F 1 "2N2222" H 4440 9755 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4450 9725 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4250 9800 50  0001 L CNN
	1    4250 9800
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3220
P 4050 9900
F 0 "#PWR?" H 4050 9650 50  0001 C CNN
F 1 "GND" H 4050 9750 50  0001 C CNN
F 2 "" H 4050 9900 50  0001 C CNN
F 3 "" H 4050 9900 50  0001 C CNN
	1    4050 9900
	0    1    1    0   
$EndComp
Wire Wire Line
	4250 9600 4250 6600
Wire Wire Line
	4250 6600 4150 6600
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D324C
P 4600 9250
F 0 "Q?" H 4790 9296 50  0000 L CNN
F 1 "2N2222" H 4790 9205 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 4800 9175 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4600 9250 50  0001 L CNN
	1    4600 9250
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D324D
P 4400 9350
F 0 "#PWR?" H 4400 9100 50  0001 C CNN
F 1 "GND" H 4405 9177 50  0001 C CNN
F 2 "" H 4400 9350 50  0001 C CNN
F 3 "" H 4400 9350 50  0001 C CNN
	1    4400 9350
	0    1    1    0   
$EndComp
Wire Wire Line
	4800 9350 4800 9800
Wire Wire Line
	4800 9800 4550 9800
Wire Wire Line
	4600 9050 4600 6500
Wire Wire Line
	4600 6500 4150 6500
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D3221
P 4950 8900
F 0 "Q?" H 5140 8946 50  0000 L CNN
F 1 "2N2222" H 5140 8855 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5150 8825 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 4950 8900 50  0001 L CNN
	1    4950 8900
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3222
P 4750 9000
F 0 "#PWR?" H 4750 8750 50  0001 C CNN
F 1 "GND" H 4755 8827 50  0001 C CNN
F 2 "" H 4750 9000 50  0001 C CNN
F 3 "" H 4750 9000 50  0001 C CNN
	1    4750 9000
	0    1    1    0   
$EndComp
Wire Wire Line
	5150 9000 5150 9450
Wire Wire Line
	5150 9450 4850 9450
Wire Wire Line
	4850 9450 4850 9850
Wire Wire Line
	4850 9850 4650 9850
Wire Wire Line
	4950 8700 4950 6400
Wire Wire Line
	4150 6400 4950 6400
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D3223
P 5300 8500
F 0 "Q?" H 5490 8546 50  0000 L CNN
F 1 "2N2222" H 5490 8455 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5500 8425 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5300 8500 50  0001 L CNN
	1    5300 8500
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3224
P 5100 8600
F 0 "#PWR?" H 5100 8350 50  0001 C CNN
F 1 "GND" H 5105 8427 50  0001 C CNN
F 2 "" H 5100 8600 50  0001 C CNN
F 3 "" H 5100 8600 50  0001 C CNN
	1    5100 8600
	0    1    1    0   
$EndComp
Wire Wire Line
	5500 8600 5500 9050
$Comp
L 2n2222:2N2222 Q?
U 1 1 60DC9182
P 5650 8150
F 0 "Q?" H 5840 8196 50  0000 L CNN
F 1 "2N2222" H 5840 8105 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5850 8075 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5650 8150 50  0001 L CNN
	1    5650 8150
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60DC9159
P 5450 8250
F 0 "#PWR?" H 5450 8000 50  0001 C CNN
F 1 "GND" H 5455 8077 50  0001 C CNN
F 2 "" H 5450 8250 50  0001 C CNN
F 3 "" H 5450 8250 50  0001 C CNN
	1    5450 8250
	0    1    1    0   
$EndComp
Wire Wire Line
	5850 8250 5850 8700
Wire Wire Line
	5850 8700 5550 8700
Wire Wire Line
	5550 8700 5550 9100
Wire Wire Line
	5500 9050 5200 9050
Wire Wire Line
	5200 9500 4900 9500
Wire Wire Line
	4900 9500 4900 9900
Wire Wire Line
	5200 9050 5200 9500
Wire Wire Line
	5550 9100 5250 9100
Wire Wire Line
	5250 9100 5250 9550
Wire Wire Line
	5250 9550 4950 9550
Wire Wire Line
	4950 9550 4950 9950
Wire Wire Line
	4950 9950 4850 9950
Wire Wire Line
	5300 8300 5300 6300
Wire Wire Line
	5300 6300 4150 6300
Wire Wire Line
	5650 7950 5650 6200
Wire Wire Line
	5650 6200 4150 6200
$Comp
L 2n2222:2N2222 Q?
U 1 1 60DC915A
P 6000 7750
F 0 "Q?" H 6190 7796 50  0000 L CNN
F 1 "2N2222" H 6190 7705 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6200 7675 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6000 7750 50  0001 L CNN
	1    6000 7750
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E8591B7
P 5800 7850
F 0 "#PWR?" H 5800 7600 50  0001 C CNN
F 1 "GND" H 5805 7677 50  0001 C CNN
F 2 "" H 5800 7850 50  0001 C CNN
F 3 "" H 5800 7850 50  0001 C CNN
	1    5800 7850
	0    1    1    0   
$EndComp
Wire Wire Line
	6200 7850 6200 8300
$Comp
L 2n2222:2N2222 Q?
U 1 1 60F05DA9
P 6350 7400
F 0 "Q?" H 6540 7446 50  0000 L CNN
F 1 "2N2222" H 6540 7355 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6550 7325 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6350 7400 50  0001 L CNN
	1    6350 7400
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60DC915D
P 6150 7500
F 0 "#PWR?" H 6150 7250 50  0001 C CNN
F 1 "GND" H 6155 7327 50  0001 C CNN
F 2 "" H 6150 7500 50  0001 C CNN
F 3 "" H 6150 7500 50  0001 C CNN
	1    6150 7500
	0    1    1    0   
$EndComp
Wire Wire Line
	6550 7500 6550 7950
Wire Wire Line
	6550 7950 6250 7950
Wire Wire Line
	6250 7950 6250 8350
$Comp
L 2n2222:2N2222 Q?
U 1 1 5E8591DB
P 6700 7000
F 0 "Q?" H 6890 7046 50  0000 L CNN
F 1 "2N2222" H 6890 6955 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6900 6925 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6700 7000 50  0001 L CNN
	1    6700 7000
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60F05DE7
P 6500 7100
F 0 "#PWR?" H 6500 6850 50  0001 C CNN
F 1 "GND" H 6505 6927 50  0001 C CNN
F 2 "" H 6500 7100 50  0001 C CNN
F 3 "" H 6500 7100 50  0001 C CNN
	1    6500 7100
	0    1    1    0   
$EndComp
Wire Wire Line
	6900 7100 6900 7550
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D322B
P 7050 6650
F 0 "Q?" H 7240 6696 50  0000 L CNN
F 1 "2N2222" H 7240 6605 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7250 6575 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 7050 6650 50  0001 L CNN
	1    7050 6650
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D322C
P 6850 6750
F 0 "#PWR?" H 6850 6500 50  0001 C CNN
F 1 "GND" H 6855 6577 50  0001 C CNN
F 2 "" H 6850 6750 50  0001 C CNN
F 3 "" H 6850 6750 50  0001 C CNN
	1    6850 6750
	0    1    1    0   
$EndComp
Wire Wire Line
	7250 6750 7250 7200
Wire Wire Line
	7250 7200 6950 7200
Wire Wire Line
	6950 7200 6950 7600
Wire Wire Line
	6900 7550 6600 7550
Wire Wire Line
	6600 8000 6300 8000
Wire Wire Line
	6300 8000 6300 8400
Wire Wire Line
	6600 7550 6600 8000
Wire Wire Line
	6950 7600 6650 7600
Wire Wire Line
	6650 7600 6650 8050
Wire Wire Line
	6000 7550 6000 6100
Wire Wire Line
	6000 6100 4150 6100
Wire Wire Line
	4150 6000 6350 6000
Wire Wire Line
	6350 6000 6350 7200
Wire Wire Line
	6700 6800 6700 5900
Wire Wire Line
	6700 5900 4150 5900
Wire Wire Line
	4150 5800 7050 5800
Wire Wire Line
	7050 5800 7050 6450
Wire Wire Line
	4900 9900 4750 9900
Wire Wire Line
	6200 8300 5900 8300
Wire Wire Line
	5900 8300 5900 8750
Wire Wire Line
	5900 8750 5600 8750
Wire Wire Line
	5600 8750 5600 9150
Wire Wire Line
	5600 9150 5300 9150
Wire Wire Line
	5300 9150 5300 9600
Wire Wire Line
	5300 9600 5000 9600
Wire Wire Line
	5000 9600 5000 10000
Wire Wire Line
	5000 10000 4950 10000
Wire Wire Line
	5350 9200 5650 9200
Wire Wire Line
	5650 9200 5650 8800
Wire Wire Line
	5650 8800 5950 8800
Wire Wire Line
	5950 8800 5950 8350
Wire Wire Line
	5950 8350 6250 8350
Wire Wire Line
	5350 9200 5350 9650
Wire Wire Line
	5350 9650 5050 9650
Wire Wire Line
	5150 9700 5400 9700
Wire Wire Line
	5400 9700 5400 9250
Wire Wire Line
	5400 9250 5700 9250
Wire Wire Line
	5700 9250 5700 8850
Wire Wire Line
	5700 8850 6000 8850
Wire Wire Line
	6000 8850 6000 8400
Wire Wire Line
	6000 8400 6300 8400
Wire Wire Line
	6650 8050 6350 8050
Wire Wire Line
	6350 8050 6350 8450
Wire Wire Line
	6350 8450 6050 8450
Wire Wire Line
	6050 8450 6050 8900
Wire Wire Line
	6050 8900 5750 8900
Wire Wire Line
	5750 8900 5750 9300
Wire Wire Line
	5750 9300 5450 9300
Wire Wire Line
	5450 9300 5450 9750
Wire Wire Line
	5450 9750 5250 9750
$Comp
L 2n2222:2N2222 Q?
U 1 1 60DC9161
P 5600 10250
F 0 "Q?" H 5790 10296 50  0000 L CNN
F 1 "2N2222" H 5790 10205 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 5800 10175 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5600 10250 50  0001 L CNN
	1    5600 10250
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D322E
P 5400 10350
F 0 "#PWR?" H 5400 10100 50  0001 C CNN
F 1 "GND" H 5400 10200 50  0001 C CNN
F 2 "" H 5400 10350 50  0001 C CNN
F 3 "" H 5400 10350 50  0001 C CNN
	1    5400 10350
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 60DC9163
P 5950 9700
F 0 "Q?" H 6140 9746 50  0000 L CNN
F 1 "2N2222" H 6140 9655 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6150 9625 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5950 9700 50  0001 L CNN
	1    5950 9700
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E8CEC15
P 5750 9800
F 0 "#PWR?" H 5750 9550 50  0001 C CNN
F 1 "GND" H 5755 9627 50  0001 C CNN
F 2 "" H 5750 9800 50  0001 C CNN
F 3 "" H 5750 9800 50  0001 C CNN
	1    5750 9800
	0    1    1    0   
$EndComp
Wire Wire Line
	6150 9800 6150 10250
Wire Wire Line
	6150 10250 5850 10250
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D3231
P 6300 9350
F 0 "Q?" H 6490 9396 50  0000 L CNN
F 1 "2N2222" H 6490 9305 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6500 9275 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6300 9350 50  0001 L CNN
	1    6300 9350
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D324F
P 6100 9450
F 0 "#PWR?" H 6100 9200 50  0001 C CNN
F 1 "GND" H 6105 9277 50  0001 C CNN
F 2 "" H 6100 9450 50  0001 C CNN
F 3 "" H 6100 9450 50  0001 C CNN
	1    6100 9450
	0    1    1    0   
$EndComp
Wire Wire Line
	6500 9450 6500 9900
Wire Wire Line
	6500 9900 6200 9900
Wire Wire Line
	6200 9900 6200 10300
Wire Wire Line
	6200 10300 5900 10300
$Comp
L 2n2222:2N2222 Q?
U 1 1 60DC9184
P 6650 8950
F 0 "Q?" H 6840 8996 50  0000 L CNN
F 1 "2N2222" H 6840 8905 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6850 8875 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6650 8950 50  0001 L CNN
	1    6650 8950
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3251
P 6450 9050
F 0 "#PWR?" H 6450 8800 50  0001 C CNN
F 1 "GND" H 6455 8877 50  0001 C CNN
F 2 "" H 6450 9050 50  0001 C CNN
F 3 "" H 6450 9050 50  0001 C CNN
	1    6450 9050
	0    1    1    0   
$EndComp
Wire Wire Line
	6850 9050 6850 9500
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D3252
P 7000 8600
F 0 "Q?" H 7190 8646 50  0000 L CNN
F 1 "2N2222" H 7190 8555 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7200 8525 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 7000 8600 50  0001 L CNN
	1    7000 8600
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E8CEC5C
P 6800 8700
F 0 "#PWR?" H 6800 8450 50  0001 C CNN
F 1 "GND" H 6805 8527 50  0001 C CNN
F 2 "" H 6800 8700 50  0001 C CNN
F 3 "" H 6800 8700 50  0001 C CNN
	1    6800 8700
	0    1    1    0   
$EndComp
Wire Wire Line
	7200 8700 7200 9150
Wire Wire Line
	7200 9150 6900 9150
Wire Wire Line
	6900 9150 6900 9550
Wire Wire Line
	6850 9500 6550 9500
Wire Wire Line
	6550 9950 6250 9950
Wire Wire Line
	6250 9950 6250 10350
Wire Wire Line
	6550 9500 6550 9950
Wire Wire Line
	6900 9550 6600 9550
Wire Wire Line
	6600 9550 6600 10000
Wire Wire Line
	6600 10000 6300 10000
Wire Wire Line
	6300 10000 6300 10400
Wire Wire Line
	6300 10400 6000 10400
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D3253
P 7350 8200
F 0 "Q?" H 7540 8246 50  0000 L CNN
F 1 "2N2222" H 7540 8155 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7550 8125 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 7350 8200 50  0001 L CNN
	1    7350 8200
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3254
P 7150 8300
F 0 "#PWR?" H 7150 8050 50  0001 C CNN
F 1 "GND" H 7155 8127 50  0001 C CNN
F 2 "" H 7150 8300 50  0001 C CNN
F 3 "" H 7150 8300 50  0001 C CNN
	1    7150 8300
	0    1    1    0   
$EndComp
Wire Wire Line
	7550 8300 7550 8750
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D3233
P 7700 7850
F 0 "Q?" H 7890 7896 50  0000 L CNN
F 1 "2N2222" H 7890 7805 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7900 7775 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 7700 7850 50  0001 L CNN
	1    7700 7850
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3255
P 7500 7950
F 0 "#PWR?" H 7500 7700 50  0001 C CNN
F 1 "GND" H 7505 7777 50  0001 C CNN
F 2 "" H 7500 7950 50  0001 C CNN
F 3 "" H 7500 7950 50  0001 C CNN
	1    7500 7950
	0    1    1    0   
$EndComp
Wire Wire Line
	7900 7950 7900 8400
Wire Wire Line
	7900 8400 7600 8400
Wire Wire Line
	7600 8400 7600 8800
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D3234
P 8050 7450
F 0 "Q?" H 8240 7496 50  0000 L CNN
F 1 "2N2222" H 8240 7405 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 8250 7375 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 8050 7450 50  0001 L CNN
	1    8050 7450
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3235
P 7850 7550
F 0 "#PWR?" H 7850 7300 50  0001 C CNN
F 1 "GND" H 7855 7377 50  0001 C CNN
F 2 "" H 7850 7550 50  0001 C CNN
F 3 "" H 7850 7550 50  0001 C CNN
	1    7850 7550
	0    1    1    0   
$EndComp
Wire Wire Line
	8250 7550 8250 8000
$Comp
L 2n2222:2N2222 Q?
U 1 1 5FC37E6A
P 8400 7100
F 0 "Q?" H 8590 7146 50  0000 L CNN
F 1 "2N2222" H 8590 7055 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 8600 7025 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 8400 7100 50  0001 L CNN
	1    8400 7100
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3257
P 8200 7200
F 0 "#PWR?" H 8200 6950 50  0001 C CNN
F 1 "GND" H 8205 7027 50  0001 C CNN
F 2 "" H 8200 7200 50  0001 C CNN
F 3 "" H 8200 7200 50  0001 C CNN
	1    8200 7200
	0    1    1    0   
$EndComp
Wire Wire Line
	8600 7200 8600 7650
Wire Wire Line
	8600 7650 8300 7650
Wire Wire Line
	8300 7650 8300 8050
Wire Wire Line
	8250 8000 7950 8000
Wire Wire Line
	7950 8450 7650 8450
Wire Wire Line
	7650 8450 7650 8850
Wire Wire Line
	7950 8000 7950 8450
Wire Wire Line
	8300 8050 8000 8050
Wire Wire Line
	8000 8050 8000 8500
Wire Wire Line
	6250 10350 5950 10350
Wire Wire Line
	7550 8750 7250 8750
Wire Wire Line
	7250 8750 7250 9200
Wire Wire Line
	7250 9200 6950 9200
Wire Wire Line
	6950 9200 6950 9600
Wire Wire Line
	6950 9600 6650 9600
Wire Wire Line
	6650 9600 6650 10050
Wire Wire Line
	6650 10050 6350 10050
Wire Wire Line
	6350 10050 6350 10450
Wire Wire Line
	6350 10450 6050 10450
Wire Wire Line
	6700 9650 7000 9650
Wire Wire Line
	7000 9650 7000 9250
Wire Wire Line
	7000 9250 7300 9250
Wire Wire Line
	7300 9250 7300 8800
Wire Wire Line
	7300 8800 7600 8800
Wire Wire Line
	6700 9650 6700 10100
Wire Wire Line
	6700 10100 6400 10100
Wire Wire Line
	6450 10150 6750 10150
Wire Wire Line
	6750 10150 6750 9700
Wire Wire Line
	6750 9700 7050 9700
Wire Wire Line
	7050 9700 7050 9300
Wire Wire Line
	7050 9300 7350 9300
Wire Wire Line
	7350 9300 7350 8850
Wire Wire Line
	7350 8850 7650 8850
Wire Wire Line
	8000 8500 7700 8500
Wire Wire Line
	7700 8500 7700 8900
Wire Wire Line
	7700 8900 7400 8900
Wire Wire Line
	7400 8900 7400 9350
Wire Wire Line
	7400 9350 7100 9350
Wire Wire Line
	7100 9350 7100 9750
Wire Wire Line
	7100 9750 6800 9750
Wire Wire Line
	6800 9750 6800 10200
Wire Wire Line
	6800 10200 6500 10200
Wire Wire Line
	5800 10350 5800 10850
Wire Wire Line
	5800 10850 5350 10850
Wire Wire Line
	5450 10900 5850 10900
Wire Wire Line
	5850 10900 5850 10250
Wire Wire Line
	5900 10300 5900 10950
Wire Wire Line
	5900 10950 5550 10950
Wire Wire Line
	5650 11000 5950 11000
Wire Wire Line
	5950 11000 5950 10350
Wire Wire Line
	6000 10400 6000 11050
Wire Wire Line
	6000 11050 5750 11050
Wire Wire Line
	5850 11100 6050 11100
Wire Wire Line
	6050 11100 6050 10450
Wire Wire Line
	6400 10100 6400 10500
Wire Wire Line
	6450 10550 6450 10150
Wire Wire Line
	6500 10200 6500 10600
Wire Wire Line
	5600 10050 5600 9350
Wire Wire Line
	5600 9350 5800 9350
Wire Wire Line
	5800 9350 5800 8950
Wire Wire Line
	5800 8950 6100 8950
Wire Wire Line
	6100 8950 6100 8500
Wire Wire Line
	6100 8500 6400 8500
Wire Wire Line
	6400 8500 6400 8100
Wire Wire Line
	6400 8100 6700 8100
Wire Wire Line
	6700 8100 6700 7650
Wire Wire Line
	6700 7650 7000 7650
Wire Wire Line
	7000 7650 7000 7250
Wire Wire Line
	7000 7250 7300 7250
Wire Wire Line
	7300 7250 7300 5700
Wire Wire Line
	7300 5700 4150 5700
Wire Wire Line
	5950 9500 5950 9000
Wire Wire Line
	5950 9000 6150 9000
Wire Wire Line
	6150 9000 6150 8550
Wire Wire Line
	6150 8550 6450 8550
Wire Wire Line
	6450 8550 6450 8150
Wire Wire Line
	6450 8150 6750 8150
Wire Wire Line
	6750 8150 6750 7700
Wire Wire Line
	6750 7700 7050 7700
Wire Wire Line
	7050 7700 7050 7300
Wire Wire Line
	7050 7300 7350 7300
Wire Wire Line
	7350 7300 7350 5600
Wire Wire Line
	7350 5600 4150 5600
Wire Wire Line
	6300 9150 6300 8600
Wire Wire Line
	6500 8600 6500 8200
Wire Wire Line
	6500 8200 6800 8200
Wire Wire Line
	6800 8200 6800 7750
Wire Wire Line
	6800 7750 7100 7750
Wire Wire Line
	7100 7750 7100 7350
Wire Wire Line
	7100 7350 7400 7350
Wire Wire Line
	7400 7350 7400 5500
Wire Wire Line
	7400 5500 4150 5500
Wire Wire Line
	6300 8600 6500 8600
Wire Wire Line
	6650 8750 6650 8250
Wire Wire Line
	6650 8250 6850 8250
Wire Wire Line
	6850 8250 6850 7800
Wire Wire Line
	6850 7800 7150 7800
Wire Wire Line
	7150 7800 7150 7400
Wire Wire Line
	7150 7400 7450 7400
Wire Wire Line
	7450 7400 7450 5400
Wire Wire Line
	7450 5400 4150 5400
Wire Wire Line
	7000 8400 7000 7850
Wire Wire Line
	7000 7850 7200 7850
Wire Wire Line
	7200 7850 7200 7450
Wire Wire Line
	7200 7450 7500 7450
Wire Wire Line
	7500 7450 7500 5300
Wire Wire Line
	7500 5300 4150 5300
Wire Wire Line
	7350 8000 7350 7500
Wire Wire Line
	7350 7500 7550 7500
Wire Wire Line
	7550 7500 7550 5200
Wire Wire Line
	7550 5200 4150 5200
Wire Wire Line
	7700 7650 7700 5100
Wire Wire Line
	7700 5100 4150 5100
Wire Wire Line
	8050 7250 8050 5000
Wire Wire Line
	8050 5000 4150 5000
Wire Wire Line
	8400 6900 8400 4900
Wire Wire Line
	8400 4900 4150 4900
$Comp
L 2n2222:2N2222 Q?
U 1 1 5EB11F9A
P 6500 11350
F 0 "Q?" H 6690 11396 50  0000 L CNN
F 1 "2N2222" H 6690 11305 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6700 11275 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6500 11350 50  0001 L CNN
	1    6500 11350
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60DC916B
P 6300 11450
F 0 "#PWR?" H 6300 11200 50  0001 C CNN
F 1 "GND" H 6300 11300 50  0001 C CNN
F 2 "" H 6300 11450 50  0001 C CNN
F 3 "" H 6300 11450 50  0001 C CNN
	1    6300 11450
	0    1    1    0   
$EndComp
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D3258
P 6850 10800
F 0 "Q?" H 7040 10846 50  0000 L CNN
F 1 "2N2222" H 7040 10755 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7050 10725 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 6850 10800 50  0001 L CNN
	1    6850 10800
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3238
P 6650 10900
F 0 "#PWR?" H 6650 10650 50  0001 C CNN
F 1 "GND" H 6655 10727 50  0001 C CNN
F 2 "" H 6650 10900 50  0001 C CNN
F 3 "" H 6650 10900 50  0001 C CNN
	1    6650 10900
	0    1    1    0   
$EndComp
Wire Wire Line
	7050 10900 7050 11350
$Comp
L 2n2222:2N2222 Q?
U 1 1 5EB11FC4
P 7200 10450
F 0 "Q?" H 7390 10496 50  0000 L CNN
F 1 "2N2222" H 7390 10405 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7400 10375 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 7200 10450 50  0001 L CNN
	1    7200 10450
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3259
P 7000 10550
F 0 "#PWR?" H 7000 10300 50  0001 C CNN
F 1 "GND" H 7005 10377 50  0001 C CNN
F 2 "" H 7000 10550 50  0001 C CNN
F 3 "" H 7000 10550 50  0001 C CNN
	1    7000 10550
	0    1    1    0   
$EndComp
Wire Wire Line
	7400 10550 7400 11000
Wire Wire Line
	7400 11000 7100 11000
Wire Wire Line
	7100 11000 7100 11400
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D323A
P 7550 10050
F 0 "Q?" H 7740 10096 50  0000 L CNN
F 1 "2N2222" H 7740 10005 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7750 9975 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 7550 10050 50  0001 L CNN
	1    7550 10050
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60F05DDB
P 7350 10150
F 0 "#PWR?" H 7350 9900 50  0001 C CNN
F 1 "GND" H 7355 9977 50  0001 C CNN
F 2 "" H 7350 10150 50  0001 C CNN
F 3 "" H 7350 10150 50  0001 C CNN
	1    7350 10150
	0    1    1    0   
$EndComp
Wire Wire Line
	7750 10150 7750 10600
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D325B
P 7900 9700
F 0 "Q?" H 8090 9746 50  0000 L CNN
F 1 "2N2222" H 8090 9655 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 8100 9625 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 7900 9700 50  0001 L CNN
	1    7900 9700
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60F05DDD
P 7700 9800
F 0 "#PWR?" H 7700 9550 50  0001 C CNN
F 1 "GND" H 7705 9627 50  0001 C CNN
F 2 "" H 7700 9800 50  0001 C CNN
F 3 "" H 7700 9800 50  0001 C CNN
	1    7700 9800
	0    1    1    0   
$EndComp
Wire Wire Line
	8100 9800 8100 10250
Wire Wire Line
	8100 10250 7800 10250
Wire Wire Line
	7800 10250 7800 10650
Wire Wire Line
	7750 10600 7450 10600
Wire Wire Line
	7450 11050 7150 11050
Wire Wire Line
	7150 11050 7150 11450
Wire Wire Line
	7450 10600 7450 11050
Wire Wire Line
	7800 10650 7500 10650
Wire Wire Line
	7500 10650 7500 11100
Wire Wire Line
	7500 11100 7200 11100
Wire Wire Line
	7200 11100 7200 11500
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D323B
P 8250 9300
F 0 "Q?" H 8440 9346 50  0000 L CNN
F 1 "2N2222" H 8440 9255 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 8450 9225 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 8250 9300 50  0001 L CNN
	1    8250 9300
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60F05DBD
P 8050 9400
F 0 "#PWR?" H 8050 9150 50  0001 C CNN
F 1 "GND" H 8055 9227 50  0001 C CNN
F 2 "" H 8050 9400 50  0001 C CNN
F 3 "" H 8050 9400 50  0001 C CNN
	1    8050 9400
	0    1    1    0   
$EndComp
Wire Wire Line
	8450 9400 8450 9850
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D325D
P 8600 8950
F 0 "Q?" H 8790 8996 50  0000 L CNN
F 1 "2N2222" H 8790 8905 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 8800 8875 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 8600 8950 50  0001 L CNN
	1    8600 8950
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D323D
P 8400 9050
F 0 "#PWR?" H 8400 8800 50  0001 C CNN
F 1 "GND" H 8405 8877 50  0001 C CNN
F 2 "" H 8400 9050 50  0001 C CNN
F 3 "" H 8400 9050 50  0001 C CNN
	1    8400 9050
	0    1    1    0   
$EndComp
Wire Wire Line
	8800 9050 8800 9500
Wire Wire Line
	8800 9500 8500 9500
Wire Wire Line
	8500 9500 8500 9900
$Comp
L 2n2222:2N2222 Q?
U 1 1 60DC9172
P 8950 8550
F 0 "Q?" H 9140 8596 50  0000 L CNN
F 1 "2N2222" H 9140 8505 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 9150 8475 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 8950 8550 50  0001 L CNN
	1    8950 8550
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60DC9173
P 8750 8650
F 0 "#PWR?" H 8750 8400 50  0001 C CNN
F 1 "GND" H 8755 8477 50  0001 C CNN
F 2 "" H 8750 8650 50  0001 C CNN
F 3 "" H 8750 8650 50  0001 C CNN
	1    8750 8650
	0    1    1    0   
$EndComp
Wire Wire Line
	9150 8650 9150 9100
$Comp
L 2n2222:2N2222 Q?
U 1 1 60DC9174
P 9300 8200
F 0 "Q?" H 9490 8246 50  0000 L CNN
F 1 "2N2222" H 9490 8155 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 9500 8125 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 9300 8200 50  0001 L CNN
	1    9300 8200
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60F05DDF
P 9100 8300
F 0 "#PWR?" H 9100 8050 50  0001 C CNN
F 1 "GND" H 9105 8127 50  0001 C CNN
F 2 "" H 9100 8300 50  0001 C CNN
F 3 "" H 9100 8300 50  0001 C CNN
	1    9100 8300
	0    1    1    0   
$EndComp
Wire Wire Line
	9500 8300 9500 8750
Wire Wire Line
	9500 8750 9200 8750
Wire Wire Line
	9200 8750 9200 9150
Wire Wire Line
	9150 9100 8850 9100
Wire Wire Line
	8850 9550 8550 9550
Wire Wire Line
	8550 9550 8550 9950
Wire Wire Line
	8850 9100 8850 9550
Wire Wire Line
	9200 9150 8900 9150
Wire Wire Line
	8900 9150 8900 9600
Wire Wire Line
	8450 9850 8150 9850
Wire Wire Line
	8150 9850 8150 10300
Wire Wire Line
	8150 10300 7850 10300
Wire Wire Line
	7850 10300 7850 10700
Wire Wire Line
	7850 10700 7550 10700
Wire Wire Line
	7550 10700 7550 11150
Wire Wire Line
	7550 11150 7250 11150
Wire Wire Line
	7250 11150 7250 11550
Wire Wire Line
	7600 10750 7900 10750
Wire Wire Line
	7900 10750 7900 10350
Wire Wire Line
	7900 10350 8200 10350
Wire Wire Line
	8200 10350 8200 9900
Wire Wire Line
	8200 9900 8500 9900
Wire Wire Line
	7600 10750 7600 11200
Wire Wire Line
	7600 11200 7300 11200
Wire Wire Line
	7650 11250 7650 10800
Wire Wire Line
	7650 10800 7950 10800
Wire Wire Line
	7950 10800 7950 10400
Wire Wire Line
	7950 10400 8250 10400
Wire Wire Line
	8250 10400 8250 9950
Wire Wire Line
	8250 9950 8550 9950
Wire Wire Line
	8900 9600 8600 9600
Wire Wire Line
	8600 9600 8600 10000
Wire Wire Line
	8600 10000 8300 10000
Wire Wire Line
	8300 10000 8300 10450
Wire Wire Line
	8300 10450 8000 10450
Wire Wire Line
	8000 10450 8000 10850
Wire Wire Line
	8000 10850 7700 10850
Wire Wire Line
	7700 10850 7700 11300
Wire Wire Line
	6400 10500 6100 10500
Wire Wire Line
	6100 10500 6100 11150
Wire Wire Line
	6100 11150 5950 11150
Wire Wire Line
	6050 11200 6150 11200
Wire Wire Line
	6150 11200 6150 10550
Wire Wire Line
	6150 10550 6450 10550
Wire Wire Line
	6150 11250 6200 11250
Wire Wire Line
	6200 11250 6200 10600
Wire Wire Line
	6200 10600 6500 10600
Wire Wire Line
	6500 11150 6500 10650
Wire Wire Line
	6500 10650 6550 10650
Wire Wire Line
	6550 10650 6550 10250
Wire Wire Line
	6550 10250 6850 10250
Wire Wire Line
	6850 10250 6850 9800
Wire Wire Line
	6850 9800 7150 9800
Wire Wire Line
	7150 9800 7150 9400
Wire Wire Line
	7150 9400 7450 9400
Wire Wire Line
	7450 9400 7450 8950
Wire Wire Line
	7450 8950 7750 8950
Wire Wire Line
	7750 8950 7750 8550
Wire Wire Line
	7750 8550 8050 8550
Wire Wire Line
	8050 8550 8050 8100
Wire Wire Line
	8050 8100 8350 8100
Wire Wire Line
	8350 8100 8350 7700
Wire Wire Line
	8350 7700 8650 7700
Wire Wire Line
	8650 7700 8650 4800
Wire Wire Line
	8650 4800 4150 4800
Wire Wire Line
	6850 10600 6850 10300
Wire Wire Line
	6850 10300 6900 10300
Wire Wire Line
	6900 10300 6900 9850
Wire Wire Line
	6900 9850 7200 9850
Wire Wire Line
	7200 9850 7200 9450
Wire Wire Line
	7200 9450 7500 9450
Wire Wire Line
	7500 9450 7500 9000
Wire Wire Line
	7500 9000 7800 9000
Wire Wire Line
	7800 9000 7800 8600
Wire Wire Line
	7800 8600 8100 8600
Wire Wire Line
	8100 8600 8100 8150
Wire Wire Line
	8100 8150 8400 8150
Wire Wire Line
	8400 8150 8400 7750
Wire Wire Line
	8400 7750 8700 7750
Wire Wire Line
	8700 7750 8700 4700
Wire Wire Line
	8700 4700 4150 4700
Wire Wire Line
	7200 10250 7200 9900
Wire Wire Line
	7200 9900 7250 9900
Wire Wire Line
	7250 9900 7250 9500
Wire Wire Line
	7250 9500 7550 9500
Wire Wire Line
	7550 9500 7550 9050
Wire Wire Line
	7550 9050 7850 9050
Wire Wire Line
	7850 9050 7850 8650
Wire Wire Line
	7850 8650 8150 8650
Wire Wire Line
	8150 8650 8150 8200
Wire Wire Line
	8150 8200 8450 8200
Wire Wire Line
	8450 8200 8450 7800
Wire Wire Line
	8450 7800 8750 7800
Wire Wire Line
	8750 7800 8750 4600
Wire Wire Line
	8750 4600 4150 4600
Wire Wire Line
	7550 9850 7550 9550
Wire Wire Line
	7550 9550 7600 9550
Wire Wire Line
	7600 9550 7600 9100
Wire Wire Line
	7600 9100 7900 9100
Wire Wire Line
	7900 9100 7900 8700
Wire Wire Line
	7900 8700 8200 8700
Wire Wire Line
	8200 8700 8200 8250
Wire Wire Line
	8200 8250 8500 8250
Wire Wire Line
	8500 8250 8500 7850
Wire Wire Line
	8500 7850 8800 7850
Wire Wire Line
	8800 7850 8800 4500
Wire Wire Line
	8800 4500 4150 4500
Wire Wire Line
	7900 9500 7900 9150
Wire Wire Line
	7900 9150 7950 9150
Wire Wire Line
	7950 9150 7950 8750
Wire Wire Line
	7950 8750 8250 8750
Wire Wire Line
	8250 8750 8250 8300
Wire Wire Line
	8250 8300 8550 8300
Wire Wire Line
	8550 8300 8550 7900
Wire Wire Line
	8550 7900 8850 7900
Wire Wire Line
	8850 7900 8850 4400
Wire Wire Line
	8850 4400 4150 4400
Wire Wire Line
	8250 9100 8250 8800
Wire Wire Line
	8250 8800 8300 8800
Wire Wire Line
	8300 8800 8300 8350
Wire Wire Line
	8300 8350 8600 8350
Wire Wire Line
	8600 8350 8600 7950
Wire Wire Line
	8600 7950 8900 7950
Wire Wire Line
	8900 7950 8900 4300
Wire Wire Line
	8900 4300 4150 4300
Wire Wire Line
	8600 8750 8600 8400
Wire Wire Line
	8600 8400 8650 8400
Wire Wire Line
	8650 8400 8650 8000
Wire Wire Line
	8650 8000 8950 8000
Wire Wire Line
	8950 8000 8950 4200
Wire Wire Line
	8950 4200 4150 4200
Wire Wire Line
	8950 8350 8950 8050
Wire Wire Line
	8950 8050 9000 8050
Wire Wire Line
	9000 8050 9000 4100
Wire Wire Line
	9000 4100 4150 4100
Wire Wire Line
	9300 8000 9050 8000
Wire Wire Line
	9050 8000 9050 4000
Wire Wire Line
	9050 4000 4150 4000
Wire Wire Line
	6700 11450 6700 11950
Wire Wire Line
	6700 11950 6250 11950
Wire Wire Line
	6350 12000 6750 12000
Wire Wire Line
	6750 12000 6750 11350
Wire Wire Line
	6750 11350 7050 11350
Wire Wire Line
	6800 11400 6800 12050
Wire Wire Line
	6800 12050 6450 12050
Wire Wire Line
	6800 11400 7100 11400
Wire Wire Line
	6550 12100 6850 12100
Wire Wire Line
	6850 12100 6850 11450
Wire Wire Line
	6850 11450 7150 11450
Wire Wire Line
	6900 11500 6900 12150
Wire Wire Line
	6900 12150 6650 12150
Wire Wire Line
	6900 11500 7200 11500
Wire Wire Line
	6750 12200 6950 12200
Wire Wire Line
	6950 12200 6950 11550
Wire Wire Line
	6950 11550 7250 11550
Wire Wire Line
	7300 11200 7300 11600
Wire Wire Line
	7300 11600 7000 11600
Wire Wire Line
	7000 11600 7000 12250
Wire Wire Line
	7000 12250 6850 12250
Wire Wire Line
	6950 12300 7050 12300
Wire Wire Line
	7050 12300 7050 11650
Wire Wire Line
	7050 11650 7350 11650
Wire Wire Line
	7350 11650 7350 11250
Wire Wire Line
	7350 11250 7650 11250
Wire Wire Line
	7400 11300 7400 11700
Wire Wire Line
	7400 11700 7100 11700
Wire Wire Line
	7400 11300 7700 11300
Wire Wire Line
	7100 11700 7100 12350
Wire Wire Line
	7100 12350 7050 12350
$Comp
L 2n2222:2N2222 Q?
U 1 1 60DC9175
P 7400 12350
F 0 "Q?" H 7590 12396 50  0000 L CNN
F 1 "2N2222" H 7590 12305 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7600 12275 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 7400 12350 50  0001 L CNN
	1    7400 12350
	0    1    1    0   
$EndComp
Wire Wire Line
	7600 12450 7600 12900
$Comp
L power:GND #PWR?
U 1 1 60F05DE1
P 7550 12050
F 0 "#PWR?" H 7550 11800 50  0001 C CNN
F 1 "GND" H 7555 11877 50  0001 C CNN
F 2 "" H 7550 12050 50  0001 C CNN
F 3 "" H 7550 12050 50  0001 C CNN
	1    7550 12050
	0    1    1    0   
$EndComp
Wire Wire Line
	7950 12050 7950 12500
$Comp
L 2n2222:2N2222 Q?
U 1 1 5F4EA809
P 8100 11600
F 0 "Q?" H 8290 11646 50  0000 L CNN
F 1 "2N2222" H 8290 11555 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 8300 11525 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 8100 11600 50  0001 L CNN
	1    8100 11600
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3243
P 7900 11700
F 0 "#PWR?" H 7900 11450 50  0001 C CNN
F 1 "GND" H 7905 11527 50  0001 C CNN
F 2 "" H 7900 11700 50  0001 C CNN
F 3 "" H 7900 11700 50  0001 C CNN
	1    7900 11700
	0    1    1    0   
$EndComp
Wire Wire Line
	8300 11700 8300 12150
Wire Wire Line
	8300 12150 8000 12150
Wire Wire Line
	8000 12150 8000 12550
$Comp
L 2n2222:2N2222 Q?
U 1 1 60DC9178
P 8450 11200
F 0 "Q?" H 8640 11246 50  0000 L CNN
F 1 "2N2222" H 8640 11155 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 8650 11125 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 8450 11200 50  0001 L CNN
	1    8450 11200
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60F05DE2
P 8250 11300
F 0 "#PWR?" H 8250 11050 50  0001 C CNN
F 1 "GND" H 8255 11127 50  0001 C CNN
F 2 "" H 8250 11300 50  0001 C CNN
F 3 "" H 8250 11300 50  0001 C CNN
	1    8250 11300
	0    1    1    0   
$EndComp
Wire Wire Line
	8650 11300 8650 11750
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D3245
P 8800 10850
F 0 "Q?" H 8990 10896 50  0000 L CNN
F 1 "2N2222" H 8990 10805 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 9000 10775 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 8800 10850 50  0001 L CNN
	1    8800 10850
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 60DC9196
P 8600 10950
F 0 "#PWR?" H 8600 10700 50  0001 C CNN
F 1 "GND" H 8605 10777 50  0001 C CNN
F 2 "" H 8600 10950 50  0001 C CNN
F 3 "" H 8600 10950 50  0001 C CNN
	1    8600 10950
	0    1    1    0   
$EndComp
Wire Wire Line
	9000 10950 9000 11400
Wire Wire Line
	9000 11400 8700 11400
Wire Wire Line
	8700 11400 8700 11800
Wire Wire Line
	8650 11750 8350 11750
Wire Wire Line
	8350 12200 8050 12200
Wire Wire Line
	8050 12200 8050 12600
Wire Wire Line
	8350 11750 8350 12200
Wire Wire Line
	8700 11800 8400 11800
Wire Wire Line
	8400 11800 8400 12250
Wire Wire Line
	7950 12500 7650 12500
Wire Wire Line
	7650 12500 7650 12950
Wire Wire Line
	7700 13000 7700 12550
Wire Wire Line
	7700 12550 8000 12550
Wire Wire Line
	7750 13050 7750 12600
Wire Wire Line
	7750 12600 8050 12600
Wire Wire Line
	8400 12250 8100 12250
Wire Wire Line
	8100 12250 8100 12650
$Comp
L 2n2222:2N2222 Q?
U 1 1 606D325F
P 7750 11950
F 0 "Q?" H 7940 11996 50  0000 L CNN
F 1 "2N2222" H 7940 11905 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 7950 11875 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 7750 11950 50  0001 L CNN
	1    7750 11950
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR?
U 1 1 606D3263
P 7200 12450
F 0 "#PWR?" H 7200 12200 50  0001 C CNN
F 1 "GND" H 7205 12277 50  0001 C CNN
F 2 "" H 7200 12450 50  0001 C CNN
F 3 "" H 7200 12450 50  0001 C CNN
	1    7200 12450
	0    1    1    0   
$EndComp
Wire Wire Line
	7600 12900 7150 12900
Wire Wire Line
	7250 12950 7650 12950
Wire Wire Line
	7700 13000 7350 13000
Wire Wire Line
	7450 13050 7750 13050
Wire Wire Line
	8100 12650 7800 12650
Wire Wire Line
	7800 12650 7800 13100
Wire Wire Line
	7800 13100 7550 13100
Wire Wire Line
	7400 12150 7400 11750
Wire Wire Line
	7400 11750 7450 11750
Wire Wire Line
	7450 11750 7450 11350
Wire Wire Line
	7450 11350 7750 11350
Wire Wire Line
	7750 11350 7750 10900
Wire Wire Line
	7750 10900 8050 10900
Wire Wire Line
	8050 10900 8050 10500
Wire Wire Line
	8050 10500 8350 10500
Wire Wire Line
	8350 10500 8350 10050
Wire Wire Line
	8350 10050 8650 10050
Wire Wire Line
	8650 10050 8650 9650
Wire Wire Line
	8650 9650 8950 9650
Wire Wire Line
	8950 9650 8950 9200
Wire Wire Line
	8950 9200 9250 9200
Wire Wire Line
	9250 9200 9250 8800
Wire Wire Line
	9250 8800 9550 8800
Wire Wire Line
	9550 3900 4150 3900
Wire Wire Line
	9550 3900 9550 8800
Wire Wire Line
	4150 3800 9600 3800
Wire Wire Line
	9600 3800 9600 8850
Wire Wire Line
	9600 8850 9300 8850
Wire Wire Line
	9300 8850 9300 9250
Wire Wire Line
	9300 9250 9000 9250
Wire Wire Line
	9000 9250 9000 9700
Wire Wire Line
	9000 9700 8700 9700
Wire Wire Line
	8700 9700 8700 10100
Wire Wire Line
	8700 10100 8400 10100
Wire Wire Line
	8400 10100 8400 10550
Wire Wire Line
	8400 10550 8100 10550
Wire Wire Line
	8100 10550 8100 10950
Wire Wire Line
	8100 10950 7800 10950
Wire Wire Line
	7800 11400 7750 11400
Wire Wire Line
	7750 11400 7750 11750
Wire Wire Line
	7800 10950 7800 11400
Wire Wire Line
	8100 11400 8100 11000
Wire Wire Line
	8100 11000 8150 11000
Wire Wire Line
	8150 11000 8150 10600
Wire Wire Line
	8150 10600 8450 10600
Wire Wire Line
	8450 10600 8450 10150
Wire Wire Line
	8450 10150 8750 10150
Wire Wire Line
	8750 10150 8750 9750
Wire Wire Line
	8750 9750 9050 9750
Wire Wire Line
	9050 9750 9050 9300
Wire Wire Line
	9050 9300 9350 9300
Wire Wire Line
	9350 9300 9350 8900
Wire Wire Line
	9350 8900 9650 8900
Wire Wire Line
	9650 3700 4150 3700
Wire Wire Line
	9650 3700 9650 8900
Wire Wire Line
	4150 3600 9700 3600
Wire Wire Line
	9700 3600 9700 8950
Wire Wire Line
	9700 8950 9400 8950
Wire Wire Line
	9400 8950 9400 9350
Wire Wire Line
	9400 9350 9100 9350
Wire Wire Line
	9100 9350 9100 9800
Wire Wire Line
	9100 9800 8800 9800
Wire Wire Line
	8800 9800 8800 10200
Wire Wire Line
	8800 10200 8500 10200
Wire Wire Line
	8500 10200 8500 10650
Wire Wire Line
	8500 10650 8450 10650
Wire Wire Line
	8450 10650 8450 11000
Wire Wire Line
	8800 10650 8800 10250
Wire Wire Line
	8800 10250 8850 10250
Wire Wire Line
	8850 10250 8850 9850
Wire Wire Line
	8850 9850 9150 9850
Wire Wire Line
	9150 9850 9150 9400
Wire Wire Line
	9150 9400 9450 9400
Wire Wire Line
	9450 9400 9450 9000
Wire Wire Line
	9450 9000 9750 9000
Wire Wire Line
	9750 9000 9750 3500
Wire Wire Line
	9750 3500 4150 3500
$Comp
L Device:R R?
U 1 1 7085AB6C
P 3300 2450
F 0 "R?" V 3093 2450 50  0000 C CNN
F 1 "1K" V 3184 2450 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" V 3230 2450 50  0001 C CNN
F 3 "~" H 3300 2450 50  0001 C CNN
	1    3300 2450
	-1   0    0    1   
$EndComp
Wire Wire Line
	3300 2600 3300 3500
Connection ~ 3300 3500
Wire Wire Line
	2650 1550 2650 1650
Wire Wire Line
	2650 2800 2650 2700
Wire Wire Line
	2650 2400 2650 2200
Wire Wire Line
	2650 2200 3300 2200
Wire Wire Line
	3300 2200 3300 2300
Connection ~ 2650 2200
Wire Wire Line
	2650 2200 2650 2050
Wire Wire Line
	4450 9900 4450 14900
Wire Wire Line
	4550 9800 4550 14900
Wire Wire Line
	4650 9850 4650 14900
Wire Wire Line
	4750 9900 4750 14900
Wire Wire Line
	4850 9950 4850 14900
Wire Wire Line
	4950 10000 4950 14900
Wire Wire Line
	5050 9650 5050 14900
Wire Wire Line
	5150 9700 5150 14900
Wire Wire Line
	5250 9750 5250 14900
Wire Wire Line
	5350 10850 5350 14900
Wire Wire Line
	5450 10900 5450 14900
Wire Wire Line
	5550 10950 5550 14900
Wire Wire Line
	5650 11000 5650 14900
Wire Wire Line
	5750 11050 5750 14900
Wire Wire Line
	5850 11100 5850 14900
Wire Wire Line
	5950 11150 5950 14900
Wire Wire Line
	6050 11200 6050 14900
Wire Wire Line
	6150 11250 6150 14900
Wire Wire Line
	6250 11950 6250 14900
Wire Wire Line
	6350 12000 6350 14900
Wire Wire Line
	6450 12050 6450 14900
Wire Wire Line
	6550 12100 6550 14900
Wire Wire Line
	6650 12150 6650 14900
Wire Wire Line
	6750 12200 6750 14900
Wire Wire Line
	6850 12250 6850 14900
Wire Wire Line
	6950 12300 6950 14900
Wire Wire Line
	7050 12350 7050 14900
Wire Wire Line
	7150 12900 7150 14900
Wire Wire Line
	7250 12950 7250 14900
Wire Wire Line
	7350 13000 7350 14900
Wire Wire Line
	7450 13050 7450 14900
Wire Wire Line
	7550 13100 7550 14900
Text HLabel 7250 14900 3    50   BiDi ~ 0
D3
Text HLabel 7350 14900 3    50   BiDi ~ 0
D2
Text HLabel 7450 14900 3    50   BiDi ~ 0
D1
Text HLabel 7550 14900 3    50   BiDi ~ 0
D0
Text HLabel 6850 14900 3    50   BiDi ~ 0
D7
Text HLabel 6950 14900 3    50   BiDi ~ 0
D6
Text HLabel 7050 14900 3    50   BiDi ~ 0
D5
Text HLabel 7150 14900 3    50   BiDi ~ 0
D4
Text HLabel 6450 14900 3    50   BiDi ~ 0
D11
Text HLabel 6550 14900 3    50   BiDi ~ 0
D10
Text HLabel 6650 14900 3    50   BiDi ~ 0
D9
Text HLabel 6750 14900 3    50   BiDi ~ 0
D8
Text HLabel 6050 14900 3    50   BiDi ~ 0
D15
Text HLabel 6150 14900 3    50   BiDi ~ 0
D14
Text HLabel 6250 14900 3    50   BiDi ~ 0
D13
Text HLabel 6350 14900 3    50   BiDi ~ 0
D12
Text HLabel 5650 14900 3    50   BiDi ~ 0
D19
Text HLabel 5750 14900 3    50   BiDi ~ 0
D18
Text HLabel 5850 14900 3    50   BiDi ~ 0
D17
Text HLabel 5950 14900 3    50   BiDi ~ 0
D16
Text HLabel 5250 14900 3    50   BiDi ~ 0
D23
Text HLabel 5350 14900 3    50   BiDi ~ 0
D22
Text HLabel 5450 14900 3    50   BiDi ~ 0
D21
Text HLabel 5550 14900 3    50   BiDi ~ 0
D20
Text HLabel 4850 14900 3    50   BiDi ~ 0
D27
Text HLabel 4950 14900 3    50   BiDi ~ 0
D26
Text HLabel 5050 14900 3    50   BiDi ~ 0
D25
Text HLabel 5150 14900 3    50   BiDi ~ 0
D24
Text HLabel 4450 14900 3    50   BiDi ~ 0
D31
Text HLabel 4550 14900 3    50   BiDi ~ 0
D30
Text HLabel 4650 14900 3    50   BiDi ~ 0
D29
Text HLabel 4750 14900 3    50   BiDi ~ 0
D28
Text HLabel 1400 1850 0    50   Input ~ 0
EN
$EndSCHEMATC
