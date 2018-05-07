import copy
from .header_parsing import parse_header


class HeaderError(Exception):
    pass


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

    @classmethod
    def build(cls, *, uri, display_name=None, parameters=None):
        '''Build a new Header from kwargs.'''
        self = object.__new__(cls)
        self._uri = uri
        if display_name and '"' in display_name:
            raise HeaderError('display name cannot contain `"`')
        self._display_name = display_name
        self._parameters = parameters if parameters else {}
        return self

    display_name = property(lambda self: self._display_name)
    parameters = property(lambda self: self._parameters)
    uri = property(lambda self: self._uri)
    tag = property(lambda self: self._parameters.get('tag', None))

    def __str__(self):
        display_name = f'"{self._display_name}" ' if self._display_name else ''
        return f'{display_name}<{self._uri}>'

    def __repr__(self):
        return f'{self.__class__.__name__}({self})'

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def __deepcopy__(self):
        return Header.build(
                uri=copy.deepcopy(self._uri),
                display_name=self.display_name,
                parameters=copy.deepcopy(self._parameters)
        )
