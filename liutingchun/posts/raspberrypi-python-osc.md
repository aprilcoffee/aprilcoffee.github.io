這篇來寫寫如何在Python當中使用OSC通訊協定傳輸基本的數字，稍微解釋一下何為OSC還有其應用範圍，然後做一個簡單的Server/Client端的使用說明，比較複雜的用途(Broadcast、Bundle、或是如何做複雜Parsing)就先跳過, 簡單易懂為主。

這篇使用的語言主要以 Python 為主，TouchDesigner, Processing, Unity 或是 MaxMsp 的 OSC 網路教學資源很多很多就自己查吧。看完這篇再搭配之前的 python GPIO 撰寫，就可以利用自己的 Raspberry Pi 和 PureData 製作自製電子樂器了～～

OSC全名為 Open Sound Control，是個基於 UDP 的通訊協定(也可以用 TCP 不過就不贅述)，被大量應用於聲音相關軟體，可以做區域網路內簡單資料的傳輸。不管是跨機器、或是跨軟體，都是傳輸資料簡單好用的工具。舉例來說，當我要將 Ableton Live 中某一軌聲音的音量視覺化，便可以傳送一個 OSC 封包給 Processing 或是TouchDesigner，得到這個參數之後，便可以做調整。或是在基於 Raspberry Pi 中以 Python 撰寫的 GPIO 收到感測器訊號時，也可以將參數傳送到 PureData 來生成聲音。一個OSC的封包主要分為兩種OSC Message或是OSC Bundle，這邊以比較簡單常用的Message為主解釋。

一個 OSC 的 Message 基本上分為三個部分

OSC Address Pattern ： 是一個由字符 ‘/’ 開始的 String，我們可以想像傳輸資料的名稱。

OSC Type Tag String ： 一些老版本的OSC會忽略它，主要說明Arguments的資料型別。

OSC Arguments ： 是為實際傳輸的資料內容，可以是零個也可以是多個字串或數字。

一個基本的OSC訊號傳輸時，可以只傳送兩個部分，Address Pattern還有Arguments

假定我們在Max/Msp時用一個message框起來 就會長這樣

![](images/wix/4eb1dd_c9bf8ebe609346249c6ff339643a8f68~mv2.webp)

這裡是指Address Pattern為/msg 而 Arguments 也就是資料為 0 和 1 兩個

題外話一下，Max/Msp的 udpSend , udpReceive都不是真的udp，而是指osc。

在使用 OSC 時分為Client和Server兩端。我自己習慣上 Server 通常作為接收端，而Client通常作為發送端 (Boardcast時另當別論)。需要注意的是通常需要在Server端軟體開啟的情況下，Client再開啟會比較安全唷～～

Python 當中可以使用OSC的套件很多，我自己非常習慣使用 pyOSC 這個套件，簡單好用。但缺點是不支援太複雜的功能。如果有其他需求，也滿推薦 python-osc 的。

安裝方式如下

```
sudo pip install pyOSC
```

就安裝完了 ._./

那我們就可以開始撰寫Python了～

一樣我們先開始一個檔案來撰寫osc傳輸，可以選擇在Desktop或是/home/pi直接建立都可以。

```
sudo vim oscServer.py
```

開始撰寫之後，我們需要先匯入對應的 library。

```
from OSC import OSCServer,OSCClient, OSCMessage
```

這邊先以Server端我們主，Server我們的任務很間單，就是開啟電腦的通道，讓別人可以傳送資料進來。所以我們需要開放自己的ip以及對應的port。ip 可以想像成電腦的地址，而 port 則是開啟的房門通道。這個通道在電腦使用的非常頻繁，凡事需要電腦主機溝通的軟硬體，都會使用到一個port，而有些則是固定使用特殊的port來溝通，例如port 22是可以做ssh的通道，80和443則是平常我們在使用瀏覽器時連結網站資料傳輸時的port。一台電腦可以開幾萬個 port 而如上所述，因此通常建議在使用自己撰寫的程式時，都會建議大家開到 5000-60000，來防止與電腦其他軟體衝突。我們在這裡就以9527為範本。

```
server = OSCServer(("0.0.0.0",9527))
```

server便是我們開始server的變數，ip對應是0.0.0.0也就是開放所有ip進入的意思(這邊說明的比較隨便，有興趣可以自己搜尋)，基本上固定事自己電腦ip即可，但懶得查的話可以用’0.0.0.0’，port則是9527，要記住這個9527，因為等回client端也需要相對的port來傳輸資料。

接著我們需要一個 Message Handler 來承接資料，每當有 osc 訊號傳入 server 時，Handler就會觸發我們去執行一個Function。而因為python程式碼是由上而下讀取，我們也需要先定義一個Function來讓Handler知道他要執行什麼。

```
def msg_callback(path, tags, args, source):
       print(int(args[0]))

server.addMsgHandler("/msg",msg_callback)
```

首先 python 在宣告一個function時，需要使用 def 來開頭，其後就是 function 的名字，括號內則是接收到的參數 ( parameter ) 最後是一個很容易忘記的冒號。

參數中，我們可以不用管 path, tags, source 有興趣的朋友可以自己print出來看看。我們需要注意的是 args，他是對應一個 OSC Arguments 的陣列。所以我們用 args[0] 來讀取陣列的第零個資料，數字可以無限增加，端看你一次增加 (Append) 多少資料。另外要注意的是 int() 這邊可加可不加，視接下來如何使用資料而定。

之後是addMsgHandler的部分，是告訴這份 python 程式，當我接受到什麼樣的Address Pattern時，需要執行哪一個函式 (Function) ，在這裏是指，如果我收到的osc訊號包含 /msg 時，我便會執行msg_callback這個Function。而且對應的 Function 就可以將我的資料Print出來，你也可以將它放入另一個變數，或是執行任何內容。

最後我們要讓我們的程式不斷地等待 OSCMessage 傳送過來，所以我們要這樣寫。

```
while True: 
       server.handle_request()
```

這樣就是完整的接收端(Server)程式了。

```
from OSC import OSCServer,OSCClient, OSCMessage
server = OSCServer(("0.0.0.0",9527))
def msg_callback(path, tags, args, source):
       print(int(args[0]))
server.addMsgHandler("/msg",msg_callback)
while True: 
       server.handle_request()
```

接著讓我們撰寫Client端，這邊就更簡單了。

一樣我們先include函式庫，還有設定我們要對輸的對象

```
from OSC import OSCServer,OSCClient, OSCMessage
client = OSCClient()
client.connect(('127.0.0.1', 9527))
```

這邊是先宣告一個變數client來當作client端接收，然後讓他連結(connect)至對應的地點，也就是ip 127.0.0.1 還有port 9527。127.0.0.1是自己電腦的地址。這樣我們就連接到我們的server了。如果今天是要連線至其他電腦或設備，記得要先找到其他電腦的ip喔。

（題外話，Mac查詢ip的方式，是按著option之後左鍵點一下上方wifi按鈕）

接著是資料的部分，如上所述，Message我們需要兩個內容，一個是 Address Pattern 一個是 Arguments。

```
oscmsg = OSCMessage() 
oscmsg.setAddress("/msg") 
oscmsg.append(0)
```

首先我們先宣告一個變數 oscmsg 來作為 Message ，然後設定他的 Address Pattern 為 /msg，最後我們用append的方式加入資料，每次 append 都是加入一個新的資料。舉例來說如果我寫了如下

```
oscmsg.append(3)
oscmsg.append(7)
oscmsg.append('H')
```

那當我在接收時，arg[0]便是3，arg[1]會是7，最後arg[2]會是字元H。可以自己搭配使用。

最後我們需要將oscmsg透過client送出。

```
client.send(oscmsg)
```

完整的發送端(Client)程式如下

```
from OSC import OSCServer,OSCClient, OSCMessage

client = OSCClient()
client.connect(('127.0.0.1', 9527))

oscmsg = OSCMessage() 
oscmsg.setAddress("/msg") 
oscmsg.append(0)
client.send(oscmsg)
```

這樣就可以傳送了資料了，最下面的四行，也就是從宣告到傳送，可以在我們需要傳輸資料時使用，例如當我們在GPIO程式中，讀取某一個pin腳的數值，便可以將這個數值傳輸出去。

例如：

```
number = digitalRead(23);

oscmsg = OSCMessage() 
oscmsg.setAddress("/msg") 
oscmsg.append(number)
client.send(oscmsg)
```

這樣便可以將接收到的數字傳送出去～

基本的python中使用OSC大概就是這樣，祝大家玩得愉快。
