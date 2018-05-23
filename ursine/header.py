import copy
import random
import string
import typing as t
from .uri import URI
from .header_parsing import parse_header


def random_tag():
    return ''.join(random.choices(string.hexdigits, k=16))


class HeaderError(Exception):
    pass


class Header:
    '''A SIP Header (Contact/To/From).'''
    __slots__ = (
        '_display_name',
        '_parameters',
        '_uri',
    )

    def __init__(self, header: str):
        result = parse_header(header)
        self._display_name = result.display_name
        self._parameters = result.parameters
        self._uri = result.uri

    @classmethod
    def build(cls, *,
              uri: URI,
              display_name: t.Optional[str]=None,
              parameters: t.Optional[t.Dict[str, str]]=None,
              tag: t.Optional[str]=None) -> 'Header':
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

    def with_display_name(self, display_name: str):
        '''Create a new Header from `self` with a specific display name.'''
        new = copy.deepcopy(self)
        new._display_name = display_name
        new._validate()
        return new

    def with_uri(self, uri: URI):
        '''Create a new Header from `self` with a specific URI.'''
        new = copy.copy(self)
        new._uri = uri
        new._validate()
        return new

    def with_parameters(self, parameters: t.Dict[str, str]):
        '''Create a new Header from `self` with specific parameters.'''
        new = copy.copy(self)
        new._parameters = parameters
        new._validate()
        return new

    def with_tag(self, tag: t.Optional[str]=None):
        '''Create a new Header from `self` guaranteed to have a tag.
        
        If tag is defined the resulting Header will always have the
        given tag value, but if tag is specied or defaulted to None
        a new Header with a randomly generated tag will be returned.
        '''
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
