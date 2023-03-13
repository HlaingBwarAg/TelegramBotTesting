def is_admin(telegram_id, cur):
    cur.execute(f'SELECT is_admin FROM user_account WHERE telegram_id={telegram_id}')
    return cur.fetchone()['is_admin']

def is_register_user(telegram_id, cur):
    cur.execute(f'SELECT EXISTS(SELECT 1 FROM user_account WHERE telegram_id={telegram_id})')
    return cur.fetchone()['exists']

def get_name(user):
    return user.first_name if not user.last_name else user.first_name + " " + user.last_name


def get_main_categories(cur):
    cur.execute(f'SELECT name FROM main_cate')
    return cur.fetchall()

def get_sub_categories(main_category_id, cur):
    cur.execute(f'SELECT id, name FROM sub_cate WHERE main_category_id = {main_category_id}')
    return cur.fetchall()

# def get_selected_mcq(mcq_number, sub_cate_ids, cur):
#     print(tuple(sub_cate_ids))
#     cur.execute(f'SELECT id,ques,ans FROM mcq WHERE id = {mcq_number} AND sub_cate_id IN {tuple(sub_cate_ids)}')
#     return cur.fetchone()

def get_random_row(cur, selected_main_cate=False):
    if selected_main_cate:
        cur.execute(f'''SELECT * FROM mcq WHERE main_cate_id IN {selected_main_cate} OFFSET floor(
                                random() * ( SELECT COUNT(*) FROM mcq))
                                LIMIT 1''')
    else:
        cur.execute(f'''SELECT * FROM mcq OFFSET floor(
                        random() * ( SELECT COUNT(*) FROM mcq))
                        LIMIT 1''')
    return cur.fetchone()

def get_selected_row(no, selected_sub_cate, cur):
    cur.execute(f'''
            SELECT * FROM mcq
            WHERE no = {no} AND sub_cate_id IN {selected_sub_cate}
            LIMIT 1''')
    return cur.fetchone()

def active_plan(telegram_id, cur):
    cur.execute(f'''
            SELECT junction.telegram_id, valid_till, main_cate.name, main_cate.id 
            FROM main_cate_user_account AS junction
            JOIN main_cate ON junction.main_cate_id = main_cate.id
            WHERE telegram_id = {telegram_id} AND valid_till > now()''')
    return cur.fetchall()


