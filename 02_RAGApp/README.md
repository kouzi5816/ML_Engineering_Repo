# 📄 文書Q&Aアプリ（RAG）

PDFをアップロードして、内容について自然言語で質問できるアプリです。  
LangChain・ChromaDB・Gemini APIを使ったRAG（Retrieval-Augmented Generation）システムを、Streamlit Cloudにデプロイしました。

🔗 **デモURL**：https://mlengineeringrepo-k9rvceybruxi3konnrs8fh.streamlit.app/

---

## 📌 概要

| 項目 | 内容 |
|------|------|
| 作成目的 | RAGシステムの設計・実装・デプロイを一気通貫で体験するPoC |
| 対象ドキュメント | 任意のPDF（複数可） |
| 回答根拠 | 参照ページ番号・参照箇所を回答とともに表示 |
| デプロイ先 | Streamlit Cloud（無料枠） |

---

## 🏗 アーキテクチャ

```
[PDF アップロード]
      ↓
[PyPDFLoader でテキスト抽出]
      ↓
[RecursiveCharacterTextSplitter でチャンク分割]
      ↓
[Gemini text-embedding-004 でベクトル化]
      ↓
[ChromaDB（インメモリ）に保存]
      ↓
[質問入力] → [類似検索（上位3件取得）] → [Gemini 2.5 Flash で回答生成]
      ↓
[回答 ＋ 参照ページ番号を表示]
```

---

## 🛠 技術スタック

| カテゴリ | 使用技術 |
|----------|----------|
| LLM | Gemini 2.5 Flash（Google AI Studio） |
| Embedding | Gemini text-embedding-004 |
| RAGフレームワーク | LangChain |
| ベクトルDB | ChromaDB（インメモリ） |
| PDFローダー | PyPDFLoader（langchain-community） |
| フロントエンド | Streamlit |
| デプロイ | Streamlit Cloud |

---

## ✨ 機能

- **複数PDFの同時アップロード**：サイドバーから複数ファイルをまとめて取り込み可能
- **意味検索**：キーワード一致ではなく、質問の意図に近い箇所を検索
- **参照箇所の表示**：回答の根拠となったページ番号・テキストを展開表示
- **ドキュメント外の質問への対応**：文書に情報がない場合はその旨を明示

---

## 🚀 ローカルでの実行方法

### 前提条件

- Python 3.10 以上
- Gemini API キー（[Google AI Studio](https://aistudio.google.com/) で無料取得）

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/your-username/ml_engineering_repo.git
cd ml_engineering_repo/02_RAGApp

# 依存関係をインストール
pip install -r requirements.txt

# APIキーを環境変数に設定
export GEMINI_API_KEY="your-api-key-here"

# アプリを起動
streamlit run app.py
```

### Streamlit Secretsを使う場合

`.streamlit/secrets.toml` を作成して以下を記載：

```toml
GEMINI_API_KEY = "your-api-key-here"
```

---

## 📁 ファイル構成

```
02_RAGApp/
├── app.py              # Streamlitアプリ本体
├── requirements.txt    # 依存パッケージ
└── README.md           # このファイル
```

---

## 🔍 実装のポイント

**インメモリChromaDBを採用した理由**  
Streamlit Cloudのファイルシステムはデプロイのたびにリセットされるため、`persist_directory` による永続化が機能しません。アップロードのたびにVectorstoreをインメモリで再構築する設計にしています。

**tempfileでPDFを処理している理由**  
StreamlitのアップロードオブジェクトはPyPDFLoaderがファイルパスを要求するため直接渡せません。一時ファイルに書き出してから処理し、完了後に削除しています。

**session_stateでVectorstoreを保持している理由**  
Streamlitはインタラクションのたびにコードが再実行されます。質問のたびにPDFを再処理しないよう、`st.session_state` にVectorstoreを保持しています。

---

## 📈 今後の拡張予定

- [ ] チャット履歴機能の追加
- [ ] Docker化とCloud Runへのデプロイ（Month 3）
- [ ] 日本語特化Embeddingモデルへの切り替え検討
- [ ] アップロード済みドキュメントの管理機能

---

## 🗒 学習ログ

| 日付 | 内容 |
|------|------|
| 2026-07 | LangChain・ChromaDB・Streamlitを使ったRAGアプリを構築 |
| 2026-07 | Streamlit Cloudへのデプロイ、requirements.txtの改行コード問題を解決 |
| 2026-07 | Embeddingモデルをtext-embedding-004に更新、PDFアップロード機能を追加 |

