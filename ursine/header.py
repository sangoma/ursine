import copy
import random
import string
from .header_parsing import parse_header


def random_tag():
    return ''.join([random.choice(string.hexdigits) for _ in range(16)])


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
        self._display_name = display_name
        self._parameters = parameters if parameters else {}
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
        new = copy.deepcopy(self)
        new._uri = uri
        new._validate()
        return new

    def with_parameters(self, parameters):
        new = copy.deepcopy(self)
        new._parameters = parameters
        new._validate()
        return new

    def with_tag(self, tag):
        if self.tag == tag:
            return self
        new = copy.deepcopy(self)
        if tag:
            new._parameters['tag'] = tag
        elif 'tag' in new._parameters:
            del new._parameters['tag']
        return new

    def with_default_tag(self, tag=None):
        '''Like `with_tag`, but will only alter
        the tag if one is not already defined.'''
        if self.tag:
            return self
        if not tag:
            tag = random_tag()
        return self.with_tag(tag)

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

    def __deepcopy__(self, memo):
        return Header.build(
                uri=copy.deepcopy(self._uri),
                display_name=self.display_name,
                parameters=copy.copy(self._parameters)
        )
