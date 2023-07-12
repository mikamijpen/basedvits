class PyCAIError(Exception):
    pass

class ServerError(PyCAIError):
    pass

class FilterError(PyCAIError):
    pass

class NotFoundError(PyCAIError):
    pass

class LabelError(PyCAIError):
    pass

class AuthError(PyCAIError):
    pass
class Loaded(PyCAIError):
    def __init__(self, message, code):
        super().__init__(message)  # 调用父类的__init__方法，传递错误信息
        self.code = code