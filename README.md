# ursine - a bearable sip uri library

[![Build Status](https://travis-ci.org/sangoma/ursine.svg?branch=master)](https://travis-ci.org/sangoma/ursine)
[![Doc State](https://readthedocs.org/projects/ursine/badge/?version=latest<Paste>)](https://ursine.readthedocs.io/en/latest/)

----
## installing
ursine is packaged and available on [pypi](https://pypi.org/project/ursine)

```sh
pip install ursine
```

----
## basic usage

```python
from ursine import URI, Header

# build new URIs / Headers
uri = URI.build(scheme='sip', host='10.10.10.10', transport='tcp')
print(uri)  # sip:10.10.10.10;transport=tcp
header = Header.build(display_name='Alice', uri=uri, tag='xyz')
print(header)  # "Alice" <sip:10.10.10.10;transport=tcp>;tag=xyz

# parse existing ones
uri = URI('sips:[::1]:5080')
uri.scheme == 'sips'
uri.host == '[::1]'
uri.transport == 'tcp'

header = Header('"Bob" <sips:[::1]:5080>;tag=abc')
header.display_name == 'Bob'
header.tag == 'abc'
header.uri.scheme == 'sips'

# Header and URI objects are immutable
alice_uri = URI('sip:alice@10.10.10.10')
modified_uri = alice_uri.with_user(None)  # 'sip:10.10.10.10;transport=udp'
modified_uri != alice_uri
```
