import pytest
from multidict import MultiDict
from ursine import URI


@pytest.mark.parametrize('uri', [
    'sip:localhost:port',
    'sip:localhost:0',
    'sip:localhost:70000',
    'sip:localhost?',
    'sip:localhost;',
    'sip:localhost&',
])
def test_invalid(uri):
    with pytest.raises(ValueError):
        URI(uri)


@pytest.mark.parametrize('uri,expect', [
    ('sip:localhost', 'sip:localhost:5060;transport=udp'),
    ('sips:localhost', 'sips:localhost:5061;transport=tcp'),
    ('<sip:localhost>', 'sip:localhost:5060;transport=udp'),
    (
        'John Doe <sip:localhost:5080?x=y&a=b>',
        '"John Doe" <sip:localhost:5080;transport=udp?x=y&a=b>',
    )
])
def test_to_str(uri, expect):
    assert str(URI(uri)) == expect


@pytest.mark.parametrize('uri1,uri2', [
    ('sip:localhost', 'sip:localhost'),
    ('sip:localhost', 'sip:localhost;transport=udp'),
    ('<sip:localhost>', 'sip:localhost'),
    ('Alice <sip:localhost>', '"Alice" <sip:localhost>'),
    ('SIP:localhost', 'sip:localhost')
    # TODO: test different parameter/header orderings?
    #       don't know if either/both are order sensitive
])
def test_equality(uri1, uri2):
    assert URI(uri1) == URI(uri2)


@pytest.mark.parametrize('uri1,uri2', [
    ('sip:localhost', 'sips:localhost'),
    ('Bob <sip:localhost>', 'sip:localhost'),
    ('Alice <sip:localhost>', 'alice <sip:localhost>'),
    ('sip:remotehost', 'sip:localhost')
])
def test_inequality(uri1, uri2):
    assert URI(uri1) != URI(uri2)


@pytest.mark.parametrize('kwargs,expect', [
    ({'scheme': 'sip', 'host': 'localhost'}, 'sip:localhost'),
    (
        {
            'scheme': 'sip', 'host': 'localhost',
            'parameters': {'transport': 'tcp'},
        },
        'sip:localhost;transport=tcp',
    ),
    (
        {
            'scheme': 'sips', 'host': '[::1]', 'port': 5080,
            'parameters': {'maddr': '[::dead:beef]'},
            'headers': MultiDict({'x': 'y', 'a': ''}),
        },
        'sips:[::1]:5080;maddr=[::dead:beef]?x=y&a=',
    ),
])
def test_build(kwargs, expect):
    assert URI.build(**kwargs) == URI(expect)


@pytest.mark.parametrize('original,attr,new,expect', [
    ('sip:localhost', 'user', 'jdoe', 'sip:jdoe@localhost'),
    ('sip:localhost;transport=tcp', 'scheme', 'sips', 'sips:localhost:5060'),
    ('sip:localhost', 'port', 5080, 'sip:localhost:5080'),
    ('sip:jdoe@localhost', 'user', None, 'sip:localhost'),
    ('"Mark" <sip:localhost>', 'contact', None, 'sip:localhost'),
    ('sip:user:pass@localhost', 'user', None, 'sip:localhost'),
    ('sip:localhost', 'user', 'user:pass', 'sip:user:pass@localhost'),
    ('sip:alice@localhost', 'password', 'pass', 'sip:alice:pass@localhost'),
    ('sip:localhost', 'transport', 'tcp', 'sip:localhost;transport=tcp'),
    ('sip:localhost', 'tag', 'bler', 'sip:localhost;transport=udp;tag=bler'),
    (
        'sip:localhost', 'parameters',
        {'maddr': '[::1]', 'foo': 'bar', 'x': ''},
        'sip:localhost;maddr=[::1];foo=bar;x=',
    ),
    (
        'sip:localhost', 'headers',
        {'ahhhh': '', 'foo': 'bar'},
        'sip:localhost?ahhhh=&foo=bar',
    ),
    (
        'sip:localhost', 'parameters',
        {'maddr': '[::1]', 'foo': 'bar', 'x': None},
        'sip:localhost;maddr=[::1];foo=bar;x=',
    ),
    (
        'sip:localhost', 'headers',
        {'ahhhh': None, 'foo': 'bar'},
        'sip:localhost?ahhhh=&foo=bar',
    ),
])
def test_modified_uri_creation(original, attr, new, expect):
    old_uri = URI(original)
    new_uri = getattr(old_uri, f'with_{attr}')(new)
    assert new_uri == URI(expect)
    assert new_uri != old_uri
