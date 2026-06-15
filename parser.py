from __future__ import annotations

from dataclasses import dataclass

from ast_nodes import (
    BinaryExpression,
    ChoiceStatement,
    Condition,
    EndStatement,
    GotoStatement,
    IfGotoStatement,
    Literal,
    Program,
    RestartStatement,
    Scene,
    SetStatement,
    ShowStatement,
    VarDeclaration,
    VariableReference,
)
from token_defs import Token, TokenType


class ParserError(Exception):
    pass


@dataclass
class Parser:
    tokens: list[Token]

    def __post_init__(self) -> None:
        self.current = 0

    def parse(self) -> Program:
        title = "Untitled RetroQuest"
        variables: list[VarDeclaration] = []
        scenes: list[Scene] = []

        if self._match(TokenType.GAME):
            title = self._consume(TokenType.STRING, "Expected game title string after 'game'").value

        while self._match(TokenType.VAR):
            variables.append(self._parse_var_declaration())

        while not self._check(TokenType.EOF):
            scenes.append(self._parse_scene())

        if not scenes:
            token = self._peek()
            raise ParserError(f"Program must define at least one scene near line {token.line}, column {token.column}")

        return Program(title=title, variables=variables, scenes=scenes)

    def _parse_var_declaration(self) -> VarDeclaration:
        name = self._consume(TokenType.IDENTIFIER, "Expected variable name after 'var'").value
        self._consume(TokenType.ASSIGN, "Expected '=' in variable declaration")
        value = self._parse_expression()
        return VarDeclaration(name=name, value=value)

    def _parse_scene(self) -> Scene:
        self._consume(TokenType.SCENE, "Expected 'scene' or 'def' declaration")
        name = self._consume(TokenType.IDENTIFIER, "Expected scene name").value
        
        # Support optional ()
        if self._match(TokenType.LPAREN):
            self._consume(TokenType.RPAREN, "Expected ')' after '('")
            
        self._consume(TokenType.COLON, "Expected ':' after scene name")
        statements = self._parse_statements()
        return Scene(name=name, statements=statements)

    def _parse_statements(self) -> list:
        statements = []
        while not self._check(TokenType.EOF) and not self._check(TokenType.SCENE):
            if self._match(TokenType.SHOW):
                # Support optional ( for print()
                has_paren = self._match(TokenType.LPAREN)
                value = self._parse_expression()
                if has_paren:
                    self._consume(TokenType.RPAREN, "Expected ')' after expression")
                statements.append(ShowStatement(value=value))
                continue
            if self._match(TokenType.CHOICE):
                text = self._consume(TokenType.STRING, "Expected string after 'choice'").value
                self._consume(TokenType.ARROW, "Expected '->' after choice text")
                target = self._consume(TokenType.IDENTIFIER, "Expected target scene after '->'").value
                statements.append(ChoiceStatement(text=text, target=target))
                continue
            if self._match(TokenType.GOTO):
                target = self._consume(TokenType.IDENTIFIER, "Expected scene name after 'goto'").value
                statements.append(GotoStatement(target=target))
                continue
            if self._match(TokenType.SET):
                name = self._consume(TokenType.IDENTIFIER, "Expected variable name after 'set'").value
                self._consume(TokenType.ASSIGN, "Expected '=' in assignment")
                value = self._parse_expression()
                statements.append(SetStatement(name=name, value=value))
                continue
            if self._match(TokenType.IF):
                condition = self._parse_condition()
                # Make 'then' optional for Pythonic style
                self._match(TokenType.THEN) 
                self._consume(TokenType.GOTO, "Expected 'goto' or 'then goto'")
                target = self._consume(TokenType.IDENTIFIER, "Expected target scene after conditional goto").value
                statements.append(IfGotoStatement(condition=condition, target=target))
                continue
            if self._match(TokenType.END):
                statements.append(EndStatement())
                continue
            if self._match(TokenType.RESTART):
                statements.append(RestartStatement())
                continue
            token = self._peek()
            raise ParserError(f"Unexpected token {token.type.name} near line {token.line}, column {token.column}")
        return statements

    def _parse_condition(self) -> Condition:
        variable = self._consume(TokenType.IDENTIFIER, "Expected variable name in condition").value
        if self._match(TokenType.EQ):
            value = self._parse_expression_value()
            return Condition(variable=variable, operator="==", value=value)
        if self._match(TokenType.NEQ):
            value = self._parse_expression_value()
            return Condition(variable=variable, operator="!=", value=value)
        if self._match(TokenType.GT):
            value = self._parse_expression_value()
            return Condition(variable=variable, operator=">", value=value)
        if self._match(TokenType.LT):
            value = self._parse_expression_value()
            return Condition(variable=variable, operator="<", value=value)
        if self._match(TokenType.GTE):
            value = self._parse_expression_value()
            return Condition(variable=variable, operator=">=", value=value)
        if self._match(TokenType.LTE):
            value = self._parse_expression_value()
            return Condition(variable=variable, operator="<=", value=value)
        return Condition(variable=variable)

    def _parse_expression(self):
        expression = self._parse_term()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous().value
            right = self._parse_term()
            expression = BinaryExpression(left=expression, operator=operator, right=right)
        return expression

    def _parse_term(self):
        expression = self._parse_primary_expression()
        while self._match(TokenType.STAR, TokenType.SLASH):
            operator = self._previous().value
            right = self._parse_primary_expression()
            expression = BinaryExpression(left=expression, operator=operator, right=right)
        return expression

    def _parse_primary_expression(self):
        if self._match(TokenType.STRING):
            return Literal(self._previous().value)
        if self._match(TokenType.NUMBER):
            return Literal(self._previous().value)
        if self._match(TokenType.TRUE, TokenType.FALSE):
            return Literal(self._previous().value)
        if self._match(TokenType.IDENTIFIER):
            return VariableReference(self._previous().value)
        token = self._peek()
        raise ParserError(f"Expected expression near line {token.line}, column {token.column}")

    def _parse_expression_value(self):
        expression = self._parse_expression()
        if isinstance(expression, Literal):
            return expression.value
        if isinstance(expression, VariableReference):
            return {"var": expression.name}
        return expression

    def _match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self._check(token_type):
                self.current += 1
                return True
        return False

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            self.current += 1
            return self._previous()
        token = self._peek()
        raise ParserError(f"{message} near line {token.line}, column {token.column}")

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return token_type == TokenType.EOF
        return self._peek().type == token_type

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF
