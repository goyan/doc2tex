"""
OMML (Office Math Markup Language) parser.

Parses OMML XML and converts to LaTeX math.
"""

from __future__ import annotations

from lxml import etree

from docx2latex.infrastructure.converters.math.symbols import SymbolMapper
from docx2latex.infrastructure.parsing.xml_namespaces import NS
from docx2latex.shared.logging import get_logger

logger = get_logger("omml")


class OmmlParser:
    """
    Parser for Office Math Markup Language (OMML).

    Converts OMML XML elements to LaTeX math notation.
    """

    def __init__(self) -> None:
        self._symbols = SymbolMapper()

    def parse(self, omml_xml: str) -> str:
        """
        Parse OMML XML string to LaTeX.

        Args:
            omml_xml: OMML XML string

        Returns:
            LaTeX math string
        """
        try:
            root = etree.fromstring(omml_xml.encode())
            return self._convert_element(root)
        except Exception as e:
            logger.warning(f"OMML parse error: {e}")
            return ""

    def _convert_element(self, elem: etree._Element) -> str:
        """
        Convert an OMML element to LaTeX.

        Dispatches to specific handlers based on element type.
        """
        tag = etree.QName(elem).localname

        handlers = {
            "oMath": self._handle_omath,
            "r": self._handle_run,
            "t": self._handle_text,
            "f": self._handle_fraction,
            "rad": self._handle_radical,
            "sSub": self._handle_subscript,
            "sSup": self._handle_superscript,
            "sSubSup": self._handle_subsup,
            "sPre": self._handle_presup,
            "nary": self._handle_nary,
            "limLow": self._handle_limlower,
            "limUpp": self._handle_limupper,
            "m": self._handle_matrix,
            "d": self._handle_delimiter,
            "eqArr": self._handle_eqarray,
            "bar": self._handle_bar,
            "acc": self._handle_accent,
            "box": self._handle_box,
            "func": self._handle_function,
            "groupChr": self._handle_groupchar,
            "borderBox": self._handle_borderbox,
            "phant": self._handle_phantom,
        }

        handler = handlers.get(tag)
        if handler:
            return handler(elem)

        # Default: process children
        return self._process_children(elem)

    def _process_children(self, elem: etree._Element) -> str:
        """Process all children of an element."""
        parts = []
        for child in elem:
            result = self._convert_element(child)
            if result:
                parts.append(result)
        return self._join_with_spacing(parts)

    def _join_with_spacing(self, parts: list[str]) -> str:
        """Join parts with smart spacing for LaTeX commands.

        Adds space when a LaTeX command ending with a letter
        is followed by content starting with a letter.
        """
        if not parts:
            return ""

        result = [parts[0]]
        for i in range(1, len(parts)):
            prev = parts[i - 1]
            curr = parts[i]

            # Check if we need a space between prev and curr
            needs_space = False
            if prev and curr:
                # Find last LaTeX command in prev
                last_backslash = prev.rfind("\\")
                if last_backslash >= 0:
                    # Get the command part after backslash
                    after_backslash = prev[last_backslash + 1:]
                    # Check if command ends at the string end and ends with letter
                    if after_backslash and after_backslash[-1].isalpha():
                        # Check if there's no brace/bracket after the command
                        # Commands like \frac{} don't need extra space
                        if not any(c in after_backslash for c in "{}[]"):
                            # Check if next part starts with letter
                            if curr and curr[0].isalpha():
                                needs_space = True

            if needs_space:
                result.append(" ")
            result.append(curr)

        return "".join(result)

    def _get_element(self, parent: etree._Element, tag: str) -> etree._Element | None:
        """Get child element by tag (without namespace)."""
        for child in parent:
            if etree.QName(child).localname == tag:
                return child
        return None

    def _get_text(self, elem: etree._Element) -> str:
        """Get text content from element tree."""
        parts = []
        for t in elem.iter(f"{{{NS['m']}}}t"):
            if t.text:
                parts.append(t.text)
        return "".join(parts)

    def _handle_omath(self, elem: etree._Element) -> str:
        """Handle oMath (math block) element."""
        return self._process_children(elem)

    def _handle_run(self, elem: etree._Element) -> str:
        """Handle math run element (m:r)."""
        # Check for special styling
        rpr = self._get_element(elem, "rPr")
        style_prefix = ""
        style_suffix = ""

        if rpr is not None:
            # Check for script type (normal, bold, italic, etc.)
            scr = self._get_element(rpr, "scr")
            sty = self._get_element(rpr, "sty")

            if scr is not None:
                scr_val = scr.get(f"{{{NS['m']}}}val", "")
                # Script types: roman, script, fraktur, double-struck, sans-serif, monospace
                script_map = {
                    "script": (r"\mathcal{", "}"),
                    "fraktur": (r"\mathfrak{", "}"),
                    "double-struck": (r"\mathbb{", "}"),
                    "sans-serif": (r"\mathsf{", "}"),
                    "monospace": (r"\mathtt{", "}"),
                }
                if scr_val in script_map:
                    style_prefix, style_suffix = script_map[scr_val]

            if sty is not None:
                sty_val = sty.get(f"{{{NS['m']}}}val", "")
                # Style: p (plain), b (bold), i (italic), bi (bold-italic)
                if sty_val == "b" and not style_prefix:
                    style_prefix, style_suffix = r"\mathbf{", "}"
                elif sty_val == "i" and not style_prefix:
                    style_prefix, style_suffix = r"\mathit{", "}"
                elif sty_val == "bi" and not style_prefix:
                    style_prefix, style_suffix = r"\boldsymbol{", "}"

        raw_text = self._get_text(elem)

        # Check if this is a function name
        if self._symbols.is_function_name(raw_text):
            text = self._symbols.get_function_latex(raw_text)
            return f"{style_prefix}{text}{style_suffix}" if style_prefix else text

        # For styled text, we need to handle mixed content carefully
        # e.g., "∈R" with double-struck should become "\in \mathbb{R}", not "\mathbb{∈R}"
        if style_prefix:
            return self._apply_style_smartly(raw_text, style_prefix, style_suffix)

        text = self._symbols.map_text(raw_text)
        return text

    def _apply_style_smartly(self, text: str, prefix: str, suffix: str) -> str:
        """Apply style only to letters, not to operators.

        This handles cases like "∈R" with double-struck style,
        which should become "\\in \\mathbb{R}" not "\\mathbb{∈R}".
        """
        result = []
        letter_buffer = []

        def flush_letters() -> None:
            if letter_buffer:
                letters = "".join(letter_buffer)
                result.append(f"{prefix}{letters}{suffix}")
                letter_buffer.clear()

        for char in text:
            mapped = self._symbols.map_char(char)
            # If it's a LaTeX command (starts with \), it's an operator
            if mapped.startswith("\\") or not char.isalpha():
                flush_letters()
                result.append(mapped)
            else:
                letter_buffer.append(char)

        flush_letters()
        return self._join_with_spacing(result) if len(result) > 1 else "".join(result)

    def _handle_text(self, elem: etree._Element) -> str:
        """Handle text element (m:t)."""
        text = elem.text or ""
        return self._symbols.map_text(text)

    def _handle_fraction(self, elem: etree._Element) -> str:
        """Handle fraction element (m:f)."""
        # Get fraction properties
        fpr = self._get_element(elem, "fPr")
        frac_type = "bar"  # Default: normal fraction with bar

        if fpr is not None:
            type_elem = self._get_element(fpr, "type")
            if type_elem is not None:
                frac_type = type_elem.get(f"{{{NS['m']}}}val", "bar")

        # Get numerator and denominator
        num = self._get_element(elem, "num")
        den = self._get_element(elem, "den")

        num_latex = self._process_children(num) if num is not None else ""
        den_latex = self._process_children(den) if den is not None else ""

        if frac_type == "noBar":
            # Binomial-like (no bar)
            return rf"\binom{{{num_latex}}}{{{den_latex}}}"
        elif frac_type == "skw":
            # Skewed fraction (diagonal)
            return rf"{{{num_latex}}}/{{{den_latex}}}"
        elif frac_type == "lin":
            # Linear fraction
            return rf"{{{num_latex}}}/{{{den_latex}}}"
        else:
            # Normal fraction with bar
            # Use \dfrac for display style if content is complex
            if len(num_latex) > 5 or len(den_latex) > 5:
                return rf"\dfrac{{{num_latex}}}{{{den_latex}}}"
            return rf"\frac{{{num_latex}}}{{{den_latex}}}"

    def _handle_radical(self, elem: etree._Element) -> str:
        """Handle radical (square root) element (m:rad)."""
        # Check for degree (nth root)
        radpr = self._get_element(elem, "radPr")
        deg_hide = False

        if radpr is not None:
            deghide = self._get_element(radpr, "degHide")
            if deghide is not None:
                deg_hide = deghide.get(f"{{{NS['m']}}}val", "0") == "1"

        deg = self._get_element(elem, "deg")
        e = self._get_element(elem, "e")

        base_latex = self._process_children(e) if e is not None else ""

        if deg is not None and not deg_hide:
            deg_latex = self._process_children(deg)
            if deg_latex and deg_latex.strip():
                return rf"\sqrt[{deg_latex}]{{{base_latex}}}"

        return rf"\sqrt{{{base_latex}}}"

    def _handle_subscript(self, elem: etree._Element) -> str:
        """Handle subscript element (m:sSub)."""
        e = self._get_element(elem, "e")
        sub = self._get_element(elem, "sub")

        base = self._process_children(e) if e is not None else ""
        sub_latex = self._process_children(sub) if sub is not None else ""

        # Wrap base if it's more than one character
        if len(base) > 1 and not base.startswith("\\"):
            base = f"{{{base}}}"

        return f"{base}_{{{sub_latex}}}"

    def _handle_superscript(self, elem: etree._Element) -> str:
        """Handle superscript element (m:sSup)."""
        e = self._get_element(elem, "e")
        sup = self._get_element(elem, "sup")

        base = self._process_children(e) if e is not None else ""
        sup_latex = self._process_children(sup) if sup is not None else ""

        # Wrap base if it's more than one character
        if len(base) > 1 and not base.startswith("\\"):
            base = f"{{{base}}}"

        return f"{base}^{{{sup_latex}}}"

    def _handle_subsup(self, elem: etree._Element) -> str:
        """Handle sub-superscript element (m:sSubSup)."""
        e = self._get_element(elem, "e")
        sub = self._get_element(elem, "sub")
        sup = self._get_element(elem, "sup")

        base = self._process_children(e) if e is not None else ""
        sub_latex = self._process_children(sub) if sub is not None else ""
        sup_latex = self._process_children(sup) if sup is not None else ""

        if len(base) > 1 and not base.startswith("\\"):
            base = f"{{{base}}}"

        return f"{base}_{{{sub_latex}}}^{{{sup_latex}}}"

    def _handle_presup(self, elem: etree._Element) -> str:
        """Handle pre-sub-superscript element (m:sPre)."""
        e = self._get_element(elem, "e")
        sub = self._get_element(elem, "sub")
        sup = self._get_element(elem, "sup")

        base = self._process_children(e) if e is not None else ""
        sub_latex = self._process_children(sub) if sub is not None else ""
        sup_latex = self._process_children(sup) if sup is not None else ""

        # Pre-scripts: use \prescript from mathtools or {}^{}_{}X format
        return rf"{{}}_{{{sub_latex}}}^{{{sup_latex}}}{base}"

    def _handle_nary(self, elem: etree._Element) -> str:
        """Handle n-ary operator (sum, product, integral) element (m:nary)."""
        narypr = self._get_element(elem, "naryPr")

        # Get operator character
        chr_val = "∫"  # Default to integral
        lim_loc = "subSup"  # Default limit location

        if narypr is not None:
            chr_elem = self._get_element(narypr, "chr")
            if chr_elem is not None:
                chr_val = chr_elem.get(f"{{{NS['m']}}}val", "∫")

            limloc_elem = self._get_element(narypr, "limLoc")
            if limloc_elem is not None:
                lim_loc = limloc_elem.get(f"{{{NS['m']}}}val", "subSup")

        # Get limits and base
        sub = self._get_element(elem, "sub")
        sup = self._get_element(elem, "sup")
        e = self._get_element(elem, "e")

        operator = self._symbols.get_nary_latex(chr_val)
        sub_latex = self._process_children(sub) if sub is not None else ""
        sup_latex = self._process_children(sup) if sup is not None else ""
        base_latex = self._process_children(e) if e is not None else ""

        # Build result
        result = operator

        if lim_loc == "undOvr":
            # Limits above and below (display style)
            if sub_latex:
                result += rf"_{{{sub_latex}}}"
            if sup_latex:
                result += rf"^{{{sup_latex}}}"
        else:
            # Limits as sub/superscript
            if sub_latex:
                result += rf"_{{{sub_latex}}}"
            if sup_latex:
                result += rf"^{{{sup_latex}}}"

        result += f" {base_latex}"
        return result

    def _handle_limlower(self, elem: etree._Element) -> str:
        """Handle lower limit element (m:limLow)."""
        e = self._get_element(elem, "e")
        lim = self._get_element(elem, "lim")

        base = self._process_children(e) if e is not None else ""
        lim_latex = self._process_children(lim) if lim is not None else ""

        return rf"\underset{{{lim_latex}}}{{{base}}}"

    def _handle_limupper(self, elem: etree._Element) -> str:
        """Handle upper limit element (m:limUpp)."""
        e = self._get_element(elem, "e")
        lim = self._get_element(elem, "lim")

        base = self._process_children(e) if e is not None else ""
        lim_latex = self._process_children(lim) if lim is not None else ""

        return rf"\overset{{{lim_latex}}}{{{base}}}"

    def _handle_matrix(self, elem: etree._Element) -> str:
        """Handle matrix element (m:m)."""
        rows = []

        for mr in elem.iter(f"{{{NS['m']}}}mr"):
            cells = []
            for e in mr.iter(f"{{{NS['m']}}}e"):
                cell_latex = self._process_children(e)
                cells.append(cell_latex)
            rows.append(" & ".join(cells))

        matrix_content = r" \\ ".join(rows)
        return rf"\begin{{matrix}} {matrix_content} \end{{matrix}}"

    def _handle_delimiter(self, elem: etree._Element) -> str:
        """Handle delimiter (brackets) element (m:d)."""
        dpr = self._get_element(elem, "dPr")

        # Default brackets
        beg_chr = "("
        end_chr = ")"
        sep_chr = ""

        if dpr is not None:
            begchr = self._get_element(dpr, "begChr")
            endchr = self._get_element(dpr, "endChr")
            sepchr = self._get_element(dpr, "sepChr")

            if begchr is not None:
                beg_chr = begchr.get(f"{{{NS['m']}}}val", "(")
            if endchr is not None:
                end_chr = endchr.get(f"{{{NS['m']}}}val", ")")
            if sepchr is not None:
                sep_chr = sepchr.get(f"{{{NS['m']}}}val", "")

        # Process content elements
        contents = []
        for e in elem.iter(f"{{{NS['m']}}}e"):
            contents.append(self._process_children(e))

        content = sep_chr.join(contents) if sep_chr else "".join(contents)

        # Map bracket characters to LaTeX (separate maps for left and right)
        left_map = {
            "(": "(",
            "[": "[",
            "{": r"\{",
            "|": "|",
            "‖": r"\|",
            "⟨": r"\langle",
            "⌈": r"\lceil",
            "⌊": r"\lfloor",
            "": "",
        }
        right_map = {
            ")": ")",
            "]": "]",
            "}": r"\}",
            "|": "|",
            "‖": r"\|",
            "⟩": r"\rangle",
            "⌉": r"\rceil",
            "⌋": r"\rfloor",
            "": "",
        }

        left = left_map.get(beg_chr, beg_chr)
        right = right_map.get(end_chr, end_chr)

        if left or right:
            return rf"\left{left} {content} \right{right}"
        return content

    def _handle_eqarray(self, elem: etree._Element) -> str:
        """Handle equation array element (m:eqArr)."""
        rows = []

        for e in elem.iter(f"{{{NS['m']}}}e"):
            row_latex = self._process_children(e)
            rows.append(row_latex)

        content = r" \\ ".join(rows)
        return rf"\begin{{aligned}} {content} \end{{aligned}}"

    def _handle_bar(self, elem: etree._Element) -> str:
        """Handle bar/overline element (m:bar)."""
        barpr = self._get_element(elem, "barPr")
        pos = "top"  # Default position

        if barpr is not None:
            pos_elem = self._get_element(barpr, "pos")
            if pos_elem is not None:
                pos = pos_elem.get(f"{{{NS['m']}}}val", "top")

        e = self._get_element(elem, "e")
        base = self._process_children(e) if e is not None else ""

        if pos == "bot":
            return rf"\underline{{{base}}}"
        return rf"\overline{{{base}}}"

    def _handle_accent(self, elem: etree._Element) -> str:
        """Handle accent element (m:acc)."""
        accpr = self._get_element(elem, "accPr")
        chr_val = "̂"  # Default to circumflex

        if accpr is not None:
            chr_elem = self._get_element(accpr, "chr")
            if chr_elem is not None:
                chr_val = chr_elem.get(f"{{{NS['m']}}}val", "̂")

        e = self._get_element(elem, "e")
        base = self._process_children(e) if e is not None else ""

        # Determine if base has multiple characters (for wide accents)
        # Strip braces and commands to count actual characters
        base_stripped = base
        for cmd in [r"\mathit", r"\mathrm", r"\mathbf"]:
            base_stripped = base_stripped.replace(cmd, "")
        base_stripped = base_stripped.replace("{", "").replace("}", "")
        is_multi_char = len(base_stripped) > 1

        # Map accent characters to LaTeX commands
        # Use wide versions for multi-character bases
        if is_multi_char:
            accent_map = {
                "̂": r"\widehat",
                "̃": r"\widetilde",
                "̄": r"\overline",
                "̇": r"\dot",
                "̈": r"\ddot",
                "⃗": r"\overrightarrow",
                "̆": r"\breve",
                "̌": r"\check",
                "̊": r"\mathring",
                "⏞": r"\overbrace",
                "⏟": r"\underbrace",
                "^": r"\widehat",
                "~": r"\widetilde",
                "→": r"\overrightarrow",
            }
        else:
            accent_map = {
                "̂": r"\hat",
                "̃": r"\tilde",
                "̄": r"\bar",
                "̇": r"\dot",
                "̈": r"\ddot",
                "⃗": r"\vec",
                "̆": r"\breve",
                "̌": r"\check",
                "̊": r"\mathring",
                "⏞": r"\overbrace",
                "⏟": r"\underbrace",
                "^": r"\hat",
                "~": r"\tilde",
                "→": r"\vec",
            }

        accent_cmd = accent_map.get(chr_val, r"\widehat" if is_multi_char else r"\hat")
        return rf"{accent_cmd}{{{base}}}"

    def _handle_box(self, elem: etree._Element) -> str:
        """Handle box element (m:box)."""
        e = self._get_element(elem, "e")
        return self._process_children(e) if e is not None else ""

    def _handle_function(self, elem: etree._Element) -> str:
        """Handle function element (m:func)."""
        fname = self._get_element(elem, "fName")
        e = self._get_element(elem, "e")

        func_name = self._process_children(fname) if fname is not None else ""
        arg = self._process_children(e) if e is not None else ""

        # Check if this is a recognized function
        clean_name = func_name.strip()
        if self._symbols.is_function_name(clean_name):
            func_latex = self._symbols.get_function_latex(clean_name)
            return f"{func_latex} {arg}"

        return f"{func_name} {arg}"

    def _handle_groupchar(self, elem: etree._Element) -> str:
        """Handle group character element (m:groupChr)."""
        groupchrpr = self._get_element(elem, "groupChrPr")
        chr_val = "⏟"  # Default to underbrace
        pos = "bot"  # Default position

        if groupchrpr is not None:
            chr_elem = self._get_element(groupchrpr, "chr")
            pos_elem = self._get_element(groupchrpr, "pos")

            if chr_elem is not None:
                chr_val = chr_elem.get(f"{{{NS['m']}}}val", "⏟")
            if pos_elem is not None:
                pos = pos_elem.get(f"{{{NS['m']}}}val", "bot")

        e = self._get_element(elem, "e")
        base = self._process_children(e) if e is not None else ""

        if chr_val == "⏞" or pos == "top":
            return rf"\overbrace{{{base}}}"
        return rf"\underbrace{{{base}}}"

    def _handle_borderbox(self, elem: etree._Element) -> str:
        """Handle border box element (m:borderBox)."""
        e = self._get_element(elem, "e")
        content = self._process_children(e) if e is not None else ""
        return rf"\boxed{{{content}}}"

    def _handle_phantom(self, elem: etree._Element) -> str:
        """Handle phantom element (m:phant)."""
        e = self._get_element(elem, "e")
        content = self._process_children(e) if e is not None else ""
        return rf"\phantom{{{content}}}"
