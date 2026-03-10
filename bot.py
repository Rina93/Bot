import json
import os
import random
import datetime
from telegram import Update, InputFile
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    JobQueue
)

# Настройки
TOKEN = '7907821821:AAFZPXf5Xw9wFRrXt630Ud-IM7vmv7YvoZc'
DATA_USERS = 'data/users.json'
DATA_SUBMISSIONS = 'data/submissions.json'

# Функции работы с данными
def load_users():
    if not os.path.exists(DATA_USERS):
        return {}
    with open(DATA_USERS, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    with open(DATA_USERS, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def load_submissions():
    if not os.path.exists(DATA_SUBMISSIONS):
        return {}
    with open(DATA_SUBMISSIONS, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_submissions(submissions):
    with open(DATA_SUBMISSIONS, 'w', encoding='utf-8') as f:
        json.dump(submissions, f, ensure_ascii=False, indent=4)

# Генератор тем
def generate_theme():
    themes = ["Природа", "Космос", "Город", "Магия", "Технологии"]
    if random.random() < 0.5:
        return random.choice(themes)
    else:
        return f"{random.choice(themes)} + {random.choice(themes)}"

# Мотивационные фразы
def get_motivation():
    return random.choice([
        "Не бойся ошибаться — бойся не пробовать.",
        "Ты становишься лучше с каждой работой!",
        "У тебя уникальный стиль — развивай его.",
        "Искусство — это когда ты продолжаешь, даже если ничего не получается.",
        "Каждая работа делает тебя сильнее."
    ])

# === Референсы ===
def send_reference(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    users = load_users()

    if user_id not in users:
        update.message.reply_text("Сначала зарегистрируйтесь командой /reg [имя]")
        return

    if len(context.args) == 0:
        update.message.reply_text("Укажите категорию: /reference позы | люди")
        return

    category = context.args[0]
    folder = f'references/{category}'

    if not os.path.exists(folder):
        update.message.reply_text(f"Категория '{category}' не найдена.")
        return

    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if not files:
        update.message.reply_text(f"Нет референсов в категории '{category}'.")
        return

    file = random.choice(files)
    path = os.path.join(folder, file)

    try:
        with open(path, 'rb') as photo:
            update.message.reply_photo(photo=photo, caption=f"Референс: {file}")
    except Exception as e:
        update.message.reply_text("Ошибка при загрузке референса.")
        print(e)

# Команды
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я Владыка Красок 🎨\n"
                              "Регистрируйся командой /reg [имя]")

def register(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    users = load_users()

    if user_id in users:
        update.message.reply_text("Вы уже зарегистрированы как " + users[user_id]['name'])
        return

    if len(context.args) == 0:
        update.message.reply_text("Укажите имя после команды /reg")
        return

    name = ' '.join(context.args)
    users[user_id] = {
        'name': name,
        'rating': 10
    }
    save_users(users)
    update.message.reply_text(f"Поздравляем, {name}! Вы зарегистрированы!")

def theme(update: Update, context: CallbackContext):
    chosen = generate_theme()
    update.message.reply_text(f"Ваша тема: *{chosen}*", parse_mode='Markdown')

def rating(update: Update, context: CallbackContext):
    users = load_users()
    sorted_users = sorted(users.items(), key=lambda x: x[1]['rating'], reverse=True)
    top = "\n".join([f"{i+1}. {u[1]['name']} — {u[1]['rating']}" for i, u in enumerate(sorted_users[:10])])
    update.message.reply_text("🏆 Топ участников:\n" + top)

def motivation(update: Update, context: CallbackContext):
    update.message.reply_text(get_motivation())

def photo_handler(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    users = load_users()

    if user_id not in users:
        update.message.reply_text("Сначала зарегистрируйтесь командой /reg [имя]")
        return

    week = datetime.datetime.now().isocalendar()[1]
    submissions = load_submissions()
    key = f"{user_id}_{week}"

    submissions[key] = {
        "user_id": user_id,
        "week": week,
        "timestamp": datetime.datetime.now().isoformat()
    }
    save_submissions(submissions)

    update.message.reply_text("✅ Работа принята!")
    update.message.reply_text(evaluate_art())

def evaluate_art():
    responses = [
        "Вау, это шедевр!",
        "Интересная композиция, но добавь больше света.",
        "Красивые цвета! Может, сделай персонажа более чётким?",
        "Крутой стиль! Ты явно прогрессируешь.",
        "Хорошо, но поработай над деталями.",
        "Очень креативно! Так держать!"
    ]
    return random.choice(responses)

def done(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    users = load_users()

    if user_id not in users:
        update.message.reply_text("Сначала зарегистрируйтесь командой /reg [имя]")
        return

    week = datetime.datetime.now().isocalendar()[1]
    submissions = load_submissions()
    key = f"{user_id}_{week}"

    if key in submissions:
        update.message.reply_text("Вы уже отметили выполнение задания этой недели.")
        return

    submissions[key] = {
        "user_id": user_id,
        "week": week,
        "timestamp": datetime.datetime.now().isoformat()
    }
    save_submissions(submissions)
    users[user_id]['rating'] += 1
    save_users(users)
    update.message.reply_text("✅ Задание отмечено выполненным! Ваш рейтинг повышен.")

# Расписание заданий
def send_task(context: CallbackContext):
    theme = generate_theme()
    users = load_users()
    for user_id in users:
        try:
            context.bot.send_message(user_id, f"🎨 Новое задание!\n\n*{theme}*\n\nСдайте работу до воскресенья!", parse_mode='Markdown')
        except Exception as e:
            print(f"Не могу отправить сообщение {user_id}: {e}")

def check_debtors(context: CallbackContext):
    now = datetime.datetime.now()
    week = now.isocalendar()[1]
    users = load_users()
    submissions = load_submissions()

    for user_id in users:
        key = f"{user_id}_{week}"
        if key not in submissions:
            users[user_id]['rating'] -= 1
            try:
                context.bot.send_message(user_id, "❌ Вы не сдали задание. Ваш рейтинг понижен.")
            except Exception as e:
                print(f"Ошибка при уведомлении {user_id}: {e}")
        else:
            try:
                context.bot.send_message(user_id, "✅ Молодец! Рейтинг повышен за сданную работу.")
            except Exception as e:
                print(f"Ошибка при уведомлении {user_id}: {e}")

    save_users(users)

def setup_scheduler(dp: JobQueue):
    dp.run_daily(send_task, datetime.time(hour=12, minute=0), days=(1,))  # Вторник
    dp.run_daily(send_task, datetime.time(hour=12, minute=0), days=(4,))  # Пятница
    dp.run_daily(check_debtors, datetime.time(hour=18, minute=0), days=(6,))  # Воскресенье

# Запуск бота
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("reg", register))
    dp.add_handler(CommandHandler("theme", theme))
    dp.add_handler(CommandHandler("rating", rating))
    dp.add_handler(CommandHandler("motivation", motivation))
    dp.add_handler(CommandHandler("reference", send_reference))
    dp.add_handler(CommandHandler("done", done))
    dp.add_handler(MessageHandler(Filters.photo, photo_handler))

    setup_scheduler(dp.job_queue)

    print("Бот запущен...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
