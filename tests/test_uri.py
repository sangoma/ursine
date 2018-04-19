import pytest
from multidict import MultiDict
from ursine import URI


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
