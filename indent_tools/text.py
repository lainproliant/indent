# --------------------------------------------------------------------
# text.py
#
# Author: Lain Musgrove (lain.proliant@gmail.com)
# Date: Monday January 6, 2025
# --------------------------------------------------------------------
import io
import sys
from dataclasses import dataclass, replace
from typing import Any, TextIO, cast, no_type_check


# --------------------------------------------------------------------
@dataclass
class IndentOptions:
    char: str = " "
    width: int = 4
    enabled: bool = True

    @classmethod
    @no_type_check
    def get(cls) -> "IndentOptions":
        if cls._INSTANCE is None:
            cls._INSTANCE = IndentOptions()
        return cls


IndentOptions._INSTANCE = None  # type: ignore


# --------------------------------------------------------------------
class IndentWriter:
    def __init__(
        self,
        outfile: TextIO = sys.stdout,
        options: IndentOptions | None = None,
        level=0,
    ):
        self._outfile = outfile
        self._options = options or IndentOptions.get()
        self._indent_level = level
        self._is_indent_applied = False
        self._line_number = 0

    def _write_indentation(self) -> int:
        nbytes = 0
        if not self._is_indent_applied and self._options.enabled:
            nbytes = self._outfile.write(
                self._options.char * self._indent_level * self._options.width
            )
            self._is_indent_applied = True
        return nbytes

    @property
    def options(self) -> IndentOptions:
        return self._options

    @property
    def line_number(self) -> int:
        return self._line_number

    def write(self, obj: Any) -> int:
        nbytes = 0
        s = str(obj)
        lines = s.split("\n")
        for n, line in enumerate(lines):
            if n > 0:
                nbytes += self.newline()
            if len(line) > 0:
                nbytes += self._write_indentation()
                nbytes += self._outfile.write(line)
        return nbytes

    def writeln(self, obj: Any):
        return self.write(str(obj) + "\n")

    def newline(self) -> int:
        nbytes = self._outfile.write("\n")
        self._is_indent_applied = False
        self._line_number += 1
        return nbytes

    def __call__(self, output: str = "") -> int:
        return self.writeln(output)

    def indent(self):
        self._indent_level += 1

    def unindent(self):
        self._indent_level -= 1

    def __enter__(self):
        self.indent()

    def __exit__(self, exc_type, exc_val, exc_traceback):
        self.unindent()


# --------------------------------------------------------------------
class IndentBuilder(IndentWriter):
    def __init__(self, options: IndentOptions | None = None, level=0):
        super().__init__(io.StringIO(), options, level)

    def __str__(self):
        return cast(io.StringIO, self._outfile).getvalue()
