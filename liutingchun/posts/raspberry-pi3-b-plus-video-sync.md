積欠已久，接了小工作決定邊弄邊把步驟寫出來。

同步播放器的工作方式，需要至少兩台電腦(在這邊使用Pi)在同個網域下運作。第一台作為Master，其他作為Slave。當Master在播放影片時，會在一定時間間隔不斷傳送目前播放的時間點給所有Slaves。但大家也知道，這樣的傳輸方法，會因為不同網路環境存在一定的延遲。因此，在Slaves收到訊息時，會自動Seek到對應的時間點，在把目前自己播放的時間點傳送回去給Master。

大致上來說，如同大家在國高中作過的「蝙蝠回聲距離問題」，當Master收到Slave回傳的訊號時，便會確認自己目前的時間點，再和自己當初傳送出訊號的時間點相減除以二。一來一往之間，Master變可以得知連結關係中的網路延遲時差，進而把目前播放時間再加上預期傳輸時間差送給所有Slaves，達成同步。

![](images/wix/4eb1dd_1b03ac6f774e41ceb06bad9ea87991af~mv2.webp)

本篇將解釋如何目前最流通的Raspberry Pi3 Model B+ 製作同步播放器。主要使用的軟體是這份：[https://github.com/turingmachine/omxplayer-sync](https://github.com/turingmachine/omxplayer-sync)

之所以特別標註B+的原因，一來是自己習慣使用B+工作，二來是B+在使用這套軟體時，會遇到非常多問題導致無法正常安裝乃至於作業系統整個弄壞。在這邊附上另外找到的解決方法。

### 基礎設定

關於Pi如何登入連結等等，就詳見一篇部落格

[https://www.liutingchun.com/post/raspberry-pi-basic](https://www.liutingchun.com/post/raspberry-pi-basic)

當我們得到一台安裝好的Pi之後（我使用的作業系統是2018-11-13-raspbian-stretch）便可以開始進行基礎的設定。首先要在Preferences的Raspberrypi Pi Configuration中，進行三個步驟，過程中會詢問是否要重新開機，都先略過，等所有設定都完成再一次重啟。

1. **調整記憶體用量至512**：方便播放影片不會卡頓
2. **開啟所有預設通道設定**：使我們可以使用VNC或SSH工作
3. **調整畫面解析度**

進行完成之後就可以重新開機等待完成

![](images/wix/4eb1dd_930e7beee924484487baa59fb33e55ff~mv2.webp)

![](images/wix/4eb1dd_f98ab4ce781a4129931a06bb2017fb9d~mv2.webp)

### 安裝軟體

再登入之後我們便可以開始基礎設定。

開啟我們的Terminal之後，我們要先進行函式庫的更新以及安裝，以及修改我們的Boot檔案

```
sudo apt-get update
sudo apt-get install vim
```

Vim安裝完成之後便可以開始撰寫以及修改我們的Code。

第一件要做的事，是把音效雜訊移除，以及關閉hdmi畫面中的閃電符號

在terminal中我們要先修改/boot/config.txt 檔案

```
sudo vim /boot/config.txt
```

之後我們會以vim開啟config.txt檔案，此時把游標一路推到檔案最下面

先輸入 i 或 a 開始編輯，在最下方輸入

```
audio_pwm_mode=2
avoid_warnings=1
```

之後鍵盤按下 **esc** 離開編輯模式 再輸入 **:wq** 變可以存檔跳出。

![](images/wix/4eb1dd_f887142c7e9b49c89fac52f51b7315d0~mv2.webp)

這時我們便可以開始安裝omxplayer-sync。

[https://github.com/turingmachine/omxplayer-sync](https://github.com/turingmachine/omxplayer-sync)

記住，千萬別使用Readme中推薦的安裝方法。請直接接著閱讀。

omxplayer在前幾篇文章中介紹中，是使用raspberry pi時的其中一個播放器軟體。

我們需要經過如下步驟進行安裝，首先打開Terminal

我們要先登入超級使用者 (super user)接著進行函式庫升級以及安裝。每一條都會需要一點時間，特別是upgrade會耗時非常非常的久。在這邊就需要耐心等待。中間要記得按下各種q或Y。**每一步驟請盡量按照步驟執行，跳過任何一步，很容易出問題。**

```
sudo su
apt-get update
apt-get upgrade
apt-get install libghc-these-prof
apt-get install libghc-terminal-size-prof
apt-get install libglib2.0-dev
apt-get install libgtk2.0-dev
apt-get install --reinstall python-gi
apt-get install ffmpeg
```

接著我們要移除原有的omxplayer 以及重新安裝新的軟體

```
apt-get remove omxplayer
rm -rf /usr/bin/omxplayer /usr/bin/omxplayer.bin
rm -rf /usr/lib/omxplayer
apt-get install libpcre3 fonts-freefont-ttf fbset
apt-get install libssh-4 python3-dbus
```

排版關係他被切開了，但請記得把以下的指令都要用一行打完喔

```
wget https://github.com/magdesign/PocketVJ-CP-v3/raw/master/sync/omxplayer_0.3.7-git20170130-62fb580_armhf.deb
dpkg -i omxplayer-0.3.7-git20170130~62fb580_armhf.deb
wget -O /usr/bin/omxplayer-sync https://github.com/turingmachine/omxplayer-sync/raw/master/omxplayer-sync
```

最後我們需要在系統授權omxplayer的使用

```
chmod 0755 /usr/bin/omxplayer-sync
chmod 0755 /usr/bin/omxplayer
```

以及修正一些前段時間安裝的錯誤

```
apt --fix-broken install
apt-get install libpcre3
apt --fix-broken install
```

### 軟體測試

首先我們先打出

```
exit
```

退出super user模式。

接著為了方便工作，我們可以在桌布上建議一個新的資料夾，然後下載測試影片開始測試。

```
mkdir /home/pi/Desktop/autoplay
cd /home/pi/Desktop/autoplay
```

以下也是一行打完

```
wget https://github.com/turingmachine/omxplayer-sync/raw/master/synctest.mp4
```

![](images/wix/4eb1dd_259a63d93f4e4a8d90cd64db3a46f227~mv2.webp)

接著我們打上

```
omxplayer-sync -muv synctest.mp4
```

變可以測試影片是否正常播放，請記得如果是在VNC模式下，是不會有畫面的。如果需要退出，按下Ctrl-C即可。

![](images/wix/4eb1dd_4809894287bd45c9b3430a46d97b2f2b~mv2.webp)

### 實際使用

我們可以在另一篇文章中找到開機自動執行的方法，請記得在sh檔案中，在master裡加上15秒延遲，slaves中加上20秒。可以確保開機之後pi已經正確完成所有初始化，以及連上網路。

[https://www.liutingchun.com/post/raspberry-pi-basic](https://www.liutingchun.com/post/raspberry-pi-basic)

請記得所有檔案名稱都需要相同。

Master執行的指令為

```
omxplayer-sync -mu -a fill -o both [檔案名稱]
```

*Slave則是*

```
omxplayer-sync -lu -a fill [檔案名稱]
```

在這邊打一些註解

-v 顯示詳細資料，會在影片播放時顯示時間

-u 循環播放

-m 設置為master

-l 設置為slave

-o both音效設置 both為同時在3.5mm和hdmi播放

-a fill 全螢幕播放 (也有其他模式fill, letterbox, stretch)

### 備註

在軟體官方頁面有幾點注意事項，在這邊小小翻譯一下，再附上一些我自己的註解。

- 請記得將所有pi都**連到同個子網域**，建議用有線接hub效果可能更好。
- 第一次輪播影片，會同步不了是正常的。
- 播放在不同pi的檔案，**檔案名稱必須要相同**。
- 在播放檔案的資料夾，**請不要放入其他無關檔案，否則同步容易失敗。**
- **網路需要先連結**，再開啟同步軟體，否則Master不會傳送資料
- Slave檔案中，請勿使用audio的參數
- **請使用h264檔案，並且影片長於60秒**

最後附張之前在府中和阿芝芳境王量弄展覽同步播放的工作圖

![](images/wix/4eb1dd_80c7db8b444b4d0e8ed9807f3ea952a4~mv2.webp)
