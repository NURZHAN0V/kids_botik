from игры.виселица import функция_виселица
from игры.угадайка import функция_угадайка
from игры.морскойбой import создать_игру_морской_бой, создать_кнопки_морской_бой, обработать_ход_морской_бой
from игры.тривряд import (
    создать_игру_три_в_ряд, создать_кнопки_три_в_ряд, обработать_ход_три_в_ряд, 
    обмен_клеток, создать_текст_игры, создать_текст_результата, 
    проверить_доступные_ходы, перетасовать_поле, сохранить_результат_в_бд,
    получить_таблицу_лидеров, получить_позицию_пользователя, создать_текст_таблицы_лидеров
)
from typing import Optional
from игры.крестикинолики import функция_крестики_нолики
from игры.дино import функция_дино

# Импорты для Telegram бота
try:
    import telebot
    from config import TELEGRAM_BOT_TOKEN, ONLY_TELEGRAM
    telegram_available = True
except ImportError:
    telegram_available = False
    TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    ONLY_TELEGRAM = None
    print("⚠️ Для работы с Telegram установите: pip install pyTelegramBotAPI")
except:
    telegram_available = False
    TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    ONLY_TELEGRAM = None
    print("⚠️ Проверьте настройки в файле config.py")

# Состояния игр для Telegram пользователей
игры_виселица = {}
игры_угадайка = {}
игры_морской_бой = {}
игры_крестики_нолики = {}
игры_три_в_ряд = {}

def создать_игру_виселица(user_id, уровень):
    """Создание новой игры виселица для пользователя"""
    import random
    слова = {
        "легкий": ['кот', 'пёс', 'дом', 'лес', 'свет'],
        "средний": ['стол', 'луна', 'река', 'ночь', 'тень'],
        "сложный": ['пример', 'улыбка', 'картина', 'решение']
    }
    
    слово = random.choice(слова[уровень])
    игры_виселица[user_id] = {
        'слово': слово,
        'угадано': ['_'] * len(слово),
        'попытки': 7 if уровень == "легкий" else 5 if уровень == "средний" else 3,
        'уровень': уровень
    }

def обработать_ход_виселица(user_id, буква):
    """Обработка хода в игре виселица"""
    игра = игры_виселица[user_id]
    слово = игра['слово']
    угадано = игра['угадано']
    
    if буква in слово:
        for i in range(len(слово)):
            if слово[i] == буква:
                угадано[i] = буква
        результат = "✅ Есть такая буква!"
    else:
        игра['попытки'] -= 1
        результат = "❌ Нет такой буквы"
    
    # Формируем состояние игры
    состояние = f"Слово: {' '.join(угадано)}\nОсталось попыток: {игра['попытки']}"
    
    # Проверяем окончание игры
    if '_' not in угадано:
        del игры_виселица[user_id]
        return f"{результат}\n{состояние}\n\n🎉 Поздравляю! Ты угадал слово: {слово}!\nЧтобы сыграть ещё, напиши 'виселица'"
    elif игра['попытки'] <= 0:
        del игры_виселица[user_id]
        return f"{результат}\n{состояние}\n\n💀 Ты проиграл. Слово было: {слово}\nЧтобы сыграть ещё, напиши 'виселица'"
    
    return f"{результат}\n{состояние}\n\nВведи следующую букву:"

def создать_игру_угадайка(user_id):
    """Создание новой игры угадайка"""
    import random
    игры_угадайка[user_id] = {
        'число': random.randint(1, 10),
        'попытки': 0
    }

def обработать_ход_угадайка(user_id, число_str):
    """Обработка хода в угадайке"""
    try:
        число = int(число_str)
        игра = игры_угадайка[user_id]
        игра['попытки'] += 1
        
        if число == игра['число']:
            del игры_угадайка[user_id]
            return f"🎉 Молодец! Ты угадал с {игра['попытки']} попытки!\nМоё число: {игра['число']}\nДля новой игры напиши 'угадайка'"
        elif число < игра['число']:
            return f"📈 Моё число больше! Попытка {игра['попытки']}\nВведи число:"
        else:
            return f"📉 Моё число меньше! Попытка {игра['попытки']}\nВведи число:"
    except:
        return "⚠️ Введи число от 1 до 10"



def создать_игру_крестики_нолики(user_id):
    """Создание новой игры крестики-нолики"""
    игры_крестики_нолики[user_id] = {
        'поле': [["⬜" for _ in range(3)] for _ in range(3)],
        'ходы': 0
    }

def создать_кнопки_крестики_нолики(поле):
    """Создание кнопок для крестиков-ноликов"""
    import telebot
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    for i in range(3):
        row = []
        for j in range(3):
            символ = поле[i][j]
            row.append(telebot.types.InlineKeyboardButton(символ, callback_data=f"tic_{i}_{j}"))
        markup.row(*row)
    return markup

def обработать_ход_крестики_нолики(user_id, x, y):
    """Обработка хода в крестиках-ноликах"""
    игра = игры_крестики_нолики[user_id]
    
    if игра['поле'][x][y] != "⬜":
        return None, "⚠️ Клетка занята"
    
    # Ход игрока
    игра['поле'][x][y] = "❌"
    игра['ходы'] += 1
    
    # Проверка победы игрока
    if проверить_победу_крестики_нолики(игра['поле'], "❌"):
        del игры_крестики_нолики[user_id]
        return None, "🎉 Ты победил!\nДля новой игры напиши 'крестики-нолики'"
    
    # Проверка ничьей
    if игра['ходы'] >= 9:
        del игры_крестики_нолики[user_id]
        return None, "🤝 Ничья!\nДля новой игры напиши 'крестики-нолики'"
    
    # Ход компьютера
    свободные = [(i, j) for i in range(3) for j in range(3) if игра['поле'][i][j] == "⬜"]
    if свободные:
        import random
        comp_x, comp_y = random.choice(свободные)
        игра['поле'][comp_x][comp_y] = "⭕"
        игра['ходы'] += 1
        
        # Проверка победы компьютера
        if проверить_победу_крестики_нолики(игра['поле'], "⭕"):
            del игры_крестики_нолики[user_id]
            return None, "💀 Победил компьютер\nДля новой игры напиши 'крестики-нолики'"
        
        # Проверка ничьей после хода компьютера
        if игра['ходы'] >= 9:
            del игры_крестики_нолики[user_id]
            return None, "🤝 Ничья!\nДля новой игры напиши 'крестики-нолики'"
    
    markup = создать_кнопки_крестики_нолики(игра['поле'])
    return markup, "Твой ход:"

def проверить_победу_крестики_нолики(поле, символ):
    """Проверка победы в крестиках-ноликах"""
    # Проверка строк
    for i in range(3):
        if all(поле[i][j] == символ for j in range(3)):
            return True
    
    # Проверка столбцов
    for j in range(3):
        if all(поле[i][j] == символ for i in range(3)):
            return True
    
    # Проверка диагоналей
    if all(поле[i][i] == символ for i in range(3)):
        return True
    if all(поле[i][2-i] == символ for i in range(3)):
        return True
    
    return False

def обработать_сообщение(сообщение, отправить_ответ, запустить_игру=None):
    """Универсальная функция обработки сообщений для консоли и Telegram"""
    сообщение = сообщение.strip().lower()

    if "привет" in сообщение:
        отправить_ответ("👮: Привет! Рад приветствовать 😊 Чем могу помочь?")

    elif "как дела" in сообщение:
        отправить_ответ("👮: У меня всё отлично, я в режиме онлайн и готов помогать! А у тебя?")

    elif "имя" in сообщение:
        отправить_ответ("👮: Меня зовут Помощник. Можно просто 👮.")

    elif "спасибо" in сообщение:
        отправить_ответ("👮: Всегда рад помочь! 😊")

    elif "пока" in сообщение or "выход" in сообщение:
        отправить_ответ("👮: До встречи! Надеюсь, тебе было весело 😄")

    elif ("виселиц" in сообщение or "угадай" in сообщение or "морской" in сообщение or "крестики" in сообщение or "дино" in сообщение or "три" in сообщение or "ряд" in сообщение) and запустить_игру is not None:
        # Обработка игр в Telegram
        if "виселиц" in сообщение: return "hangman_start"
        elif "угадай" in сообщение: return "guess_start"
        elif "морской" in сообщение: return "sea_start"
        elif "крестики" in сообщение: return "tic_start"
        elif "дино" in сообщение: return "dino_start"
        elif "три" in сообщение or "ряд" in сообщение: return "match_start"

    elif "игр" in сообщение:
        отправить_ответ("👮: Отлично! Я умею играть в:\n- Виселица (напиши 'виселица')\n- Угадай число (напиши 'угадайка')\n- Морской бой (напиши 'морской бой')\n- Крестики-нолики (напиши 'крестики-нолики')\n- Три в ряд (напиши 'три в ряд')\n- Дино (напиши 'дино')")

    elif "анекдот" in сообщение:
        отправить_ответ("👮: — Что сказал программист на свидании?\n— У меня \"404: чувство не найдено\".")

    elif "погода" in сообщение:
        отправить_ответ("👮: Я не слежу за погодой, но думаю, сегодня будет хорошее настроение 😉")

    elif "умеешь" in сообщение:
        отправить_ответ("👮: Я умею болтать, шутить, играть и немного думать... Но пока без интернета 😅")

    elif "почему" in сообщение:
        отправить_ответ("👮: Потому что кто-то когда-то написал код, который запустил меня в этот мир 🤖")

    else:
        отправить_ответ("👮: Хороший вопрос... Давай обсудим это по-другому?")



def запустить_бота():
    """Запуск Telegram бота"""
    if not telegram_available:
        print("❌ Telegram бот недоступен. Установите: pip install pyTelegramBotAPI")
        return False
    
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Настройте TELEGRAM_BOT_TOKEN в файле config.py")
        return False
    
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        # Сохраняем пользователя при первом взаимодействии
        from database import db
        db.save_user(
            message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        import telebot
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        
        # Кнопки игр
        games_row1 = [
            telebot.types.InlineKeyboardButton("🎯 Виселица", callback_data="menu_hangman"),
            telebot.types.InlineKeyboardButton("🎲 Угадайка", callback_data="menu_guess")
        ]
        games_row2 = [
            telebot.types.InlineKeyboardButton("🚢 Морской бой", callback_data="menu_sea"),
            telebot.types.InlineKeyboardButton("❌⭕ Крестики-нолики", callback_data="menu_tic")
        ]
        games_row3 = [
            telebot.types.InlineKeyboardButton("🎯 Три в ряд", callback_data="menu_match"),
            telebot.types.InlineKeyboardButton("🦕 Дино", callback_data="menu_dino")
        ]
        
        # Кнопки общения и статистики
        chat_row = [
            telebot.types.InlineKeyboardButton("💬 Поболтать", callback_data="menu_chat"),
            telebot.types.InlineKeyboardButton("😄 Анекдот", callback_data="menu_joke")
        ]
        
        # Кнопки статистики
        stats_row = [
            telebot.types.InlineKeyboardButton("🏆 Таблица лидеров", callback_data="menu_leaderboard"),
            telebot.types.InlineKeyboardButton("📊 Моя статистика", callback_data="menu_stats")
        ]
        
        markup.row(*games_row1)
        markup.row(*games_row2)
        markup.row(*games_row3)
        markup.row(*chat_row)
        markup.row(*stats_row)
        
        bot.reply_to(message, "👋 Привет! Я твой виртуальный помощник и игровой бот! 🎮\n\n"
                              "🎯 Выбери, чем хочешь заняться:\n\n"
                              "🎮 **Игры** - увлекательные развлечения\n"
                              "💬 **Общение** - просто поболтаем\n"
                              "📊 **Статистика** - таблица лидеров и твои результаты\n\n"
                              "Что выберешь?", reply_markup=markup)
    
    @bot.message_handler(commands=['menu'])
    def show_menu(message):
        import telebot
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        
        # Кнопки игр
        games_row1 = [
            telebot.types.InlineKeyboardButton("🎯 Виселица", callback_data="menu_hangman"),
            telebot.types.InlineKeyboardButton("🎲 Угадайка", callback_data="menu_guess")
        ]
        games_row2 = [
            telebot.types.InlineKeyboardButton("🚢 Морской бой", callback_data="menu_sea"),
            telebot.types.InlineKeyboardButton("❌⭕ Крестики-нолики", callback_data="menu_tic")
        ]
        games_row3 = [
            telebot.types.InlineKeyboardButton("🎯 Три в ряд", callback_data="menu_match"),
            telebot.types.InlineKeyboardButton("🦕 Дино", callback_data="menu_dino")
        ]
        
        # Кнопки общения и статистики
        chat_row = [
            telebot.types.InlineKeyboardButton("💬 Поболтать", callback_data="menu_chat"),
            telebot.types.InlineKeyboardButton("😄 Анекдот", callback_data="menu_joke")
        ]
        
        # Кнопки статистики
        stats_row = [
            telebot.types.InlineKeyboardButton("🏆 Таблица лидеров", callback_data="menu_leaderboard"),
            telebot.types.InlineKeyboardButton("📊 Моя статистика", callback_data="menu_stats")
        ]
        
        markup.row(*games_row1)
        markup.row(*games_row2)
        markup.row(*games_row3)
        markup.row(*chat_row)
        markup.row(*stats_row)
        
        bot.reply_to(message, "🎮 **Главное меню**\n\n"
                              "Выбери игру или действие:", reply_markup=markup)
    
    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        user_id = message.from_user.id
        текст = message.text.strip().lower()
        
        def отправить_ответ(текст):
            bot.reply_to(message, текст)
        
        # Обрабатываем команду "стоп"
        if текст == "стоп":
            игра_остановлена = False
            if user_id in игры_виселица: 
                del игры_виселица[user_id]
                игра_остановлена = True
            elif user_id in игры_угадайка: 
                del игры_угадайка[user_id]
                игра_остановлена = True
            elif user_id in игры_морской_бой: 
                del игры_морской_бой[user_id]
                игра_остановлена = True
            elif user_id in игры_крестики_нолики: 
                del игры_крестики_нолики[user_id]
                игра_остановлена = True
            elif user_id in игры_три_в_ряд: 
                del игры_три_в_ряд[user_id]
                игра_остановлена = True
            
            if игра_остановлена:
                отправить_ответ("👮: Игра остановлена. Напиши название игры для запуска новой!")
            else:
                отправить_ответ("👮: Ты не в игре. Напиши название игры для запуска!")
            return

        # Проверяем активные игры
        if user_id in игры_виселица:
            if len(текст) == 1 and текст.isalpha():
                результат = обработать_ход_виселица(user_id, текст)
                отправить_ответ(результат)
            else:
                отправить_ответ("Пожалуйста, введи одну букву или 'стоп'")
            return
        elif user_id in игры_угадайка:
            if текст.isdigit():
                результат = обработать_ход_угадайка(user_id, текст)
                отправить_ответ(результат)
            else:
                отправить_ответ("Введи число от 1 до 10 или 'стоп'")
            return
        elif user_id in игры_морской_бой:
            отправить_ответ("Используй кнопки для игры или напиши 'стоп'")
            return
        elif user_id in игры_крестики_нолики:
            отправить_ответ("Используй кнопки для игры или напиши 'стоп'")
            return
        elif user_id in игры_три_в_ряд:
            отправить_ответ("Используй кнопки для игры или напиши 'стоп'")
            return
        
        # Обычная обработка сообщений
        результат = обработать_сообщение(message.text, отправить_ответ, запустить_игру=True)
        
        # Запуск игр
        if результат == "hangman_start":
            отправить_ответ("🎮 Выбери уровень:\n\n1️⃣ легкий (7 попыток)\n2️⃣ средний (5 попыток)\n3️⃣ сложный (3 попытки)\n\nНапиши: легкий, средний или сложный")
        elif результат == "guess_start":
            создать_игру_угадайка(user_id)
            отправить_ответ("🎯 Я загадал число от 1 до 10!\nВведи своё число или 'стоп' для выхода:")
        elif результат == "sea_start":
            игра = создать_игру_морской_бой(user_id)
            игры_морской_бой[user_id] = игра
            markup = создать_кнопки_морской_бой(игра['поле'])
            bot.reply_to(message, "🚢 Морской бой!\nФлот: 1×3, 2×2, 3×1\nНажми на клетку:", reply_markup=markup)
            return
        elif результат == "tic_start":
            создать_игру_крестики_нолики(user_id)
            игра = игры_крестики_нолики[user_id]
            markup = создать_кнопки_крестики_нолики(игра['поле'])
            bot.reply_to(message, "❌⭕ Крестики-нолики!\nТы играешь за ❌\nВыбери клетку:", reply_markup=markup)
            return
        elif результат == "dino_start":
            отправить_ответ("🦕 Дино - простая текстовая игра, лучше работает в консоли.\nПопробуйте другие игры!")
        elif результат == "match_start":
            import time
            игра = создать_игру_три_в_ряд(user_id)
            игра['время_начала'] = time.time()
            игры_три_в_ряд[user_id] = игра
            markup = создать_кнопки_три_в_ряд(игра['поле'])
            bot.reply_to(message, создать_текст_игры(игра), reply_markup=markup)
            return
        else:
            # Если не распознали команду, показываем меню
            import telebot
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            
            games_row1 = [
                telebot.types.InlineKeyboardButton("🎯 Виселица", callback_data="menu_hangman"),
                telebot.types.InlineKeyboardButton("🎲 Угадайка", callback_data="menu_guess")
            ]
            games_row2 = [
                telebot.types.InlineKeyboardButton("🚢 Морской бой", callback_data="menu_sea"),
                telebot.types.InlineKeyboardButton("❌⭕ Крестики-нолики", callback_data="menu_tic")
            ]
            games_row3 = [
                telebot.types.InlineKeyboardButton("🎯 Три в ряд", callback_data="menu_match"),
                telebot.types.InlineKeyboardButton("🦕 Дино", callback_data="menu_dino")
            ]
            
            chat_row = [
                telebot.types.InlineKeyboardButton("💬 Поболтать", callback_data="menu_chat"),
                telebot.types.InlineKeyboardButton("😄 Анекдот", callback_data="menu_joke")
            ]
            
            markup.row(*games_row1)
            markup.row(*games_row2)
            markup.row(*games_row3)
            markup.row(*chat_row)
            
            bot.reply_to(message, "🤔 Не совсем понял, что ты хочешь...\n\n"
                                  "🎮 Выбери игру или действие из меню:", reply_markup=markup)
        
        # Обработка выбора уровня для виселицы
        if результат is None and текст in ["легкий", "средний", "сложный"] and user_id not in игры_виселица:
            создать_игру_виселица(user_id, текст)
            игра = игры_виселица[user_id]
            состояние = f"Слово: {' '.join(игра['угадано'])}\nОсталось попыток: {игра['попытки']}"
            отправить_ответ(f"🎯 Игра начата!\n{состояние}\n\nВведи букву или 'стоп':")
    
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        user_id = call.from_user.id
        data = call.data
        
        # Обработка меню
        if data.startswith("menu_"):
            if data == "menu_hangman":
                # Показываем уровни для виселицы
                import telebot
                markup = telebot.types.InlineKeyboardMarkup(row_width=1)
                markup.row(telebot.types.InlineKeyboardButton("🟢 Легкий (7 попыток)", callback_data="level_easy"))
                markup.row(telebot.types.InlineKeyboardButton("🟡 Средний (5 попыток)", callback_data="level_medium"))
                markup.row(telebot.types.InlineKeyboardButton("🔴 Сложный (3 попытки)", callback_data="level_hard"))
                markup.row(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="menu_back"))
                
                try:
                    bot.edit_message_text("🎯 **Виселица**\n\n"
                                          "Выбери уровень сложности:\n\n"
                                          "🟢 **Легкий** - 7 попыток, простые слова\n"
                                          "🟡 **Средний** - 5 попыток, обычные слова\n"
                                          "🔴 **Сложный** - 3 попытки, сложные слова", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
                    
            elif data == "menu_guess":
                # Запускаем угадайку
                создать_игру_угадайка(user_id)
                import telebot
                markup = telebot.types.InlineKeyboardMarkup()
                markup.row(telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back"))
                
                try:
                    bot.edit_message_text("🎲 **Угадай число**\n\n"
                                          "Я загадал число от 1 до 10!\n\n"
                                          "💡 Введи своё число в чат или нажми 'стоп' для выхода", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
                    
            elif data == "menu_sea":
                # Запускаем морской бой
                игра = создать_игру_морской_бой(user_id)
                игры_морской_бой[user_id] = игра
                markup = создать_кнопки_морской_бой(игра['поле'])
                
                try:
                    bot.edit_message_text("🚢 **Морской бой**\n\n"
                                          "Флот: 1×3, 2×2, 3×1\n"
                                          "Нажми на клетку для выстрела!", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
                    
            elif data == "menu_tic":
                # Запускаем крестики-нолики
                создать_игру_крестики_нолики(user_id)
                игра = игры_крестики_нолики[user_id]
                markup = создать_кнопки_крестики_нолики(игра['поле'])
                
                try:
                    bot.edit_message_text("❌⭕ **Крестики-нолики**\n\n"
                                          "Ты играешь за ❌\n"
                                          "Выбери клетку для хода!", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
                    
            elif data == "menu_match":
                # Запускаем три в ряд
                import time
                
                # Сохраняем пользователя при запуске игры
                from database import db
                db.save_user(
                    user_id,
                    username=call.from_user.username,
                    first_name=call.from_user.first_name,
                    last_name=call.from_user.last_name
                )
                
                игра = создать_игру_три_в_ряд(user_id)
                игра['время_начала'] = time.time()
                игры_три_в_ряд[user_id] = игра
                markup = создать_кнопки_три_в_ряд(игра['поле'])
                
                try:
                    bot.edit_message_text(создать_текст_игры(игра), 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
                    
            elif data == "menu_dino":
                # Дино игра
                import telebot
                markup = telebot.types.InlineKeyboardMarkup()
                markup.row(telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back"))
                
                try:
                    bot.edit_message_text("🦕 **Дино**\n\n"
                                          "Это простая текстовая игра, которая лучше работает в консоли.\n\n"
                                          "🎮 Попробуй другие игры из меню!", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
                    
            elif data == "menu_chat":
                # Общение
                import telebot
                markup = telebot.types.InlineKeyboardMarkup(row_width=2)
                chat_buttons = [
                    telebot.types.InlineKeyboardButton("👋 Привет", callback_data="chat_hello"),
                    telebot.types.InlineKeyboardButton("😊 Как дела?", callback_data="chat_how_are_you"),
                    telebot.types.InlineKeyboardButton("🤔 Кто ты?", callback_data="chat_who_are_you"),
                    telebot.types.InlineKeyboardButton("💭 Расскажи о себе", callback_data="chat_about"),
                    telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back")
                ]
                markup.row(chat_buttons[0], chat_buttons[1])
                markup.row(chat_buttons[2], chat_buttons[3])
                markup.row(chat_buttons[4])
                
                try:
                    bot.edit_message_text("💬 **Общение**\n\n"
                                          "Привет! Давай поболтаем! 😊\n\n"
                                          "Выбери тему для разговора:", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
                    
            elif data == "menu_joke":
                # Анекдот
                import telebot
                markup = telebot.types.InlineKeyboardMarkup()
                markup.row(telebot.types.InlineKeyboardButton("😄 Ещё анекдот", callback_data="menu_joke"))
                markup.row(telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back"))
                
                анекдоты = [
                    "— Что сказал программист на свидании?\n— У меня \"404: чувство не найдено\".",
                    "— Почему программисты путают Рождество и Хэллоуин?\n— Потому что Oct 31 == Dec 25",
                    "— Как программист ломает голову?\n— Git push --force",
                    "— Что сказал программист, когда упал с лестницы?\n— Ошибка 500: Internal Server Error",
                    "— Почему программисты не любят природу?\n— Там слишком много багов"
                ]
                import random
                анекдот = random.choice(анекдоты)
                
                try:
                    bot.edit_message_text(f"😄 **Анекдот**\n\n{анекдот}", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
                    
            elif data == "menu_leaderboard":
                # Таблица лидеров
                try:
                    лидеры = получить_таблицу_лидеров(10)
                    позиция_пользователя = получить_позицию_пользователя(user_id)
                    текст_лидеров = создать_текст_таблицы_лидеров(лидеры, позиция_пользователя)
                    
                    import telebot
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.row(telebot.types.InlineKeyboardButton("🔄 Обновить", callback_data="menu_leaderboard"))
                    markup.row(telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back"))
                    
                    bot.edit_message_text(текст_лидеров, call.message.chat.id, call.message.message_id, reply_markup=markup)
                except Exception as e:
                    import telebot
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.row(telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back"))
                    
                    bot.edit_message_text(f"❌ Ошибка загрузки таблицы лидеров: {str(e)}", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                    
            elif data == "menu_stats":
                # Моя статистика
                try:
                    from database import db
                    
                    # Сохраняем пользователя
                    db.save_user(user_id, 
                                username=call.from_user.username,
                                first_name=call.from_user.first_name,
                                last_name=call.from_user.last_name)
                    
                    # Получаем статистику
                    stats = db.get_user_stats(user_id, "три_в_ряд")
                    achievements = db.get_user_achievements(user_id, "три_в_ряд")
                    
                    if stats:
                        текст_статистики = f"📊 **Моя статистика - Три в ряд**\n\n" \
                                          f"🎮 Игр сыграно: {stats['games_played']}\n" \
                                          f"🏆 Лучший счёт: {stats['best_score']}\n" \
                                          f"📈 Средний счёт: {stats['avg_score']}\n" \
                                          f"🎯 Всего ходов: {stats['total_moves']}\n" \
                                          f"⏱️ Общее время: {stats['total_time']} сек"
                        
                        if achievements:
                            текст_статистики += f"\n\n🏅 **Достижения:**\n" + "\n".join(achievements)
                        else:
                            текст_статистики += "\n\n🏅 Достижения: пока нет"
                    else:
                        текст_статистики = "📊 **Моя статистика - Три в ряд**\n\n" \
                                          "🎮 Ты ещё не играл в эту игру!\n" \
                                          "🎯 Попробуй сыграть и установить рекорд!"
                    
                    import telebot
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.row(telebot.types.InlineKeyboardButton("🎯 Играть", callback_data="menu_match"))
                    markup.row(telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back"))
                    
                    bot.edit_message_text(текст_статистики, call.message.chat.id, call.message.message_id, reply_markup=markup)
                except Exception as e:
                    import telebot
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.row(telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back"))
                    
                    bot.edit_message_text(f"❌ Ошибка загрузки статистики: {str(e)}", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                    
            elif data == "menu_back":
                # Возврат в главное меню
                import telebot
                markup = telebot.types.InlineKeyboardMarkup(row_width=2)
                
                games_row1 = [
                    telebot.types.InlineKeyboardButton("🎯 Виселица", callback_data="menu_hangman"),
                    telebot.types.InlineKeyboardButton("🎲 Угадайка", callback_data="menu_guess")
                ]
                games_row2 = [
                    telebot.types.InlineKeyboardButton("🚢 Морской бой", callback_data="menu_sea"),
                    telebot.types.InlineKeyboardButton("❌⭕ Крестики-нолики", callback_data="menu_tic")
                ]
                games_row3 = [
                    telebot.types.InlineKeyboardButton("🎯 Три в ряд", callback_data="menu_match"),
                    telebot.types.InlineKeyboardButton("🦕 Дино", callback_data="menu_dino")
                ]
                
                chat_row = [
                    telebot.types.InlineKeyboardButton("💬 Поболтать", callback_data="menu_chat"),
                    telebot.types.InlineKeyboardButton("😄 Анекдот", callback_data="menu_joke")
                ]
                
                stats_row = [
                    telebot.types.InlineKeyboardButton("🏆 Таблица лидеров", callback_data="menu_leaderboard"),
                    telebot.types.InlineKeyboardButton("📊 Моя статистика", callback_data="menu_stats")
                ]
                
                markup.row(*games_row1)
                markup.row(*games_row2)
                markup.row(*games_row3)
                markup.row(*chat_row)
                markup.row(*stats_row)
                
                try:
                    bot.edit_message_text("🎮 **Главное меню**\n\n"
                                          "Выбери игру или действие:", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
        
        # Обработка уровней виселицы
        elif data.startswith("level_"):
            if data == "level_easy":
                создать_игру_виселица(user_id, "легкий")
                игра = игры_виселица[user_id]
                состояние = f"Слово: {' '.join(игра['угадано'])}\nОсталось попыток: {игра['попытки']}"
                
                import telebot
                markup = telebot.types.InlineKeyboardMarkup()
                markup.row(telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back"))
                
                try:
                    bot.edit_message_text(f"🎯 **Виселица - Легкий уровень**\n\n"
                                          f"Игра начата!\n{состояние}\n\n"
                                          f"💡 Введи букву в чат или 'стоп' для выхода", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
                    
            elif data == "level_medium":
                создать_игру_виселица(user_id, "средний")
                игра = игры_виселица[user_id]
                состояние = f"Слово: {' '.join(игра['угадано'])}\nОсталось попыток: {игра['попытки']}"
                
                import telebot
                markup = telebot.types.InlineKeyboardMarkup()
                markup.row(telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back"))
                
                try:
                    bot.edit_message_text(f"🎯 **Виселица - Средний уровень**\n\n"
                                          f"Игра начата!\n{состояние}\n\n"
                                          f"💡 Введи букву в чат или 'стоп' для выхода", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
                    
            elif data == "level_hard":
                создать_игру_виселица(user_id, "сложный")
                игра = игры_виселица[user_id]
                состояние = f"Слово: {' '.join(игра['угадано'])}\nОсталось попыток: {игра['попытки']}"
                
                import telebot
                markup = telebot.types.InlineKeyboardMarkup()
                markup.row(telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back"))
                
                try:
                    bot.edit_message_text(f"🎯 **Виселица - Сложный уровень**\n\n"
                                          f"Игра начата!\n{состояние}\n\n"
                                          f"💡 Введи букву в чат или 'стоп' для выхода", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
        
        # Обработка чата
        elif data.startswith("chat_"):
            if data == "chat_hello":
                import telebot
                markup = telebot.types.InlineKeyboardMarkup()
                markup.row(telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back"))
                
                try:
                    bot.edit_message_text("👋 **Привет!**\n\n"
                                          "Рад тебя видеть! 😊\n\n"
                                          "Я твой виртуальный помощник и игровой бот. "
                                          "Могу играть с тобой в разные игры, болтать и даже рассказывать анекдоты! 🎮", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
                    
            elif data == "chat_how_are_you":
                import telebot
                markup = telebot.types.InlineKeyboardMarkup()
                markup.row(telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back"))
                
                try:
                    bot.edit_message_text("😊 **Как дела?**\n\n"
                                          "У меня всё отлично! Я в режиме онлайн и готов помогать! 🚀\n\n"
                                          "А у тебя как дела? Надеюсь, тоже хорошо! 😄", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
                    
            elif data == "chat_who_are_you":
                import telebot
                markup = telebot.types.InlineKeyboardMarkup()
                markup.row(telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back"))
                
                try:
                    bot.edit_message_text("🤖 **Кто я?**\n\n"
                                          "Меня зовут Помощник! 👮\n\n"
                                          "Я виртуальный собеседник и игровой бот. "
                                          "Умею играть в разные игры, общаться и развлекать! "
                                          "Создан для того, чтобы сделать твоё время более интересным! 🎯", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
                    
            elif data == "chat_about":
                import telebot
                markup = telebot.types.InlineKeyboardMarkup()
                markup.row(telebot.types.InlineKeyboardButton("🔙 В меню", callback_data="menu_back"))
                
                try:
                    bot.edit_message_text("💭 **О себе**\n\n"
                                          "Я - искусственный интеллект, созданный для общения и развлечений! 🤖\n\n"
                                          "**Что я умею:**\n"
                                          "🎮 Играть в 6 разных игр\n"
                                          "💬 Общаться на разные темы\n"
                                          "😄 Рассказывать анекдоты\n"
                                          "🎯 Помогать и развлекать\n\n"
                                          "Моя цель - сделать твоё время более интересным! ✨", 
                                          call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
        
        elif data.startswith("sea_"):
            if user_id in игры_морской_бой:
                _, x, y = data.split("_")
                игра = игры_морской_бой[user_id]
                markup, текст = обработать_ход_морской_бой(игра, int(x), int(y))
                if markup:
                    try:
                        bot.edit_message_text(текст, call.message.chat.id, call.message.message_id, reply_markup=markup)
                    except:
                        pass
                else:
                    del игры_морской_бой[user_id]
                    try:
                        bot.edit_message_text(текст, call.message.chat.id, call.message.message_id)
                    except:
                        pass

        
        elif data.startswith("tic_"):
            if user_id in игры_крестики_нолики:
                _, x, y = data.split("_")
                markup, текст = обработать_ход_крестики_нолики(user_id, int(x), int(y))
                if markup:
                    try:
                        bot.edit_message_text(текст, call.message.chat.id, call.message.message_id, reply_markup=markup)
                    except:
                        pass
                else:
                    try:
                        bot.edit_message_text(текст, call.message.chat.id, call.message.message_id)
                    except:
                        pass
        
        elif data.startswith("match_"):
            if user_id in игры_три_в_ряд:
                игра = игры_три_в_ряд[user_id]
                
                # Обработка специальных команд
                if data == "match_cancel":
                    игра['выбранная_клетка'] = None
                    markup = создать_кнопки_три_в_ряд(игра['поле'])
                    try:
                        bot.edit_message_text(создать_текст_игры(игра), call.message.chat.id, call.message.message_id, reply_markup=markup)
                    except:
                        pass
                elif data == "match_end":
                    # Завершение игры
                    результат_текст = создать_текст_результата(игра)
                    
                    # Сохраняем результат в базу данных
                    try:
                        # Сохраняем пользователя с актуальными данными
                        from database import db
                        db.save_user(
                            user_id,
                            username=call.from_user.username,
                            first_name=call.from_user.first_name,
                            last_name=call.from_user.last_name
                        )
                        
                        is_personal_record, is_global_record, achievements = сохранить_результат_в_бд(user_id, игра)
                        
                        # Добавляем уведомления о рекордах
                        уведомления = ""
                        if is_global_record:
                            уведомления += "\n\n🏆🎉 **НОВЫЙ МИРОВОЙ РЕКОРД!** 🎉🏆"
                        elif is_personal_record:
                            уведомления += "\n\n🥇 **Новый личный рекорд!** 🥇"
                        
                        # Добавляем уведомления о достижениях
                        if achievements:
                            уведомления += "\n\n🏅 **Достижения:**\n" + "\n".join(achievements)
                        
                        # Проверяем позицию в таблице лидеров
                        позиция = получить_позицию_пользователя(user_id)
                        if позиция == 1:
                            уведомления += "\n\n👑 **Ты на первом месте!** 👑"
                        elif позиция and позиция <= 3:
                            уведомления += f"\n\n🥉 **Ты в топ-{позиция}!** 🥉"
                        
                        результат_текст += уведомления
                        
                    except Exception as e:
                        результат_текст += f"\n\n⚠️ Ошибка сохранения результата: {str(e)}"
                    
                    # Создаём кнопки для поделиться результатом
                    import telebot
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.row(telebot.types.InlineKeyboardButton("🏆 Таблица лидеров", 
                                                                callback_data="menu_leaderboard"))
                    markup.row(telebot.types.InlineKeyboardButton("📤 Поделиться результатом", 
                                                                callback_data="match_share"))
                    markup.row(telebot.types.InlineKeyboardButton("🔄 Новая игра", 
                                                                callback_data="match_new"))
                    
                    del игры_три_в_ряд[user_id]
                    try:
                        bot.edit_message_text(результат_текст, call.message.chat.id, call.message.message_id, reply_markup=markup)
                    except:
                        pass
                elif data == "match_share":
                    # Поделиться результатом
                    try:
                        позиция = получить_позицию_пользователя(user_id)
                        позиция_текст = ""
                        if позиция:
                            if позиция == 1:
                                позиция_текст = "🥇 **1 место!**"
                            elif позиция == 2:
                                позиция_текст = "🥈 **2 место!**"
                            elif позиция == 3:
                                позиция_текст = "🥉 **3 место!**"
                            else:
                                позиция_текст = f"#{позиция} место"
                        
                        # Определяем имя игрока
                        if call.from_user.username:
                            имя_игрока = f"@{call.from_user.username}"
                        elif call.from_user.first_name:
                            имя_игрока = call.from_user.first_name
                        else:
                            имя_игрока = "Игрок"
                        
                        результат_текст = f"🎮 **Три в ряд - Результат!**\n\n" \
                                         f"👤 Игрок: {имя_игрока}\n" \
                                         f"📊 Счёт: {игра['счёт']}\n" \
                                         f"🎯 Ходы: {игра['ходы']}\n" \
                                         f"⏱️ Время: {игра['общее_время']} сек\n" \
                                         f"🔥 Макс. комбо: x{игра['максимальное_комбо']}\n\n" \
                                         f"🏆 {позиция_текст}\n\n" \
                                         f"🎲 Попробуй сыграть сам!"
                    except:
                        результат_текст = f"🎮 **Три в ряд - Результат!**\n\n" \
                                         f"📊 Счёт: {игра['счёт']}\n" \
                                         f"🎯 Ходы: {игра['ходы']}\n\n" \
                                         f"🎲 Попробуй сыграть сам!"
                    
                    try:
                        bot.edit_message_text(результат_текст, call.message.chat.id, call.message.message_id)
                    except:
                        pass
                elif data == "match_new":
                    # Новая игра
                    import time
                    новая_игра = создать_игру_три_в_ряд(user_id)
                    новая_игра['время_начала'] = time.time()
                    игры_три_в_ряд[user_id] = новая_игра
                    markup = создать_кнопки_три_в_ряд(новая_игра['поле'])
                    try:
                        bot.edit_message_text(создать_текст_игры(новая_игра), call.message.chat.id, call.message.message_id, reply_markup=markup)
                    except:
                        pass
                else:
                    # Обычная обработка хода
                    _, x, y = data.split("_")
                    
                    # Если это первый выбор клетки или нет выбранной
                    if not игра.get('выбранная_клетка'):
                        markup, текст = обработать_ход_три_в_ряд(игра, int(x), int(y))
                        if markup:
                            try:
                                bot.edit_message_text(текст, call.message.chat.id, call.message.message_id, reply_markup=markup)
                            except:
                                pass
                        else:
                            игра['выбранная_клетка'] = None
                            try:
                                bot.edit_message_text(текст, call.message.chat.id, call.message.message_id)
                            except:
                                pass
                    else:
                        # Второй выбор - обмен клеток
                        x1, y1 = игра['выбранная_клетка']
                        x2, y2 = int(x), int(y)
                        
                        # Проверяем, что клетки соседние
                        if abs(x1 - x2) + abs(y1 - y2) == 1:
                            успех, текст = обмен_клеток(игра, x1, y1, x2, y2)
                            игра['выбранная_клетка'] = None
                            
                            markup = создать_кнопки_три_в_ряд(игра['поле'])
                            новый_текст = f"{текст}\n\n{создать_текст_игры(игра)}"
                            
                            try:
                                bot.edit_message_text(новый_текст, call.message.chat.id, call.message.message_id, reply_markup=markup)
                            except:
                                pass
                        else:
                            # Не соседние клетки - выбираем новую
                            markup, текст = обработать_ход_три_в_ряд(игра, x2, y2)
                            if markup:
                                try:
                                    bot.edit_message_text(текст, call.message.chat.id, call.message.message_id, reply_markup=markup)
                                except:
                                    pass
                            else:
                                игра['выбранная_клетка'] = None
                                try:
                                    bot.edit_message_text(текст, call.message.chat.id, call.message.message_id)
                                except:
                                    pass
        
        bot.answer_callback_query(call.id)

    print("🤖 Telegram бот запущен...")
    print("📱 Найдите своего бота в Telegram и напишите /start")
    bot.polling()
    return True

# Основная логика запуска
if __name__ == "__main__":
    try:
        запустить_бота()
    except KeyboardInterrupt:
        print("\n👮: До свидания!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")