"""
Style resolver for DOCX documents.

Handles style inheritance and resolution from styles.xml.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from lxml import etree

from docx2latex.domain.value_objects.color import Color
from docx2latex.domain.value_objects.dimension import Dimension
from docx2latex.domain.value_objects.font import FontSpec
from docx2latex.domain.value_objects.style import (
    Alignment,
    ParagraphStyle,
    TextStyle,
    UnderlineStyle,
)
from docx2latex.infrastructure.parsing.xml_namespaces import NS, W


@dataclass
class StyleDefinition:
    """
    A style definition from styles.xml.

    Contains both paragraph and run (text) properties.
    """

    style_id: str
    name: str
    style_type: str  # paragraph, character, table, numbering
    based_on: str | None = None
    paragraph_props: ParagraphStyle = field(default_factory=ParagraphStyle.empty)
    run_props: TextStyle = field(default_factory=TextStyle.empty)
    is_default: bool = False
    outline_level: int | None = None


class StyleResolver:
    """
    Resolves styles from DOCX styles.xml.

    Handles style inheritance (basedOn relationships) and
    provides resolved styles for paragraphs and runs.
    """

    def __init__(self) -> None:
        self._styles: dict[str, StyleDefinition] = {}
        self._default_paragraph_style: StyleDefinition | None = None
        self._default_character_style: StyleDefinition | None = None
        self._resolved_cache: dict[str, StyleDefinition] = {}

    def load_from_xml(self, styles_xml: bytes) -> None:
        """
        Load styles from styles.xml content.

        Args:
            styles_xml: Raw XML bytes from styles.xml
        """
        root = etree.fromstring(styles_xml)
        self._parse_styles(root)

    def _parse_styles(self, root: etree._Element) -> None:
        """Parse all style elements."""
        # Find all w:style elements
        for style_elem in root.findall(f".//{W.P}/../w:style", namespaces=NS):
            self._parse_style_element(style_elem)

        # Alternative path for styles
        for style_elem in root.iter(f"{{{NS['w']}}}style"):
            if style_elem.get(f"{{{NS['w']}}}styleId") not in self._styles:
                self._parse_style_element(style_elem)

    def _parse_style_element(self, elem: etree._Element) -> None:
        """Parse a single style element."""
        style_id = elem.get(f"{{{NS['w']}}}styleId", "")
        if not style_id:
            return

        style_type = elem.get(f"{{{NS['w']}}}type", "paragraph")
        is_default = elem.get(f"{{{NS['w']}}}default") == "1"

        # Get style name
        name_elem = elem.find(f"{{{NS['w']}}}name", namespaces=NS)
        name = name_elem.get(f"{{{NS['w']}}}val", style_id) if name_elem is not None else style_id

        # Get basedOn
        based_on_elem = elem.find(f"{{{NS['w']}}}basedOn", namespaces=NS)
        based_on = based_on_elem.get(f"{{{NS['w']}}}val") if based_on_elem is not None else None

        # Parse paragraph properties
        ppr_elem = elem.find(f"{{{NS['w']}}}pPr", namespaces=NS)
        paragraph_props = self._parse_paragraph_props(ppr_elem) if ppr_elem is not None else ParagraphStyle.empty()

        # Parse run properties
        rpr_elem = elem.find(f"{{{NS['w']}}}rPr", namespaces=NS)
        run_props = self._parse_run_props(rpr_elem) if rpr_elem is not None else TextStyle.empty()

        # Get outline level (for headings)
        outline_level = None
        if ppr_elem is not None:
            outline_elem = ppr_elem.find(f"{{{NS['w']}}}outlineLvl", namespaces=NS)
            if outline_elem is not None:
                try:
                    outline_level = int(outline_elem.get(f"{{{NS['w']}}}val", "0"))
                except ValueError:
                    pass

        style_def = StyleDefinition(
            style_id=style_id,
            name=name,
            style_type=style_type,
            based_on=based_on,
            paragraph_props=paragraph_props,
            run_props=run_props,
            is_default=is_default,
            outline_level=outline_level,
        )

        self._styles[style_id] = style_def

        if is_default:
            if style_type == "paragraph":
                self._default_paragraph_style = style_def
            elif style_type == "character":
                self._default_character_style = style_def

    def _parse_paragraph_props(self, ppr: etree._Element) -> ParagraphStyle:
        """Parse paragraph properties element."""
        # Alignment
        alignment = Alignment.JUSTIFY
        jc_elem = ppr.find(f"{{{NS['w']}}}jc", namespaces=NS)
        if jc_elem is not None:
            jc_val = jc_elem.get(f"{{{NS['w']}}}val", "")
            alignment = {
                "left": Alignment.LEFT,
                "start": Alignment.LEFT,
                "center": Alignment.CENTER,
                "right": Alignment.RIGHT,
                "end": Alignment.RIGHT,
                "both": Alignment.JUSTIFY,
                "distribute": Alignment.JUSTIFY,
            }.get(jc_val, Alignment.JUSTIFY)

        # Spacing
        space_before = None
        space_after = None
        line_spacing = None
        spacing_elem = ppr.find(f"{{{NS['w']}}}spacing", namespaces=NS)
        if spacing_elem is not None:
            before = spacing_elem.get(f"{{{NS['w']}}}before")
            if before:
                space_before = Dimension.from_twips(int(before))

            after = spacing_elem.get(f"{{{NS['w']}}}after")
            if after:
                space_after = Dimension.from_twips(int(after))

            line = spacing_elem.get(f"{{{NS['w']}}}line")
            line_rule = spacing_elem.get(f"{{{NS['w']}}}lineRule", "auto")
            if line and line_rule == "auto":
                # Line spacing as multiple (240 = single)
                line_spacing = int(line) / 240.0

        # Indentation
        first_line_indent = None
        left_indent = None
        right_indent = None
        ind_elem = ppr.find(f"{{{NS['w']}}}ind", namespaces=NS)
        if ind_elem is not None:
            first_line = ind_elem.get(f"{{{NS['w']}}}firstLine")
            if first_line:
                first_line_indent = Dimension.from_twips(int(first_line))

            hanging = ind_elem.get(f"{{{NS['w']}}}hanging")
            if hanging:
                # Hanging indent is negative first-line indent
                first_line_indent = Dimension.from_twips(-int(hanging))

            left = ind_elem.get(f"{{{NS['w']}}}left") or ind_elem.get(f"{{{NS['w']}}}start")
            if left:
                left_indent = Dimension.from_twips(int(left))

            right = ind_elem.get(f"{{{NS['w']}}}right") or ind_elem.get(f"{{{NS['w']}}}end")
            if right:
                right_indent = Dimension.from_twips(int(right))

        # Outline level
        outline_level = None
        outline_elem = ppr.find(f"{{{NS['w']}}}outlineLvl", namespaces=NS)
        if outline_elem is not None:
            try:
                outline_level = int(outline_elem.get(f"{{{NS['w']}}}val", "0"))
            except ValueError:
                pass

        # Style reference
        style_name = None
        pstyle_elem = ppr.find(f"{{{NS['w']}}}pStyle", namespaces=NS)
        if pstyle_elem is not None:
            style_name = pstyle_elem.get(f"{{{NS['w']}}}val")

        return ParagraphStyle(
            alignment=alignment,
            line_spacing=line_spacing,
            space_before=space_before,
            space_after=space_after,
            first_line_indent=first_line_indent,
            left_indent=left_indent,
            right_indent=right_indent,
            style_name=style_name,
            outline_level=outline_level,
        )

    def _parse_run_props(self, rpr: etree._Element) -> TextStyle:
        """Parse run (character) properties element."""
        # Bold
        bold = rpr.find(f"{{{NS['w']}}}b", namespaces=NS) is not None
        if bold:
            # Check if explicitly turned off
            b_elem = rpr.find(f"{{{NS['w']}}}b", namespaces=NS)
            if b_elem is not None and b_elem.get(f"{{{NS['w']}}}val") == "0":
                bold = False

        # Italic
        italic = rpr.find(f"{{{NS['w']}}}i", namespaces=NS) is not None
        if italic:
            i_elem = rpr.find(f"{{{NS['w']}}}i", namespaces=NS)
            if i_elem is not None and i_elem.get(f"{{{NS['w']}}}val") == "0":
                italic = False

        # Underline
        underline = UnderlineStyle.NONE
        u_elem = rpr.find(f"{{{NS['w']}}}u", namespaces=NS)
        if u_elem is not None:
            u_val = u_elem.get(f"{{{NS['w']}}}val", "single")
            underline = UnderlineStyle.from_docx(u_val)

        # Strike
        strike = rpr.find(f"{{{NS['w']}}}strike", namespaces=NS) is not None
        dstrike = rpr.find(f"{{{NS['w']}}}dstrike", namespaces=NS) is not None
        strike = strike or dstrike

        # Vertical alignment (superscript/subscript)
        superscript = False
        subscript = False
        vert_elem = rpr.find(f"{{{NS['w']}}}vertAlign", namespaces=NS)
        if vert_elem is not None:
            vert_val = vert_elem.get(f"{{{NS['w']}}}val", "")
            superscript = vert_val == "superscript"
            subscript = vert_val == "subscript"

        # Small caps / All caps
        small_caps = rpr.find(f"{{{NS['w']}}}smallCaps", namespaces=NS) is not None
        all_caps = rpr.find(f"{{{NS['w']}}}caps", namespaces=NS) is not None

        # Color
        color = None
        color_elem = rpr.find(f"{{{NS['w']}}}color", namespaces=NS)
        if color_elem is not None:
            color_val = color_elem.get(f"{{{NS['w']}}}val")
            color = Color.from_docx_color(color_val)

        # Highlight
        highlight = None
        hl_elem = rpr.find(f"{{{NS['w']}}}highlight", namespaces=NS)
        if hl_elem is not None:
            hl_val = hl_elem.get(f"{{{NS['w']}}}val")
            # Map highlight names to colors
            highlight_colors = {
                "yellow": Color(255, 255, 0),
                "green": Color(0, 255, 0),
                "cyan": Color(0, 255, 255),
                "magenta": Color(255, 0, 255),
                "blue": Color(0, 0, 255),
                "red": Color(255, 0, 0),
                "darkBlue": Color(0, 0, 139),
                "darkCyan": Color(0, 139, 139),
                "darkGreen": Color(0, 100, 0),
                "darkMagenta": Color(139, 0, 139),
                "darkRed": Color(139, 0, 0),
                "darkYellow": Color(128, 128, 0),
                "darkGray": Color(169, 169, 169),
                "lightGray": Color(211, 211, 211),
                "black": Color(0, 0, 0),
            }
            highlight = highlight_colors.get(hl_val)

        # Font
        font = None
        sz_elem = rpr.find(f"{{{NS['w']}}}sz", namespaces=NS)
        fonts_elem = rpr.find(f"{{{NS['w']}}}rFonts", namespaces=NS)

        font_family = None
        font_size = None

        if fonts_elem is not None:
            font_family = (
                fonts_elem.get(f"{{{NS['w']}}}ascii")
                or fonts_elem.get(f"{{{NS['w']}}}hAnsi")
                or fonts_elem.get(f"{{{NS['w']}}}cs")
            )

        if sz_elem is not None:
            try:
                font_size = int(sz_elem.get(f"{{{NS['w']}}}val", "0"))
            except ValueError:
                pass

        if font_family or font_size:
            font = FontSpec.from_docx(family=font_family, size_half_points=font_size)

        return TextStyle(
            bold=bold,
            italic=italic,
            underline=underline,
            strike=strike,
            superscript=superscript,
            subscript=subscript,
            small_caps=small_caps,
            all_caps=all_caps,
            color=color,
            highlight=highlight,
            font=font,
        )

    def resolve_paragraph_style(self, style_id: str | None) -> ParagraphStyle:
        """
        Resolve a paragraph style with inheritance.

        Args:
            style_id: Style ID to resolve

        Returns:
            Fully resolved ParagraphStyle
        """
        if not style_id:
            if self._default_paragraph_style:
                return self._default_paragraph_style.paragraph_props
            return ParagraphStyle.empty()

        # Check cache
        cache_key = f"para:{style_id}"
        if cache_key in self._resolved_cache:
            return self._resolved_cache[cache_key].paragraph_props

        # Get style definition
        style_def = self._styles.get(style_id)
        if not style_def:
            return ParagraphStyle.empty()

        # Resolve inheritance chain
        resolved = self._resolve_style_chain(style_def)
        self._resolved_cache[cache_key] = resolved
        return resolved.paragraph_props

    def resolve_run_style(self, style_id: str | None) -> TextStyle:
        """
        Resolve a character (run) style with inheritance.

        Args:
            style_id: Style ID to resolve

        Returns:
            Fully resolved TextStyle
        """
        if not style_id:
            if self._default_character_style:
                return self._default_character_style.run_props
            return TextStyle.empty()

        # Check cache
        cache_key = f"run:{style_id}"
        if cache_key in self._resolved_cache:
            return self._resolved_cache[cache_key].run_props

        # Get style definition
        style_def = self._styles.get(style_id)
        if not style_def:
            return TextStyle.empty()

        # Resolve inheritance chain
        resolved = self._resolve_style_chain(style_def)
        self._resolved_cache[cache_key] = resolved
        return resolved.run_props

    def _resolve_style_chain(self, style_def: StyleDefinition) -> StyleDefinition:
        """Resolve the full inheritance chain for a style."""
        # Build chain from base to derived
        chain: list[StyleDefinition] = [style_def]
        current = style_def

        while current.based_on:
            parent = self._styles.get(current.based_on)
            if not parent or parent in chain:  # Prevent cycles
                break
            chain.insert(0, parent)
            current = parent

        # Merge styles from base to derived
        result_para = ParagraphStyle.empty()
        result_run = TextStyle.empty()

        for style in chain:
            result_para = result_para.merge_with(style.paragraph_props)
            result_run = result_run.merge_with(style.run_props)

        return StyleDefinition(
            style_id=style_def.style_id,
            name=style_def.name,
            style_type=style_def.style_type,
            based_on=style_def.based_on,
            paragraph_props=result_para,
            run_props=result_run,
            is_default=style_def.is_default,
            outline_level=style_def.outline_level,
        )

    def get_outline_level(self, style_id: str | None) -> int | None:
        """Get outline level for a style (for headings)."""
        if not style_id:
            return None

        style_def = self._styles.get(style_id)
        if style_def and style_def.outline_level is not None:
            return style_def.outline_level

        # Check resolved
        resolved = self._resolve_style_chain(style_def) if style_def else None
        return resolved.outline_level if resolved else None

    def is_heading_style(self, style_id: str | None) -> bool:
        """Check if a style is a heading style."""
        if not style_id:
            return False

        # Check outline level
        if self.get_outline_level(style_id) is not None:
            return True

        # Check style name
        style_def = self._styles.get(style_id)
        if style_def:
            name_lower = style_def.name.lower()
            return "heading" in name_lower or "titre" in name_lower

        return False
