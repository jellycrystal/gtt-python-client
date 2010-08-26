gtt-python-client
=======================

Python bindings for Google Tranlator Toolkit API
http://code.google.com/apis/gtt/

Alpha version, have only basic support (models, ACL) yet.

Installation
------------

    pip install gtt-python-client


Usage
-----

    >>> import translator.client

    >>> client = translator.client.TranslatorToolkitClient()

    >>> client.client_login('some.google@account', 'P4ssW0rD', 'gtt-client')

    >>> document = client.get_documents().entry[0]

    >>> acl_link = document.find_acl_link()

    >>> client.add_acl(acl_link, 'other.gooogle@account', 'writer')

