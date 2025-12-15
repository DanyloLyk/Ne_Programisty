# === ЕТАП 1: Будівельник (Builder) ===
# Беремо легкий Linux (Alpine) з Python 3.11
FROM python:3.11-alpine AS builder

# Робимо робочу папку /app
WORKDIR /app

# Встановлюємо компілятори, потрібні для деяких бібліотек Python
# Це потрібно, щоб pip install не впав з помилкою
RUN apk add --no-cache gcc musl-dev libffi-dev

# Копіюємо список бібліотек
COPY requirements.txt .

# Встановлюємо бібліотеки в спеціальну папку (.local)
RUN pip install --no-cache-dir --user -r requirements.txt

# === ЕТАП 2: Фінальний (Final) ===
# Беремо чистий Linux знову
FROM python:3.11-alpine

# Щоб показувало відразу логи, а не збирало їх
ENV PYTHONUNBUFFERED=1

# Робоча папка
WORKDIR /app

# Встановлюємо wget для перевірки здоров'я сервера (Healthcheck)
RUN apk add --no-cache wget

# Копіюємо встановлені бібліотеки з першого етапу (щоб не компілювати знову)
COPY --from=builder /root/.local /root/.local

# Налаштовуємо шляхи, щоб Python бачив бібліотеки
ENV PATH=/root/.local/bin:$PATH

# Створюємо папку для бази даних і даємо їй права (щоб не було помилок доступу)
RUN mkdir -p /app/data && chmod 777 /app/data

# Копіюємо ВЕСЬ код проекту в контейнер
COPY . .

# Відкриваємо порт 5000 (стандарт Flask)
EXPOSE 5000

# Перевірка: чи живий сервер? 
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:5000/ || exit 1

# Команда запуску програми 
CMD ["python", "app.py"]