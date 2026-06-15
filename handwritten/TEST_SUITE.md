# RetroQuest Test Suite

This project includes at least 5 test programs. Use them to demonstrate valid execution, optimization, and error handling.

## 1. `examples/treasure_hunt.rq`
Purpose:
- basic branching
- variable update
- conditional goto

Expected behavior:
- player can collect the key and then escape

## 2. `examples/fixed_ending.rq`
Purpose:
- demonstrate constant folding
- demonstrate unreachable code elimination

Expected behavior:
- optimizer resolves the branch to the ending scene

## 3. `examples/restart_demo.rq`
Purpose:
- demonstrate restart semantics

Expected behavior:
- story resets runtime variables to compiled initial state

## 4. `tests/undefined_scene.rq`
Purpose:
- semantic error case

Expected behavior:
- compiler reports `Undefined scene`

## 5. `tests/duplicate_variable.rq`
Purpose:
- duplicate declaration error

Expected behavior:
- compiler reports `Duplicate variable declaration`

## 6. `tests/missing_start.rq`
Purpose:
- missing entry point error

Expected behavior:
- compiler reports missing `start` scene

## 7. `tests/unterminated_string.rq`
Purpose:
- lexer error case

Expected behavior:
- compiler reports unterminated string with line/column

## Recommended Demo Commands
```bash
python main.py examples/treasure_hunt.rq --debug
python main.py examples/fixed_ending.rq --debug
python main.py examples/restart_demo.rq --run
python main.py tests/undefined_scene.rq
python main.py tests/unterminated_string.rq
```
