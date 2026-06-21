"""Hand-rolled lexer for BSL.

Dependency-free. Each token records its character span; the parser turns those
into byte spans via `Source`. Keywords are emitted as NAME tokens and
disambiguated by the parser.
"""

from __future__ import annotations

from dataclasses import dataclass


class BSLError(Exception):
    """A lexing, parsing, or checking error with source position."""

    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"{message} (line {line}, col {col})")
        self.message = message
        self.line = line
        self.col = col


@dataclass
class Token:
    kind: str          # "NAME", "NUMBER", "EOF", or the literal punctuation
    value: str
    cstart: int        # char offset (inclusive)
    cend: int          # char offset (exclusive)
    line: int          # 1-based
    col: int           # 1-based


# Single-character punctuation tokens.
_PUNCT = set("{}:+[](),=@")

_NAME_START = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
_NAME_CONT = _NAME_START | set("0123456789")
_DIGITS = set("0123456789")


def tokenize(text: str) -> list[Token]:
    toks: list[Token] = []
    i = 0
    n = len(text)
    line = 1
    col = 1

    def adv(count: int = 1) -> None:
        nonlocal i, line, col
        for _ in range(count):
            if i < n and text[i] == "\n":
                line += 1
                col = 1
            else:
                col += 1
            i += 1

    while i < n:
        ch = text[i]

        # whitespace
        if ch in " \t\r\n":
            adv()
            continue

        # comment to end of line
        if ch == "#":
            while i < n and text[i] != "\n":
                adv()
            continue

        start = i
        sline, scol = line, col

        # arrow
        if ch == "-" and i + 1 < n and text[i + 1] == ">":
            adv(2)
            toks.append(Token("->", "->", start, i, sline, scol))
            continue

        # number: '-'? [0-9]+ ('.' [0-9]+)? ([eE] [+-]? [0-9]+)?
        # Negative literals lex fine; non-negativity is a *physical* invariant
        # enforced by the typechecker, with a message that explains why.
        if ch in _DIGITS or (ch == "-" and i + 1 < n and text[i + 1] in _DIGITS):
            if ch == "-":
                adv()
            while i < n and text[i] in _DIGITS:
                adv()
            if i < n and text[i] == ".":
                adv()
                while i < n and text[i] in _DIGITS:
                    adv()
            if i < n and text[i] in "eE":
                adv()
                if i < n and text[i] in "+-":
                    adv()
                if i >= n or text[i] not in _DIGITS:
                    raise BSLError("malformed exponent in number", sline, scol)
                while i < n and text[i] in _DIGITS:
                    adv()
            toks.append(Token("NUMBER", text[start:i], start, i, sline, scol))
            continue

        # name / keyword
        if ch in _NAME_START:
            while i < n and text[i] in _NAME_CONT:
                adv()
            toks.append(Token("NAME", text[start:i], start, i, sline, scol))
            continue

        # punctuation
        if ch in _PUNCT:
            adv()
            toks.append(Token(ch, ch, start, i, sline, scol))
            continue

        if ch == "-":
            raise BSLError("unexpected '-' (did you mean '->'?)", line, col)

        raise BSLError(f"unexpected character {ch!r}", line, col)

    toks.append(Token("EOF", "", n, n, line, col))
    return toks
