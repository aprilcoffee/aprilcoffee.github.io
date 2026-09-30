這篇來談談近期如何使用 Raspberry Pi 進行互動的影片切換播放。一些用詞上如果有錯誤還請閱讀的大大見諒，並留言幫助我提出修正以分享正確資訊給更多朋友。另外附上上次忘記提及的小小功能，Raspberry Pi最討人厭的小閃電符號移除。

這篇文主要談談如何使用 Raspberry Pi 透過 python 來進行電子控制，以及影片播放，關於馬達運作以及GPIO輸出的部分會先跳過，主要講input，開發環境在Python 2.7 上，都是內建在RPi裏頭，我習慣的撰寫方式是使用vim，然後利用python的GPIO library進行互動的部分。透過subprocess的方式，開啟omxplayer來播放全螢幕影片。最初建立這樣的架構時是使用在[林瑜亮的作品](https://gunter292.wixsite.com/gunter/copy-of-moonlight-segment)上，為了方便展出不使用電腦，便利用Raspberry Pi 同時當播放器與互動的控制。作品運作技術大致上來說，便是有兩段不同的跑步小人動畫，以投影機放在線性馬達的方式隨著投影機移動，每當線性馬達抵達其中一端(以微動開關觸發)便會觸發馬達往另一個方向移動，並且切換影片，千言萬語無法形容作品，瑜亮下個月會在台北數位藝術中心展出，可以直接去看作品 <3

![](images/wix/4eb1dd_3f8ef3988dba403bb7850d50376fe759~mv2_d_2448_3264_s_4_2.webp)

一般會談到為什麼不使用Processing或Arduino來進行簡單的互動prototype，主要的原因在於Processing在Raspberry Pi上必須使用「GL Video」這套Library來跑影片，然而執行效率實在堪憂，為了給自己一點挑戰，便嘗試把互動的部分組合影像。並使用omxplayer來代理processing播放影片的角色。

看過前篇的朋友應該已經做完了setup但是這邊再重複一次。在Raspberry Pi的terminal上，記得要先安裝以下套件來播放影音檔

```
sudo apt-get install omxplayer
```

當時基本的code都有放在github上頭：

https://github.com/aprilcoffee/autoVideoplayOnRaspberryPi

這邊就來稍微談一下如合撰寫簡單的GPIO程式，基本上會稍作與Arduino在撰寫習慣上的不同。使用的範例是之前瑜亮的作品的部分，**控制馬達移動的同時，在觸碰到兩個不同的微動開關會進行影片切換。**

在Arduino上，基本必須在 setup() 做初始化 (initialize) 後，在 loop()中撰寫執行內容。一般來說，製作互動影片不管觸發的感測器是什麼，通常是loop()中讀取感測器之後，以Serialport的方式送至processing去切換影片。本篇文主要有兩段撰寫需要做說明，一段為如何使用python的GPIO library進行電子控制，和如何以python播放影片。

![](images/wix/4eb1dd_08964e75f0bf41eab840a367f9ab39e3~mv2.webp)

在了解Processing與Arduino播放方式之後，我們進入基礎的GPIO撰寫。

首先必須透過terminal在執行檔案的資料夾去新增一個python檔案。

```
vim videoplayer.py
```

python的編寫方法並不使用大括號來分層，全部使用縮排的方式(tab)來表達層級。

一開始時我們需要先呼叫幾個基本的函式庫來進行運作GPIO以及影片播放。

```
import RPi.GPIO as GPIO
import time, os, signal, sys
import subprocess
import multiprocessing
```

這幾行除了呼叫GPIO之外，我使用subprocess的方式去開啟影片。

首先必須先初始化GPIO的模式以及宣告pin。

GPIO有兩種模式：

```
GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
```

這兩種不同模式的差異在，BOARD是以排插對應的編號，而BCM是系統排的GPIO編號，我習慣使用BCM原因在於我不會誤用到5V GND等等錯誤的位置。在此附上編號的排序圖(Raspberry Pi 3適用)。中間的那排數字代表使用BOARD模式時對應的號碼。

![](images/wix/4eb1dd_ed6893fb609f4325841d16a9047edaae~mv2.webp)

接著便是宣告按鈕變數(或感測器位置)，以及宣告幾個數字用來存取感測器讀取到的值，這幾行的用意與Arduino中使用以下用法相同。

```
int l_btn = 0;
int r_btn = 0;
pinMode(23,INPUT_PULLUP);
pinMode(24,INPUT_PULLUP);
```

```
l_btn = 0
r_btn = 0
GPIO.setup(23,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(24,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
```

可以發現宣告變數的部分，python並不需要事前做型別的宣告，不用在告知變數視為int或char，直接assignment的值為初始化的型別。

而因為python中沒有loop()這樣的結構，在運算的部分，我們需要使用一個 while True: 來包著所有執行序，在期間會不停的執行。因為這次設計的結構是兩支影片在觸碰不同的開關後會切換，我需要以兩個不同的函式來包含這樣的行為。def在python的語法中為宣告函式的意思。簡而言之這樣的寫法在arduino中便是如此：

```
void goright(){
         r_btn = digitalRead(23);
         delay(0.1)
                   if(r_btn==0){
                   r_btn = digitalRead(23);
                   }
}
```

```
def goright():
          r_btn = GPIO.input(23)
          time.sleep(0.1)
          while (r_btn==0):
                    r_btn = GPIO.input(23)

def goleft():
           l_btn = GPIO.input(24)
           time.sleep(0.1)
           while (l_btn==0):
                     l_btn = GPIO.input(23)
```

因為裝置本身是一來一往，我便只要輪流呼叫不同的函式便可以知道目前應該前進的方向。

附帶一提在這邊有做GPIO.input的範例，要做output的話也十分簡單，以下便可以執行high,low等輸出

```
GPIO.output(7,GPIO.HIGH)
GPIO.output(8,GPIO.LOW)
```

當我有了兩個不同的函式，我便需要在python中撰寫需要的loop()來確保程式不斷運作。**在goright函式中，偵測開關會不斷運算，當開關不等於0時便會跳出。因此才會是在goright()之後播放往左影片。**

```
播放往右影片 //剛開始便播放
while True:
           goright()
           播放往左影片
           goleft()
           播放往右影片
```

接著來談談影片播放的部分

使用RaspberryPi與Arduino最大的不同，在於Arduino運算上是為單執行緒，而RPi可以進行多執行序的運算。多執行緒(multithreading)做個簡單的舉例，便是像我們的手機電腦可以同時進行多件事情，例如我們可以同時在電腦上編寫這篇，一邊開著spotify放自己的音樂，兩件事情電腦是可以同時運作。Raspberry Pi基本上可以做到一樣的事，因此我們可以讓他在控制互動的同時播放影片。但在這邊我們需要引入python的函式庫subprocess來做到這件事，讓執行python時，可以開啟另一條thread播放影片。

回到python的部分，我是以一行程式來播放影片的

```
proc1 = subprocess.Popen(args=['omxplayer','--no-osd','--loop','-b','--aspect-mode','fill','right.mp4'])
```

以及兩行程式來做關閉影片的動作

```
subprocess.call(['pkill','-P',str(proc1.pid)])
proc1.kill()
```

這邊稍微幫這幾行做個拆解說明

```
proc1 = subprocess.Popen(args=['omxplayer','--no-osd','--loop','-b','--aspect-mode','fill','right.mp4'])
```

首先proc1在python中視為宣告一個變數，型態為一個subprocess，我在開啟這條執行緒之後，輸入的指令為以下，各位朋友可以嘗試直接在terminal中使用這串文字，也可以開啟名為right的影片。(請cd到影片檔案的資料夾，運作python時將影片位置放在執行python的位置)

```
omxplayer --no-osd --loop -b --aspect-mode fill 'right.mp4'
```

這邊附上omxplayer各個arguments的表列：

https://elinux.org/Omxplayer

--no-osd為不在影片播放時顯示時間或是影片任何內容的資訊

--loop 為重複播放

-b 同 --blank 讓影片常設背景為黑色

--aspect-mode fill 便是把影片強迫延伸至整個畫面大小，並且為全螢幕。

這樣便可以開啟一部影片了！！～～～

而後在切換影片時，我們可以直接刪除他，（如在電腦中按下x按鈕關閉影片）

```
subprocess.call(['pkill','-P',str(proc1.pid)])
proc1.kill()
```

當我在python中建立proc1這個subprocess時，系統會給予它一個pid，類似於電腦給予這個thread的編號，我只要直接呼叫電腦強制關閉這個thread影片便可以關閉，然後保持隨手好習慣，將這個變數在python中也刪除掉。

如此便是大致上的影片切換與播放了，在不同時候呼叫不同的subprocess開啟影片，並在需要切換時關閉它，另外附帶一提，有空也可以嘗試同時開啟兩部影片，會有意想不到很酷的視覺效果.........

在此附上完整程式，有問題也歡迎回應。

![](images/wix/4eb1dd_5186c79ebb484bbca79c6dea24d6bf16~mv2_d_1383_1732_s_2.webp)

P.S：使用Raspberry Pi 播放影像最討厭人的部分便是用電警示的小小閃電符號，會在螢幕最上方很討厭的一直出現解決方法其實很簡單。回到terminal中到達/boot/config.txt。

```
vim /boot/config.txt
```

於文件最底下，加入一行文字。

```
avoid_warnings=1
```

以上，祝大家玩得愉快！！！
