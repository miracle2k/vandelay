class Node(object):
    """The mother of all nodes.
    """

    # The name of the node.
    name = None

    # Simple builtin argument validation for nodes.
    valid_keys = None
    valid_args = None
    allow_children = False

    @classmethod
    def configure(self, values):
        """Run once the first time a node is used in a script.

        May return a dict of values that can potentially be stored
        by the script runner. In a future run, you may receive a set
        of previously stored ``values``, allowing you to skip the
        configuration steps for which a value already exists.

        If a ``values`` dict was passed in, you should always return
        it again (possibly modified).
        """
        pass

    def __init__(self, parent):
        """Setup a node as part of the tree.

        You may do some basic validation here already in terms of
        number of arguments etc.
        """
        pass


    def run(self):
        """Run the node. Do whatever it should do.
        """
        raise NotImplementedError()


class Expr(Node):
    pass


class Bin(Expr):
    def __init__(self, left, right, lineno=None):
        Expr.__init__(self, lineno)
        self.left = left
        self.right = right


class Add(Bin):
    pass


class Literal(Expr):
    pass


class Call(Expr):
    pass


class Statement(Node):
    pass


class Assign(Statement):
    def __init__(self, asignee, expression):
        pass


class Command(Call):
    pass



class Echo(Command):
    """Print something to the output.
    """

    def run(self):
        print " ".join(self.args.as_strings(self.env))


class Target(Statement):

    valid_keys = ('depends',)

    def validate(self, parent, args):
        self.env.require(parent, 'root')

    def run(self):
        self.nodes.


class Namespace(Node):
    """Basically, an invididual build file.
    """

    allow_children = True

    def set_children(self, nodes):
        self.pre = []
        self.post = []
        self.targets = []

        # Split into pre-run steps, post-run steps, and targets.
        found_target = False
        last_non_target = None
        for node in nodes:
            if isinstance(node, Target):
                if not found_target:
                    found_target = True
                else if last_non_target:
                    raise SyntaxError(last_non_target)
                self.targets.append(node)
                # XXX: add the targets of nested namespaces
            else:
                if found_target:
                    self.post.append(node)
                else:
                    self.pre.append(node)
                last_non_target = node

    def execute(self, runner, target):
        self.execute(self.pre)
        target.run()
        run(self.post)


class Set(Node):

    valid_keys = True

    def execute(self):
        for key, value in self.args.keys():
            self.env.resolve(key).set(self.env.resolve(value))


class Use(Namespace):
    """Include another file or library.
    """

    allow_children = False

    def validate(self, parent, args):
        self.env.require(parent, (None, Use),
                         "use most the the first thing in a file.""")

        env.load_file(filename)

