create_order_table_sql = ''' 
    CREATE TABLE IF NOT EXISTS user_order (
        id              serial PRIMARY KEY,
        telegram_id     integer,
        username        varchar(60),
        name            varchar(60),            
        duration        integer,
        status          order_type DEFAULT 'waiting',    
        verify_by       integer REFERENCES user_account(telegram_id) ON DELETE SET NULL,
        created_at      timestamp DEFAULT CURRENT_TIMESTAMP,
        updated_at      timestamp DEFAULT CURRENT_TIMESTAMP                                             
    )'''

create_main_cate_user_order_sql = '''
    CREATE TABLE IF NOT EXISTS main_cate_user_order (
        id              serial PRIMARY KEY,
        main_cate_id    integer REFERENCES main_cate,
        user_order_id   integer REFERENCES user_order
    )'''

create_report_table_sql = ''' 
    CREATE TABLE IF NOT EXISTS report (
        id              serial PRIMARY KEY,
        telegram_id     integer,
        username        varchar(60),
        name            varchar(60),
        mcq_id          integer REFERENCES mcq ON DELETE SET NULL,
        status          order_type DEFAULT 'waiting',
        created_at      timestamp DEFAULT CURRENT_TIMESTAMP,
        updated_at      timestamp DEFAULT CURRENT_TIMESTAMP
    )'''

create_main_cate_user_account_table_sql = '''
    CREATE TABLE IF NOT EXISTS main_cate_user_account (
        id              serial PRIMARY KEY,
        main_cate_id    integer REFERENCES main_cate ON DELETE SET NULL,
        telegram_id     integer REFERENCES user_account(telegram_id) on DELETE SET NULL,
        valid_till      date DEFAULT now()::date,
        created_at      timestamp DEFAULT CURRENT_TIMESTAMP,
        updated_at      timestamp DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(main_cate_id, telegram_id)
    )'''

create_mcq_table_sql = ''' 
    CREATE TABLE IF NOT EXISTS mcq (
        id                  serial PRIMARY KEY,
        no                  integer,
        ques                text NOT NULL,
        ans                 varchar(20) NOT NULL,
        explanation         text,
        main_cate_id        integer REFERENCES main_cate ON DELETE SET NULL,
        sub_cate_id         integer REFERENCES sub_cate ON DELETE SET NULL,
        user_account_id     integer REFERENCES user_account ON DELETE SET NULL,
        checked_time        integer,
        note                varchar(40),
        created_at          timestamp DEFAULT CURRENT_TIMESTAMP,
        updated_at          timestamp DEFAULT CURRENT_TIMESTAMP
    )'''

create_sub_cate_table_sql = ''' 
    CREATE TABLE IF NOT EXISTS sub_cate (
        id                  serial PRIMARY KEY,
        name                varchar(60),
        main_category_id    integer REFERENCES main_cate ON DELETE SET NULL,
        created_at          timestamp DEFAULT CURRENT_TIMESTAMP,
        updated_at          timestamp DEFAULT CURRENT_TIMESTAMP
    )'''

create_main_cate_table_sql = ''' 
    CREATE TABLE IF NOT EXISTS main_cate (
        id              serial PRIMARY KEY,
        name            varchar(60),                                                   
        created_at      timestamp DEFAULT CURRENT_TIMESTAMP,
        updated_at      timestamp DEFAULT CURRENT_TIMESTAMP
    )'''

crate_user_script = ''' 
    CREATE TABLE IF NOT EXISTS user_account (
        id              serial PRIMARY KEY,
        telegram_id     integer UNIQUE,
        username        varchar(60),
        name            varchar(60),
        valid_till      date DEFAULT now()::date,
        verified        boolean DEFAULT False,
        is_admin        boolean DEFAULT False,
        total_mark      integer DEFAULT 0,
        time            integer DEFAULT 0,  
        minus_mark      integer DEFAULT 0,
        minus_time      integer DEFAULT 0,
        created_at      timestamp DEFAULT CURRENT_TIMESTAMP,
        updated_at      timestamp DEFAULT CURRENT_TIMESTAMP
    )'''