import os


class Testcase_Extraction:

    # 编译单个文件，并根据编译生成的code_object进行分析。
    # 文件内的一个函数对应了一个code_object。
    # 一个类也对应一个code_object，且类中的每个函数都为一个code_object，记录在类的code_object的属性co_consts中。
    def one_file(self, root, file, path):
        executor_code = []
        module_name = file.replace('.py', '')
        with open(os.path.join(root, file), "r") as source_file:
            try:
                code_object = compile(source_file.read(), file, "exec")
            except:
                return []

            for sub_object in code_object.co_consts:
                if isinstance(sub_object, type(code_object)) \
                        and sub_object.co_argcount == 0:
                    sub_function = self.get_sub_function(sub_object)

                    # 如果当前的code_object不含有子code_object，说明这是一个独立的函数，可以直接import然后调用。
                    if len(sub_function) == 0:
                        exec_content = ''
                        # exec_content = 'import sys\n'
                        # exec_content += 'sys.path.append(\'/home/xin/Documents/PIL_data\')\n'
                        exec_content += \
                            'from ' + root.replace(path, '').replace('/', '.') \
                            + '.' + module_name + ' import ' + sub_object.co_name + '\n'
                        exec_content += '\n'
                        exec_content += sub_object.co_name + '()'
                        executor_code.append(exec_content)

                    # 当前的code_object是一个类，需要先构造这个类，再调用其中test_开头，且不含其他参数的函数。
                    else:
                        for one_func in sub_function:
                            if 'test_' in one_func.co_name and one_func.co_argcount == 1:
                                exec_content = ''
                                # exec_content = 'import sys\n'
                                # exec_content += 'sys.path.append(\'/home/xin/Documents/PIL_data\')\n'
                                exec_content += \
                                    'from ' + root.replace(path, '').replace('/', '.') \
                                    + '.' + module_name + ' import ' + sub_object.co_name + '\n'
                                exec_content += 'instance_object = ' + sub_object.co_name + '()\n'
                                exec_content += 'instance_object.' + one_func.co_name + '()'
                                executor_code.append(exec_content)

        return executor_code

    def get_sub_function(self, code_object):
        sub_function = []
        for sub_object in code_object.co_consts:
            if isinstance(sub_object, type(code_object)):
                sub_function.append(sub_object)

        return sub_function