# === ЕТАП 1: Будівельник (Builder) ===
FROM python:3.11-alpine AS builder

# Робоча папка
WORKDIR /app

# Встановлюємо компілятори, потрібні для деяких бібліотек Python
# Це потрібно, щоб pip install не впав з помилкою
RUN apk add --no-cache gcc musl-dev libffi-dev

# Копіюємо список бібліотек
COPY requirements.txt .

# Встановлюємо залежності в user site-packages
RUN pip install --no-cache-dir --user -r requirements.txt

# === ЕТАП 2: Фінальний (Final) ===
FROM python:3.11-alpine

# Щоб Python показував логи відразу
ENV PYTHONUNBUFFERED=1

# Робоча папка
WORKDIR /app

# Копіюємо встановлені бібліотеки з етапу builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Встановлюємо wget для healthcheck
RUN apk add --no-cache wget

# Копіюємо ВЕСЬ код проекту в контейнер
COPY . .

# Підвантажуємо змінні середовища з .env
RUN pip install --no-cache-dir python-dotenv

# Створюємо папку для бази даних
RUN mkdir -p /app/data && chmod 755 /app/data

# Відкриваємо порт Flask
EXPOSE 5000

# Перевірка: чи живий сервер? 
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:5000/ || exit 1

# Команда запуску програми 
CMD ["python", "app.py"]
