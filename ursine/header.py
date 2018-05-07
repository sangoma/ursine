import copy
import random
import string
from .header_parsing import parse_header


def random_tag():
    return ''.join(random.choices(string.hexdigits, k=16))


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
    def build(cls, *, uri, display_name=None, parameters=None, tag=None):
        '''Build a new Header from kwargs.'''
        self = object.__new__(cls)
        self._uri = uri
        self._display_name = display_name
        self._parameters = parameters if parameters else {}
        if tag:
            self._parameters['tag'] = tag
        self._validate()
        return self

    display_name = property(lambda self: self._display_name)
    parameters = property(lambda self: self._parameters)
    uri = property(lambda self: self._uri)
    tag = property(lambda self: self._parameters.get('tag', None))

    def with_display_name(self, display_name):
        new = copy.deepcopy(self)
        new._display_name = display_name
        new._validate()
        return new

    def with_uri(self, uri):
        new = copy.copy(self)
        new._uri = uri
        new._validate()
        return new

    def with_parameters(self, parameters):
        new = copy.copy(self)
        new._parameters = parameters
        new._validate()
        return new

    def with_tag(self, tag):
        if tag and self.tag == tag:
            return self
        new = copy.copy(self)
        new._parameters = copy.copy(self._parameters)
        if tag is None:
            tag = random_tag()
        new._parameters['tag'] = tag
        return new

    def _validate(self):
        '''Ensure correctness of properties.'''
        if self.display_name and '"' in self.display_name:
            raise HeaderError('display name cannot contain `"`')

    def __str__(self):
        display_name = f'"{self._display_name}" ' if self._display_name else ''
        param_pairs = ';'.join(['='.join([k, v])
                                for k, v in sorted(self._parameters.items())])
        params = f';{param_pairs}' if param_pairs else ''
        return f'{display_name}<{self._uri}>{params}'

    def __repr__(self):
        return f'{self.__class__.__name__}({self})'

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def __copy__(self):
        return Header.build(
                uri=copy.copy(self._uri),
                display_name=self.display_name,
                parameters=self._parameters,
        )
