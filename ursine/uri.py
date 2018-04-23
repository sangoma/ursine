'''URI object for parsing/building sip URIs with optional contact.'''
import copy
from typing import Optional
from multidict import MultiDict
from .parsing import (
    parse_contact,
    parse_scheme,
    parse_user_part,
    parse_host,
    parse_port,
    parse_parameters,
    parse_headers,
)


class URI:
    __slots__ = (
        '_contact',
        '_scheme',
        '_user',
        '_password',
        '_host',
        '_port',
        '_parameters',
        '_headers',
    )

    contact = property(lambda self: self._contact)
    scheme = property(lambda self: self._scheme)
    user = property(lambda self: self._user)
    password = property(lambda self: self._password)
    host = property(lambda self: self._host)
    port = property(lambda self: self._port)
    parameters = property(lambda self: self._parameters)
    headers = property(lambda self: self._headers)
    transport = property(lambda self: self.parameters.get('transport'))
    tag = property(lambda self: self.parameters.get('tag'))

    def __init__(self, uri: str):
        '''Parse a uri string into a URI.'''
        the_rest = uri
        self._contact, the_rest = parse_contact(the_rest)
        self._scheme, the_rest = parse_scheme(the_rest)
        self._user, self._password, the_rest = parse_user_part(the_rest)
        self._host, the_rest = parse_host(the_rest)
        self._port, the_rest = parse_port(the_rest)
        self._parameters, the_rest = parse_parameters(the_rest)
        self._headers, the_rest = parse_headers(the_rest)
        if len(the_rest) > 0:
            raise ValueError(f'cannot parse {uri}')
        self._validate_and_default()

    @classmethod
    def build(cls, *,
              contact: Optional[str] = None,
              scheme: str,
              user: Optional[str]=None,
              password: Optional[str]=None,
              host: str,
              port: Optional[int]=None,
              parameters: Optional[dict]=None,
              headers: Optional[MultiDict]=None,
              ):
        '''Build a URI from kwargs for each component.'''
        self = object.__new__(cls)
        self._contact = contact
        self._scheme = scheme
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._parameters = parameters if parameters else {}
        self._headers = headers if headers else MultiDict()
        self._validate_and_default()
        return self

    def with_contact(self, contact): return self._with(contact=contact)

    def with_scheme(self, scheme): return self._with(scheme=scheme)

    def with_user(self, user):
        if user and ':' in user[1:-1]:
            try:
                new_user, new_pass = user.split(':')
            except ValueError:
                raise ValueError('user must be either `user` or `user:pass`')
            return self._with(user=new_user, password=new_pass)
        elif user is None and self.password is not None:
            return self._with(user=user, password=None)
        else:
            return self._with(user=user)

    def with_password(self, password):
        if self.user is None:
            raise ValueError('cannot have a password without a user')
        return self._with(password=password)

    def with_host(self, host): return self._with(host=host)

    def with_port(self, port): return self._with(port=port)

    def with_parameters(self, parameters):
        for k, v in parameters.items():
            if v is None:
                parameters[k] = ''
        return self._with(parameters=parameters)

    def with_headers(self, headers):
        for k, v in headers.items():
            if v is None:
                headers[k] = ''
        return self._with(headers=headers)

    def with_transport(self, transport): return self._with(transport=transport)

    def with_tag(self, tag): return self._with(tag=tag)

    def _with(self, **kwargs):
        new = self.__deepcopy__()
        for attr in self.__slots__:
            name = attr[1:]
            if name in kwargs:
                setattr(new, attr, kwargs[name])
        for parameter in ['transport', 'tag']:
            if parameter in kwargs:
                new.parameters[parameter] = kwargs[parameter]
        new._validate_and_default()
        return new

    def _validate_and_default(self):
        '''Populate default port/transport if not explicitly
        given by uri string / build args, and ensure port is
        a valid value.'''
        if self.scheme not in ('sip', 'sips'):
            raise ValueError('scheme must be `sip` or `sips`')
        if self.port is None:
            self._port = 5061 if self.scheme == 'sips' else 5060
        if self.port not in range(1, 2**16):
            raise ValueError(f'port number {self.port} is not valid')
        if self.parameters.get('transport') is None:
            transport = 'tcp' if self.scheme == 'sips' else 'udp'
            self.parameters['transport'] = transport
        else:
            if self.scheme == 'sips' and self.transport == 'udp':
                raise ValueError(f'sips uris *must* use reliable transports,'
                                 f' {self.transport} is not reliable.')

    def __deepcopy__(self):
        return URI.build(
            contact=self.contact,
            scheme=self.scheme,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            parameters=copy.deepcopy(self.parameters),
            headers=copy.deepcopy(self.headers),
        )

    def __str__(self):
        '''Give a normalized string representation of the URI.

        Normalization here means applying these rules:
            * only place uri in <> brackets if the contact is defined
            * always explicitly specify the port
            * always explicitly specify the transport parameter
        '''
        if self.user and self.password:
            user = f'{self.user}:{self.password}@'
        elif self.user:
            user = f'{self.user}@'
        else:
            user = ''

        parameter_pairs = ';'.join(['='.join([k, v])
                                    for k, v in self.parameters.items()])
        parameters = f';{parameter_pairs}'
        header_pairs = '&'.join(['='.join([k, v])
                                 for k, v in self.headers.items()])
        headers = f'?{header_pairs}' if len(header_pairs) else ''

        uri = (f'{self.scheme}:{user}{self.host}'
               f':{self.port}{parameters}{headers}')

        if self.contact:
            return f'"{self.contact}" <{uri}>'
        else:
            return uri

    def __eq__(self, other):
        # TODO: are the parameters/headers order-sensitive or not?
        return str(self) == str(other)

    def __hash__(self):
        # TODO: are the parameters/headers order-sensitive or not?
        return hash(str(self))
