======
URI
======

The URI object can be created from a parseable URI in a string,
and unspecified attributes will take on reasonable defaults or,
where applicable, defaults as specified in the SIP standard.

URIs are treated as immutable, though new URIs can be created from
existing ones easily.

.. testcode:: python

   from ursine import URI

   uri1 = URI('sip:localhost:5080;transport=tcp')
   uri2 = URI('sips:localhost:5080')

   assert uri1 != uri2
   assert uri1 == uri2.with_scheme('sip')
   # since URIs are immutable, uri2 is unchanged
   assert uri1 != uri2

.. automodule:: ursine.uri
   :members:
