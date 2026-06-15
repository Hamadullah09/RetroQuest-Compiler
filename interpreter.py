from __future__ import annotations

from copy import deepcopy
from typing import Any


class RuntimeError(Exception):
    pass


class Interpreter:
    def __init__(self, ir: dict[str, Any]) -> None:
        self.ir = ir
        self.initial_variables = self._resolve_initial_variables(ir.get("variables", {}))
        self.variables = deepcopy(self.initial_variables)

    def run(self) -> None:
        current_scene = self.ir.get("entry_scene", "start")
        while True:
            if current_scene not in self.ir["scenes"]:
                raise RuntimeError(f"Scene '{current_scene}' does not exist in IR")
            next_scene = self._execute_scene(current_scene)
            if next_scene is None:
                return
            if next_scene == "__restart__":
                self.variables = deepcopy(self.initial_variables)
                current_scene = self.ir.get("entry_scene", "start")
                continue
            current_scene = next_scene

    def _execute_scene(self, scene_name: str) -> str | None:
        statements = self.ir["scenes"][scene_name]
        index = 0
        while index < len(statements):
            statement = statements[index]
            statement_type = statement["type"]
            if statement_type == "ShowStatement":
                print(self._resolve_value(statement["value"]))
            elif statement_type == "SetStatement":
                self.variables[statement["name"]] = self._resolve_value(statement["value"])
            elif statement_type == "GotoStatement":
                return statement["target"]
            elif statement_type == "IfGotoStatement":
                if self._evaluate_condition(statement["condition"]):
                    return statement["target"]
            elif statement_type == "ChoiceStatement":
                return self._handle_choices(statements[index:])
            elif statement_type == "EndStatement":
                print("The story has ended.")
                return None
            elif statement_type == "RestartStatement":
                print("Restarting story...")
                return "__restart__"
            index += 1
        return None

    def _handle_choices(self, statements: list[dict[str, Any]]) -> str:
        choices: list[dict[str, Any]] = []
        for statement in statements:
            if statement["type"] != "ChoiceStatement":
                break
            choices.append(statement)
        if not choices:
            raise RuntimeError("Choice handler called with no choices")
        print("Choose an option:")
        for idx, choice in enumerate(choices, start=1):
            print(f"{idx}. {choice['text']}")
        while True:
            raw = input("> ").strip()
            if raw.isdigit():
                selected = int(raw)
                if 1 <= selected <= len(choices):
                    return choices[selected - 1]["target"]
            print("Invalid choice. Enter the number of one option.")

    def _resolve_value(self, value):
        if isinstance(value, dict) and "var" in value:
            return self.variables[value["var"]]
        if isinstance(value, dict) and "binary" in value:
            left = self._resolve_value(value["binary"]["left"])
            right = self._resolve_value(value["binary"]["right"])
            operator = value["binary"]["operator"]
            if operator == "+":
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                if not isinstance(left, int) or not isinstance(right, int):
                    raise RuntimeError("Arithmetic (+) supports integers or string concatenation.")
                return left + right
            
            if operator in {"-", "*", "/"}:
                if not isinstance(left, int) or not isinstance(right, int):
                    raise RuntimeError(f"Operator {operator} only supports integer operands")
                if operator == "-":
                    return left - right
                if operator == "*":
                    return left * right
                if right == 0:
                    raise RuntimeError("Division by zero is not allowed")
                return left // right
            raise RuntimeError(f"Unsupported operator: {operator}")
        return value

    def _resolve_initial_variables(self, raw_variables: dict[str, Any]) -> dict[str, Any]:
        resolved: dict[str, Any] = {}
        previous_variables = self.variables if hasattr(self, "variables") else {}
        self.variables = resolved
        try:
            for name, value in raw_variables.items():
                resolved[name] = self._resolve_value(deepcopy(value))
        finally:
            self.variables = previous_variables
        return resolved

    def _evaluate_condition(self, condition: dict[str, Any]) -> bool:
        left = self.variables[condition["variable"]]
        operator = condition.get("operator")
        if operator is None:
            return bool(left)
        right = condition.get("value")
        if isinstance(right, dict):
            right = self._resolve_value(right)
        if operator == "==":
            return left == right
        if operator == "!=":
            return left != right
        if operator == ">":
            return left > right
        if operator == "<":
            return left < right
        if operator == ">=":
            return left >= right
        if operator == "<=":
            return left <= right
        raise RuntimeError(f"Unsupported operator: {operator}")
