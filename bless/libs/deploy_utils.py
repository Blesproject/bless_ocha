import docker, requests
from passlib.hash import pbkdf2_sha256
from bless.libs import utils
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


def docker_deploy(bless_object, app_path):
    app_name = bless_object['config']['app']['name']
    img_data = check_image(app_name)
    if img_data:
        client.images.remove(image=app_name)
    

def neo_deploy_new(bless_object):
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
    app_name = bless_object['config']['app']['name']
    app_port = bless_object['config']['app']['port']
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
        url_vm = head_url+"/api/list/vm"
        url_pemkey = head_url+"/api/list/pemkey/"+app_name
        c_limit = True;
        while c_limit:
            data_vm = utils.get_http(url_vm, headers=headers)
            for i in data_vm['data']:
                if i['name'] == app_name:
                    res_fix = i
                    c_limit = False
            data_pemkey = utils.get_http(url_pemkey, headers=headers)
    except Exception as e:
        return e
    else:
        data_respon.append({
            "create": data_create['data'],
            "vm": res_fix,
            "pemkey": data_pemkey
        })
        return data_respon


# Deploying in neo service
def neo_deploy(bless_object, app_path):
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
    files = {'bless_file': open(app_path+"/.deploy/bless.ocha",'rb')}

    headers = {
        "Authorization": auth
    }
    values = {
        'app_name': bless_object['config']['app']['name'],
        'app_port': bless_object['config']['app']['port'],
        'username': env_data['username'],
    }

    respons = requests.post(head_url+"/api/project", files=files, data=values, headers=headers)
    return respons.json()