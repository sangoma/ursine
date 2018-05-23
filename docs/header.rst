=======
Header
=======

A SIP header wraps together a display name, sip URI, and header parameters,
and so too does the ursine header, but the Header class also offers one
utility - it can be used to ensure that a given header has a tag (randomly
generating one and applying it if no tag exists and no tag to use is
specified).

.. testcode::

   from ursine import Header, URI

   hdr1 = Header('"Alice" <sip:localhost>;tag=foo')
   hdr2 = Header('<sip:localhost>')

   assert hdr1 == hdr2.with_display_name('Alice').with_tag('foo')
   assert hdr1.with_display_name(None) == hdr2.with_tag('foo')

   uri = URI.build(scheme='sip', host='localhost')
   header_with_tag = Header.build(uri=uri).with_tag()

   assert header_with_tag.tag is not None

.. automodule:: ursine.header
   :members:
