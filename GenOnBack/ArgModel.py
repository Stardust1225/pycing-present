import copy
import random
import numpy
import Config


class ArgModel:
    def __init__(self):
        pass

    def gen_args(self, arg_val, arg_list=[], arg_str=''):
        self.arg_list = arg_list
        self.arg_str = arg_str
        self.modules = []

        arg_type = type(arg_val).__name__

        if arg_type == 'int64':
            arg_type = 'int'

        if arg_type == 'int' or arg_type == 'str' or arg_type == 'bool' or arg_type == 'complex' \
                or arg_type == 'NoneType' or arg_type == 'float' or arg_type == 'bytes':
            self.__basic_types(arg_val, arg_type)

        elif arg_type == 'dict':
            self.__dict(arg_val)

        elif arg_type == 'list' \
                or arg_type == 'tuple':
            self.__list_tuple(arg_val, arg_type)

        elif arg_type == 'ndarray':
            if len(numpy.shape(arg_val)) == 0:
                self.__basic_types(arg_val, 'int')
            else:
                self.__narray(arg_val)

        else:
            self.__basic_types(arg_val, 'int')

    def __list_tuple(self, arg_val, arg_type):
        if arg_type == 'list':
            if self.arg_str == '' \
                    or self.arg_str[-1] == '[' \
                    or self.arg_str[-1] == '(' \
                    or self.arg_str[-1] == '{':
                self.arg_str += '['
            else:
                self.arg_str += ', ['
        else:
            if self.arg_str == '' \
                    or self.arg_str[-1] == '[' \
                    or self.arg_str[-1] == '(' \
                    or self.arg_str[-1] == '{':
                self.arg_str += '('
            else:
                self.arg_str += ', ('

            if len(self.arg_list) > 0:
                formal_type = type(self.arg_list[-1]).__name__

        for sub_one_arg in arg_val:
            self.gen_args(sub_one_arg, self.arg_list, self.arg_str)

        if arg_type == 'list':
            self.arg_str += ']'
        else:
            self.arg_str += ')'

    def __narray(self, arg_val):
        self.modules.append('numpy')
        if self.arg_str == '' or self.arg_str[-1] == '[' \
                or self.arg_str[-1] == '(' or self.arg_str[-1] == '{':
            self.arg_str += 'numpy.array(['
        else:
            self.arg_str += ', numpy.array(['

        num_type = 'int'
        size = numpy.shape(arg_val)
        if len(size) == 1:
            line = 1
            column = size[0]
        else:
            line = size[0]
            column = size[1]

        if line > Config.object_length:
            line = Config.object_length
        if column > Config.object_length:
            column = Config.object_length

        length = line * column
        for j in range(length):
            self.arg_list.append(self.__builtin_object(num_type))
            if self.arg_str == '' or self.arg_str[-1] == '[' \
                    or self.arg_str[-1] == '(' or self.arg_str[-1] == '{':
                self.arg_str += 'arg_list[' + str(len(self.arg_list) - 1) + ']'
            else:
                self.arg_str += ', arg_list[' + str(len(self.arg_list) - 1) + ']'
        self.arg_str += ']'
        self.arg_str += ').reshape([' + str(line) + ', ' + str(column) + '])'

    def __dict(self, arg_val):
        if self.arg_str == '' \
                or self.arg_str[-1] == '[' \
                or self.arg_str[-1] == '(' \
                or self.arg_str[-1] == '{':
            self.arg_str += '{'
        else:
            self.arg_str += ',{'

        for sub_one_arg in arg_val.keys():
            self.arg_list.append(sub_one_arg)
            if self.arg_str == '' \
                    or self.arg_str[-1] == '[' \
                    or self.arg_str[-1] == '(' \
                    or self.arg_str[-1] == '{':
                self.arg_str += 'arg_list[' + str(len(self.arg_list) - 1) + '] : '
            else:
                self.arg_str += ', arg_list[' + str(len(self.arg_list) - 1) + '] : '
            self.arg_list.append(self.__builtin_object('int'))
            self.arg_str += 'arg_list[' + str(len(self.arg_list) - 1) + ']'

        self.arg_str += '}'

    def __basic_types(self, arg_val, arg_type):
        self.arg_list.append(self.__builtin_object(arg_type))
        if self.arg_str == '' \
                or self.arg_str[-1] == '[' \
                or self.arg_str[-1] == '(' \
                or self.arg_str[-1] == '{':
            self.arg_str += 'arg_list[' + str(len(self.arg_list) - 1) + ']'
        else:
            self.arg_str += ', arg_list[' + str(len(self.arg_list) - 1) + ']'

    def __builtin_object(self, types):
        if types == 'str':
            str_list = random.sample(Config.str_seed, random.randint(1, Config.str_length))
            ran_str = ''
            for one_char in str_list:
                ran_str += one_char
            return ran_str

        elif types == 'float':
            return random.uniform(Config.num_low, Config.num_top)

        elif types == 'bool':
            return random.choice([True, False])

        elif types == 'complex':
            return complex(random.randint(Config.num_low, Config.num_top),
                           random.randint(Config.num_low, Config.num_top))

        elif types == 'int':
            return random.randint(Config.num_low, Config.num_top)

        elif types == 'bytes':
            ins_list = []
            length = random.randint(0, Config.object_length)
            for i in range(length):
                ins_list.append(random.randint(0, 255))
            return bytes(ins_list)

        elif types == 'NoneType':
            return None

        else:
            return '1'


def gen_builtin_arg(deltype=None):
    choice_type = Config.built_in_types
    if deltype != None and deltype in choice_type:
        choice_type.remove(deltype)
    elif isinstance(deltype, list):
        for one_type in deltype:
            if one_type in choice_type:
                choice_type.remove(one_type)

    types = random.choice(choice_type)
    if types == 'str':
        str_list = random.sample(Config.str_seed, random.randint(1, Config.str_length))
        ran_str = ''
        for one_char in str_list:
            ran_str += one_char
        return ran_str

    elif types == 'float':
        return random.uniform(Config.num_low, Config.num_top)

    elif types == 'bool':
        return random.choice([True, False])

    elif types == 'complex':
        return complex(random.randint(Config.num_low, Config.num_top),
                       random.randint(Config.num_low, Config.num_top))

    elif types == 'int':
        return random.randint(Config.num_low, Config.num_top)

    elif types == 'bytes':
        ins_list = []
        length = random.randint(0, Config.object_length)
        for i in range(length):
            ins_list.append(random.randint(0, 255))
        return bytes(ins_list)

    elif types == 'NoneType':
        return None

    elif types == 'list':
        return [gen_builtin_arg(['list', 'set', 'dict', 'tuple']) for i in range(Config.object_length)]

    elif types == 'set':
        ret_obj = set()
        for i in range(Config.object_length):
            ret_obj.add(gen_builtin_arg(['list', 'set', 'dict', 'tuple']))
        return ret_obj

    elif types == 'tuple':
        return tuple(gen_builtin_arg(['list', 'set', 'dict', 'tuple']) for i in range(Config.object_length))

    elif types == 'dict':
        value = dict()
        for i in range(Config.object_length):
            str_list = random.sample(Config.str_seed, random.randint(1, Config.str_length))
            ran_str = ''
            for one_char in str_list:
                ran_str += one_char
            value[ran_str] = gen_builtin_arg(['list', 'set', 'dict', 'tuple'])
        return value

    else:
        return '1'
