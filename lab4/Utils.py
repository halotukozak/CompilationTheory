def report_error(self, message: str, lineno: int):
    self.failed = True
    print(f"Error at line {lineno}: {message}")
