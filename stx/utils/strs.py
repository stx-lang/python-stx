

def crop_text(text: str, length: int, append_ellipsis=True) -> str:
    if len(text) <= length:
        return text

    return text[:length] + '...'
