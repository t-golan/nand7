"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

SEGMENTS = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT", "pointer": 3,
            "constant": "CONST", "temp": 5, "static": "STATIC"}
REG_SEGMENTS = {"LCL", "ARG", "THIS", "THAT"}


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.filename = None
        self.output = output_stream
        self.label_counter = 0

    def pop_from_stack(self):
        self.output.write("@SP\n"
                          "M = M - 1\n"
                          "A=M\n"
                          "D=M\n")

    def push_to_stack(self, argToPush):
        self.output.write("@SP\n"
                          "A = M\n"
                          "M = {0}\n"
                          "@SP\n"
                          "M = M+1\n".format(argToPush))

    def check_x(self):
        self.output.write("@X_NEG{0}\n"
                            "D;JLE\n"  #jump if the x less than 0 or equal to 0
                            # otherwise, x greater than 0. now check y:
                            "@R13\n"
                            "D=M\n"
                            "@SAME_SIGN{0}\n"
                            "D;JGT\n"  # jump if the both are positive
                            # else - x positive and y negative, so x-y = positive
                            "D=1\n"
                            "@CHECK_CONDITION{0}\n"
                            "0;JMP\n".format(self.label_counter))

    def x_neg_check_y(self):
        self.output.write("(X_NEG{0})\n"
                            "@R13\n"
                            "D=M\n"
                            "@SAME_SIGN{0}\n"
                            "D;JLE\n"  # jump if the both are negative or equal to 0
                            # else - x negative and y positive, so x-y = negative
                            "D=-1\n"
                            "@CHECK_CONDITION{0}\n"
                            "0;JMP\n".format(self.label_counter))

    def x_y_same_sign(self):
        self.output.write("(SAME_SIGN{0})\n"
                            "@R13\n"
                            "D=M\n"
                            "@R14\n"
                            "D=M-D\n"
                            "@CHECK_CONDITION{0}\n"
                            "0;JMP\n".format(self.label_counter))

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.filename = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        # D = first argument in stack, SP--
        self.pop_from_stack()

        if command == "not":
            self.output.write("D = !D\n")
        elif command == "neg":
            self.output.write("D = -D\n")
        elif command == "shiftleft":
            self.output.write("D = D<<\n")
        elif command == "shiftright":
            self.output.write("D = D>>\n")

        else:  # command in ("add", "sub", "eq", "gt", "lt", "and", "or"):
            self.output.write("@R13\n"  # save Y in R13
                              "M = D\n"
                              "@SP\n"
                              "M = M-1\n"
                              "A = M\n")
            if command == "add":
                self.output.write("D = D+M\n")
            elif command == "sub":
                self.output.write("D = M-D\n")
            elif command == "and":
                self.output.write("D = M&D\n")
            elif command == "or":
                self.output.write("D = M|D\n")
            else:
                self.output.write("D=M\n"  # save X in D
                                    "@R14\n"  # save X in R14
                                    "M=D\n")
                self.check_x()
                self.x_neg_check_y()
                self.x_y_same_sign()

                self.output.write("(CHECK_CONDITION{0})\n"
                                  "@TRUE{0}\n".format(self.label_counter))
                if command == "eq":
                    self.output.write("D;JEQ\n")
                elif command == "gt":
                    self.output.write("D;JGT\n")
                elif command == "lt":
                    self.output.write("D;JLT\n")
                self.output.write("D=0\n"
                                  "@CONTINUE{0}\n"
                                  "0;JMP\n"
                                  "(TRUE{0})\n"
                                  "D=-1\n"
                                  "(CONTINUE{0})\n".format(self.label_counter))

            self.label_counter += 1
        self.push_to_stack("D")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # local, argument, this, and that
        if command == "C_POP":
            if SEGMENTS[segment] in REG_SEGMENTS:
                # SP-
                self.pop_from_stack()
                self.output.write("@R13\nM=D\n")

                # R13 = SEGMENTS[segment] + index (the address)"
                self.output.write("@{0}\n"
                                    "D=A\n" 
                                    "@{1}\n" 
                                    "D=M+D\n"
                                    "@R14\n" 
                                    "M=D\n" 
                                    "@R13\n"
                                    "D=M\n"
                                    "@R14\n"
                                    "A=M\n"
                                    "M=D\n".format(index, SEGMENTS[segment]))

            elif segment == "temp" or segment == "pointer":
                self.pop_from_stack()
                self.output.write("@{0}\n"
                                  "M=D\n".format(SEGMENTS.get(segment) + index))
            elif segment == "static":
                self.pop_from_stack()
                self.output.write("@{0}.{1}\n"
                                  "M=D\n".format(self.filename, index))

        elif command == "C_PUSH":
            if SEGMENTS[segment] == "CONST":
                # D = index
                self.output.write("@{0}\n"
                                  "D = A\n".format(index))
            elif SEGMENTS[segment] in REG_SEGMENTS:
                # D = *(SEGMENTS[segment] + index)"
                self.output.write("@{0}\n"
                                  "D = M\n"
                                  "@{1}\n"
                                  "A = A+D\n"
                                  "D = M\n".format(SEGMENTS[segment], index))

            elif segment == "temp" or segment == "pointer":
                self.output.write("@{0}\n"
                                  "D=M\n".format(SEGMENTS.get(segment) + index))

            elif segment == "static":
                self.output.write("@{0}.{1}\n"
                                  "D = M\n".format(self.filename, index))

            self.push_to_stack("D")

    def close(self) -> None:
        """Closes the output file."""
        self.output.close()

