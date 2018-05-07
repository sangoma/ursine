import pytest
from ursine import Header, URI


@pytest.mark.parametrize('header,expect', [
    (
        'sip:localhost',
        Header.build(
            uri=URI.build(scheme='sip', host='localhost')
        )
    ),
    (
        '<sip:localhost>',
        Header.build(
            uri=URI.build(scheme='sip', host='localhost')
        )
    ),
    (
        '"Bob" <sip:localhost>',
        Header.build(
            display_name='Bob',
            uri=URI.build(scheme='sip', host='localhost')
        )
    ),
    (
        '"Bob" <sip:localhost;x=y>;tag=abc',
        Header.build(
            display_name='Bob',
            uri=URI.build(
                scheme='sip',
                host='localhost',
                parameters={'x': 'y'}
            ),
            tag='abc',
        )
    ),
])
def test_header(header, expect, benchmark):
    header = benchmark(Header, header)
    assert header == expect


@pytest.mark.parametrize('header,expect', [
    ('sip:localhost', f'<{str(URI("sip:localhost"))}>'),
    ('Alice <sip:localhost>', f'"Alice" <{str(URI("sip:localhost"))}>'),
    ('"Alice" <sip:localhost>', f'"Alice" <{str(URI("sip:localhost"))}>'),
])
def test_str(header, expect):
    assert str(Header(header)) == expect


@pytest.mark.parametrize('uri,display_name,params,expect', [
    (URI('sip:localhost'), 'John', {}, '"John" <sip:localhost>'),
    (URI('sip:localhost;x=y'), 'John', {}, '"John" <sip:localhost;x=y>'),
    (URI('sip:localhost'), 'John', {'x': 'y'}, '"John" <sip:localhost>;x=y'),
    (URI('sip:localhost;x=y'), 'John', {
     'x': 'y'}, '"John" <sip:localhost;x=y>;x=y'),
    (URI('sip:localhost'), None, {}, '<sip:localhost>'),
])
def test_build(uri, display_name, params, expect):
    header = Header.build(uri=uri,
                          display_name=display_name,
                          parameters=params)
    assert header == Header(expect)


@pytest.mark.parametrize('original,attr,new_value,expect', [
    (
        Header('"John" <sip:localhost>'),
        'display_name', None,
        Header('<sip:localhost>')
    ),
    (
        Header('<sip:localhost>'),
        'display_name', 'Alice',
        Header('"Alice" <sip:localhost>'),
    ),
    (
        Header('<sip:localhost>'),
        'tag', 'abcde',
        Header('<sip:localhost>;tag=abcde'),
    ),
])
def test_with_attr(original, attr, new_value, expect):
    assert getattr(original, f'with_{attr}')(new_value) == expect


@pytest.mark.parametrize('original,attr,new_value', [
    (Header('sip:localhost'), 'display_name', 'Bob'),
    (Header('"Alice" <sip:localhost>'), 'display_name', 'Bob'),
    (Header('<sip:localhost>tag=abc'), 'tag', 'xyz'),
    (Header('<sip:localhost>'), 'parameters', {'key': 'value'}),
])
def test_immutability(original, attr, new_value):
    assert original != getattr(original, f'with_{attr}')(new_value)
