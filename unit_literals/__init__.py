import tokenize
from io import StringIO
import pint
from pprint import pprint
from .parser import GeneratedParser
from .pegen_tokenizer import Tokenizer

ureg = pint.UnitRegistry(auto_reduce_dimensions=True)

def Quantity(value, units):
  if isinstance(value, ureg.Quantity):
    return value.to(units)
  else:
    return ureg.Quantity(value, units)

VERBOSE = False

def generate_tokens(code: str):
    file = StringIO(code)
    return tokenize.generate_tokens(file.readline)

def parse(code: str):
    tokens = generate_tokens(code)
    tokenizer = Tokenizer(tokens, verbose=VERBOSE)
    parser = GeneratedParser(tokenizer, verbose=VERBOSE)
    tree = parser.start()
    if not tree:
      err = parser.make_syntax_error("<input>")
      raise err
    return tree

def print_to_pos(text: str):
  it = iter(text)
  cur_row, cur_col = 1, 0
  def inner(pos):
    nonlocal cur_row, cur_col

    while (cur_row, cur_col) < pos:
      try:
        c = next(it)
        if c == "\n":
          cur_row += 1
          cur_col = 0
        else:
          cur_col += 1
        yield c
      except StopIteration:
        return
  return inner

def ast_to_segments(node, printfn):
  if isinstance(node, list):
    for t in node:
      yield from ast_to_segments(t, printfn)
  elif isinstance(node, tokenize.TokenInfo):
    yield from printfn(node.end)
  elif isinstance(node, tuple) and node[0] == 'unit_atom':
    yield "unit_literals.Quantity("
    yield from ast_to_segments(node[1], printfn)
    yield ", \""
    yield from ast_to_segments(node[2], printfn)
    yield "\")"

def transform(code: str) -> str:
  tree = parse(code)
  printfn = print_to_pos(code)
  return "".join(ast_to_segments(tree, printfn))

def transform_lines(lines):
  print("transform_lines", lines)
  a = transform("".join(lines)).splitlines()
  print("out", a)
  return a

def hook_ipython():
  import IPython
  ip = IPython.get_ipython()
  if hasattr(ip, 'input_transformers_post'):
    print("hooking new ip")
    ip.input_transformers_post.append(transform_lines)
  else:
    print("hooking ip 5")
    # support IPython 5, which is used in Google Colab
    # https://ipython.org/ipython-doc/3/config/inputtransforms.html
    from IPython.core.inputtransformer import StatelessInputTransformer

    @StatelessInputTransformer.wrap
    def fn(line):
      return transform(line)

    ip.input_splitter.logical_line_transforms.append(fn())
    ip.input_transformer_manager.logical_line_transforms.append(fn())

