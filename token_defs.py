from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    GAME = auto()
    VAR = auto()
    SCENE = auto()
    SHOW = auto()
    CHOICE = auto()
    GOTO = auto()
    SET = auto()
    IF = auto()
    THEN = auto()
    END = auto()
    RESTART = auto()
    TRUE = auto()
    FALSE = auto()
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    COLON = auto()
    ASSIGN = auto()
    ARROW = auto()
    EQ = auto()
    NEQ = auto()
    GT = auto()
    LT = auto()
    GTE = auto()
    LTE = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()


KEYWORDS = {
    "game": TokenType.GAME,
    "var": TokenType.VAR,
    "scene": TokenType.SCENE,
    "def": TokenType.SCENE,      # Pythonic scene
    "show": TokenType.SHOW,
    "print": TokenType.SHOW,      # Pythonic show
    "choice": TokenType.CHOICE,
    "goto": TokenType.GOTO,
    "set": TokenType.SET,
    "if": TokenType.IF,
    "then": TokenType.THEN,
    "end": TokenType.END,
    "return": TokenType.END,     # Pythonic end
    "restart": TokenType.RESTART,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: object
    line: int
    column: int

    def to_dict(self) -> dict[str, object]:
        return {
            "type": self.type.name,
            "value": self.value,
            "line": self.line,
            "column": self.column,
        }
