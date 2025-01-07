# About `indent-tools`

Indenti is a Python package with tools that make text indentation and XML/HTML
markup generation easier and more _functional_.

The `indent_tools` package contains the following modules:

-  `text`
    - `IndentWriter`
    - `IndentBuilder`
-  `xml`
    - `Node` -> `Text`, `Comment`, `XML` -> `HTML`
    - `XML`, `XML.Factory`, `XML.Parser`
    - `HTML`, `HTML.Factory`, `HTML.Parser`

# Installation

Installation is simple. With python3-pip, do the following:

```
$ sudo pip install -e .
```

# Documentation
## `text.IndentWriter`
The `IndentWriter` is a class that simplifies the task of indenting output.
It keeps track of indent levels and provides a pythonic way of
incrementing and decrementing the indent level using the optional 'with'
syntax. By default, IndentWriter writes to sys.stdout, but can be told
to write to any other File object at construction.

```python
from indent_tools.text import IndentWriter

iw = IndentWriter()

iw('def hello():')
with iw:
    iw('print "Hello!"')
```

## `text.IndentBuilder`
The `IndentBuilder` is a specialization of the `IndentWriter` which collects
output in an internal `io.StringIO` buffer.  Use `str()` to fetch the contents
of the buffer once you are done building the indented string.

```python
from indent_tools.text import IndentBuilder

sb = IndentBuilder()

sb('def hello():')
with sb:
    sb('print "Hello!"')

print str(sb)
```

## `xml.Node`
This base class represents any node in an XML/HTML DOM.  Use `type()` to
determine which `Node.Type` the node represents:

- `Node.Type.Element`: An XML or HTML element/tag.
- `Node.Type.Text`: Text contents of an XML or HTML element/tag.
- `Node.Type.CDATA`: CDATA blocks, not currently supported.
- `Node.Type.Comment`: An XML/HTML comment block.

## `xml.XML`
A specialization of `Node` for `Node.Type.Element`, this class represents an
XML element/tag and is the main building block of an XML DOM.  Child nodes can
be added using `append()`, `apply()`, or `__call__()`, while attributes can be
specified either as dictionaries or keyword arguments to `apply()` or
`__call__()`.

Use `XML.Factory` to create an XML DOM structure in Python code.  Via
`__getattr__`, any node name can be specified as a method name to construct a
node of that name, and further parameters to `apply()/__call__()` can be
provided to chain construction.

```python
import cherrypy
from indent_tools.xml import XML

class HelloWorld:
    def index(self):
        xf = XML.Factory(html=True)

        xml = xf.html(
            xf.head(
                xf.title("Hello, world!")),
            xf.body(
                xf.h1("Hello, CherryPy!", style='color: red; font-size: 20px')))

        return str(xml)

    index.exposed = True
```

`XML.Parser` can be used to construct a DOM from an XML string using the
built-in `xml.sax` parser:

```python
from indent_tools.xml import XML

parser = XML.Parser()
with open("input.xml", "w") as infile:
    doc = parser.parse(infile.read())
```

## `xml.HTML`
This class is a shorthand specialization of `XML` where HTML mode (`html=True`)
is always true.  Several differences should be noted:

- A `<!DOCTYPE html>` declarative will be emitted before the root element.  To
    disable this, set `doctype=None` in the `HTML` or `HTML.Factory` constructor.
- The `<?xml ...?>` declarative will not be emitted in HTML mode.
- While writing out in HTML mode:
    - Only "void" elements can be specified as
      "open-close" tags, e.g. `<img src="image.png"/>`.  All other tags will be
      given open and close tags regardless of their contents, e.g. `<p></p>`.
        - This applies to `area`, `base`, `br`, `col`, `embed`, `hr`, `img`,
            `input`, `link`, `meta`, `param`, `source`, `track`, and `wbr`.
    - Certain "no-indent" elements will not have
      their contents indented to match the indent level of the output, as this
      would affect their rendered contents.
        - This applies only to `textarea`.
    - "Inline" elements will be written without line breaks so long as their
      contents are all either text nodes or other inline elements.
        - This applies to `a`, `abbr`, `b`, `bdi`, `bdo`, `br`, `cite`, `code`,
            `data`, `dfn`, `em`, `i`, `kdb`, `mark`, `q`, `rp`, `rt`, `ruby`,
            `s`, `samp`, `small`, `strong`, `sub`, `sup`, `time`, `u`, `var`,
            and `wbr`.
- Any attributes with a boolean `True` value will be emitted as HTML boolean
    attributes, i.e. they will not have a value listed, e.g.
    `<button disabled>Disabled Button</button>` if `disabled=True`.
- The `HTML.Parser` uses the more lenient `html.parser`, which allows for
    parsing many malformed documents which would not be valid XML.

## NOTE:
The word 'class' is a python keyword, so we can't use it as a keyword argument
to create an attribute name. In this case, we pass a dictionary, which is
interpreted as a map of attributes for the node, to the `__call__` or `apply`
methods of the `XML` or `HTML` object.  You can always do this instead of using
keyword arguments, if this is your preference.

# Change Log

### Version 2.0: January 6th, 2025
- Major overhaul and modernization, moved packages to `indent_tools` parent package.

### Version 1.4: April 22nd, 2017
- Make XmlFactory callable, allowing tags with dashes, e.g. xf('my-dash-tag')()

### Version 1.2: November 1st, 2016
- Make parents respect the NOINDENT status of their children in HTML mode.

### Version 1.1: October 18th, 2016
- Added support for unindented blocks in HTML mode (for textarea)
- Fixed escaping of XML attributes
