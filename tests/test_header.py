import pytest
from ursine import Header, URI


@pytest.mark.parametrize('header,expect', [
    ('sip:localhost', f'<{str(URI("sip:localhost"))}>'),
    ('Alice <sip:localhost>', f'"Alice" <{str(URI("sip:localhost"))}>'),
    ('"Alice" <sip:localhost>', f'"Alice" <{str(URI("sip:localhost"))}>'),
])
def test_str(header, expect):
    assert str(Header(header)) == expect
