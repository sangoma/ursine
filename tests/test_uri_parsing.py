import pytest
from ursine.uri_parsing import parse_uri


@pytest.mark.parametrize('uri,expect', [
    ('sip:localhost', 'sip'),
    ('sips:localhost', 'sips'),
])
def test_scheme(uri, expect):
    assert parse_uri(uri).scheme == expect


@pytest.mark.parametrize('uri', [
    '',
    ':',
    ':localhost',
])
def test_scheme_fail(uri):
    with pytest.raises(ValueError):
        parse_uri(uri)


@pytest.mark.parametrize('uri,expect', [
    ('sip:localhost', 'localhost'),
    ('sip:127.0.0.1', '127.0.0.1'),
    ('sip:[::dead:beef]', '[::dead:beef]'),
    ('sip:localhost:5060', 'localhost:5060'),
    ('sip:127.0.0.1:5060', '127.0.0.1:5060'),
    ('sip:[::dead:beef]:5060', '[::dead:beef]:5060'),
])
def test_hostport(uri, expect):
    assert parse_uri(uri).hostport == expect


@pytest.mark.parametrize('uri', [
    'sip:',
    'sip:?',
    'sip:;',
])
def test_hostport_fail(uri):
    with pytest.raises(ValueError):
        parse_uri(uri)


@pytest.mark.parametrize('uri,expect', [
    ('sip:user@localhost', 'user'),
    ('sip:user:pass@localhost', 'user:pass'),
    ('sip:u:p@localhost', 'u:p'),
])
def test_userinfo(uri, expect):
    assert parse_uri(uri).userinfo == expect
