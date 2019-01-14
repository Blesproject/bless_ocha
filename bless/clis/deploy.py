from bless.clis.base import Base
from bless.libs import deploy_utils
import os


CURR_DIR = os.getcwd()

class Deploy(Base):
    """
        usage:
            deploy
            deploy docker
            deploy neo
            deploy [-S server]

        Build Project

        Options:
        -h --help                             Print usage
        -S server --server=SERVER       sequence execute object
    """

    def execute(self):
        if self.args['docker']:
            bless_object = deploy_utils.utils.yaml_read(CURR_DIR+"/.deploy/bless.ocha")
            deploy_utils.docker_deploy(bless_object, CURR_DIR)
        
        if self.args['neo']:
            bless_object = deploy_utils.utils.yaml_read(CURR_DIR+"/.deploy/bless.ocha")
            respon = deploy_utils.neo_deploy(bless_object,CURR_DIR)
            data = respon['data']
            data_vm = dict()
            data_project = dict()
            pemkey=""
            for i in data:
                data_vm = i['vm']
                data_project = i['create']
                pemkey = i['pemkey']
            pemkey = pemkey.decode('utf-8')
            data_deploy = {
                "id_vm": data_vm['id'],
                "status": data_vm['status'],
                "username": data_project[0]['stack']['parameters']['username'],
                "ip": data_vm['ip'][1]
            }
            pemkey_name = data_project[0]['stack']['parameters']['key_name']
            deploy_utils.utils.yaml_create(data_deploy, CURR_DIR+"/.deploy/deploy.ocha")
            deploy_utils.utils.create_file(pemkey_name, CURR_DIR+"/.deploy/", pemkey)
            print("ID VM : ",data_vm['id'])
            print("Status : ",data_vm['status'])
            print("Username : ",data_project[0]['stack']['parameters']['username'])
            print("IP : ",data_vm['ip'][1])
            print("PORT : ",data_project[0]['stack']['parameters']['app_port'])
            access_api = "http://"+data_vm['ip'][1]+":"+data_project[0]['stack']['parameters']['app_port']+"/api/<endpoint>"
            print("ACCESS_API: ", access_api)