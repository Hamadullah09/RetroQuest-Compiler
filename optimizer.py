from __future__ import annotations

from copy import deepcopy
from typing import Any


UNKNOWN = object()


class Optimizer:
    def optimize(self, ir: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
        optimized = deepcopy(ir)
        initial_env = self._resolve_initial_variables(optimized.get("variables", {}))
        mutable_variables = self._collect_mutable_variables(optimized["scenes"])
        scene_stats = {"folded_conditions": 0, "removed_statements": 0, "removed_scenes": 0}

        optimized_scenes: dict[str, list[dict[str, Any]]] = {}
        for scene_name, statements in optimized["scenes"].items():
            new_statements, stats = self._optimize_scene(statements, initial_env, mutable_variables)
            optimized_scenes[scene_name] = new_statements
            scene_stats["folded_conditions"] += stats["folded_conditions"]
            scene_stats["removed_statements"] += stats["removed_statements"]

        optimized["scenes"] = optimized_scenes
        reachable = self._collect_reachable_scenes(
            optimized["scenes"], optimized.get("entry_scene", "start")
        )
        all_scenes = set(optimized["scenes"].keys())
        unreachable = all_scenes - reachable
        for scene_name in unreachable:
            del optimized["scenes"][scene_name]
        scene_stats["removed_scenes"] = len(unreachable)
        optimized["optimization_stats"] = scene_stats
        return optimized, scene_stats

    def _resolve_initial_variables(self, variables: dict[str, Any]) -> dict[str, Any]:
        resolved: dict[str, Any] = {}
        for name, value in variables.items():
            resolved[name] = self._resolve_value(value, resolved)
        return resolved

    def _optimize_scene(
        self,
        statements: list[dict[str, Any]],
        initial_env: dict[str, Any],
        mutable_variables: set[str],
    ) -> tuple[list[dict[str, Any]], dict[str, int]]:
        env = dict(initial_env)
        optimized: list[dict[str, Any]] = []
        stats = {"folded_conditions": 0, "removed_statements": 0}
        terminated = False

        for index, statement in enumerate(statements):
            if terminated:
                stats["removed_statements"] += 1
                continue

            statement_type = statement["type"]
            if statement_type == "SetStatement":
                value = self._resolve_value(statement["value"], env)
                new_statement = dict(statement)
                new_statement["value"] = value
                optimized.append(new_statement)
                env[statement["name"]] = value if not isinstance(value, dict) else UNKNOWN
                continue

            if statement_type == "IfGotoStatement":
                condition_value = self._evaluate_condition(
                    statement["condition"], env, mutable_variables
                )
                if condition_value is True:
                    optimized.append({"type": "GotoStatement", "target": statement["target"]})
                    stats["folded_conditions"] += 1
                    terminated = True
                    continue
                if condition_value is False:
                    stats["folded_conditions"] += 1
                    stats["removed_statements"] += 1
                    continue
                optimized.append(statement)
                continue

            optimized.append(statement)
            if statement_type in {"GotoStatement", "EndStatement", "RestartStatement"}:
                terminated = True
                continue
            if statement_type == "ChoiceStatement":
                next_is_choice = index + 1 < len(statements) and statements[index + 1]["type"] == "ChoiceStatement"
                if not next_is_choice:
                    terminated = True

        return optimized, stats

    def _resolve_value(self, value: Any, env: dict[str, Any]) -> Any:
        if isinstance(value, dict) and "var" in value:
            resolved = env.get(value["var"], UNKNOWN)
            if resolved is UNKNOWN:
                return value
            return resolved
        if isinstance(value, dict) and "binary" in value:
            left = self._resolve_value(value["binary"]["left"], env)
            right = self._resolve_value(value["binary"]["right"], env)
            if isinstance(left, dict) or isinstance(right, dict):
                return {
                    "binary": {
                        "left": left,
                        "operator": value["binary"]["operator"],
                        "right": right,
                    }
                }
            operator = value["binary"]["operator"]
            if operator in {"+", "-", "*", "/"} and isinstance(left, int) and isinstance(right, int):
                if operator == "+":
                    return left + right
                if operator == "-":
                    return left - right
                if operator == "*":
                    return left * right
                if right != 0:
                    return left // right
            return value
        return value

    def _evaluate_condition(
        self, condition: dict[str, Any], env: dict[str, Any], mutable_variables: set[str]
    ) -> bool | None:
        if condition["variable"] in mutable_variables:
            return None
        left = env.get(condition["variable"], UNKNOWN)
        if left is UNKNOWN:
            return None

        operator = condition.get("operator")
        if operator is None:
            return bool(left)

        right = condition.get("value")
        if isinstance(right, dict) and "var" in right:
            if right["var"] in mutable_variables:
                return None
        if isinstance(right, dict):
            right = self._resolve_value(right, env)
        if right is UNKNOWN or isinstance(left, dict) or isinstance(right, dict):
            return None
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
        return None

    def _collect_mutable_variables(self, scenes: dict[str, list[dict[str, Any]]]) -> set[str]:
        mutable_variables: set[str] = set()
        for statements in scenes.values():
            for statement in statements:
                if statement["type"] == "SetStatement":
                    mutable_variables.add(statement["name"])
        return mutable_variables

    def _collect_reachable_scenes(
        self, scenes: dict[str, list[dict[str, Any]]], entry_scene: str
    ) -> set[str]:
        if entry_scene not in scenes:
            return set()
        visited: set[str] = set()
        stack = [entry_scene]
        while stack:
            scene_name = stack.pop()
            if scene_name in visited or scene_name not in scenes:
                continue
            visited.add(scene_name)
            for statement in scenes[scene_name]:
                target = statement.get("target")
                if target:
                    stack.append(target)
        return visited
