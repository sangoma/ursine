'''Parsing for SIP URIs.'''
from collections import namedtuple
from multidict import MultiDict
import re


URIParseResult = namedtuple('URIParseResult', (
    'scheme',
    'userinfo',
    'hostport',
    'parameters',
    'headers',
))


uri_re = re.compile(r'(?P<scheme>[^:]+):'
                    r'((?P<userinfo>[^@]+)@)?'
                    r'(?P<hostport>[^;?]+)'
                    r'(;(?P<parameters>[^?]*))?'
                    r'(\?(?P<headers>.*))?'
                    )


def parse_uri(uri):
    '''Parse a SIP URI into the scheme/userinfo/hostport/parameters/headers.'''
    match = uri_re.match(uri)
    if not match:
        raise ValueError(f"'{uri}' is not a valid SIP URI")
    groups = match.groupdict()

    scheme = groups.get('scheme')
    userinfo = groups.get('userinfo', None)
    hostport = groups.get('hostport')

    parameters = {}
    if groups.get('parameters'):
        param_pairs = groups.get('parameters').split(';')
    else:
        param_pairs = []
    for pair in param_pairs:
        param = pair.split('=')
        if len(param) != 2:
            raise ValueError('parameters must be formatted as `key=[val]`')
        key, val = param
        parameters[key] = val

    headers = MultiDict()
    if groups.get('headers'):
        header_pairs = groups.get('headers').split('&')
    else:
        header_pairs = []
    for pair in header_pairs:
        if len(pair.split('=')) != 2:
            raise ValueError('headers must be formatted as `key=[val]`')
        key, val = pair.split('=')
        headers.add(key, val)

    return URIParseResult(
        scheme=scheme,
        userinfo=userinfo,
        hostport=hostport,
        parameters=parameters,
        headers=headers,
    )
