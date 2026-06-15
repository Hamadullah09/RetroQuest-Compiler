from __future__ import annotations

from dataclasses import asdict
from typing import Any

from ast_nodes import (
    BinaryExpression,
    EndStatement,
    GotoStatement,
    IfGotoStatement,
    Literal,
    Program,
    RestartStatement,
    SetStatement,
    VariableReference,
)


class IRGenerator:
    def generate(self, program: Program) -> dict[str, Any]:
        return {
            "title": program.title,
            "variables": {
                declaration.name: self._serialize_expression(declaration.value)
                for declaration in program.variables
            },
            "scenes": {
                scene.name: [self._serialize_statement(statement) for statement in scene.statements]
                for scene in program.scenes
            },
            "entry_scene": "start",
        }

    def _serialize_expression(self, expression):
        if isinstance(expression, Literal):
            return expression.value
        if isinstance(expression, VariableReference):
            return {"var": expression.name}
        if isinstance(expression, BinaryExpression):
            return {
                "binary": {
                    "left": self._serialize_expression(expression.left),
                    "operator": expression.operator,
                    "right": self._serialize_expression(expression.right),
                }
            }
        return asdict(expression)

    def _serialize_statement(self, statement):
        data = asdict(statement)
        data["type"] = statement.__class__.__name__
        if statement.__class__.__name__ == "ShowStatement":
            data["value"] = self._serialize_expression(statement.value)
        elif isinstance(statement, SetStatement):
            data["value"] = self._serialize_expression(statement.value)
        elif isinstance(statement, IfGotoStatement):
            data["condition"] = statement.condition.__dict__.copy()
            if statement.condition.value is not None:
                data["condition"]["value"] = self._serialize_condition_value(statement.condition.value)
        elif isinstance(statement, (GotoStatement, EndStatement, RestartStatement)):
            pass
        return data

    def _serialize_condition_value(self, value):
        if isinstance(value, (Literal, VariableReference, BinaryExpression)):
            return self._serialize_expression(value)
        return value
