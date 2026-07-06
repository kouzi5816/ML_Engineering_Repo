
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os

st.title("📄 文書Q&Aアプリ（RAG）")
st.caption("アップロードした文書に基づいて回答します")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@st.cache_resource
def load_chain():
    embedding = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY
    )
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embedding
    )
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GEMINI_API_KEY
    )
    prompt = ChatPromptTemplate.from_template("""
以下のコンテキストのみを使って質問に答えてください。
コンテキストに答えがない場合は「情報が見つかりませんでした」と答えてください。

コンテキスト:
{context}

質問: {question}
""")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt | llm | StrOutputParser()
    )
    return chain, retriever

chain, retriever = load_chain()

question = st.text_input("質問を入力してください", placeholder="例：DX推進に必要なことは？")

if question:
    with st.spinner("回答を生成中..."):
        docs = retriever.invoke(question)
        answer = chain.invoke(question)

    st.subheader("💬 回答")
    st.write(answer)

    with st.expander("📎 参照した箇所"):
        for i, doc in enumerate(docs):
            st.markdown(f"**[{i+1}]** {doc.page_content}")
