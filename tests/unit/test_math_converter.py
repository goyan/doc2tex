"""Tests for math conversion."""

import pytest

from docx2latex.infrastructure.converters.math.omml_parser import OmmlParser
from docx2latex.infrastructure.converters.math.symbols import SymbolMapper


class TestSymbolMapper:
    """Tests for symbol mapping."""

    def test_greek_letters(self) -> None:
        mapper = SymbolMapper()
        assert mapper.map_char("α") == r"\alpha"
        assert mapper.map_char("β") == r"\beta"
        assert mapper.map_char("Γ") == r"\Gamma"
        assert mapper.map_char("Δ") == r"\Delta"

    def test_operators(self) -> None:
        mapper = SymbolMapper()
        assert mapper.map_char("×") == r"\times"
        assert mapper.map_char("÷") == r"\div"
        assert mapper.map_char("±") == r"\pm"
        assert mapper.map_char("≤") == r"\leq"
        assert mapper.map_char("≥") == r"\geq"

    def test_function_names(self) -> None:
        mapper = SymbolMapper()
        assert mapper.is_function_name("sin")
        assert mapper.is_function_name("cos")
        assert mapper.is_function_name("lim")
        assert not mapper.is_function_name("xyz")

    def test_function_latex(self) -> None:
        mapper = SymbolMapper()
        assert mapper.get_function_latex("sin") == r"\sin"
        assert mapper.get_function_latex("log") == r"\log"
        assert mapper.get_function_latex("custom") == r"\operatorname{custom}"


class TestOmmlParser:
    """Tests for OMML parsing."""

    def test_simple_fraction(self) -> None:
        """Test basic fraction conversion."""
        omml = """
        <m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
            <m:f>
                <m:num><m:r><m:t>a</m:t></m:r></m:num>
                <m:den><m:r><m:t>b</m:t></m:r></m:den>
            </m:f>
        </m:oMath>
        """
        parser = OmmlParser()
        result = parser.parse(omml)
        assert r"\frac{a}{b}" in result

    def test_superscript(self) -> None:
        """Test superscript conversion."""
        omml = """
        <m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
            <m:sSup>
                <m:e><m:r><m:t>x</m:t></m:r></m:e>
                <m:sup><m:r><m:t>2</m:t></m:r></m:sup>
            </m:sSup>
        </m:oMath>
        """
        parser = OmmlParser()
        result = parser.parse(omml)
        assert "x^{2}" in result

    def test_subscript(self) -> None:
        """Test subscript conversion."""
        omml = """
        <m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
            <m:sSub>
                <m:e><m:r><m:t>x</m:t></m:r></m:e>
                <m:sub><m:r><m:t>i</m:t></m:r></m:sub>
            </m:sSub>
        </m:oMath>
        """
        parser = OmmlParser()
        result = parser.parse(omml)
        assert "x_{i}" in result

    def test_square_root(self) -> None:
        """Test square root conversion."""
        omml = """
        <m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
            <m:rad>
                <m:radPr><m:degHide m:val="1"/></m:radPr>
                <m:deg/>
                <m:e><m:r><m:t>x</m:t></m:r></m:e>
            </m:rad>
        </m:oMath>
        """
        parser = OmmlParser()
        result = parser.parse(omml)
        assert r"\sqrt{x}" in result

    def test_delimiter_parentheses(self) -> None:
        """Test parentheses conversion."""
        omml = """
        <m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
            <m:d>
                <m:dPr>
                    <m:begChr m:val="("/>
                    <m:endChr m:val=")"/>
                </m:dPr>
                <m:e><m:r><m:t>x+y</m:t></m:r></m:e>
            </m:d>
        </m:oMath>
        """
        parser = OmmlParser()
        result = parser.parse(omml)
        assert r"\left(" in result
        assert r"\right)" in result
