Welcome to ursine's documentation!
======================================

ursine is a SIP URI library intended to be easy to integrate into and use for other SIP-focused libraries such as aiosip_. In particular its meant to be easy to do the following

- parse SIP URIs into easy to work with objects
- generate new SIP URIs
- normalize the representation of SIP URIs
- allowing comparisons / hashing of URIs

and do all the same as well for SIP header values with contained URIs.


userinfo and hostport
---------------------

The SIP spec often refers to the 'userinfo' and 'hostport' meaning the
username+password and hostname+port respectively in a URI. For convenience
ursine offers handling the userinfo and hostport either as a single entity
or individually. The code below shows this with two effectively identical
ways of creating the same URI.

.. testcode::

   from ursine import URI

   uri1 = URI.build(scheme='sip',
                    host='localhost',
                    port=5080,
                    userinfo='john:pass')
   uri2 = URI.build(scheme='sip',
                    hostport='localhost:5080',
                    user='john',
                    password='pass')
   assert uri1 == uri2


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   uri
   header



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



.. _aiosip: https://github.com/eyepea/aiosip
