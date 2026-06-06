# Образ приложения: FastAPI-сервис поиска дубликатов
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

# Ставим CPU-версию PyTorch отдельно, с официального CPU-индекса.
# Иначе под Linux pip тянет GPU-сборку с многогигабайтными CUDA-библиотеками,
# которые нам не нужны (инференс идёт на CPU).
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Остальные зависимости. torch уже установлен (CPU), повторно не скачивается.
RUN pip install --no-cache-dir -r requirements.txt

# Код приложения и веб-страница
COPY app ./app
COPY web ./web

EXPOSE 8000

# host 0.0.0.0 — чтобы сервис был доступен снаружи контейнера
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
