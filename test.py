import os
import subprocess
from traceback import print_tb
from ansible_runner.runner import ansible_runner
from pandas._libs import index
from pandas.core.frame import IgnoreRaise
from pandas.tseries.offsets import CustomBusinessDay
import paramiko
import pandas as pd
from ansible_runner import run

CURRENT_DIR = os.getcwd()

def create_inventory():
# Read Workbook
   df_input = pd.read_csv('input.csv',delimiter=',',index_col=False)
   ip_count = 0
   list_ssh_fail = []
   list_OS = []
# Create and open inventory
   os.mkdir("inventory")
# Application
   for row in range(0, df_input.shape[0]):
# Variable
      host_ip = df_input.loc[row,'ip']
      username = df_input.loc[row,'user']
      user_pass = df_input.loc[row,'user_pass']
      root_pass = df_input.loc[row,'root_pass']
# SSH connect
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      try:
         ssh.connect(hostname=host_ip,username=username,password=str(user_pass),timeout=0.1)
         (ssh_stdin, ssh_stdout, ssh_stderr)= ssh.exec_command('. /etc/os-release; echo "$ID"')
         ip_count += 1
         print(f'{host_ip} OK!')
         host_os = ssh_stdout.readline().rstrip().lower()
         inventory = open(f'./inventory/{host_os}_family_inventory.ini','a')
         inventory.write(f"{host_ip} ansible_user={username} ansible_password={user_pass} ansible_sudo_pass={root_pass}\n")
         inventory.close()
         if host_os not in list_OS:
            list_OS.append(host_os)
      except:
         fail_ssh = f'{host_ip} SSH Fail!'
         list_ssh_fail.append(fail_ssh)
         print(fail_ssh)
# Close ssh connect
      ssh.close()
# Save file inventory
   print(f'Got data from {ip_count}-server')
   return list_OS, list_ssh_fail

def check_list_OS(list_OS):
# Define inventory
   inventory_dir = './inventory'
# Set the option for the runner
   for os in list_OS:
      run_playbook = CURRENT_DIR + f'/playbook/{os}/check_list.yaml'
      run_inventory = CURRENT_DIR + f'/inventory/{os}_family_inventory.ini'
      check_list = ansible_runner.run(
         private_data_dir = inventory_dir,
         inventory = run_inventory,
         playbook = run_playbook
      )

def setup_OS(list_OS):
# Define inventory
   inventory_dir = './inventory'
# Set the option for the runner
   for os in list_OS:
      run_playbook = CURRENT_DIR + f'/playbook/{os}/setup.yaml'
      run_inventory = CURRENT_DIR + f'/inventory/{os}_family_inventory.ini'
      check_list = ansible_runner.run(
         private_data_dir = inventory_dir,
         inventory = run_inventory,
         playbook = run_playbook
      )

def reboot_OS(list_OS):
# Define inventory
   inventory_dir = './inventory'
# Set the option for the runner
   for os in list_OS:
      run_playbook = CURRENT_DIR + f'/playbook/reboot.yaml'
      run_inventory = CURRENT_DIR + f'/inventory/{os}_family_inventory.ini'
      check_list = ansible_runner.run(
         private_data_dir = inventory_dir,
         inventory = run_inventory,
         playbook = run_playbook
      )

def highlight(x):
   color = ['darkgreen','darkorange','darkred','darkblue','black']
   bg_color = ['honeydew','antiquewhite','mistyrose','lightsteelblue','white']
   if x == 'OK':
      i = 0
   elif x == 'WARNING':
      i = 1
   elif x == 'NOK':
      i = 2
   elif x == 'FAIL':
      i = 3
   else:
      i = 4
   return f'color: {color[i]}; background-color: {bg_color[i]}'

def condition(row):
   if row.eq('OK').all():
      return 'OK'
   else:
      return 'NOK'

def generate_result(list_OS, list_ssh_fail):
# Take dataframe from collect_data
   writer = pd.ExcelWriter('result.xlsx')

# Create a total result column
   # Create sheet Ubuntu in result
   for os in list_OS:
      index = []
      df = f'df_{os}'
      df = pd.read_csv(f'output_{os}_family.csv',delimiter=';')
      for i in range(2,df.shape[1]):
         index.append(i)
      df.fillna('FAIL', inplace= True)
      df['FINAL_RESULT'] = df.iloc[:,index].apply(condition,axis=1)
      df.insert(2,'FINAL_RESULT',df.pop('FINAL_RESULT'))
      df.style.applymap(highlight).to_excel(writer, sheet_name=f'{os}',index=False)
      subprocess.run(['rm',f'output_{os}_family.csv'])

   # Print ip fail to file result
   if list_ssh_fail != []:
      df_fail = pd.Series(list_ssh_fail)
      df_fail.to_excel(writer,sheet_name="IP_SSH_FAIL", header=False, index=False)

   writer.close()

if __name__ == '__main__':
   choice = 0
   print('Loading...')
   list_OS, list_ssh_fail = create_inventory()
   while choice != 4:
      print('Please choice what to do next\n1. Check_list\n2. Setup\n3. Reboot after config\n4. End!')
      choice = int(input('Choice: '))
      if int(choice) not in range(0,4):
         print('Try again!')
      elif int(choice) == 1:
         check_list_OS(list_OS)
         generate_result(list_OS,list_ssh_fail)
      elif int(choice) == 2:
         setup_OS(list_OS)
      elif int(choice) == 3:
         reboot_OS(list_OS)
# Remove unexpected result
   subprocess.run(['rm', '-rf', 'inventory'])
   print('Done!')
