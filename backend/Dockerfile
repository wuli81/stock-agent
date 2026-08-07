FROM python:3.12-slim

WORKDIR /app

# 安装共享层与后端（shared 必须先于 backend 安装）
COPY shared /app/shared
COPY backend /app/backend
RUN pip install --no-cache-dir /app/shared && \
    pip install --no-cache-dir /app/backend

WORKDIR /app/backend
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health')"

# 启动前先执行数据库迁移，再启动 API
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]