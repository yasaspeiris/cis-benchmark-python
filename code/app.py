import paramiko
import configparser
config = configparser.ConfigParser() 
config.read(r'cis-benchmark-config.txt')

username = config['session']['username']
password = config['session']['password']
ip = config['session']['ip']
port = config['session']['port']

cmd='uname' 

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ip,port,username,password)

stdin,stdout,stderr=ssh.exec_command(cmd)
outlines=stdout.readlines()
resp=''.join(outlines)
print(resp)