# 🤖 Telegram Bot с Webhook на Render.com (бесплатно!)

Этот бот работает через **webhook** и развернут на **Render.com** — бесплатно, без кредитной карты.

## ✅ Как использовать

1. Создайте бота у [@BotFather](https://t.me/BotFather) и скопируйте `BOT_TOKEN`
2. Разверните этот репозиторий на [Render.com](https://render.com)
3. В настройках Render → **Environment Variables** добавьте:
   - `BOT_TOKEN` → ваш токен
   - `WEBHOOK_URL` → `https://ваш-апп-на-render.onrender.com`
4. Готово! Бот работает 24/7.

> 💡 Не коммитите `.env` — используйте переменные окружения на Render!

[Инструкция по деплою на Render](https://render.com/docs/deploy-python-web-apps)
