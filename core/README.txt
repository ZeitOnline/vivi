=========
zeit.push
=========

This packages provides Python bindings to various Social Media services.


Parse.com
=========

Configure the following settings in the batou environment:
* ``parse_application_id``
* ``parse_rest_api_key``


Twitter
=======

0. Register vivi as an application with Twitter
-----------------------------------------------

Go to https://apps.twitter.com and sign in (I'd guess @zeitonline or
@zeitonline_dev would be the appropriate owner of the application?) and create
a new app called ``vivi``. The access level needs to be "Read and Write", so
vivi can post messages.

Configure the following settings in the batou environment:
* ``twitter_application_id``: API key
* ``twitter_application_secret``: API secret


1. Authorize the vivi application with a Twitter account
--------------------------------------------------------

1. Sign out of Twitter in your web browser in case you are signed in.

2. We'll use the command-line utility `twurl`_ for doing the authoriztion::

    $ gem install twurl
    $ twurl authorize --consumer-key <API key> --consumer-secret <API SECRET>

3. Open the generated URL in a web browser, and sign in with the Twitter account
  you want to authorize (e.g. @zeitonline). Approve the request.

4. Repeat 2+3 for all accounts

5. Retrieve the access tokens from ~/.twurlrc, which looks something like
   this::

    profiles:
      gocepttest:
        GwK5gIOXUG4JnKWjOOVXFmDr0:
          username: gocepttest
          consumer_key: GwK5gIOXUG4JnKWjOOVXFmDr0
          consumer_secret: Z2zrg2QYZAY2wEVqcG5smZOxdHCX0eo9SLkutb8aRljxVvG4sB
          token: 2512010726-zzomC6jSp453N4Hsn7Ji3hYirt0a35sV0uL8Dy3
          secret: DiVzrTRkh5YJCJztiqCCwXBIzGlqa1q7Zi1bDB8aASYOj

We'll need the ``token`` and ``secret`` settings for each account in the next
step.

.. _`twurl`: https://github.com/twitter/twurl


2. Configure Twitter accounts in vivi
-------------------------------------

Edit http://cms-backend.zeit.de:9000/cms/forms/twitter-accounts.xml
(this is in ``/cms/forms`` since it will contain credentials which we'd rather
not have publicly available via http://xml.zeit.de)::

    <twitter-accounts>
      <account name="zeitonline" token="" secret="">ZON Hauptaccount</account>
      <account name="zeitonline_pol" token="" secret="">Politik</account>
      ...
    </twitter-accounts>
