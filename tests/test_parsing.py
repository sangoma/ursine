import pytest
from ursine.parsing import (
    parse_contact,
    parse_scheme,
    parse_user_part,
    parse_host,
    parse_port,
    parse_parameters,
    parse_headers,
)


@pytest.mark.parametrize('uri,expect_contact,expect_the_rest', [
    ('sip:host', None, 'sip:host'),
    ('<sip:host>', None, 'sip:host'),
    ('John <sip:host>', 'John', 'sip:host'),
    ('"Mary" <sip:host>', 'Mary', 'sip:host'),
    ('"Alice Cooper" <sip:host>', 'Alice Cooper', 'sip:host'),
    ('"<>>:<<>" <sip:host>', '<>>:<<>', 'sip:host'),
    ('<sip:host', None, '<sip:host'),
    ('sip:host>', None, 'sip:host>'),
    ('Mary" <sip:host>', None, 'Mary" <sip:host>'),
    ('Alice sip:host', None, 'Alice sip:host'),
    (' sip:host', None, ' sip:host'),
])
def test_contact(uri, expect_contact, expect_the_rest):
    contact, the_rest = parse_contact(uri)
    assert contact == expect_contact
    assert the_rest == expect_the_rest


@pytest.mark.parametrize('uri,expect_scheme,expect_the_rest', [
    ('sip:', 'sip', ''),
    ('sips:', 'sips', ''),
    ('sip:localhost:5060', 'sip', 'localhost:5060'),
])
def test_scheme(uri, expect_scheme, expect_the_rest):
    scheme, the_rest = parse_scheme(uri)
    assert scheme == expect_scheme
    assert the_rest == expect_the_rest


@pytest.mark.parametrize('uri', [
    '', 'sisp:', ':', 'sip', 'sips', 'localhost:5060',
])
def test_scheme_fails(uri):
    with pytest.raises(ValueError):
        parse_scheme(uri)


@pytest.mark.parametrize('uri,expect_user,expect_pass,expect_the_rest', [
    ('bob:pass@some.tld', 'bob', 'pass', 'some.tld'),
    ('bob@some.tld', 'bob', None, 'some.tld'),
    ('some.tld', None, None, 'some.tld'),
    ('a@some.tld', 'a', None, 'some.tld'),
    ('@some.tld', None, None, '@some.tld'),
    (':some.tld', None, None, ':some.tld'),
])
def test_user_part(uri, expect_user, expect_pass, expect_the_rest):
    user, password, the_rest = parse_user_part(uri)
    assert user == expect_user
    assert password == expect_pass
    assert the_rest == expect_the_rest


@pytest.mark.parametrize('uri,expect_host,expect_the_rest', [
    ('some.tld', 'some.tld', ''),
    ('some.tld:5060;x=y', 'some.tld', ':5060;x=y'),
    ('tld', 'tld', ''),
    ('tld:5060;x=y', 'tld', ':5060;x=y'),
    ('[::1]:5060', '[::1]', ':5060'),
])
def test_host(uri, expect_host, expect_the_rest):
    host, the_rest = parse_host(uri)
    assert host == expect_host
    assert the_rest == expect_the_rest


@pytest.mark.parametrize('uri,expect_port,expect_the_rest', [
    (':5060', 5060, ''),
    (':1', 1, ''),
    (':5060;x=y', 5060, ';x=y'),
    (':5060?x=y', 5060, '?x=y'),
    (':65535', 65535, ''),
])
def test_port(uri, expect_port, expect_the_rest):
    port, the_rest = parse_port(uri)
    assert port == expect_port
    assert the_rest == expect_the_rest


@pytest.mark.parametrize('uri,expect_params,expect_the_rest', [
    (';ten=10', {'ten': '10'}, ''),
    (';ten=10;five=5', {'ten': '10', 'five': '5'}, ''),
    (';ten=10;five=5?x=y', {'ten': '10', 'five': '5'}, '?x=y'),
])
def test_parameters(uri, expect_params, expect_the_rest):
    params, the_rest = parse_parameters(uri)
    assert params == expect_params
    assert the_rest == expect_the_rest


@pytest.mark.parametrize('uri,expect_headers,expect_the_rest', [
    ('?x=y', {'x': ['y']}, ''),
    ('?x=y&x=z', {'x': ['y', 'z']}, ''),
    ('?x=y&a=b', {'x': ['y'], 'a': ['b']}, ''),
    ('?x=&y=', {'x': [''], 'y': ['']}, ''),
])
def test_headers(uri, expect_headers, expect_the_rest):
    headers, the_rest = parse_headers(uri)
    for k, v in expect_headers.items():
        assert headers.popall(k) == v
    assert len(headers) == 0
    assert the_rest == expect_the_rest
