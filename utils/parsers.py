def parse_card_line(line: str):
    parts = line.strip().split('|')
    if len(parts) == 4:
        return {
            "cc": parts[0],
            "mm": parts[1],
            "yy": parts[2],
            "cvv": parts[3]
        }
    return None
