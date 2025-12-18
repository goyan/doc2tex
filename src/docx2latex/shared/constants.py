"""
Constants used throughout the application.

Includes XML namespaces, LaTeX special characters, and other configuration.
"""

from typing import Final

# OOXML (Office Open XML) namespaces used in DOCX files
OOXML_NS: Final[dict[str, str]] = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
}

# LaTeX special characters that need escaping
LATEX_SPECIAL_CHARS: Final[dict[str, str]] = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
    "<": r"\textless{}",
    ">": r"\textgreater{}",
    "|": r"\textbar{}",
    '"': r"''",
}

# Characters that don't need escaping in math mode
LATEX_MATH_SAFE_CHARS: Final[set[str]] = {
    "^", "_", "{", "}", "\\", "$",
}

# Supported image formats
SUPPORTED_IMAGE_FORMATS: Final[set[str]] = {
    ".png", ".jpg", ".jpeg", ".pdf", ".eps", ".svg",
}

# EMU (English Metric Units) conversion - DOCX uses EMUs for measurements
EMU_PER_INCH: Final[int] = 914400
EMU_PER_CM: Final[int] = 360000
EMU_PER_PT: Final[float] = 914400 / 72

# Twips conversion - used for some measurements in DOCX
TWIPS_PER_INCH: Final[int] = 1440
TWIPS_PER_PT: Final[float] = 20

# Half-points - used for font sizes in DOCX
HALF_POINTS_PER_PT: Final[int] = 2

# Default LaTeX document class options
DEFAULT_DOCUMENT_CLASS: Final[str] = "article"
DEFAULT_FONT_SIZE: Final[int] = 11
DEFAULT_PAPER_SIZE: Final[str] = "a4paper"

# Math delimiters
INLINE_MATH_START: Final[str] = "$"
INLINE_MATH_END: Final[str] = "$"
DISPLAY_MATH_START: Final[str] = r"\["
DISPLAY_MATH_END: Final[str] = r"\]"

# Unicode math operators that need special handling
UNICODE_MATH_OPERATORS: Final[dict[str, str]] = {
    "\u2212": "-",  # Minus sign
    "\u00d7": r"\times",  # Multiplication sign
    "\u00f7": r"\div",  # Division sign
    "\u2264": r"\leq",  # Less than or equal
    "\u2265": r"\geq",  # Greater than or equal
    "\u2260": r"\neq",  # Not equal
    "\u00b1": r"\pm",  # Plus-minus
    "\u2213": r"\mp",  # Minus-plus
    "\u221e": r"\infty",  # Infinity
    "\u2202": r"\partial",  # Partial derivative
    "\u2211": r"\sum",  # Summation
    "\u220f": r"\prod",  # Product
    "\u222b": r"\int",  # Integral
    "\u222c": r"\iint",  # Double integral
    "\u222d": r"\iiint",  # Triple integral
    "\u221a": r"\sqrt",  # Square root
    "\u00b2": "^{2}",  # Superscript 2
    "\u00b3": "^{3}",  # Superscript 3
    "\u2070": "^{0}",  # Superscript 0
    "\u00b9": "^{1}",  # Superscript 1
    "\u2074": "^{4}",  # Superscript 4
    "\u2075": "^{5}",  # Superscript 5
    "\u2076": "^{6}",  # Superscript 6
    "\u2077": "^{7}",  # Superscript 7
    "\u2078": "^{8}",  # Superscript 8
    "\u2079": "^{9}",  # Superscript 9
    "\u207a": "^{+}",  # Superscript +
    "\u207b": "^{-}",  # Superscript -
    "\u2080": "_{0}",  # Subscript 0
    "\u2081": "_{1}",  # Subscript 1
    "\u2082": "_{2}",  # Subscript 2
    "\u2083": "_{3}",  # Subscript 3
    "\u2084": "_{4}",  # Subscript 4
    "\u2085": "_{5}",  # Subscript 5
    "\u2086": "_{6}",  # Subscript 6
    "\u2087": "_{7}",  # Subscript 7
    "\u2088": "_{8}",  # Subscript 8
    "\u2089": "_{9}",  # Subscript 9
    "\u2192": r"\rightarrow",  # Right arrow
    "\u2190": r"\leftarrow",  # Left arrow
    "\u2194": r"\leftrightarrow",  # Left-right arrow
    "\u21d2": r"\Rightarrow",  # Double right arrow
    "\u21d0": r"\Leftarrow",  # Double left arrow
    "\u21d4": r"\Leftrightarrow",  # Double left-right arrow
    "\u2200": r"\forall",  # For all
    "\u2203": r"\exists",  # Exists
    "\u2204": r"\nexists",  # Not exists
    "\u2208": r"\in",  # Element of
    "\u2209": r"\notin",  # Not element of
    "\u2282": r"\subset",  # Subset
    "\u2283": r"\supset",  # Superset
    "\u2286": r"\subseteq",  # Subset or equal
    "\u2287": r"\supseteq",  # Superset or equal
    "\u222a": r"\cup",  # Union
    "\u2229": r"\cap",  # Intersection
    "\u2205": r"\emptyset",  # Empty set
    "\u2227": r"\land",  # Logical and
    "\u2228": r"\lor",  # Logical or
    "\u00ac": r"\neg",  # Logical not
    "\u22c5": r"\cdot",  # Dot operator
    "\u2026": r"\ldots",  # Horizontal ellipsis
    "\u22ef": r"\cdots",  # Centered horizontal ellipsis
    "\u22ee": r"\vdots",  # Vertical ellipsis
    "\u22f1": r"\ddots",  # Diagonal ellipsis
    "\u2248": r"\approx",  # Approximately equal
    "\u2261": r"\equiv",  # Identical to
    "\u221d": r"\propto",  # Proportional to
    "\u2225": r"\parallel",  # Parallel
    "\u22a5": r"\perp",  # Perpendicular
    "\u2220": r"\angle",  # Angle
    "\u00b0": r"^{\circ}",  # Degree
    "\u2032": "'",  # Prime
    "\u2033": "''",  # Double prime
    "\u2034": "'''",  # Triple prime
}

# Greek letters mapping (lowercase)
GREEK_LOWERCASE: Final[dict[str, str]] = {
    "\u03b1": r"\alpha",
    "\u03b2": r"\beta",
    "\u03b3": r"\gamma",
    "\u03b4": r"\delta",
    "\u03b5": r"\varepsilon",
    "\u03b6": r"\zeta",
    "\u03b7": r"\eta",
    "\u03b8": r"\theta",
    "\u03b9": r"\iota",
    "\u03ba": r"\kappa",
    "\u03bb": r"\lambda",
    "\u03bc": r"\mu",
    "\u03bd": r"\nu",
    "\u03be": r"\xi",
    "\u03bf": "o",  # omicron - same as Latin o
    "\u03c0": r"\pi",
    "\u03c1": r"\rho",
    "\u03c2": r"\varsigma",
    "\u03c3": r"\sigma",
    "\u03c4": r"\tau",
    "\u03c5": r"\upsilon",
    "\u03c6": r"\varphi",
    "\u03c7": r"\chi",
    "\u03c8": r"\psi",
    "\u03c9": r"\omega",
    # Variant forms
    "\u03d1": r"\vartheta",
    "\u03d5": r"\phi",
    "\u03d6": r"\varpi",
    "\u03f0": r"\varkappa",
    "\u03f1": r"\varrho",
    "\u03f5": r"\epsilon",
}

# Greek letters mapping (uppercase)
GREEK_UPPERCASE: Final[dict[str, str]] = {
    "\u0391": "A",  # Alpha - same as Latin A
    "\u0392": "B",  # Beta
    "\u0393": r"\Gamma",
    "\u0394": r"\Delta",
    "\u0395": "E",  # Epsilon
    "\u0396": "Z",  # Zeta
    "\u0397": "H",  # Eta
    "\u0398": r"\Theta",
    "\u0399": "I",  # Iota
    "\u039a": "K",  # Kappa
    "\u039b": r"\Lambda",
    "\u039c": "M",  # Mu
    "\u039d": "N",  # Nu
    "\u039e": r"\Xi",
    "\u039f": "O",  # Omicron
    "\u03a0": r"\Pi",
    "\u03a1": "P",  # Rho
    "\u03a3": r"\Sigma",
    "\u03a4": "T",  # Tau
    "\u03a5": r"\Upsilon",
    "\u03a6": r"\Phi",
    "\u03a7": "X",  # Chi
    "\u03a8": r"\Psi",
    "\u03a9": r"\Omega",
}

# Combined Greek mapping
GREEK_LETTERS: Final[dict[str, str]] = {**GREEK_LOWERCASE, **GREEK_UPPERCASE}
