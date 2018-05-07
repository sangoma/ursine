import pytest
from ursine import Header, URI


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
    (
        Header('<sip:localhost>;tag=xyz'),
        'default_tag', 'abcde',
        Header('<sip:localhost>;tag=xyz'),
    ),
    (
        Header('<sip:localhost>'),
        'default_tag', 'abcde',
        Header('<sip:localhost>;tag=abcde'),
    ),
])
def test_with_attr(original, attr, new_value, expect):
    assert getattr(original, f'with_{attr}')(new_value) == expect


def test_with_deafult_tag_generation():
    assert Header('sip:localhost').with_default_tag().tag is not None


@pytest.mark.parametrize('original,attr,new_value', [
    (Header('sip:localhost'), 'display_name', 'Bob'),
    (Header('"Alice" <sip:localhost>'), 'display_name', 'Bob'),
    (Header('<sip:localhost>tag=abc'), 'tag', 'xyz'),
    (Header('<sip:localhost>'), 'parameters', {'key': 'value'}),
])
def test_immutability(original, attr, new_value):
    assert original != getattr(original, f'with_{attr}')(new_value)
