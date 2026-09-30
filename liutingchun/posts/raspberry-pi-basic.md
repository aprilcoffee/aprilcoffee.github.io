因為近期接案使用頻繁(或是幫新銳動畫裝置藝術家[林瑜亮](https://gunter292.wixsite.com/gunter)於香港布展)，遂做個簡單的資料整理；包含遠端操控、開機自動執行、影片播放、3.5音源輸出消除雜音等等，做個常見的 Raspberry Pi 使用經驗分享。盼能拋磚引玉，得到更多分享與回饋。

隨著 Raspberry Pi 的價格逐漸親民，運算量也遠大於一代二代，第三代又內附 wifi 晶片，以Raspberry Pi 作為互動裝置的主機板門檻逐漸降低。想說整理一下最近對 Rapsberry Pi 的使用方法，以及一些十分重要的基礎。

本篇文的撰寫有些操作的門檻，基本上不在 command line 的部分多做介紹。使用的皆為 Raspberry Pi 3 以上之型號，包含 Raspberry Pi 3 Model B, Raspberry Pi Model B+。

---

**Raspberry Pi 3 購買：**

建議能購買正版的主板就購買正版主板，價格雖較高但是運作穩定。

台北車站新裝潢完成的天瓏書局，老闆很善心的把RPi3其他設備包裝成一組，價格為親民的2400，包含 RPi3一台，HDMI線一條，16G記憶卡，電源變壓器，散熱片，RPi外殼，滿推薦購買的。絕對沒有業配，歡迎老闆幫我做個折扣QQ

**作業系統：**

https://www.raspberrypi.org/downloads/raspbian/

作業系統基本上使用官方推薦的**Raspbian**。個人習慣使用2016年中出的raspbian-jessie目前使用上十分穩定，但切記不要開啟官方測試實驗的gpu加速。

基本上作業系統在安裝時有兩種 *Raspbian Stretch Lite與Raspbian Stretch with desktop，* 端看使用方式決定下載哪一款，如果純粹作聲音裝置、網路功能，包含無線分享器、藍芽喇叭，可以選擇使用Stretch Lite，如果要使用影像功能，包含影片播放等等，絕對要使用 **desktop，** 另外加裝Desktop會因為gui的關係導致運算效率降低。**但推薦新手安裝請選擇Raspbian Stretch with desktop**，多了介面多了方便。

**燒錄與連線：**

安裝時需先格式化記憶卡，Mac使用者推薦使用兩套軟體，先於**SDFormatter**格式化記憶卡後，以**ApplePi-Baker**安裝RPi作業系統。燒錄完成後，便可以將記憶卡插入RPi開機。

不熟悉terminal的使用者可以先插上一組螢幕和鍵盤滑鼠，切記切記 **不能購買藍芽的鍵盤滑鼠，** 初始化時是抓不到的。

熟悉terminal的使用者，可以先以電腦分享網路給Rpi，先將電腦連線上無線網路，透過分享網路的方式，走網路線給RPi，在terminal上輸入

```
arp -a
```

就可以搜尋區域網路內所有ip，找到raspberry pi的ip之後，輸入指令連線，**內建帳號為pi 密碼為raspberry。**

```
ssh pi@xxx.xxx.xxx.xxx
```

**基本安裝設定：**

開機後基本設定，在RPi的terminal中打上 sudo raspi-config 開始做初始化設定，在advance的部分開啟 scp, gpio, ssh, vnc, i2c。將時區設定好，並且將無線網路連線至手機熱點一次之後便會記憶。

![](images/wix/4eb1dd_341b6ac20bdd4ae88c19db1de94d0391~mv2.webp)

開啟VNC之後，便可以在自己電腦使用軟體 VNC Viewer 連線ip直接操作RPi的桌面。

https://www.realvnc.com/en/connect/download/viewer/

RPi上不需要另外安裝下載，再advanced options設定時便會自動安裝。

**系統套件安裝：**

接下來是最為重要的系統套件部分，在此推薦幾個非常重要的套件。

首先先在terminal 輸入指令同步官方套件庫的資訊，並且更新所有現有套件。

```
sudo apt-get update
sudo apt-get -y dist-upgrade
```

更新完畢後，開始安裝套件，以下有幾個推薦套件使用。可以以下指令來安裝

```
sudo apt-get install (欲安裝套件名稱)
```

推薦套件包含，omxplayer, vim, git. 這些都是必要的套件，但是不像python或vnc官方已經內建好了。

（註：內建python視版本而定，大部分是python 2.7，如果需要python 3需要另外下載）

**清除音源線雜訊：**

許多使用RPi作為聲音裝置的好朋友，時常遇到一個問題，因為3.5音源線輸出的聲音包含許多雜訊，因此常另外購買一張usb音效卡輸出聲音，其實這問題非常好解決。只要到 /boot/config.txt 在最底下加入一行以下指令便可以解決了啦～～～～～

```
audio_pwm_mode=2
```

**開機自動執行：**

開機自動執行的方法，需要先製作一份shell script寫下開機要做的所有事情。

首先在你需要執行的檔案，不管是puredata或是python或是omxplayer播一支影片，檔案的隔壁新增一個shell script

```
vim launcher.sh
```

在script中打上需要前往的路徑(我不好的習慣會放在Desktop)，以及要執行的檔案(如autorun.py)。

```
cd /
cd home/pi/Desktop
sudo python autorun.py
cd /
```

儲存檔案後，在terminal同個位置下輸入以下指令確保launcher檔案可以被執行。

```
chmod 755 launcher.sh
```

有時運作的檔案有問題時，開機後不會自動跑執行檔，為了保持良好習慣觀測出了什麼問題，可以回到根目錄建立一個logs的資料夾，再指派系統每次自動執行時將輸出的資料(包含錯誤執行的內容)跑到logs的資料夾中。首先建立logs資料夾，再開啟crontab檔寫上欲執行的launcher檔

```
cd
mkdir logs
sudo crontab -e
```

在crontab中寫入 **(請記得修改launcher檔案路徑)**

```
@reboot sh /home/pi/Desktop/launcher.sh >/home/pi/logs/cronlog 2>&1
```

這時 sudo reboot 後就會自動執行了！

另外另外如果開機後跑的是全畫面的影片，想要跳出又不知道怎麼辦，但是又沒有透過ssh進入。

可以很暴力的盲打以下指令來關閉。

```
ctrl + alt + T
sudo pkill omxplayer
```

以下大概是Raspberry Pi基本的一些功能。

之後有空再來撰寫 python 控制GPIO的部分，以及如何使用subprocess切換omxplayer來開啟影片。還有如何使用Raspberry Pi架設簡單的無線基地台。
