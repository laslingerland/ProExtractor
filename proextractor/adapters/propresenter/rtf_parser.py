"""Small dependency-free RTF text decoder suitable for ProPresenter text blocks."""

import re


_DESTINATIONS = {"fonttbl", "colortbl", "stylesheet", "info", "pict", "expandedcolortbl", "generator"}


def rtf_to_text(rtf: bytes | str) -> str:
    source = rtf.decode("cp1252", errors="replace") if isinstance(rtf, bytes) else rtf
    output: list[str] = []
    stack: list[tuple[bool, int]] = []
    ignored = False
    unicode_skip = 1
    index = 0
    while index < len(source):
        char = source[index]
        if char == "{":
            stack.append((ignored, unicode_skip))
            index += 1
        elif char == "}":
            if stack:
                ignored, unicode_skip = stack.pop()
            index += 1
        elif char != "\\":
            if not ignored and char not in "\r\n":
                output.append(char)
            index += 1
        else:
            if index + 1 >= len(source):
                break
            next_char = source[index + 1]
            if next_char in "{}\\":
                if not ignored:
                    output.append(next_char)
                index += 2
                continue
            if next_char == "'" and index + 3 < len(source):
                if not ignored:
                    try:
                        output.append(bytes([int(source[index + 2:index + 4], 16)]).decode("cp1252"))
                    except ValueError:
                        pass
                index += 4
                continue
            match = re.match(r"\\([a-zA-Z]+)(-?\d+)? ?", source[index:])
            if not match:
                if next_char == "*":
                    ignored = True
                index += 2
                continue
            word, parameter = match.group(1), match.group(2)
            index += len(match.group(0))
            if word in _DESTINATIONS:
                ignored = True
            elif word == "uc" and parameter:
                unicode_skip = int(parameter)
            elif word == "u" and parameter and not ignored:
                value = int(parameter)
                output.append(chr(value if value >= 0 else value + 65536))
                index += unicode_skip
            elif word in {"par", "line"} and not ignored:
                output.append("\n")
            elif word == "tab" and not ignored:
                output.append("\t")
    text = "".join(output).replace("\xa0", " ")
    return "\n".join(line.strip() for line in text.splitlines()).strip()

