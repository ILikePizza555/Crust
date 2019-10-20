"""Defines the exceptions used by the preprocessor module."""


class PreprocessorSyntaxError(Exception):
    def __init__(self, line_number, column_number, message):
        self.line_number = line_number
        self.column_number = column_number
        self.message = message

    def __str__(self):
        return f"Syntax error on line {self.line_number}, {self.column_number}: {self.message}"


class UnexpectedTokenError(Exception):
    """Thrown when the preprocessor encounters an unexpected token"""
    def __init__(self, unexpected_token, expected_set):
        self.unexpected_token = unexpected_token
        self.expected_set = expected_set

    def __str__(self):
        return f"Unexpected token {self.unexpected_token.error_str}. Expected one of {self.expected_set}"


class UnknownPreprocessorDirectiveError(Exception):
    def __init__(self, line_number: int, directive: str):
        self.line_number = line_number
        self.directive = directive

    def __str__(self):
        return f"Unknown directive on line {self.line_number}, '{self.directive}'."


class UnknownTokenError(Exception):
    """Exception thrown when an unknown token is encountered during tokenization"""
    def __init__(self, line_number: int, column_number: int, token: str):
        self.line_number = line_number
        self.column_number = column_number
        self.token = token

    def __str__(self):
        return f"Unknown token \"{self.token}\" on line {self.line_number}: {self.column_number}"
