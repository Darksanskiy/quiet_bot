Import telebot
Import json
Import os
Import random


TOKEN = «8609555142:AAHYr6K8yvjaFrZHd712p-22MSailOljbqw»

Bot = telebot.TeleBot(TOKEN)
DATA_FILE = «places.json»

Def load_places():
    If os.path.exists(DATA_FILE):
        With open(DATA_FILE, «r», encoding=»utf-8») as f:
            Return json.load(f)
    Return []

Def save_places(places):
    With open(DATA_FILE, «w», encoding=»utf-8») as f:
        Json.dump(places, f, ensure_ascii=False, indent=2)

Def main_keyboard():
    Kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    Kb.row(«🏔 Найти тихое место», «📝 Подтвердить»)
    Kb.row(«➕ Добавить место», «📊 Статистика»)
    Return kb

@bot.message_handler(commands=['start'])
Def start(message):
    Bot.send_message(
        Message.chat.id,
        «🏔 *Тихий Алтай*\n\nВыбирайте действие на кнопках:»,
        Parse_mode='Markdown',
        Reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == «🏔 Найти тихое место»)
Def find_place(message):
    Places = load_places()
    Good = [p for p in places if p.get('confirm', 0) > 0]
    
    If not good:
        Bot.send_message(message.chat.id, «😔 Нет подтверждённых мест. Добавьте первым!»)
        Return
    
    Selected = random.sample(good, min(3, len(good)))
    Answer = «🏔 *Где сейчас тихо:*\n\n»
    For i, p in enumerate(selected, 1):
        Answer += f»{i}. *{p['name']}*\n   📍 {p['loc']}\n   👍 {p['confirm']}\n\n»
    
    Bot.send_message(message.chat.id, answer, parse_mode='Markdown')

User_data = {}

@bot.message_handler(func=lambda m: m.text == «➕ Добавить место»)
Def add_place_start(message):
    Msg = bot.send_message(message.chat.id, «📍 Напишите *название* места:», parse_mode='Markdown')
    Bot.register_next_step_handler(msg, get_name)

Def get_name(message):
    User_data[message.chat.id] = {'name': message.text}
    Msg = bot.send_message(message.chat.id, «📍 Напишите *описание* (как найти):», parse_mode='Markdown')
    Bot.register_next_step_handler(msg, get_loc)

Def get_loc(message):
    Name = user_data.get(message.chat.id, {}).get('name', '')
    Loc = message.text
    
    Places = load_places()
    Places.append({
        'name': name,
        'loc': loc,
        'confirm': 0,
        'who': []
    })
    Save_places(places)
    
    Bot.send_message(message.chat.id, f»✅ *{name}* добавлено!», parse_mode='Markdown')
    Del user_data[message.chat.id]

@bot.message_handler(func=lambda m: m.text == «📝 Подтвердить»)
Def confirm_list(message):
    Places = load_places()
    If not places:
        Bot.send_message(message.chat.id, «😔 Нет мест»)
        Return
    
    Markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    For p in places:
        Btn = telebot.types.InlineKeyboardButton(p['name'], callback_data=f»c_{p['name']}»)
        Markup.add(btn)
    
    Bot.send_message(message.chat.id, «🗳 Где сейчас тихо?», reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('c_'))
Def confirm_place(call):
    Name = call.data.replace('c_', '')
    Places = load_places()
    Uid = str(call.from_user.id)
    
    For p in places:
        If p['name'] == name:
            If uid not in p.get('who', []):
                P['confirm'] = p.get('confirm', 0) + 1
                P['who'].append(uid)
                Save_places(places)
                Bot.answer_callback_query(call.id, f»✅ Спасибо! Теперь {p['confirm']} подтверждений»)
            Else:
                Bot.answer_callback_query(call.id, «⚠️ Вы уже подтверждали», show_alert=True)
            Return
    
    Bot.answer_callback_query(call.id, «❌ Ошибка», show_alert=True)

@bot.message_handler(func=lambda m: m.text == «📊 Статистика»)
Def stats(message):
    Places = load_places()
    Total = len(places)
    Confirmed = len([p for p in places if p.get('confirm', 0) > 0])
    Bot.send_message(
        Message.chat.id,
        F»📊 *Статистика*\nВсего мест: {total}\nПодтверждённых: {confirmed}»,
        Parse_mode='Markdown'
    )

Print(«✅ Бот запущен!»)
Bot.infinity_polling()
