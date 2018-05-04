'''Parsing for SIP URIs.'''
from .uri import URI
from collections import namedtuple


HeaderParseResult = namedtuple('HeaderParseResult', (
    'display_name',
    'parameters',
    'uri',
))


def parse_params(params_str):
    params = {}
    for pair in params_str.split(';'):
        if pair == '':
            continue
        key, eq, val = pair.partition('=')
        if len(key) == 0 or eq != '=':
            raise ValueError(f'invalid uri parameter `{pair}`')
        params[key] = val
    return params


def parse_display_name(dsp):
    if dsp is None:
        return None
    if '"' in dsp:
        quoted_parts = dsp.split('"')
        if len(quoted_parts) != 3:
            raise ValueError(f'invalid display name `{dsp}`')
        return quoted_parts[1]
    else:
        return dsp.strip()


def parse_header(hdr):
    '''Parse a SIP URI in a header format.

    Ex `Alice <sip:localhost>`
    '''
    uri_start = hdr.find('<')
    uri_end = hdr.find('>')
    if (uri_start == -1) ^ (uri_end == -1) or \
            uri_start > uri_end:
        raise ValueError('unbalanced <> delimiters')
    if uri_start == -1:
        display_part = None
        uri_part, _, params_part = hdr.partition(';')
    else:
        display_part, _, remainder = hdr.partition('<')
        uri_part, _, params_part = remainder.partition('>')

    return HeaderParseResult(
        display_name=parse_display_name(display_part),
        parameters=parse_params(params_part),
        uri=URI(uri_part),
    )
