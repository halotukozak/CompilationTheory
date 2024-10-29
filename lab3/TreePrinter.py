def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator


class TreePrinter:
    # @addToClass(Node)
    # def printTree(self, indent=0):
#
