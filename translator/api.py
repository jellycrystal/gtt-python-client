"""
Handy abstractions for Google Translator's API
"""
import urllib
import cgi
import urlparse
import translator.client
import translator.data

try:
    import lxml.etree
    lxml_enable = True
except ImportError:
    lxml_enable = False

WORKBENCH_URL = 'http://translate.google.com/toolkit/workbench'

class _FakeClient(object):

    def __getattr__(self, name):
        raise ValueError("Requested to use client.%s, but "
                         "TranslatorToolkitClient instance didn't passed "
                         "as client parameter" % name)

def get_id(id_or_url):
    if id_or_url.startswith('http://'):
        parts = urlparse.urlparse(id_or_url)
        if id_or_url.startswith(WORKBENCH_URL):
            query = cgi.parse_qs(parts[4])
            return query.get('did', [None])[0]
        elif id_or_url.startswith(translator.client.AUTH_SCOPE):
            return parts[2].split('/')[-1]
        else:
            raise ValueError("Doesn't know how to extract document id from %s:"
                             " it should be a link to workbench or to feed" %
                             id_or_url)
    else:
        return id_or_url


def get_url(id_or_url):
    if id_or_url.startswith(('http://', 'https://')):
        return id_or_url
    else:
        return WORKBENCH_URL + '?' + urllib.urlencode({'did': id_or_url})


class Acl(object):

    def __init__(self, client, entry):
        self.client = client if client is not None else _FakeClient()
        self.acl_link = entry.find_acl_link()

    def add(self, account, role='reader'):
        # remove cache of acl_list
        self._acl_list = None
        return self.client.add_acl(self.acl_link, account, role)

    def update(self, account, role):
        self._acl_list = None
        return self.client.update_acl(self.acl_link, account, role)

    def delete(self, account):
        self._acl_list = None
        return self.client.delete_acl(self.acl_link, account)

    def add_or_update(self, account, role):
        if account in self.acl_list:
            if self.acl_list[account] == role:
                # Nothing to do
                return
            return self.update(account, role)
        else:
            return self.add(account, role)

    @property
    def acl_list(self):
        if not getattr(self, '_acl_list', None):
            self._acl_list = dict((e.scope.value, e.role.value)
                                  for e in
                                  self.client.get_acl_list(self.acl_link).entry)
        return self._acl_list


class TranslationDocument(object):
    def __init__(self, client, document_id=None, entry=None):
        """
        Create higher-level abstraction TranslationDocument with more
        clear Python API.

        Arguments:
         - client: instance of TranslatorToolkitClient,
             need for update/modify document. Could be a None
             for RO documents or offline processing.
         - document_id: ID of document need to be fetched using `client`.
         - entry: document entry parsed XML (instance of
             `translator.data.TranslationEntry`). Must be provided if
             `client` is None.
        """
        if document_id is None and entry is None:
            raise ValueError("One of document_id or entry parametr "
                             "must be provided")
        if client is None and entry is None:
            raise ValueError("Client is not provided, then entry is required")

        self.entry = entry

        if document_id is None:
            self.id = get_id(entry.id.text)
        else:
            self.id = document_id

        if client is None:
            self.client = _FakeClient()
        else:
            self.client = client

        if self.entry is None:
            self.update()


    def update(self):
        self.entry = self.client.get_document(self.id)
        self.acl = Acl(self.client, self.entry)

    @property
    def url(self):
        return get_url(self.id)

    @property
    def status(self):
        return self.entry.annotation.text.replace('google.com:', '')

    @property
    def stats(self):
        stats_dict = dict((e.translationType.text, e.numWords.text)
                          for e in self.entry.prefillStats.entry)
        stats_dict.update({'overall': self.entry.numberOfSourceWords.text})
        return stats_dict

    @property
    def raw_entry(self):
        as_string = self.entry.to_string()
        if lxml_enable:
            as_string = lxml.etree.tostring(lxml.etree.fromstring(as_string),
                                            pretty_print=True)
        return as_string


    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.__str__())


def fetch_translation_documents(client):
    feed = client.get_documents()
    while feed:
        for document in feed.entry:
            yield TranslationDocument(client=client, entry=document)
        feed = client.get_next(feed) if feed.get_next_link() else None
