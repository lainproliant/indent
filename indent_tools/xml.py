# --------------------------------------------------------------------
# xml.py
#
# Author: Lain Musgrove (lain.proliant@gmail.com)
# Date: Monday January 6, 2025
# --------------------------------------------------------------------

from dataclasses import dataclass, field, replace
from enum import StrEnum, auto
from html.entities import name2codepoint as name_to_codepoint
from html.parser import HTMLParser
from typing import Any, Callable, Generator, Generic, Iterable, TypeVar, cast
from xml.sax import parseString as xml_parse
from xml.sax.handler import ContentHandler as XMLParser
from xml.sax.saxutils import escape as xml_escape
from xml.sax.saxutils import quoteattr as attr_escape

from indent_tools.text import IndentBuilder, IndentOptions

# --------------------------------------------------------------------
T = TypeVar("T")

HTML_VOID_ELEMENTS = set(
    [
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    ]
)

HTML_NOINDENT_ELEMENTS = set(["textarea"])

HTML_INLINE_ELEMENTS = set(
    [
        "a",
        "abbr",
        "b",
        "bdi",
        "bdo",
        "br",
        "cite",
        "code",
        "data",
        "dfn",
        "em",
        "i",
        "kdb",
        "mark",
        "q",
        "rp",
        "rt",
        "ruby",
        "s",
        "samp",
        "small",
        "span",
        "strong",
        "sub",
        "sup",
        "time",
        "u",
        "var",
        "wbr",
    ]
)


# --------------------------------------------------------------------
class ParserMixin(Generic[T]):
    def __init__(self, *args, **kwargs):
        self.results: list[T] = []
        self.stack: list[T] = []

    @property
    def current(self) -> T | None:
        return self.stack[-1] if len(self.stack) > 0 else None

    def push(self, item: T):
        self.stack.append(item)

    def pop(self):
        self.stack.pop()

    def add_result(self, item: T):
        self.results.append(item)

    def finalize(self) -> list[T]:
        results = self.results
        self.results = []
        self.stack = []
        return results

    def parse(self, data: str) -> list[T]:
        raise NotImplementedError()

    def parse_one(self, data: str) -> T:
        results = self.parse(data)
        if len(results) < 1:
            raise ValueError("No document was parsed from the given input.")
        return results[0]


# --------------------------------------------------------------------
class Node:
    class Type(StrEnum):
        Element = "Element"
        Text = "Text"
        CDATA = "CDATA"
        Comment = "Comment"

    def __init__(self):
        self.parent: Node | None = None

    @property
    def is_inline(self) -> bool:
        return False

    @property
    def is_root(self) -> bool:
        return self.parent is None

    @property
    def is_last(self) -> bool:
        return self.parent is None or self == cast(XML, self.parent).last

    @property
    def type(self) -> "Node.Type":
        raise NotImplementedError()

    def write_sb(self, sb: IndentBuilder | None = None) -> IndentBuilder:
        raise NotImplementedError()


# --------------------------------------------------------------------
class Text(Node):
    def __init__(self, text: str):
        super().__init__()
        self._text = text

    @property
    def type(self) -> Node.Type:
        return Node.Type.Text

    @property
    def is_inline(self) -> bool:
        return True

    @property
    def text(self) -> str:
        return self._text

    def write_sb(self, sb: IndentBuilder | None = None) -> IndentBuilder:
        sb = sb or IndentBuilder()
        sb.write(xml_escape(self.text).strip())
        return sb


# --------------------------------------------------------------------
class Comment(Node):
    def __init__(self, comment: str):
        super().__init__()
        self._comment = comment

    @property
    def type(self) -> Node.Type:
        return Node.Type.Comment

    @property
    def comment(self) -> str:
        return self._comment

    def write_sb(self, sb: IndentBuilder | None = None) -> IndentBuilder:
        sb = sb or IndentBuilder()
        sb.write(f"<!--{xml_escape(self.comment)}-->")
        return sb


# --------------------------------------------------------------------
class XML(Node):
    class Factory:
        def __init__(self, html=False):
            super().__init__()
            self._html = html

        def __call__(self, name: str) -> "XML":
            return XML(name, html=self._html)

        def __getattr__(self, name) -> "XML":
            return self(name)

    class Parser(ParserMixin["XML"], XMLParser):
        def __init__(self):
            super().__init__()

        def parse(self, data: str) -> list["XML"]:
            xml_parse(data, self)
            return self.finalize()

        def startElement(self, tag, attrs):
            element = XML(tag, attrs)
            if self.current is not None:
                self.current(element)
            self.push(element)

        def endElement(self, tag):
            if self.current is None:
                raise ValueError(f"End tag for '{tag}' found with no opening tag")
            if self.current.tag != tag:
                raise ValueError(
                    f"End tag for '{tag}' encountered, expected end tag for '{self.current.tag}'"
                )
            if len(self.stack) == 1:
                self.add_result(self.current)
            self.pop()

        def characters(self, data):
            if self.current is None:
                raise ValueError(f"Non-tag data encountered outside of any tag")
            if data.strip():
                self.current(data)

    def __init__(
        self,
        name: str | None = None,
        attrs: dict[str, Any] = {},
        html=False,
        doctype: str | None = None,
    ):
        super().__init__()
        self._name = "html" if name is None and html else name or ""
        self._attrs = {**attrs}
        self._children: list[Node] = []
        self._doctype: str | None = "html" if html and doctype is None else doctype
        self._is_html = html or self._doctype == "html"

    def __contains__(self, value: str | Node):
        if isinstance(value, str):
            return value in self._attrs

        return value in self._children

    def __getitem__(self, key: str):
        return self._attrs[key]

    def __setitem__(self, key: str, value: Any):
        self._ingest_attrs({key: value})

    def __delitem__(self, key: str):
        del self._attrs[key]

    @property
    def type(self) -> Node.Type:
        return Node.Type.Element

    @property
    def doctype(self) -> str | None:
        return self._doctype

    @property
    def name(self) -> str:
        return xml_escape(self._name)

    @property
    def tag(self) -> str:
        return self._name

    @property
    def is_void(self) -> bool:
        return self.name in HTML_VOID_ELEMENTS

    @property
    def is_noindent(self) -> bool:
        return self.name in HTML_NOINDENT_ELEMENTS

    @property
    def is_inline(self) -> bool:
        return self.name in HTML_INLINE_ELEMENTS

    @property
    def is_content_inline(self) -> bool:
        return self.is_inline or all(c.is_inline for c in self.children)

    @property
    def is_html(self) -> bool:
        return self._is_html

    @property
    def has_children(self) -> bool:
        return len(self._children) > 0

    @property
    def children(self) -> list[Node]:
        return [*self._children]

    @property
    def last(self) -> Node | None:
        return None if not self.has_children else self._children[-1]

    @property
    def attr_str(self) -> str:
        decls: list[str] = [""]
        for key, value in self._attrs.items():
            if self.is_html and isinstance(value, bool):
                if value == True:
                    decls.append(key)
            else:
                decls.append(f"{xml_escape(key)}={attr_escape(str(value))}")

        if len(decls) == 1:
            return ""
        return " ".join(decls)

    def attrs(self) -> Generator[tuple[str, Any], None, None]:
        yield from self._attrs.items()

    def _ingest_attrs(self, attrs: dict[str, Any]):
        for key, value in attrs.items():
            if key == "class" and self.is_html:
                classes: list[str] = []
                if isinstance(value, str):
                    classes.append(value)
                elif isinstance(value, (list, tuple)):
                    classes.extend([str(x) for x in value])
                else:
                    classes.append(str(value))
                self._attrs[key] = classes
            else:
                self._attrs[key] = value

    def append(self, child: Node) -> "XML":
        if self.is_html and self.is_void:
            raise ValueError(f"HTML void tag '{self.name}' cannot contain child nodes.")

        if (
            child.type == Node.Type.Text
            and self._children
            and self._children[-1].type == Node.Type.Text
        ):
            prev_text = cast(Text, self._children[-1])
            self._children.pop()
            child = Text(prev_text.text + cast(Text, child).text)

        self._children.append(child)
        child.parent = self
        return self

    def apply(self, *args, **kwargs) -> "XML":
        if kwargs is not None:
            self._ingest_attrs(kwargs)

        for child in args:
            if isinstance(child, (list, tuple)):
                self.apply(*child)
            elif isinstance(child, dict):
                self._ingest_attrs(child)
            elif isinstance(child, Node):
                self.append(child)
            else:
                self.append(Text(str(child)))

        return self

    def write_sb(self, sb: IndentBuilder | None = None) -> IndentBuilder:
        sb = sb or IndentBuilder()

        if self.is_root:
            if not self.is_html:
                sb('<?xml version="1.0" encoding="UTF-8"?>')
            if self.doctype is not None:
                sb(f"<!DOCTYPE {self.doctype}>")

        if not self.has_children:
            if self.is_html and not self.is_void:
                sb.write(f"<{self.name}{self.attr_str}></{self.name}>")
            else:
                sb.write(f"<{self.name}{self.attr_str}/>")
        else:
            sb.write(f"<{self.name}{self.attr_str}>")
            with sb:
                if not self.is_content_inline:
                    sb.newline()
                child_sb = sb
                if self.is_noindent:
                    child_sb = IndentBuilder(IndentOptions(enabled=False))
                for child in self.children:
                    child.write_sb(child_sb)
                if not self.is_content_inline:
                    sb.newline()
            sb.write(f"</{self.name}>")
        if not self.is_inline and not self.is_last:
            sb.newline()

        return sb

    def __call__(self, *args, **kwargs) -> "XML":
        return self.apply(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.write_sb())


# --------------------------------------------------------------------
class HTML(XML):
    class Factory(XML.Factory):
        def __init__(self):
            super().__init__(html=True)

    class Parser(ParserMixin["HTML"], HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)

        def handle_startendtag(self, tag, attrs):
            element = HTML(tag, attrs)
            if self.current is not None:
                self.current(element)
            else:
                self.add_result(element)

        def handle_starttag(self, tag, attrs):
            element = HTML(tag, attrs)
            if self.current is not None:
                self.current(element)
            self.push(element)

        def handle_endtag(self, tag):
            if self.current is None:
                raise ValueError(
                    f"End tag for '{tag}' found with no opening tag @ {self.getpos()}"
                )
            if self.current.tag != tag:
                raise ValueError(
                    f"End tag for '{tag}' encountered, expected end tag for '{self.current.tag}' @ {self.getpos()}"
                )
            if len(self.stack) == 1:
                self.add_result(self.current)
            self.pop()

        def handle_data(self, data: str):
            if self.current is None:
                raise ValueError(
                    f"Non-tag data encountered outside of any tag @ {self.getpos()}"
                )
            self.current(data)

        def parse(self, data: str) -> list["HTML"]:
            self.feed(data)
            self.close()
            return self.finalize()

    def __init__(self, name="html", attrs: dict[str, Any] = {}):
        super().__init__(name, attrs, html=True)
