from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Literal:
    value: Any


@dataclass
class VariableReference:
    name: str


@dataclass
class BinaryExpression:
    left: "Expression"
    operator: str
    right: "Expression"


Expression = Literal | VariableReference | BinaryExpression


@dataclass
class Condition:
    variable: str
    operator: str | None = None
    value: Any | None = None


@dataclass
class ShowStatement:
    value: Expression


@dataclass
class ChoiceStatement:
    text: str
    target: str


@dataclass
class GotoStatement:
    target: str


@dataclass
class SetStatement:
    name: str
    value: Expression


@dataclass
class IfGotoStatement:
    condition: Condition
    target: str


@dataclass
class EndStatement:
    pass


@dataclass
class RestartStatement:
    pass


Statement = (
    ShowStatement
    | ChoiceStatement
    | GotoStatement
    | SetStatement
    | IfGotoStatement
    | EndStatement
    | RestartStatement
)


@dataclass
class VarDeclaration:
    name: str
    value: Expression


@dataclass
class Scene:
    name: str
    statements: list[Statement]


@dataclass
class Program:
    title: str
    variables: list[VarDeclaration]
    scenes: list[Scene]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
