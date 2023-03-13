import os
import time
import telebot
import psycopg
from psycopg.rows import dict_row
import database as db
from datetime import datetime
from telebot import types
import pprint
import markup
import helper_function
import create_table_sql as table

pp = pprint.PrettyPrinter()

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot('6260923464:AAHpnPmincf-hCJR9gc1qHKnTB0CbbVObdo')

key = None
conn = None
letter_for_blank = 'b'
minus_system = False
daily_limit = 3
today_time = 0
last_day = None
duration = 0
admin = '@hlaingbwaraung'
is_random = True
monthly_fee = 2000
selected_main_cate = [0]
selected_sub_cate = [0]
allowed_cate = [0]
mcq_number = 0
module_fee = 2000
buy_cate = {'id': [], 'name': []}
buy_cate_string = ''
answering_method = None
channel_id = -1001705112405
group_id = -1001845957783

def is_register_verified_user(telegram_id):
    cur.execute(f'SELECT EXISTS(SELECT 1 FROM user_account WHERE telegram_id={telegram_id} AND verified=True AND valid_till > CURRENT_DATE)')
    return cur.fetchone()['exists']

@bot.message_handler(commands=['start'])
def start(message, randomly=True, selected_mcq_number=mcq_number):
    user = message.from_user
    user_name = user.first_name if not user.last_name else user.first_name + " " + user.last_name
    is_register = helper_function.is_register_user(user.id, cur)
    if not is_register:
        try:
            insert_user_script = 'INSERT INTO user_account (telegram_id, username, name) VALUES (%s, %s, %s)'
            cur.execute(insert_user_script, (user.id, user.username, user_name))
            conn.commit()

        except Exception as err:
            print(err)
            bot.send_message(message.chat.id, f'''Sorry {user_name}.\nPlease try again later.''')

    active_plan = helper_function.active_plan(user.id, cur)
    active_main_cate = [0]
    for record in active_plan:
        active_main_cate.append(record['id'])

    print(active_main_cate)

    if len(active_plan) > 0:
        if answering_method is None or answering_method == 'Random':
            mcq = helper_function.get_random_row(cur, tuple(active_main_cate))
        elif answering_method == 'Serial':
            mcq = helper_function.get_selected_row(mcq_number, selected_sub_cate, cur)
            mcq_number += 1

        global key
        key = mcq['ans']
        mcq_id = mcq['id']
        reply = mcq['ques'] + f'\nIf there is something wrong in mcq please report here /report_{mcq_id}'

        bot.send_message(message.chat.id, reply)

    else:
        bot.send_message(message.chat.id, 'Sorry you dont have active plan. '
                                          'Please buy active to able to select the category you want to answer. '
                                          'Here is the random mcq. ')
        mcq = helper_function.get_random_row(cur)

        key = mcq['ans']
        mcq_id = mcq['id']
        reply = mcq['ques'] + f'\nIf there is something wrong in mcq please report here /report_{mcq_id}'

        bot.send_message(message.chat.id, reply)

    # is_register = helper_function.is_register_user(user.id, cur)
    # name = helper_function.get_name(user)
    #
    # # if not register insert into db
    # if not is_register:
    #     insert_user_script = 'INSERT INTO user_account (telegram_id, username, name) VALUES (%s, %s, %s)'
    #     cur.execute(insert_user_script, (user.id, user.username, name))
    #     conn.commit()
    #
    # if randomly:
    #     mcq = helper_function.get_random_row('mcq', cur)
    # else:
    #     mcq = helper_function.get_selected_mcq(selected_mcq_number, selected_cate, cur)
    #
    # global key
    # key = mcq['ans']
    # reply = mcq['ques']
    # mcq_id = mcq['id']
    #
    # bot.send_message(message.chat.id, reply, reply_markup=markup.report_markup(mcq_id))


@bot.message_handler(commands=['select'])
def select(message):
    user = message.from_user
    active_plans = helper_function.active_plan(user.id, cur)

    if len(active_plans) > 0:
        main_cate_markup = markup.main_category_markup(active_plans)
        global selected_main_cate
        selected_main_cate = [0]
        bot.send_message(message.chat.id, 'Select Main Category', reply_markup=main_cate_markup, )
    else:
        bot.send_message(message.chat.id, 'Sorry you dont have active plan. '
                                          'Please buy active to able to select the category you want to answer. '
                                          'Here is the random mcq. ')
        mcq = helper_function.get_random_row(cur)

        global key
        key = mcq['ans']
        mcq_id = mcq['id']
        reply = mcq['ques'] + f'\nIf there is something wrong in mcq please report here /report_{mcq_id}'

        bot.send_message(message.chat.id, reply)

@bot.message_handler(func=lambda m: m.text.split(" ")[1] == '(Main)' if len(m.text.split(" ")) > 1 else False)
def select_subcategory(message):
    cur.execute(f'''SELECT id FROM main_cate WHERE name = '{message.text.split(" ")[0]}' ''')
    main_id = cur.fetchone()['id']

    selected_main_cate.append(main_id)

    sub_categories = helper_function.get_sub_categories(main_id, cur)
    sub_cate_markup = markup.sub_category_markup(sub_categories)
    bot.send_message(message.chat.id, 'Select Sub Category', reply_markup=sub_cate_markup)

@bot.message_handler(func=lambda m: m.text.split(" ")[1] == '(Sub)' if len(m.text.split(" ")) > 1 else False)
def select_answering_method(message):
    cur.execute(f'''SELECT id FROM sub_cate WHERE name = '{message.text.split(" ")[0]}' ''')
    sub_cate_id = cur.fetchone()['id']
    selected_sub_cate.append(sub_cate_id)

    bot.send_message(message.chat.id, 'Select answering method', reply_markup=markup.answering_markup())


@bot.message_handler(func=lambda m: m.text == 'Random')
def reply_random_mcq(message):
    mcq = helper_function.get_random_row(cur, tuple(selected_main_cate))

    global key, answering_method
    answering_method = 'Random'
    key = mcq['ans']
    mcq_id = mcq['id']
    reply = mcq['ques'] + f'\nIf there is something wrong in mcq please report here /report_{mcq_id}'

    bot.send_message(message.chat.id, reply)

@bot.message_handler(func=lambda m: m.text == 'Serial')
def select_mcq_number(message):
    global is_random, answering_method
    answering_method = 'Serial'
    is_random = False
    bot.send_message(message.chat.id, 'Send MCQ No you want to start with in the formant of\n'
                                      'No MCQ-Number\n'
                                      'Eg.No 21')

@bot.message_handler(func=lambda m: m.text.split(" ")[0] == 'No')
def reply_selected_mcq(message):
    selected_mcq_number = message.text.split(" ")[1]

    mcq = helper_function.get_selected_row(selected_mcq_number, tuple(selected_sub_cate), cur)
    global key, mcq_number

    key = mcq['ans']
    mcq_id = mcq['id']
    reply = mcq['ques'] + f'\nIf there is something wrong in mcq please report here /report_{mcq_id}'

    bot.send_message(message.chat.id, reply)

    mcq_number = int(selected_mcq_number) + 1


@bot.message_handler(commands=['hCate'])
def get_main_cate(message):
    print(datetime.now())
    user = message.from_user
    is_admin = helper_function.is_admin(user.id, cur)
    if is_admin:
        cur.execute('SELECT sub_cate.name AS sub_name, main_cate.name AS main_name FROM sub_cate JOIN main_cate on sub_cate.main_category_id = main_cate.id;')
        cates = cur.fetchall()
        reply = ''
        for cate in cates:
            reply += f'''{cate['main_name']}   {cate['sub_name']}\n'''
        bot.send_message(message.chat.id, reply)
    print(datetime.now())

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    user = message.from_user
    is_register = helper_function.is_register_user(user.id, cur)
    global duration, buy_cate_string
    duration = 0
    buy_cate_string = ""
    buy_cate['id'] = []
    buy_cate['name'] = []
    user_name = user.first_name if not user.last_name else user.first_name + " " + user.last_name

    # markup = types.InlineKeyboardMarkup()
    # btn_1mth = types.InlineKeyboardButton('1 mth', callback_data='1mth')
    # btn_3mth = types.InlineKeyboardButton('3 mth', callback_data='3mth')
    # btn_6mth = types.InlineKeyboardButton('6 mth', callback_data='6mth')
    # btn_cancel = types.InlineKeyboardButton('Cancel', callback_data='cancel')
    # markup.add(btn_1mth, btn_3mth, btn_6mth, btn_cancel)
    if not is_register:
        try:
            insert_user_script = 'INSERT INTO user_account (telegram_id, username, name) VALUES (%s, %s, %s)'
            cur.execute(insert_user_script, (user.id, user.username, user_name))
            conn.commit()

        except Exception as err:
            print(err)
            bot.send_message(message.chat.id, f'''Sorry {user_name}.\nPlease try again later.''')

    bot.send_message(message.chat.id, f'Welcome dear {user_name}\n'
                                      f'Please select category.', reply_markup=markup.main_category_inline_markup(cur))


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'cate')
def select_category_query(call):
    main_category_id = call.data.split('_')[1]
    main_category_name = call.data.split('_')[2]

    global buy_cate_string

    print(main_category_id, buy_cate['id'])
    print(main_category_id not in buy_cate['id'])
    if main_category_id not in buy_cate['id']:
        buy_cate_string += main_category_name + " "
        buy_cate['id'].append(main_category_id)
        buy_cate['name'].append(main_category_name)
    else:
        pass

    # for name in buy_cate['name']:
    #     buy_cate_string += name + " "
    reply = 'Your selected category:\n' \
            f'{buy_cate_string}'
    bot.edit_message_text(message_id=call.message.id, chat_id=call.message.chat.id, text=reply,
                          reply_markup=markup.main_category_inline_markup(cur, add_done=True))

@bot.callback_query_handler(func=lambda call: call.data == 'cateDone')
def select_category_done_query(call):
    # buy_cate_string = ""
    # for name in buy_cate['name']:
    #     buy_cate_string += name + " "
    reply = f'{buy_cate_string}\n' \
            f'Please select duration'

    bot.edit_message_text(message_id=call.message.id, chat_id=call.message.chat.id, text=reply,
                          reply_markup=markup.month_markup())

@bot.callback_query_handler(func=lambda call: call.data in ['1mth', '3mth', '6mth'])
def month_query(call):
    user = call.from_user
    user_name = user.first_name if not user.last_name else user.first_name + " " + user.last_name
    global duration
    if call.data == '1mth':
        duration += 1
    elif call.data == '3mth':
        duration += 3
    elif call.data == '6mth':
        duration += 6

    reply = f'{buy_cate_string}\n'\
            f'Your selected duration is {duration} Month'

    bot.edit_message_text(message_id=call.message.id, chat_id=call.message.chat.id, text=reply, reply_markup=markup.month_markup(add_done=True))

    # print(call)
    # print('chat', call.message.chat.id)
    # print('user', call.from_user)
    # print('msg', call.message)
    # # print('reply', call.reply_markup)
    # print('data', call.data)

@bot.callback_query_handler(func=lambda call: call.data == 'done')
def done_query(call):
    user = call.from_user
    user_name = user.first_name if not user.last_name else user.first_name + " " + user.last_name

    insert_order_sql = f'INSERT INTO user_order (telegram_id, username, name, duration) VALUES (%s, %s, %s, %s) RETURNING id'
    cur.execute(insert_order_sql, (user.id, user.username, user_name, duration))
    order_id = cur.fetchone()['id']

    insert_main_cate_order_sql = '''INSERT INTO main_cate_user_order (main_cate_id, user_order_id) VALUES (%s, %s)'''
    print(buy_cate['id'])
    for i in buy_cate['id']:
        print(i)
        cur.execute(insert_main_cate_order_sql, (i, order_id))

    conn.commit()

    fee = monthly_fee * len(buy_cate['id']) * duration
    orders = ""
    for name in buy_cate['name']:
        orders += f'{name.ljust(12, "_")}{str(duration).ljust(7, "_")}{monthly_fee}MMK\n'

    reply = 'Thanks for your order.\n' \
            '\n' \
            f'{orders}' \
            f'{"Total:".ljust(19, "_")}{fee}MMK\n' \
            f'\n' \
            f'Please send screenshot of your payment'

    force_reply = types.ForceReply(input_field_placeholder="Do Not Remove Reply")
    bot.edit_message_text(message_id=call.message.id, chat_id=call.message.chat.id, text=reply)
    bot.send_message(call.message.chat.id, f'/PaymentPhoto_{order_id}_{duration}', reply_markup=force_reply)

@bot.message_handler(content_types=['photo'])
@bot.message_handler(func=lambda m: m.content_type == 'photo' and m.reply_to_message.text.split('_')[0] == '/PaymentPhoto')
def payment_photo(message):
    cur.execute('SELECT telegram_id FROM user_account WHERE is_admin = True')
    admins = cur.fetchall()
    reply = message.reply_to_message.text.split('_')
    order_id = reply[1]
    month = reply[2]

    for a in admins:
        bot.send_photo(a['telegram_id'], message.photo[-1].file_id)
        bot.send_message(a['telegram_id'], f'order_{order_id}_{message.from_user.id}_@{message.from_user.username}_{month}')

    reply = "We'll let you know after checking your information."
    bot.send_message(message.chat.id, reply)

@bot.message_handler(func=lambda m: m.text.lower() == 'yes' and m.reply_to_message.text.split('_')[0] == 'order')
def order_confirm(message):
    user = message.from_user
    is_admin = helper_function.is_admin(user.id, cur)
    if is_admin:
        msg_list = message.reply_to_message.text.split('_')
        order_id = msg_list[1]
        telegram_id = msg_list[2]
        username = msg_list[3]
        cur.execute(f'''UPDATE user_order SET status = 'done', verify_by = {user.id}, updated_at = now() WHERE id = {order_id} ''')
        cur.execute(f'''SELECT user_order.telegram_id, user_order.duration, main_cate_user_order.main_cate_id
                        FROM user_order
                        INNER JOIN main_cate_user_order ON user_order.id = main_cate_user_order.user_order_id
                        WHERE user_order.id = {order_id}; ''')
        categories = cur.fetchall()

        for c in categories:
            print(c['duration'])
            cur.execute(f'''INSERT INTO main_cate_user_account
                            (main_cate_id, telegram_id, valid_till)
                            VALUES ({c['main_cate_id']}, {c['telegram_id']}, now() + INTERVAL '{c['duration']} month')
                            ON CONFLICT (main_cate_id, telegram_id) DO UPDATE
                            SET valid_till = main_cate_user_account.valid_till + INTERVAL '{c['duration']} month' ''')
        conn.commit()

        # send to admin
        bot.send_message(message.chat.id, f'Success {username}')

        # send to buyer
        bot.send_message(telegram_id, 'Your subscription is successful. You can check your account information here /info')

@bot.message_handler(commands=['info'])
def info(message):
    cur.execute(f'''SELECT u.telegram_id, u.username, u.name,
                    u.total_mark, u.time, u.minus_mark, u.minus_time,
                    main_cate.name AS main_cate_name, junction.valid_till
                    FROM user_account AS u
                    INNER JOIN main_cate_user_account AS junction ON u.telegram_id = junction.telegram_id
                    INNER JOIN main_cate ON junction.main_cate_id = main_cate.id 
                    WHERE u.telegram_id = {message.from_user.id}''')
    results = cur.fetchall()
    username = results[0]['username']
    name = results[0]['name']
    subscription = ''
    for rec in results:
        act_or_exp = '✔️' if rec['valid_till'] > datetime.now().date() else '✖️'
        subscription += f'{act_or_exp} {rec["main_cate_name"].ljust(12)}  {rec["valid_till"]}\n'

    total_mark = results[0]['total_mark']
    time = results[0]['time']
    avg_mark = total_mark / time if time != 0 else "_"
    minus_mark = results[0]['minus_mark']
    minus_time = results[0]['minus_time']
    minus_avg_mark = minus_mark / minus_time if minus_time != 0 else '_'

    reply = 'Your Info\n\n' \
            f'Username : {username}\n' \
            f'Name : {name}\n' \
            f'Subscription :\n' \
            f'{subscription}' \
            '\n' \
            'Your Personal Stats\n\n' \
            f'Answers with minus system not carried over\n' \
            f'Total Marks : {total_mark}\n' \
            f'Total Times : {time}\n' \
            f'Average Marks : {avg_mark}\n\n'\
            f'Answer with minus system carried over\n'\
            f'Total Marks : {minus_mark}\n'\
            f'Total Times : {minus_time}\n'\
            f'Average Marks : {minus_avg_mark}'

    bot.send_message(message.chat.id, reply)


# @bot.message_handler(commands=['stats'])
# def stats(message):
#     user = message.from_user
#
#     cur.execute(f'SELECT * FROM user_account WHERE telegram_id = {user.id}')
#     record = cur.fetchone()
#     total_mark = record['total_mark']
#     time = record['time']
#     avg_mark = total_mark / time if time != 0 else "_"
#     minus_mark = record['minus_mark']
#     minus_time = record['minus_time']
#     minus_avg_mark = minus_mark / minus_time if minus_time != 0 else '_'
#
#     reply = f'''Your personal stats:
#
# Answers with minus system not carried over
# Total Marks : {total_mark}
# Total Times : {time}
# Average Marks : {avg_mark}
#
# Answer with minus system carried over
# Total Marks : {minus_mark}
# Total Times : {minus_time}
# Average Marks : {minus_avg_mark}'''
#
#     bot.send_message(message.chat.id, reply)


def get_mark(user_answers, mcq_key, is_carried_over=False):
    mark = 0
    for index, user_answer in enumerate(user_answers.lower()):
        if user_answer.lower() == letter_for_blank.lower():
            pass
        elif user_answer.lower() == mcq_key[index].lower():
            mark += 1
        elif user_answer.lower() != mcq_key[index].lower():
            mark -= 1

    if not is_carried_over and mark < 0:
        mark = 0

    return mark

@bot.message_handler(commands=['stop'])
def stop(message):
    global key
    key = None

    reply = '''The MCQ session is over.
/start - start another MCQ session
/stats - see your stats'''

    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=['top'])
def top(message):
    cur.execute('SELECT username,total_mark,time FROM user_account ORDER BY total_mark DESC LIMIT 10')
    top_ten = cur.fetchall()

    cur.execute('SELECT username,minus_mark,minus_time FROM user_account ORDER BY minus_mark DESC LIMIT 10')
    top_ten_carried_over = cur.fetchall()

    top_ten_list = ""
    for index, user in enumerate(top_ten):
        m = f'{str(index)}. {user["username"]} ({user["total_mark"]} Marks, {user["time"]} Mcqs)\n'
        top_ten_list += m

    top_ten_carried_over_list = ""
    for index, user in enumerate(top_ten_carried_over):
        m = f'{str(index)}. {user["username"]} ({user["minus_mark"]} Marks, {user["minus_time"]} Mcqs)\n'
        top_ten_carried_over_list += m

    reply = 'Top 10 users with the highest marks\n\nWith minus system not carried over\n' \
            '%s\n' \
            'With minus system carried over\n' \
            '%s' % (top_ten_list, top_ten_carried_over_list)

    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=['h_order'])
def admin_order(message):
    user = message.from_user
    cur.execute(f'SELECT is_admin FROM user_account WHERE telegram_id={user.id}')
    is_admin = cur.fetchone()['is_admin']

    if is_admin:
        cur.execute(''' SELECT * FROM user_order WHERE status='waiting' ''')
        orders = cur.fetchall()
        reply = 'Orders\n'
        for order in orders:
            reply += f'/con_{order["id"]}_{order["telegram_id"]}_{order["username"]}_{order["duration"]}\n'

        bot.send_message(message.chat.id, reply)

@bot.message_handler(func=lambda m: m.text.split('_')[0] == '/hAddMainCate')
def insert_main_cate(message):
    user = message.from_user
    is_admin = helper_function.is_admin(user.id, cur)
    name = message.text.split('_')[1]
    if is_admin:
        cur.execute(f'''INSERT INTO main_cate (name) VALUES ('{name}') RETURNING *''')
        conn.commit()
        added_cate = cur.fetchone()
        bot.send_message(message.chat.id, f'''{added_cate['id']}    {added_cate['name']}''')

@bot.message_handler(func=lambda m: m.text.split('_')[0] == '/hAddSubCate')
def insert_sub_cate(message):
    user = message.from_user
    is_admin = helper_function.is_admin(user.id, cur)
    main_category_id = message.text.split('_')[1]
    name = message.text.split('_')[2]
    if is_admin:
        cur.execute(f'''INSERT INTO sub_cate (name, main_category_id) VALUES ('{name}', '{main_category_id}') RETURNING *''')
        conn.commit()
        added_cate = cur.fetchone()
        bot.send_message(message.chat.id, f'''{added_cate['id']}    {added_cate['name']}''')


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'report')
def report_call_back_query(call):
    callback_data = call.data.split('_')
    mcq_id = callback_data[1]
    user = call.from_user
    user_name = user.first_name if not user.last_name else user.first_name + " " + user.last_name

    values = (user.id, user.username, user_name, mcq_id)
    cur.execute(f'INSERT INTO report (telegram_id, username, name, mcq_id) VALUES {values}')
    conn.commit()

    bot.edit_message_text(message_id=call.message.id, chat_id=call.message.chat.id, text='You have reported successfully')

    start(call.message)

@bot.message_handler(commands=['c_send'])
def channel_send_message(message):
    print('run')
    cur.execute('SELECT * FROM mcq limit 1')
    mcqs = cur.fetchall()
    abc = ['A.', 'B.', 'C.', 'D.', 'E.']
    no_arr = []
    for index, mcq in enumerate(mcqs):
        ques = mcq['ques'].replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
        ans = [f'<span class="tg-spoiler">{"✅ " if ans.upper() == "T" else "❌ "}</span>' for ans in mcq['ans']]
        for letter in abc:
            no = mcq['ques'].find(letter)
            no_arr.append(no)
        ques_with_ans = ques[:no_arr[0]] + ans[0] + ques[no_arr[0]:no_arr[1]] + ans[1] + ques[no_arr[1]:no_arr[2]] + ans[2] + ques[no_arr[2]:no_arr[3]] + ans[3] + ques[no_arr[3]:no_arr[4]] + ans[4] + ques[no_arr[4]:]
        # print(mcq['ques'][:mcq['ques'].find('\nA.')] + 'T' + mcq['ques'][mcq['ques'].find('\nA.'):])
        # reply = f'{ques_with_ans.replace("<","&lt;").replace(">", "&gt;").replace("&", "&amp;")}\n\n' \
        #         f'Answer: <span class="tg-spoiler">{mcq["ans"].upper()}</span>'
        reply = ques_with_ans
        bot.send_message(channel_id, reply, parse_mode="HTML")
        if (index + 1) % 15 == 0:
            time.sleep(60)

    message_id = 130
    for index, mcq in enumerate(mcqs):
        bot.send_message(group_id, mcq['explanation'], reply_to_message_id=message_id)
        message_id += 1
        if (index + 1) % 15 == 0:
            time.sleep(60)


@bot.message_handler(func=lambda m: True if key is not None else False)
def reply_another_mcq(message):
    active_plan = helper_function.active_plan(message.from_user.id, cur)
    active_main_cate = [0]
    for record in active_plan:
        active_main_cate.append(record['id'])
    active_plan_len = len(active_plan)
    is_verified = is_register_verified_user(message.from_user.id)

    global last_day, today_time, key, mcq_number
    if active_plan_len == 0:
        if last_day == datetime.today().date():
            today_time += 1
        else:
            last_day = datetime.today().date()
            today_time = 1

    if active_plan_len > 0:
        if answering_method == 'Random' or answering_method is None:
            mcq = helper_function.get_random_row(cur, tuple(active_main_cate))
        elif answering_method == 'Serial':
            mcq = helper_function.get_selected_row(mcq_number, tuple(selected_sub_cate), cur)
            mcq_number += 1

        mcq_id = mcq['id']
        next_mcq_ques = mcq['ques']
        mark = get_mark(message.text, key)

        if not minus_system:
            mark_column = 'total_mark'
            time_column = 'time'
        else:
            mark_column = 'minus_mark'
            time_column = 'minus_time'

        cur.execute(
            f'UPDATE user_account SET {mark_column} = {mark_column}+{mark}, {time_column} = {time_column}+1 WHERE telegram_id = {message.from_user.id}')
        conn.commit()

        # markup = types.InlineKeyboardMarkup()
        # report_btn = types.InlineKeyboardButton('Report', callback_data=f'report_{mcq_id}')

        # markup.add(report_btn)

        reply = 'You Got %s marks.\n' \
                'Correct answer is %s.\n' \
                '\n' \
                '%s' \
                f'\nIf there is something wrong in mcq please report here /report_{mcq_id}' % (
                mark, key.upper(), next_mcq_ques)

        bot.send_message(message.chat.id, reply)
        key = mcq['ans']

    elif active_plan_len == 0 and today_time < daily_limit:
        mcq = helper_function.get_random_row(cur)
        next_mcq_ques = mcq['ques']

        key = mcq['ans']
        mcq_id = mcq['id']
        mark = get_mark(message.text, key)

        if not minus_system:
            mark_column = 'total_mark'
            time_column = 'time'
        else:
            mark_column = 'minus_mark'
            time_column = 'minus_time'

        cur.execute(
            f'UPDATE user_account SET {mark_column} = {mark_column}+{mark}, {time_column} = {time_column}+1 WHERE telegram_id = {message.from_user.id}')
        conn.commit()

        reply = 'You Got %s marks.\n' \
                'Correct answer is %s.\n' \
                '\n' \
                '%s' \
                f'\nIf there is something wrong in mcq please report here /report_{mcq_id}' % (
                    mark, key.upper(), next_mcq_ques)

        bot.send_message(message.chat.id, reply)

    elif today_time >= daily_limit:
        bot.send_message(message.chat.id, 'Daily limit have reach. Please /subscribe for unlimited MCQS.')


@bot.message_handler(commands=['tests'])
def testing(message):
    markup = types.ReplyKeyboardMarkup(input_field_placeholder='HIHI', resize_keyboard=True, one_time_keyboard=True, row_width=1)
    btn_cvs = types.KeyboardButton('CVS')
    btn_resp = types.KeyboardButton('Resp')
    markup.add(btn_cvs, btn_resp)

    bot.send_message(message.chat.id, 'hihihi', reply_markup=markup)

if __name__ == '__main__':
    try:
        print('initialize the configuration')
        # connect the database
        with psycopg.connect(host=db.hostname, dbname=db.database, user=db.username, password=db.pwd, port=db.port_id, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                print('connected to database')

                # cur.execute('DROP TABLE IF EXISTS user_account CASCADE')
                cur.execute(table.crate_user_script)

                cur.execute(table.create_main_cate_table_sql)

                cur.execute(table.create_sub_cate_table_sql)

                # cur.execute('DROP TABLE IF EXISTS mcq CASCADE')
                cur.execute(table.create_mcq_table_sql)

                # cur.execute('DROP TYPE order_type CASCADE')
                # cur.execute('''CREATE TYPE order_type AS ENUM ('waiting', 'done', 'cancel')''')
                cur.execute(table.create_order_table_sql)

                cur.execute(table.create_report_table_sql)

                cur.execute(table.create_main_cate_user_account_table_sql)

                cur.execute(table.create_main_cate_user_order_sql)

                print('tables are created')

                print('bot started')
                bot.infinity_polling()
        # bot.infinity_polling()
    except Exception as error:
        print(error)

    finally:
        pass
        if conn is not None:
            conn.close()

