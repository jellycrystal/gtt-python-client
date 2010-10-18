#!/usr/bin/env python
#
# Copyright (c) 2010 oDesk corp.
#
# Licensed under terms of BSD license.
#

"""
Contains a client to communicate with the Google Translation
servers.

For documentation on the Google Translator Toolkit API, see:
http://code.google.com/apis/gtt/
"""

__author__ = 'yyurevich@jellycrystal.com (Yury Yurevich)'

import urllib
import atom.http_core
import gdata.client
import gdata.acl.data
import translator.data as tdata


AUTH_SCOPE = 'http://translate.google.com/toolkit/feeds'
DOCUMENTS_URL = AUTH_SCOPE + '/documents'
TRANSLATION_MEMORIES_URL = AUTH_SCOPE + '/tm'
GLOSSARIES_URL = AUTH_SCOPE + '/glossary'
ACL_ROLES = ('owner', 'writer', 'commenter', 'reader')


def _provide_url(id_or_url):
    """
    >>> _provide_url('http://translate.google.com/toolkit/feeds/documents/xxx')
    'http://translate.google.com/toolkit/feeds/documents/xxx'
    >>> _provide_url('zzzz')
    'http://translate.google.com/toolkit/feeds/documents/zzzz'
    """
    if id_or_url.startswith(('http://', 'https://')):
        return id_or_url
    else:
        return '%s/%s' % (DOCUMENTS_URL, urllib.quote(id_or_url))


class PutEntryGDClient(gdata.client.GDClient):
    """
    GDClient with .put_entry() written in similar way to .post().
    """

    def put_entry(self, entry, uri, auth_token=None, converter=None,
                  desired_class=None, **kwargs):
        if converter is None and desired_class is None:
            desired_class = entry.__class__
        http_request = atom.http_core.HttpRequest()
        http_request.add_body_part(
            entry.to_string(gdata.client.get_xml_version(self.api_version)),
            'application/atom+xml')
        return self.request(method='PUT', uri=uri, auth_token=auth_token,
                            http_request=http_request, converter=converter,
                            desired_class=desired_class, **kwargs)

    PutEntry = put_entry


class TranslatorToolkitClient(PutEntryGDClient):
    api_version = '1.0'
    auth_service = 'gtrans'
    auth_scopes = [AUTH_SCOPE]
    ssl = False

    def get_documents(self, auth_token=None,
                      desired_class=tdata.TranslationFeed, **kwargs):
        """
        Obtains a feed with translation documents belonging to the current user.

        Args:
          auth_token: An object which sets the Authorization HTTP header in its
              modify_request method. Recommended classes include
              gdata.gauth.ClientLoginToken abd gdata.gauth.AuthSubToken
              among others. Represents the current user. Defaults to None.
              If None, this method will look for a value in the auth_token
              member of TranslationClient.
          desired_class: class descended from atom.cor.XmlElement to which
              a successful response should be converted. Defaults to
              translator.data.TranslationFeed.
          **kwargs: named arguments passed to gdata.client.GDClient.get_feed.
        """
        return self.get_feed(DOCUMENTS_URL, auth_token=auth_token,
                             desired_class=desired_class, **kwargs)

    GetDocuments = get_documents

    def get_document(self, id_or_url, auth_token=None,
                     desired_class=tdata.TranslationEntry, **kwargs):

        url = _provide_url(id_or_url)
        return self.get_entry(url, auth_token=auth_token,
                              desired_class=desired_class, **kwargs)

    GetDocument = get_document


    def get_translation_memories(self, auth_token=None,
                                 desired_class=tdata.TranslationMemoryFeed,
                                 **kwargs):
        """
        Obtains a feed with translation memories belonging to the current user.

        Args:
          auth_token: An object which sets the Authorization HTTP header in its
              modify_request method. Recommended classes include
              gdata.gauth.ClientLoginToken abd gdata.gauth.AuthSubToken
              among others. Represents the current user. Defaults to None.
              If None, this method will look for a value in the auth_token
              member of TranslationClient.
          desired_class: class descended from atom.cor.XmlElement to which
              a successful response should be converted. Defaults to
              translator.data.TranslationMemoryFeed.
          **kwargs: named arguments passed to gdata.client.GDClient.get_feed.
        """
        return self.get_feed(TRANSLATION_MEMORIES_URL, auth_token=auth_token,
                             desired_class=desired_class, **kwargs)

    GetTranslationMemories = get_translation_memories


    def get_glossaries(self, auth_token=None, desired_class=tdata.GlossaryFeed,
                       **kwargs):
        """
        Obtains a feed with glossaries belonging to the current user.

        Args:
          auth_token: An object which sets the Authorization HTTP header in its
              modify_request method. Recommended classes include
              gdata.gauth.ClientLoginToken abd gdata.gauth.AuthSubToken
              among others. Represents the current user. Defaults to None.
              If None, this method will look for a value in the auth_token
              member of TranslationClient.
          desired_class: class descended from atom.cor.XmlElement to which
              a successful response should be converted. Defaults to
              translator.data.GlossaryFeed.
          **kwargs: named arguments passed to gdata.client.GDClient.get_feed.
        """
        return self.get_feed(TRANSLATION_GLOSSARIES_URL, auth_token=auth_token,
                             desired_class=desired_class, **kwargs)

    GetGlossaries = get_glossaries


    def get_acl_list(self, acl_link, auth_token=None,
                     desired_class=gdata.acl.data.AclFeed, **kwargs):
        return self.get_feed(acl_link, auth_token=auth_token,
                             desired_class=desired_class, **kwargs)

    GetAclList = get_acl_list


    def add_acl(self, acl_link, user_email, role, auth_token=None,
                **kwargs):
        assert role in ACL_ROLES
        scope = gdata.acl.data.AclScope(type='user', value=user_email)
        role = gdata.acl.data.AclRole(value=role)
        entry = gdata.acl.data.AclEntry(role=role, scope=scope)
        return self.post(entry, acl_link, auth_token=auth_token, **kwargs)

    AddAcl = add_acl


    def update_acl(self, acl_link, user_email, new_role, auth_token=None,
                   **kwargs):
        assert new_role in ACL_ROLES
        scope = gdata.acl.data.AclScope(type='user', value=user_email)
        new_role = gdata.acl.data.AclRole(value=new_role)
        entry = gdata.acl.data.AclEntry(role=new_role, scope=scope)
        link = '%s/%s' % (acl_link, urllib.quote(user_email))
        return self.put_entry(entry, link, auth_token=auth_token, **kwargs)

    UpdateAcl = update_acl

    def delete_acl(self, acl_link, user_email, auth_token=None, **kwargs):
        link = '%s/%s' % (acl_link, urllib.quote(user_email))
        return self.delete(link)

    DeleteAcl = delete_acl
