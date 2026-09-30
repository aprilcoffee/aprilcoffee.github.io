本篇來寫寫當初在月津港(現在在台北數位藝術中心展覽的數位藝術家)很猛的架結構的林瑜亮、跟負責電路板製作焊接(月薪很高小公主)李翎暄跟很廢的我，含辛茹苦的花了18萬的裝置。如何Hardcore的使用python GPIO功能控制移位暫存器，python GPIO的code部分就不多做說明，可以看前面幾篇文章轉換成Arduino，然後這篇也會稍微解釋Latch, Clock, Data三個名稱，以及很簡單很簡單的在這邊使用位元運算。我很廢在此拋磚引玉，還請大大指正。

適用晶片是TPIC6C594，還有74HC595或各種場合燈節超級萬用的燈條WS2812也可以使用同樣方式(還有還有其他的移位暫存器晶片，例如可以控制16個輸出的STP16C596，只是我沒用過不多說)

(這篇先私心問一下 Wix SEO有沒有有經驗的人會用ＱＱ 我發現在wix寫的blog，google都搜不到)

[https://www.liutingchun.com/segmentary-moonlight](https://www.liutingchun.com/segmentary-moonlight)

![](images/wix/4eb1dd_3386eacc14aa498a9cba779f92284edc~mv2_d_4032_3024_s_4_2.webp)

直接控制移位暫存器的好處，是如果沒有適當library(如Arduino的FastLED或Adafruit_NeoPixel)才需要使用。另外如果使用arduino firmata的話也可以用這種方式控制。就可以直接在processing呼叫arduino使用ws2812做mapping唷～～

TPIC6C594非常類似74HC595，只是當需要驅動LED的電壓高於5V，就可以使用這片晶片。邏輯電路的部分我就跳過啦(因為我也看不懂)，直接說明code的部分。因為TPIC6C594非常類似74HC595除了可以供更高壓的電流外，我也忘記差別，希望大大指證，所以下面就以74HC595代稱並說明。使用74HC595這種晶片，可以簡單的使用3個pin腳便可以控制八個燈光/元件，當然進行串聯之後便可以控制更多的元件。

### Pin腳們的說明

![](images/wix/4eb1dd_7b25c618bce2424999bbc24786271a16~mv2.webp)

74HC595基本上上頭有16個腳位，分別是DS、SH_CP、ST_CP、Q0-Q7、Q7' ，還有 VCC、GND、OE跟MR。

DS是Serial data input，就是負責給予Data的腳位。

SH_CP是Shift register clock pin，也就是Clock Pin。

ST_CP是Storage register clock pin，作為Latch Pin。

基本上只要使用這三個pin腳，便可以操作七個以上的燈點～～

Q0-Q7是變成接上需要控制的燈或是七段顯示器的八個燈點(包含小數點的小燈)，Q7' 可以作為串接的pin腳，後面再作說明。

VCC跟GND，恩.....就是VCC跟GND，請接到供電跟接地的地方。

OE是Output Enable，設成低電位時，便可以允許訊號輸出，在連接七段顯示器時，直接與GND即可。

MR是指Master Reset，設為低電位時，會清除暫存器中所有資料。暫時不會用到，放旁邊。

串連多個74HC595的方式，便是把Q7' 接到 下一個74HC595的DSpin腳，然後並聯SH_CP, ST_CP兩個pin腳。就可以多個輸出囉～～(記得下一顆七段顯示器的GND也要併聯近前一顆的GND喔)

### 74HC595初始化的部分

Arduino有個函式叫**shiftOut(dataPin, clockPin, MSBFIRST, low_Byte);**，可以很快地做好這件事，只要開關latch就好，方便快速，但小弟白痴沒用過就跳過不說明，如果想要快速的arduino code，後面我會補上，這邊直接進python的code。

如果只有使用單顆的74HC595，控制的方法就十分簡單。

首先我們先initialize所有的pin腳。

```
segmentLatch = 23
segmentClock = 24
segmentData = 25
```

將所有想要輸出的數字做編號以及建成變數，基本上七段顯示器每顆燈的編號如下。

![](images/wix/4eb1dd_ec30c34a1b724964b37876e9fda6c675~mv2.webp)

我們可以看到對應的英文，便可以由此建立變數。為了方便我們使用移位暫存器時同時將一卡車位元(一顆七段顯示)送進去，我們要將這些英文對應成正確的位元組。

舉例來說數字1便是B+C，數字7便是A+B+C

```
a = 1 << 0
b = 1 << 6
c = 1 << 5
d = 1 << 4
e = 1 << 3
f = 1 << 1
g = 1 << 2
dp = 1 << 7
```

「<<」是位元運算中推一個位元的意思。<<6則是推6個位元，天呀我不知道這篇怎麼解釋又懶得畫圖。

舉例來說假使這邊有個位元組

00000000

當我寫下 1 << 2 時便會將1(正)推兩個位元，就成了

00000100

之後我們需要用到「且」這個運算子(|)，來組合我們得到的位置。

```
segments = 0 //首先建立segment變數來儲存要送的data
if number == 1:
        segments = b | c
elif number == 2:
        segments = a | b | d | e | g
elif number == 3:
        segments = a | b | c | d | g
elif number == 4:
        segments = f | g | b | c
elif number == 5:
        segments = a | f | g | c | d
elif number == 6:
        segments = a | f | g | e | c | d
elif number == 7:
        segments = a | b | c
elif number == 8:
        segments = a | b | c | d | e | f | g
elif number == 9:
        segments = a | b | c | d | f | g
elif number == 0:
        segments = a | b | c | d | e | f
else:
        segments = 0
```

且的運算組，可以將兩個位元作且運算，下面附圖表ＸＤＤＤ

![](images/wix/4eb1dd_673f21f2538a4640991d535f8ae83696~mv2.gif)

舉例來說：

a(1<<0) 在我們剛剛的data assignment之後，視為00000001

b(1<<6) 在剛剛建立成01000000，c(1<<5))在剛剛建立成00100000

當我們把a,b,c三個組合做了且運算，便是以下運作邏輯

```
00000001 |
01000000 |
00100000 |
----------------
01100001
```

對於七段顯示器而言，1便是所有要亮的點，0便是不亮的，我們便會形成數字「7」

以此方式我們便建議好了各種輸入方法的變數，當然也可以以個人使用自行斟酌～～～

### 開始輸出資料進去

開始輸出時，我們先latch拉至低電位，便可以送data進去，再把latch設為高電位關起來～～

而每一次送出一個位元時，我們必須把clock設為低電位初始化，送一個值，再把clock設為高電位。把這個值往前推一個位元。

Latch在此指的是便是整個晶片接收資料的開關。

Clock則是每一次設置為高電位時，便會推送一個值到下一個位元，以此來說，當我串接一大堆的74HC595我便可以不斷開關clock把所有數字一直一直推送到下一個暫存器。

```
GPIO.output(segmentLatch, GPIO.LOW)
n = 0
while n < 8:
        GPIO.output(segmentclock, GPIO.LOW)
        GPIO.output(segmentdata, segments & 1 << (7 - n))
        GPIO.output(segmentclock, GPIO.HIGH)
        n += 1
GPIO.output(segmentLatch, GPIO.LOW)
```

這邊的解釋有點玄，我們就先以「7」這個數字(01100001)來說明

首先設計 n = 0 初始化

跑一個當n不小於8時會停止的回圈每次不段開關clock

segments & 1 << (7-n)這個運算式，便是一次一次把下一個數字送去data

這邊有個且運作子(&)，便是做且運算，我們一樣附圖耶～

![](images/wix/4eb1dd_51a5ae2a3d8e4172a5d05e3959d04ec8~mv2.gif)

剛開始 segments 為 01100001

第一次跑回圈時n==0，我們便會將1 << (7-0)，得位元組為10000000

```
01100001 &
10000000
-----------------
00000000
```

便是我們送進去的第一組資料

第二個數字為n==1 我們便會將 1 << 6，得位元組01000000做且運算

```
01100001 &
01000000
-----------------
01000000
```

便是我們送的第二組資料。

如此一來，我們便可以送入這些資料之後迴圈變會結束。

```
00000000
01000000
00100000
00000000
00000000
00000000
00000000
00000001
```

而七段顯示器便會得到這串數字 01100001 視為 「7」

如此一來，我們便可以寫出很快速的一套function來負責解釋我要送的數字。

而當我們需要串接更多的數字時，我只需要不斷的呼叫這套函式，他便會送入不同的74HC595當中。每次呼叫時便會完成一顆七段顯示器的顯示。

附上當時的code，寫了一些函式來執行不同的效果，包含當我收到數字10的時候，會跑隨機的效果等等

[https://github.com/aprilcoffee/SegmentaryMoonlight/blob/master/source/mu.py](https://github.com/aprilcoffee/SegmentaryMoonlight/blob/master/source/mu.py)

附個很隨便的影片

https://vimeo.com/324791977

(紅色小光段版本是用Arduino Mega硬幹的，因為很酷所以想放一下，但是code完全不一樣)

![](images/wix/4eb1dd_6f5c193c2808446bb77995688f32161b~mv2_d_3888_2592_s_4_2.webp)

![](images/wix/4eb1dd_8f2574ee3a384d79a224cb20f25692a2~mv2.webp)
