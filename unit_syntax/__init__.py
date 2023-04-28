import tokenize
from io import StringIO
from typing import Iterator, Optional, Generator
import pint
from .parser import GeneratedParser
from pegen.tokenizer import Tokenizer
from pprint import pprint

ureg = pint.UnitRegistry(auto_reduce_dimensions=True)


def Quantity(value, units):
    if isinstance(value, ureg.Quantity):
        return value.to(units)
    else:
        return ureg.Quantity(value, units)


VERBOSE = False


def generate_tokens(code: str) -> Iterator[tokenize.TokenInfo]:
    return tokenize.generate_tokens(StringIO(code).readline)


def parse(tokens: Iterator[tokenize.TokenInfo]):
    tok = Tokenizer(tokens, verbose=VERBOSE)
    parser = GeneratedParser(tok, verbose=VERBOSE)
    tree = parser.start()
    if not tree:
        raise parser.make_syntax_error("<input>")
    return tree


Position = tuple[int, int]


class SourcePosQuery:
    """Return source ranges between two (line, column) pairs"""

    def __init__(self, code: str):
        self.code_lines = code.splitlines()
        # The ENDMARKER token points to one line past the end of the file
        self.code_lines.append("")

    def between_pos(self, prev_end: Position, next_start: Position) -> Iterator[str]:
        """returns the text between two tokens"""

        # convert to 0-based indexing because I'm not a maniac
        prev_end = prev_end[0] - 1, prev_end[1]
        next_start = next_start[0] - 1, next_start[1]

        prev_line = self.code_lines[prev_end[0]]
        if prev_end[0] == next_start[0]:
            yield prev_line[prev_end[1] : next_start[1]]
        else:
            yield prev_line[prev_end[1] :]
            yield from self.code_lines[prev_end[0] + 1 : next_start[0]]
            next_line = self.code_lines[next_start[0]]
            yield next_line[: next_start[1]]


class OutputWriter:
    source: SourcePosQuery
    prev_tok_end: Position
    output: list[str]

    def __init__(self, source: SourcePosQuery):
        self.source = source
        self.prev_tok_end = (0, 0)
        self.output = []

    def write_segment(self, lit: str, token: tokenize.TokenInfo, emit_gap=True):
        if emit_gap:
            gap = self.source.between_pos(self.prev_tok_end, token.start)
            self.output.extend(gap)
        if token.end > self.prev_tok_end:
            self.prev_tok_end = token.end
        self.output.append(lit)

    def write_bare(self, lit: str):
        self.output.append(lit)

    def to_string(self) -> str:
        return "".join(self.output)


def first_child(node):
    if isinstance(node, list):
        for n in node:
            if n is not None:
                return first_child(n)
    elif isinstance(node, tokenize.TokenInfo):
        return node
    elif isinstance(node, tuple):
        return first_child(node[1])
    else:
        raise Exception("unknown node: ", node)


def ast_to_segments(node, output: OutputWriter):
    if isinstance(node, list):
        for child in node:
            ast_to_segments(child, output)
    elif isinstance(node, tokenize.TokenInfo):
        output.write_segment(node.string, node)
    elif isinstance(node, tuple) and node[0] == "primary_with_units":
        value_node = node[1]
        units_node = node[2]

        # Gross hack: since we're customizing the output of the units and value
        # retreive the children to direcly update the last token's end position
        first = first_child(node)

        output.write_segment("unit_syntax.Quantity(", first)
        ast_to_segments(value_node, output)
        output.write_bare(', "')
        ast_to_segments(units_node, output)
        output.write_bare('")')
    elif node is None:
        # TODO whats this
        pass
    else:
        raise Exception("unknown node: ", node)


def transform(code: str) -> str:
    tokens = generate_tokens(code)
    tree = parse(tokens)
    source_query = SourcePosQuery(code)
    output = OutputWriter(source_query)
    ast_to_segments(tree, output)
    return output.to_string()


def transform_lines(lines: list[str]) -> list[str]:
    return transform("".join(lines)).splitlines()
