import sys, os
from os import path
from .parser import Lexer, Parser


__all__  = ('main', 'Environment',)


class ScopedDict(dict):
    pass


class Context(object):
    self.namespace = ScopedDict()
    self.globals = dict()
    self.locals = ScopedDict()
    self.superlocals = ScopedDict()

    def push(self):
        self.namespace.push()
        self.locals.push()
        self.superlocals.push()

    def pop(self):
        self.namespace.pop()
        self.locals.pop()
        self.superlocals.pop()


class Environment(object):
    """Is good for loading a build script and running it once.
    """

    def __init__(self):
        self.loaded_nodes = []

    def setup_execution_context(self):
        self.context = Context()

    def load_file(self, parent, filename):
        """Parse and load a list of nodes from ``filename``, attach
        them to ``parent``.
        """
        file = open(filename, 'rb')
        try:
            lexer = Lexer(file)
            parser = Parser(lexer)
            stack = [parent]

            # Note that we have chosen an iterative approach versus
            # building the tree recursively, so that syntax errors
            # that occur further up in the thread will be raised first.
            prev = None
            for elem in parser:
                if elem == Parser.CHILD:
                    stack.insert(0, prev)
                elif elem == Parser.END:
                    stack.pop(0)
                else:
                    stack[0].add_child(elem)

                prev = elem

        finally:
            file.close()


def run(tree, target):
    assert "can only run namespace instances", isinstance(tree, Namespace)
    target_node = find_target(target)
    target_to_run = build_dep_tree(target_node)
    tree.execute()


DEFAULT_FILENAME = 'architect'

def main(argv):
    """The main program.
    """
    assert len(argv) == 2
    selected_target = argv[1]

    # Find the build file
    if not path.exists(DEFAULT_FILE):
        print "No %s file in current directory" % DEFAULT_FILENAME

    env = Environment()
    script = Script()
    nodes = env.load_file(script, DEFAULT_FILE)

    env.setup_execution_context()
    script.run(env, target)


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)