import paramiko
import json
import configparser
from datetime import datetime

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

log_file_name = "cis_benchmark_"+ip+"_"+datetime.today().strftime('%Y-%m-%d')+".log"
LOG_FILE = open(log_file_name, "a")

no_passed = 0

def auditor_engine(item):
    global no_passed
    print(item['name'] +" : ", end = '')
    LOG_FILE.write("--------- "+item['name'] + " ---------\n\n")
    item_pass = True
    for audit_item in item['audit']:

        if audit_item['elevated'] == True:
            stdin, stdout, stderr = ssh.exec_command("sudo -S " + audit_item['cmd'])
            stdin.write(password+ "\n")
            stdin.flush()            
        else:
            stdin,stdout,stderr=ssh.exec_command(audit_item['cmd'])

        LOG_FILE.write("[COMMAND] : \n"+audit_item['cmd'] + '\n\n')
        outlines=stdout.readlines()
        stdout_string=''.join(outlines[:max_outlines])
        LOG_FILE.write("[STDOUT] : \n"+stdout_string + '\n\n')
        errlines=stdout.readlines()
        err_string=''.join(errlines[:max_errlines])
        LOG_FILE.write("[STDERR] : \n"+err_string + '\n\n')
        item_eval = response_evaluator(stdout_string,err_string,audit_item['response_conditions'])
        item_pass = item_pass and item_eval
    if item_pass:
        print("PASSED")
        LOG_FILE.write("[VERDICT] : PASSED\n")
        no_passed = no_passed + 1
    else:
        print("FAILED")
        LOG_FILE.write("[VERDICT] : FAILED\n")
        

def response_evaluator(stdout_string,err_string,response_conditions):
    condition = False
    first_run = True
    for response_condition in response_conditions:
        iter_response_condition = False
        
        if response_condition['on'] == 'stdout':
            response_string = stdout_string
        elif response_condition['on'] == 'stderr':
            response_string = err_string

        if response_condition['condition'] == 'like':
            if response_condition['like_to'] in response_string: 
                iter_response_condition = True
        elif response_condition['condition'] == 'not_like':
            if response_condition['not_like_to'] not in response_string: 
                iter_response_condition = True
        elif response_condition['condition'] == 'pass_if_no_lines':
            if response_string == "": 
                iter_response_condition = True
        elif response_condition['condition'] == 'pass_if_lines':
            if response_string != "": 
                iter_response_condition = True
        elif response_condition['condition'] == 'default_pass':
            #### log here
            pass

        if response_condition['control_flag'] == 'required':
            if first_run:
                condition = condition or iter_response_condition
                first_run = False
            else:
                condition = condition and iter_response_condition
        elif response_condition['control_flag'] == 'optional':
            condition = condition or iter_response_condition
        
    return condition


def main():
    global no_passed
    print (benchmark['title'])
    for item in benchmark['items']:
        auditor_engine(item)

    print (str(no_passed)+"/"+str(len(benchmark['items']))+" PASSED")

if __name__ == "__main__":
    main()

