# RetroQuest Language Reference Manual

## 1. Overview
RetroQuest is a small DSL for building retro-style text adventures. Programs define scenes, choices, variables, and branching logic. The compiler translates source code into an intermediate story graph which can be executed by the RetroQuest interpreter.

## 2. File Extension
`.rq`

## 3. Lexical Grammar

### Keywords
`game`, `var`, `scene`, `show`, `choice`, `goto`, `set`, `if`, `then`, `end`, `restart`, `true`, `false`

### Token Categories
- Identifier: `[A-Za-z_][A-Za-z0-9_]*`
- String literal: `"..."` with support for escaped characters
- Number literal: `[0-9]+`
- Boolean literal: `true | false`
- Assignment operator: `=`
- Comparison operators: `==`, `!=`
- Arrow operator: `->`
- Colon: `:`
- Comment: `#` until end of line

## 4. Syntax Specification (EBNF)
```text
<program>         ::= [<game_decl>] {<var_decl>} {<scene_decl>}
<game_decl>       ::= "game" <string>
<var_decl>        ::= "var" <identifier> "=" <expr>
<scene_decl>      ::= "scene" <identifier> ":" {<statement>}

<statement>       ::= <show_stmt>
                    | <choice_stmt>
                    | <goto_stmt>
                    | <set_stmt>
                    | <if_goto_stmt>
                    | <end_stmt>
                    | <restart_stmt>

<show_stmt>       ::= "show" <string>
<choice_stmt>     ::= "choice" <string> "->" <identifier>
<goto_stmt>       ::= "goto" <identifier>
<set_stmt>        ::= "set" <identifier> "=" <expr>
<if_goto_stmt>    ::= "if" <condition> "then" "goto" <identifier>
<end_stmt>        ::= "end"
<restart_stmt>    ::= "restart"

<condition>       ::= <identifier>
                    | <identifier> "==" <expr>
                    | <identifier> "!=" <expr>

<expr>            ::= <string> | <number> | <boolean> | <identifier>
<identifier>      ::= letter {letter | digit | "_"}
<string>          ::= '"' {character} '"'
<number>          ::= digit {digit}
<boolean>         ::= "true" | "false"
```

## 5. Type System
RetroQuest uses a simple dynamic value model.

Supported values:
- string
- integer
- boolean

Semantic rules:
- A variable must be declared before it is used
- A scene must be declared before it can be a valid target
- `start` scene is required as the entry point
- Duplicate variable names are not allowed
- Duplicate scene names are not allowed

## 6. Memory Model
- Global variables only
- No nested scopes in the current version
- Variables are stored in a global symbol table
- The interpreter maintains a runtime variable store
- `restart` resets runtime variables to their initial compiled values

## 7. Error Handling Strategy
RetroQuest reports:
- lexical errors with line and column
- parser errors with line and column
- semantic errors for:
  - undefined variables
  - undefined scenes
  - duplicate declarations
  - missing `start` scene

## 8. Intermediate Representation
The compiler emits a custom JSON story graph:
- `title`
- `variables`
- `scenes`
- `entry_scene`

Each scene contains a list of statements such as `ShowStatement`, `ChoiceStatement`, `GotoStatement`, and `IfGotoStatement`.

## 9. Optimization Strategy
Implemented optimizations:
- constant folding and propagation
- unreachable code elimination after `goto`, `end`, `restart`, or resolved branches
- unreachable scene elimination after control-flow analysis

## 10. Example Programs

### Example 1: Treasure Hunt
```text
game "Treasure Hunt"

var has_key = false

scene start:
show "You wake up in a dark room."
choice "Open the wooden chest" -> chest
choice "Try the locked door" -> door

scene chest:
show "Inside the chest you find a rusty key."
set has_key = true
goto start

scene door:
if has_key then goto freedom
show "The door is locked."
end

scene freedom:
show "You unlock the door and escape. You win!"
end
```

Expected output:
- If the player opens the chest first, the key is set and the `freedom` scene becomes reachable.

### Example 2: Fixed Ending
```text
game "Fixed Ending"

var open_gate = true

scene start:
if open_gate then goto ending
show "This line is removed by optimization."
end

scene ending:
show "The gate is already open."
end
```

Expected output:
- Optimizer folds the condition and removes unreachable statements.

### Example 3: Restart Demo
```text
game "Restart Demo"

var seen_intro = false

scene start:
if seen_intro then goto done
show "First run only."
set seen_intro = true
restart

scene done:
show "You reached the second pass."
end
```

Expected output:
- On the first execution the intro appears and the story restarts.

