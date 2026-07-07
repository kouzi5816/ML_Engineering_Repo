# ベースイメージ（Python 3.11 スリム版）
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係を先にコピー（キャッシュを効かせるため）
COPY requirements.txt .

# パッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリのコードをコピー
COPY app.py .

# Cloud Runはポート8080を使う（Streamlitのデフォルトは8501なので変更）
EXPOSE 8080

# 起動コマンド
CMD ["streamlit", "run", "app.py",
     "--server.port=8080",
     "--server.address=0.0.0.0",
     "--server.headless=true"]