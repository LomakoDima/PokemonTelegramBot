# <--- Main.py | Author: DimaLab, License: MIT --->
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import token
from random import randint
from logic import *
import time
from datetime import datetime, timedelta
import threading

bot = telebot.TeleBot(token)

ATTACK_COOLDOWN = timedelta(seconds=30)

# Main Menu Keyboard
def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("🎮 Выбрать покемона", callback_data="choose_pokemon"),
        InlineKeyboardButton("ℹ️ Информация о покемоне", callback_data="pokemon_info"),
    )
    keyboard.add(
        InlineKeyboardButton("⚔️ Атаковать", callback_data="attack"),
        InlineKeyboardButton("🍖 Покормить", callback_data="feed"),
    )
    keyboard.add(
        InlineKeyboardButton("❤️ Вылечить", callback_data="heal"),
        InlineKeyboardButton("💪 Тренировка", callback_data="train"),
    )
    keyboard.add(
        InlineKeyboardButton("🏆 Таблица лидеров", callback_data="leaders"),
        InlineKeyboardButton("❌ Удалить покемона", callback_data="quit_game"),
    )
    return keyboard

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(
        message.chat.id,
        "✨ Привет, Повелитель покемонов! Добро пожаловать в мир покемонов! ✨",
        reply_markup=main_menu_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == "choose_pokemon")
def choose_pokemon_menu(call):
    username = call.from_user.username
    if username in Pokemon.pokemons:
        bot.answer_callback_query(call.id, "❌ Ты уже выбрал покемона!")
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🧙 Wizard", callback_data="choose_wizard"))
        keyboard.add(InlineKeyboardButton("🥊 Fighter", callback_data="choose_fighter"))
        #keyboard.add(InlineKeyboardButton("⚕️ Healer (В разработке)", callback_data="choose_healer"))
        bot.send_message(call.message.chat.id, "🔹 *Выбери своего покемона:*", reply_markup=keyboard, parse_mode="Markdown")

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
    #elif call.data == "choose_healer":  (В разработке)
        #pokemon = Healer(username)

    pokemon.last_attack_time = datetime.now() - ATTACK_COOLDOWN

    bot.send_message(call.message.chat.id, f"🎉 *Поздравляем!* Ты выбрал {pokemon.name.capitalize()}!", parse_mode="Markdown")
    bot.send_photo(call.message.chat.id, pokemon.show_img())

@bot.callback_query_handler(func=lambda call: call.data == "pokemon_info")
def info(call):
    username = call.from_user.username
    if username in Pokemon.pokemons.keys():
        pok = Pokemon.pokemons[username]
        bot.send_message(call.message.chat.id, f"📜 *Информация о покемоне:*\n{pok.info()}\n🍗 Сытость покемона: {pok.hunger}", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "attack")
def attack_pokemon(call):
    bot.send_message(call.message.chat.id, "⚠️ Ответь на сообщение противника, чтобы атаковать!")

@bot.callback_query_handler(func=lambda call: call.data == "feed")
def feed_pokemon(call):
    username = call.from_user.username
    if username in Pokemon.pokemons.keys():
        pok = Pokemon.pokemons[username]
        bot.send_message(call.message.chat.id, f"🍖 {pok.feed()}", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "heal")
def heal_pokemon(call):
    username = call.from_user.username
    if username in Pokemon.pokemons.keys():
        pok = Pokemon.pokemons[username]
        if pok.hp < 200 and pok.heal_count > 0:
            pok.hp = min(200, pok.hp + 50)
            pok.heal_count -= 1
            bot.send_message(call.message.chat.id, "❤️ Покемон подлечен на 50 HP!", parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, "⚠️ Лечение недоступно! У покемона максимальное здоровье или закончились попытки.")

@bot.callback_query_handler(func=lambda call: call.data == "train")
def train_pokemon(call):
    username = call.from_user.username
    if username in Pokemon.pokemons.keys():
        pok = Pokemon.pokemons[username]
        if datetime.now() - pok.last_training >= timedelta(days=1):
            pok.power += 5
            pok.last_training = datetime.now()
            bot.send_message(call.message.chat.id, f"💪 Тренировка завершена! Сила покемона увеличена: {pok.power}", parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, "⚠️ Тренироваться можно 1 раз в день!")

@bot.callback_query_handler(func=lambda call: call.data == "leaders")
def leaderboard(call):
    if Pokemon.pokemons:
        leaders = sorted(Pokemon.pokemons.values(), key=lambda p: p.hp, reverse=True)
        leaderboard_text = "🏆 *Таблица лидеров:*\n" + "\n".join([f"🥇 {p.pokemon_trainer}: {p.hp} HP" for p in leaders])
        bot.send_message(call.message.chat.id, leaderboard_text, parse_mode="Markdown")
    else:
        bot.send_message(call.message.chat.id, "❌ Пока нет зарегистрированных покемонов!", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "quit_game")
def quit_game(call):
    username = call.from_user.username
    if username in Pokemon.pokemons.keys():
        del Pokemon.pokemons[username]
        bot.send_message(call.message.chat.id, "❌ Ты успешно удалил своего покемона и вышел из игры!")
    else:
        bot.send_message(call.message.chat.id, "⚠️ У тебя нет покемона для удаления!")


def hunger_timer():
    while True:
        for pok in Pokemon.pokemons.values():
            pok.hunger -= 15
            if pok.hunger < 0:
                pok.hunger = 0
        time.sleep(600)  # 10 минут

threading.Thread(target=hunger_timer, daemon=True).start()

bot.infinity_polling(none_stop=True)

