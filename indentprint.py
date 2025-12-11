import builtins

class IndentPrint:
    def __init__(self, count = 1, placeholder = "  "):
        self._indent_ = placeholder * count
        self._print_ = print
    def __enter__(self):
        builtins.print = lambda *a, **k: self._print_(self._indent_, *a, **k)

    def __exit__(self, *exc):
        builtins.print = self._print_