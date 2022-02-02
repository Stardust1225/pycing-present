def LOAD_CONST_handler(stack, instr, frame):
    LOAD_handler(stack, instr, frame)


def LOAD_NAME_handler(stack, instr, frame):
    LOAD_handler(stack, instr, frame)


def LOAD_ATTR_handler(stack, instr, frame):
    ins_object = get_corres_value(frame, stack.pop())
    if hasattr(ins_object, instr.argval):
        stack.append(getattr(ins_object, instr.argval))
    else:
        stack.append(ins_object + '.' + instr.argval)


def LOAD_handler(stack, instr, frame):
    stack.append(instr.argval)


def LOAD_GLOBAL_handler(stack, instr, frame):
    LOAD_handler(stack, instr, frame)


def LOAD_FAST_handler(stack, instr, frame):
    LOAD_handler(stack, instr, frame)


def LOAD_DEREF_handler(stack, instr, frame):
    LOAD_handler(stack, instr, frame)


def LOAD_METHOD_handler(stack, instr, frame):
    module = get_corres_value(frame, stack.pop())

    if hasattr(module, instr.argval):
        stack.append(getattr(module, instr.argval))
        return
    stack.append(instr.argval)


def LOAD_CLOSURE_handler(stack, instr, frame):
    stack.append(instr.argval)


def BUILD_LIST_handler(stack, instr, frame):
    ins_list = []
    for i in range(instr.arg):
        ins_list.insert(0, stack.pop())
    stack.append(ins_list)


def BUILD_TUPLE_handler(stack, instr, frame):
    ins_tuple = []
    for i in range(instr.arg):
        ins_tuple.insert(0, stack.pop())
    stack.append(tuple(ins_tuple))


def BUILD_CONST_KEY_MAP_handler(stack, instr, frame):
    keys = stack.pop()
    ins_dict = dict()
    for i in range(len(keys) - 1, -1, -1):
        ins_dict[keys[i]] = stack.pop()
    stack.append(ins_dict)


def BUILD_SET_handler(stack, instr, frame):
    ins_list = []
    for i in range(instr.arg):
        ins_list.insert(0, stack.pop())
    stack.append(set(ins_list))


def BUILD_STRING_handler(stack, instr, frame):
    result = ''
    for i in range(instr.arg):
        result.join(stack.pop())
    stack.append(result)


def BINARY_ADD_handler(stack, instr, frame):
    first_operator = stack.pop()
    second_operator = stack.pop()

    type1 = type(first_operator)
    type2 = type(second_operator)

    if type1 == int and type2 == str:
        stack.append(first_operator + frame.f_locals[second_operator])
    elif type1 == str and type2 == int:
        stack.append(second_operator + frame.f_locals[first_operator])
    else:
        result = None
        try:
            result = first_operator + second_operator
        except:
            stack.append(str(first_operator) + '+' + str(second_operator))
        else:
            stack.append(result)


def BINARY_MULTIPLY_handler(stack, instr, frame):
    second_operator = get_corres_value(frame=frame, key=stack.pop())
    first_operator = get_corres_value(frame=frame, key=stack.pop())
    try:
        stack.append(first_operator * second_operator)
    except:
        stack.append(str(first_operator) + '&*&' + str(second_operator))


def BINARY_POWER_handler(stack, instr, frame):
    second_operator = get_corres_value(frame=frame, key=stack.pop())
    first_operator = get_corres_value(frame=frame, key=stack.pop())
    stack.append(first_operator ** second_operator)


def BINARY_MATRIXMULTIPLY_handler(stack, instr, frame):
    first_operator = stack.pop()
    second_operator = stack.pop()
    stack.append(str(first_operator) + '@' + str(second_operator))


def BINARY_FLOOR_DIVIDE_handler(stack, instr, frame):
    second_operator = get_corres_value(frame=frame, key=stack.pop())
    first_operator = get_corres_value(frame=frame, key=stack.pop())
    stack.append(first_operator // second_operator)


def BINARY_MODULO_handler(stack, instr, frame):
    second_operator = get_corres_value(frame=frame, key=stack.pop())
    first_operator = get_corres_value(frame=frame, key=stack.pop())
    stack.append(first_operator % second_operator)


def BINARY_AND_handler(stack, instr, frame):
    second_operator = get_corres_value(frame=frame, key=stack.pop())
    first_operator = get_corres_value(frame=frame, key=stack.pop())
    stack.append(first_operator & second_operator)


def BINARY_XOR_handler(stack, instr, frame):
    second_operator = get_corres_value(frame=frame, key=stack.pop())
    first_operator = get_corres_value(frame=frame, key=stack.pop())
    stack.append(first_operator ^ second_operator)


def BINARY_OR_handler(stack, instr, frame):
    second_operator = get_corres_value(frame=frame, key=stack.pop())
    first_operator = get_corres_value(frame=frame, key=stack.pop())
    stack.append(first_operator | second_operator)


def BINARY_SUBSCR_handler(stack, instr, frame):
    first_operator = stack.pop()
    second_operator = stack.pop()
    stack.append(str(second_operator) + '[' + str(first_operator) + ']')


def BINARY_TRUE_DIVIDE_handler(stack, instr, frame):
    second_operator = get_corres_value(frame, stack.pop())
    first_operator = get_corres_value(frame, stack.pop())

    if isinstance(second_operator, str) \
            or isinstance(first_operator, str):
        stack.append(str(first_operator) + ' / ' + str(second_operator))
    else:
        stack.append(first_operator / second_operator)


def COMPARE_OP_handler(stack, instr, frame):
    second_operator = get_corres_value(frame, stack.pop())
    first_operator = get_corres_value(frame, stack.pop())
    try:
        if instr.argval == '==':
            stack.append(first_operator == second_operator)
        elif instr.argval == 'in':
            stack.append(first_operator in second_operator)
        elif instr.argval == '!=':
            stack.append(first_operator != second_operator)
        else:
            stack.append(str(first_operator) + '&' + instr.argval + '&' + str(second_operator))
    except:
        stack.append(str(first_operator) + '&' + instr.argval + '&' + str(second_operator))


def POP_TOP_handler(stack, instr, frame):
    stack.pop()


def LIST_APPEND_handler(stack, instr, frame):
    ins_value = stack.pop()
    ins_list = stack.pop()
    if not isinstance(ins_list, type(stack)):
        ins_list = stack.pop()
    ins_list.append(ins_value)
    stack.append(ins_list)


def IMPORT_NAME_handler(stack, instr, frame):
    stack.append(instr.argval)


def MAKE_FUNCTION_handler(stack, instr, frame):
    func_name = stack.pop()
    func_body = stack.pop()
    if instr.arg == 8:
        stack.pop()
    stack.append(func_body)


def SETUP_WITH_handler(stack, instr, frame):
    stack.append('in with block')


def BUILD_MAP_UNPACK_WITH_CALL_handler(stack, instr, frame):
    BUILD_TUPLE_handler(stack, instr, frame)


def get_corres_value(frame, key):
    try:
        if key in frame.f_locals:
            return frame.f_locals[key]
        elif key in frame.f_globals:
            return frame.f_globals[key]
        elif key in frame.f_builtins:
            return frame.f_builtins[key]
    except:
        pass

    return key
