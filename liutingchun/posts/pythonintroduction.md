![](images/wix/4eb1dd_52c491c8438c43fea253894252aa5a6e~mv2.webp)

這學期算是比較正式接了助教，想説寫給自己整理也分享這學期的課程大綱，還有一些自己的雜談與碎念。

[工作室](https://ground-zero.khm.de/)開的課程，無論是實務課程或理論課程一直以來都是以電腦文學和自然語言處理作為討論基礎。在這邊對於電腦文學的討論，源自於希臘哲學中的 *Poiesis*，意指為創造的過程與行為，在詞源上也與詩 Poetry 同源。因此導向了無論是程式語言本身作為詩的表現形式、亦或是以程式語言生產與分析文學的方向。往年也試著開過LSTM、[馬可夫鏈](https://github.com/experimental-informatics/hands-on-text-generators)、[基礎神經網絡](https://github.com/experimental-informatics/hands-on-artificial-neural-networks)、[認知系統與電腦詩](https://github.com/experimental-informatics/codichte_experiments-with-cognitive-systems)等課程。從 GPT-2 延伸的 aitextgen, ai dungeon、Dall-E 1等等都曾經被納入討論。這學期是這幾年來第一次花一整學期走完程式設計基礎的課程。

教授很喜歡以1941年阿根廷作家 Jorge Luis Borges 的《[巴別塔圖書館](https://www.libraryofbabel.info/)》(Library of Babel)作為課程的起點，想像一種基於無限遞迴的結構便能窮盡宇宙中所有基於拉丁文字的詩。以此開啟關於程式語言的想像。無論是 Joseph Weizenbaum 的 Eiza 和 Hans Magnus Enzensberger 的 Landsberger Poesieautomat (詩的販賣機) [2006年重現的裝置版](https://www.youtube.com/watch?v=vj1buZhKKko)，作為德文一脈關於自然語言處理以降的彙整與推進，也算是老教授在退休前希望著重的方向吧。

在這幾年舉凡 GPT-3、Stable Diffusion、Midjourney 等等 Transformer Model 百花齊放之下，文字再度成為人工智慧發展的重點關注對象。剛好也結合學校文學組的課程，自然語言處理基礎便成為了學校架構基礎程式設計課程的主要方向。也只有在實際走過文字處理發展的歷史，才能更加深刻的操作與理解當代複雜人工智慧背後所影射的社會偏見。

底下變成課程的大綱，想找時間更詳細的補完所有內容，也算是給自己的整理。有趣的地方去年我們還在 GPT-2 的 AItextgen中玩耍（曾經我們很堅持使用 common crawl 的模型，但open ai 實在碾壓了眾生），才剛過一年到現在 ChatGPT 的發表，語言模型推層出新的同時，課程也不斷在被修正與修改。某種程度上，老教授也堅信只有無論技術或是理論的基礎打實，才能更加理解而非浪漫化這波浪潮。

小小的disclaimer是我知道正常的CS包含基礎程式設計和DSA甚至是ADA都是要花一年要兩年，但因為課綱的關係我們全部塞進一學期裡頭，也算是很概述的「介紹」程式設計。很多實務的部分還是看學生自己想進行的計畫再來進行修正

課程簡介：

在日益媒體化的社會中，演算法與程式設計的基本理解是數字自決 (Digital Self-determination)的核心關鍵。數位資訊和通訊系統主導著我們對生活現實和媒體自我形象的感知。更關鍵的是，我們正在透過演算法產生全新的體驗、行動和決策空間。 人工智慧也已在創作音樂、互動視覺和詩歌創作中使用。 因此，我們必須將分析和生成式演算法理解為一種基本的文化技術，其危險和美學層面必須以同樣的方式暴露出來。

這堂課程將教授以 Python 程式語言為基礎的技術和藝術實踐，並以文本生成作為核心方法。除了在簡單的開發環境中討論如何學習程式設計基礎，更重要的是將程式設計作為一種藝術乃至於社會實踐。然而，課程只能幫助克服第一道障礙，只有當掌握一定程度的技術，程式語言將不再是單純的功能問題，而是探索美學潛力的問題時，程式碼才能成為自身的藝術簽名。乃至於進一步理解與分析大規模演算法所帶來的社會現象、演算法偏見(Algorithmic Bias)等等問題意識。生成過程是關於自由與控制之間的平衡。我在哪裡可以放棄控制而創造驚喜，在哪裏又要保留控制以達到某種美感結果？

課程內容全部放置於 Github 頁面中：

[https://github.com/experimental-informatics/plunging-into-code](https://github.com/experimental-informatics/plunging-into-code)

教學環境：

程式設計介面為透過 [Jupyter hub](https://jupyter.org/hub) 架設 Python Notebook 伺服器，環境控制為 [mini conda](https://docs.conda.io/en/latest/miniconda.html)，檔案皆為 .ipynb。進階內容則建議自行安裝包含 GUI 的 [Anaconda-Navigator](https://anaconda.org/anaconda/anaconda-navigator)

使用資料庫：

[openai](https://pypi.org/project/openai/), [requests](https://pypi.org/project/requests/), [nltk](https://pypi.org/project/nltk/),  [numpy](https://pypi.org/project/numpy/), [pandas](https://pypi.org/project/pandas/), [Wikipedia-API](https://pypi.org/project/Wikipedia-API/), [markovify](https://pypi.org/project/markovify/)

課綱設計原則：

原則上以上半節課講授程式相關內容，包含程式設計藝術家，電腦文學、人工智慧歷史，技術哲學、線上資料庫、演算法與資料偏見相關的文獻與論文。下半節課進行實務操作。

內容設計的分配原則上是我（基礎程式、資料結構）、博士生（資訊社會學、資料偏見與對抗式攻擊）、技工（電子控制與樹莓派）和教授（電腦文學、人工智慧史、技術哲學）之間的拔河，上課的時候會互相插播討論。因為希望所有內容都基於 Python 上讓學生不至於切換語言而感到混亂，所以共識是環繞文字處理與電腦文學為核心發展出來的。因為還是第一學期這樣執行，所以內容還十分混亂，應該明年會繼續整合和優化吧。

第一週：[Prompt Design 作為與電腦互動的基礎](https://github.com/experimental-informatics/plunging-into-code/tree/master/Week1-Prompting)

- Demo 自動化的 Prompt Design，來理解現今許多GPT-3相關軟體的基礎運作邏輯。

第二週：[基礎 Python（一）- 環境介紹｜變數、資料型態、字串](https://github.com/experimental-informatics/plunging-into-code/tree/master/Week2-PythonEinf%C3%BChrung01)

- 介紹 Jupyter Hub 作為環境基礎，盡量讓所有人使用瀏覽器編寫程式以避免太多的環境安裝問題。

第三週：[基礎 Python（二）- 藝術家介紹 ｜陣列、列表、檔案讀取](https://github.com/experimental-informatics/plunging-into-code/tree/master/Week3-PythonEinf%C3%BChrung02)

- 以一些電腦文字或是人工智慧相關的藝術家作為開端，帶學生想像可能的創作方向，乃至於對於人工智慧的社會批判現況。

第四週：[基礎 Python（三）- 字串處理、迴圈、排序](https://github.com/experimental-informatics/plunging-into-code/tree/master/Week4-PythonEinf%C3%BChrung03)

- 以排序演算法作為理解經典演算法運作的原理

第五週：[資料庫基礎 - 線上資料庫與其偏見｜資料交換格式 - txt, Json, CSV](https://github.com/experimental-informatics/plunging-into-code/tree/master/Week5-DatasetEinf%C3%BChrung)

- 介紹各種線上資料庫作為學生未來下載的各種可能性與方法。

第六週：[電腦文學基礎 Hans Enzensberger 與 Joseph Weizenbaum｜字典、條件判斷](https://github.com/experimental-informatics/plunging-into-code/tree/master/Week6-Enzensberger_Weizenbaum)

- 因上週 Hans Enzensberger 過世，教授決定以當週課程來緬懷與回溯其對於德國電腦科學的貢獻。

第七週：[馬可夫鏈 ｜函式、N-order text generation](https://github.com/experimental-informatics/plunging-into-code/tree/master/Week7-MarkovChain)

第八週：[電腦圖像基礎 ｜多維陣列、PIL](https://github.com/experimental-informatics/plunging-into-code/tree/master/Week8-Graph-Image)

第九週：樹莓派與網路基礎｜Command Line (CMD)、python GPIO

--------------聖誕節後沒有人想上課跟教課於是很待定--------------

第十週：電腦文學與NLTK（待定）

第十一週：自動化 Prompt Design 與 openai API（待定）

密集課程：對抗式攻擊與其藝術實踐

資料整理：

[【藝術家與作品列表】](https://github.com/experimental-informatics/plunging-into-code/blob/master/Week3-PythonEinf%C3%BChrung02/KI-K%C3%BCnstlerinnen_Liste.md)

[【List of Propaganda, Misinformation & Hate Speech Datasets】](https://github.com/experimental-informatics/plunging-into-code/blob/master/Week5-DatasetEinf%C3%BChrung/datasets-4-NLG-tasks.md)

[【War on Error】](https://ground-zero.khm.de/portfolio/war-on-error/)

[【Library of Babel 巴別圖書館】](https://github.com/experimental-informatics/Workshop-Fernuni-Hagen/blob/master/1_Bibliothek_von_Babel.ipynb)

[【On the Road】 Based on the novel “On the Road” by Jack Kerouac and Google Maps Direction Service.](https://gregorweichbrodt.de/project/on-the-road.html)

論文：

[Joseph Weizenbaum. 1966. ELIZA—a computer program for the study of natural language communication between man and machine](https://dl.acm.org/doi/10.1145/365153.365168)

[*Emily M. Bender, Timnit Gebru, Angelina McMillan-Major, and Shmargaret Shmitchell. 2021. On the Dangers of Stochastic Parrots: Can Language Models Be Too Big? 🦜.*](https://dl.acm.org/doi/10.1145/3442188.3445922)

[*Harini Suresh and John Guttag. 2021. A Framework for Understanding Sources of Harm throughout the Machine Learning Life Cycle.*](https://dl.acm.org/doi/fullHtml/10.1145/3465416.3483305)

[*Nick Seaver. 2018. What Should an Anthropology of Algorithms Do?*](https://journal.culanth.org/index.php/ca/article/view/ca33.3.04)

[*OpenAI. 2020. Language Models are Few-Shot Learners*](https://arxiv.org/abs/2005.14165)

[Algorithmische Einfühlung: Über Nick Montforts »Megawatt«](https://0x0a.li/de/algorithmische-einfuehlung-nick-montforts-megawatt/)

"Explaining consciousness: the hard problem" Edited by Jonathan Shear

學習資源：

[Speech and Language Processing (3rd ed. draft)](https://web.stanford.edu/~jurafsky/slp3/)

[Dive into Deep Learning](https://d2l.ai/index.html)
