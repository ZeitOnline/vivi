=========
zeit.push
=========

This packages provides Python bindings to various Social Media services.


Urban Airship (Push Notifications)
==================================

Configure the following settings in the batou environment:
* ``urbanairship_android_application_key``
* ``urbanairship_android_master_secret``
* ``urbanairship_ios_application_key``
* ``urbanairship_ios_master_secret``

The keys / secrets for Android and iOS are the same for production, since those
are Enterprise builds. However, for all other environments the credentials are
different, since iOS requires a certificate and thus must be a special testing
build.


Parse.com (Push Notifications)
==============================

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


Facebook
========

0. Register vivi as an application with Facebook
------------------------------------------------

- Log in to Facebook account that has write access to the 'ZEIT ONLINE' page
- Go to http://developer.facebook.com and register as developer
- Create a New App, name 'ZEIT ONLINE' (so that "posted by" type of things look
  nice)
- Go to Settings:
  * Click "Add Platform", Type: Website, Site URL: http://www.zeit.de
  * Set App Domains: zeit.de
  * Set contact email
  * Click "Save Changes"
- Go to Status & Review
  * Set application "public" (i.e. not longer developer mode, so posts made
  through it actually appear publicly).


1. Authorize the vivi application with a Facebook account
---------------------------------------------------------

Log in to Facebook account that has write access to the 'ZEIT ONLINE' page and
that is configured as administrator or developer for the Facebook application.
Then run::

    $ ./work/maintenancejobs/bin/facebook-access-token \
         --app-id=<APP-ID> \
         --app-secret=<APP SECRET> \
         --page-name=<PAGE NAME>  # e.g. 'ZEIT ONLINE'

The script will prompt you to open an URL, which contains a kind of Facebook
loging screen where you need to confirm the request for permission to post
statuses (set visibility to 'public') and manage pages. Then the browser will
be redirected to a "success" page, and its URL will contain a user-specific
access code. Paste the URL to the script, and it will exchange this code for a
long-lived (60 days) access token for the *page*.

NOTE: We require write permissions, and Facebook only allows an application to
request write permissions after they have reviewed that application. Since vivi
is an internal application, reviewing it does not make much sense. There is a
workaround, however: The user(s) that grant permissions to the application must
be registered as administrators or developers of that application -- then, no
review is necessary and the write permission can be requested anyway
(see https://developers.facebook.com/docs/apps/review/login for details).
