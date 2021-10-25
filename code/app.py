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

max_outlines = 25
max_errlines = 25

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ip,port,username,password)

f = open(benchmark_file,)
benchmark = json.load(f)

def auditor_engine(item):
    print(item['name'] +" : ", end = '')
    item_pass = True
    for audit_item in item['audit']:

        if audit_item['elevated'] == True:
            stdin, stdout, stderr = ssh.exec_command("sudo -S " + audit_item['cmd'])
            stdin.write(password+ "\n")
            stdin.flush()            
        else:
            stdin,stdout,stderr=ssh.exec_command(audit_item['cmd'])
        outlines=stdout.readlines()
        stdout_string=''.join(outlines[:max_outlines])
        errlines=stdout.readlines()
        err_string=''.join(errlines[:max_errlines])
        item_eval = response_evaluator(stdout_string,err_string,audit_item['response_conditions'])
        item_pass = item_pass and item_eval
    if item_pass:
        print("PASSED")
    else:
        print("FAILED")
        

def response_evaluator(stdout_string,err_string,response_conditions):
    condition = True
    for response_condition in response_conditions:
        iter_response_condition = True
        if response_condition['on'] == 'stdout':
            response_string = stdout_string
            if err_string != "":
                iter_response_condition = False
        else:
            response_string = err_string
            if response_string != "":
                iter_response_condition = False

        if iter_response_condition: #only proceed if the iter condition is still true
            
            if response_condition['condition'] == 'like':
                if response_condition['like_to'] not in response_string: 
                    iter_response_condition = False
            elif response_condition['condition'] == 'not_like':
                if response_condition['not_like_to'] in response_string: 
                    iter_response_condition = False
            elif response_condition['condition'] == 'pass_if_no_lines':
                if response_string != "": 
                    iter_response_condition = False
            elif response_condition['condition'] == 'pass_if_lines':
                if response_string == "": 
                    iter_response_condition = False

            if response_condition['control_flag'] == 'required':
                condition = condition and iter_response_condition
            elif response_condition['control_flag'] == 'optional':
                condition = condition or iter_response_condition
        

    if condition:
        return True
    else:
        return False

        

print (benchmark['title'])

for item in benchmark['items']:
    auditor_engine(item)
