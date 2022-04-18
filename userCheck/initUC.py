import multiprocessing
import subprocess
import pandas as pd

## PXH Configs ##
phxConfig = 'C:\PhoenixControl\MissionControl\configFiles\phxConfig.csv'
#phxConfig2 = 'C:\PhoenixControl\MissionControl\configFiles\phxConfigSHG.csv'
#################

# Import Current Configuration
conf = pd.read_csv(phxConfig)
#conf = conf.append(pd.read_csv(phxConfig2))

def startUserCheck(vm):
    name = vm.split('.')[0]
    cmd = f'powershell .\checkUsers.ps1 -machineDNS {vm} >> out_{name}.log'
    subprocess.run(cmd)

if __name__ == '__main__':
    for vm in conf['vmNameDNS']:
        multiprocessing.Process(target=startUserCheck, args=(vm,)).start()

    print('any key to kill')
    input()