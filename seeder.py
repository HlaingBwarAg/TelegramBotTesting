import datetime

import database as db
import psycopg
import csv
import pandas

conn = None

def seed(file):
    try:
        with psycopg.connect(host=db.hostname, dbname=db.database, user=db.username, password=db.pwd, port=db.port_id, row_factory=db.dict_row) as conn:
            with conn.cursor() as cur:
                data_df = pandas.read_csv(file)

                data_list = data_df.to_dict('records')
                insert_mcq_script = 'INSERT INTO mcq (no, ques, ans, explanation, main_cate_id, sub_cate_id) VALUES (%s, %s, %s, %s, %s, %s)'

                for index, rec in enumerate(data_list):
                    # user_account_id = 'NULL'
                    value = (index + 1, rec['ques'], rec['ans'], rec['explanation'], 1, 1)
                    cur.execute(insert_mcq_script, value)

                print('data added')

    except Exception as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()
            print('connection close')

seed('Part 2 Medical MCQ - CVS MCQ Part 2.csv')


