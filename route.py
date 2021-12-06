from subprocess import Popen
import shlex
import os

# os.environ["COMSPEC"] = 'powershell'

input_path = './test_data/StickHub.dsn'
output_path = './StickHub.ses'
command_path = ['java.exe', '-jar', './freerouting-1.4.5.1.jar']
args = ['-de', input_path, '-do', output_path, '-mp', '100', '-mt', '12', '-Xmx1024m', '-Xms256m']

process = Popen(command_path + args, shell=True)


process.wait()