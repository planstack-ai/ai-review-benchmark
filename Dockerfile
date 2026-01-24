FROM python:3.11-slim

WORKDIR /app

# システム依存関係
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコード
COPY . .

# 結果出力ディレクトリ
RUN mkdir -p /app/results

ENTRYPOINT ["python", "scripts/runner.py"]
CMD ["--help"]
