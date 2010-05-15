"""Simple Lexer/Parser.

TODO: This is currently using PLY for quick prototyping, but we don't
want to have a dependency here, so get rid of it eventually.
"""

from ply import lex


__all__ = ('Lexer', 'LexerError', 'Parser',)


class LexerError(Exception):
    pass


class ParserError(Exception):
    pass


def make_lex():
    """Return a ``lex`` lexer object, which will take care of the
    actual tokenization.
    """
    tokens = (
        'NAME',
        'COLON',
        'WHITESPACE',
        'NEWLINE',
        'NUMBER',
        'LBRACKET',
        'RBRACKET',
    )

    t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    t_COLON = r':'
    t_WHITESPACE = r'[ ]+'
    t_NUMBER = r'[0-9]+'
    t_LBRACKET = r'\('
    t_RBRACKET = r'\)'

    def t_NEWLINE(t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t

    def t_error(t):
        t.lexer.skip(1)
        raise LexerError('invalid token %s in line %d' % (t.value, t.lexpos))

    return lex.lex()


def make_token(type, value='', lineno=None, lexpos=None):
    """Helper to make a ``LexToken`` instance.
    """
    t = lex.LexToken()
    t.type = type
    t.value = value
    t.lineno = lineno
    t.lexpos = lexpos
    return t


def fix_lex_eof(tokenstream):
    """Wrap around a lex.token() method to return EOF tokens rather
    than ``None`` at the end. This is easier to deal with.
    """
    def wrapped():
        token = tokenstream()
        if token is None:
            return make_token('EOF')
        else:
            return token
    return wrapped


class Lexer(object):
    """Return a stream of tokens.

    Normalizes newlines by either returning an INDENT, OUTDENT, or a
    NEWLINE token if no indentation change occured.
    """

    def __init__(self, file):
        lex = make_lex()
        lex.input(file.read())
        self.token = fix_lex_eof(lex.token)

        self._indent = [0]
        self._buffer = []
        self.current = None

    def _read(self):
        """Read more tokens into the buffer. This handles indentation.
        """
        token = self.token()
        if token and token.type == 'WHITESPACE':
            while token and token.type in ('NEWLINE', 'WHITESPACE'):
                prev = token
                token = self.token()
            self._buffer.append(token)

        elif token and token.type == 'NEWLINE':
            newline_token = token
            # Process until the next non-whitespace token
            prev = None
            while token and token.type in ('NEWLINE', 'WHITESPACE'):
                prev = token
                token = self.token()

            # Bail out early
            if token is None:
                self._buffer.append(token)
                return

            # If the previous token was space, determine the indentation.
            # This relies on WHITESPACE tokens to not occur multiple times
            # in a row.
            if prev.type == 'WHITESPACE':
                new_indent = len(prev.value.expandtabs())
            else:
                new_indent = 0

            # If the indentation changed, generate indent/outdent tokens
            indent_change = new_indent - self._indent[0]
            if indent_change > 0:
                self._indent.insert(0, new_indent)
                self._buffer.append(
                    make_token('INDENT', '', token.lineno, token.lexpos))
            elif indent_change < 0:
                while self._indent[0] != new_indent:
                    if len(self._indent) <= 1:
                        raise LexerError("broken indentation")
                    self._indent.pop(0)
                    self._buffer.append(
                        make_token('OUTDENT', '', token.lineno, token.lexpos))
            else:
                # No whitespace change, add a NEWLINE token
                self._buffer.append(newline_token)

            # Add the next-non whitespace token itself
            self._buffer.append(token)
        else:
            self._buffer.append(token)

    def next(self):
        if not self._buffer:
            self._read()
        previous = self.current
        self.current = self._buffer.pop(0)
        return previous

    def check(self, *what):
        return self.current.type in what

    def expect(self, *what):
        if self.check(*what):
            return self.next()
        else:
            raise LexerError('Line %d: Expected %s, got %s' % (
                self.current.lineno, what, self.current))


class Parser(object):
    """Takes input tokens from the lexer and builds a node tree.
    """

    def __init__(self, lexer):
        self.lexer = lexer
        self.lexer.next()

    def __iter__(self):
        def _flatten(items):
            for name, children in items:
                yield name
                if children:
                    for r in _flatten(children):
                        yield r

        return _flatten(self.node_list())

    def node_list(self):
        nodes = []
        while not self.lexer.check('EOF', 'OUTDENT'):
            if self.lexer.check('NEWLINE'):
                self.lexer.next()
                continue
            nodes.append(self.node())
        return nodes

    def node(self):
        node_name = self.call()
        child_nodes = []
        if self.lexer.check('COLON'):
            self.lexer.next()
            self.lexer.expect('INDENT')
            child_nodes = self.node_list()
            self.lexer.expect('OUTDENT')

        return node_name, child_nodes

    def call(self):
        node_name = self.lexer.expect('NAME').value
        args = self.expression()
        if not isinstance(args, (list,)):
            args = [args]
        return node_name, args

    def expression(self):
        """could be multiple values, lists, nested calls)
        """
        expr_list = []
        while not self.lexer.check('COLON', 'OUTDENT', 'NEWLINE', 'EOF', 'RBRACKET'):
            expr_list.append(self.single_value())
        return expr_list

    def single_value(self):
        return self.primary()

    def primary(self):
        if self.lexer.check('NUMBER'):
            #return nodes.Number(self.lexer.expect('NUMBER').value)
            return self.lexer.expect('NUMBER').value
        elif self.lexer.check('LBRACKET'):
            self.lexer.next()
            result = self.expression()
            self.lexer.expect('RBRACKET')
            return result
        elif self.lexer.check('NAME'):
            return self.call()
        else:
            raise ParserError('Unexpected token: %s', self.lexer.current)


if __name__ == '__main__':
    import StringIO
    text = '''
a 34 (b) 12:
    rm 12 34 45 56 456
b'''
    l = Lexer(StringIO.StringIO(text))
    l.next()
    while True:
        if l.current.type == 'EOF':
            break
        print l.next()

    print "-------------"

    p = Parser(Lexer(StringIO.StringIO(text)))
    for x in list(p):
        print x
