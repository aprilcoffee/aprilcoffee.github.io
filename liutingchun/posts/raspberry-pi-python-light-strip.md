這篇貼文想簡單分享一些如何使用python操作彩色LED燈條，如何安裝相關套件跟一些使用規格。原理其實跟使用Arduino搭配NeoPixel或FastLED這兩款套件相同，只是在這邊語法上會使用Raspberry Pi的GPIO與Python。如果對寫程式比較棘手，也推薦直接購買LED燈條控制器 (如 T500K) 搭配適當的軟體 (LEDEdit)，就可以直接將影片map成燈光。因為發現自己始終沒有整理好的檔案，所以決定順手寫一下部落格來做個資料的整理。

使用python的好處是，當進行與其他軟體的互動或通訊時，相容性會高很多。遠端操作上也可以直接使用[OSC進行通訊](https://www.liutingchun.com/post/raspberrypi-python-osc)，或是Websocket等等各種協定。對於只會撰寫python的朋友也會容易許多。

市面上大部分的單顆可控制燈條，主要的型號分為SK系列與WS281x系列。值得注意的是WS系列雖然並不是指燈本身，而且其控制晶片的名稱。LED燈泡本身還是使用5050規格。購買LED時也可以注意購買燈泡的密度，大致上分為幾種規格，**每一公尺內含30, 60, 144顆燈泡**，也有的燈條控制單元是以**三顆燈泡為一個單位控制**，並不是每顆燈泡都可以獨立操作。

這邊也稍微整理一下幾種常見型號，給大家看看各個型號的差異，在需要購買時以供參考。

細節的規格上還是有很多差異，如果有需求也可以直接去查規格書

![](images/wix/4eb1dd_ed5d093e03034228a59a3677701cc3a9~mv2.webp)

大致的規格解說完，我們就可以開工寫python了。

我們這邊使用NeoPixel的library在這邊使用的語言是python3，舊版python2的library已經下架，為大家方便在這都以python3為主。

新版Raspberry Pi OS 預設的python依舊是2.7，如果在寫執行時覺得麻煩，可以用一行指令來將python指令轉換為直接使用python3。

```
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10
```

首先打開terminal，輸入以下兩行指令來安裝對應的library

```
pip3 install rpi_ws281x adafruit-circuitpython-neopixel
python3 -m pip install --force-reinstall adafruit-blinka
```

注意是如果已經執行剛剛的指令就可以**直接使用pip代替pip3，python代替python3**

\*\*\*\*\*\*\*注意\*\*\*\*\*\*\*

更新後的adafruit library，一般來說，需要使用root來操作(sudo)

舉例來說檔案為 **light.py** 就必須要用 **sudo python light.py** 來呼叫

作為訊號的pin腳，只能使用D10, D12, D18, D21

![](images/wix/4eb1dd_cd37178f863947ae97f99b116415029c~mv2.webp)

而有個**繞過這項規則的方法**，就是直接使用SPI pin腳

這邊要做的事情便是更改系統設定來開啟SPI使用

```
sudo raspi-config
```

在**Interface -> SPI -> YES** 開啟SPI設定 就可以利用SPI的pin腳例如 D10。

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

完成之後我們便可以進入python編輯了。開啟自己習慣的編輯方法，或是直接在terminal用vim開啟檔案。Vim的使用方式在前面部落格已經提過，這邊就不再贅述。

當然Raspberry Pi內建的Thonny Python IDE也是個不錯的選擇。

首先我們需要import對應的資料庫。

```
import board
import neopixel
```

接著初始化pixels這個變數，來操作燈條。

```
length = 30
pixels = neopixel.NeoPixel(board.D10, length, brightness=0.8, auto_write=False,pixel_order=neopixel.RGB)
```

這邊可以稍微解釋一下各個argument。

**使用pin腳：board.D10** (規格是以board為原則，參照上面GPIO表)

**控制燈數：length** (是使用我們剛剛預設的變數 length，來存取燈數)

**亮度：brightness=0.8** (以0~1控制總亮度，在供電不足時十分方便)

**自動上傳：auto_write=False** (這部分等等會再說明，與運算效率有很大關係)

**色彩編碼：pixel_order=neopixel.RGB** (預設並不是習慣的RGB，建議更改一下)

接著我們先試著點亮他，fill會讓整條燈條都填滿紅色

```
pixels.fill(255,0,0)
pixels.show()
```

這邊會發現 pixels.show() 這個函式，可以講回前面提到**auto_write**這件事

當我們把auto_write設成true，每一次更動燈條顏色，他便會直接輸出這個訊號給燈條。

在工作上確實會方便，但當我們要個別操作每一顆個別燈條時，運算效能便會很差。

設定成false時，我們設定完每一顆個別的燈，之後一次輸出，會節省很多效能浪費。

剛剛我們學會 pixels.fill()

至於單顆燈的操作也很簡單，直接指定pixels陣列的index

```
pixels[29] = (255,0,0)
```

這樣第30顆 (陣列從0開始) 燈，便會亮出紅色。

接下來我們來試做流水燈效果吧，這份範本很簡單，也會有很多不同的細節可以做修改。

```
from numpy import interp
import time

counter = 0

#初始化燈條陣列回黑色
for i in range(length):
    pixels[i] = (0,0,0)

while True:
    counter += 1
    counter %= length
    light_range = int(length/3)
    
    #先預設所有燈為黑色
    for i in range(length):
        pixels[i]=(0,0,0)
    
    #跑三分之一長的燈 設定顏色
    for i in range(light_range):
        c = int(interp(i,[0,light_range],[0,255]))
        if(counter-i)<0:
            break
        pixels[counter-i] = (c,c,c)

    pixels.show()
    time.sleep(0.005)
```

稍微說明一下幾個函式

**interp()** 是在numpy裡頭的function，用法與processing或arduino的map類似

我們在這邊把 i的範圍，拓展成0~255，符合RGB的設定

另外最後的 **time.sleep(0.005)** 則是設定每次while重複的頻率。

當我們可以操作單顆燈時，變化便可以自己設定。

祝大家玩得愉快
