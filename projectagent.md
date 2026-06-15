# Project Agent Guide

## Project Name
RetroQuest

## Course Context
FAST-NUCES, CS4031 - Compiler Construction, Spring 2026

## Project Overview
RetroQuest ek domain-specific language (DSL) hai jo text-based interactive adventure games banane ke liye design ki ja rahi hai. Is language ka goal yeh hai ke user simple syntax ke through scenes, choices, variables, inventory items, aur endings define kar sake. Compiler iska source code read karega, usay validate karega, aur phir ek structured story graph / intermediate representation generate karega jo command-line interpreter par run ho sake.

## Main Objective
Proposal ke mutabiq project ka core target yeh hai:

1. `.rq` source file ko parse karna
2. lexical, syntax, aur semantic analysis perform karna
3. story ko graph-based IR mein convert karna
4. command-line interpreter ke through game ko execute karna
5. debug mode dena jahan tokens, AST, symbol table, aur IR show ho

## Language Features To Implement
Proposal ke mutabiq RetroQuest mein yeh features honi chahiye:

1. `game "Title"` ke through game title define karna
2. `var` ke through variables / flags declare karna
3. `scene name:` ke through story scenes define karna
4. `show "text"` ke through output text display karna
5. `choice "text" -> target_scene` ke through branching choices
6. `goto scene_name` ke through direct jump
7. `set variable = value` ke through state update
8. `if condition then goto scene_name` ke through conditional branching
9. `end` ke through game termination
10. optional restart / replay support

## Required Compiler Modules

### 1. Lexer
Lexer ka kaam:

1. source file ko character by character read karna
2. keywords identify karna:
   `game`, `var`, `scene`, `show`, `choice`, `goto`, `set`, `if`, `then`, `end`
3. identifiers, strings, booleans, operators, arrows, colon, aur assignment tokens banana
4. invalid characters par lexical error dena

### 2. Parser
Parser ka kaam:

1. grammar ke mutabiq token stream parse karna
2. AST ya parse tree generate karna
3. scene blocks aur statements ki structure validate karna
4. syntax errors with line numbers report karna

### 3. Semantic Analyzer
Semantic analysis ka kaam:

1. duplicate variable declarations detect karna
2. duplicate scene labels detect karna
3. undefined scenes par error dena
4. undefined variables par error dena
5. type validity check karna, for example boolean variable ko invalid value assign na ho
6. story control flow sanity check karna

### 4. IR / Story Graph Generator
IR generator ka kaam:

1. har scene ko graph node mein convert karna
2. choices aur gotos ko graph edges mein convert karna
3. conditions ko branch rules ke form mein store karna
4. final IR ko JSON ya internal object structure mein represent karna

### 5. Interpreter / Virtual Machine
Interpreter ka kaam:

1. story graph ko load karna
2. current scene execute karna
3. text show karna
4. user se input lena for choices
5. variables / flags update karna
6. winning, losing, aur ending states handle karna

### 6. Debug Mode
Debug mode mein yeh outputs available hon:

1. tokens list
2. parse tree ya AST
3. symbol table
4. intermediate representation / story graph

## Suggested Project Structure
```text
CC/
├── projectagent.md
├── main.py
├── lexer.py
├── parser.py
├── ast_nodes.py
├── semantic_analyzer.py
├── ir_generator.py
├── interpreter.py
├── utils.py
├── examples/
│   ├── treasure_hunt.rq
│   └── sample_errors.rq
└── output/
    └── story.json
```

## Suggested Workflow

### Phase 1 - Language Design

1. final syntax decide karo
2. grammar likho
3. token list define karo
4. sample `.rq` programs banao

### Phase 2 - Lexer Development

1. token classes banao
2. source scanning implement karo
3. strings, identifiers, keywords, operators handle karo
4. test cases likho

### Phase 3 - Parser Development

1. grammar implement karo
2. AST nodes define karo
3. scene blocks parse karo
4. choices, conditions, aur statements parse karo
5. syntax error handling improve karo

### Phase 4 - Semantic Analysis

1. symbol table banao
2. variables aur scenes register karo
3. undefined references check karo
4. duplicate declarations detect karo

### Phase 5 - IR Generation

1. story graph model define karo
2. AST ko graph mein convert karo
3. graph serialization JSON mein support karo

### Phase 6 - Interpreter

1. graph execute karne wala engine banao
2. user input based choice selection implement karo
3. variable state maintain karo
4. win/lose/end states display karo

### Phase 7 - Debugging and Testing

1. `--debug` option add karo
2. tokens print mode banao
3. AST print mode banao
4. semantic errors ke sample files banao
5. multiple stories run karke testing karo

### Phase 8 - Final Demo Preparation

1. ek clean sample game ready rakho
2. compiler pipeline demo prepare karo
3. live interpreter execution demo ready rakho
4. report aur slides complete karo

## Task Breakdown For Team

### Member 1 - Frontend of Compiler

1. lexer implement kare
2. token definitions banaye
3. parser ki base grammar likhe
4. syntax error reporting handle kare

### Member 2 - Semantic and IR

1. symbol table implement kare
2. semantic checks banaye
3. AST se story graph generate kare
4. JSON export support kare

### Member 3 - Runtime and Testing

1. interpreter / VM banaye
2. CLI arguments handle kare
3. debug mode integrate kare
4. example stories aur test cases banaye

## Command Line Goals
Proposal ke mutabiq interface kuch is tarah hona chahiye:

```text
python main.py story.rq -o story.json
python main.py story.rq --debug
python main.py --interactive
```

## Minimum Deliverables

1. RetroQuest language grammar
2. working lexer
3. working parser
4. semantic analyzer
5. graph/IR generation
6. command-line interpreter
7. debug mode
8. kam az kam 2 sample `.rq` programs
9. final documentation and demo

## Risks / Challenges
Proposal ke hisaab se sab se important challenges yeh hain:

1. grammar ko ambiguous hone se bachana
2. scenes aur branches ko correctly validate karna
3. undefined labels aur invalid variables detect karna
4. branching logic ko easy-to-run graph mein convert karna

## Success Criteria
Project successful tab samjha jayega jab:

1. `.rq` file bina crash ke parse ho
2. invalid programs par proper errors milen
3. valid story graph generate ho
4. interpreter story ko playable bana de
5. debug mode compiler phases ka output show kare

## Recommended Next Step
Sab se pehle team ko yeh 4 cheezein freeze karni chahiye:

1. exact grammar
2. token set
3. AST design
4. story graph structure

Us ke baad implementation lexer se start karni chahiye.
