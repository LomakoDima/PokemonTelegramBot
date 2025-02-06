import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import token
from random import randint
from logic import *
import time
from datetime import datetime, timedelta

bot = telebot.TeleBot(token)


def generate_pokemon_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🧙 Wizard", callback_data="choose_wizard"))
    keyboard.add(InlineKeyboardButton("🥊 Fighter", callback_data="choose_fighter"))
    return keyboard


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
                     "✨ Привет, тренер! Добро пожаловать в мир покемонов! ✨\nИспользуй /help для списка команд.")


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id,
                     "📜 *Список команд:*\n\n🎮 /go – Выбрать покемона\nℹ️ /info – Информация о покемоне\n⚔️ /attack – Атаковать другого покемона\n🍖 /feed – Покормить покемона\n❤️ /heal – Вылечить покемона (до 2 раз)\n💪 /train – Тренировка покемона (1 раз в день)\n🏆 /leaders – Таблица лидеров",
                     parse_mode="Markdown")


@bot.message_handler(commands=['go'])
def start(message):
    if message.from_user.username not in Pokemon.pokemons.keys():
        bot.send_message(message.chat.id, "🔹 *Выбери своего покемона:*", reply_markup=generate_pokemon_keyboard(),
                         parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ Ты уже создал себе покемона!")


@bot.callback_query_handler(func=lambda call: call.data.startswith("choose_"))
def choose_pokemon(call):
    username = call.from_user.username
    if username in Pokemon.pokemons:
        bot.answer_callback_query(call.id, "❌ Ты уже выбрал покемона!")
        return

    if call.data == "choose_wizard":
        pokemon = Wizard(username)
    elif call.data == "choose_fighter":
        pokemon = Fighter(username)

    bot.send_message(call.message.chat.id, f"🎉 *Поздравляем!* Ты выбрал {pokemon.name.capitalize()}!",
                     parse_mode="Markdown")
    bot.send_photo(call.message.chat.id, pokemon.show_img())


@bot.message_handler(commands=['info'])
def info(message):
    if message.from_user.username in Pokemon.pokemons.keys():
        pok = Pokemon.pokemons[message.from_user.username]
        bot.send_message(message.chat.id, f"📜 *Информация о покемоне:*\n{pok.info()}\n🍗 Сытость покемона: {pok.hunger}",
                         parse_mode="Markdown")


@bot.message_handler(commands=['attack'])
def attack_pok(message):
    if message.reply_to_message:
        if message.reply_to_message.from_user.username in Pokemon.pokemons.keys() and message.from_user.username in Pokemon.pokemons.keys():
            enemy = Pokemon.pokemons[message.reply_to_message.from_user.username]
            pok = Pokemon.pokemons[message.from_user.username]
            res = pok.attack(enemy)
            bot.send_message(message.chat.id, f"⚔️ {res}", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "⚠️ Сражаться можно только с покемонами!")
    else:
        bot.send_message(message.chat.id, "⚠️ Чтобы атаковать, нужно ответить на сообщение противника!")


@bot.message_handler(commands=['feed'])
def feed_pok(message):
    if message.from_user.username in Pokemon.pokemons.keys():
        pok = Pokemon.pokemons[message.from_user.username]
        bot.send_message(message.chat.id, f"🍖 {pok.feed()}", parse_mode="Markdown")


@bot.message_handler(commands=['heal'])
def heal_pok(message):
    if message.from_user.username in Pokemon.pokemons.keys():
        pok = Pokemon.pokemons[message.from_user.username]
        if pok.hp < 200 and pok.heal_count < 2:
            pok.heal_count += 1
            bot.send_message(message.chat.id, "❤️ Покемон подлечен!", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "⚠️ Лечение недоступно!")


@bot.message_handler(commands=['train'])
def train_pok(message):
    if message.from_user.username in Pokemon.pokemons.keys():
        pok = Pokemon.pokemons[message.from_user.username]
        if datetime.now() - pok.last_training >= timedelta(days=1):
            pok.power += 5
            pok.last_training = datetime.now()
            bot.send_message(message.chat.id, f"💪 Тренировка завершена! Сила покемона увеличена: {pok.power}",
                             parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "⚠️ Тренироваться можно 1 раз в день!")


@bot.message_handler(commands=['leaders'])
def leaderboard(message):
    if Pokemon.pokemons:
        leaders = sorted(Pokemon.pokemons.values(), key=lambda p: p.hp, reverse=True)
        leaderboard_text = "🏆 *Таблица лидеров:*\n" + "\n".join([f"🥇 {p.pokemon_trainer}: {p.hp} HP" for p in leaders])
        bot.send_message(message.chat.id, leaderboard_text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Пока нет зарегистрированных покемонов!", parse_mode="Markdown")


def hunger_timer():
    while True:
        for pok in Pokemon.pokemons.values():
            pok.hunger -= 15
            if pok.hunger < 0:
                pok.hunger = 0
        time.sleep(600)  # 10 минут


import threading

threading.Thread(target=hunger_timer, daemon=True).start()

bot.infinity_polling(none_stop=True)

