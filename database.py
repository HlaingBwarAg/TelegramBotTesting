import psycopg
from psycopg.rows import dict_row

hostname = 'localhost'
database = 'demo'
username = 'postgres'
pwd = 'aaaaa'
port_id = 5432

# conn = None
#
# try:
#     with psycopg.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id, row_factory=dict_row) as conn:
#         with conn.cursor() as cur:
#
#             crate_user_script = ''' CREATE TABLE IF NOT EXISTS user_account (
#                                         id              serial PRIMARY KEY,
#                                         name            varchar(60),
#                                         telegram_id     varchar(60),
#                                         validity        date,
#                                         create_date     timestamp,
#                                         write_date      timestamp
#             )'''
#             cur.execute(crate_user_script)
#
#             create_mcq_script = ''' CREATE TABLE IF NOT EXISTS mcq (
#                                     id          serial PRIMARY KEY,
#                                     question    text NOT NULL,
#                                     ans         varchar(20),
#                                     category    varchar(40),
#                                     user_account_id     integer REFERENCES user_account ON DELETE SET NULL,
#                                     note        varchar(40),
#                                     create_date timestamp,
#                                     write_date  timestamp
#             )'''
#             cur.execute(create_mcq_script)
#
#             # insert_script = 'INSERT INTO employee (id, name, salary, dept_id) VALUES (%s, %s, %s, %s)'
#             # insert_values = [(1, 'James', 15000, 'D1'), (2, 'John', 13000, 'D2')]
#             # for rec in insert_values:
#             #     cur.execute(insert_script, rec)
#             #
#             # insert_user_script = ''' INSERT INTO user (name, '''
#
# except Exception as error:
#     print(error)
#
# finally:
#     if conn is not None:
#         conn.close()
