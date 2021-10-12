import paramiko
import json
import configparser
import time
config = configparser.ConfigParser() 
config.read(r'cis-benchmark-config.txt')

username = config['session']['username']
password = config['session']['password']
ip = config['session']['ip']
port = config['session']['port']
benchmark_file = config['session']['benchmark']

max_outlines = 20

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ip,port,username,password)

f = open(benchmark_file,)
benchmark = json.load(f)

def auditor_engine(item):
    print(item['name'] +" : ", end = '')
    item_fail = False
    for audit_item in item['audit']:

        if audit_item['elevated'] == True:
            stdin, stdout, stderr = ssh.exec_command("sudo -S " + audit_item['cmd'])
            stdin.write(password+ "\n")
            stdin.flush()            
        else:
            stdin,stdout,stderr=ssh.exec_command(audit_item['cmd'])
        outlines=stdout.readlines()
        response_string=''.join(outlines[:max_outlines])
        item_eval = response_evaluator(response_string,audit_item['response_conditions'])
        item_fail = item_fail or item_eval
    if item_fail:
        print("FAILED")
    else:
        print("PASSED")
        

def response_evaluator(response_string,response_conditions):
    condition_fail = False
    for response_condition in response_conditions:
        if response_condition['condition'] == 'match':
            if response_string != response_condition['match_to']:
                condition_fail = True
        if response_condition['condition'] == 'like':
            if response_condition['like_to'] not in response_string: 
                condition_fail = True
        if response_condition['condition'] == 'pass_if_no_lines':
            if response_string == "": 
                condition_fail = False
            else:
                condition_fail = True
        if response_condition['condition'] == 'pass_if_lines':
            if response_string != "": 
                condition_fail = False
            else:
                condition_fail = True

    if condition_fail == False:
        return False
    else:
        return True

        

print (benchmark['title'])

for item in benchmark['items']:
    auditor_engine(item)
