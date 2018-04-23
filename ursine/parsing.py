'''Regex based parsing for sip uris.'''
import re
import multidict


# optionally extract either a quoted or unquoted
# contact name and extract the rest discarding the <>
# brackets if present
contact_re = re.compile(r'("(?P<quoted>[^"]+)" '
                        r'|(?P<unquoted>[^\<"]+) )?'
                        r'\<(?P<the_rest>.*)\>\Z')

# extract a scheme, discard the : and extract the rest
scheme_re = re.compile(r'(?P<scheme>[^:]+):(?P<the_rest>.*)')

# optionally extract a user part (either user
# or user:pass) and discard the @ symbol
user_part_re = re.compile(r'(?P<user_part>[^:@]+(:[^@:]+)?)@(?P<the_rest>.*)')

# extract a host component that may be [...]
# delimited in order to support ipv6 hosts
host_re = re.compile(r'(?P<host>('
                     r'\[[^\]]+])|([^:;?&]+)'
                     r')(?P<the_rest>.*)')

# optionally discard a : and extract a port number
port_re = re.compile(r':(?P<port>[^;?]*)(?P<the_rest>.*)')

# optionally discard a ; and extract a single key=val pair
param_re = re.compile(r';(?P<key>[^=]+)=(?P<val>[^;?]*)(?P<the_rest>.*)')

# optionally extract a key=val pair
base_header_re = r'(?P<key>[^=]+)=(?P<val>[^&]*)(?P<the_rest>.*)'
# match a ? then a key=val pair - only first header starts with ?
first_header_re = re.compile(rf'\?{base_header_re}')
# match a & then a key=val pair - matches (n>1)th headers
nth_header_re = re.compile(rf'&{base_header_re}')


def parse_contact(uri):
    '''Attempt a contact match, and remove the
    proper sip uri from a <> pair if present
    '''
    match = contact_re.match(uri)
    if not match:
        return None, uri

    groups = match.groupdict()
    contact = groups.get('quoted')
    if contact is None:
        contact = groups.get('unquoted')

    return contact, groups['the_rest']


def parse_scheme(uri):
    '''Require a scheme match.'''
    match = scheme_re.match(uri)
    if match is None:
        raise ValueError('no scheme specified')
    groups = match.groupdict()

    scheme = groups['scheme'].lower()
    if scheme not in ('sip', 'sips'):
        raise ValueError(f'invalid scheme {scheme}')

    return scheme, groups['the_rest']


def parse_user_part(uri):
    '''Attempt to match user@ or user:pass@.'''
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
    '''Require a host match.

    The host can either be anything ending
    with the EOL, a ; or a :, and optionally
    can be enclosed in [...] to allow
    containing : characters.
    '''
    match = host_re.match(uri)
    if match is None:
        raise ValueError('host must be specified')
    groups = match.groupdict()
    return groups['host'], groups['the_rest']


def parse_port(uri):
    '''Attempt to match a : and port number.'''
    match = port_re.match(uri)
    if match is None:
        return None, uri
    groups = match.groupdict()

    try:
        port = int(groups['port'])
    except ValueError:
        raise ValueError('port must be an integer')

    return port, groups['the_rest']


def parse_parameters(uri):
    '''Attempt to match many ;key=val pairs.'''
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
    '''Attempt to match a ?key=val pair, then
    attempt to match many &key=val pairs.
    '''
    the_rest = uri
    headers = multidict.MultiDict()

    match = first_header_re.match(the_rest)
    while match:
        groups = match.groupdict()
        headers.add(groups['key'], groups['val'])
        the_rest = groups['the_rest']
        match = nth_header_re.match(the_rest)

    return headers, the_rest
