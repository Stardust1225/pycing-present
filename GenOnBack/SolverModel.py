import random

import Config


class SolverModel:
    def __init__(self, constraints):
        self.constraints = constraints

    def gen_one_type(self, gen_type):
        if gen_type == 'list' or gen_type == 'tuple' or gen_type == 'set':
            length = random.randint(1, Config.object_length)
            result = []
            for i in range(length):
                result.append(self.random_gen(['list', 'tuple', 'dict', 'set']))
            if gen_type == 'list':
                return result
            elif gen_type == 'tuple':
                return tuple(result)
            return set(result)

        elif gen_type == 'int' or gen_type == 'long':
            return random.randint(Config.num_low, Config.num_top)

        elif gen_type == 'str':
            str_list = random.sample(Config.str_seed, random.randint(1, Config.str_length))
            ran_str = ''
            for one_char in str_list:
                ran_str += one_char
            return ran_str

        elif gen_type == 'float':
            return random.uniform(Config.num_low, Config.num_top)

        elif gen_type == 'bool':
            return random.choice([True, False])

        elif gen_type == 'complex':
            return complex(random.randint(Config.num_low, Config.num_top),
                           random.randint(Config.num_low, Config.num_top))

        elif gen_type == 'bytes':
            str_list = random.sample(Config.str_seed, random.randint(1, Config.str_length))
            ran_str = ''
            for one_char in str_list:
                ran_str += one_char
            return bytes(ran_str, 'utf-8')

        elif gen_type == 'dict':
            length = random.randint(1, Config.object_length)
            result = dict()
            for i in range(length):
                result[self.gen_one_type('str')] = self.random_gen(['list', 'dict', 'set'])
            return result

    def random_gen(self, not_type=None):
        candidate_types = ['list', 'tuple', 'int', 'complex', 'dict', 'float', 'long', 'bool', 'set', 'bytes', 'str']
        if not_type != None and not isinstance(not_type, list):
            if not_type in candidate_types:
                candidate_types.remove(not_type)
            if not_type == 'long':
                if 'int' in candidate_types:
                    candidate_types.remove('int')
            elif not_type == 'int':
                if 'long' in candidate_types:
                    candidate_types.remove('long')

        if isinstance(not_type, list):
            for one_type in not_type:
                if one_type in candidate_types:
                    candidate_types.remove(one_type)

        gen_type = random.choice(candidate_types)
        return self.gen_one_type(gen_type)

    def produce_object(self):
        ret_obj = None
        type_list = []
        for one_item in self.constraints:
            type_list.append(one_item[0:one_item.index(':')])
            if 'mapping_getitemstring:' in one_item:
                key = one_item[one_item.index(':') + 1:]
                if ret_obj == None:
                    ret_obj = {key: self.random_gen()}
                elif isinstance(ret_obj, dict):
                    if key in ret_obj:
                        del ret_obj[key]
                    else:
                        ret_obj[key] = self.random_gen()
                else:
                    new_obj = {key: ret_obj}
                    ret_obj = new_obj

            elif 'list_getitem:' in one_item \
                    or 'sequence_getitem:' in one_item:
                index = int(one_item[one_item.index(':') + 1:])
                if ret_obj == None:
                    ret_obj = [self.random_gen() for i in range(index + 1)]
                elif isinstance(ret_obj, list):
                    if len(ret_obj) < index:
                        ret_obj.extend([self.random_gen() for i in range(index - len(ret_obj) + 1)])
                else:
                    new_obj = [x for x in range(index + 1)]
                    new_obj[index] = ret_obj
                    ret_obj = new_obj

            elif 'tuple_getitem:' in one_item:
                index = int(one_item[one_item.index(':') + 1:])
                if ret_obj == None:
                    ret_obj = tuple(self.random_gen() for i in range(index + 1))
                elif isinstance(ret_obj, tuple):
                    if len(ret_obj) < index:
                        ret_obj += tuple(self.random_gen() for i in range(index - len(ret_obj) + 1))
                else:
                    new_obj = tuple(x for x in range(index))
                    new_obj += (ret_obj)
                    ret_obj = new_obj

            elif 'tuple' in one_item and '1' in one_item:
                if ret_obj == None:
                    ret_obj = self.gen_one_type('tuple')
                if isinstance(ret_obj, tuple):
                    continue
                elif not isinstance(ret_obj, tuple):
                    break

            elif ('list' in one_item or 'slice' in one_item or 'mapping' in one_item) and '1' in one_item:
                if ret_obj == None:
                    ret_obj = self.gen_one_type('list')
                if isinstance(ret_obj, list):
                    continue
                elif not isinstance(ret_obj, list):
                    break

            elif 'float' in one_item and '1' in one_item:
                if ret_obj == None:
                    ret_obj = self.gen_one_type('float')
                if isinstance(ret_obj, float):
                    continue
                elif not isinstance(ret_obj, float):
                    break

            elif 'dict' in one_item and '1' in one_item:
                if ret_obj == None:
                    ret_obj = self.gen_one_type('dict')
                if isinstance(ret_obj, dict):
                    continue
                elif not isinstance(ret_obj, dict):
                    break

            elif 'complex' in one_item and '1' in one_item:
                if ret_obj == None:
                    ret_obj = self.gen_one_type('complex')
                if isinstance(ret_obj, complex):
                    continue
                elif not isinstance(ret_obj, complex):
                    break

            elif 'long' in one_item and '1' in one_item:
                if ret_obj == None:
                    ret_obj = self.gen_one_type('long')
                if isinstance(ret_obj, int):
                    continue
                elif not isinstance(ret_obj, int):
                    break

            elif 'bool' in one_item and '1' in one_item:
                if ret_obj == None:
                    ret_obj = self.gen_one_type('bool')
                if isinstance(ret_obj, bool):
                    continue
                elif not isinstance(ret_obj, bool):
                    break

            elif 'set' in one_item and '1' in one_item:
                if ret_obj == None:
                    ret_obj = self.gen_one_type('set')
                if isinstance(ret_obj, set):
                    continue
                elif not isinstance(ret_obj, set):
                    break

        if ret_obj == None:
            ret_obj = self.random_gen(type_list)

        return ret_obj


if __name__ == '__main__':
    cons = ['dict:0', 'tuple_getitem:3']
    solver = SolverModel(cons)