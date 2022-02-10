import multiprocessing
import os
import pickle
import sys

from SelfTracer import TracerRecorder
from SimExec import SimExec


def run_one_code(tracer, compile_code):
    try:
        sys.settrace(tracer.self_tracer)
        exec(compile_code)
    except:
        pass
    sys.settrace(None)

def one_file(file_path, number, project):
    results = []
    if not os.path.exists(file_path):
        return

    if os.path.exists(directory + 'test_case_dump/' + str(number) + '_func_dump'):
        return

    sim_exec = SimExec(project)

    tracer = TracerRecorder(file_path, 3, sim_exec, project)
    with open(file_path, 'r') as input_file:
        compile_code = compile(input_file.read(), file_path, 'exec')
        run_one_code(tracer, compile_code)

    for one_call in sim_exec.local_function_call:
        try:
            called_func = one_call['func']

            if isinstance(called_func, str):
                continue

            if hasattr(called_func, '__module__') \
                    and called_func.__module__ != None \
                    and 'builtin' in str(type(called_func)) \
                    and project in called_func.__module__ \
                    and len(one_call['para']) > 0:
                pickle.dumps(one_call)
                results.append(one_call)

            if len(one_call['para']) > 0:
                pickle.dumps(one_call)
                results.append(one_call)
        except:
            pass

    with open(directory + 'test_case_dump/' + str(number) + '_func_dump', 'wb') as dump_file:
        pickle.dump(results, dump_file)

    results.clear()
    del results
    del sim_exec
    del tracer


if __name__ == '__main__':
    directory = '/home/xin/Documents/scipy_data/'

    path = directory + 'single_test_case/'

    # if not os.path.exists(directory + 'test_case_dump'):
    #     os.mkdir(directory + 'test_case_dump')
    #
    # sys.path.append(path)
    #
    # pool = multiprocessing.Pool(8)
    # process_result = []
    # for i in range(6900, 20000):
    #     file_path = path + str(i) + '.py'
    #     process_result.append(pool.apply_async(one_file, [file_path, i, 'scipy']))
    #
    # pool.close()
    #
    # for i in range(len(process_result)):
    #     try:
    #         process_result[i].get(60)
    #     except:
    #         with open(directory + 'test_case_dump/' + str(i) + '_func_dump', 'wb') as dump_file:
    #             pickle.dump([], dump_file)
    #
    # pool.terminate()

    func_map = dict()
    count = 0
    for i in range(0, 9000):
        file_path = directory + '/test_case_dump/' + str(i) + '_func_dump'
        if not os.path.exists(file_path):
            continue

        with open(file_path, 'rb') as dump_file:
            try:
                one_result = pickle.load(dump_file)
                for one_call in one_result:
                    called_func = one_call['func']

                    key = str(called_func)
                    if key in func_map:
                        func_map[key].append(one_call)
                    else:
                        func_map[key] = [one_call]
            except Exception as e:
                print(e)

    count = 0
    out_path = directory + '/local_func/'
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    for one_func in func_map.keys():
        file_path = out_path + str(count)
        with open(file_path, 'wb') as out_dump_file:
            pickle.dump({one_func: func_map[one_func]}, out_dump_file)

        count += 1