"""
XML namespace handling for OOXML (Office Open XML).

Provides convenient access to DOCX XML namespaces and qualified names.
"""

from typing import Final

# Primary namespace URIs
NS: Final[dict[str, str]] = {
    # Word processing
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    # Drawing
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    # Relationships
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
    # Math
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    # Content types
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    # Core properties
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    # VML (legacy drawings)
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
    # Markup compatibility
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    # Charts
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    # Extended properties
    "ep": "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties",
}

# Namespace map for lxml
nsmap: Final[dict[str, str]] = NS.copy()


def qn(tag: str) -> str:
    """
    Create a qualified name from a prefixed tag.

    Example:
        qn("w:p") -> "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"

    Args:
        tag: Tag with namespace prefix (e.g., "w:p", "m:oMath")

    Returns:
        Fully qualified tag name
    """
    if ":" not in tag:
        return tag

    prefix, local = tag.split(":", 1)
    if prefix not in NS:
        raise ValueError(f"Unknown namespace prefix: {prefix}")

    return f"{{{NS[prefix]}}}{local}"


def local_name(tag: str) -> str:
    """
    Extract local name from a qualified tag.

    Example:
        local_name("{http://...}p") -> "p"

    Args:
        tag: Fully qualified tag name

    Returns:
        Local part of the tag
    """
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def get_prefix(tag: str) -> str | None:
    """
    Get namespace prefix from a qualified tag.

    Args:
        tag: Fully qualified tag name

    Returns:
        Namespace prefix or None
    """
    if not tag.startswith("{"):
        return None

    uri = tag[1:].split("}", 1)[0]
    for prefix, ns_uri in NS.items():
        if ns_uri == uri:
            return prefix
    return None


# Common qualified names (pre-computed for performance)
class W:
    """Word processing namespace qualified names."""

    DOCUMENT = qn("w:document")
    BODY = qn("w:body")
    P = qn("w:p")  # Paragraph
    R = qn("w:r")  # Run
    T = qn("w:t")  # Text
    BR = qn("w:br")  # Break
    TAB = qn("w:tab")  # Tab
    SYM = qn("w:sym")  # Symbol

    # Paragraph properties
    PPR = qn("w:pPr")
    PSTYLE = qn("w:pStyle")
    JC = qn("w:jc")  # Justification
    SPACING = qn("w:spacing")
    IND = qn("w:ind")  # Indentation
    OUTLINE_LVL = qn("w:outlineLvl")

    # Run properties
    RPR = qn("w:rPr")
    RSTYLE = qn("w:rStyle")
    B = qn("w:b")  # Bold
    I = qn("w:i")  # Italic
    U = qn("w:u")  # Underline
    STRIKE = qn("w:strike")
    DSTRIKE = qn("w:dstrike")  # Double strike
    VERTALING = qn("w:vertAlign")
    SMALLCAPS = qn("w:smallCaps")
    CAPS = qn("w:caps")
    COLOR = qn("w:color")
    HIGHLIGHT = qn("w:highlight")
    SZ = qn("w:sz")  # Font size
    SZCS = qn("w:szCs")  # Complex script font size
    RFONTS = qn("w:rFonts")  # Fonts

    # Tables
    TBL = qn("w:tbl")  # Table
    TR = qn("w:tr")  # Table row
    TC = qn("w:tc")  # Table cell
    TBLPR = qn("w:tblPr")  # Table properties
    TBLGRID = qn("w:tblGrid")  # Table grid
    GRIDCOL = qn("w:gridCol")  # Grid column
    TRPR = qn("w:trPr")  # Row properties
    TCPR = qn("w:tcPr")  # Cell properties
    TCBORDERS = qn("w:tcBorders")
    GRIDSPAN = qn("w:gridSpan")
    VMERGE = qn("w:vMerge")
    HMERGE = qn("w:hMerge")
    TCW = qn("w:tcW")  # Cell width

    # Lists
    NUMPR = qn("w:numPr")  # Numbering properties
    ILVL = qn("w:ilvl")  # List level
    NUMID = qn("w:numId")  # Numbering ID

    # Hyperlinks
    HYPERLINK = qn("w:hyperlink")
    BOOKMARKSTART = qn("w:bookmarkStart")
    BOOKMARKEND = qn("w:bookmarkEnd")

    # Sections
    SECTPR = qn("w:sectPr")
    PGSZ = qn("w:pgSz")  # Page size
    PGMAR = qn("w:pgMar")  # Page margins
    COLS = qn("w:cols")  # Columns
    HEADERREFERENCE = qn("w:headerReference")
    FOOTERREFERENCE = qn("w:footerReference")

    # Drawings
    DRAWING = qn("w:drawing")

    # Attributes
    VAL = qn("w:val")


class M:
    """Math namespace qualified names."""

    OMATH = qn("m:oMath")  # Math block
    OMATHPARA = qn("m:oMathPara")  # Math paragraph (display)

    # Math elements
    R = qn("m:r")  # Math run
    T = qn("m:t")  # Math text
    F = qn("m:f")  # Fraction
    NUM = qn("m:num")  # Numerator
    DEN = qn("m:den")  # Denominator
    RAD = qn("m:rad")  # Radical
    DEG = qn("m:deg")  # Degree
    E = qn("m:e")  # Base/element
    SUB = qn("m:sub")  # Subscript
    SUP = qn("m:sup")  # Superscript
    SSUB = qn("m:sSub")  # Subscript structure
    SSUP = qn("m:sSup")  # Superscript structure
    SSUBSUP = qn("m:sSubSup")  # Sub-superscript
    SPRE = qn("m:sPre")  # Pre-sub/superscript
    NARY = qn("m:nary")  # N-ary operator
    LIM = qn("m:lim")  # Limit
    LIMLOW = qn("m:limLow")  # Lower limit
    LIMUP = qn("m:limUpp")  # Upper limit
    M = qn("m:m")  # Matrix
    MR = qn("m:mr")  # Matrix row
    D = qn("m:d")  # Delimiter
    DELPRIM = qn("m:dPr")  # Delimiter properties
    BEGCHR = qn("m:begChr")  # Begin character
    ENDCHR = qn("m:endChr")  # End character
    SEPCHR = qn("m:sepChr")  # Separator character
    EQU = qn("m:eqArr")  # Equation array
    BAR = qn("m:bar")  # Bar/overline
    BARPR = qn("m:barPr")  # Bar properties
    POS = qn("m:pos")  # Position (top/bot)
    ACC = qn("m:acc")  # Accent
    ACCPR = qn("m:accPr")  # Accent properties
    CHR = qn("m:chr")  # Character
    BOX = qn("m:box")  # Box
    FUNC = qn("m:func")  # Function
    FNAME = qn("m:fName")  # Function name
    GROUPCHR = qn("m:groupChr")  # Group character
    BORDERBOX = qn("m:borderBox")  # Border box
    PHANT = qn("m:phant")  # Phantom

    # Properties
    NARYPR = qn("m:naryPr")
    CHR_ATTR = qn("m:chr")
    LIMLOCP = qn("m:limLoc")
    SUBHIDE = qn("m:subHide")
    SUPHIDE = qn("m:supHide")
    RADPR = qn("m:radPr")
    DEGHIDE = qn("m:degHide")


class R:
    """Relationship namespace qualified names."""

    ID = qn("r:id")
    EMBED = qn("r:embed")
    LINK = qn("r:link")


class A:
    """Drawing namespace qualified names."""

    GRAPHIC = qn("a:graphic")
    GRAPHICDATA = qn("a:graphicData")
    BLIP = qn("a:blip")


class WP:
    """Word processing drawing namespace qualified names."""

    INLINE = qn("wp:inline")
    ANCHOR = qn("wp:anchor")
    EXTENT = qn("wp:extent")
    DOCPR = qn("wp:docPr")


class PIC:
    """Picture namespace qualified names."""

    PIC = qn("pic:pic")
    BLIPFILL = qn("pic:blipFill")
