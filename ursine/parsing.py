import re
import multidict


contact_re = re.compile('("(?P<quoted>[^"]+)" '
                        '|(?P<unquoted>[^\<"]+) )?'
                        '\<(?P<the_rest>.*)\>\Z')

scheme_re = re.compile('(?P<scheme>[^:]+):(?P<the_rest>.*)')

user_part_re = re.compile('(?P<user_part>[^:@]+(:[^@:]+)?)@(?P<the_rest>.*)')

host_re = re.compile('(?P<host>('
                     '\[[^\]]+])|([^:|;]+)'
                     ')(?P<the_rest>.*)')

port_re = re.compile(':(?P<port>[^;?]*)(?P<the_rest>.*)')

param_re = re.compile(';(?P<key>[^=]+)=(?P<val>[^;?]*)(?P<the_rest>.*)')

base_header_re = '(?P<key>[^=]+)=(?P<val>[^&]*)(?P<the_rest>.*)'
first_header_re = re.compile(f'\?{base_header_re}')
nth_header_re = re.compile(f'&{base_header_re}')


def parse_contact(uri):
    match = contact_re.match(uri)
    if not match:
        return None, uri

    groups = match.groupdict()
    contact = groups.get('quoted')
    if contact is None:
        contact = groups.get('unquoted')

    return contact, groups['the_rest']


def parse_scheme(uri):
    match = scheme_re.match(uri)
    if match is None:
        raise ValueError('no scheme specified')
    groups = match.groupdict()

    scheme = groups['scheme'].lower()
    if scheme not in ('sip', 'sips'):
        raise ValueError(f'invalid scheme {scheme}')

    return scheme, groups['the_rest']


def parse_user_part(uri):
    match = user_part_re.match(uri)
    if match is None:
        return None, None, uri
    groups = match.groupdict()

    subparts = groups['user_part'].split(':')
    if len(subparts) == 2:
        user, password = subparts
    else:
        user, password = subparts[0], None

    return user, password, groups['the_rest']


def parse_host(uri):
    match = host_re.match(uri)
    if match is None:
        raise ValueError('host must be specified')
    groups = match.groupdict()
    return groups['host'], groups['the_rest']


def parse_port(uri):
    match = port_re.match(uri)
    if match is None:
        return None, uri
    groups = match.groupdict()

    try:
        port = int(groups['port'])
    except ValueError:
        raise ValueError('port must be an integer')

    if port not in range(1, 2**16):
        raise ValueError(f'invalid port number {port}')

    return port, groups['the_rest']


def parse_parameters(uri):
    the_rest = uri
    params = {}

    match = param_re.match(the_rest)
    while match:
        groups = match.groupdict()
        if params.get(groups['key']):
            raise ValueError('parameters must be unique')
        params[groups['key']] = groups['val']
        the_rest = groups['the_rest']
        match = param_re.match(the_rest)

    return params, the_rest


def parse_headers(uri):
    the_rest = uri
    headers = multidict.MultiDict()

    match = first_header_re.match(the_rest)
    while match:
        groups = match.groupdict()
        headers.add(groups['key'], groups['val'])
        the_rest = groups['the_rest']
        match = nth_header_re.match(the_rest)

    return headers, the_rest
