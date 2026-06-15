from __future__ import annotations

import argparse
import json
from pathlib import Path

from interpreter import Interpreter
from ir_generator import IRGenerator
from lexer import Lexer, LexerError
from optimizer import Optimizer
from parser import Parser, ParserError
from semantic_analyzer import SemanticAnalyzer, SemanticError


def build_pipeline(source_text: str) -> tuple[list, object, object, dict, dict, dict]:
    print("[LOG] Starting lexical analysis...")
    tokens = Lexer(source_text).tokenize()
    print(f"[LOG] Lexical analysis complete. Found {len(tokens)} tokens.")
    
    print("[LOG] Starting syntax analysis (parsing)...")
    program = Parser(tokens).parse()
    print("[LOG] Syntax analysis complete. AST generated.")
    
    print("[LOG] Starting semantic analysis...")
    symbols = SemanticAnalyzer().analyze(program)
    print("[LOG] Semantic analysis complete. Symbol table verified.")
    
    print("[LOG] Generating Intermediate Representation (IR)...")
    ir = IRGenerator().generate(program)
    print("[LOG] IR generation complete.")
    
    print("[LOG] Running optimizer...")
    optimized_ir, optimization_stats = Optimizer().optimize(ir)
    print(f"[LOG] Optimization complete. Stats: {optimization_stats}")
    
    return tokens, program, symbols, ir, optimized_ir, optimization_stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RetroQuest compiler and interpreter")
    parser.add_argument("source", nargs="?", help="Path to a .rq story file")
    parser.add_argument("-o", "--output", help="Write generated IR to a JSON file")
    parser.add_argument("--debug", action="store_true", help="Print tokens, AST, symbol table, and IR")
    parser.add_argument("--run", action="store_true", help="Run the story after compilation")
    parser.add_argument("--interactive", action="store_true", help="Compile and run interactively")
    return parser.parse_args()


def print_debug(tokens, program, symbols, ir, optimized_ir, optimization_stats) -> None:
    print("=== TOKENS ===")
    print(json.dumps([token.to_dict() for token in tokens], indent=2))
    print("\n=== AST ===")
    print(json.dumps(program.to_dict(), indent=2))
    print("\n=== SYMBOL TABLE ===")
    print(json.dumps(symbols.to_dict(), indent=2))
    print("\n=== IR (BEFORE OPTIMIZATION) ===")
    print(json.dumps(ir, indent=2))
    print("\n=== OPTIMIZATION STATS ===")
    print(json.dumps(optimization_stats, indent=2))
    print("\n=== IR (AFTER OPTIMIZATION) ===")
    print(json.dumps(optimized_ir, indent=2))


def write_output(path: str, ir: dict) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(ir, indent=2), encoding="utf-8")
    print(f"IR written to {output_path}")


def repl() -> int:
    print("RetroQuest REPL")
    print("Write your program line by line. Use :run to compile/run, :reset to clear, :quit to exit.")
    buffer: list[str] = []
    while True:
        prompt = "rq> " if not buffer else "... "
        line = input(prompt)
        stripped = line.strip()
        if stripped == ":quit":
            return 0
        if stripped == ":reset":
            buffer.clear()
            print("Buffer cleared.")
            continue
        if stripped == ":show":
            print("\n".join(buffer) if buffer else "[empty]")
            continue
        if stripped == ":run":
            source_text = "\n".join(buffer).strip()
            if not source_text:
                print("Buffer is empty.")
                continue
            try:
                _, _, _, _, optimized_ir, _ = build_pipeline(source_text)
            except (LexerError, ParserError, SemanticError) as exc:
                print(f"Compilation failed: {exc}")
                continue
            print(f"Running '{optimized_ir['title']}'...\n")
            Interpreter(optimized_ir).run()
            continue
        buffer.append(line)


def main() -> int:
    args = parse_args()
    source_path = args.source

    if args.interactive and source_path is None:
        return repl()

    if source_path is None:
        default_path = Path(__file__).parent / "examples" / "treasure_hunt.rq"
        source_path = str(default_path)

    path = Path(source_path)
    if not path.exists():
        raise SystemExit(f"Source file not found: {path}")

    try:
        source_text = path.read_text(encoding="utf-8")
        tokens, program, symbols, ir, optimized_ir, optimization_stats = build_pipeline(source_text)
    except (LexerError, ParserError, SemanticError) as exc:
        print(f"Compilation failed: {exc}")
        return 1

    if args.debug:
        print_debug(tokens, program, symbols, ir, optimized_ir, optimization_stats)

    if args.output:
        write_output(args.output, optimized_ir)

    if args.run or args.interactive:
        print(f"Running '{optimized_ir['title']}'...\n")
        Interpreter(optimized_ir).run()
    elif not args.output and not args.debug:
        print("Compilation successful.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
