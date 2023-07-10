# docGPT

[English](./README.md) | [中文版](./README.zh-TW.md)

- 目錄
    - [Introduction](#introduction)
    - [What's LangChain?](#whats-langchain)
    - [How to Use docGPT?](#how-to-use-docgpt)
    - [How to develope a docGPT with streamlit?](#how-to-develope-a-docgpt-with-streamlit)


* 主要開發軟體與套件:
    * `Python 3.8.6`
    * `Langchain 0.0.218`
    * `Streamlit 1.22.0`

* 使用該工具至少須具備 `openai_api_key`，有關如何取得 key 可以前往[連結](https://platform.openai.com/)

---

### Introduction

* 專案目的:
    * 使用 langchain、streamlit 輕鬆搭建出一個強大的 "LLM" 模型，**讓您的 LLM 模型能夠實現 ChatGPT 做不到的事**:
      * 與**外部數據連接**，本專案以 **PDF 文件**為例子，透過 RetrievalQA 技術讓 LLM 理解您上傳的文件
      * 整合 LLM 與其他工具，達到**連網功能**，本專案以 Serp API 為例子，透過 Langchain 框架，使您能夠詢問模型有關**現今問題** (即 **google 搜尋引擎**)
      * 整合 LLM 與 **LLM Math 模型**，使您能夠讓模型準確做到**數學計算**
* 本專案的設計架構主要有三個元素:
    * [`DataConnection`](../model/data_connection.py): 讓 LLM 負責與外部數據溝通，也就是讀取 PDF 檔案，並針對大型 PDF 進行文本切割，避免超出 OPENAI 4000 tokens 的限制
    * [`docGPT`](../docGPT/): 該元素就是讓模型了解 PDF 內容的核心，包含將 PDF 文本進行向量嵌入、建立 langchain 的 retrievalQA 模型。詳細簡介請[參考](https://python.langchain.com/docs/modules/chains/popular/vector_db_qa)
    * [`agent`](../agent/agent.py): 負責管理模型所用到的工具、並根據使用者提問**自動判斷**使用何種工具處理，工具包含
        * `SerpAI`: 當使用者問題屬於 "**現今問題**"，使用該工具可以進行 **google 搜索**
        * `llm_math_chain`: 當使用者問題屬於 "**數學計算**"，使用該工具可以進行 數學計算
        * `docGPT`: 當使用者詢問有關 PDF 文檔內容，使用該工具可以進行解答 (該工具也是我們透過 retrievalQA 建立的)
* `docGPT` 是基於 **langchain** 與 **streamlit** 開發的

---

### What's LangChain?

* LangChain 是一個用於**開發由語言模型支持的應用程序的框架**。它支持以下應用程序
    1. 可以將 LLM 模型與外部數據源進行連接
    2. 允許與 LLM 模型進行交互

* 有關 langchain 的介紹，建議查看官方文件、[Github源專案](https://github.com/hwchase17/langchain)


**ChatGPT 無法回答的問題，交給 Langchain 實現!**

在這邊，作者將簡單介紹 langchain 與 chatgpt 之間的差異，相信您理解以下例子，你會對 langchain 這個開源項目感到震驚!

>今天可以想像 chatgpt 無法回答數學問題、超過 2020 年後的事情(例如2023年貴國總統是誰?)
>
> * 數學問題: 除了 Openai 模型，還存在專門處理數學問題的 math-llm
> * 現今問題: 可以使用 google 搜尋
>
>因此，我們要設計一個強大通用的 ai 模型，勢必要加入** "chatgpt"、"math-llm"、"google search"** 三個工具
>
>如果使用者的提問屬於數學計算類型，我們就使用 math-llm 工具解決、回答
>
>非AI時代，我們就會透過 `if...else...` 方式判斷使用者提問屬於哪種類型，此時就必須在使用者介面讓使用者選擇提問類型
>(UI 介面會有選擇欄位)
>
>但在AI時代，我們要讓使用者直接提問，而不需要事先選擇提問類型!
>在 langchain 中有一個 agent 的概念，它讓我們可以:
>
>  * 我們提供工具給他管理，例如 `tools = ['chatgpt', 'math-llm', 'google-search']`
>  * 工具也可以包含透過 langchain 設計出的 chain，例如使用 `retrievalQA chain` 設計一個可以回答來自文檔內容的提問，並將此 chain append 到 agent 管理的 tools
>  * **藉由 agent 判斷使用者提問，並自行決策出使用哪個工具處理問題** (完全自動化、ai化)

透過 langchain，我們可以創建屬於自己的 chatgpt 模型，它可以是通用型的模型，也可以是**企業化、商業化**的!

---

### How to Use docGPT?

* 前往[應用程序](https://docgpt-app.streamlit.app/)

* 輸入您的 `API_KEY`:
    * `OpenAI API KEY`: 必須設定
    * `SERPAPI API KEY`: 根據您需求，如果您要問**PDF文檔沒有出現**的內容，您就需要用此 KEY

* 上傳來自本地的 PDF 檔案
* 開始進行提問 ! 

![RGB_cleanup](https://github.com/Lin-jun-xiang/docGPT-streamlit/blob/main/img/docGPT.gif?raw=true)

---

### How to develope a docGPT with streamlit?

手把手教學，讓你快速建立一個屬於自己的 chatGPT !

首先請進行 `git clone https://github.com/Lin-jun-xiang/docGPT-streamlit.git`

方法有如下兩種:

* 於本地開發方式
    * `pip install -r requirements.txt`: 下載開發需求套件
    * `streamlit run ./app.py`: 於專案根目錄啟動服務
    * 開始體驗!

* 使用 Streamlit Community Cloud 免費部屬、管理和共享應用程序
    * 將您的應用程序放在公共 GitHub 存儲庫中（並確保它有一個 `requirements.txt`！）
    * 登錄[share.streamlit.io](https://share.streamlit.io/)
    * 單擊“部署應用程序”，然後粘貼您的 GitHub URL
    * 完成部屬[應用程序](https://docgpt-app.streamlit.app//)

<a href="#top">Back to top</a>
