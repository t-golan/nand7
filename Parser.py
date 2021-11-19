"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

ARITHMETICS = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}
COMMAND = 0
ARG1 = 1
ARG2 = 2
C_ARITHMETIC = "C_ARITHMETIC"
COMMANDS_DICT = {'push': "C_PUSH", 'pop': 'C_POP', "label": "C_LABEL",
                 "goto": "C_GOTO", "if": "C_IF", "function": "C_FUNCTION",
                 'return': "C_RETURN", 'call': "C_CALL"}
BLANK = ""
COMMENT_SYMBOL = "//"


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient
    access to their components.
    In addition, it removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.
        Args:
            input_file (typing.TextIO): input file.
        """
        self.lines = input_file.read().splitlines()
        self.length = len(self.lines)
        self.line_idx = -1
        self.cur_line = None
        self.type = None

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?
        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.length - 1 > self.line_idx

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        self.line_idx += 1
        self.cur_line = self.lines[self.line_idx].split()

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        if self.cur_line[COMMAND] in ARITHMETICS:
            self.type = C_ARITHMETIC
        else:
            self.type = COMMANDS_DICT.get(self.cur_line[COMMAND])
        return self.type

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned.
            Should not be called if the current command is "C_RETURN".
        """
        if self.type == C_ARITHMETIC:
            return self.cur_line[COMMAND]
        else:
            return self.cur_line[ARG1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP",
            "C_FUNCTION" or "C_CALL".
        """
        return int(self.cur_line[ARG2])

    def remove_line(self):
        """
        Removes the current line
        """
        del self.lines[self.line_idx]
        self.length -= 1
        self.line_idx -= 1
        # self.cur_line = self.lines[self.line_idx]


    def comments_and_spaces(self) -> bool:
        """
        Remove comments and spaces from the line. is the line is just comment or blank line, remove the line.
        """
        # if the line deleted (comment or empty) returns True, otherwise returns False
        self.lines[self.line_idx] = self.lines[self.line_idx]
        if self.lines[self.line_idx] == BLANK:
            self.remove_line()
            return True
        comment_start_idx = self.lines[self.line_idx].find(COMMENT_SYMBOL)
        if comment_start_idx == 0:
            self.remove_line()
            return True
        elif comment_start_idx > -1:
            self.lines[self.line_idx] = self.lines[self.line_idx][:comment_start_idx]
        return False
