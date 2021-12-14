from subprocess import Popen
import shlex
import os, shutil
import multiprocessing as mp
from pathlib import Path


PARENT_DIR = Path(__file__).absolute().parent

#num_cores = int(mp.cpu_count() / 2)
num_cores = 1
num_runs = num_cores
run_threads = int(num_cores/num_runs)
num_iterations = 10

print(num_cores, num_runs, run_threads)

input_path = PARENT_DIR / 'test_data' / 'StickHub.dsn'
output_folder = PARENT_DIR / 'output'
jar_path = PARENT_DIR / 'freerouting-1.4.5.1.jar'
command_path = ['java', '-jar', str(jar_path)]

def run_routing(num, iteration):
    print(f'Starting run {num} iteration {iteration}')
    run_folder = output_folder / f'run_{num}'
    input_path = run_folder / f'iteration{iteration}.dsn'
    output_path = run_folder / f'iteration{iteration+1}.dsn'
    args = ['-de', input_path, '-do', output_path, '-mp', '1', '-mt', '1', '-test']

    process = Popen(command_path + args, cwd=run_folder)
    process.wait()
    
    print(f'Finished run {num} iteration {iteration}')

    log_location = run_folder / 'logs' / 'freerouter.log'
    new_log_path = run_folder / 'logs' / f'log{iteration}.log'
    os.rename(log_location, new_log_path)

    return output_path

def main():

    shutil.rmtree(output_folder, ignore_errors=True)

    run_args = []
    for run in range(num_runs):
        run_folder = output_folder / f'run_{run}'
        os.makedirs(run_folder)

        new_input_path = run_folder / 'iteration0.dsn'
        shutil.copyfile(input_path, new_input_path)

        args = []
        args.append(run)

        run_args.append(args)

    pool_size = int(num_cores/run_threads)
    with mp.Pool(pool_size) as p:
        for iteration in range(num_iterations):
            routing_args = [x + [iteration] for x in run_args]
            print(p.starmap(run_routing, routing_args))

if __name__ == '__main__':
    main()