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
        'contact',
        'scheme',
        'user',
        'password',
        'host',
        'port',
        'parameters',
        'headers',
    )

    def __new__(cls, uri: Optional[str]=None):
        self = object.__new__(cls)
        if uri:
            self._build_from_uri(uri)
        return self

    def _build_from_uri(self, uri: str):
        the_rest = uri
        self.contact, the_rest = parse_contact(the_rest)
        self.scheme, the_rest = parse_scheme(the_rest)
        self.user, self.password, the_rest = parse_user_part(the_rest)
        self.host, the_rest = parse_host(the_rest)
        self.port, the_rest = parse_port(the_rest)
        self.parameters, the_rest = parse_parameters(the_rest)
        self.headers, the_rest = parse_headers(the_rest)
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
        self = cls()
        self.contact = contact
        self.scheme = scheme
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.parameters = parameters if parameters else {}
        self.headers = headers if headers else MultiDict()
        self._validate_and_default()
        return self

    def _validate_and_default(self):
        if self.scheme not in ('sip', 'sips'):
            raise ValueError('scheme must be `sip` or `sips`')
        if self.port is None:
            self.port = 5061 if self.scheme == 'sips' else 5060
        if self.parameters.get('transport') is None:
            transport = 'tcp' if self.scheme == 'sips' else 'udp'
            self.parameters['transport'] = transport

    @property
    def transport(self):
        return self.parameters.get('transport')

    @property
    def tag(self):
        return self.parameters.get('tag')

    def __str__(self):
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
