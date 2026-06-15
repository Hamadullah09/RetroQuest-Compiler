# RetroQuest Compiler Architecture

## 1. Pipeline Overview
RetroQuest follows a standard compiler pipeline:

1. Lexical analysis
2. Syntax analysis
3. Semantic analysis
4. Intermediate representation generation
5. Optimization
6. Code generation / execution through interpretation

## 2. Module Breakdown

### `token_defs.py`
Defines token types, keyword mapping, and token data structure.

### `lexer.py`
Scans the source program character by character and emits tokens with line/column metadata.

### `parser.py`
Consumes the token stream and builds an AST using recursive descent parsing.

### `ast_nodes.py`
Defines the program, scene, statement, expression, and condition node types.

### `semantic_analyzer.py`
Builds the symbol table and validates names, scenes, and variable references.

### `ir_generator.py`
Transforms the AST into a custom JSON-compatible IR based on story scenes and transitions.

### `optimizer.py`
Runs two basic optimizations:
- constant folding and propagation
- unreachable code and unreachable scene elimination

### `interpreter.py`
Executes the optimized IR directly as a virtual machine for RetroQuest stories.

### `main.py`
Acts as the compiler driver. It handles command-line arguments, debug output, file generation, and REPL mode.

## 3. Symbol Table Design
Current symbol table structure:
```text
variables: { name -> initial_value }
scenes:    { scene_name }
```

This is sufficient because RetroQuest currently supports a single global scope.

## 4. Control Flow Model
Each `scene` is treated as a node. Edges are created from:
- `choice` statements
- `goto` statements
- `if ... then goto` statements

This makes the generated IR easy to visualize as a directed graph.

## 5. Intermediate Representation Design
RetroQuest uses a custom story graph IR instead of machine code. This is valid for the assignment because the brief allows a custom IR interpreted by a virtual machine.

Example:
```json
{
  "title": "Treasure Hunt",
  "variables": {
    "has_key": false
  },
  "scenes": {
    "start": [
      { "type": "ShowStatement", "text": "You wake up in a dark room." },
      { "type": "ChoiceStatement", "text": "Open the wooden chest", "target": "chest" }
    ]
  },
  "entry_scene": "start"
}
```

## 6. Optimization Design

### Constant Folding / Propagation
If a condition can be evaluated from known constant variable values, the optimizer rewrites:
- `IfGotoStatement` to `GotoStatement` when always true
- removes `IfGotoStatement` when always false
- propagates known values into assignments

### Unreachable Code Elimination
Statements after unconditional control transfer are removed:
- `goto`
- `end`
- `restart`
- fully resolved conditional branches

### Unreachable Scene Elimination
After control-flow analysis, any scene not reachable from `start` is removed from the final IR.

## 7. Error Reporting
Errors are phase-specific:
- Lexer errors: invalid characters, unterminated strings
- Parser errors: missing tokens, invalid statement order
- Semantic errors: duplicate or undefined names, missing `start`

## 8. Why This Fits the Semester Brief
- Custom retro-themed language
- Complete compiler phases
- CLI support
- Debug mode
- Custom IR
- Basic optimization
- Execution through a virtual machine
