from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ast_nodes import (
    BinaryExpression,
    ChoiceStatement,
    Condition,
    GotoStatement,
    IfGotoStatement,
    Literal,
    Program,
    Scene,
    SetStatement,
    ShowStatement,
    VarDeclaration,
    VariableReference,
)


class SemanticError(Exception):
    pass


@dataclass
class SymbolTable:
    variables: dict[str, Any] = field(default_factory=dict)
    scenes: set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, Any]:
        return {
            "variables": self.variables,
            "scenes": sorted(self.scenes),
        }


class SemanticAnalyzer:
    def analyze(self, program: Program) -> SymbolTable:
        symbols = SymbolTable()
        for declaration in program.variables:
            self._register_variable(declaration, symbols)
        for scene in program.scenes:
            if scene.name in symbols.scenes:
                raise SemanticError(f"Oops! The scene label '{scene.name}' has been used more than once. Every scene needs a unique name so I know where to go!")
            symbols.scenes.add(scene.name)
        if "start" not in symbols.scenes:
            raise SemanticError("Wait, I can't find a 'start' scene! Every RetroQuest story needs to begin somewhere. Please add a 'scene start:' label.")
        for scene in program.scenes:
            self._validate_scene(scene, symbols)
        return symbols

    def _register_variable(self, declaration: VarDeclaration, symbols: SymbolTable) -> None:
        if declaration.name in symbols.variables:
            raise SemanticError(f"Wait a second! The variable '{declaration.name}' is already declared. You can't have two variables with the same name!")
        value = self._resolve_initial_value(declaration.value, symbols)
        symbols.variables[declaration.name] = value

    def _resolve_initial_value(self, expression, symbols: SymbolTable):
        if isinstance(expression, Literal):
            return expression.value
        if isinstance(expression, VariableReference):
            if expression.name not in symbols.variables:
                raise SemanticError(f"I found a reference to '{expression.name}', but I don't know what that is! Did you forget to declare it with 'var' first?")
            return symbols.variables[expression.name]
        if isinstance(expression, BinaryExpression):
            return self._evaluate_binary_expression(expression, symbols)
        raise SemanticError("Unsupported initializer")

    def _validate_scene(self, scene: Scene, symbols: SymbolTable) -> None:
        for statement in scene.statements:
            if isinstance(statement, ChoiceStatement):
                self._require_scene(statement.target, symbols)
            elif isinstance(statement, GotoStatement):
                self._require_scene(statement.target, symbols)
            elif isinstance(statement, SetStatement):
                self._require_variable(statement.name, symbols)
                self._validate_expression(statement.value, symbols)
            elif isinstance(statement, ShowStatement):
                self._validate_expression(statement.value, symbols)
            elif isinstance(statement, IfGotoStatement):
                self._validate_condition(statement.condition, symbols)
                self._require_scene(statement.target, symbols)

    def _validate_expression(self, expression, symbols: SymbolTable) -> None:
        if isinstance(expression, Literal):
            return
        if isinstance(expression, VariableReference):
            self._require_variable(expression.name, symbols)
            return
        if isinstance(expression, BinaryExpression):
            self._validate_expression(expression.left, symbols)
            self._validate_expression(expression.right, symbols)
            self._ensure_addition_types(expression, symbols)
            return
        raise SemanticError("Unsupported expression")

    def _validate_condition(self, condition: Condition, symbols: SymbolTable) -> None:
        self._require_variable(condition.variable, symbols)
        if isinstance(condition.value, dict) and "var" in condition.value:
            self._require_variable(condition.value["var"], symbols)
        elif isinstance(condition.value, (Literal, VariableReference, BinaryExpression)):
            self._validate_expression(condition.value, symbols)

    def _require_variable(self, name: str, symbols: SymbolTable) -> None:
        if name not in symbols.variables:
            raise SemanticError(f"I'm confused! I see the name '{name}', but it hasn't been defined as a variable. Check your 'var' declarations!")

    def _require_scene(self, name: str, symbols: SymbolTable) -> None:
        if name not in symbols.scenes:
            raise SemanticError(f"Uh oh! You're trying to go to a scene called '{name}', but that scene doesn't exist. Better check your labels!")

    def _evaluate_binary_expression(self, expression: BinaryExpression, symbols: SymbolTable):
        left = self._resolve_expression_value(expression.left, symbols)
        right = self._resolve_expression_value(expression.right, symbols)
        if expression.operator == "+":
            # Support string concatenation
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            if not isinstance(left, int) or not isinstance(right, int):
                raise SemanticError("Arithmetic (+) supports integers or string concatenation. Other operators require integers.")
            return left + right
        if expression.operator == "-":
            if not isinstance(left, int) or not isinstance(right, int):
                raise SemanticError("Arithmetic only supports integer operands")
            return left - right
        if expression.operator == "*":
            if not isinstance(left, int) or not isinstance(right, int):
                raise SemanticError("Arithmetic only supports integer operands")
            return left * right
        if expression.operator == "/":
            if not isinstance(left, int) or not isinstance(right, int):
                raise SemanticError("Arithmetic only supports integer operands")
            if right == 0:
                raise SemanticError("Division by zero is not allowed")
            return left // right
        raise SemanticError(f"Unsupported operator: {expression.operator}")

    def _resolve_expression_value(self, expression, symbols: SymbolTable):
        if isinstance(expression, Literal):
            return expression.value
        if isinstance(expression, VariableReference):
            self._require_variable(expression.name, symbols)
            return symbols.variables[expression.name]
        if isinstance(expression, BinaryExpression):
            return self._evaluate_binary_expression(expression, symbols)
        raise SemanticError("Unsupported expression")

    def _ensure_addition_types(self, expression: BinaryExpression, symbols: SymbolTable) -> None:
        left = self._resolve_expression_value(expression.left, symbols)
        right = self._resolve_expression_value(expression.right, symbols)
        if expression.operator == "+":
            # Allow strings or integers for +
            if not (isinstance(left, (int, str)) and isinstance(right, (int, str))):
                 raise SemanticError("The '+' operator requires integers or strings.")
            return
        
        if expression.operator in {"-", "*", "/"}:
            if not isinstance(left, int) or not isinstance(right, int):
                raise SemanticError("Arithmetic (-, *, /) only supports integer operands")
            if expression.operator == "/" and right == 0:
                raise SemanticError("Division by zero is not allowed")
