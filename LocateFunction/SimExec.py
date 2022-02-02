import dis
import sys
import _ctypes

import BytecodeHandler


class SimExec():
    def __init__(self, project):
        self.local_function_call = []
        self.__stack = []
        self.__call_stack = []

        self.project = project

    def one_frame(self, frame, l_frame):
        try:
            self.__one_frame(frame, l_frame)
        except:
            pass

    def __one_frame(self, frame, l_frame):
        used_frame = l_frame
        if l_frame.event == 'return' and frame.f_code != l_frame.f_code:
            used_frame = frame
        self.next_frame = frame

        dis_list = self.__get_dis_list(used_frame)
        if len(dis_list) <= 0:
            return
        has_call = False
        for one_dis in dis_list:
            if 'CALL_' in one_dis.opname:
                has_call = True
                break
        if not has_call:
            return

        esp = l_frame.f_lasti // 2

        if l_frame.f_lasti == -1: esp = 0

        if l_frame.event == 'return' \
                and len(self.__stack) > 0 \
                and len(self.__call_stack) > 0 \
                and frame.f_code != l_frame.f_code:
            re_value = self.__stack.pop()
            self.__stack, esp = self.__call_stack.pop()
            self.__stack.append(re_value)
            esp += 1

        in_loop = False

        while (esp < len(dis_list)):
            instr = dis_list[esp]

            if hasattr(BytecodeHandler, instr.opname + '_handler'):
                handle_func = getattr(BytecodeHandler, instr.opname + '_handler')
                handle_func(self.__stack, instr, used_frame)

            elif 'RAISE_VARARGS' in instr.opname:
                break

            elif 'RETURN_VALUE' in instr.opname:
                break

            elif 'JUMP_IF_TRUE_OR_POP' in instr.opname \
                    or 'POP_JUMP_IF_FALSE' in instr.opname:
                value = self.__stack.pop()
                in_loop = True
                if instr.argval == frame.f_lasti or not value:
                    esp = instr.argval // 2 - 1

            elif 'POP_JUMP_IF_TRUE' in instr.opname:
                value = self.__get_corres_value(used_frame, self.__stack.pop())
                in_loop = True
                if value:
                    esp = instr.argval // 2 - 1

            elif 'FOR_ITER' in instr.opname:
                if frame.f_lasti >= instr.argval:
                    esp = instr.argval // 2 - 1
                elif in_loop:
                    break

            else:
                need_to_break = self.__one_instr(instr, used_frame, esp)

                if need_to_break == 'break':
                    break

                elif need_to_break == 'continue' and not in_loop:
                    in_loop = True

                elif need_to_break == 'jump':
                    esp = instr.argval // 2 - 1
                    in_loop = True

            esp += 1

            if frame.f_lasti != -1 and esp * 2 == frame.f_lasti: break

    def __one_instr(self, instr, frame, esp):
        if 'BINARY' in instr.opname:
            second_operator = self.__stack.pop()
            first_operator = self.__stack.pop()
            self.__stack.append(str(first_operator) + '&' + instr.opname + '&' + str(second_operator))

        # 对于跳转函数，如果需要跳转，则直接赋值j，并退出分析
        elif 'JUMP_ABSOLUTE' in instr.opname \
                or 'JUMP_FORWARD' in instr.opname:
            return 'jump'

        elif 'CALL_' in instr.opname:
            result = self.__deal_with_call(esp, frame, instr)
            if result == 'break' or result == 'continue': return result

        return 'go on'

    def __deal_with_call(self, esp, frame, instr):
        called_func, argu_type = self.__get_arg_and_func(self.__stack, frame, instr)

        called_func = self.__get_corres_value(frame, called_func)
        func_type = type(called_func)
        next_code = self.next_frame.f_code.co_name

        if isinstance(called_func, str):
            if called_func == next_code:
                self.__enter_call(called_func, argu_type, esp)
                return 'break'
            else:
                self.__no_enter_call(called_func, argu_type, frame)
                return 'continue'

        if hasattr(called_func, '__name__'):
            if called_func.__name__ == next_code:
                self.__enter_call(called_func, argu_type, esp)
                return 'break'
            else:
                self.__no_enter_call(called_func, argu_type, frame)
                return 'continue'

        if hasattr(called_func, '__qualname__'):
            if called_func.__qualname__ == next_code:
                self.__enter_call(called_func, argu_type, esp)
                return 'break'
            else:
                self.__no_enter_call(called_func, argu_type, frame)
                return 'continue'

        if hasattr(called_func, 'co_name'):
            if called_func.co_name == next_code:
                self.__enter_call(called_func, argu_type, esp)
                return 'break'
            else:
                self.__no_enter_call(called_func, argu_type, frame)
                return 'continue'

        else:
            if frame.f_code != self.next_frame.f_code:
                self.__call_stack.append([self.__stack, esp])
                self.__stack = []
                return 'break'
            else:
                return 'continue'

    def __no_enter_call(self, called_func, argu_type, frame):
        self.__local_call(called_func, argu_type, frame)

        key = called_func
        if hasattr(called_func, '__qualname__'):
            key = called_func.__qualname__
        if hasattr(called_func, '__name__') and called_func.__name__ != None:
            key = called_func.__name__
        if hasattr(called_func, '__module__') and called_func.__module__ != None:
            key = called_func.__module__ + '.' + key

        self.__stack.append(key)

    def __enter_call(self, called_func, argu_type, esp):
        self.__call_stack.append([self.__stack, esp])
        self.__stack = []

    def __local_call(self, called_func, argu_type, frame):
        one_call = dict()

        if hasattr(called_func, '__closure__'):
            return

        if hasattr(called_func, '__qualname__') \
                and '<locals>' in called_func.__qualname__:
            return

        for one_arg in argu_type:
            if hasattr(one_arg[0], '__array_function__') \
                    and '<locals>' in one_arg[0].__array_wrap__.__qualname__:
                return

            if one_arg[1].__name__ == 'module' \
                    or one_arg[1].__name__ == 'function' \
                    or one_arg[1].__name__ == 'method' \
                    or one_arg[1].__name__ == 'code' \
                    or '<locals>' in str(one_arg[1]):
                return

        call_str = str(called_func)
        if 'numpy.ufunc object at 0x' in call_str:
            key = call_str[call_str.index('0x'):len(call_str) - 1]
            one_call['par_obj'] = _ctypes.PyObj_FromPtr(int(key, 16))

        one_call['func'] = called_func
        one_call['para'] = argu_type
        self.local_function_call.append(one_call)

    def __get_arg_and_func(self, stack, frame, call_instr):
        argument_number = call_instr.arg
        argument_type = []

        if call_instr.opname == 'CALL_FUNCTION_KW': stack.pop()

        for i in range(argument_number):
            item = stack.pop()
            argument_type.insert(0, self.__get_argument_type(item, frame))

        if call_instr.opname == 'CALL_FUNCTION_EX': stack.pop()

        function = stack.pop()

        return (function, argument_type)

    def __get_argument_type(self, argument, frame):
        argu_type = None
        if isinstance(argument, str):
            if argument in frame.f_locals:
                argu_type = [frame.f_locals[argument], type(frame.f_locals[argument])]

            elif argument in frame.f_globals:
                argu_type = [frame.f_globals[argument], type(frame.f_globals[argument])]

            else:
                argu_type = [argument, type(argument)]

        else:
            argu_type = [argument, type(argument)]

        return argu_type

    def __get_dis_list(self, frame):
        dis_list = []
        for instr in dis.get_instructions(frame.f_code):
            if instr.starts_line != None \
                    and instr.starts_line > frame.f_lineno:
                break

            dis_list.append(instr)
            if instr.opname == 'LOAD_BUILD_CLASS':
                return []
        return dis_list

    def __get_corres_value(self, frame, key):
        try:
            if key in frame.f_locals:
                return frame.f_locals[key]
            elif key in frame.f_globals:
                return frame.f_globals[key]
        except:
            pass

        return key
