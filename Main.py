import telebot
import pandas as pd
from telebot import types

# Загрузка данных
try:
    df = pd.read_csv('/content/Most Streamed Spotify Songs 2024.csv', encoding='utf-8')
except UnicodeDecodeError:
    try:
        df = pd.read_csv('/content/Most Streamed Spotify Songs 2024.csv', encoding='latin1')
    except UnicodeDecodeError:
        df = pd.read_csv('/content/Most Streamed Spotify Songs 2024.csv', encoding='cp1252')

# Переименование столбцов, если есть лишние пробелы
df.columns = [col.strip() for col in df.columns]

# Переименование столбца 'Track Name' на 'Track'
if 'Track Name' in df.columns:
    df.rename(columns={'Track Name': 'Track'}, inplace=True)

# Создание экземпляра бота с указанием токена
bot = telebot.TeleBot('6997992698:AAE6trCUQ28FrVhr12jOrTH1_5VYl4G7D7c')

# Словарь для хранения состояний пользователей (для отслеживания контекста вопросов)
user_state = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот для поиска информации о популярной музыке на Spotify. Какую песню ты хочешь найти?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id in user_state and user_state[chat_id]['awaiting_response'] == 'additional_info':
        handle_additional_info(message)
    else:
        send_song_info(message)

def send_song_info(message):
    track_name = message.text
    chat_id = message.chat.id
    filtered_df = df[df['Track'].str.contains(track_name, case=False)]

    if not filtered_df.empty:
        song_info = filtered_df.iloc[0]
        response = f"Название трека: {song_info['Track']}\n"
        response += f"Исполнитель: {song_info['Artist']}\n"
        response += f"Популярность на Spotify: {song_info['Spotify Popularity']}\n"
        response += f"Название альбома: {song_info['Album Name']}\n"
        response += f"Место в топе: {song_info['All Time Rank']}\n"
        response += f"Лайки на YouTube: {song_info['YouTube Likes']}\n"
        response += f"Лайки в TikTok: {song_info['TikTok Likes']}\n"

        user_state[chat_id] = {'song_info': song_info, 'awaiting_response': 'additional_info'}
        bot.reply_to(message, response)
        show_options(chat_id)
    else:
        bot.reply_to(message, f"Трек с названием '{track_name}' не найден.")

def show_options(chat_id):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Год выпуска', 'Просмотры на YouTube', 'Выбрать новую песню')
    bot.send_message(chat_id, "Что бы ты хотел узнать дальше?", reply_markup=markup)

def handle_additional_info(message):
    chat_id = message.chat.id
    song_info = user_state[chat_id]['song_info']
    if message.text == 'Год выпуска':
        response = f"Год выпуска: {song_info['Release Date']}"
    elif message.text == 'Просмотры на YouTube':
        response = f"Просмотры на YouTube: {song_info['YouTube Views']}"
    else:
        bot.send_message(chat_id, "Введите название новой песни:")
        user_state.pop(chat_id)
        return
    bot.reply_to(message, response)
    show_options(chat_id)

# Запуск бота
bot.polling()
