import string
from typing import TextIO, Any

entities = {
    # Main Entities
    160: '&nbsp;',
    60: '&lt;',
    62: '&gt;',
    38: '&amp;',
    34: '&quot;',
    39: '&apos;',

    # Mathematical Symbols
    8704: '&forall;',
    8706: '&part;',
    8707: '&exist;',
    8709: '&empty;',
    8711: '&nabla;',
    8712: '&isin;',
    8713: '&notin;',
    8715: '&ni;',
    8719: '&prod;',
    8721: '&sum;',

    # Greek Letters
    913: '&Alpha;',
    914: '&Beta;',
    915: '&Gamma;',
    916: '&Delta;',
    917: '&Epsilon;',
    918: '&Zeta;',

    # Other Entities
    162: '&cent;',
    163: '&pound;',
    165: '&yen;',
    169: '&copy;',
    174: '&reg;',
    8364: '&euro;',
    8482: '&trade;',
    8592: '&larr;',
    8593: '&uarr;',
    8594: '&rarr;',
    8595: '&darr;',
    9824: '&spades;',
    9827: '&clubs;',
    9829: '&hearts;',
    9830: '&diams;',
}


def write_text(value: Any, out: TextIO):
    if value is None:
        return

    for c in str(value):
        code = ord(c)
        entity = entities.get(code)

        if entity is not None:
            out.write(entity)
        # Non-text control codes
        elif code not in [9, 10, 13] and (code <= 31 or (127 <= code <= 159)):
            out.write(f'&#{code};')
        else:
            out.write(c)
