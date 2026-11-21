#!/usr/bin/env python3

"""
Hack assembler for Nand to Tetris.

Usage:
python assembler.py input.asm [output.hack]

K = 83
K mod 3 = 2
Feature: Warn when a label is declared more than once.
"""

import sys
import re
from pathlib import Path


# Destination instruction table
DEST = {
    "": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
}


# Jump instruction table
JUMP = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}


# Computation instruction table
COMP = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",

    "D": "0001100",
    "A": "0110000",
    "M": "1110000",

    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",

    "-D": "0001111",
    "-A": "0110011",
    "-M": "1110011",

    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",

    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",

    "D+A": "0000010",
    "D+M": "1000010",

    "D-A": "0010011",
    "D-M": "1010011",

    "A-D": "0000111",
    "M-D": "1000111",

    "D&A": "0000000",
    "D&M": "1000000",

    "D|A": "0010101",
    "D|M": "1010101"
}


# Predefined symbols
PREDEFINED = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576
}

PREDEFINED.update({
    f"R{i}": i for i in range(16)
})


# Remove comments and whitespace
def clean_lines(source):

    result = []

    for number, raw in enumerate(source.splitlines(), 1):

        line = raw.split("//", 1)[0].strip()

        if line:
            result.append(
                (number, re.sub(r"\s+", "", line))
            )

    return result


# Main assembler function
def assemble(source):

    lines = clean_lines(source)

    symbols = dict(PREDEFINED)

    duplicate_labels = []

    rom_address = 0


    # PASS 1: Find labels
    for line_no, line in lines:

        if line.startswith("(") and line.endswith(")"):

            label = line[1:-1]

            if not label or not re.fullmatch(
                r"[A-Za-z_.$:][\w.$:]*", label
            ):
                raise ValueError(
                    f"Line {line_no}: invalid label declaration"
                )

            if label in symbols or label in duplicate_labels:

                print(
                    f"Warning: Line {line_no}: "
                    f"duplicate label '{label}'"
                )

                duplicate_labels.append(label)

            else:

                symbols[label] = rom_address

        else:

            rom_address += 1


    # PASS 2: Generate machine code
    output = []

    next_variable = 16

    for line_no, line in lines:

        if line.startswith("(") and line.endswith(")"):
            continue


        # A-instruction
        if line.startswith("@"):

            value = line[1:]

            if value.isdigit():

                address = int(value)

            else:

                if not re.fullmatch(
                    r"[A-Za-z_.$:][\w.$:]*", value
                ):
                    raise ValueError(
                        f"Line {line_no}: invalid A-instruction '{line}'"
                    )

                if value not in symbols:

                    symbols[value] = next_variable

                    next_variable += 1

                address = symbols[value]


            if not 0 <= address <= 32767:

                raise ValueError(
                    f"Line {line_no}: A-instruction value out of range"
                )

            output.append(
                f"{address:016b}"
            )


        # C-instruction
        else:

            if line.count("=") > 1 or line.count(";") > 1:

                raise ValueError(
                    f"Line {line_no}: invalid C-instruction '{line}'"
                )

            if ";" in line:

                left, jump = line.split(";")

            else:

                left, jump = line, ""


            if "=" in left:

                dest, comp = left.split("=")

            else:

                dest, comp = "", left


            if dest not in DEST:

                raise ValueError(
                    f"Line {line_no}: invalid destination '{dest}'"
                )

            if comp not in COMP:

                raise ValueError(
                    f"Line {line_no}: invalid computation '{comp}'"
                )

            if jump not in JUMP:

                raise ValueError(
                    f"Line {line_no}: invalid jump '{jump}'"
                )


            machine_instruction = (
                "111"
                + COMP[comp]
                + DEST[dest]
                + JUMP[jump]
            )

            output.append(machine_instruction)


    return output, symbols


# Program entry point
def main():

    if len(sys.argv) not in (2, 3):

        print(
            "Usage: python assembler.py input.asm [output.hack]"
        )

        raise SystemExit(2)


    input_path = Path(sys.argv[1])

    if len(sys.argv) == 3:

        output_path = Path(sys.argv[2])

    else:

        output_path = input_path.with_suffix(".hack")


    try:

        machine_code, symbols = assemble(
            input_path.read_text(encoding="utf-8")
        )

        output_path.write_text(
            "\n".join(machine_code) + "\n",
            encoding="utf-8"
        )


        print(
            f"Assembly successful: "
            f"{len(machine_code)} instructions -> {output_path}"
        )

        print("Symbols:")

        for name, address in sorted(symbols.items()):

            if (
                name not in PREDEFINED
                or name in ("SP", "LCL", "ARG", "THIS", "THAT")
            ):

                print(f"  {name}: {address}")


    except (OSError, ValueError) as error:

        print(error)

        raise SystemExit(1)


if __name__ == "__main__":

    main()