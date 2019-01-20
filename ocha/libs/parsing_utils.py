from ocha.libs import utils
import os, yaml
from ocha.libs import setting


def create_production_env(data_env, app_path):
    host = data_env['app']['host']
    port = data_env['app']['port']
    f=open(app_path+"/production.sh", "a+")
    f.write("gunicorn production:app -b "+str(host)+":"+str(port)+" -w 2 --chdir "+app_path+"/")
    f.close()


def create_env(data_env, app_path):
    db_driver = None
    try:
        db_driver = data_env['database']['driver']
    except Exception:
        db_driver = "cockroachdb"

    env_check = None
    try:
        env_check = data_env['app']['environment']
    except Exception as e:
        print(e)

    env_sett = ""
    if env_check:
        
        if env_check == 'production':
            env_sett = "False"
        else:
            env_sett = "True"

    f=open(app_path+"/.env", "a+")
    # APP CONFIG
    f.write("APP_NAME = "+data_env['app']['name'])
    f.write("\n")
    f.write("APP_HOST = "+data_env['app']['host'])
    f.write("\n")
    f.write("APP_PORT = "+str(data_env['app']['port']))
    f.write("\n")
    f.write("FLASK_DEBUG = "+env_sett)
    f.write("\n")
    f.write("\n")

    # MEMCACHE CONFIG
    f.write("MEMCACHE_HOST = "+data_env['app']['host'])
    f.write("\n")
    f.write("MEMCACHE_PORT = 11211")
    f.write("\n")
    f.write("\n")
    # DATABASE CONFIG
    f.write("DB_NAME = "+data_env['database']['name'])
    f.write("\n")
    f.write("DB_HOST = "+data_env['database']['host'])
    f.write("\n")
    f.write("DB_PORT = "+str(data_env['database']['port']))
    f.write("\n")
    f.write("DB_USER = "+data_env['database']['username'])
    f.write("\n")
    f.write("DB_SSL = "+data_env['database']['ssl'])
    f.write("\n")
    f.write("DB_DRIVER = "+db_driver)
    f.write("\n")
    f.write("\n")
    # REDIS CONFIG
    f.write("FLASK_REDIS_URL = redis://:"+data_env['redis']['password']+"@"+str(data_env['redis']['host'])+":"+str(data_env['redis']['port'])+"/0")
    f.write("\n")
    f.write("\n")
    f.write("JWT_SECRET_KEY = wqertyudfgfhjhkcxvbnmn@123$32213")
    f.close()


def create_file_controller(nm_controller, app_path, security): 
    controller_path = app_path+"/app/controllers/api"
    file_controller_path = controller_path+"/"+nm_controller+".py"
    create_controller(nm_controller,file_controller_path, security)


def create_controller(nm_controller, file_controller_path, security):
    sec_value = ""

    if security == True:
        sec_value = "@jwt_required"
    
    nm_ctrl = nm_controller.capitalize()
    f=open(file_controller_path, "a+")
    value_ctrl = """from flask_restful import Resource, reqparse, request
from app.helpers.rest import response
from app.helpers import cmd_parser as cmd
from app import psycopg2
from app.libs import utils
from app.models import model as db
from app.middlewares.auth import jwt_required
from app.helpers import endpoint_parse as ep
import json

class """+nm_ctrl+"""(Resource):
    """+sec_value+"""
    def post(self):
        json_req = request.get_json(force=True)
        command = utils.get_command(request.path)
        command = command
        init_data = cmd.parser(json_req, command)
        a = ep.endpoint_parser(command, init_data)
        return response(200, data=a)
    """
    f.write(value_ctrl)
    f.close()

def read_app(app_name, path=None):
    if path is None:
        app_path = utils.APP_HOME+"/BLESS/"+app_name
    else:
        app_path = path+"/"+app_name
    if not os.path.exists(app_path):
        return None
    else:
        return app_path


def set_endpoint_template(endpoint_obj, app_path):
    endpoint_fix = {
        "endpoint": endpoint_obj
    }
    endpoint_value = yaml.dump(endpoint_fix)
    template_path = app_path+"/app/static/templates/endpoint.yml"
    f=open(template_path, "a+")
    f.write(endpoint_value)
    f.close()


def create_app(app_name, app_framework, path=None):
    url_git = "https://github.com/Blesproject/bless_"+app_framework+".git"
    if path is None:
        app_path = utils.APP_HOME+"/BLESS"
        dst_path = app_path+"/"+app_name
    else:
        app_path = path
        dst_path = app_path+"/"+app_name

    if not os.path.exists(app_path):
        os.makedirs(app_path)
        # copy(flask_path,dst_path)
        try:
            clone = utils.template_git(url=url_git, dir=dst_path)
        except Exception as e:
            print(str(e))
        else:
            return True
    else:
        # copy(flask_path,dst_path)
        try:
            clone = utils.template_git(url=url_git, dir=dst_path)
        except Exception as e:
            print(str(e))
        else:
            return False

def create_routing(endpoint_obj, app_path):
    init_import = "from flask import Blueprint\nfrom flask_restful import Api \nfrom .user import *\nfrom .auth import *\n"
    ctrl_import = ""
    for i in endpoint_obj:
        ctrl_import += "from ."+i+" import * \n"
    p_import = init_import+ctrl_import
    
    value_start = """\n\napi_blueprint = Blueprint("api", __name__, url_prefix='/api')
api = Api(api_blueprint)
api.add_resource(UserdataResource, '/user')
api.add_resource(UserdataResourceById, '/user/<userdata_id>')
api.add_resource(UserdataInsert, '/user')
api.add_resource(UserdataUpdate, '/user/<userdata_id>')
api.add_resource(UserdataRemove, '/user/<userdata_id>')

api.add_resource(Usersignin, '/sign')
api.add_resource(UserTokenRefresh, '/sign/token')
api.add_resource(UserloginInsert, '/user/add')\n"""

    value_default = p_import+value_start
    add_resource_data = ""
    for a in endpoint_obj:
        ctrl_class = a.capitalize()
        add_resource_data  += "api.add_resource("+ctrl_class+", '/"+a+"')\n"
    
    all_value = value_default+ add_resource_data
    
    init_path = app_path+"/app/controllers/api/__init__.py"
    f=open(init_path, "a+")
    f.write(all_value)
    f.close()


def create_moduls(moduls_name, moduls_data, app_path, sync_md=None):
    import_value = "from app.models import model as db\n\n\n"
    moduls_path = ""
    file_moduls_path = ""
    if sync_md is None:
        moduls_path = app_path+"/app/moduls/"
        file_moduls_path = moduls_path+moduls_name+".py"
    else:
        moduls_path = app_path+"/moduls/"
        file_moduls_path = moduls_path+moduls_name+".py"

    f=open(file_moduls_path, "a+")
    f.write(import_value)
    function_value = ""
    utils.report("Moduls "+moduls_name+" Create")
    for i in moduls_data:
        if moduls_data[i]['action'] == 'insert':
            function_value += """def """+moduls_data[i]['action']+"""(args):
    # your code here
    table = args['table']
    fields = args['fields']
    try:
        result = db.insert(table, fields)
    except Exception as e:
        respons = {
            "status": False,
            "error": str(e)
        }
    else:
        respons = {
            "status": True,
            "messages": "Fine!",
            "id": result
        }
    finally:
        return respons\n\n
    """

        elif moduls_data[i]['action'] == 'remove':
            function_value += """def """+moduls_data[i]['action']+"""(args):
    # your code here
    table = args['table']
    fields = ""
    field_value = ""
    for i in args['fields']:
        fields = i
        field_value = args['fields'][i]
    try:
        result = db.delete(table,fields,field_value)
    except Exception as e:
        respons = {
            "status": False,
            "messages": str(e)
        }
    else:
        respons = {
            "status": result,
            "messages": "Fine Deleted!"
        }
    finally:
        return respons\n\n
    """
        elif moduls_data[i]['action'] == 'get':
            function_value += """def """+moduls_data[i]['action']+"""(args):
    # your code here
    col = db.get_columns(args['table'])
    dt_types = db.get_types(args['table'])
    results = None
    try:
        results = db.get_all(args['table'])
    except Exception as e:
        return {
            'error': str(e)
        }
    else:
        respons = list()
        for i in results:
            index = 0
            data = dict()
            for a in i:
                if a in col:
                    if dt_types[index] == 'INT':
                        data[a]=str(i[a])
                    else:
                        data[a]=str(i[a])
                    index += 1
            respons.append(data)
        return respons\n\n
    """
        elif moduls_data[i]['action'] == 'where':
            function_value += """def """+moduls_data[i]['action']+"""(args):
    # your code here
    col = db.get_columns(args['table'])
    dt_types = db.get_types(args['table'])
    results = None
    fields = ""
    field_value = ""
    for i in args['fields']:
        fields = i
        field_value = args['fields'][i]
    try:
        results = db.get_by_id(args['table'],fields,field_value)
    except Exception as e:
        return {
            'error': str(e)
        }
    else:
        respons = list()
        for i in results:
            index = 0
            data = dict()
            for a in i:
                if a in col:
                    if dt_types[index] == 'INT':
                        data[a]=str(i[a])
                    else:
                        data[a]=str(i[a])
                    index += 1
            respons.append(data)
        return respons\n\n
    """
        else:
            function_value += """def """+moduls_data[i]['action']+"""(args):
    # your code here
        return args\n\n
    """
    
    f.write(function_value)
    f.close()

def add_function_moduls(moduls_name, moduls_data, app_path, sync_md = None):
    moduls_path = ""
    file_moduls_path = ""
    if sync_md is None:
        moduls_path = app_path+"/app/moduls/"
        file_moduls_path = moduls_path+moduls_name+".py"
    else:
        moduls_path = app_path+"/moduls/"
        file_moduls_path = moduls_path+moduls_name+".py"

    with open(file_moduls_path, "a") as myfile:
        function_value = ""
        for i in moduls_data:
            # print(i)
            if moduls_data[i]['action'] == 'insert':
                function_value += """
def """+moduls_data[i]['action']+"""(args):
    # your code here
    table = args['table']
    fields = args['fields']
    try:
        result = db.insert(table, fields)
    except Exception as e:
        respons = {
            "status": False,
            "error": str(e)
        }
    else:
        respons = {
            "status": True,
            "messages": "Fine!",
            "id": result
        }
    finally:
        return respons\n\n
"""

            elif moduls_data[i]['action'] == 'remove':
                function_value += """
def """+moduls_data[i]['action']+"""(args):
    # your code here
    table = args['table']
    fields = ""
    field_value = ""
    for i in args['fields']:
        fields = i
        field_value = args['fields'][i]
    try:
        result = db.delete(table,fields,field_value)
    except Exception as e:
        respons = {
            "status": False,
            "messages": str(e)
        }
    else:
        respons = {
            "status": result,
            "messages": "Fine Deleted!"
        }
    finally:
        return respons\n\n
"""
            elif moduls_data[i]['action'] == 'get':
                function_value += """
def """+moduls_data[i]['action']+"""(args):
    # your code here
    col = db.get_columns(args['table'])
    dt_types = db.get_types(args['table'])
    results = None
    try:
        results = db.get_all(args['table'])
    except Exception as e:
        return {
            'error': str(e)
        }
    else:
        respons = list()
        for i in results:
            index = 0
            data = dict()
            for a in i:
                if a in col:
                    if dt_types[index] == 'INT':
                        data[a]=str(i[a])
                    else:
                        data[a]=str(i[a])
                    index += 1
            respons.append(data)
        return respons\n\n
    """
            elif moduls_data[i]['action'] == 'where':
                function_value += """
def """+moduls_data[i]['action']+"""(args):
    col = db.get_columns(args['table'])
    dt_types = db.get_types(args['table'])
    results = None
    fields = ""
    field_value = ""
    for i in args['fields']:
        fields = i
        field_value = args['fields'][i]
    try:
        results = db.get_by_id(args['table'],fields,field_value)
    except Exception as e:
        return {
            'error': str(e)
        }
    else:
        respons = list()
        for i in results:
            index = 0
            data = dict()
            for a in i:
                if a in col:
                    if dt_types[index] == 'INT':
                        data[a]=str(i[a])
                    else:
                        data[a]=str(i[a])
                    index += 1
            respons.append(data)
        return respons\n\n
    """
            else:
                function_value += """
def """+moduls_data[i]['action']+"""(args):
    # your code here
    return args\n\n
"""
        myfile.write(function_value)



