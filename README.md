# 🤖 Telegram Bot — Генерация изображений + Музыка

Профессиональный async Telegram-бот на Python + aiogram 3.x.

---

## ✨ Возможности

| Функция | Описание |
|---------|----------|
| 🎨 Генерация изображений | DALL·E 3 / Stability AI, 5 стилей, 3 размера |
| 🎵 Поиск музыки | YouTube, TikTok, Instagram, по названию/исполнителю |
| 🔍 Распознавание | Shazam через ссылку на видео или аудиофайл |
| 👤 Профиль | История генераций и музыки |
| ⚙️ Настройки | Стиль/размер по умолчанию, уведомления |
| 🌐 Мультиязычность | RU / EN / UZ |

---

## 🚀 Быстрый старт

### 1. Клонируй проект
```bash
git clone https://github.com/your/bot.git
cd bot
```

### 2. Скопируй и заполни `.env`
```bash
cp .env.example .env
nano .env
```

Обязательные поля:
```
BOT_TOKEN=        # от @BotFather
OPENAI_API_KEY=   # от platform.openai.com (для генерации картинок)
```

### 3. Установи зависимости
```bash
# Системные (Ubuntu/Debian)
sudo apt install ffmpeg python3.12 python3-pip -y

# Python
pip install -r requirements.txt
```

### 4. Запусти
```bash
python bot.py
```

---

## 🐳 Docker

```bash
# Сборка и запуск
docker compose up -d --build

# Логи
docker compose logs -f bot

# Остановка
docker compose down
```

---

## ☁️ Деплой на VPS (Ubuntu)

```bash
# Установка
sudo apt update && sudo apt install docker.io docker-compose ffmpeg -y
git clone https://github.com/your/bot.git && cd bot
cp .env.example .env && nano .env

# Запуск
docker compose up -d --build

# Автозапуск при перезагрузке — уже настроен через restart: unless-stopped
```

---

## ☁️ Render / Railway

1. Создай новый **Web Service** (Render) или **Service** (Railway)
2. Подключи репозиторий
3. Добавь переменные окружения из `.env.example`
4. Build command: `pip install -r requirements.txt`
5. Start command: `python bot.py`

> ⚠️ На бесплатных тарифах Render бот «засыпает» через 15 мин неактивности.  
> Используй Railway или VPS для production.

---

## 📁 Структура проекта

```
├── bot.py                  # Точка входа
├── config/
│   └── config.py           # Настройки через pydantic-settings
├── handlers/
│   ├── start.py            # /start, /help, язык
│   ├── image.py            # Генерация изображений
│   ├── music.py            # Поиск и скачивание музыки
│   ├── recognize.py        # Распознавание
│   └── profile.py          # Профиль и настройки
├── services/
│   ├── image_service.py    # OpenAI / Stability AI
│   ├── music_service.py    # yt-dlp поиск и скачивание
│   └── recognize_service.py# shazamio распознавание
├── database/
│   ├── models.py           # SQLAlchemy модели
│   ├── engine.py           # Async engine
│   └── crud.py             # CRUD операции
├── keyboards/
│   └── keyboards.py        # Все клавиатуры
├── middlewares/
│   └── middlewares.py      # User, AntiSpam, Logging
├── states/
│   └── states.py           # FSM состояния
├── utils/
│   ├── helpers.py          # Форматирование, валидация
│   └── logger.py           # Настройка логов
├── data/                   # SQLite база данных
├── downloads/              # Временные файлы
├── logs/                   # Лог-файлы
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## 🔑 API ключи

| Ключ | Где получить | Обязателен |
|------|-------------|------------|
| `BOT_TOKEN` | [@BotFather](https://t.me/BotFather) | ✅ |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) | Для генерации |
| `STABILITY_API_KEY` | [stability.ai](https://stability.ai) | Альтернатива OpenAI |
| `ACRCLOUD_*` | [acrcloud.com](https://acrcloud.com) | Для ACRCloud |

> shazamio работает без API-ключа — достаточно установить библиотеку.

---

## ⚙️ Лимиты (настраиваются в .env)

```
RATE_LIMIT_IMAGE=10      # Генераций в час
RATE_LIMIT_MUSIC=20      # Поисков в час  
RATE_LIMIT_RECOGNIZE=15  # Распознаваний в час
MAX_FILE_SIZE_MB=50      # Максимальный размер файла
```

---

## 📝 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Главное меню |
| `/help` | Справка |
| `/image` | Генерация картинки |
| `/music` | Поиск музыки |
| `/recognize` | Распознать трек |
| `/profile` | Мой профиль |
| `/settings` | Настройки |

---

## 🛡️ Безопасность

- Валидация всех входящих URL
- Антиспам (throttle 0.7 сек)
- Почасовые лимиты на каждую функцию
- Ограничение размера файлов
- Бан-система для пользователей
- Скачанные файлы удаляются после отправки

---

## 📄 Лицензия

MIT
