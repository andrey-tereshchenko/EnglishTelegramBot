import datetime
import random
import time
import telepot
from django.http import HttpResponse
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import MessageLoop

from test_telegram_bot.models import Question, UsersQuestion, UserInformation

BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'
TOKEN = '700213562:AAFa9RojjehuOw_lTOUjyqls_Kx3vosPSdU'
TelegramBot = telepot.Bot(TOKEN)

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Do did does', callback_data='button1'),
     InlineKeyboardButton(text='am is are', callback_data='button2'),
     InlineKeyboardButton(text='in at on', callback_data='button3')],
])

keyboard2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Еще вопрос', callback_data='more'),
     InlineKeyboardButton(text='К выбору категорий', callback_data='back'),
     InlineKeyboardButton(text='Граматика', callback_data='grammar')],
])
keyboard3 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Еще вопрос', callback_data='more'),
     InlineKeyboardButton(text='К выбору категорий', callback_data='back')],
])


def index(request):
    bot = telepot.Bot(TOKEN)
    MessageLoop(bot, {'chat': on_chat_message,
                      'callback_query': on_callback_query}).run_as_thread()
    print('Listening ...')
    while 1:
        time.sleep(10)


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    commands = ['/start']
    user_question = UsersQuestion.objects.filter(user_id=chat_id)
    user_information = UserInformation.objects.filter(user_id=chat_id).first()
    lenght = len(user_question)
    if lenght > 0:
        if msg["text"] == user_question[lenght - 1].question.answer_text:
            cost_question = user_question[lenght - 1].question.cost
            score = user_information.score + cost_question
            date = user_information.date_registered
            TelegramBot.sendMessage(chat_id,
                                    text=f'Правильно! +{cost_question} балла к счету. С {date} Вы заработали {score} балла',
                                    reply_markup=keyboard3)
            user_question[lenght - 1].answer = msg["text"]
            user_question[lenght - 1].save()
            user_information.score = score
            user_information.save()
        elif msg["text"] not in commands:
            TelegramBot.sendMessage(chat_id,
                                    text=f'Ответ не правильный! Правильный ответ : *{user_question[lenght - 1].question.answer_text}*',
                                    parse_mode='Markdown',
                                    reply_markup=keyboard2)
            user_question[lenght - 1].answer = msg["text"]
            user_question[lenght - 1].save()
    if msg["text"] == commands[0]:
        if not user_information:
            now = datetime.datetime.now()
            user_information = UserInformation(user_id=chat_id, date_registered=now.strftime("%Y-%m-%d"), score=0)
            user_information.save()
        TelegramBot.sendMessage(chat_id, 'Выберите категорию', reply_markup=keyboard)


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    msg_idf = telepot.message_identifier(msg['message'])

    if query_data == 'back':
        TelegramBot.editMessageText(msg_idf, text="Выберите категорию", reply_markup=keyboard)
    elif query_data == 'grammar':
        photos = ['https://englsecrets.ru/wp-content/uploads/2013/05/formy-glagola-to-be.jpg',
                  'http://englishtexts.ru/wp-content/VerbToBe.png',
                  'https://lingvoelf.ru/images/english_grammar/at_on_in.JPG']
        user_question = UsersQuestion.objects.filter(user_id=from_id)
        lenght = len(user_question)
        type = user_question[lenght - 1].question.type_question
        TelegramBot.deleteMessage(msg_idf)
        TelegramBot.sendPhoto(chat_id=from_id, photo=photos[type - 1])
        TelegramBot.sendMessage(chat_id=from_id,
                                text='Продолжаем ?',
                                reply_markup=keyboard3)
    else:
        if query_data == 'button1':
            question = generete_question_by_type(Question.TYPE_DO)

        if query_data == 'button2':
            question = generete_question_by_type(Question.TYPE_AM)

        if query_data == 'button3':
            question = generete_question_by_type(Question.TYPE_IN)

        if query_data == 'more':
            user_question = UsersQuestion.objects.filter(user_id=from_id)
            lenght = len(user_question)
            type = user_question[lenght - 1].question.type_question
            question = generete_question_by_type(type)

        users_question = UsersQuestion(user_id=from_id, question=question)
        cost_question = question.cost
        users_question.save()
        TelegramBot.editMessageText(msg_idf,
                                    f'Переведите предложение : {question.question_text} (+{cost_question} points)'
                                    )


def generete_question_by_type(type):
    questions = Question.objects.filter(type_question=type)
    return random.choice(questions)
