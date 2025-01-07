# -------------------------------------------------------------------
# indent_tools.py: Tools for printing code strings,
#                  XML markup, and other indented text.
#
# `indent_tools` is a module that simplifies the task of indenting output.  It
# keeps track of indent levels and provides a pythonic way of incrementing and
# decrementing the indent level using the optional 'with' syntax.
#
# Makes clever use of the semantics of the Python 2.5+ "with" statement to
# allow indented generator code to indent along with its indented output.  This
# allows generator code to look much cleaner.
#
# (c) 2011-2016, 2025 Lain Musgrove (lain_proliant)
# Released under the MIT License.
# -------------------------------------------------------------------
