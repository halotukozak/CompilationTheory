# todo: can be simplified to tuple?


class Result[T]:
    def __init__(self, value: T):
        self.value = value

    def map(self, f):
        raise NotImplementedError


class Success[T](Result[T]):
    def __init__(self, value: T):
        super().__init__(value)

    def map(self, f) -> Result[T]:
        return Success(f(self.value))


class Warn[T](Result[T]):
    __match_args__ = ('value', 'warns')

    def __init__(self, value: T, *warns: str):
        super().__init__(value)
        self.warns = warns

    def map(self, f) -> Result[T]:
        return Warn(f(self.value), *self.warns)


class Failure[T](Result[T]):
    __match_args__ = ('value', 'errors')

    def __init__(self, value: T, *errors: str):
        super().__init__(value)
        self.errors = errors

    def map(self, f) -> Result[T]:
        return Failure(f(self.value), *self.errors)
