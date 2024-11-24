def report_error(self, message: str, lineno: int):
    self.failed = True
    print(f"Error at line {lineno}: {message}")


def report_warn(self, message: str, lineno: int):
    print(f"Warn at line {lineno}: {message}")


def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator
