import pkg_resources


def get_text(name: str) -> str:
    try:
        content = pkg_resources.resource_string(__name__, 'data/' + name)
        text = content.decode('utf-8')
        return text
    except FileNotFoundError:
        raise Exception(f'Resource not found: {name}')
