from collections import defaultdict

debug = False

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


def print_errors_and_warnings():
    for i, line in sorted(errors_and_warnings.items()):
        tab = "  " if i < 10 else " " if i < 100 else ""
        print(f"Line {tab}{i}:")
        for level, msg in line:
            print(f"\t{level}: {msg}")


def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator
