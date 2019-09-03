class CommonException(Exception):
    def __init__(self, message, code):
        super().__init__(message, code)
        self.message = message
        self.code = code
