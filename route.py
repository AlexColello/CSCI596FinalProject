from subprocess import Popen
import shlex
import os, shutil
import multiprocessing as mp
from pathlib import Path


PARENT_DIR = Path(__file__).absolute().parent

num_iterations = 5
num_cores = mp.cpu_count()
# num_runs = num_cores
num_runs = 2
run_threads = int(num_cores/num_runs)

print(num_cores, num_runs, run_threads)

input_path = PARENT_DIR / 'test_data' / 'StickHub.dsn'
output_folder = PARENT_DIR / 'output'
jar_path = PARENT_DIR / 'freerouting-executable.jar'
command_path = ['java', '-jar', str(jar_path)]

def get_iteration_directory(iteration_num):
    return output_folder / f'iter_{iteration_num}'

def get_run_directory(iteration_num, run_num):
    return get_iteration_directory(iteration_num) / f'run_{run_num}'

def get_log_path(iteration, run_num):
    return get_run_directory(iteration, run_num) / 'logs' / f'freerouter.log'

def parse_results(iteration, run_num):
    log_path = get_log_path(iteration, run_num)

    with open(log_path, 'r') as f:
        for line in f.readlines():
            pass

def init_iteration(num, input_dsn_path):
    iteration_folder = get_iteration_directory(num)
    os.makedirs(iteration_folder)
    shutil.copyfile(input_dsn_path, iteration_folder / 'initial.dsn')

    return iteration_folder

def select_best_dsn(iteration_directory):
    return iteration_directory / 'run_0' / 'output.dsn'

def run_routing(iteration, run_num):
    print(f'Starting run {run_num} iteration {iteration}')
    iteration_folder = get_iteration_directory(iteration)
    run_folder = get_run_directory(iteration, run_num)
    os.mkdir(run_folder)
    input_path = run_folder / 'input.dsn'
    shutil.copyfile(iteration_folder / 'initial.dsn', input_path)
    
    output_path = run_folder / 'output.dsn'
    args = ['-de', input_path, '-do', output_path, '-mp', '1', '-mt', '1', '-test']

    process = Popen(command_path + args, cwd=run_folder)
    process.wait()
    
    print(f'Finished iteration {iteration} run {run_num}')

    # original_log_location = run_folder / 'logs' / 'freerouter.log'
    # log_path = get_log_path(run_num, iteration)
    # os.rename(original_log_location, log_path)

    return output_path

def main():

    shutil.rmtree(output_folder, ignore_errors=True)

    #pool_size = int(num_cores/run_threads)
    pool_size = 2
    previous_best_path = input_path
    with mp.Pool(pool_size) as p:
        for iteration in range(num_iterations):
            iteration_directory = init_iteration(iteration, previous_best_path)
            routing_args = [(iteration, x) for x in range(num_runs)]
            print(p.starmap(run_routing, routing_args))

            previous_best_path = select_best_dsn(iteration_directory)

if __name__ == '__main__':
    main()