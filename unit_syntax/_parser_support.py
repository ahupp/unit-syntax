"""CPython string semantics and UTF-8 source locations for the PEG parser."""

import ast
import sys


def type_parameter(parser, kind, name, bound, default, **locations):
    if sys.version_info < (3, 12):
        return object()
    arguments = {"name": name, **locations}
    if kind == "TypeVar":
        arguments["bound"] = bound
    if sys.version_info >= (3, 13):
        arguments["default_value"] = default
    return getattr(ast, kind)(**arguments)


def source_lines(source):
    # Tokenization advances on LF, not Unicode separators inside strings.
    parts = source.split("\n")
    return [line + "\n" for line in parts[:-1]] + parts[-1:]


def utf8_locations(tree, source):
    lines = source_lines(source)
    for node in ast.walk(tree):
        for line_attr, column_attr in (
            ("lineno", "col_offset"),
            ("end_lineno", "end_col_offset"),
        ):
            line = getattr(node, line_attr, None)
            column = getattr(node, column_attr, None)
            if line and column is not None and line <= len(lines):
                setattr(
                    node, column_attr, len(lines[line - 1][:column].encode("utf-8"))
                )
    return tree


def character_locations(tree, source):
    """Convert native AST byte columns back to PEG character columns."""
    lines = source_lines(source)
    for node in ast.walk(tree):
        for line_attr, column_attr in (
            ("lineno", "col_offset"),
            ("end_lineno", "end_col_offset"),
        ):
            line = getattr(node, line_attr, None)
            column = getattr(node, column_attr, None)
            if line and column is not None:
                encoded = lines[line - 1].encode("utf-8")
                setattr(node, column_attr, len(encoded[:column].decode("utf-8")))
    return tree


def formatted_field(node, debug):
    node._unit_syntax_debug = debug
    return node


def interpolated_string(parser, start, parts, end):
    """Let CPython decode strings, then restore the already-parsed unit ASTs.

    Mask only replacement expressions, preserving every character position.
    CPython handles escapes, debug labels, and template interpolation metadata.
    No expression is evaluated, and the original expression ASTs are retained.
    """
    source = parser.source
    lines = source_lines(source)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))

    def offset(position):
        return offsets[position[0] - 1] + position[1]

    begin, finish = offset(start.start), offset(end.end)
    replacements = {}
    edits = []
    for part in parts:
        for node in ast.walk(part):
            if not isinstance(node, ast.FormattedValue):
                continue
            value = node.value
            a = offset((value.lineno, value.col_offset))
            b = offset((value.end_lineno, value.end_col_offset))
            # A nested formatted string belongs to its containing expression.
            if any(left <= a and b <= right for left, right, _ in edits):
                continue
            edits.append(
                (
                    a,
                    b,
                    "0"
                    + "".join("\n" if c == "\n" else " " for c in source[a + 1 : b]),
                )
            )
            replacements[(value.lineno, value.col_offset)] = (value, node)

    masked = source[begin:finish]
    for a, b, text in sorted(edits, reverse=True):
        masked = masked[: a - begin] + text + masked[b - begin :]
    tree = ast.parse(masked, filename=parser.filename, mode="eval").body
    masked_lines = source_lines(masked)
    # Native AST columns are bytes; the PEG tree uses character columns until
    # parse_string's final, shared conversion to CPython UTF-8 coordinates.
    for node in ast.walk(tree):
        for line_attr, column_attr in (
            ("lineno", "col_offset"),
            ("end_lineno", "end_col_offset"),
        ):
            line = getattr(node, line_attr, None)
            column = getattr(node, column_attr, None)
            if line and column is not None:
                text = masked_lines[line - 1]
                char_column = len(text.encode("utf-8")[:column].decode("utf-8"))
                setattr(
                    node,
                    column_attr,
                    char_column + (start.start[1] if line == 1 else 0),
                )
                setattr(node, line_attr, line + start.start[0] - 1)

    class Restore(ast.NodeTransformer):
        def visit_JoinedStr(self, node):
            return self.restore_parts(node)

        def visit_TemplateStr(self, node):
            return self.restore_parts(node)

        def restore_parts(self, node):
            for i, part in enumerate(node.values):
                if not isinstance(
                    part,
                    (
                        ast.FormattedValue,
                        getattr(ast, "Interpolation", ast.FormattedValue),
                    ),
                ):
                    continue
                original = replacements.get((part.value.lineno, part.value.col_offset))
                if original:
                    value, old_field = original
                    if getattr(old_field, "_unit_syntax_debug", None):
                        a = offset((value.lineno, value.col_offset))
                        b = offset((value.end_lineno, value.end_col_offset))
                        label = source[a:b]
                        masked_label = masked[a - begin : b - begin]
                        if i and isinstance(node.values[i - 1], ast.Constant):
                            previous = node.values[i - 1]
                            at = previous.value.rfind(masked_label)
                            if at >= 0:
                                previous.value = (
                                    previous.value[:at]
                                    + label
                                    + previous.value[at + len(masked_label) :]
                                )
                    part.value = value
                    if isinstance(part, getattr(ast, "Interpolation", ())):
                        a = offset((value.lineno, value.col_offset))
                        b = offset((value.end_lineno, value.end_col_offset))
                        masked_expression = masked[a - begin : b - begin]
                        # Python 3.14 drops trailing field whitespace from str;
                        # 3.15 retains it. Restore the expression in either form.
                        if masked_expression not in part.str:
                            masked_expression = masked_expression.rstrip()
                        part.str = part.str.replace(masked_expression, source[a:b], 1)
                if part.format_spec:
                    self.visit(part.format_spec)
            return node

    return Restore().visit(tree)


def concatenate_templates(parts):
    values = []
    for part in parts:
        for value in part.values:
            if (
                values
                and isinstance(values[-1], ast.Constant)
                and isinstance(value, ast.Constant)
            ):
                values[-1].value += value.value
            else:
                values.append(value)
    template_type = getattr(ast, "TemplateStr", None)
    if template_type is None:
        raise SyntaxError("Template strings require Python 3.14 or newer")
    result = ast.copy_location(template_type(values=values), parts[0])
    result.end_lineno, result.end_col_offset = (
        parts[-1].end_lineno,
        parts[-1].end_col_offset,
    )
    return result
