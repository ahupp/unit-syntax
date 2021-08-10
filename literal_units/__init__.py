import tokenize
from io import StringIO
import token
import pint

from typing import Generator, List, Tuple
from collections.abc import Callable
from collections.abc import Iterable

ureg = pint.UnitRegistry(auto_reduce_dimensions=True)

def Quantity(value, units):
  return ureg.Quantity(value, units)

def maybe_find_units(tokens: List[tokenize.TokenInfo], start_idx: int) -> List[tokenize.TokenInfo]:
  "find the longest valid units expression starting at start_idx. "
  "Returns the list of tokens, or None if none is found."

  end_idx = start_idx + 1
  prev_tok = None
  valid_unit_tokens = None
  while end_idx <= len(tokens):
    last_tok = tokens[end_idx - 1]

    is_power = (
        last_tok.type == token.NUMBER and
        prev_tok is not None and
        prev_tok.type == token.OP and
        prev_tok.string in ('**','^')
    )
    is_name = last_tok.type == token.NAME
    is_unit_op = last_tok.type == token.OP and last_tok.string in (
      '/', '*', '**', '^'
    )

    is_possibly_unit = is_power or is_name or is_unit_op
    if not is_possibly_unit:
      break

    toks = tokens[start_idx:end_idx]
    exp = tokenize.untokenize(toks).strip()
    try:
      ureg.parse_units(exp)
      valid_unit_tokens = toks
    except:
      pass
    prev_tok = last_tok
    end_idx += 1
  return valid_unit_tokens


def generate_tokens(code: str) -> Generator[tokenize.TokenInfo, None, None]:
  sio = StringIO(code)
  return tokenize.generate_tokens(sio.readline)

def transform_inner(code: str) -> str:
  tokens = list(generate_tokens(code))

  i = 0
  while i < len(tokens):
    tok = tokens[i]
    i += 1
    if tok.type == token.NUMBER:
      # see if its followed by a valid unit expression
      unit_exp_tokens = maybe_find_units(tokens, i)
      if unit_exp_tokens is not None:
        i += len(unit_exp_tokens)
        unit_exp = tokenize.untokenize(unit_exp_tokens).strip()
        quantity = "literal_units.Quantity({}, '{}')".format(tok.string, unit_exp)
        for j in generate_tokens(quantity):
          yield j
      else:
        yield tok
    else:
      yield tok


def transform(code: str) -> str:
  return tokenize.untokenize(i[:2] for i in transform_inner(code))

def transform_lines(lines: Iterable[str]) -> List[str]:
  return map(transform, lines)

if __name__ == "__main__":
  tests = [
    "1 meter/s**2",
    "1 meter",
    "1 meter/s^2",
    "1 meter/s * 1 second",
    "2**4 meters",
    # TODO
    "x meters",
  ]
  for i in tests:
    print(i, "->", transform(i))
else:
  import IPython
  ip = IPython.get_ipython()
  if hasattr(ip, 'input_transformers_cleanup'):
    ip.input_transformers_cleanup.append(transform_lines)
  else:
    # support IPython 5, which is used in Google Colab
    # https://ipython.org/ipython-doc/3/config/inputtransforms.html
    from IPython.core.inputtransformer import StatelessInputTransformer

    @StatelessInputTransformer.wrap
    def fn(line):
      return transform(line)

    ip.input_splitter.logical_line_transforms.append(fn())
    ip.input_transformer_manager.logical_line_transforms.append(fn())





