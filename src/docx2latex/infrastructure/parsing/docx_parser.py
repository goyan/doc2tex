"""
DOCX document parser.

Parses DOCX files into domain Document entities.
"""

from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING

from lxml import etree

from docx2latex.domain.entities.document import Document, DocumentMetadata, DocumentSection
from docx2latex.domain.entities.elements import (
    Hyperlink,
    Image,
    ListBlock,
    ListItem,
    MathBlock,
    Paragraph,
    Run,
    Table,
    TableCell,
    TableRow,
)
from docx2latex.domain.value_objects.dimension import Dimension
from docx2latex.domain.value_objects.layout import PageLayout
from docx2latex.domain.value_objects.style import (
    Alignment,
    ListType,
    MathType,
    ParagraphStyle,
    TextStyle,
)
from docx2latex.infrastructure.parsing.style_resolver import StyleResolver
from docx2latex.infrastructure.parsing.xml_namespaces import NS, A, M, PIC, R, W, WP
from docx2latex.shared.exceptions import DocxParseError
from docx2latex.shared.logging import get_logger
from docx2latex.shared.result import Err, Ok, Result

if TYPE_CHECKING:
    pass

logger = get_logger("parser")


class DocxParser:
    """
    Parser for DOCX files.

    Extracts document content, styles, and embedded resources
    into domain entities.
    """

    def __init__(self) -> None:
        self._style_resolver = StyleResolver()
        self._relationships: dict[str, dict[str, str]] = {}
        self._numbering: dict[str, dict[str, dict]] = {}  # numId -> ilvl -> props
        self._current_list_stack: list[ListBlock] = []
        self._zipfile: zipfile.ZipFile | None = None

    def parse(self, path: Path) -> Result[Document, str]:
        """
        Parse a DOCX file into a Document entity.

        Args:
            path: Path to the DOCX file

        Returns:
            Result containing Document or error message
        """
        if not path.exists():
            return Err(f"File not found: {path}")

        if not path.suffix.lower() == ".docx":
            return Err(f"Not a DOCX file: {path}")

        try:
            with open(path, "rb") as f:
                data = f.read()
            result = self.parse_bytes(data)
            if isinstance(result, Ok):
                result.value.source_path = path
            return result
        except Exception as e:
            return Err(f"Failed to read file: {e}")

    def parse_bytes(self, data: bytes) -> Result[Document, str]:
        """
        Parse DOCX data from bytes.

        Args:
            data: Raw DOCX file bytes

        Returns:
            Result containing Document or error message
        """
        try:
            self._zipfile = zipfile.ZipFile(BytesIO(data))
        except zipfile.BadZipFile:
            return Err("Invalid DOCX file (not a valid ZIP archive)")

        try:
            # Load relationships
            self._load_relationships()

            # Load styles
            self._load_styles()

            # Load numbering definitions
            self._load_numbering()

            # Parse core properties (metadata)
            metadata = self._parse_metadata()

            # Parse main document
            document = self._parse_document(metadata)

            return Ok(document)

        except DocxParseError as e:
            return Err(str(e))
        except Exception as e:
            logger.exception("Unexpected error parsing DOCX")
            return Err(f"Parse error: {e}")
        finally:
            if self._zipfile:
                self._zipfile.close()
                self._zipfile = None

    def _load_relationships(self) -> None:
        """Load document relationships from _rels/document.xml.rels."""
        rels_path = "word/_rels/document.xml.rels"

        if rels_path not in self._zipfile.namelist():
            return

        rels_xml = self._zipfile.read(rels_path)
        root = etree.fromstring(rels_xml)

        self._relationships["document"] = {}
        for rel in root.iter(f"{{{NS['pr']}}}Relationship"):
            rel_id = rel.get("Id", "")
            rel_type = rel.get("Type", "")
            target = rel.get("Target", "")
            self._relationships["document"][rel_id] = {
                "type": rel_type,
                "target": target,
            }

    def _load_styles(self) -> None:
        """Load styles from word/styles.xml."""
        styles_path = "word/styles.xml"

        if styles_path not in self._zipfile.namelist():
            return

        styles_xml = self._zipfile.read(styles_path)
        self._style_resolver.load_from_xml(styles_xml)

    def _load_numbering(self) -> None:
        """Load numbering definitions from word/numbering.xml."""
        numbering_path = "word/numbering.xml"

        if numbering_path not in self._zipfile.namelist():
            return

        numbering_xml = self._zipfile.read(numbering_path)
        root = etree.fromstring(numbering_xml)

        # Parse abstract numbering definitions
        abstract_nums: dict[str, dict] = {}
        for abstract in root.iter(f"{{{NS['w']}}}abstractNum"):
            abstract_id = abstract.get(f"{{{NS['w']}}}abstractNumId", "")
            levels = {}
            for lvl in abstract.iter(f"{{{NS['w']}}}lvl"):
                ilvl = lvl.get(f"{{{NS['w']}}}ilvl", "0")
                num_fmt_elem = lvl.find(f"{{{NS['w']}}}numFmt", namespaces=NS)
                num_fmt = num_fmt_elem.get(f"{{{NS['w']}}}val", "bullet") if num_fmt_elem is not None else "bullet"
                levels[ilvl] = {"format": num_fmt}
            abstract_nums[abstract_id] = levels

        # Parse numbering instances
        for num in root.iter(f"{{{NS['w']}}}num"):
            num_id = num.get(f"{{{NS['w']}}}numId", "")
            abstract_ref = num.find(f"{{{NS['w']}}}abstractNumId", namespaces=NS)
            if abstract_ref is not None:
                abstract_id = abstract_ref.get(f"{{{NS['w']}}}val", "")
                if abstract_id in abstract_nums:
                    self._numbering[num_id] = abstract_nums[abstract_id]

    def _parse_metadata(self) -> DocumentMetadata:
        """Parse document metadata from docProps/core.xml."""
        core_path = "docProps/core.xml"

        metadata = DocumentMetadata()

        if core_path not in self._zipfile.namelist():
            return metadata

        try:
            core_xml = self._zipfile.read(core_path)
            root = etree.fromstring(core_xml)

            # Title
            title_elem = root.find(f".//{{{NS['dc']}}}title")
            if title_elem is not None and title_elem.text:
                metadata.title = title_elem.text

            # Author
            creator_elem = root.find(f".//{{{NS['dc']}}}creator")
            if creator_elem is not None and creator_elem.text:
                metadata.author = creator_elem.text

            # Subject
            subject_elem = root.find(f".//{{{NS['dc']}}}subject")
            if subject_elem is not None and subject_elem.text:
                metadata.subject = subject_elem.text

            # Description
            desc_elem = root.find(f".//{{{NS['dc']}}}description")
            if desc_elem is not None and desc_elem.text:
                metadata.description = desc_elem.text

            # Created date
            created_elem = root.find(f".//{{{NS['dcterms']}}}created")
            if created_elem is not None and created_elem.text:
                metadata.created = created_elem.text

            # Modified date
            modified_elem = root.find(f".//{{{NS['dcterms']}}}modified")
            if modified_elem is not None and modified_elem.text:
                metadata.modified = modified_elem.text

        except Exception as e:
            logger.warning(f"Failed to parse metadata: {e}")

        return metadata

    def _parse_document(self, metadata: DocumentMetadata) -> Document:
        """Parse the main document content."""
        document_path = "word/document.xml"

        if document_path not in self._zipfile.namelist():
            raise DocxParseError("Missing document.xml")

        document_xml = self._zipfile.read(document_path)
        root = etree.fromstring(document_xml)

        document = Document(metadata=metadata)
        self._current_list_stack = []

        # Find document body
        body = root.find(f".//{{{NS['w']}}}body")
        if body is None:
            return document

        # Parse body elements
        current_section = document.current_section
        pending_list_items: list[tuple[Paragraph, int, str]] = []  # (para, level, numId)

        for elem in body:
            tag = etree.QName(elem).localname

            if tag == "p":
                # Check if this is a list item
                num_info = self._get_numbering_info(elem)
                if num_info:
                    num_id, ilvl = num_info
                    para = self._parse_paragraph(elem)
                    pending_list_items.append((para, ilvl, num_id))
                else:
                    # Flush any pending list items
                    if pending_list_items:
                        list_block = self._build_list_from_items(pending_list_items)
                        current_section.add_list(list_block)
                        pending_list_items = []

                    para = self._parse_paragraph(elem)
                    current_section.add_paragraph(para)

            elif tag == "tbl":
                # Flush any pending list items
                if pending_list_items:
                    list_block = self._build_list_from_items(pending_list_items)
                    current_section.add_list(list_block)
                    pending_list_items = []

                table = self._parse_table(elem)
                current_section.add_table(table)

            elif tag == "sectPr":
                # Section properties - create new section for subsequent content
                layout = self._parse_section_props(elem)
                current_section.layout = layout
                # Create new section for subsequent content
                current_section = document.new_section()

        # Flush any remaining list items
        if pending_list_items:
            list_block = self._build_list_from_items(pending_list_items)
            current_section.add_list(list_block)

        # Load images
        self._load_images(document)

        return document

    def _get_numbering_info(self, para_elem: etree._Element) -> tuple[str, int] | None:
        """Get numbering info (numId, ilvl) if paragraph is a list item."""
        ppr = para_elem.find(f"{{{NS['w']}}}pPr", namespaces=NS)
        if ppr is None:
            return None

        numpr = ppr.find(f"{{{NS['w']}}}numPr", namespaces=NS)
        if numpr is None:
            return None

        num_id_elem = numpr.find(f"{{{NS['w']}}}numId", namespaces=NS)
        ilvl_elem = numpr.find(f"{{{NS['w']}}}ilvl", namespaces=NS)

        if num_id_elem is None:
            return None

        num_id = num_id_elem.get(f"{{{NS['w']}}}val", "0")
        if num_id == "0":  # numId 0 means no numbering
            return None

        ilvl = 0
        if ilvl_elem is not None:
            try:
                ilvl = int(ilvl_elem.get(f"{{{NS['w']}}}val", "0"))
            except ValueError:
                pass

        return num_id, ilvl

    def _build_list_from_items(
        self, items: list[tuple[Paragraph, int, str]]
    ) -> ListBlock:
        """Build a ListBlock from a sequence of list item paragraphs."""
        if not items:
            return ListBlock()

        # Determine list type from first item's numbering
        first_num_id = items[0][2]
        list_type = ListType.BULLET

        if first_num_id in self._numbering:
            num_def = self._numbering[first_num_id]
            if "0" in num_def:
                fmt = num_def["0"].get("format", "bullet")
                if fmt in ("decimal", "lowerLetter", "upperLetter", "lowerRoman", "upperRoman"):
                    list_type = ListType.NUMBERED

        root_list = ListBlock(list_type=list_type, level=0)
        list_stack: list[tuple[ListBlock, int]] = [(root_list, -1)]

        for para, level, num_id in items:
            # Find or create the right list at this level
            while list_stack and list_stack[-1][1] >= level:
                list_stack.pop()

            if not list_stack:
                list_stack = [(root_list, -1)]

            current_list, current_level = list_stack[-1]

            if level > current_level + 1:
                # Need to create intermediate levels
                for _ in range(current_level + 1, level):
                    new_list = ListBlock(list_type=list_type, level=len(list_stack))
                    if current_list.items:
                        current_list.items[-1].sub_items.append(
                            ListItem(paragraphs=[], level=len(list_stack))
                        )
                        # This is a placeholder for nesting
                    list_stack.append((new_list, len(list_stack) - 1))
                    current_list = new_list

            # Add item to current list
            item = ListItem(paragraphs=[para], level=level)
            current_list.items.append(item)
            list_stack.append((current_list, level))

        return root_list

    def _parse_paragraph(self, para_elem: etree._Element) -> Paragraph:
        """Parse a paragraph element."""
        # Get paragraph properties
        ppr = para_elem.find(f"{{{NS['w']}}}pPr", namespaces=NS)
        style = self._parse_paragraph_style(ppr)

        paragraph = Paragraph(style=style)

        # Parse content (runs, math, hyperlinks)
        for child in para_elem:
            tag = etree.QName(child).localname

            if tag == "r":
                run = self._parse_run(child)
                if run:
                    paragraph.content.append(run)

            elif tag == "hyperlink":
                hyperlink = self._parse_hyperlink(child)
                if hyperlink:
                    paragraph.content.append(hyperlink)

            elif tag == "oMath":
                math = self._parse_math(child, MathType.INLINE)
                paragraph.content.append(math)

            elif tag == "oMathPara":
                # Display math - may contain multiple oMath elements
                for omath in child.iter(f"{{{NS['m']}}}oMath"):
                    math = self._parse_math(omath, MathType.DISPLAY)
                    paragraph.content.append(math)

        return paragraph

    def _parse_paragraph_style(self, ppr: etree._Element | None) -> ParagraphStyle:
        """Parse paragraph properties into a style."""
        if ppr is None:
            return ParagraphStyle.empty()

        # Get style reference
        pstyle_elem = ppr.find(f"{{{NS['w']}}}pStyle", namespaces=NS)
        style_id = pstyle_elem.get(f"{{{NS['w']}}}val") if pstyle_elem is not None else None

        # Get base style from resolver
        base_style = self._style_resolver.resolve_paragraph_style(style_id)

        # Parse direct formatting (overrides style)
        direct = self._style_resolver._parse_paragraph_props(ppr)

        # Merge: base <- direct
        return base_style.merge_with(direct)

    def _parse_run(self, run_elem: etree._Element) -> Run | None:
        """Parse a run element."""
        # Get run properties
        rpr = run_elem.find(f"{{{NS['w']}}}rPr", namespaces=NS)
        style = self._parse_run_style(rpr)

        # Collect text content
        text_parts = []

        for child in run_elem:
            tag = etree.QName(child).localname

            if tag == "t":
                text_parts.append(child.text or "")

            elif tag == "br":
                br_type = child.get(f"{{{NS['w']}}}type", "")
                if br_type == "page":
                    text_parts.append("\n\\newpage\n")
                else:
                    text_parts.append("\n")

            elif tag == "tab":
                text_parts.append("\t")

            elif tag == "sym":
                # Symbol - try to get character
                char = child.get(f"{{{NS['w']}}}char", "")
                if char:
                    try:
                        text_parts.append(chr(int(char, 16)))
                    except ValueError:
                        text_parts.append("?")

        text = "".join(text_parts)

        if not text:
            return None

        return Run(text=text, style=style)

    def _parse_run_style(self, rpr: etree._Element | None) -> TextStyle:
        """Parse run properties into a style."""
        if rpr is None:
            return TextStyle.empty()

        # Get style reference
        rstyle_elem = rpr.find(f"{{{NS['w']}}}rStyle", namespaces=NS)
        style_id = rstyle_elem.get(f"{{{NS['w']}}}val") if rstyle_elem is not None else None

        # Get base style from resolver
        base_style = self._style_resolver.resolve_run_style(style_id)

        # Parse direct formatting
        direct = self._style_resolver._parse_run_props(rpr)

        # Merge: base <- direct
        return base_style.merge_with(direct)

    def _parse_hyperlink(self, hl_elem: etree._Element) -> Hyperlink | None:
        """Parse a hyperlink element."""
        # Get relationship ID or anchor
        rel_id = hl_elem.get(f"{{{NS['r']}}}id", "")
        anchor = hl_elem.get(f"{{{NS['w']}}}anchor", "")

        url = ""
        if rel_id and rel_id in self._relationships.get("document", {}):
            rel = self._relationships["document"][rel_id]
            url = rel.get("target", "")
        elif anchor:
            url = f"#{anchor}"

        # Parse runs inside hyperlink
        runs = []
        for run_elem in hl_elem.iter(f"{{{NS['w']}}}r"):
            run = self._parse_run(run_elem)
            if run:
                runs.append(run)

        if not runs:
            return None

        return Hyperlink(url=url, runs=runs, bookmark=anchor if anchor else None)

    def _parse_math(self, math_elem: etree._Element, math_type: MathType) -> MathBlock:
        """Parse a math element."""
        # Store original OMML XML for conversion
        omml_xml = etree.tostring(math_elem, encoding="unicode")
        return MathBlock(omml_xml=omml_xml, math_type=math_type)

    def _parse_table(self, tbl_elem: etree._Element) -> Table:
        """Parse a table element."""
        table = Table()

        # Parse table properties
        tblpr = tbl_elem.find(f"{{{NS['w']}}}tblPr", namespaces=NS)
        if tblpr is not None:
            # Alignment
            jc_elem = tblpr.find(f"{{{NS['w']}}}jc", namespaces=NS)
            if jc_elem is not None:
                jc_val = jc_elem.get(f"{{{NS['w']}}}val", "")
                table.alignment = {
                    "left": Alignment.LEFT,
                    "center": Alignment.CENTER,
                    "right": Alignment.RIGHT,
                }.get(jc_val, Alignment.CENTER)

        # Parse table grid (column widths)
        tblgrid = tbl_elem.find(f"{{{NS['w']}}}tblGrid", namespaces=NS)
        if tblgrid is not None:
            for gridcol in tblgrid.iter(f"{{{NS['w']}}}gridCol"):
                width = gridcol.get(f"{{{NS['w']}}}w", "0")
                try:
                    table.column_widths.append(Dimension.from_twips(int(width)))
                except ValueError:
                    pass

        # Parse rows
        for tr_elem in tbl_elem.iter(f"{{{NS['w']}}}tr"):
            row = self._parse_table_row(tr_elem)
            table.rows.append(row)

            # Check if this is a header row
            trpr = tr_elem.find(f"{{{NS['w']}}}trPr", namespaces=NS)
            if trpr is not None:
                tblheader = trpr.find(f"{{{NS['w']}}}tblHeader", namespaces=NS)
                if tblheader is not None:
                    row.is_header = True
                    table.has_header_row = True

        return table

    def _parse_table_row(self, tr_elem: etree._Element) -> TableRow:
        """Parse a table row element."""
        row = TableRow()

        # Parse row properties
        trpr = tr_elem.find(f"{{{NS['w']}}}trPr", namespaces=NS)
        if trpr is not None:
            # Height
            trheight = trpr.find(f"{{{NS['w']}}}trHeight", namespaces=NS)
            if trheight is not None:
                height = trheight.get(f"{{{NS['w']}}}val", "0")
                try:
                    row.height = Dimension.from_twips(int(height))
                except ValueError:
                    pass

        # Parse cells
        for tc_elem in tr_elem.iter(f"{{{NS['w']}}}tc"):
            cell = self._parse_table_cell(tc_elem)
            row.cells.append(cell)

        return row

    def _parse_table_cell(self, tc_elem: etree._Element) -> TableCell:
        """Parse a table cell element."""
        cell = TableCell()

        # Parse cell properties
        tcpr = tc_elem.find(f"{{{NS['w']}}}tcPr", namespaces=NS)
        if tcpr is not None:
            # Width
            tcw = tcpr.find(f"{{{NS['w']}}}tcW", namespaces=NS)
            if tcw is not None:
                width = tcw.get(f"{{{NS['w']}}}w", "0")
                try:
                    cell.width = Dimension.from_twips(int(width))
                except ValueError:
                    pass

            # Grid span (horizontal merge)
            gridspan = tcpr.find(f"{{{NS['w']}}}gridSpan", namespaces=NS)
            if gridspan is not None:
                try:
                    cell.col_span = int(gridspan.get(f"{{{NS['w']}}}val", "1"))
                except ValueError:
                    pass

            # Vertical merge
            vmerge = tcpr.find(f"{{{NS['w']}}}vMerge", namespaces=NS)
            if vmerge is not None:
                merge_val = vmerge.get(f"{{{NS['w']}}}val", "continue")
                if merge_val == "restart":
                    cell.row_span = 1  # Will be updated later
                # "continue" means this cell is merged with above

            # Vertical alignment
            valign = tcpr.find(f"{{{NS['w']}}}vAlign", namespaces=NS)
            if valign is not None:
                cell.vertical_alignment = valign.get(f"{{{NS['w']}}}val", "top")

        # Parse paragraphs in cell
        for p_elem in tc_elem.iter(f"{{{NS['w']}}}p"):
            para = self._parse_paragraph(p_elem)
            cell.paragraphs.append(para)

        return cell

    def _parse_section_props(self, sectpr: etree._Element) -> PageLayout:
        """Parse section properties."""
        # Page size
        width = None
        height = None
        pgsz = sectpr.find(f"{{{NS['w']}}}pgSz", namespaces=NS)
        if pgsz is not None:
            w = pgsz.get(f"{{{NS['w']}}}w")
            h = pgsz.get(f"{{{NS['w']}}}h")
            if w:
                try:
                    width = int(w)
                except ValueError:
                    pass
            if h:
                try:
                    height = int(h)
                except ValueError:
                    pass

        # Page margins
        margin_top = None
        margin_bottom = None
        margin_left = None
        margin_right = None
        header = None
        footer = None
        gutter = None

        pgmar = sectpr.find(f"{{{NS['w']}}}pgMar", namespaces=NS)
        if pgmar is not None:
            for attr, var_name in [
                ("top", "margin_top"),
                ("bottom", "margin_bottom"),
                ("left", "margin_left"),
                ("right", "margin_right"),
                ("header", "header"),
                ("footer", "footer"),
                ("gutter", "gutter"),
            ]:
                val = pgmar.get(f"{{{NS['w']}}}{attr}")
                if val:
                    try:
                        locals()[var_name] = int(val)
                    except ValueError:
                        pass

        return PageLayout.from_docx_section(
            width_twips=width,
            height_twips=height,
            margin_top_twips=margin_top,
            margin_bottom_twips=margin_bottom,
            margin_left_twips=margin_left,
            margin_right_twips=margin_right,
            header_twips=header,
            footer_twips=footer,
            gutter_twips=gutter,
        )

    def _load_images(self, document: Document) -> None:
        """Load embedded images from the DOCX package."""
        if not self._relationships.get("document"):
            return

        for rel_id, rel_info in self._relationships["document"].items():
            rel_type = rel_info.get("type", "")
            target = rel_info.get("target", "")

            # Check if this is an image relationship
            if "image" not in rel_type.lower():
                continue

            # Resolve target path
            if target.startswith("/"):
                image_path = target[1:]
            else:
                image_path = f"word/{target}"

            if image_path not in self._zipfile.namelist():
                continue

            try:
                image_data = self._zipfile.read(image_path)
                filename = Path(target).name

                # Determine content type
                content_type = "image/png"  # Default
                if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
                    content_type = "image/jpeg"
                elif filename.lower().endswith(".gif"):
                    content_type = "image/gif"
                elif filename.lower().endswith(".svg"):
                    content_type = "image/svg+xml"

                image = Image(
                    rel_id=rel_id,
                    filename=filename,
                    content_type=content_type,
                    data=image_data,
                )

                document.register_image(rel_id, image)

            except Exception as e:
                logger.warning(f"Failed to load image {target}: {e}")
