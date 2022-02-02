def args(arg_list, name):
    content = ['try:']
    content.append('    ' + name + ' = []')
    for one_arg in arg_list:
        if type(one_arg).__name__ == 'str':
            content.append('    ' + name + '.append(\'' + str(one_arg) + '\')')
        else:
            content.append('    ' + name + '.append(' + str(one_arg) + ')')
    return content


def import_part(one_module):
    content = []
    content.append('import numpy')

    if not isinstance(one_module, list):
        content.append('import ' + str(one_module))
    else:
        content.append('from ' + str(one_module[0]) + ' import ' + str(one_module[1]))
    return content


def func_call(func, arg_str):
    content = []
    content.append('    ' + str(func) + '(' + arg_str + ')')
    content.append('except:')
    content.append('    pass')
    return content
