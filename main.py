import os
import random

import telebot
from data import data

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot('6260923464:AAHpnPmincf-hCJR9gc1qHKnTB0CbbVObdo')

answer = ''

@bot.message_handler(commands=['start', 'help'])
def start(message):
    reply_obj = random.choice(data)
    global answer
    answer = reply_obj['ans']
    reply = '%s\n1. %s\n2. %s\n3. %s\n4. %s\n5. %s' % \
            (reply_obj['title'], reply_obj['1'], reply_obj['2'], reply_obj['3'], reply_obj['4'], reply_obj['5'],)

    bot.send_message(message.chat.id, reply)

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    mark = 0
    global answer
    for ind, ans in enumerate(message.text.lower()):
        if ans == answer[ind] and ans != 'b':
            mark += 1
        elif ans != answer[ind] and ans != 'b':
            mark -= 1
    next_ques_obj = random.choice(data)
    next_ques = '%s\n1. %s\n2. %s\n3. %s\n4. %s\n5. %s' % \
                 (next_ques_obj['title'],
                  next_ques_obj['1'], next_ques_obj['2'], next_ques_obj['3'], next_ques_obj['4'], next_ques_obj['5'],)

    reply = 'You Got %s marks.\nCorrect answer is %s.\n\n%s' % (mark, answer.upper(), next_ques)

    bot.send_message(message.chat.id, reply)

    answer = next_ques_obj['ans']


bot.infinity_polling()

