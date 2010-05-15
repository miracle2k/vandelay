from vandelib.parser import Lexer
from StringIO import StringIO


class LexerTester:
    def lex(self, text):
        l = Lexer(StringIO(text))
        l.next()
        result = []
        while not l.check('EOF'):
            result.append(l.next().type)
        return tuple(result)


class TestTokens(LexerTester):

    def test_simple_tokens(self):
        assert self.lex('(') == ('LBRACKET',)
        assert self.lex(')') == ('RBRACKET',)
        assert self.lex(':') == ('COLON',)

    def test_name(self):
        assert self.lex('abc') == ('NAME',)
        assert self.lex('a123') == ('NAME',)

    def test_number(self):
        assert self.lex('123') == ('NUMBER',)


class TestIndentation(LexerTester):

    def test(self):
        assert self.lex(
"""
foo
    foo
    foo
foo
"""
        ) == ('NEWLINE', 'NAME', 'INDENT', 'NAME', 'NEWLINE', 'NAME', 'OUTDENT', 'NAME', 'NEWLINE')