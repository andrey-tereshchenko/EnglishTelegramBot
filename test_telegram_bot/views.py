import random
import time
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import MessageLoop

from test_telegram_bot.models import Question, UsersQuestion

TOKEN = '700213562:AAFa9RojjehuOw_lTOUjyqls_Kx3vosPSdU'
TelegramBot = telepot.Bot(TOKEN)


def index(request):
    bot = telepot.Bot(TOKEN)
    MessageLoop(bot, {'chat': on_chat_message,
                      'callback_query': on_callback_query}).run_as_thread()
    print('Listening ...')

    while 1:
        time.sleep(60)


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    commands = ['/start', '/send-image', '/send-audio']

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Do did does', callback_data='button1'),
         InlineKeyboardButton(text='am is are', callback_data='button2'),
         InlineKeyboardButton(text='in at on', callback_data='button3')],
    ])

    keyboard2 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Еще вопрос', callback_data='more'),
         InlineKeyboardButton(text='К выбору категорий', callback_data='back')],
    ])
    user_question = UsersQuestion.objects.filter(used_id=chat_id)
    lenght = len(user_question)
    if lenght > 0:
        if msg["text"] == user_question[lenght - 1].question.answer_text:
            TelegramBot.sendMessage(chat_id, text='Ответ правильный +1 points', reply_markup=keyboard2)
        elif msg["text"] not in commands:
            TelegramBot.sendMessage(chat_id,
                                    text=f'Ответ не правильный! Правильный ответ : {user_question[lenght - 1].question.answer_text} ',
                                    reply_markup=keyboard2)
    if msg["text"] == commands[0]:
        TelegramBot.sendMessage(chat_id, 'Выберите категорию', reply_markup=keyboard)
    if msg["text"] == commands[1]:
        TelegramBot.sendPhoto(chat_id=chat_id, photo='https://telegram.org/img/t_logo.png')
    if msg["text"] == commands[2]:
        TelegramBot.sendAudio(chat_id=chat_id, audio=open('static/audio/1.mp3', 'rb'))


def on_callback_query(msg):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Do did does', callback_data='button1'),
         InlineKeyboardButton(text='Am is are', callback_data='button2'),
         InlineKeyboardButton(text='In at on', callback_data='button3')],
    ])
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    msg_idf = telepot.message_identifier(msg['message'])

    if query_data == 'button1':
        question = generete_question_by_type(Question.TYPE_DO)
        users_question = UsersQuestion(used_id=from_id, question=question)
        users_question.save()
        TelegramBot.editMessageText(msg_idf, f'Переведите предложение : {question.question_text}')

    if query_data == 'button2':
        question = generete_question_by_type(Question.TYPE_AM)
        users_question = UsersQuestion(used_id=from_id, question=question)
        users_question.save()
        TelegramBot.editMessageText(msg_idf, f'Переведите предложение : {question.question_text}')

    if query_data == 'button3':
        question = generete_question_by_type(Question.TYPE_IN)
        users_question = UsersQuestion(used_id=from_id, question=question)
        users_question.save()
        TelegramBot.editMessageText(msg_idf, f'Переведите предложение : {question.question_text}')

    if query_data == 'more':
        user_question = UsersQuestion.objects.filter(used_id=from_id)
        lenght = len(user_question)
        type = user_question[lenght - 1].question.type_question
        question = generete_question_by_type(type)
        users_question = UsersQuestion(used_id=from_id, question=question)
        users_question.save()
        TelegramBot.editMessageText(msg_idf, f'Переведите предложение : {question.question_text}')

    if query_data == 'back':
        TelegramBot.editMessageText(msg_idf, text="Выберите категорию", reply_markup=keyboard)


def generete_question_by_type(type):
    questions = Question.objects.filter(type_question=type)
    return random.choice(questions)