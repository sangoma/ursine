import pytest
from ursine import URI
from ursine.header_parsing import parse_header


@pytest.mark.parametrize('header,expect', [
    ('Alice <sip:localhost>;tag=abc', 'sip:localhost'),
    ('"Alice" <sip:localhost>;tag=abc', 'sip:localhost'),
    ('"Alice" <sip:[::dead:beef]?x=y>;tag=abc', 'sip:[::dead:beef]?x=y'),
    (
        '"Alice" <sip:localhost;maddr=1.1.1.1>;tag=abc',
        'sip:localhost;maddr=1.1.1.1'
    ),
    ('sip:localhost?x=y;tag=abc', 'sip:localhost?x=y'),
])
def test_uri(header, expect):
    h = parse_header(header)
    assert h.uri == URI(expect)


@pytest.mark.parametrize('header,expect', [
    ('Alice <sip:localhost>', {}),
    ('Alice <sip:localhost>;tag=abc', {'tag': 'abc'}),
    ('Alice <sip:localhost>;tag=abc;foo=bar', {'tag': 'abc', 'foo': 'bar'}),
    ('Alice <sip:localhost;red=herring>', {}),
    ('Alice <sip:localhost;a=b;b=c>;tag=abc', {'tag': 'abc'}),
    ('Alice <sip:localhost;x=y;n=m>;tag=abc;foo=bar', {'tag': 'abc', 'foo': 'bar'}),
])
def test_parameters(header, expect):
    assert parse_header(header).parameters == expect


@pytest.mark.parametrize('header,expect', [
    ('Alice <sip:localhost>', 'Alice'),
    ('"Alice" <sip:localhost>', 'Alice'),
    ('John Doe <sip:localhost>', 'John Doe'),
    ('"John Doe" <sip:localhost>', 'John Doe'),
])
def test_display_name(header, expect):
    assert parse_header(header).display_name == expect
