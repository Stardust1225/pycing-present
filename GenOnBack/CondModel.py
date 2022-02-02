class CondModel:
    def __init__(self, func, arg_list, cond, arg_str_list, content, turn):
        self.cond = cond
        self.arg_list = arg_list
        self.func = func
        self.arg_str_list = arg_str_list
        self.content = content
        self.turn = turn
