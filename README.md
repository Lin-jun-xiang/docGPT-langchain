# docGPT

[English](./README.md) | [中文版](./README.zh-TW.md)

- Table of Contents
    - [Introduction](#introduction)
    - [What's LangChain?](#whats-langchain)
    - [How to Use docGPT?](#how-to-use-docgpt)
    - [How to Develop a docGPT with Streamlit?](#how-to-develop-a-docgpt-with-streamlit)


* Main Development Software and Packages:
    * `Python 3.8.6`
    * `Langchain 0.0.218`
    * `Streamlit 1.22.0`

* Using this tool requires at least the `openai_api_key`. You can visit the [link](https://platform.openai.com/) to learn how to obtain the key.


---


### Introduction

* Project Purpose:
    * Build a powerful "LLM" model using langchain and streamlit, **enabling your LLM model to do what ChatGPT can't**:
      * **Connect with external data** by using PDF documents as an example, allowing the LLM model to understand the uploaded files through RetrievalQA techniques.
      * Integrate LLM with other tools to achieve **internet connectivity**. For instance, using Serp API as an example, leverage the Langchain framework to enable querying the model for **current issues** (i.e., **Google search engine**).
      * Integrate LLM with the **LLM Math model**, enabling accurate **mathematical calculations**.

* This project consists of three main components:
    * [`DataConnection`](../model/data_connection.py): Allows LLM to communicate with external data, i.e., read PDF files and perform text segmentation for large PDFs to avoid exceeding OPENAI's 4000-token limit.
    * [`docGPT`](../docGPT/): This component enables the model to understand the content of PDFs. It includes embedding PDF text and building a retrievalQA model using Langchain. For more details, please refer to the [documentation](https://python.langchain.com/docs/modules/chains/popular/vector_db_qa).
    * [`agent`](../agent/agent.py): Responsible for managing the tools used by the model and automatically determining which tool to use based on the user's question. The tools include:
        * `SerpAI`: Used for "**current questions**" by performing a **Google search**.
        * `llm_math_chain`: Used for "**mathematical calculations**" by performing mathematical computations.
        * `docGPT`: Used for answering questions about the content of PDF documents. (This tool is built using retrievalQA)


* `docGPT` is developed based on **Langchain** and **Streamlit**.

---

### What's LangChain?

* LangChain is a framework for developing applications powered by language models. It supports the following applications:
    1. Connecting LLM models with external data sources.
    2. Enabling interactions with LLM models.

* For an introduction to LangChain, it is recommended to refer to the official documentation or the GitHub [repository](https://github.com/hwchase17/langchain).

**Questions that ChatGPT cannot answer can be handled by Langchain!**

Here, the author briefly introduces the differences between Langchain and ChatGPT. You will be amazed by this open-source project called Langchain through the following example!

> Imagine a scenario where ChatGPT cannot answer mathematical questions or questions about events beyond 2020 (e.g., "Who will be the president in 2023?").
>
> * For mathematical questions: In addition to the OpenAI model, there is a specialized tool called math-llm that handles mathematical questions.
> * For current questions: We can use Google search.
>
> Therefore, to design a powerful and versatile AI model, we need to include three tools: "chatgpt", "math-llm", and "Google search".
>
> If the user's question involves mathematical calculations, we use the math-llm tool to handle and answer it.
>
> In the non-AI era, we would use `if...else...` to decide which tool to use based on the user's question. However, Langchain provides a more flexible and powerful way to handle this.
> In the AI era, we want users to directly ask their questions without having to pre-select the question type! In Langchain, there is a concept called "agent" that allows us to:

* Provide tools for the agent to manage, such as `tools = ['chatgpt', 'math-llm', 'google-search']`.
* Include chains designed using Langchain, such as using the `retrievalQA chain` to create a question-answering model based on document content, and append this chain to the tools managed by the agent.
* **Allow the agent to determine which tool to use based on the user's question** (fully automated and AI-driven).

With Langchain, we can create our own ChatGPT model that can be general-purpose or tailored for specific industries and commercial use!

---

### How to Use docGPT?

* Visit the [application](https://docgpt-app.streamlit.app/).

* Enter your API keys:
    * `OpenAI API Key`: Required.
    * `SERPAPI API Key`: Optional. If you want to ask questions about content not appearing in the PDF document, you need this key.

* Upload a PDF file from your local machine.
* Start asking questions!

![docGPT](https://github.com/Lin-jun-xiang/docGPT-streamlit/blob/main/img/docGPT.gif?raw=true)

---

### How to Develop a docGPT with Streamlit?

A step-by-step tutorial to quickly build your own chatGPT!

First, clone the repository using `git clone https://github.com/Lin-jun-xiang/docGPT-streamlit.git`.

There are two methods:

* Local development:
    * `pip install -r requirements.txt`: Download the required packages for development.
    * `streamlit run ./app.py`: Start the service in the project's root directory.
    * Start exploring!

* Use Streamlit Community Cloud for free deployment, management, and sharing of applications:
    * Put your application in a public GitHub repository (make sure it has a `requirements.txt`!).
    * Log in to [share.streamlit.io](https://share.streamlit.io/).
    * Click "Deploy an App" and paste your GitHub URL.
    * Complete the deployment of your [application](https://docgpt-app.streamlit.app/).

<a href="#top">Back to top</a>
 