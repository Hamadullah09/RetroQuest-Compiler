# RetroQuest Compiler

RetroQuest is a semester project for `CS4031 - Compiler Construction` at FAST-NUCES, Spring 2026. It is a retro-inspired mini compiler for a custom interactive-fiction DSL. Source programs written in `.rq` are compiled into a JSON story graph and executed through a command-line interpreter.

## Features
- Custom DSL for branching text adventures
- Lexical analysis with line/column errors
- Recursive-descent parser and AST
- Semantic analysis with symbol table checks
- JSON-based intermediate representation
- Basic optimizations
- Interactive command-line runtime
- REPL mode for quick testing

## Project Structure
```text
compiler_project/
├── main.py
├── token_defs.py
├── lexer.py
├── parser.py
├── ast_nodes.py
├── semantic_analyzer.py
├── ir_generator.py
├── optimizer.py
├── interpreter.py
├── examples/
├── tests/
├── handwritten/
└── projectagent.md
```

## Run
Open PowerShell or Command Prompt and first go to the project folder:

```bash
cd "D:\6th semester\CC\compiler_project"
```

To run any example program, use:

```bash
python main.py examples/treasure_hunt.rq --run
```

New larger example programs:

```bash
python main.py examples/procom_tech_event.rq --run
python main.py examples/robot_repair_mission.rq --run
python main.py examples/village_market_helper.rq --run
python main.py examples/score_calculator.rq --run
```

Compile only, without running:

```bash
python main.py examples/procom_tech_event.rq
```

Debug mode, to see tokens, AST, symbol table, and IR:

```bash
python main.py examples/fixed_ending.rq --debug
```

Interactive REPL mode:

```bash
python main.py --interactive
```

## Documentation
All submission-oriented documentation is inside the [`handwritten`](./handwritten) folder.

- `submission_handout.html`: handwritten artifacts guide
- `final_report.html`: report-ready HTML
- `LANGUAGE_REFERENCE.md`
- `COMPILER_ARCHITECTURE.md`
- `TEST_SUITE.md`

## Team
- Hamadullah Arain - 23K-0723
- Tashkeel Pasha - 23K-2014
- Yousaf Bhatti - 23K-0809
