import docker, requests
from passlib.hash import pbkdf2_sha256
from ocha.libs import utils
from getpass import getpass


client = docker.from_env()

# deploying in docker
def check_image(app_name):
    try:
        img_chek = client.images.get(app_name)
    except Exception:
        return None
    else:
       return img_chek


def docker_deploy(ocha_object, app_path):
    app_name = ocha_object['config']['app']['name']
    img_data = check_image(app_name)
    if img_data:
        client.images.remove(image=app_name)

def check_neo_service(id_vm):
    env_data = utils.get_env_values()
    password = getpass("Your Neo Password: ")
    password_unhash = pbkdf2_sha256.verify(password, env_data['password'])
    head_url = env_data['project_url']+":"+env_data['project_port']
    auth = None
    if not password_unhash:
        print("Password Wrong")
        exit()
    else:
        url_login = head_url+"/api/login"
        auth = utils.sign_to_project(url_login,env_data['username'], password)
    auth = auth['data']['access_token']
    headers = {
        "Access-Token": auth
    }
    url_vm = head_url+"/api/list/vm/"+id_vm
    
    try:
        data_vm = utils.get_http(url_vm, headers=headers)
        data_vm = data_vm['data']
    except Exception:
        return None
    else:
        return data_vm

def neo_deploy_new(ocha_object):
    env_data = utils.get_env_values()
    password = getpass("Your Neo Password: ")
    password_unhash = pbkdf2_sha256.verify(password, env_data['password'])
    head_url = env_data['project_url']+":"+env_data['project_port']
    auth = None
    if not password_unhash:
        print("Password Wrong")
        exit()
    else:
        url_login = head_url+"/api/login"
        auth = utils.sign_to_project(url_login,env_data['username'], password)
    auth = auth['data']['access_token']
    headers = {
        "Access-Token": auth
    }
    app_name = ocha_object['config']['app']['name']
    app_port = ocha_object['config']['app']['port']
    username = env_data['username']
    username = username.split("@")[0]
    send_to_openstack={
        "instances": {
            app_name: {
                "parameters": {
                    "app_name": app_name,
                    "app_port":app_port,
                    "private_network": "vm-net",
                    "key_name": "vm-key",
                    "username": username
                },
                "template": "bless"
            }
        }
    }

    url_vm = head_url+"/api/create"
    res_fix = dict()
    data_create = list()
    data_respon = list()
    data_pemkey = ""

    try:
        data_create = utils.send_http(url_vm, send_to_openstack, headers)
    except Exception as e:
        print(e)
        exit()

    url_vm = head_url+"/api/list/vm"
    url_pemkey = head_url+"/api/list/pemkey/"+app_name
    check = True
    while check:
        data_vm = utils.get_http(url_vm, headers=headers)
        if data_vm['data']:
            check = False

    for i in data_vm['data']:
        if i['name'] == app_name:
            res_fix = i
    data_pemkey = utils.get_http(url_pemkey, headers=headers)

    data_respon.append({
        "create": data_create['data'],
        "vm": res_fix,
        "pemkey": data_pemkey
    })
    return data_respon


# Deploying in neo service
def neo_deploy(ocha_object, app_path):
    env_data = utils.get_env_values()
    password = getpass("Your Neo Password: ")
    password_unhash = pbkdf2_sha256.verify(password, env_data['password'])
    head_url = env_data['project_url']+":"+env_data['project_port']
    auth = None
    
    if not password_unhash:
        print("Password Wrong")
        exit()
    else:
        url_login = head_url+"/api/sign"
        auth = utils.sign_to_project(url_login,env_data['username'], password) 
    auth = auth['data']['token']
    files = {'ocha_file': open(app_path+"/.deploy/ocha.ocha",'rb')}

    headers = {
        "Authorization": auth
    }
    values = {
        'app_name': ocha_object['config']['app']['name'],
        'app_port': ocha_object['config']['app']['port'],
        'username': env_data['username'],
    }

    respons = requests.post(head_url+"/api/project", files=files, data=values, headers=headers)
    return respons.json()