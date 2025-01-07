# --------------------------------------------------------------------
# test.py
#
# Author: Lain Musgrove (lain.proliant@gmail.com)
# Date: Tuesday January 7, 2025
# --------------------------------------------------------------------

import tracemalloc
import unittest
from pathlib import Path

from indent_tools.text import IndentBuilder
from indent_tools.xml import HTML, XML

# --------------------------------------------------------------------
tracemalloc.start()


# --------------------------------------------------------------------
def read_test_file(filename: str | Path) -> str:
    with open(Path("testsrc/") / filename, "r") as infile:
        return infile.read().strip()


# --------------------------------------------------------------------
def print_doc(doc):
    print()
    print("----------")
    print(str(doc))
    print("----------")


# --------------------------------------------------------------------
class IndentWriterTests(unittest.TestCase):
    def test_basic_indent_builder(self):
        """Test to verify that IndentBuilder works."""

        sb = IndentBuilder()
        sb("int main() {")
        with sb:
            sb("int x = 0;")
            sb("return x;")
        sb("}")
        print_doc(sb)
        self.assertEqual(str(sb).strip(), read_test_file("main.c"))

    def test_write_newlines(self):
        """Test to verify that splitting on newlines in write() works."""
        sb = IndentBuilder()
        sb.write("int main() {")
        with sb:
            sb.write("\nint x = 0;\nreturn x;\n")
        sb("}")
        self.assertEqual(str(sb).strip(), read_test_file("main.c"))


# --------------------------------------------------------------------
class XMLTests(unittest.TestCase):
    def test_basic_xml_generation(self):
        """Test that a sample XML file can be replicated."""
        xml = XML.Factory()
        doc = xml.address(type="Residential")(
            xml.street("123 Main St"),
            xml.city("Bremerton"),
            xml("state")("WA"),
            xml.zip_code("98310"),
        )
        print_doc(doc)
        self.assertEqual(str(doc).strip(), read_test_file("address.xml"))

    def test_xml_round_trip(self):
        """Test that an XML file parsing and generating are stable."""
        parser = XML.Parser()
        doc = parser.parse_one(read_test_file("address.xml"))
        self.assertEqual(str(doc).strip(), read_test_file("address.xml"))

    def test_basic_html_generation(self):
        """Test that a sample HTML file can be replicated."""
        html = HTML.Factory()
        doc = html.html(
            html.head(html.meta(charset="utf-8"), html.title("Example")),
            html.body(html.h1("This is a sample page.")),
        )
        print_doc(doc)
        self.assertEqual(str(doc).strip(), read_test_file("example.html"))


# --------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
