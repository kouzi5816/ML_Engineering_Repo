
import streamlit as st
import os
import tempfile
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ─── APIキー取得 ───────────────────────────────────────────
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

# ─── ページ設定 ────────────────────────────────────────────
st.set_page_config(page_title="📄 文書Q&Aアプリ", layout="wide")
st.title("📄 文書Q&Aアプリ（RAG）")
st.caption("PDFをアップロードして、内容について質問できます")

# ─── Embedding・LLM の初期化 ───────────────────────────────
@st.cache_resource
def get_embedding():
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GEMINI_API_KEY
    )

@st.cache_resource
def get_llm():
    return ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        google_api_key=GEMINI_API_KEY
    )

# ─── PDFをChromaDBに取り込む関数 ───────────────────────────
def process_pdfs(uploaded_files):
    """アップロードされたPDFを読み込み、ChromaDBに保存して返す"""
    all_chunks = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    for uploaded_file in uploaded_files:
        # Streamlitのアップロードファイルは一時ファイルに書き出す必要がある
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            loader = PyPDFLoader(tmp_path)
            pages = loader.load()

            # ページ番号・ファイル名をメタデータに追加
            for page in pages:
                page.metadata["source_file"] = uploaded_file.name

            chunks = splitter.split_documents(pages)
            all_chunks.extend(chunks)
        finally:
            os.unlink(tmp_path)  # 一時ファイルを削除

    if not all_chunks:
        return None

    # ChromaDBに保存（インメモリ：Streamlit Cloud向け）
    vectorstore = Chroma.from_documents(
        documents=all_chunks,
        embedding=get_embedding()
    )
    return vectorstore

# ─── RAGチェーンを組み立てる関数 ───────────────────────────
def build_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    prompt = ChatPromptTemplate.from_template("""
以下のコンテキストのみを使って質問に答えてください。
コンテキストに答えがない場合は「この文書には該当する情報が見つかりませんでした」と答えてください。

コンテキスト:
{context}

質問: {question}
""")
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | get_llm()
        | StrOutputParser()
    )
    return chain, retriever

# ─── サイドバー：PDFアップロード ───────────────────────────
with st.sidebar:
    st.header("📂 PDFをアップロード")
    uploaded_files = st.file_uploader(
        "PDFファイルを選択（複数可）",
        type="pdf",
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("📥 文書を取り込む", use_container_width=True):
            with st.spinner("PDFを処理中..."):
                vectorstore = process_pdfs(uploaded_files)
                if vectorstore:
                    st.session_state["vectorstore"] = vectorstore
                    st.session_state["file_names"] = [f.name for f in uploaded_files]
                    st.success(f"{len(uploaded_files)}件のPDFを取り込みました")

    # 取り込み済みファイルの表示
    if "file_names" in st.session_state:
        st.divider()
        st.caption("取り込み済みファイル")
        for name in st.session_state["file_names"]:
            st.caption(f"✅ {name}")

# ─── メイン：質問・回答 ────────────────────────────────────
if "vectorstore" not in st.session_state:
    st.info("← 左のサイドバーからPDFをアップロードして「文書を取り込む」を押してください")
else:
    chain, retriever = build_chain(st.session_state["vectorstore"])
    question = st.text_input(
        "質問を入力してください",
        placeholder="例：この文書の要点を教えてください"
    )

    if question:
        with st.spinner("回答を生成中..."):
            docs = retriever.invoke(question)
            answer = chain.invoke(question)

        st.subheader("💬 回答")
        st.write(answer)

        with st.expander("📎 参照した箇所"):
            for i, doc in enumerate(docs):
                page = doc.metadata.get("page", "?")
                source = doc.metadata.get("source_file", "不明")
                st.markdown(f"**[{i+1}] {source}（{int(page)+1}ページ）**")
                st.caption(doc.page_content)
