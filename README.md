# ursine - a bearable sip uri library

[![Build Status](https://travis-ci.org/sangoma/ursine.svg?branch=master)](https://travis-ci.org/sangoma/ursine)

----
## installing
ursine is packaged and available on [pypi](https://pypi.org/project/ursine)

    pip install ursine

----
## basic usage
from ursine import URI

	alice_uri = URI('"Alice" <sips:alice@localhost:5080>')
	bob_uri = URI('"Bob" <sips:bob@localhost:5080>')

	# URI mutations actually return new, distinct URIs
	modified_uri = alice_uri.with_port(6000)
	assert modified_uri != alice_uri  # True

	# optional URI components can be removed
	userless_uri = bob_uri.with_contact(None).with_user(None)

	# URIs can be stringified again for use in other sytems
	print(userless_uri)  # 'sips:localhost:5080;transport=tcp'
