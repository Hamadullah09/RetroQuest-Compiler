from __future__ import annotations

from dataclasses import dataclass

from token_defs import KEYWORDS, Token, TokenType


class LexerError(Exception):
    pass


@dataclass
class Lexer:
    source: str

    def __post_init__(self) -> None:
        self.index = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while not self._is_at_end():
            current = self._peek()
            if current in " \t\r":
                self._advance()
                continue
            if current == "\n":
                self._advance()
                continue
            if current == "#":
                self._skip_comment()
                continue
            if current.isalpha() or current == "_":
                tokens.append(self._identifier())
                continue
            if current.isdigit():
                tokens.append(self._number())
                continue
            if current == '"':
                tokens.append(self._string())
                continue
            tokens.append(self._symbol())
        tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return tokens

    def _identifier(self) -> Token:
        line, column = self.line, self.column
        chars: list[str] = []
        while not self._is_at_end() and (self._peek().isalnum() or self._peek() == "_"):
            chars.append(self._advance())
        text = "".join(chars)
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        if token_type is TokenType.TRUE:
            return Token(token_type, True, line, column)
        if token_type is TokenType.FALSE:
            return Token(token_type, False, line, column)
        return Token(token_type, text, line, column)

    def _number(self) -> Token:
        line, column = self.line, self.column
        chars: list[str] = []
        while not self._is_at_end() and self._peek().isdigit():
            chars.append(self._advance())
        return Token(TokenType.NUMBER, int("".join(chars)), line, column)

    def _string(self) -> Token:
        line, column = self.line, self.column
        self._advance()
        chars: list[str] = []
        while not self._is_at_end() and self._peek() != '"':
            if self._peek() == "\n":
                raise LexerError(f"Unterminated string at line {line}, column {column}")
            if self._peek() == "\\":
                self._advance()
                if self._is_at_end():
                    raise LexerError(f"Unterminated escape sequence at line {line}, column {column}")
                escaped = self._advance()
                escape_map = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
                chars.append(escape_map.get(escaped, escaped))
                continue
            chars.append(self._advance())
        if self._is_at_end():
            raise LexerError(f"Unterminated string at line {line}, column {column}")
        self._advance()
        return Token(TokenType.STRING, "".join(chars), line, column)

    def _symbol(self) -> Token:
        line, column = self.line, self.column
        current = self._advance()
        if current == ":":
            return Token(TokenType.COLON, current, line, column)
        if current == "+":
            return Token(TokenType.PLUS, current, line, column)
        if current == "*":
            return Token(TokenType.STAR, current, line, column)
        if current == "/":
            return Token(TokenType.SLASH, current, line, column)
        if current == "=":
            if self._match("="):
                return Token(TokenType.EQ, "==", line, column)
            return Token(TokenType.ASSIGN, current, line, column)
        if current == ">":
            if self._match("="):
                return Token(TokenType.GTE, ">=", line, column)
            return Token(TokenType.GT, current, line, column)
        if current == "<":
            if self._match("="):
                return Token(TokenType.LTE, "<=", line, column)
            return Token(TokenType.LT, current, line, column)
        if current == "!":
            if self._match("="):
                return Token(TokenType.NEQ, "!=", line, column)
            raise LexerError(f"Unexpected character '!' at line {line}, column {column}")
        if current == "-":
            if self._match(">"):
                return Token(TokenType.ARROW, "->", line, column)
            return Token(TokenType.MINUS, current, line, column)
        if current == "(":
            return Token(TokenType.LPAREN, current, line, column)
        if current == ")":
            return Token(TokenType.RPAREN, current, line, column)
        raise LexerError(f"Unexpected character Hamadullah'{current}' at line {line}, column {column}")

    def _skip_comment(self) -> None:
        while not self._is_at_end() and self._peek() != "\n":
            self._advance()

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self._peek() != expected:
            return False
        self._advance()
        return True

    def _peek(self) -> str:
        return self.source[self.index]

    def _advance(self) -> str:
        char = self.source[self.index]
        self.index += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def _is_at_end(self) -> bool:
        return self.index >= len(self.source)
