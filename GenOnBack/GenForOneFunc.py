import copy
import multiprocessing
import os
import random
import sys

import Config, Comp
from ArgModel import ArgModel, gen_builtin_arg
from CondModel import CondModel
from SolverModel import SolverModel


class GenForOneFunc:
    def __init__(self, func, arg_list, count):
        self.func = func
        self.arg_list = arg_list[0:Config.num_explore_top]
        self.count = count
        self.find_cond_list = []
        self.origin_cond_list = []
        self.explored_trace = set()

    def gen_trace(self, turn_number):
        # first turn
        self.func_name, self.modules = self.__get_called_func(self.arg_list[0]['func'])

        cond_model_list = []
        for one_arg in self.arg_list:
            content, arg_list, arg_str_list = self.one_call(one_arg)
            one_cond_model = CondModel(one_arg['func'], arg_list, {}, arg_str_list, content, 0)
            cond_model_list.append(one_cond_model)

        if len(cond_model_list) >= Config.num_explore_top:
            random.shuffle(cond_model_list)
            cond_model_list = cond_model_list[0:Config.num_explore_top]
        self.build_cond(cond_model_list, 0)

        for one_cond in cond_model_list:
            for one_key in one_cond.cond:
                if tuple(one_cond.cond[one_key]) not in self.explored_trace:
                    self.explored_trace.add(tuple(one_cond.cond[one_key]))
                    self.origin_cond_list.append(one_cond)

        # other turns
        for turn in range(1, turn_number + 1):
            mutated_cond = []
            for one_cond in cond_model_list:
                mutated_cond.extend(self.mutate_condition(one_cond, turn))

            if len(mutated_cond) >= Config.num_explore_top:
                random.shuffle(mutated_cond)
                mutated_cond = mutated_cond[0:Config.num_explore_top]
            else:
                if turn <= Config.num_explore_top // 2:
                    random_cond = []
                    for one_cond in cond_model_list:
                        random_cond.extend(self.mutate_random(one_cond, turn))

                    if len(random_cond) >= Config.num_explore_top - len(mutated_cond):
                        random.shuffle(random_cond)
                        mutated_cond.extend(random_cond[0:Config.num_explore_top - len(mutated_cond)])
                    else:
                        mutated_cond.extend(random_cond)

            if len(mutated_cond) <= 0:
                break

            for one_cond in mutated_cond:
                self.build_content(one_cond)

            self.build_cond(mutated_cond, turn)

            for one_cond in mutated_cond:
                for one_key in one_cond.cond:
                    if tuple(one_cond.cond[one_key]) not in self.explored_trace:
                        self.explored_trace.add(tuple(one_cond.cond[one_key]))
                        self.find_cond_list.append(one_cond)

            cond_model_list = copy.copy(mutated_cond)

    def build_cond(self, cond_list, turn):
        split = 0
        start = 0
        line_count = 0
        for i in range(len(cond_list)):
            line_count += len(cond_list[i].content)
            if line_count >= Config.num_line_per_file:
                self.run_and_build_cond(cond_list[start:i], turn, split)
                split += 1
                start = i
                line_count = 0
            if split > Config.num_split_file:
                break
        self.run_and_build_cond(cond_list[start:], turn, split)

    def mutate_condition(self, one_cond, turn):
        new_cond_list = []
        for one_key in one_cond.cond.keys():
            if len(one_cond.cond[one_key]) <= 0:
                continue
            condition = one_cond.cond[one_key]
            for i in range(len(condition)):
                if '0' in condition[i]:
                    condition[i] = condition[i].replace('0', '1')
                else:
                    condition[i] = condition[i].replace('1', '0')

                if tuple(condition[0:i]) not in self.explored_trace:
                    for j in range(Config.num_extend_one_cond):
                        solver = SolverModel(condition[0:i])
                        new_arg = solver.produce_object()
                        new_cond_list.append(self.build_new_cond(one_cond, int(one_key), new_arg, turn))
                    self.explored_trace.add(tuple(condition[0:i]))

                if '0' in condition[i]:
                    condition[i] = condition[i].replace('0', '1')
                else:
                    condition[i] = condition[i].replace('1', '0')
        return new_cond_list

    def mutate_random(self, one_cond, turn):
        new_cond_list = []
        for one_key in one_cond.cond.keys():
            for j in range(Config.num_extend_one_cond_random):
                if len(one_cond.cond[one_key]) <= 0:
                    if int(one_key) < len(one_cond.arg_list):
                        new_arg = gen_builtin_arg(type(one_cond.arg_list[int(one_key)]))
                    else:
                        new_arg = gen_builtin_arg()
                    new_cond_list.append(self.build_new_cond(one_cond, int(one_key), new_arg, turn))
                    if len(new_cond_list) > Config.num_explore_top:
                        return new_cond_list
        return new_cond_list

    def build_content(self, one_cond):
        func_name, modules = self.__get_called_func(one_cond.func)

        content = []
        content.extend(Comp.args(one_cond.arg_list, 'arg_list'))
        arg_str = ''
        count = len(one_cond.arg_list)
        for one_arg_str in one_cond.arg_str_list:
            content.append('    arg_list.append(' + one_arg_str + ')')
            if arg_str == '':
                arg_str += 'arg_list[' + str(count) + ']'
            else:
                arg_str += ', arg_list[' + str(count) + ']'
            count += 1

        content.append('    print(\'pycing address start\')')
        for i in range(len(one_cond.arg_list) + len(one_cond.arg_str_list)):
            content.append('    print(\'address:0x%x\\n\' % id(arg_list[' + str(i) + ']))')
        content.append('    print(\'pycing address end\')')

        content.append('    print(\'pycing native start\')')
        content.extend(Comp.func_call(func_name, arg_str))
        content.append('print(\'pycing native end\')')

        one_cond.content = content

    def build_new_cond(self, one_cond, index, new_arg, turn):
        if index < len(one_cond.arg_list):
            new_arg_list = copy.copy(one_cond.arg_list)
            new_arg_list[index] = new_arg
            new_one_cond = CondModel(one_cond.func, new_arg_list, {},
                                     one_cond.arg_str_list, None, turn)
            return new_one_cond
        else:
            new_arg_str = copy.copy(one_cond.arg_str_list)
            if isinstance(new_arg, str):
                new_arg_str[index - len(one_cond.arg_list) - 1] = '\'' + new_arg + '\''
            else:
                new_arg_str[index - len(one_cond.arg_list) - 1] = str(new_arg)
            new_one_cond = CondModel(one_cond.func, one_cond.arg_list, {}, new_arg_str, None, turn)
            return new_one_cond

    def run_and_build_cond(self, cond_list, turn, split):
        tmp_file_name = Config.path \
                        + 'fun_' + str(self.count) + '_tu_' + str(turn) \
                        + '_sp_' + str(split) + '.py'

        with open(tmp_file_name, 'w') as tmp_file:
            content = []
            content.extend(Comp.import_part(self.modules))
            for one_line in content:
                tmp_file.write(one_line + '\n')
            tmp_file.write('\n')

            for one_cond in cond_list:
                for one_line in one_cond.content:
                    tmp_file.write(one_line + '\n')
                tmp_file.write('\n')

        try:
            result = os.popen('python3.8 ' + tmp_file_name).read().splitlines()
        except:
            os.remove(tmp_file_name)
            del result
            return

        print_addre = False
        print_cond = False
        address = []
        address_map = {}
        count = 0
        for line in result:
            if 'pycing arg failed' in line:
                cond_list[count].cond = {}
                count += 1

            if 'pycing address start' in line:
                print_addre = True
                continue
            elif 'pycing address end' in line:
                print_addre = False

            if print_addre and line.startswith('address:'):
                address.append(line[10:])
                address_map[line[10:]] = []

            if 'pycing native start' in line:
                print_cond = True
                continue
            elif 'pycing native end' in line:
                cond_map = {}
                for i in range(len(address)):
                    cond_map[str(i)] = address_map[address[i]]
                cond_list[count].cond = cond_map
                count += 1
                address = []
                address_map = {}
                print_cond = False

            if print_cond:
                for one_add in address:
                    if one_add in line:
                        address_map[one_add].append(line[7:line.index("&")])
        os.remove(tmp_file_name)
        del result

    def one_call(self, one_call):
        one_model = ArgModel()
        arg_list = []
        arg_str_list = []
        for one_arg in one_call['para']:
            one_model.gen_args(one_arg[0], arg_list)
            arg_str_list.append(one_model.arg_str)

        content = []
        content.extend(Comp.args(arg_list, 'arg_list'))
        arg_str = ''
        count = len(arg_list)
        for one_arg_str in arg_str_list:
            content.append('    arg_list.append(' + one_arg_str + ')')
            if arg_str == '':
                arg_str += 'arg_list[' + str(count) + ']'
            else:
                arg_str += ', arg_list[' + str(count) + ']'
            count += 1

        content.append('    print(\'pycing address start\')')
        for i in range(len(arg_list) + len(arg_str_list)):
            content.append('    print(\'address:0x%x\\n\' % id(arg_list[' + str(i) + ']))')
        content.append('    print(\'pycing address end\')')

        content.append('    print(\'pycing native start\')')
        content.extend(Comp.func_call(self.func_name, arg_str))
        content.append('print(\'pycing native end\')')

        return content, arg_list, arg_str_list

    def __get_called_func(self, called_func):
        modules = None
        call_func = None

        if hasattr(called_func, '__module__') and called_func.__module__ != None:
            call_func = called_func.__module__ + '.' + called_func.__name__
            modules = called_func.__module__

        return call_func, modules
