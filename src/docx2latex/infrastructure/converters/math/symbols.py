"""
Symbol mapping for math conversion.

Maps Unicode characters and OMML symbols to LaTeX commands.
"""

from typing import Final

# Greek letters - lowercase
GREEK_LOWER: Final[dict[str, str]] = {
    "α": r"\alpha",
    "β": r"\beta",
    "γ": r"\gamma",
    "δ": r"\delta",
    "ε": r"\varepsilon",
    "ϵ": r"\epsilon",
    "ζ": r"\zeta",
    "η": r"\eta",
    "θ": r"\theta",
    "ϑ": r"\vartheta",
    "ι": r"\iota",
    "κ": r"\kappa",
    "ϰ": r"\varkappa",
    "λ": r"\lambda",
    "μ": r"\mu",
    "ν": r"\nu",
    "ξ": r"\xi",
    "π": r"\pi",
    "ϖ": r"\varpi",
    "ρ": r"\rho",
    "ϱ": r"\varrho",
    "σ": r"\sigma",
    "ς": r"\varsigma",
    "τ": r"\tau",
    "υ": r"\upsilon",
    "φ": r"\varphi",
    "ϕ": r"\phi",
    "χ": r"\chi",
    "ψ": r"\psi",
    "ω": r"\omega",
}

# Greek letters - uppercase
GREEK_UPPER: Final[dict[str, str]] = {
    "Α": "A",
    "Β": "B",
    "Γ": r"\Gamma",
    "Δ": r"\Delta",
    "Ε": "E",
    "Ζ": "Z",
    "Η": "H",
    "Θ": r"\Theta",
    "Ι": "I",
    "Κ": "K",
    "Λ": r"\Lambda",
    "Μ": "M",
    "Ν": "N",
    "Ξ": r"\Xi",
    "Ο": "O",
    "Π": r"\Pi",
    "Ρ": "P",
    "Σ": r"\Sigma",
    "Τ": "T",
    "Υ": r"\Upsilon",
    "Φ": r"\Phi",
    "Χ": "X",
    "Ψ": r"\Psi",
    "Ω": r"\Omega",
}

# Mathematical operators
OPERATORS: Final[dict[str, str]] = {
    # Special characters that need escaping
    "%": r"\%",
    "#": r"\#",
    "&": r"\&",
    "$": r"\$",
    "_": r"\_",
    # Basic arithmetic
    "−": "-",
    "×": r"\times",
    "÷": r"\div",
    "±": r"\pm",
    "∓": r"\mp",
    "·": r"\cdot",
    "∗": r"\ast",
    "⋆": r"\star",
    "∘": r"\circ",
    "•": r"\bullet",
    # Relations
    "≠": r"\neq",
    "≤": r"\leq",
    "≥": r"\geq",
    "≪": r"\ll",
    "≫": r"\gg",
    "≈": r"\approx",
    "≃": r"\simeq",
    "≅": r"\cong",
    "≡": r"\equiv",
    "∼": r"\sim",
    "∝": r"\propto",
    "≺": r"\prec",
    "≻": r"\succ",
    "⪯": r"\preceq",
    "⪰": r"\succeq",
    # Arrows
    "→": r"\rightarrow",
    "←": r"\leftarrow",
    "↔": r"\leftrightarrow",
    "⇒": r"\Rightarrow",
    "⇐": r"\Leftarrow",
    "⇔": r"\Leftrightarrow",
    "↦": r"\mapsto",
    "↑": r"\uparrow",
    "↓": r"\downarrow",
    "⇑": r"\Uparrow",
    "⇓": r"\Downarrow",
    "↗": r"\nearrow",
    "↘": r"\searrow",
    "↙": r"\swarrow",
    "↖": r"\nwarrow",
    "⟵": r"\longleftarrow",
    "⟶": r"\longrightarrow",
    "⟷": r"\longleftrightarrow",
    "⟹": r"\Longrightarrow",
    "⟸": r"\Longleftarrow",
    "⟺": r"\Longleftrightarrow",
    # Set theory
    "∈": r"\in",
    "∉": r"\notin",
    "∋": r"\ni",
    "⊂": r"\subset",
    "⊃": r"\supset",
    "⊆": r"\subseteq",
    "⊇": r"\supseteq",
    "⊊": r"\subsetneq",
    "⊋": r"\supsetneq",
    "∪": r"\cup",
    "∩": r"\cap",
    "∅": r"\emptyset",
    "⊕": r"\oplus",
    "⊗": r"\otimes",
    "⊖": r"\ominus",
    "⊘": r"\oslash",
    # Logic
    "∧": r"\land",
    "∨": r"\lor",
    "¬": r"\neg",
    "∀": r"\forall",
    "∃": r"\exists",
    "∄": r"\nexists",
    "⊢": r"\vdash",
    "⊣": r"\dashv",
    "⊤": r"\top",
    "⊥": r"\bot",
    "⊨": r"\models",
    # Calculus / Analysis
    "∂": r"\partial",
    "∞": r"\infty",
    "∇": r"\nabla",
    "√": r"\sqrt",
    "∫": r"\int",
    "∬": r"\iint",
    "∭": r"\iiint",
    "∮": r"\oint",
    "∑": r"\sum",
    "∏": r"\prod",
    "∐": r"\coprod",
    # Miscellaneous
    "°": r"^{\circ}",
    "′": "'",
    "″": "''",
    "‴": "'''",
    "ℓ": r"\ell",
    "ℏ": r"\hbar",
    "ℜ": r"\Re",
    "ℑ": r"\Im",
    "℘": r"\wp",
    "ℵ": r"\aleph",
    "∠": r"\angle",
    "∡": r"\measuredangle",
    "⊥": r"\perp",
    "∥": r"\parallel",
    "⋮": r"\vdots",
    "⋯": r"\cdots",
    "⋱": r"\ddots",
    "…": r"\ldots",
    "□": r"\square",
    "△": r"\triangle",
    "▽": r"\triangledown",
    "★": r"\bigstar",
    "♠": r"\spadesuit",
    "♥": r"\heartsuit",
    "♦": r"\diamondsuit",
    "♣": r"\clubsuit",
}

# Superscript digits
SUPERSCRIPTS: Final[dict[str, str]] = {
    "⁰": "^{0}",
    "¹": "^{1}",
    "²": "^{2}",
    "³": "^{3}",
    "⁴": "^{4}",
    "⁵": "^{5}",
    "⁶": "^{6}",
    "⁷": "^{7}",
    "⁸": "^{8}",
    "⁹": "^{9}",
    "⁺": "^{+}",
    "⁻": "^{-}",
    "⁼": "^{=}",
    "⁽": "^{(}",
    "⁾": "^{)}",
    "ⁿ": "^{n}",
    "ⁱ": "^{i}",
}

# Subscript digits
SUBSCRIPTS: Final[dict[str, str]] = {
    "₀": "_{0}",
    "₁": "_{1}",
    "₂": "_{2}",
    "₃": "_{3}",
    "₄": "_{4}",
    "₅": "_{5}",
    "₆": "_{6}",
    "₇": "_{7}",
    "₈": "_{8}",
    "₉": "_{9}",
    "₊": "_{+}",
    "₋": "_{-}",
    "₌": "_{=}",
    "₍": "_{(}",
    "₎": "_{)}",
}

# Math accents
ACCENTS: Final[dict[str, str]] = {
    "̂": r"\hat",  # combining circumflex
    "̃": r"\tilde",  # combining tilde
    "̄": r"\bar",  # combining macron
    "̇": r"\dot",  # combining dot above
    "̈": r"\ddot",  # combining diaeresis
    "⃗": r"\vec",  # combining right arrow above
    "̆": r"\breve",  # combining breve
    "̌": r"\check",  # combining caron
    "̊": r"\mathring",  # combining ring above
}

# N-ary operators (big operators with limits)
NARY_OPERATORS: Final[dict[str, str]] = {
    "∑": r"\sum",
    "∏": r"\prod",
    "∐": r"\coprod",
    "∫": r"\int",
    "∬": r"\iint",
    "∭": r"\iiint",
    "∮": r"\oint",
    "⋀": r"\bigwedge",
    "⋁": r"\bigvee",
    "⋂": r"\bigcap",
    "⋃": r"\bigcup",
    "⨁": r"\bigoplus",
    "⨂": r"\bigotimes",
    "⨀": r"\bigodot",
    "⨄": r"\biguplus",
    "⨆": r"\bigsqcup",
}

# Function names that should use \operatorname or be recognized
FUNCTION_NAMES: Final[set[str]] = {
    "sin", "cos", "tan", "cot", "sec", "csc",
    "sinh", "cosh", "tanh", "coth", "sech", "csch",
    "arcsin", "arccos", "arctan", "arccot",
    "asin", "acos", "atan", "acot",
    "exp", "log", "ln", "lg",
    "lim", "liminf", "limsup",
    "max", "min", "sup", "inf",
    "arg", "det", "dim", "gcd", "hom", "ker", "deg",
    "Pr", "mod",
}

# Bracket pairs
BRACKETS: Final[dict[str, tuple[str, str]]] = {
    "(": (r"\left(", r"\right)"),
    "[": (r"\left[", r"\right]"),
    "{": (r"\left\{", r"\right\}"),
    "⟨": (r"\left\langle", r"\right\rangle"),
    "|": (r"\left|", r"\right|"),
    "‖": (r"\left\|", r"\right\|"),
    "⌈": (r"\left\lceil", r"\right\rceil"),
    "⌊": (r"\left\lfloor", r"\right\rfloor"),
}


class SymbolMapper:
    """
    Maps symbols from OMML/Unicode to LaTeX.

    Provides comprehensive symbol translation for math conversion.
    """

    def __init__(self) -> None:
        # Combine all mappings
        self._map: dict[str, str] = {}
        self._map.update(GREEK_LOWER)
        self._map.update(GREEK_UPPER)
        self._map.update(OPERATORS)
        self._map.update(SUPERSCRIPTS)
        self._map.update(SUBSCRIPTS)

    # Invisible characters that should be stripped
    INVISIBLE_CHARS = {
        "\u200b",  # Zero-width space
        "\u200c",  # Zero-width non-joiner
        "\u200d",  # Zero-width joiner
        "\u2060",  # Word joiner
        "\ufeff",  # Zero-width no-break space (BOM)
    }

    def map_char(self, char: str) -> str:
        """
        Map a single character to LaTeX.

        Args:
            char: Unicode character

        Returns:
            LaTeX equivalent or original character, empty string for invisible chars
        """
        # Strip invisible characters
        if char in self.INVISIBLE_CHARS:
            return ""
        return self._map.get(char, char)

    def map_text(self, text: str) -> str:
        """
        Map a string of characters to LaTeX.

        Args:
            text: Unicode text

        Returns:
            LaTeX equivalent text
        """
        result = []
        for i, char in enumerate(text):
            mapped = self.map_char(char)
            result.append(mapped)

            # Add space after LaTeX commands ending with letter if followed by letter
            # e.g., \times followed by P should become \times P, not \timesP
            if (mapped.startswith("\\") and mapped[-1].isalpha()
                    and i + 1 < len(text) and text[i + 1].isalpha()):
                result.append(" ")

        return "".join(result)

    def is_function_name(self, name: str) -> bool:
        """Check if a name is a recognized function."""
        return name.lower() in FUNCTION_NAMES

    def get_function_latex(self, name: str) -> str:
        """
        Get LaTeX representation of a function name.

        Args:
            name: Function name

        Returns:
            LaTeX command (e.g., \\sin, \\operatorname{custom})
        """
        lower_name = name.lower()
        if lower_name in FUNCTION_NAMES:
            # Check for standard functions with built-in commands
            standard = {"sin", "cos", "tan", "cot", "sec", "csc",
                       "sinh", "cosh", "tanh", "coth",
                       "arcsin", "arccos", "arctan",
                       "exp", "log", "ln", "lg",
                       "lim", "liminf", "limsup",
                       "max", "min", "sup", "inf",
                       "arg", "det", "dim", "gcd", "hom", "ker", "deg", "Pr"}
            if lower_name in standard:
                return rf"\{lower_name}"
            return rf"\operatorname{{{name}}}"
        return rf"\operatorname{{{name}}}"

    def is_nary_operator(self, char: str) -> bool:
        """Check if character is an n-ary (big) operator."""
        return char in NARY_OPERATORS

    def get_nary_latex(self, char: str) -> str:
        """Get LaTeX command for n-ary operator."""
        return NARY_OPERATORS.get(char, char)

    def get_accent_latex(self, accent: str) -> str | None:
        """Get LaTeX accent command."""
        return ACCENTS.get(accent)

    def get_bracket_pair(self, open_char: str) -> tuple[str, str] | None:
        """Get bracket pair for auto-sizing."""
        return BRACKETS.get(open_char)
