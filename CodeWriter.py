"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

SEGMENTS = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT", "pointer 0": "R3", "pointer 1": "R4",
            "constant": "CONST", "temp": "TEMP"}
REG_SEGMENTS = {"LCL", "ARG", "THIS", "THAT", "TEMP"}


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output = output_stream
        # Your code goes here!
        pass

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        pass

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given 
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        # D = first argument in stack, SP--
        self.output.write("@SP\nA = M\nD = M\n@SP\nM = M - 1\n")

        if command == "not":
            self.output.write("D = !D\n")
        elif command == "neg":
            self.output.write("D = -D\n")

        else:  # command in ("add", "sub", "eq", "gt", "lt", "and", "or"):
            # M = the next argument in stack
            "@SP\nA = M\n"
            if command == "add":
                "D = D + M\n"
            elif command == "sub":
                "D = M - D\n"
            elif command == "eq":
                "D = M - D\nD = !D\n"
            elif command == "gt":
                "D = M - D\n"  #################
            elif command == "lt":
                "D = M - D\n"  #####################
            elif command == "and":
                "D = M&D\n"
            elif command == "or":
                "D = M|D\n"

        # push D to the stack, SP++
            self.output.write("@SP\nA = M\nM = D\n@SP\nM = M + 1\n")


    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        if command == "C_POP":
            if SEGMENTS[segment] in REG_SEGMENTS:
                # addr = SEGMENTS[segment] + index (the address)"
                "@{0}\nD = {1}\nD = D + A\n".format(SEGMENTS[segment], index)
                # SP--
                "A = SP\nM = M - 1\n"
                # "*addr = *SP"   ##########################################
                "@D\nM = "
                "A = M\n"


        elif command == "C_PUSH":
            if SEGMENTS[segment] in REG_SEGMENTS:
                # D = *(SEGMENTS[segment] + index)"
                self.output.write("@{0}\nD = A\n@{1}\nA = A + D\nA = M\nD = M\n".format(SEGMENTS[segment], index))
            elif SEGMENTS[segment] == "CONST":
                # D = index
                self.output.write("@{0}\nD = A\n".format(index))

            # *SP = D
            "@SP\nA = M\nM = D\n"
            # SP++
            "@SP\nM = M + 1\n"


    def close(self) -> None:
        """Closes the output file."""
        # Your code goes here!
        pass
