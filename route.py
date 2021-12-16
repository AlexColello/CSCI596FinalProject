from subprocess import Popen
import shlex
import os, shutil, re
import multiprocessing as mp
from pathlib import Path


PARENT_DIR = Path(__file__).absolute().parent

via_regex = re.compile(r" with .* vias and .*\n")
trace_length_regex = re.compile(r"vias and .* trace length")
incomplete_regex = re.compile(r"incomplete: \d.*\n")

num_iterations = 3
num_cores = mp.cpu_count()
num_runs = 2

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

class Results:
    iteration = -1
    run = -1

    vias = -1
    trace_length = -1
    incomplete = -1

def parse_results(iteration, run_num):
    log_path = get_log_path(iteration, run_num)

    vias = -1
    trace_length = -1
    incomplete = -1

    with open(log_path, 'r') as f:
        for line in f.readlines():
            via_result = via_regex.search(line)
            trace_length_result = trace_length_regex.search(line)
            incomplete_result = incomplete_regex.search(line)

            if via_result:
                vias = int(via_result[0].split()[1].replace(',',''))
            if trace_length_result:
                trace_length = float(trace_length_result[0].split()[2].replace(',',''))
            if incomplete_result:
                incomplete = int(incomplete_result[0].split()[1].replace(',',''))

    results = Results()
    results.iteration = iteration
    results.run = run_num
    results.vias = vias
    results.trace_length = trace_length
    results.incomplete = incomplete

    print(f"iteration: {iteration}, run: {run_num}, vias: {vias}, trace length: {trace_length}, incomplete: {incomplete} ")

    return results

def init_iteration(num, input_dsn_path):
    iteration_folder = get_iteration_directory(num)
    os.makedirs(iteration_folder)
    shutil.copyfile(input_dsn_path, iteration_folder / 'initial.dsn')

    return iteration_folder

def calc_cost(result):
    return result.vias + result.trace_length * 0.000001 + result.incomplete * 100

def select_best_dsn(iteration):
    results = []
    for run in range(num_runs):
        results.append(parse_results(iteration, run))

    best = min(results, key=calc_cost)
    print(f'Selected iteration {best.iteration} run {best.run}')

    return get_run_directory(best.iteration, best.run) / 'output.dsn'

def run_routing(iteration, run_num):
    print(f'Starting run {run_num} iteration {iteration}')
    iteration_folder = get_iteration_directory(iteration)
    run_folder = get_run_directory(iteration, run_num)
    os.mkdir(run_folder)
    input_path = run_folder / 'input.dsn'
    shutil.copyfile(iteration_folder / 'initial.dsn', input_path)
    
    output_path = run_folder / 'output.dsn'
    args = ['-de', input_path, '-do', output_path, '-mp', '1', '-mt', '1', '-is', 'random', '-test']

    process = Popen(command_path + args, cwd=run_folder)
    process.wait()
    
    print(f'Finished iteration {iteration} run {run_num}')

    return output_path

def main():

    shutil.rmtree(output_folder, ignore_errors=True)

    #pool_size = num_cores
    pool_size = 2
    previous_best_path = input_path
    with mp.Pool(pool_size) as p:
        for iteration in range(num_iterations):
            init_iteration(iteration, previous_best_path)
            routing_args = [(iteration, x) for x in range(num_runs)]
            p.starmap(run_routing, routing_args)

            previous_best_path = select_best_dsn(iteration)

if __name__ == '__main__':
    main()