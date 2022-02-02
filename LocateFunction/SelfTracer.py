import copy


class TracerRecorder:
    def __init__(self, path, start_line, sim_exec, project):
        self.__path = path
        self.__start_line = start_line
        self.__sim_exec = sim_exec
        self.project = project

        self.__l_frame = None
        self.__in_with = False
        self.count = 0
        self.__start_record = False

    def self_tracer(self, frame, event, arg):
        # if self.project not in frame.f_code.co_filename:
        #     return None

        if '__init__' in frame.f_code.co_filename:
            return None

        if self.count >= 50000:
            return None

        if self.__path in frame.f_code.co_filename \
                and self.__start_line <= frame.f_lineno \
                and not self.__start_record:
            self.__start_record = True

        if (frame.f_code.co_name == '__enter__'
            or frame.f_code.co_name == '__exit__') \
                and event == 'call' and self.__start_record:
            self.__in_with = True

        if (frame.f_code.co_name == '__enter__'
            or frame.f_code.co_name == '__exit__') \
                and event == 'return':
            self.__in_with = False

        if self.__start_record \
                and not self.__in_with:
            del self.__l_frame
            self.__l_frame = self.copy_frame(frame, event)

        if self.__l_frame != None \
                and self.__start_record \
                and self.__l_frame.f_lasti != -1 \
                and not self.__in_with:
            self.count += 1
            self.__sim_exec.one_frame(frame, self.__l_frame)

        return self.self_tracer

    def copy_frame(self, frame, event):
        new_frame = Frame()

        new_frame.f_locals = frame.f_locals
        new_frame.f_globals = frame.f_globals
        new_frame.f_code = copy.deepcopy(frame.f_code)
        new_frame.f_lineno = copy.deepcopy(frame.f_lineno)
        new_frame.f_builtins = frame.f_builtins
        new_frame.f_lasti = copy.deepcopy(frame.f_lasti)
        new_frame.event = copy.deepcopy(event)

        return new_frame


class Frame:
    def __init__(self):
        pass
