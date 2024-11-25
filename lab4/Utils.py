from collections import defaultdict

debug = True

errors_and_warnings = defaultdict(lambda: [])


def report(message: str, lineno: int, level: str):
    errors_and_warnings[lineno].append((level, message))
    if debug:
        print(f"{level} at line {lineno}: {message}")


def report_error(self, message: str, lineno: int):
    self.failed = True
    report(message, lineno, "error")


def report_warn(self, message: str, lineno: int):
    report(message, lineno, "warn")


def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator
