'''URI object for parsing/building SIP URIs.'''
import copy
from typing import Optional
from multidict import MultiDict
from .uri_parsing import parse_uri


class URIError(Exception):
    pass


class URI:
    __slots__ = (
        '_scheme',
        '_userinfo',
        '_hostport',
        '_parameters',
        '_headers',
    )

    def __init__(self, uri: str):
        result = parse_uri(uri)
        self._scheme = result.scheme
        self._userinfo = result.userinfo
        self._hostport = result.hostport
        self._parameters = result.parameters
        self._headers = result.headers
        if self._parameters.get('transport') is None:
            self._parameters['transport'] = self._default_transport()
        self._validate()

    @classmethod
    def build(cls, *,
              scheme: str,
              user: Optional[str]=None,
              password: Optional[str]=None,
              userinfo: Optional[str]=None,
              host: Optional[str]=None,
              port: Optional[int]=None,
              hostport: Optional[str]=None,
              parameters: Optional[dict]=None,
              headers: Optional[MultiDict]=None,
              transport: Optional[str]=None,
              ):
        '''Build a URI from individual pieces.

        Both the userinfo and hostport may be broken
        down into user/password and host/port respectively
        for convenience, and similarly the transport
        parameter is offered as an argument for convenience.
        '''
        if (user or password) and userinfo:
            raise URIError('userinfo and user/password'
                           ' are mutually exclusive')
        if not ((host or port) is None) ^ (hostport is None):
            raise URIError('hostport and host/port kwargs'
                           ' are mutually exclusive, but at'
                           ' least one of host or hostport'
                           ' must be given')

        self = object.__new__(cls)
        self._scheme = scheme
        if userinfo:
            self._userinfo = userinfo
        elif user:
            if password:
                self._userinfo = f'{user}:{password}'
            else:
                self._userinfo = user
        else:
            self._userinfo = None
        if hostport:
            self._hostport = hostport
        elif host:
            if port:
                self._hostport = f'{host}:{port}'
            else:
                self._hostport = host
        else:
            self._hostport = None
        self._parameters = parameters if parameters else {}
        self._headers = headers if headers else MultiDict()
        if transport:
            self._parameters['transport'] = transport
        else:
            self._parameters['transport'] = self._default_transport()
        self._validate()
        return self

    scheme = property(lambda self: self._scheme)
    userinfo = property(lambda self: self._userinfo)
    hostport = property(lambda self: self._hostport)
    parameters = property(lambda self: self._parameters)
    headers = property(lambda self: self._headers)
    transport = property(lambda self: self._parameters['transport'])

    @property
    def user(self):
        if self._userinfo is None or ':' not in self._userinfo:
            return self._userinfo
        else:
            return self._userinfo.split(':')[0]

    @property
    def password(self):
        if self._userinfo is None or ':' not in self._userinfo:
            return None
        else:
            return self._userinfo.split(':')[1]

    @property
    def host(self):
        if ':' in self._hostport:
            return self._hostport.split(':')[0]
        else:
            return self._hostport

    @property
    def port(self):
        if '[' in self._hostport:
            port_part = self._hostport.rpartition(']')[2]
            if ':' in port_part:
                return int(port_part[1:])
            else:
                return self._default_port()
        elif ':' in self._hostport:
            return int(self._hostport.split(':')[1])
        else:
            return self._default_port()

    def _validate(self):
        '''Ensure correctness of properties.'''
        if self._scheme not in ('sip', 'sips'):
            raise URIError('scheme is a required to be either `sip` or `sips`')
        if self._hostport is None:
            raise URIError('host is a required attribute')
        if ':' in self._hostport:
            try:
                if self.port not in range(1, 2**16):
                    raise URIError(f'invalid port {self.port}')
            except ValueError:
                raise URIError(f'invalid port in hostport: {self._hostport}')

    def _default_port(self):
        '''Get the default port for ourselves.'''
        return 5060 if self._scheme == 'sip' else 5061

    def _default_transport(self):
        '''Get the default transport for ourselves.'''
        return 'udp' if self._scheme == 'sip' else 'tcp'

    def with_scheme(self, scheme):
        new = copy.copy(self)
        new._scheme = scheme
        new._validate()
        return new

    def with_userinfo(self, userinfo):
        new = copy.copy(self)
        new._userinfo = userinfo
        new._validate()
        return new

    def with_user(self, user):
        new = copy.copy(self)
        if self.password:
            new._userinfo = f'{user}:{self.password}'
        else:
            new._userinfo = user
        new._validate()
        return new

    def with_password(self, password):
        new = copy.copy(self)
        if self.user is None:
            raise URIError('cannot set password without user')
        new._userinfo = f'{self.user}:{password}'
        new._validate()
        return new

    def with_hostport(self, hostport):
        new = copy.copy(self)
        new._hostport = hostport
        new._validate()
        return new

    def with_host(self, host):
        new = copy.copy(self)
        if ':' in self._hostport:
            new._hostport = f'{host}:{self.port}'
        else:
            new._hostport = host
        new._validate()
        return new

    def with_port(self, port):
        new = copy.copy(self)
        if port == self._default_port():
            new._hostport = self.host
        else:
            new._hostport = f'{self.host}:{port}'
        new._validate()
        return new

    def with_parameters(self, parameters):
        new = copy.copy(self)
        new._parameters = parameters
        new._validate()
        return new

    def with_headers(self, headers):
        new = copy.copy(self)
        new._headers = headers
        new._validate()
        return new

    def with_transport(self, transport):
        new = copy.copy(self)
        new._parameters['transport'] = transport
        new._validate()
        return new

    def short_str(self):
        return self.__str__(short=True)

    def __str__(self, short=False):
        userinfo = f'{self._userinfo}@' if self._userinfo else ''
        if short:
            params = ''
            headers = ''
        else:
            param_pairs = ';'.join(['='.join([k, v])
                                    for k, v in sorted(self._parameters.items())])
            header_pairs = '&'.join(['='.join([k, v])
                                     for k, v in sorted(self._headers.items())])
            params = f';{param_pairs}'
            headers = f'?{header_pairs}' if len(header_pairs) else ''

        return f'{self._scheme}:{userinfo}{self.hostport}{params}{headers}'

    def __repr__(self):
        return f'{self.__class__.__name__}({self})'

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def __copy__(self):
        return URI.build(
            scheme=self._scheme,
            userinfo=self._userinfo,
            hostport=self._hostport,
            parameters=self._parameters,
            headers=self._headers,
        )
