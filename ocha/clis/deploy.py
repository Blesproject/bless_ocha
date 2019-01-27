from ocha.clis.base import Base
from ocha.libs import deploy_utils, scp_utils
import os , time


CURR_DIR = os.getcwd()
APP_HOME = deploy_utils.utils.APP_HOME

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
            ocha_object = deploy_utils.utils.yaml_read(CURR_DIR+"/.deploy/ocha.ocha")
            deploy_utils.docker_deploy(ocha_object, CURR_DIR)

        if self.args['neo']:
            ocha_config = deploy_utils.utils.yaml_read(CURR_DIR+"/config.ocha")
            if deploy_utils.utils.read_file(CURR_DIR+"/.deploy/deploy.ocha"):
                deploy_data = deploy_utils.utils.yaml_read(CURR_DIR+"/.deploy/deploy.ocha")
                id_vm = deploy_data['id_vm']
                data = deploy_utils.check_neo_service(id_vm)
                if data is not None:
                    print("WARNING: Your Neo Service Is Ready | Run: ocha modul sync to sync local project on neo service")
                    exit()

            respon = deploy_utils.neo_deploy_new(ocha_config)
           
            data_vm = dict()
            data_project = dict()
            pemkey=""
            for i in respon:
                data_vm = i['vm']
                data_project = i['create']
                pemkey = i['pemkey']

            pemkey = pemkey['data']['pemkey']
            username = data_project[0]['stack']['parameters']['username']
            data_deploy = {
                "id_vm": data_vm['id'],
                "status": data_vm['status'],
                "username": username,
                "ip": data_vm['ip'][1]
            }
            deploy_utils.utils.yaml_create(data_deploy, CURR_DIR+"/.deploy/deploy.ocha")
            if deploy_utils.utils.read_file(CURR_DIR+"/.deploy/ssh_key.pem"):
                os.remove(CURR_DIR+"/.deploy/ssh_key.pem")
            deploy_utils.utils.create_file("ssh_key.pem", CURR_DIR+"/.deploy/", pemkey)
            os.chmod(CURR_DIR+"/.deploy/ssh_key.pem", 0o600)

            if deploy_utils.utils.read_file(CURR_DIR+"/.deploy/listdir.ocha"):
                os.remove(CURR_DIR+"/.deploy/listdir.ocha")
            file = deploy_utils.utils.list_dir(CURR_DIR)
            deploy_utils.utils.yaml_writeln(file,CURR_DIR+"/.deploy/listdir.ocha")
            app_name = data_project[0]['stack']['parameters']['app_name']
            host = data_vm['ip'][1]
            if deploy_utils.utils.read_file(CURR_DIR+"/."+str(app_name)+".zip"):
                os.remove(CURR_DIR+"/."+str(app_name)+".zip")
            deploy_utils.utils.make_archive("."+str(app_name), CURR_DIR)

            
            print("###############################################")
            print("######### BUILDING NEO SERVICE SUCCESS ########")
            print("###############################################")
            print("ID VM : ",data_vm['id'])
            print("Status : ",data_vm['status'])
            print("Username : ",data_project[0]['stack']['parameters']['username'])
            print("IP : ",data_vm['ip'][1])
            print("PORT : ",data_project[0]['stack']['parameters']['app_port'])
            access_api = "http://"+data_vm['ip'][1]+":"+str(data_project[0]['stack']['parameters']['app_port'])+"/api/<endpoint>"
            print("ACCESS_API: ", access_api)
            print("###############################################")
            print("----------------- DEPLOYING ------------------")
            print("-- DEPLOYING SYSTEM A FEW MINUTE ! RELAXING --")
            print("###############################################")
            time.sleep(120)
            # app_name="ocha_test01"
            # username = "sofyan"
            # host = "103.93.53.106"
            project_archive = CURR_DIR+"/."+str(app_name)+".zip"
            key = CURR_DIR+"/.deploy/ssh_key.pem"
            ssh = scp_utils.ssh_connect(host,username, key_filename=key)
            ssh.get_transport().is_active()
            ftp_client= ssh.open_sftp()
            scp_utils.sync_file(ftp_client, project_archive, "/home/"+username+"/project.zip")
            ftp_client.close()
            print("###############################################")
            print("-------------- DEPLOYING SUCCESS --------------")
            print("###############################################")
            ssh.exec_command("mkdir "+app_name)
            ssh.exec_command("mv project.zip "+app_name+"/"+app_name+".zip")
            ssh.exec_command("cd "+app_name+"; unzip "+app_name+".zip; rm "+app_name+".zip")
            _,stdout,_ = ssh.exec_command("cd "+app_name+"; ocha build;")
            report = stdout.read().decode("utf8")
            print(report)
            print("###############################################")
            ssh.close()
            exit()