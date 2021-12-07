from subprocess import Popen
import shlex
import os, shutil
from multiprocessing import Pool
from pathlib import Path

# os.environ["COMSPEC"] = 'powershell'

PARENT_DIR = Path(__file__).absolute().parent

num_runs = 4

input_path = PARENT_DIR / 'test_data' / 'StickHub.dsn'
output_folder = PARENT_DIR / 'output'
jar_path = PARENT_DIR / 'freerouting-1.4.5.1.jar'
command_path = ['java.exe', '-jar', str(jar_path)]

def run_routing(num):
    run_folder = output_folder / f'run_{num}'
    os.makedirs(run_folder)

    new_input_path = run_folder / input_path.name
    shutil.copyfile(input_path, new_input_path)

    output_path = run_folder / 'StickHub.ses'
    args = ['-de', new_input_path, '-do', output_path, '-mp', '100', '-mt', '4', '-test']

    process = Popen(command_path + args, cwd=run_folder)
    process.wait()

    return output_path

def main():

    shutil.rmtree(output_folder, ignore_errors=True)

    run_args = []
    for run in range(num_runs):
        args = []
        args.append(run)

        run_args.append(args)

    with Pool(4) as p:
        print(p.starmap(run_routing, run_args))

if __name__ == '__main__':
    main()