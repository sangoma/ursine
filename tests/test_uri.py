import pytest
from multidict import MultiDict
from ursine import URI, URIError


@pytest.mark.parametrize('uri,expect', [
    ('sip:localhost', URI.build(scheme='sip', host='localhost')),
    (
        'sip:localhost;transport=tcp',
        URI.build(scheme='sip', hostport='localhost', transport='tcp'),
    ),
    (
        'sips:localhost;transport=tcp',
        URI.build(scheme='sips', host='localhost')),
    (
        'sips:localhost;transport=tcp;maddr=10.10.0.1',
        URI.build(
            scheme='sips', host='localhost', transport='tcp',
            parameters={'maddr': '10.10.0.1'},
        ),
    ),
    (
        'sips:localhost;transport=tcp;maddr=10.10.0.1?x=y&y=z',
        URI.build(
            scheme='sips', host='localhost', transport='tcp',
            parameters={'maddr': '10.10.0.1'},
            headers=MultiDict({'x': 'y', 'y': 'z'}),
        ),
    ),
])
def test_uri(uri, expect):
    assert URI(uri) == expect


@pytest.mark.parametrize('uri', [
    'sip:localhost:port',
    'sip:localhost:0',
    'sip:localhost:70000',
])
def test_invalid(uri):
    with pytest.raises(URIError):
        URI(uri)


@pytest.mark.parametrize('uri', [
    'sip:[::dead:beef]:5060',
    'sip:[::dead:beef]',
])
def test_ipv6_hostport(uri):
    assert URI(uri).port == 5060
