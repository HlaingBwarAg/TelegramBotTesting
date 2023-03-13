from telebot import types

def report_markup(mcq_id):
    markup = types.InlineKeyboardMarkup()
    report_btn = types.InlineKeyboardButton('Report', callback_data=f'report_{mcq_id}')

    return markup.add(report_btn)

def main_category_markup(main_categories):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    for category in main_categories:
        btn = types.KeyboardButton(category['name'] + " " + "(Main)")
        markup.add(btn)

    return markup

def sub_category_markup(sub_categories):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    for category in sub_categories:
        btn = types.KeyboardButton(category['name'] + " " + "(Sub)")
        markup.add(btn)

    return markup

def month_markup(add_done=False):
    markup = types.InlineKeyboardMarkup()
    btn_1mth = types.InlineKeyboardButton('1 mth', callback_data='1mth')
    btn_3mth = types.InlineKeyboardButton('3 mth', callback_data='3mth')
    btn_6mth = types.InlineKeyboardButton('6 mth', callback_data='6mth')
    btn_cancel = types.InlineKeyboardButton('Cancel', callback_data='cancel')
    markup.add(btn_1mth, btn_3mth, btn_6mth, btn_cancel)

    if add_done:
        btn_done = types.InlineKeyboardButton('Done', callback_data='done')
        markup.add(btn_done)

    return markup

def main_category_inline_markup(cur, add_done=False):
    markup = types.InlineKeyboardMarkup()
    cur.execute('SELECT id, name FROM main_cate')
    main_cate = cur.fetchall()
    for cate in main_cate:
        data = 'cate_' + str(cate['id']) + '_' + cate['name']
        btn = types.InlineKeyboardButton(cate['name'], callback_data=data)
        markup.add(btn)

    btn_cancel = types.InlineKeyboardButton('Cancel', callback_data='cancel')
    markup.add(btn_cancel)

    if add_done:
        btn_done = types.InlineKeyboardButton('Done', callback_data='cateDone')
        markup.add(btn_done)
    return markup

def answering_markup():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

    btn_rdn = types.KeyboardButton('Random')
    btn_serial = types.KeyboardButton('Serial')

    markup.add(btn_rdn, btn_serial)

    return markup

