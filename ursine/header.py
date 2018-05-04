from .header_parsing import parse_header


class Header:
    __slots__ = (
        '_display_name',
        '_parameters',
        '_uri',
    )

    def __init__(self, header):
        result = parse_header(header)
        self._display_name = result.display_name
        self._parameters = result.parameters
        self._uri = result.uri

    display_name = property(lambda self: self._display_name)
    parameters = property(lambda self: self._parameters)
    uri = property(lambda self: self._uri)
    tag = property(lambda self: self._parameters.get('tag', None))

    def __str__(self):
        display_name = f'"{self._display_name}" ' if self._display_name else ''
        return f'{display_name}<{str(self._uri)}>'
