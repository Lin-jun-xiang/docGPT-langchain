## docGPT

主要開發工具:
* `Python`
* `Langchain`
* `Streamlit`

使用該工具至少須具備 `openai_api_key`，有關如何取得 key 可以前往[連結](https://platform.openai.com/)

## Introduction

* `docGPT` 是基於 langchain 與 streamlit 開發的
    * `langchain`: LangChain 是一個用於**開發由語言模型支持的應用程序的框架**。它支持以下應用程序
        1. 可以將 LLM 模型與外部數據源進行連接
        2. 允許與 LLM 模型進行交互
    * `streamlit`: streamlit 使 python 可以快速、免費的部署屬於你的應用程序 (通常拿來部屬AI)
* 原理
  * 透過 langchain 結合多種模型
    * 基於 langchain retrievalQA 開發的 **pdf 問答工具**
    * 基於 math-llm 開發的 **數學計算工具**
    * 基於 google-search 開發的 **搜索工具**

## LangChain

* 有關 langchain 的介紹，建議查看官方文件、[Github源專案](https://github.com/hwchase17/langchain)

#### Questions that ChatGPT cannot answer are handed over to LangChain for implementation!

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

## How to Use?

* 輸入您的 `API_KEY`:
    * `OpenAI API KEY`: 必須設定
    * `SERPAPI API KEY`: 根據您需求，如果您要問**PDF文檔沒有出現**的內容，您就需要用此 KEY

* 上傳來自本地的 PDF 檔案
* 開始進行提問 ! 

![RGB_cleanup](https://github.com/Lin-jun-xiang/docGPT-streamlit/blob/main/img/docGPT.gif?raw=true)


## Why Use?

* 本專案開發的 `docGPT` 具有以下功能:
  * 上傳 PDF
  * 與GPT進行來回答覆，快速學習PDF內容
  * 進行文檔總結
  * 附加 **"math-llm"**，提供您進行**數學計算**相關問答 (chatgpt無法回答的問題)
  * 附加 **"google-search"**，提供您進行**google搜尋** (chatgpt無法回答的問題)


