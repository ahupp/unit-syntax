import tokenize
from io import StringIO
from typing import Iterator, Optional, Generator
from .parser import GeneratedParser
from pegen.tokenizer import Tokenizer

Position = tuple[int, int]


class SourcePosQuery:
    """Return source ranges between two (line, column) pairs"""

    def __init__(self, code: str):
        self.code_lines = code.splitlines(keepends=True)
        # The ENDMARKER token points to one line past the end of the file
        self.code_lines.append("")

    def between_pos(self, prev_end: Position, next_start: Position) -> Iterator[str]:
        """returns the text between two tokens, inclusive of prev_end and exclusive of next_start"""

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
        # token lines are 1-indexed
        self.prev_tok_end = (1, 0)
        self.output = []

    def write_segment(self, lit: str, token: tokenize.TokenInfo):
        # pegen rules of the form
        #   '<sep>'.rule
        #  match zero or more instances of `rule`` separated by `sep`, and sep is not included
        # in the resulting tree.  Handle this include any un-emitted preceding text when emitting
        # a token, except when we're actually emitting the translated units expressions.
        gap = self.source.between_pos(self.prev_tok_end, token.start)
        self.output.extend(gap)
        if token.end > self.prev_tok_end:
            self.prev_tok_end = token.end
        self.output.append(lit)

    def write_bare(self, lit: str):
        self.output.append(lit)

    def to_string(self) -> str:
        return "".join(self.output)


def first_token(node):
    """Return the first child token of this node"""
    if isinstance(node, list):
        for n in node:
            if n is not None:
                return first_token(n)
    elif isinstance(node, tokenize.TokenInfo):
        return node
    elif isinstance(node, tuple):
        return first_token(node[1])
    else:
        raise Exception("unknown node: ", node)


def ast_to_segments(node, output: OutputWriter):
    """Given an AST produced by pegen, rewrite unit expressions into standard python and write the
    whole tree as a string back to `output`"""
    if isinstance(node, list):
        for child in node:
            ast_to_segments(child, output)
    elif isinstance(node, tokenize.TokenInfo):
        output.write_segment(node.string, node)
    elif isinstance(node, tuple) and node[0] == "value_with_units":
        value_node = node[1]
        units_node = node[2]

        # sinc we're emitting text that doesn't appear in the input code, we need to manually grab the
        # first token of value node to ensure any preceding text is also emitted before it.
        # e.g, for "(1 meters, 2 meters)", this ensures the comma is emitted *before* the Quantity constructor
        # rather than inside it.
        first = first_token(node)

        output.write_segment("unit_syntax.Quantity(", first)
        ast_to_segments(value_node, output)
        output.write_bare(', "')
        output.prev_tok_end = first_token(units_node).start
        # no need to escape this because the units grammar rule only allows
        # identifiers, parens and math operations
        ast_to_segments(units_node, output)
        output.write_bare('")')
    elif node is None:
        # TODO whats this
        pass
    else:
        raise Exception("unknown node: ", node)


def generate_tokens(code: str) -> Iterator[tokenize.TokenInfo]:
    return tokenize.generate_tokens(StringIO(code).readline)


def parse(tokens: Iterator[tokenize.TokenInfo]):
    VERBOSE = False
    tok = Tokenizer(tokens, verbose=VERBOSE)
    parser = GeneratedParser(tok, verbose=VERBOSE)
    tree = parser.start()
    if not tree:
        raise parser.make_syntax_error("<input>")
    return tree


def transform(code: str) -> str:
    """Transform a string of python-with-units into a standard python string"""
    tokens = generate_tokens(code)
    tree = parse(tokens)
    source_query = SourcePosQuery(code)
    output = OutputWriter(source_query)
    ast_to_segments(tree, output)
    return output.to_string()


def transform_lines(lines: list[str]) -> list[str]:
    """IPython transforms provide a list of strings in the current cell, but to parse correctly we
    need to parse them as a single string"""
    return transform("".join(lines)).splitlines(keepends=True)
