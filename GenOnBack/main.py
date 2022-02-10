import multiprocessing
import os
import pickle

import Config
from GenForOneFunc import GenForOneFunc


def one_func_explore(count, path):
    with open(path + str(count), 'rb') as dump_file:
        try:
            origin_dump = pickle.load(dump_file)
        except:
            return

    for func in origin_dump.keys():
        one_func_model = GenForOneFunc(func, origin_dump[func], count)

        one_func_model.gen_trace(Config.num_loop)

        with open(out_path + 'dump_' + str(count) + '_explored', 'wb') as dump_file:
            pickle.dump({'func': func, 'trace': one_func_model.find_cond_list}, dump_file)

        with open(out_path + 'dump_' + str(count) + '_origin', 'wb') as dump_file:
            pickle.dump({'func': func, 'trace': one_func_model.origin_cond_list}, dump_file)

        print('func: ' + str(count)
              + '  ori: ' + str(len(one_func_model.origin_cond_list))
              + '  exp: ' + str(len(one_func_model.find_cond_list)))

        del one_func_model

    del origin_dump


if __name__ == '__main__':

    path = '/home/xin/Documents/numpy_data/'

    out_path = path + 'func_explore_dump/'
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    pool = multiprocessing.Pool(8)

    func_result = []

    for i in range(0, 2000):
        if not os.path.exists(path + 'local_func/' + str(i)):
            continue
        if os.path.exists(out_path + 'dump_' + str(i) + '_origin'):
            continue

        func_result.append(pool.apply_async(one_func_explore, [i, path + 'local_func/']))

    pool.close()

    for one_result in func_result:
        one_result.get()

    pool.terminate()
