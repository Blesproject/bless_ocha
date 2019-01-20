import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from ocha.libs import utils
from passlib.hash import pbkdf2_sha256
from ocha.libs import setting

def check_db(qry, db, db_name):
    db.execute(qry)
    for row in db.fetchall():
        if row[0] == db_name:
            return True
        else:
            return False

def insert(db,table, data = None):
    value = ''
    column = ''
    for row in data:
        column += row+","
        value += "'"+str(data[row]+"',")
    column = "("+column[:-1]+")"
    value = "("+value[:-1]+")"
    try:
        db.execute("INSERT INTO "+table+" "+column+" VALUES "+value+" RETURNING *")
    except (Exception, psycopg2.DatabaseError) as e:
        raise e
    else:
        id_of_new_row = db.fetchone()[0]
        return str(id_of_new_row)


def database_setting(config):
    conn = psycopg2.connect(
        user=config['username'],
        sslmode=config['ssl'],
        port=config['port'],
        host=config['host']
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    db = conn.cursor()
    if check_db('SHOW DATABASES', db, config['name']):
        conn = psycopg2.connect(
            database=config['name'],
            user=config['username'],
            sslmode=config['ssl'],
            port=config['port'],
            host=config['host']
        )
        db = conn.cursor()
        conn.set_session(autocommit=True)
        try:
            db.execute("SHOW TABLES")
        except (Exception, psycopg2.DatabaseError) as e:
            utils.log_err(e)
    
        else:
            data = db.fetchall()
            utils.log_warn("Remove All Tables")
            for i in data:
                qry = None
                qry = "DROP TABLE "+i[0]
                try:
                    db.execute(qry)
                except (Exception, psycopg2.DatabaseError) as e:
                    raise e
    else:
        db_check = None
        try:
            db.execute("CREATE DATABASE "+config['name'])
        except (Exception, psycopg2.DatabaseError) as e:
            utils.log_err(e)
            db_check = True

        if db_check:
            conn = psycopg2.connect(
                database=config['name'],
                user=config['username'],
                sslmode=config['ssl'],
                port=config['port'],
                host=config['host']
            )
            db = conn.cursor()
            conn.set_session(autocommit=True)
            try:
                db.execute("SHOW TABLES")
            except (Exception, psycopg2.DatabaseError) as e:
                utils.log_err(e)
            else:
                data = db.fetchall()
                utils.log_warn("Remove All Tables")

                for i in data:
                    qry = None
                    qry = "DROP TABLE "+i[0]
                    try:
                        db.execute(qry)
                    except (Exception, psycopg2.DatabaseError) as e:
                        raise e
        else:
            conn = psycopg2.connect(
                database=config['name'],
                user=config['username'],
                sslmode=config['ssl'],
                port=config['port'],
                host=config['host']
            )

    db = conn.cursor()
    conn.set_session(autocommit=True)

    return db

def database_parse(config, obj_database, security = None, auth_config= None):
    db = database_setting(config)
    # # data_finish = list()
    if security:
        df_table = setting.default_table
        for d_tables in df_table['tables']:
            config_table = list()
            for column in df_table['tables'][d_tables]:
                data_f = {
                    "column": column,
                    "rules": df_table['tables'][d_tables][column]
                }
                config_table.append(data_f)
            query = create_table(d_tables, config_table)
            execute_query(query,db)
        utils.report("Default Table Created")

    for tables in obj_database['tables']:
        config_table = list()
        for column in obj_database['tables'][tables]:
            data_f = {
                "column": column,
                "rules": obj_database['tables'][tables][column]
            }
            config_table.append(data_f)
        query = create_table(tables, config_table)
        execute_query(query,db)

    if security:
        # inserting admin user
        admin_userdata = {
            'first_name': auth_config['user'],
            'last_name': auth_config['user'],
            'location': '',
            'email': auth_config['email'],
        }
        id_userdata = insert(db,'tb_userdata', admin_userdata)
        if id_userdata:
            password_hash = pbkdf2_sha256.hash(auth_config['password'])
            admin_login = {
                'id_userdata': id_userdata,
                'username': auth_config['user'],
                'password': password_hash
            }
            insert(db, 'tb_user', admin_login)


def create_table(tables, config_table): 
    query = "CREATE TABLE "+tables
    str_config = ""
    pkey_config = ""
    unique_config= ""
    family_config = ""
    foreign_config = ""

    for k_column in config_table:
        check_foreign = None
        not_null = ""
        default = ""
        pmr_key = ""
        type_data = ""
        try:
            if k_column['rules']['notNull']:
                not_null="NOT NULL"
            else:
                not_null = "NULL"
        except Exception:
            pass

        if k_column['rules']['type']=='serial':
            default = "DEFAULT unique_rowid()"
            type_data = "int"
        else:
            type_data = k_column['rules']['type']
        try:
            if k_column['rules']['primaryKey']:
                pmr_key ="CONSTRAINT "+tables+"_pk PRIMARY KEY ("+k_column['column']+" ASC)"
            else:
                pmr_key = ""
        except Exception:
            pass

        try:
            if k_column['rules']['unique']:
                unique_config +="UNIQUE INDEX "+tables+"_un ("+k_column['column']+" ASC),\n"
            else:
                unique_config = ""
        except Exception:
            pass
        
        try:
            check_foreign = k_column['rules']['foreignKey']
        except Exception:
            check_foreign

        if check_foreign:
            foreign_config += "CONSTRAINT "+tables+"_"+k_column['rules']['foreignKey']['reference']+"_fk FOREIGN KEY ("+k_column['rules']['foreignKey']['field']+") REFERENCES "+k_column['rules']['foreignKey']['reference']+" ("+k_column['rules']['foreignKey']['field']+") ON DELETE "+k_column['rules']['foreignKey']['on_delete']+" ON UPDATE "+k_column['rules']['foreignKey']['on_update']+",\n"


        str_config += k_column['column']+" "+type_data+" "+not_null+" "+default+",\n"
        pkey_config += pmr_key
        family_config += k_column['column']+","
    family_config = "FAMILY \"primary\" ("+family_config[:-1]+")"
    query_fix = query+" (\n"+str_config+"\n"+pkey_config+",\n"+foreign_config+unique_config+"\n"+family_config+")"
    return query_fix


def execute_query(query, db):
    try:
        db.execute(query)
        return db
    except (Exception, psycopg2.DatabaseError) as e:
        raise e