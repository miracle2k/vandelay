__all__ = ('LazyType', 'Type', 'Number', 'String', 'FileSet', 'Variable')


class Type(object):
    pass


class Number(Type):
    pass


class String(Type):
    pass


class FileSet(Type):
    pass


class Variable(Type):
    pass


class LazyType(object):

    def __init__(self, data):
        self.data = data
