These are the changelogs of the individual packages,
before they were combined into a single `vivi.core` package on 2019-04-29.


zeit.addcentral changes
=======================

1.1.6 (2016-09-26)
------------------

- Update to `zeit.cms >= 2.90`.


1.1.5 (2016-07-26)
------------------

- Extend product config to fix source configuration for testing. (ZON-3171)


1.1.4 (2014-06-24)
------------------

- Make ressort required for breaking news (VIV-25).


1.1.3 (2014-03-10)
------------------

- zeit.content.image has its own egg now.


1.1.2 (2014-02-10)
------------------

- Use Fanstatic instead of zc.resourcelibrary (VIV-296).


1.1.1 (2013-10-02)
------------------

- Use webdriver (#12573).


1.1.0 (2012-12-17)
------------------

- Fold IContentAdder and IAddLocation into zeit.cms from zeit.addcentral
  (for #10692).


1.0.3 (2012-03-06)
------------------

- Provide name of interface in dummy add context to make debugging easier.


1.0.1 (2011-11-13)
------------------

- Fix brown bag release.


1.0.0 (2011-11-13)
------------------

- Made Ressort optional (for #9133).

- Make add location configurable via an adapter (#9133)


0.2.1 (2010-08-09)
------------------

- Using versions from the ZTK.

- Adapt for test changes in zeit.cms.

- Use ``gocept.selenium`` for Selenium tests (#7549).


0.2 (2009-08-21)
----------------

- Filter Subressort again (#6016).


0.1 (2009-08-17)
----------------

- first release.


zeit.arbeit changes
====================


1.2.4 (2019-03-29)
------------------

- PERF: Don't grok browser packages by default


1.2.3 (2017-10-19)
------------------

- MAINT: Move jobbox module to z.c.modules and z.c.article


1.2.2 (2017-09-05)
------------------

- ARBEIT-61: Make IJobboxTicker API consistent with zeit.content.cp


1.2.1 (2017-09-04)
------------------

- ARBEIT-61: Move jobbox source to zeit.cms, it is used by both cp and article


1.2.0 (2017-08-29)
------------------

- ARBEIT-61: Add jobbox ticker module for articles.


1.1.0 (2017-08-10)
------------------

- ARBEIT-96: Add IZARInfobox just like IZCOInfobox


1.0.0 (2017-07-12)
------------------

- ARBEIT-1: Add arbeit speicifc interfaces


zeit.brightcove changes
=======================

2.12.7 (2018-09-05)
-------------------

- ZON-4894: Remove unused solr dependency


2.12.6 (2018-05-08)
-------------------

- HOTFIX: Handle `schedule: None` case (we previously expected empty
  dict, but BC doesn't use that)


2.12.5 (2018-05-08)
-------------------

- BUG-919: Import `expires`, which was lost in 2.10.0


2.12.4 (2018-01-26)
-------------------

- BUG-834: Send created+modified events so handlers like author
  freetext copy are triggered


2.12.3 (2018-01-17)
-------------------

- FIX: Fix error response logging


2.12.2 (2018-01-10)
-------------------

- BUG-829: Log BC error sub-code for playback API,
  log whole response if it contains no poster image


2.12.1 (2018-01-09)
-------------------

- MAINT: Remove feature toggle ``zeit.brightcove.write_on_checkin``,
  which has been in production for some time now


2.12.0 (2017-11-17)
-------------------

- BUG-747: Implement playback API connection to retrieve media data


2.11.0 (2017-10-04)
-------------------

- ZON-3409: Move from remotetask to celery


2.10.8 (2017-09-28)
-------------------

- BUG-790: Import changes to inactive videos, too


2.10.7 (2017-08-10)
-------------------

- BUG-769: Use field defaults if values are missing from BC data


2.10.6 (2017-08-08)
-------------------

- FIX: Fix entrypoint after removing old API code


2.10.5 (2017-08-08)
-------------------

- ZON-2752: Import `economics=ad_supported` as `has_advertisement`


2.10.4 (2017-08-07)
-------------------

- MAINT: Remove all old API code


2.10.3 (2017-07-13)
-------------------

- ZON-3984: Map channels to/from BC custom field


2.10.2 (2017-07-12)
-------------------

- FIX: Set explicit principal, since the notification hook runs anonymously


2.10.1 (2017-07-07)
-------------------

- FIX: Correctly map boolean fields, remove None items from custom fields

- FIX: Correctly retry API requests on auth failure

- MAINT: Add debug logging to API connection


2.10.0 (2017-07-07)
-------------------

- ZON-3984: Write to Brightcove using the new "CMS API"
  This is enabled via feature toggle ``zeit.brightcove.write_on_checkin``
  (since e.g. in staging we only have readonly credentials).

- ZON-4062: Import videos+playlists using the Brightcove "CMS API"


2.9.0 (2017-01-18)
------------------

- ZON-3576: Add commentsPremoderate property


2.8.5 (2016-10-06)
------------------

- Make authors writeable.


2.8.4 (2016-09-28)
------------------

- Really disable writing for ``disabled`` write tokens.


2.8.3 (2016-09-26)
------------------

- Update to `zeit.cms >= 2.90`.


2.8.2 (2016-09-14)
------------------

- Don't attempt writing if no write token is configured.


2.8.1 (2016-09-02)
------------------

- Fix brown-bag 2.8.0 that needlessly depended on an unreleased zeit.cms


2.8.0 (2016-09-02)
------------------

- Read ``credit`` and ``authors`` from brightcove. (ZON-2409)


2.7.2 (2016-04-18)
------------------

- Don't load Zope/UI specific ZCML in the model ZCML


2.7.1 (2015-08-24)
------------------

- Undo erroneous 2.7.0: rendition information is read-only (ZON-1566).


2.7.0 (2015-06-09)
------------------

- Make video rendition duration attribute settable (ZON-1566).


2.6.13 (2015-05-22)
-------------------

- Log raw http API results for debugging (BUG-231).


2.6.12 (2015-04-17)
-------------------

- Support serie objects for video series, too (ZON-1464).


2.6.11 (2015-03-13)
-------------------

- Update tests for re-removal of XMLSnippet (VIV-648).


2.6.10 (2015-02-03)
-------------------

- Remove characters from json that are illegal in JavaScript (BUG-114).


2.6.9 (2015-01-29)
------------------

- Also import video duration for each rendition (ZON-1275).


2.6.8 (2015-01-21)
------------------

- Update tests for re-introduction of XMLSnippet (VIV-648).


2.6.7 (2014-06-05)
------------------

- Use gocept.httpserverlayer.custom to avoid port collisions in tests.


2.6.6 (2014-01-08)
------------------

- Update to navigation source being contextual.


2.6.5 (2013-09-24)
------------------

- Skip video renditions that don't have an URL (#12852).


2.6.4 (2013-08-27)
------------------

- Publish videos/playlists synchronously (#12685).


2.6.3 (2013-08-14)
------------------

- Update to Python-2.7 and ZTK-1.1.5 (#11005).


2.6.2 (2013-05-22)
------------------

- Fix brownbag release 2.6.1


2.6.1 (2013-05-21)
------------------

- Fix double publish of videos and playlist (#12411)


2.6 (2013-04-23)
----------------

- Use the new tagging infrastructure (#8623).


2.5.2 (2013-02-20)
------------------

- Apply ignore_for_update also while adding and publishing (#11990)


2.5.1 (2013-01-09)
------------------

- Remove ignore_for_update from BC-URL (#11805)


2.5.0 (2012-12-17)
------------------

- Evaluate ignore_for_update customField, which results in not updating
  anything, if set to true (#11782)


2.4.0 (2012-06-07)
------------------

- Fixed removal of restricted characters from Brightcove JSON response in
  conjunction with UTF-8 encoding. (#10600)
- Add view for manually updating Brightcove objects (#10934).


2.3.0 (2012-03-06)
------------------

- Log a warning if multiple video objects with the same id are found (#10254).

- Filter xml restricted characters from brightcove's json responses in
  addition to json invalid characters. (#9705)


2.2.0 (2012-01-17)
------------------

- Convert renditions to cms-renditions.


2.1.2 (2011-12-08)
------------------

- Update the metadata of playlists when a video changes (#10042).


2.1.1 (2011-12-01)
------------------

- Commit after each BC object (#10024).


2.1.0 (2011-12-01)
------------------

- Use separate Remotetask service for publishing BC objects (#10024).

- When importing from BC, also publish videos/playlists when they already are
  published but have been changed in DAV (#10023).

- When updating from BC, delete playlists in two phases in order to play nice
  with asynchronous publication (retraction) (#10022).


2.0.1 (2011-11-23)
------------------

- Import and export references (#9831).

- Fix change detection of playlists (#9976)

- Remove bits and pieces which try to save playlists back to brightcove:
  playlists are not changed in the CMS so there is no need to actually update
  brightcove.

- Map brightcove release date correcly to date first released.

- Default Daily Newsletter to false for videos.

- Move serie source to zeit.content.video.

- BC-Deleted videos are now retracted in one pass and deleted in a second
  pass. This means that they are actually being retracted.

- BC-Inactive videos are now kept in the CMS as unpublished objects.


2.0.0 (2011-11-13)
------------------

- Impport videos and playlists into the DAV servers (#8996).

- Add backward compatibility adapters for old video and playlist unique Ids
  (#9746).


0.10.0 (2011-08-12)
-------------------

- added mediadeliverymethod in connection.


0.9.1 (2011-04-29)
------------------

- Add timeout for all Brightcove requests (#8021).


0.9.0 (2011-03-23)
------------------

- Changed mapping for ``last-semantic-change`` to ``date_first_released``

- Videos can be checked out now by the system. This allows to create free
  teasers of videos (for #7826).

- Extracted ``get_expires`` to get the me earliest expires date from a list of
  playlists and videos.

- Change indexes as the interface requires an solr attribute now (for #8559)

- Remove Brightcove content from addcentral.


0.8.0 (2010-08-16)
------------------

- New layout for video-form

- Honour the default values of the interface in mapped properties.


0.7.0 (2010-08-09)
------------------

- Fix tests after changes in zeit.cms (#7549)
- changes some default values
- Button "Save and back to search" (#7827)

0.6.1 (2010-07-15)
------------------

- Fix brightove SOLR updater so it implements IUpdater correctly. Otherwise
  re-indexing videos doesn't work correctly.


0.6.0 (2010-07-12)
------------------

- Since brightcove caches absolute URLs better, we use the same timestamp for
  a request more often
- Use proper preview URL for brightcove content (#7030).
- Adapted last_semantic_change from date_last_modified
- Use an empty string instead of null in REST calls for brightcove does not
  recognize null
- Update brightcove videos if video_still is updated. Even though the
  modified_date is not updated, this might happen in upstream.
- Add image-tag to video XML reference (#7625)
- Add type="video" attribute to video XML reference (#7625)


0.5.0 (2010-06-09)
------------------

- Added solr indexes for banner and banner-id (#7382).
- Update videos "latest modified first" (#7209).
- Add uniqueId to asset references (#7381).


0.4.1 (2010-06-03)
------------------

- Handle missing expire dates when writing asset references.
- Add id_prefix to the interface so it gets security clearance.


0.4.0 (2010-06-02)
------------------

- Add a solr index 'h264_url' that contains the 'flv_url' of the video (#7362).
- Change update-repository to be long-running instead of one-shot (#7339).
- Provide an adapter to ITimeBasedPublishing, so videos get an expires
  attribute when included in a centerpage (#7335).
- Allow both videos and playlists as assets (#7195).
- Prefix the IDs of video/playlist assets in XML (vid123/pls987) (#7194).
- Add expires attribute to asset XML-references (#7380).


0.3.2 (2010-05-06)
------------------

- Explicitly index solr instead of modified event which causes the modification
  time to change.


0.3.1 (2010-05-06)
------------------

- Do not unconditionally delete all playlists from solr but only those we know
  about but brightcove doesn't know about.

- Update solr synchronously. The async updating was not intentional.


0.3.0 (2010-05-03)
------------------

- The repository does not access the Brightcove API directly anymore, it only
  functions as a local cache. It is populated periodically by cron (Solr is
  updated then, too, as a "byproduct"). (#7150, #7163)


0.2.1 (2010-04-27)
------------------

- Fully implement IPublishInfo interface for videos and playlist.


0.2.0 (2010-04-22)
------------------

- videoIds in Playlists are a property
- added IBCContent between ICMSContent and IBrightcoveContent
- IReferenceProvider adapted, which returns a list of IBCContent
  (to avoid API-Calls)
- set timdedelta for modified videos to 2hours. this decreases amount of
  timeouts

0.1.2 (2010-04-14)
------------------

- brightcove will delete all videos with state != ACTIVE from internal and
  public solr


0.1.1 (2010-04-12)
------------------

- better handling for page iteration using brightcove API.


0.1.0 (2010-04-09)
------------------

- First release


zeit.campus changes
====================

1.6.10 (2019-03-29)
-------------------

- PERF: Don't grok browser packages by default


1.6.9 (2018-08-06)
------------------

- ZON-4670: Restructrure link ui


1.6.8 (2018-05-29)
------------------

- MAINT: Update to changed CP API


1.6.7 (2017-10-04)
------------------

- ZON-3409: Move from remotetask to celery


1.6.6 (2017-08-10)
------------------

- ARBEIT-96: Delete debate interaface and its property adapter


1.6.5 (2017-08-07)
------------------

- ZON-4006: Update to mobile field split


1.6.4 (2017-05-22)
------------------

- ZON-3917 remove bigshare button checkbox


1.6.3 (2016-09-14)
------------------

- ZON-3318: Remove bigshare buttons in Campus.


1.6.2 (2016-04-21)
------------------

- Only show relevant infobox form fields


1.6.1 (2016-04-20)
------------------

- BUG-401: Remove validation constraint from ITopic.label


1.6.0 (2016-04-15)
------------------

- ZON-2988: Change ``IStudyCourse`` from DAVPropertiesAdapter to article module


1.5.0 (2016-04-08)
------------------

- ZON-2930: Add separate facebook fields for article/gallery/link


1.4.0 (2016-04-06)
------------------

- ZON-2494: Add ``IStudyCourse`` setting for articles


1.3.0 (2016-03-15)
------------------

- ZON-2491: Add ``IDebate.action_url`` for infoboxes


1.2.0 (2016-03-11)
------------------

- ZON-2838: Add topicpage link


1.1.0 (2016-02-22)
------------------

- ZON-2507: Allow ressort-based section markers


1.0.0 (2016-02-12)
------------------

- ZON-2507: Add zeit.campus specific interfaces


zeit.cms changes
================

3.30.0 (2019-04-23)
-------------------

- IR-80: Implement `/@@source?name=` API


3.29.0 (2019-04-10)
-------------------

- IR-54: Implement `/@@lock_status?uuid=` API


3.28.0 (2019-04-02)
-------------------

- IR-36: If configured, POST content uniqueId to HTTP webhook after checkin


3.27.1 (2019-04-02)
-------------------

- FIX: Add missing import


3.27.0 (2019-03-29)
-------------------

- PERF: Don't grok browser packages by default, since at least zeit.web does not
  need them.
  This necessitates backporting `<grok exclude="">` to be multivalued
  from grokcore.component-2.7.


3.26.1 (2019-03-20)
-------------------

- FIX: Use channel source for channel dropdowns, not the ressort source


3.26.0 (2019-03-18)
-------------------

- MAINT: Set otherwise unused `byline` field readonly

- MAINT: Support configuring the fluentbit logging formatter from ini files


3.25.4 (2019-03-07)
-------------------

- FIX: Display the actual publish error message instead of "500
  Internal Server Error" in the quick publish dialog.


3.25.3 (2019-02-22)
-------------------

- PERF: Don't unnecessarily evaluate the repository root folder,
  when all we want is to check a getUtility result.


3.25.2 (2019-02-21)
-------------------

- PERF: Don't unnecessarily resolve parent on checkout


3.25.1 (2019-02-19)
-------------------

- ZON-2932: Revert <pre> for IText, it's too far-ranging in effect (see 3.23.2)


3.25.0 (2019-02-18)
-------------------

- ZON-2932: Add RestructuredTextDisplayWidget


3.24.0 (2019-02-18)
-------------------

- FIX: Allow multiple filters for retractlog


3.23.5 (2019-02-15)
-------------------

- ZON-2932: Add convenience API to SimpleFixedValueSource


3.23.4 (2019-02-11)
-------------------

- ZON-2932: Don't apply <pre> to ITextLine (see 3.23.2)


3.23.3 (2019-02-07)
-------------------

- BUG-1054: Consider a workingcopy's `has_semantic_change` setting on
  the default checkin menu button, too


3.23.2 (2019-02-07)
-------------------

- ZON-2932: Always display IText with <pre>


3.23.1 (2019-02-06)
-------------------

- FIX: Support `https` CMS `vivi.zeit.de` URLs in ICMSContent resolution


3.23.0 (2019-02-05)
-------------------

- ZON-5115: Prevent renaming a folder with content


3.22.0 (2019-02-01)
-------------------

- ZON-5110: Add podigee_url as an attribute of Serie


3.21.0 (2019-01-30)
-------------------

- ZON-5091: Add color as an attribute of Serie


3.20.1 (2019-01-22)
-------------------

- ZON-5026: Add `banner_outer` to admin tab


3.20.0 (2019-01-09)
-------------------

- ZON-5025: Make SimpleFixedValueSource work with dicts


3.19.2 (2018-12-20)
-------------------

- BUG-951: Suppress errors when unpickling XML objects, so we can
  always load _something_


3.19.1 (2018-11-28)
-------------------

- ZON-4106: Adjust UI for copyrights


3.19.0 (2018-10-17)
-------------------

- ZON-2694: Add retract log to retract multiple resources and view status


3.18.0 (2018-10-11)
-------------------

- ZC-90: Add `commentsAPIv2` property to ICommonMetadata


3.17.0 (2018-10-05)
-------------------

- ZON-4801: Make CMSContentTypeSource DAV-serializable

- ZON-4849: Add podigee ID to Serie objects

- ZON-3312: Remove deprecated fields from ICommonMetadata, asset badges,
  obsolete workflow states `refined` and `images_added`


3.16.0 (2018-09-17)
-------------------

- ZON-4893: Move BeforePublishEvent after we update published and date_last_published,
  so zeit.retresco can run its indexing at that point in time.

- MAINT: Remove long-obsolete old workflow 'OK' status


3.15.0 (2018-09-03)
-------------------

- ZON-4846: Support multiple values for `available` in XMLSource


3.14.5 (2018-08-20)
-------------------

- BUG-978: Fix showing series title in display view


3.14.4 (2018-08-06)
-------------------

- ZON-4670: Use filename normalization for link objects as well


3.14.3 (2018-08-01)
-------------------

- FIX: Be defensive about tags to highlight


3.14.2 (2018-08-01)
-------------------

- FIX: Be defensive about nonexistent source values


3.14.1 (2018-07-26)
-------------------

- FIX: Fix mock setup for tagger


3.14.0 (2018-07-26)
-------------------

- ZON-4742: Add highlighting to tags with topicpages


3.13.1 (2018-07-11)
-------------------

- ZON-4753: Add checkbox to hide adblocker notification

- MAINT: Add user information to SSO cookie


3.13.0 (2018-06-08)
-------------------

- ZON-4709: Add `IUUID.shortened` property


3.12.2 (2018-06-06)
-------------------

- TMS-227: Make autocomplete available on DropObjectWidget


3.12.1 (2018-05-30)
-------------------

- TMS-227: Refactor `channels` serialization so zeit.retresco can reuse it


3.12.0 (2018-05-29)
-------------------

- TMS-227: Change serialization to DAVPropertyConverter for
  reusability, for `channels`, `product`, `serie`.

- TMS-227: Remove obsolete `product_text` field (and `workflow:product-name` DAV property)

- MAINT: Move autocomplete source query view here from zeit.find,
  generalize using ISourceQueryURL lookup mechanism

- FIX: Allow to delete object path properties by setting them to `None`.


3.11.1 (2018-05-14)
-------------------

- FIX: Update DAVConverterWrapper to changed IDAVPropertyConverter API


3.11.0 (2018-05-14)
-------------------

- FIX: Use the DAV properties as additional descriptor for
  IDAVPropertyConverter instead of the content object (see 3.4.0)

3.10.1 (2018-05-14)
-------------------

- BUG-890: Store title and type in clipboard entries, so we don't have
  to resolve the content to render the clipboard


3.10.0 (2018-05-09)
-------------------

- ZON-4639: Add `kind` property to `Serie` objects


3.9.1 (2018-05-04)
------------------

- FIX: Handle non-ascii in DAV properties tab


3.9.0 (2018-05-03)
------------------

- MAINT: Put DAV properties tab behind zeit.cms.repository.ViewProperties permission


3.8.3 (2018-05-02)
------------------

- ZON-2855: No longer update related content objects on checkin


3.8.2 (2018-05-02)
------------------

- MAINT: Add tab that lists DAV properties


3.8.1 (2018-04-19)
------------------

- MAINT: Support `https` live `www.zeit.de` URLs in ICMSContent resolution


3.8.0 (2018-04-19)
------------------

- OPS-874: Introduce ``INonRecursiveCollection`` marker interface


3.7.1 (2018-04-17)
------------------

- ZON-4532: Remove feature toggle `zeit.retresco.tms`


3.7.0 (2018-04-17)
------------------

- ZON-4532: Remove intrafind/retresco abstraction from tagging widget


3.6.7 (2018-04-09)
------------------

- ZON-4581: Move banner checkbox from option to admin tab


3.6.6 (2018-03-22)
------------------

- BUG-717: Fix column overriding inheritance


3.6.5 (2018-03-22)
------------------

- BUG-717: Ignore any errors in listing columns


3.6.4 (2018-03-21)
------------------

- MAINT: Put "show/hide in tree" views behind feature toggle
  ``zeit.cms.repository.tree`` too (see 3.2.2)


3.6.3 (2018-03-15)
------------------

- TMS-190: Don't suppress events on checkin via "quick publish"


3.6.2 (2018-03-15)
------------------

- TMS-188: Only sync tags to XML if a <head> node exists


3.6.1 (2018-03-13)
------------------

- TMS-186: Fix cookie domain configuration handling


3.6.0 (2018-03-13)
------------------

- TMS-186: Implement SSO-style cookie generating login view

- MAINT: Add `zopeshell` entrypoint that sets up logging from paste.ini


3.5.1 (2018-03-06)
------------------

- FIX: Put "update keywords" button rule behind feature toggle
  `zeit.retresco.tms`


3.5.0 (2018-03-01)
------------------

- TMS-156: Don't show "update keywords" for new articles

- MAINT: Introduce permission for "show in TMS" link


3.4.1 (2018-02-28)
------------------

- TMS-173: No longer mark the first x keywords differently


3.4.0 (2018-02-27)
------------------

- TMS-162: Register DAVProperty descriptors
- TMS-162: Add the content object as a descriptor for IDAVPropertyConverter
- TMS-162: Provide lookup of TypeDeclaration by type name


3.3.1 (2018-02-13)
------------------

- BUG-846: Work around celery vs. DAV-cache race condition for "save+publish"

- MAINT: Remove trisolute current topics service, it's not used anymore


3.3.0 (2018-01-30)
------------------

- BUG-834: Don't log access changes when the value didn't actually change

- BUG-841: Provide ``ISkipDefaultChannel`` interface so content types can
  opt out of setting default channel from ressort.


3.2.2 (2018-01-17)
------------------

- MAINT: Put repository tree viewlet behind feature toggle
  ``zeit.cms.repository.tree``, which we leave disabled everywhere,
  since it's unused and can be very slow due to lots of DAV traversal


3.2.1 (2018-01-09)
------------------

- TMS-134: Fix ObjectMovedEvent after introducing dynamic parents


3.2.0 (2018-01-08)
------------------

- TMS-134: Resolve content without traversal if possible


3.1.4 (2017-11-01)
------------------

- BUG-791: Ignore nonexistent childname entries in repository values()


3.1.3 (2017-10-20)
------------------

- FIX: Send no-cache headers at least for our full pages,
  so browsers don't cache e.g. a directory listing


3.1.2 (2017-10-19)
------------------

- MAINT: Move jobbox source to z.c.modules


3.1.1 (2017-10-17)
------------------

- MAINT: Remove remotetask from ZODB


3.1.0 (2017-10-12)
------------------

- ZON-4210: Add fallback_image flag to serie source


3.0.0 (2017-10-04)
------------------

- ZON-3409: Move from remotetask to celery


2.108.0 (2017-08-09)
--------------------

- BUG-757: Allow storing publish_multiple errors in objectlog


2.109.2 (2017-09-28)
--------------------

- ARBEIT-116: Better markdown support


2.109.1 (2017-09-07)
--------------------

- ZON-3885: Remove ad placeholder configuration source


2.109.0 (2017-09-04)
--------------------

- ARBEIT-61: Add source for jobbox ticker feeds


2.108.2 (2017-08-31)
--------------------

- Show ZAR logo on ZAR resources


2.108.1 (2017-08-17)
--------------------

- BUG-773: Don't cycle non-XML content during publish


2.108.0 (2017-08-09)
--------------------

- BUG-757: Allow storing publish_multiple errors in objectlog


2.107.1 (2017-08-08)
--------------------

- FIX: Translate collected publish_multi errormessages


2.107.0 (2017-08-07)
--------------------

- ARBEIT-96: Add "Arbeit" ressort to test ressorts.xml

- ZON-3860: Support start_job() with URL parameter in publish.js

- ZON-3677: Remove `ICommonMetadata.push_news`, it's not used anymore

- BUG-757: Collect errors during publish_multiple instead of aborting

- BUG-199: Abort publish if content is already locked


2.106.1 (2017-07-18)
--------------------

- BUG-748: Handle IAutomaticallyRenameable in timebased workflow
  and object log


2.106.0 (2017-07-18)
--------------------

- BUG-345: Delete objectlog entries on delete and move

- BUG-345: Only reset actual publishinfo properties on copy

- BUG-500: Add `retract_dependencies` flag to `IPublicationDependencies`


2.105.1 (2017-07-13)
--------------------

- MAINT: Rename navigation source


2.105.0 (2017-07-12)
--------------------

- ZON-4065: Support setting async principal explicitly


2.104.3 (2017-07-10)
--------------------

- MAINT: Allow changing date_first_released in admin tab


2.104.2 (2017-07-07)
--------------------

- MAINT: Remove obsolete feature toggle ``zeit.cms.rr-access``


2.104.1 (2017-07-07)
--------------------

- MAINT: Add link to TMS to keyword widget


2.104.0 (2017-07-07)
--------------------

- ZON-3983: Base SerieSource on ObjectSource

- MAINT: Provide `toggleFormFieldHelp` JS to make zc.form combinationwidget happy


2.103.1 (2017-07-08)
--------------------

- ZON-4065: Install separate task queue for brightcove imports


2.103.0 (2017-06-27)
--------------------

- ZON-4008: Add title to PrintRessortSource


2.102.0 (2017-06-22)
--------------------

- ZON-4012: JS for "insert bullet" button

- ZON-4013: Support `warning` state in `limitedInput`

- FIX: Improve styling of unloadable object references


2.101.0 (2017-06-21)
--------------------

- MAINT: Send specific event when a user triggers a cache refresh

- FIX: Empty blacklist config entry prevents publishing

- FIX: Improve error handling with unloadable object references


2.100.2 (2017-06-13)
--------------------

- BUG-730: Remove rename warning, its most common case is now prohibited anyway


2.100.1 (2017-06-12)
--------------------

- ZON-3485: Respect missing_value in MarkdownWidget


2.100.0 (2017-06-09)
--------------------

- BUG-730: Prevent renaming published content

- ZON-3948: Implement configurable path blacklist to prevent publishing
  product-config ``zeit.workflow:blacklist``


2.99.1 (2017-06-01)
-------------------

- Fix broken release


2.99.0 (2017-06-01)
-------------------

- BUG-669: Honor the configured field's missing_value in `Structure` descriptor


2.98.0 (2017-05-22)
-------------------

- ZON-3917: Remove big share buttons field from ICommenMetadata

- ZON-3942: Create retract jobs after publishing imported objects that
  only have `released_to` set

- BUG-301: Cancel scheduled publish jobs when timestamps are changed,
  regardless of while checked-out or checked-in

- BUG-562: RelatedBase must use XML-Persistent, so changes are stored
  properly on commit


2.97.5 (2017-05-11)
-------------------

- BUG-105: Remove unneded double-unpickle workaround; since it looks
  as if it might provoke double free().


2.97.4 (2017-05-10)
-------------------

- FIX: Serialize tag uniqueIds correctly in update json view


2.97.3 (2017-05-10)
-------------------

- FIX: Serialize tag uniqueIds correctly in formlib widget


2.97.2 (2017-05-05)
-------------------

- FIX: Synchronous multi publish works with ID's now


2.97.1 (2017-04-12)
-------------------

- ZON-3851: Log article access changes in Vivi-Chronik.

- MAINT: Dont start multipublish task if no objects to publish are given


2.97.0 (2017-04-06)
-------------------

- ZON-3475: Make checkout lock timeout configurable
  product-config ``zeit.cms:checkout-lock-timeout[-temporary]``


2.96.6 (2017-03-20)
-------------------

- FIX: Work around the longstanding "context menu UI bug" by hiding
  the main context menu when a child is selected


2.96.5 (2017-03-15)
-------------------

- ZON-3792: Put ``access`` widget behind feature toggle ``zeit.cms.rr-access``


2.96.4 (2017-03-10)
-------------------

- HOTFIX: Add bw-compat for persistent input instances of timebased publish jobs


2.96.3 (2017-03-09)
-------------------

- FIX: IObjectLog needs ICMSContent to work.


2.96.2 (2017-03-08)
-------------------

- FIX: Add Workflow log entry to publish_multiple


2.96.1 (2017-03-01)
-------------------

- Handle dependencies in publish_multiple


2.96.0 (2017-03-01)
-------------------

- ZON-3447: Implement ``IPublish().publish_multiple([id, id, id, ...])``


2.95.3 (2017-02-15)
-------------------

- PERF: Don't update relationship index twice on checkin


2.95.2 (2017-02-15)
-------------------

- MAINT: Remove obsolete syndication/channel support on publish


2.95.1 (2017-02-13)
-------------------

- MAINT: Skip filename conventions for rawxml and text, too.


2.95.0 (2017-02-08)
-------------------

- ZON-3533: Implement dependent products

- ZON-3485: Introduce ``OverridableProperty`` descriptor


2.94.2 (2017-01-26)
-------------------

- ZON-3629: Add overscrolling option


2.94.1 (2017-01-25)
-------------------

- PERF: Only write section markers if they actually changed, not every time


2.94.0 (2017-01-18)
-------------------

- ZON-3464: Add banner content option

- ZON-3576: Add commentsPremoderate property


2.93.3 (2017-01-13)
-------------------

- BUG-505: Try a different workaround for the zope.component cache poisoning


2.93.2 (2016-12-30)
-------------------

- BUG-505: Work around strange zope.component bug that intermittently
  causes IZONContent to not be found as an ISectionMarker.


2.93.1 (2016-12-15)
-------------------

- MAINT: Be defensive about ContainedProxy vs provided interfaces


2.93.0 (2016-12-06)
-------------------

- Add ``set_none`` parameter to ``apply_default_values`` helper function.


2.92.3 (2016-12-06)
-------------------

- BUG-558: Display ``date_last_published_semantic`` on workflow form.


2.92.2 (2016-11-25)
-------------------

- ZON-3172: Assume default "free" for ``access`` when content has no value.


2.92.1 (2016-11-23)
-------------------

- ZON-2996: Prevent deleting published content


2.92.0 (2016-10-19)
-------------------

- ZON-3377: Add ``IProduct.cp_template``.

- ZON-3356: Add ``PRINT_RESSOURT_SOURCE``.


2.91.2 (2016-10-06)
-------------------

- Shorten the displayed traceback on the error page


2.91.1 (2016-10-04)
-------------------

- Return None from ObjectSource properties if the ID was not found.


2.91.0 (2016-09-30)
-------------------

- Add ``suppress_errors`` parameter to ``ContentList.insert``.


2.90.1 (2016-09-29)
-------------------

- Fix keyword display widget


2.90.0 (2016-09-26)
-------------------

- ZON-3364: Add ``IWhitelist.locations()`` to abstract location search.

- ZON-3228: Move ``Result`` from ``zeit.cms.tagging`` to ``zeit.cms``.

- ZON-3362: Add ``IProduct.centerpage`` uniqueId template.

- Rename `TestContentType` to `ExampleContentType` to avoid py.test warnings.


2.89.0 (2016-09-16)
-------------------

- ZON-3199: Do not provide dict-like access on ``Whitelist`` anymore. ``get``
  is provided to query for a specific ``id`` instead.

- ZON-3199: Move intrafind specific ``Whitelist`` and ``Tag`` to
  ``zeit.intrafind``.

- ZON-3236: Introduce ``ITopicpages`` utility to abstract the total of
  all topic pages / whitelist entries.


2.88.0 (2016-09-14)
-------------------

- ZON-3318: Add field bigshare_buttons to metadata.


2.87.0 (2016-09-13)
-------------------

- Rename ``acquisition`` to ``access``.


2.86.1 (2016-09-12)
-------------------

- Make finding the section of a content object work with ressort-based
  sections as well as folder-based sections.
  ISection(content) now directly returns the section interface,
  instead of the folder implementing a section interface.
  As a side-effect, vivi now wears a doctoral hat on campus content.


2.86.0 (2016-09-07)
-------------------

- Include celery task id in log messages.


2.85.1 (2016-09-02)
-------------------

- ``live_url_to_content`` and ``vivi_url_to_content`` do no longer break if
  content does not exist.


2.85.0 (2016-08-24)
-------------------

- Remove sitecontrol sidebar, it's a resource hog and not really used anymore.

- Do not automatically set channel when products.xml forbids it. (ZON-3248)


2.84.1 (2016-08-22)
-------------------

- Extend ``zeit.cms.content.sources.ProductSource`` to store the XML attributes
  ``volume`` and ``location`` on it's values to filter the source in
  ``z.c.volume``. (ZON-3252, ZON-3255)


2.84.0 (2016-07-21)
-------------------

- Ignore strange JS errors caused by Firefox bug.

- Add acquisition attribute to CMS content


2.83.0 (2016-07-04)
-------------------

- Set up celery/zope integration (ZON-3188).


2.82.2 (2016-06-29)
-------------------

- Cache sitecontrol contents to relieve load from the servers.


2.82.1 (2016-06-27)
-------------------

- Heuristically remove vivi view names when resolving ICMSContent.


2.82.0 (2016-06-13)
-------------------

- Assign type-specific section markers before general ones, so they
  count as more specific (BUG-428).


2.81.1 (2016-06-06)
-------------------

- Be defensive about missing/invalid storystream references.


2.81.0 (2016-06-06)
-------------------

- Move tags-to-xml and trisolute code here from zeit.intrafind (ZON-3114).

- Change ``ICommonMetadata.storystreams`` to objects that provide
  id, title and the CP as ``references`` (ZON-2769).


2.80.0 (2016-05-12)
-------------------

- Integrate bugsnag for error reporting


2.70.3 (2016-05-10)
-------------------

- Display server error message in publish popup.


2.70.2 (2016-04-27)
-------------------

- Fix error handling in publish popup.


2.70.1 (2016-04-26)
-------------------

- Consider publish priority in publish popup.


2.70.0 (2016-04-26)
-------------------

- Determine publish priority according to content type (ZON-2924).


2.69.2 (2016-04-21)
-------------------

- Remove accidental JS debugger statement


2.69.1 (2016-04-21)
-------------------

- Silence annoying ZCML warning


2.69.0 (2016-04-19)
-------------------

- Don't load Zope/UI specific ZCML in the model ZCML


2.68.0 (2016-04-13)
-------------------

- Don't automatically publish RelatedContent anymore (ZON-2750).

- Remove related CenterPages from references index (ZON-2750, ZON-2764).


2.67.0 (2016-04-07)
-------------------

- Move ``hex_literal`` here from zeit.content.cp (ZON-2898).


2.66.0 (2016-03-21)
-------------------

- Support DAV type conversion for ObjectSource (ZON-2931).


2.65.2 (2016-03-03)
-------------------

- Mark redirects to content as not cacheable (BUG-352).

- Add new logo for zeit.campus (ZON-2507).


2.65.1 (2016-02-29)
-------------------

- Don't update relationship index during cycling while publishing.


2.65.0 (2016-02-22)
-------------------

- Introduce ressort-based section markers for zeit.campus (ZON-2507)

- Introduce ``zeit.cms.util.MemoryFile``, a closeable StringIO. Use it for
  resource bodies (BUG-338).

- Limit display size of search result images (BUG-331).


2.64.3 (2016-02-03)
-------------------

- Don't call style_dropdowns for the whole document for each fragment.


2.64.2 (2016-01-22)
-------------------

- Configure dogpile.cache via product config, not paste.ini, since only the
  webservers even know about the latter.


2.64.1 (2016-01-22)
-------------------

- Remove some spacing around widgets


2.64.0 (2016-01-20)
-------------------

- Replace gocept.cache.method with dogpile.cache, so the caching backend is
  configurable, and compatible with zeit.web (ZON-2576).


2.63.0 (2016-01-05)
-------------------

- Add ``find(type_id)`` to CMSContentTypeSource.


2.62.1 (2016-01-04)
-------------------

- Make FakeEntry actually conform to ICMSContent.


2.62.0 (2015-11-17)
-------------------

- XML property descriptors now return themselves when accessed via the
  class.


2.61.1 (2015-10-30)
-------------------

- Be more defensive about looking up reference targets.


2.61.0 (2015-10-29)
-------------------

- Add "admin" tab, for now it allows changing the
  ``date_last_published_semantic`` property (DEV-951).


2.60.2 (2015-10-22)
-------------------

- Even more complete security declaration for lxml objects.


2.60.1 (2015-10-22)
-------------------

- More complete security declaration for lxml objects.


2.60.0 (2015-10-14)
-------------------

- Look up queue names in product config for ``zeit.cms.async.function``.

- Add separate task queue ``solr``.


2.59.2 (2015-10-09)
-------------------

- Declare ICMSContent on syndication FakeEntry, conform to
  XMLReferenceUpdater API.


2.59.1 (2015-10-09)
-------------------

- Remove PUBLISHED_FUTURE_SHIFT, instead use a PUBLISH_DURATION_GRACE fudge
  factor during comparison for "published with changes".


2.59.0 (2015-10-05)
-------------------

- Add parameter ``use_default_value`` to ``ObjectPathAttributeProperty``,
  and generally make it behave more like ``ObjectPathProperty``.

- Apply PUBLISH_FUTURE_SHIFT to ``date_last_published_semantic``, too.


2.58.1 (2015-09-11)
-------------------

- Update date_last_published_semantic before publish, since after publish
  would mean that the change is not publicly visible.

- Support preferring ``.cp2015`` CPs in sitecontrol (DEV-939).


2.58.0 (2015-09-10)
-------------------

- Add fields ``advertisement_title`` and ``advertisement_text`` to
  ``ICommonMetadata`` (ZON-1340, ZON-1341).


2.57.1 (2015-09-08)
-------------------

- Fix security declaration for feed FakeEntry.


2.57.0 (2015-09-07)
-------------------

- Update to changed whitelist XML format so we can use one unified XML file
  (ZON-2115).


2.56.2 (2015-09-02)
-------------------

- Remove button for checkin with semantic change when displaying a checkin
  conflict error. (DEV-927)


2.56.1 (2015-08-27)
-------------------

- Use named pipes for subprocess.Popen calling the publish script to prevent
  hanging.


2.56.0 (2015-08-27)
-------------------

- Change checkin menu button to not update last semantic change,
  add checkbox to update semantic change to workflow form (DEV-834).

- Add helper classes ObjectSource and AllowedMixin.


2.55.1 (2015-08-25)
-------------------

- Preserve API compatiblity of ``zeit.cms.Tabs.activate``.


2.55.0 (2015-08-24)
-------------------

- Add ``tldr`` fields for storystreams (DEV-883, DEV-885).

Internal:

- Add field to register colorpicker widget on.

- Add CSS classes to datetime widget buttons.

- Add parameter ``show_parent`` to ``zeit.cms.Tabs.activate`` (DEV-853).


2.54.4 (2015-08-24)
-------------------

- Don't prematurely unlock during cycle() while publishing, hold lock until the
  actual unlock() at the end (BUG-308).


2.54.3 (2015-08-18)
-------------------

- Include CSS in error page.


2.54.2 (2015-08-14)
-------------------

- Workingcopy previews done via Friedbert now traverse the workingcopy directly
  instead of a temporary DAV upload (DEV-908).


2.54.1 (2015-08-13)
-------------------

- Use separate config file for subchannels, too (DEV-634).


2.54.0 (2015-08-13)
-------------------

- Let FakeEntry implement ICommonMetadata with all attributes set to None.

- Extract "list of content" behaviour from Feed content type into separate
  class.

- Ignore attributes starting with _v_ in xmlsupport.Persistent, so we
  better conform to the zodb.Persistent behaviour.


2.53.2 (2015-08-05)
-------------------

- Make workingcopy preview commit configurable, since it leads to taskprocessor
  conflict errors for unknown reasons (DEV-855).


2.53.1 (2015-08-05)
-------------------

- Log when cycling objects to update metadata.


2.53.0 (2015-08-04)
-------------------

- Add uniqueId to repr for content objects.


2.52.1 (2015-07-29)
-------------------

- Manually commit workingcopy preview upload to make it visible for zeit.web
  (DEV-855).


2.52.0 (2015-07-23)
-------------------

- Add MarkdownWidget (DEV-847).


2.51.1 (2015-07-06)
-------------------

- Parametrize queue name in monitoring view.


2.51.0 (2015-07-06)
-------------------

- Set default channel to ressort for all content types, not just articles
  (DEV-833).

- Add ``use_default`` parameter to ObjectPathProperty.


2.50.0 (2015-06-30)
-------------------

- Make taskprocessor queue name for async functions configurable (DEV-816).
  * Requires product config ``zeit.cms:task-queue-async``.


2.49.0 (2015-06-25)
-------------------

- Remove feature toggle ``zeit.content.cp.automatic`` and permission
  ``zeit.content.cp.View/EditAutomatic`` (DEV-832).


2.48.0 (2015-06-23)
-------------------

- Revert using default values for both comment metadata properties (BUG-272).


2.47.2 (2015-06-23)
-------------------

- Use separate config file for channels (DEV-634).

- Fix table sorting JS in FF38 (BUG-276).


2.47.1 (2015-06-18)
-------------------

- Point several taskprocessor views to the configured queue instead of
  hardcoding (DEV-816).


2.47.0 (2015-06-18)
-------------------

- Use default values for both comment metadata properties (BUG-272).


2.46.3 (2015-06-11)
-------------------

- Mark message notifier red only when error messages are present (DEV-22).


2.46.2 (2015-06-10)
-------------------

- Style error messages more prominently (DEV-22).


2.46.1 (2015-06-10)
-------------------

- Make taskprocessor queue name for publishing configurable (DEV-816).


2.46.0 (2015-06-09)
-------------------

- Display validation errors in Lightbox / Popup during publish. (DEV-22)

- Allow user to publish even though validation *warnings* are present. (DEV-22)

- Configure js.underscore.


2.45.2 (2015-05-18)
-------------------

- Tweak MochiKit DragAndDrop to allow landing zones to enlarge on hover.


2.45.1 (2015-05-04)
-------------------

- Replace MochiKit $$ with jQuery, which is *much* faster in Firefox.

- Disable JS debug logging to console by default.

- Overwrite parts of MochiKit Droppables / Draggables to improve performance.


2.45.0 (2015-04-28)
-------------------

- Allow using custom images for checkboxes (DEV-745).


2.44.0 (2015-04-23)
-------------------

- Internal: set site and create interaction in setup of selenium tests, too.

- Add append method to Feed. (DEV-745)

- Add id to TabViews, so they can be manipulated using CSS. (DEV-746)


2.43.1 (2015-04-17)
-------------------

- Support serie objects for video series, too.


2.43.0 (2015-04-15)
-------------------

- Recognize content_ad as banner position (DEV-724).

- Display the exception traceback in the error view.


2.42.0 (2015-03-26)
-------------------

- Switch from basic auth to login form (DEV-7).


2.41.0 (2015-03-23)
-------------------

- Add ``suppress_errors`` parameter to ``IReference.create`` (VIV-629).

- Apply timeout to series source caching (BUG-218).

- Hide date_print_published field from form (ZON-1280).


2.40.1 (2015-03-20)
-------------------

- Integrate werkzeug debugger.

- Bugfix: Don't break when adding more entries to an already full Feed.


2.40.0 (2015-03-17)
-------------------

- Add ``suppress_errors`` parameter to ``IReference.update_metadata`` (VIV-629).


2.39.0 (2015-03-13)
-------------------

- Distinguish between sucessful and failed drag&drop operations (DEV-60).

- Sort serie values properly (BUG-215).


2.38.2 (2015-03-10)
-------------------

- Reorganize series source into dictionary structure for performance (BUG-214).

- Fix serializing Serie objects to XML (ZON-1464).


2.41.0 (2015-03-23)
-------------------

- Add ``suppress_errors`` parameter to ``IReference.create`` (VIV-629).

- Apply timeout to series source caching (BUG-218).

- Hide date_print_published field from form (ZON-1280).


2.40.1 (2015-03-20)
-------------------

- Integrate werkzeug debugger.

- Bugfix: Don't break when adding more entries to an already full Feed.


2.40.0 (2015-03-17)
-------------------

- Add ``suppress_errors`` parameter to ``IReference.update_metadata`` (VIV-629).


2.39.0 (2015-03-13)
-------------------

- Distinguish between sucessful and failed drag&drop operations (DEV-60).

- Sort serie values properly (BUG-215).


2.38.2 (2015-03-10)
-------------------

- Reorganize series source into dictionary structure for performance (BUG-214).

- Fix serializing Serie objects to XML (ZON-1464).


2.38.1 (2015-03-04)
-------------------

- Fix security declaration for Serie objects (ZON-1464).

- Fix search button styling (DEV-23).


2.38.0 (2015-03-03)
-------------------

- Expand series source to include more attributes (ZON-1464).

- Introduce ``zeit.cms.content.reference.SingleResource``.

- Gracefully handle unresolveable interfaces for source availability (ZON-1466).

- Change ``lead_candidate`` default to true (DEV-662).


2.37.1 (2015-02-19)
-------------------

- Extend product class to include more attributes (ZON-1280).


2.37.0 (2015-02-19)
-------------------

- Add ``date_print_published`` to ``IPublishInfo`` (ZON-1280).

- Re-implement filename normalization algorithm in Python (DEV-567).


2.36.0 (2015-02-17)
-------------------

- Add safetybelt so we don't put non-wellformed XML into DAV (BUG-194).


2.35.1 (2015-01-29)
-------------------

- Disable ``XMLSnippet`` for the time being, the widget is not smart enough.


2.35.0 (2015-01-21)
-------------------

- Re-introduce ``XMLSnippet`` (had been removed in 2.0).

- Allow ``p`` and ``span`` tags and ``style`` attributes in XMLSnippet
  (VIV-648).


2.34.0 (2015-01-12)
-------------------

- Set ``publishing`` attribute for checkout events, too, not just checkin.

- Log semantic change status during checkin.


2.33.0 (2015-01-08)
-------------------

- Fix test setup (clearing localStorage) to work with Webdriver (VIV-266).


2.32.0 (2014-12-17)
-------------------

- Update tests since mock connector now yields trailing slashes for folder ids
  (FRIED-37).


2.31.0 (2014-12-17)
-------------------

- Introduce parameter ``suppress_errors`` for XMLReferenceUpdater (VIV-629).

- The Exception view now returns the error as text/plain for XHR requests.

- Provide helper object for invalidations. (VIV-618)


2.30.0 (2014-11-14)
-------------------

- Log stack trace of JavaScript errors.

- Introduce ``zeit.cms.content.dav.findProperty``.

- Pass draggable to ``before-content-drag`` event (VIV-405).

- Sort add menu items alphabetically.

- Add readonly permission ``zeit.content.cp.ViewAutomatic`` (VIV-525).

- Use same hooks to apply changes for EditForm and InlineForm by removing
  custom hook in EditForm. (VIV-516).

- Add extra layer to the request, to distinguish between workingcopy and
  repository views during registration. (VIV-496)


2.29.0 (2014-10-21)
-------------------

- Register moved objects with external redirector service, adjust references to
  moved objects (WEB-298).

- Add ``push_news`` flag to ICommonMetadata (VIV-526).

- Fix bug, so more than one excessive Ghost can be removed.


2.28.0 (2014-10-07)
-------------------

- Introduce permission ``zeit.content.cp.EditAutomatic`` (VIV-525).

- Fix submitting SubPageForms (VIV-488).

- Update dependency to ZODB-4.0.


2.27.3 (2014-10-02)
-------------------

- Edit MANIFEST.in.


2.27.2 (2014-10-02)
-------------------

- Add MANIFEST.in.


2.27.1 (2014-10-02)
-------------------

- Option to identify new (zeit.frontend) content from XSLT content


2.27.0 (2014-09-18)
-------------------

- Redirect to renamed object instead of its parent folder (VIV-487).

- Offer both checkin and checkin/correction on conflict warning dialog
  (VIV-485).

- Store timestamp of last checkout.

- Improve clickable area for object details preview links (VIV-492).

- Improve wording for "delete workingcopy" (VIV-483).

- Move retract menu item to secondary actions menu (VIV-499).

- Introduce special permissions for delete and retract of centerpages (VIV-496).


2.26.2 (2014-09-03)
-------------------

- Use feature toggle ``zeit.content.cp.automatic``.


2.26.1 (2014-08-29)
-------------------

- Fix brown-bag release.


2.26.0 (2014-08-28)
-------------------

- Add channels to ICommonMetadata (VIV-469).

- Filename rewriting: Remove all dots except for those of explicitly
  whitelisted filename extensions (VIV-463).

- When resolving "WC or CMS" content, ignore the workingcopy part if there is
  no interaction.

- Fix bug in publish/retract dialog: use the correct context when the dialog is
  opened from a folder view (VIV-452).


2.25.0 (2014-07-17)
-------------------

- Enable rewriting filenames for all content types; keep filename extenions
  intact (moved from zeit.content.article) (VIV-409).

- Move JS character counter from zeit.content.article here.

- Support non-<form> containers for SubPageForm/InlineForm,
  since nested <form>-tags are not valid HTML (VIV-428).


2.24.0 (2014-07-02)
-------------------

- Internal: add ``run_js`` method for selenium tests.


2.23.1 (2014-06-20)
-------------------

- Enable translating menu item titles (VIV-361).


2.23.0 (2014-06-20)
-------------------

- Include "Select2" jQuery plugin for nicer select widgets (VIV-389).

- Fix "retract" icon (VIV-361).

Internal:

- Make context of publish worklist configurable.
- Make current LightboxForm available as ``zeit.cms.current_lightbox``.
- Move RemoteTaskHelper to zeit.workflow.testing so it's reusable.


2.22.0 (2014-06-16)
-------------------

- Populate ``author`` attribute of references with author objects instead of
  freetext authors (VIV-410).


2.21.0 (2014-06-06)
-------------------

- Allow overriding name of ZCMLLayer.


2.20.0 (2014-06-05)
-------------------

- Fix icon sprite (VIV-407).

- Complete switching of ZCMLLayer to plone.testing.


2.19.0 (2014-06-03)
-------------------

- Switch ZCMLLayer to plone.testing.

- Add ``serie`` attribute to XML references (VIV-383).

- Fix styling of fields with errors (VIV-25).

- Remove ``teaser_supertitle`` from XML references (TT-511).


2.18.0 (2014-05-09)
-------------------

- Add field ``seo_optimized`` to IContentWorkflow (VIV-329).

- Move CharlimitMixin from zeit.content.article to zeit.cms.browser.form.

- Allow registering additional entries as addable content (VIV-367).


2.17.0 (2014-04-22)
-------------------

- Add interface for current topics (VIV-359).

- Removed unused interface.


2.16.1 (2014-03-28)
-------------------

- Update jqueryui from 1.9 to 1.10, use js.jqueryui instead of vendoring our
  own copy, since the colorpicker widget depends on that version.


2.16.0 (2014-03-24)
-------------------

- Add colorpicker widget.


2.15.3 (2014-03-18)
-------------------

- Add diagnostics for XMLReferenceUpdater so we can pinpoint errors more easily


2.15.2 (2014-03-17)
-------------------

- Fix bug in SingleReferenceProperty that deleted the value when setting the
  same value again (VIV-305).


2.15.1 (2014-03-14)
-------------------

- Fix broken split of SubpageForm/InlineForm JS code: InlineForms do need
  reload() functionality (VIV-285).

- Fix XML structure of image references (VIV-305).

- Fix bug in determining the correct XML node for SingleReferenceProperty.


2.15.0 (2014-03-10)
-------------------

- Add ``uniqueId`` attribute to feed items which means "referenced uniqueId",
  so that ``href`` now means "final resolved uniqueId", which XSLT needs
  (VIV-322).

- Write teaserSupertitle into separate XML tag (VIV-106).

- Write breadcrumb_title into XML references for ICommonMetadata (VIV-324).

- Add ``SingleReferenceProperty`` for single-valued references (VIV-305).

- Extract zeit.content.image and zeit.content.link into their own eggs.

- Internal: Use py.test runner.

- Internal: Split off InlineForm (that does auto-save) from SubPageForm
  (VIV-285, RED-1596).


2.14.1 (2014-02-12)
-------------------

- Fix styling of folder table filter widget.


2.14.0 (2014-02-10)
-------------------

- Use Fanstatic instead of zc.resourcelibrary (VIV-296).

- Use WSGI pipeline instead of zope.server (VIV-295).

- Fix handling of 'related' references to image groups (VIV-306).

- Prevent adding the same reference target twice (VIV-309).


2.13.1 (2014-01-22)
-------------------

- Allow referencing the same object several times for MultiResource (VIV-282).


2.13.0 (2014-01-20)
-------------------

- ICommonMetadata now uses reference objects for authors (VIV-273).

- Add ``ReferenceProperty`` for qualified references between content objects,
  and corresponding ``ReferenceSequenceWidget`` (VIV-274, VIV-276).

- Add autocompleteable source for locations (VIV-275).

- Add DAV property ``deeplink_url`` to ICommonMetadata (VIV-270).

internal:

- RelatedBase is now based on MultiResource (VIV-282).


2.12.0 (2014-01-07)
-------------------

- Introduce ISection, which means that all content objects below a folder are
  marked with specific marker interfaces, so they can have their behaviour/UI
  tailored specifically (VIV-252).

- XMLSource checks whether each value is available for the context via an
  optional interface given in the ``available`` attribute (VIV-252).

- Add ``url_value`` to Tag objects (for zeit.frontend).

internal:

- Remove old mechanism for registering content types (content<-->resource
  adapteres), only TypeDeclaration is supported now (set register_as_type=False
  if a type should not show up in the UI).

- Remove IPreviewURL adapter from uniqueId. This was only used by zeit.find and
  we have a better solution there now: use the @@redirect_to view. (VIV-251)

- Generalize MasterSlaveSource from SubNavigationSource (for VIV-241).

- Add ConvertingRestructuredTextWidget (for VIV-245).


2.11.0 (2013-11-25)
-------------------

- Make grouped form macros available for SubPageForms.


2.10.0 (2013-11-15)
-------------------

- Fix bug that prevented renaming containers, e.g. ImageGroup, Folder (VIV-174).


2.9.0 (2013-10-11)
------------------

- Fix css field offsets to fix layout of topic links (VIV-153)


2.8.0 (2013-10-02)
------------------

- Support webdriver alongside seleniumrc for tests (#12573).

- Update to lxml-3.x (#11611).

- Remove temporary thumbnail files directly after the request ends (#12879).


2.7.0 (2013-09-24)
------------------

- Support rel="nofollow" on Link and Image objects (VIV-104).

- Add DAV property ``breadcrumb_title`` to ICommonMetadata (VIV-105).

- Validate type of object when entering an URL to ObjectSequenceWidget (#12790).

- Validate filename of new articles to prevent using an already existing name
  (#12759).

- Fix CSS to avoid cutting off content that should scroll (VIV-108).

- Reset workflow status for copied objects (#12554).

- Use checkbox instead of prefix selection for mobile alternative widget
  (VIV-103).

- Silence superfluous JS alert regarding logging (#12757).

- Add public ``ping`` view that monitoring checks can use (#12851).

- Remove unittest2, we have 2.7 now


2.6.2 (2013-09-06)
------------------

- Fix default for DailyNL (should be True), that was changed accidentally in
  2.6.0.


2.6.1 (2013-09-05)
------------------

- Revert ill-conceived ICommonMetadata default value change from 2.6.0: if a
  document has no value for a property, we should not pretend it does (#12556).

- Add specialized widget for ``mobile_alternative`` that offers easy access to
  some default URLs (#12749).


2.6.0 (2013-08-27)
------------------

- Introduce synchronous publish mode (``async`` parameter for
  IPublish.publish() and retract) (#12685).

- Use interface default values for most boolean properties of ICommonMetadata
  when the content object has no values (#12556).

- Add DAV property ``mobile_alternative`` to ICommonMetadata (#12749).

- Handle non-ASCII uniqueIds in the repository tree display.

- Respect filename constraints when renaming (#12758).


2.5.0 (2013-08-14)
------------------

- Update to Python-2.7 and ZTK-1.1.5 (#11005).


2.4.0 (2013-08-13)
------------------

- Disable checkin validation during publishing (#12690).
- Fix styling for publish indicator so it's visible outside of object-details
  again (#12691).


2.3.0 (2013-08-05)
------------------

- Add authors to blocks in centerpage xml (#12695).


2.2.8 (2013-07-11)
------------------

- Make keywords optional for the time being.


2.2.7 (2013-07-10)
------------------

- Stopgap: accept any tags, even when they are not in the whitelist (#12609).


2.2.6 (2013-07-10)
------------------

- Require at least three keywords, not just one.


2.2.5 (2013-07-08)
------------------

- Log JavaScript errors to the server error log. (#12417)
- Trigger change after "generate keywords" (so error messages are cleared
  immediately) (#12521).


2.2.4 (2013-07-05)
------------------

- Add keywords from whitelist to the start of the list, not the end.


2.2.3 (2013-07-04)
------------------

- Drop duplicate keywords.


2.2.2 (2013-07-03)
------------------

- Support jsuri in tests. (#12557)

- `zeit.cms.view` renders error message if XHR request failed. (#12530)


2.2.1 (2013-07-02)
------------------

- Improve icons for pinned keywords.


2.2.0 (2013-07-01)
------------------

- Support adding keywords from the whitelist with an autocomplete widget
  (#11421).

- Support pinning keywords (#12521).

- Require at least one keyword to be entered as the default for any content
  type, make this configurable by content type (#12478).

- Set character limit for title and subtitle metadata (instead of validating
  them on check-in) (#12462).

- Autocomplete keywords on any substring, not just on prefix (#12519).

- Support entity type in keyword whitelist (#12520).


2.1.1 (2013-05-16)
------------------

- Display last semantic change in object details heading, not an artificial
  "created date" (#12368).


2.1 (2013-04-23)
----------------

- Removed package dependencies that have become unused.


2.0 (2013-04-23)
----------------

- Add type identifier to blocks in centerpage xml. (#12269)

- When parsing html to xml, ``objectify_soup_fromstring`` fixes  HTML5 boolean
  attributes and HTML entities so they are XML compatible (#12267).

- Fix generating of tags (#12254)

- Fix autosaving of forms when user clicks on a DOM node inside the form
  container (#12211).

- Fix selecting of objects in reference dialog (#12102)

- Publish is not allowed in ILocalContent via the security machinery now (for
  #8413).

- Improved ObjectSequenceWidget so it became usable again.

- Added in-place add functionality to ObjectSequenceWidget (#8402).

- Included JQuery as well as MochiKit for the best of both worlds.

- Added a DAVConverterWrapper for XML properties to make it easy to use the
  DAV converter infrastructure with XML properties.

- Testing: HTTPLayer calls tearDown on the request handler during testTearDown
  now.

- ObjectSequenceWidget and DropObjectWidget don't accept any draggable anymore,
  they offer a parameter to configure the accept setting instead. Clipboard and
  zeit.find annotate their draggables with the content types (#9390).

- Introduce ValidateCheckinEvent (#9406).

- Introduce ICheckinCheckoutEvent.publishing (for #8996).

- Changed zeit.cms.browser.form.apply_default_values to not overwrite an
  objects's existing data attributes.

- DropObjectWidget raises ValidationError when the given uniqueId does not
  exist in the repository.

- In the ObjectSequenceWidget, placed the search field and add button above
  the list of sequence items (#10666).

- Introduce RestructuredTextWidget (#10661).

- Introduce IPublishInfo.date_last_published_semantic (#10704).

- Introduce zeit.workflow.publishinfo.PublishInfo as base class for workflows
  instead of NotPublishablePublishInfo (#10739).

- Remove XMLSnippet, its functionality is not used anymore.

- We need to use @@raw view to get the actual URL of images (#12159)


1.55.0 (2012-12-17)
-------------------

- Don't consider ``refined`` and ``images_added`` as a precondition for
  publishing (#11717).

- Fix image group type to ignore master image (#11116).

- Added a teaser kicker field to the common metadata.



1.54.0 (2012-07-13)
-------------------

- Fold IContentAdder and IAddLocation into zeit.cms from zeit.addcentral
  (for #10692).

- Added a teaser kicker field to the common metadata (#11460).


1.53.4 (2012-03-15)
-------------------

- Fixed the fixed isolation of ``product_config`` between tests.

- When the enhanced breadcrumbs (#10151) are disabled, the path to the
  workingcopy is shown again, instead of always showing the path to the
  repository object.


1.53.3 (2012-03-14)
-------------------

- The enhanced breadcrumbs (#10151) are configurable now via the product-config
  option ``breadcrumbs-use-common-metadata`` (true or false).

- Fixed isolation of ``product_config`` between tests.


1.53.2 (2012-03-06)
-------------------

- Backout changeset:89a6328dd4d0: This changeset was grafted from editor-ng but
  does not work on default as it changes publication security. The change
  prevents quick publish in zeit.content.cp then.



1.53.1 (2012-03-06)
-------------------

- Testing expected ``/bin/true`` to exist which is not the case on all systems.
  Just using ``true`` now, expecting true to be somewhere in the path.


1.53.0 (2012-03-06)
-------------------
- Added metadata checkbox show commentthread (zeit-mantis 3664)

- Limit the amount of PubliationDependencies that are actually published;
  configurable as product config of zeit.workflow: ``dependency-publish-limit``
  (#10242).

- Use gocept.testing.

- For an article, include ressort and sub-ressort in the breadcrumbs instead
  of the repository path. (#10151)

- Restructured test layer and test cases so as to have a more reliable
  tear-down. (#10456)

- Added helpers for selenium tests: eval JS and wait for conditions in the
  current window. Also use gocept.zcapatch to register temporary views etc.


1.52.0 (2011-12-08)
-------------------

- Add handler that updates XMLReferences for MultiResources on checkin
  (for #10042).


1.51.0 (2011-12-01)
-------------------

- Provide another Remotetask-Service, "low-priority", that handles publish
  tasks serially (#10024).


1.50.2 (2011-11-24)
-------------------

- Make link an IXMLContent. It is expected from content to implement
  ICMSContent (which is implied in IXMLContent). (#10017)


1.50.1 (2011-11-13)
-------------------

- Fix brown bag release 1.50.0


1.50.0 (2011-11-13)
-------------------

- Backported test helpers and fixes from the editor-ng branch to the main
  development line.


1.49.1 (2011-06-21)
-------------------

- Fix product source so it works in the face of SecurityProxies (#9231).

- Introduce ICheckinCheckoutEvent.publishing (for #8996).


1.49.0 (2011-06-20)
-------------------

- Add SourceFactory helper for sources with a small set of fixed values (for
  #8953).

- Change ICommonMetadata.product_id to be a product object with id, title and
  VGWort-Code (for #9033).

1.48.0 (2011-03-23)
-------------------

- Generalised how checkout/checkin works so it also works for non-dav content
  (for #7826)

- Added IDAVContent for content from the original repository. This is to
  separate it from content from other repositories (like brightcove) (for
  #7826).

- Made locking support optional (for #7826)

- A view on workingcopy objects used to lookup objects directly in the
  repository. Replaced this by an ICMSContent() adapter lookup (for #7826)

- Improve HTTP test layer: stores errors in a list instead of printing them
  (for #8085).


1.47.0 (2010-08-16)
-------------------

- Add detail url to access counter (#7860).



1.46.0 (2010-08-09)
-------------------

- Make sure indexing referencing object doesn't break when there is change in
  the list duinng iteration (#7635).
- Use gocept.selenium to run selenium tests (#7549).
- Remove the automatic syndication of articles with serie 'News' to a news
  channel.


1.45.0 (2010-07-07)
-------------------

- Fix test isolation problem (#7467).
- Removed assignment of UUIDs, this is handled by the DAV-Server now (#7366).
- Added trackeback info to publish/rectract tasks (#7443).
- Show UUID when there are duplication errors (#7247).
- Allow "checkin" for ghosts (#7152).
- Preview URLs are now determined using an adapter (#7030).
- Added a Nagios checkable view for the length of the publish task queue
  (#6801).
- Update relation index not only on checkin but also on add (#6415).
- Enable flashmessages to be updated via javascript (#6415).
- checkout.helper supports ignoring conflicts now (#7587).
- Avoid race-condition during publish: don't check if we can checkout/checkin,
  but try to checkout/checkin and catch errors. (#7586).


1.44.0 (2010-06-09)
-------------------

- Live-Propertys nur setzen, wenn sich der Wert geändert hat (#7392).
- CAP-Kontext wieder entfernt (#7365).
- Bilddatei ist beim Anlegen jetzt obligatorisch, beim Editieren nicht (#7253).
- Obskurer Clipboard/Ghost-Fehler behoben (#6631).
- Neues Tab 'References', in dem die Objekte aufgelistet werden, von denen ein
  Objekt referenziert wird (#6160).
- Fehler beim Feed-Update mit FakeEntry behoben (#7391).
- Sortieren einer Bildergruppe nach Dateiname repariert (#7087).
- Autoren sind nicht mehr Freitext, sondern CMS-Objekte (#7333).
- SingleResource erlaubt Löschen (#5010).


1.43.0 (2010-06-02)
-------------------

- Retrieving None from XML now yields None, not the unicode string u'None'
  (#7360).

- Copyrights-field from CommonMetadata is now optional

- Copyrights moved to "navigation" in metadata form.

- ``product_id`` moved to "head" in metadata form.


1.42.0 (2010-05-17)
-------------------

- DAV-Properties from the "INTERNAL" namespace are no longer copied to XML
  (#7151).

- Last-Semantic-Change is now determined by the last save of the workingcopy.
  Before it was determined by the time of the checkin which lead to superfluous
  conflict errors (#7151).

- Generalised the way to control which dav properties are copied to XML
  (#7213).


1.41.4 (2010-04-14)
-------------------

- Provide useful error message in the ``redirect_to`` view when the object
  doesn't exist (#6998).

- When trying to view the thumbnail of an empty image group a 404 is returned
  instead of 500 (#6998).

1.41.3 (2010-04-14)
-------------------

- Prefer ``log.error(..., exc_info=True)`` over ``log.exception(...)``.


1.41.2 (2010-04-09)
-------------------

- Using ICMSContet adapter instead of direct repository access in most places
  to support multiple repositories (i.e. videos).


1.41.1 (2010-03-31)
-------------------

- PURGE für HTTP-Cache-Server (#6969).

- Using versions from the ZTK.

- Improved test infrastructure.

- "Trotzdem einchecken" honoriert nicht "als korrektur einchecken"  (#6880)


1.41.0 (2010-03-10)
-------------------

- Fix that text fields which are mapped to xml nodes still work even when there
  is no py:pytype and the contents is an integer (#6824).

- Change the way asset interfaces are registered. This fixes isolation problems
  during tests (#6712).

- Checkin-Conflict-Resolver wird mit HTTP-Status 200 ausgeliefert, statt bisher
  500 (#6392).

- Checkin-Conflict-Resolver checkt jetzt auch Korrekturen korrekt ein (#6880).

- Die Felder CAP-Kontext und CAP-Titel auf allen Objekten mit Standardmetadaten
  verfügbar gemacht (#6923).

- Kein ``alert()`` mehr bei Nicht-Firefox-Browsern (#6935).

- Relaunch-Preview-Icon an- und abschaltbar (#6878).

- Syndication-Tab und dezentrale Syndizierung an- und abschaltbar (#6878).

- Alte CenterPage komplett entfernt (#6878).

- Channel sind keine vollwertigen Inhaltstypen mehr, wenn das dezentrale
  Syndizieren ausgeschaltet ist (#6878).

- Metadatum "Sub-Typ" entfernt (#6114).

1.40.3 (2010-02-23)
-------------------

- Site settings' working directory creator ignores empty path elements
  correctly now.


1.40.2 (2010-01-16)
-------------------

- ITZInfo-Adapter für alle Requests registriert, nicht nur für BrowserRequest.


1.40.1 (2010-01-16)
-------------------

- Index-Updater ``load_references`` repariert (no interaction, #6713).

- Security-Problem bei Bild-XMLReferenz behoben.

1.40.0 (2009-12-18)
-------------------

- Favicon aktualisiert.
- Wenn im XML für die Keywords ein Fehler ist, wird das Laden abgebrochen und
  die alte Fassung behalten (#6046).
- Last-semantic-change wird direkt beim Anlegen eines Objektes gestzt, nicht
  erst beim Einchecken (#6476).
- Neue Option »Schlagzeile«.
- Bilder, die aus Bildergruppen kommen, übernehmen die expires-Einstellung der
  Gruppe (#6662).
- Ressort wird in die XML-Referenz (z. B. in Feeds) übernommen (#6650).

Technische Änderungen
+++++++++++++++++++++

- Relationen zwischen Content-Objekten werden über einen allgemeinen Index
  abgebildet, nicht mehr einzelne (related, syndicated, image) (#6300).

1.39.3 (2009-11-25)
-------------------

Technische Änderungen
+++++++++++++++++++++

- Fehlertolerante Funktion zum XML parsen: objectify_soup_fromstring.
- Das XMLTree-Feld hat einen optionalen Parameter tidy_input, mit dem es
  kaputtes Markup per BeautifulSoup repariert.

1.39.2 (2009-11-06)
-------------------

- Daten an das Veröffentlichungsscript werden nicht mehr per STDIN übermittelt
  sondern per Datei und Argument.


1.39.1 (2009-11-04)
-------------------

Technische Änderungen
+++++++++++++++++++++

- Ermöglicht zusätzliche Drop-Query-Argumente bei
  ``createDraggableContentObject`` anzugeben.


1.39.0 (2009-11-02)
-------------------

Technische Änderungen
+++++++++++++++++++++

- `ICMSContent` adapter flexibilisiert um per Scheme und/oder Netloc
  verschiedene Repositorys ansprechen zu können (#6385).

- UUIDs werden bereits beim erzeugen (ObjectCreatedEvent) vergeben (#6385).

- UUIDs werden bereits beim kopieren neu vergeben (nur auf dem direkt kopierten
  Objekt, #6385)

- Adaptieren eines Objekts auf ITypeDeclaration (#6385).


1.38.1 (2009-10-26)
-------------------

- Asset-Badges werden jetzt zuverlässig gespeichert (#6165).


1.38.0 (2009-10-19)
-------------------

- Site-Steuerung ist jetzt ein Dropdown (#6350).

- Die alte Suche (zeit.search) wurde entfernt.

- Extra Permission für den Repository-Navigationsbaum (#6165).

1.37.1 (2009-10-12)
-------------------

- Preview-Redirect ist jetzt trusted.


1.37.0 (2009-10-12)
-------------------

- Art und Weise geändert wie Einträge aus Channeln entfernt werden (#6200).

- Objekte erhalten jetzt direkt beim Hinzufügen eine UUID und nicht erst beim
  Einchecken (#6295).


1.36.1 (2009-10-05)
-------------------

- ObjectAddedEvent wird jetzt nur noch gesendet, wenn ein Objekt auch wirklich
  dem Repository hinzugefügt wird.


1.36 (2009-10-02)
-----------------

- Bildergruppen haben jetzt ein Thumbnail.

- Veröffentlichen hat jetzt immer ein Ergebnis; vorher konnte es vorkommen,
  dass der Prozess keine Abbruchmeldung geschrieben hat.


1.35.1 (2009-09-29)
-------------------

- Persistente Thumbnails können wieder angelegt werden (schlug fehl mit
  Conflict / PreconditionFailed).


1.35 (2009-09-28)
-----------------

- Konflikte beim Einchecken werden erkannt und können umgangen werden.

- Löschen aus der Arbeitskopie wird jetzt gesondert behandelt, so dass
  verständlicher ist, was passiert.

1.34.2 (2009-09-22)
-------------------

- Invalidieren der Resourcen vor dem Veröffentlichen um der Locking-Errors Herr
  zu werden.


1.34.1 (2009-09-21)
-------------------

- Site-Steuerung geht zum richtigen Link (@@view.html).


1.34 (2009-09-21)
-----------------

- Site-Steuerung checkt nicht mehr aus.

- Workflow sperrt, wenn möglich, alle benötigten Resourcen vor dem
  Veröffentlichen.


1.33.3 (2009-09-16)
-------------------

- Der Workflow loggt wofür Zeit verbraucht wird. Ziel ist das Veröffentlichen
  zu beschleunigen.


1.33.2 (2009-09-14)
-------------------

- UUID-Lookup ist robuster gegen nicht vorhandene Objekte (#5734).


1.33.1 (2009-09-11)
-------------------

- Date-Last-Modified, Last-Semantic-Change, Date-First-Released und
  Date-Last-Published zur XML-Referenz wieder entfernt. Dies wird explizit in
  CPs eingebaut.


1.33 (2009-09-09)
-----------------

- Zurückziehen zieht abhängige Objekte nicht mehr mit zurück.

- Publish- und RetractEvents haben jetzt Informationen über das Objekt, das der
  Benutzer veröffentlichen/zurückziehen wollte.


1.32.1 (2009-09-06)
-------------------

- ObjectPathAttributeProperty kann jetzt ``None`` speichern, ohne "None" als
  Text zu produzieren.


1.32 (2009-09-05)
-----------------

- Site-Steuerung vor Dateiverwaltung (#6159).

- Kurz-Teaser und Homepage-Teaser gibt es nicht mehr (#6161).

- XMLReferenzen beinhalten keine Relateds mehr.

1.31.2 (2009-08-31)
-------------------

- Bessere Fehlerbeschreibung, wenn Bildergruppen referenziert werden, die
  plötzlich keine Bildergruppen mehr sind (#6137).


1.31.1 (2009-08-31)
-------------------

- Metadaten von Bildern in den bearbeiteten Dokumenten gehen nicht mehr kaputt,
  wenn das Bild gelöscht wurde (#6132).


1.31 (2009-08-27)
-----------------

- Neues Feld »Banner-Id« (#6088).

- Neue Optionen »Content« und »Countings« (#6104).


1.30 (2009-08-26)
-----------------

- XML-RPC-Methode ``retract`` um veröffentlichte Inhalte zurückzuziehen
  (#6071).

- »Erstes Related als Box« versteckt (nur Vivi-Skin, #6076).

- Bilder innerhalb von Bildergruppen „erben“ die Metadaten der Bildergruppe,
  bis die Metadaten des Bildes bearbeitet wurden, bzw. das Bild eingecheckt
  wurde (#6073).

- Neue Optionen »Einklappbar« und »Minimalheader« (#6015).

- Neue Felder »Farbwelt« und »Sub-Typ« (#6070).

- Im Ressort-Baum wird die Homepage jetzt explizit angezeigt (#6072).

Technisches
+++++++++++

- Funktion zum Bestimmen der automatischen Veöffentlichungsfähigkeit eines
  Objekts (für #6057) extrahiert.

- Test-Hilfs-Methoden aus zeit.content.cp verschoben.

- `get_working_directory` kann zusätzliche Ersetzungen vornehmen (für #6045).

1.29 (2009-08-21)
-----------------

- Ressort-Baum hinzugefügt, von dem aus die Index-Seiten der Ressorts
  (CenterPages) direkt bearbeitet werden können (nur Vivi-Skin, #5548).

Technisches
+++++++++++

- MasterSlaveDropDown kommt mit verschiedenen Form-Prefixes klar (für #6016).

- Warnung bei parallelem Veröffentlichen wird korrekt ausgegeben (#6030).

1.28.4 (2009-08-19)
-------------------

- Related-Updater aktualisiert nur noch eine Ebene um »maximum recursion depth
  exceeded« zu verhindern (#6026).


1.28.3 (2009-08-18)
-------------------

- Kompatibilität zu Python 2.6


1.28.2 (2009-08-18)
-------------------

- Asset-Badges im CMS-Skin versteckt.


1.28.1 (2009-08-17)
-------------------

- XML-RPC für Workflow gibt bei publish und retract die Job-Id zurück
  (für #5661).

- SubPageForm sended after-reload auch beim Form-Post.

- JSON-Views für publish und um den Status von Jobs abzufragen hinzugefügt
  (#5661).

1.28 (2009-08-14)
-----------------

- Schönere Anzeige von Checkboxen (CMS-Skin und Vivi-Skin).

- Date-Last-Modified, Last-Semantic-Change, Date-First-Released und
  Date-Last-Published zur XML-Referenz hinzugefügt (#5965).

Technisches
+++++++++++

- AddableCMSContentTypeSource hinzugefügt (#5937).

- checkout/checkin-View neuer Parameter redirect=False für JavaScript (#5661).

1.27 (2009-08-10)
-----------------

- Markierungen für Inline-Assets (#5770).

- WebDAV-Metadaten werden in das XML des Link-Objekts kopiert (#5904).

- »Banner« in die Standardmetadaten (bisher nur bei Artikel, #5931).

- Schönere Anzeige für Checkboxen in Metadaten (Vivi).

- Panels in der Sidebar werden wieder vollständig angeeigt (Vivi, #5840).

Technisches
+++++++++++

- Basisklasse für Adapter, die WebDAVPropertys brauchen.

- SubPageForm wurde von LightboxForm abgespalten (für #5937).

- Die TypeDeclaration enthält den Namen des Add-Forms (für #5937).

1.26.1 (2009-08-04)
-------------------

- DragAndDrop im Clipboard funktioniert wieder.

- Objektauswahl-Lightbox funktioniert wieder.

1.26 (2009-08-03)
-----------------

- Neues Feld »Product-Id« in den Standardmetadaten (#5819).

- printRessort als CommonMetadata hinzugefügt.

1.25 (2009-07-28)
-----------------

- Es ist jetzt nicht mehr möglich, dass das CMS das selbe Objekte zwei mal
  gleichzeitig veröffentlicht. Verschiedene Objekte werden weiterhin parallel
  veröffentlicht (#5579).

Technisches
+++++++++++

- JSONView verwendet busy-CSS-Klasse statt den Text "Loading"

- JSONView gibt JSON in den Deferreds als Ergebnis aus.

- Objectify-Bäume werden nur noch einmal pro Transaktion geladen.

- CMSContentSource gibt Auskunft über beinhaltete Content-Typen.

1.24 (2009-07-22)
-----------------

- SubRessort wird immer umgeschrieben, auch wenn es vorher einen ungültigen
  Wert hatte (#5431)

- Ungültige Ressorts und Unterressorts werden jetzt im CMS angezeigt (via
  #5431).

- Navigationsbaum wird asynchron geladen und zwischengespeichert. Dies sollte
  die Ladezeiten deutlich verbessern.

Technisches
+++++++++++

- ObjektReferenceWidget umgebaut damit die Suche integriert werden kann.

- Unterstüzung für `_p_changed` auf XML-Klassen.

- Icons werden mit vollem Pfad eingebunden (#5657).

- DragAndDrop-Panes werden anders zusammen gebaut.

- ObjectWidgets kompatibel zum Verwenden in einer Lightbox gemacht
  (deregistrieren von Events, etc.)

- ObjectWidget öffnet den Browser nur, wenn noch keiner auf der Seite vorhanden
  ist (relevant für CP-Editor).

1.23.2 (2009-06-18)
-------------------

- Repackaged 1.23.1 (setupools/svn 1.6 problem).

1.23.1 (2009-06-18)
-------------------

- Test-Skin repariert

- Tab-Resource-Library repariert

- ObjectPathAttributeProperty kann jetzt auch mit ContextualSources umgehen.

1.23 (2009-06-17)
-----------------

- Anfänge eines neuen Skins: Vivi. Tabs sehen schon besser aus.

- DragAndDrop: Wird ein Objekt gezogen gibt es keine besondere »Drag-Pane«
  mehr. Das gezogene Element wird direkt angezeigt.

- Beim Veröffentlichen »oldstatus« nur setzen, wenn sich der Wert auch geändert
  hat.

- Sidebar ein/ausklappen mit expliziter Statusangabe anstatt mit umschalten
  (damit der CP-Editor es vernünftig einklappen kann).

- Statische Resourcen mit einem Hash in der URL versehen.

1.22.1 (2009-06-09)
-------------------

- ``with_staement`` wird durch die FunctionalDocFileSuite bereitgestellt.

1.22 (2009-06-08)
-----------------

- WebDAV-Sperren von Hintergrundprozessen dauern nur noch maximal 30 Sekunden.

- Bessere Fehlemeldung, wenn Checkout nicht funktioniert.

1.21.6 (2009-06-08)
-------------------

- Bilder sind wieder IImageTypes

- Logging-Fehler im XMLTypeGrokker behoben.

1.21.5 (2009-06-05)
-------------------

- FunctionalDocFileSuite statt der FunctionalBlobDocFileSuite aus zope.file
  benutzen, was mit ZODB 3.9 möglich wird und anders nicht funktioniert.

- Registrieren von Content-Type via Typdeklaration und Martian statt diverser
  ZCML-Statements.

1.21.4 (2009-05-31)
-------------------

- Fehler beim aktualisieren von Metadaten beim Veröffentlichen behoben.

1.21.3 (2009-05-28)
-------------------

- Cache-Collector lockt nicht mehr bei jedem Request.

- ViewTabs (JS) laden jetzt nur noch bei der ersten Aktivierung den View.

- Methoden in JS-Views geben Deferreds zurück.

- zeit.wysiwyg, zeit.content.infobox, zeit.content.portraitbox und
  zeit.content.gallery in extra eggs verschoben.

1.21.2 (2009-05-27)
-------------------

- Im DAV gespeicherte ``__provides__`` gehen beim Checkout nicht mehr verloren
  (#5402).

1.21.1 (2009-05-26)
-------------------

- ListRepresentation für CommonMetadata hinzugefügt.

- Basisklasse für JSON-Views aus zeit.find in den Kern verschoben.

- JSONTemplate aktualisiert

- Generischer Handler für Links (z.B. tab://foo)

- Glboale TAB-Registry, um Tabs mit ihrer Id finden (und aktivieren) zu können.

1.21 (2009-05-18)
-----------------

- Objekte mit der Serie »News« werden automatisch in den News-Channel
  syndiziert. Der News-Channel wird automatisch veröffentlicht (#5270).

1.20.2 (2009-05-17)
-------------------

- Übersetzung einer Fehlemeldung im Workflow repariert.

1.20.1 (2009-05-17)
-------------------

- Nach dem Umbenennen eines Objekts befindet man sich auf dem Ordner, nicht auf
  dem umbenannten Objekt.

- Hilfsfunktion um beliebigen Ordner in Abhängigkeit von der aktuellen Ausgabe
  zu bekommen um Vorlagen erweitert. Dies ermöglicht z.B.
  'online/$year/$volume/berlin'

1.20 (2009-05-15)
-----------------

- Adapter für den Publikationsstatus (veröffentlich, mit Änderungen, nicht
  veröffentlicht) hinzugefügt (#5320).

- Views zum Umbenennen von Ordnern mit einer extra Permission abgesichert
  (#5319).

- Sichergestellt, dass immer nur genau ein Tooltip angezeigt wird. Tooltips
  werden nicht angezeigt, wenn eine DragAndDrop-Operation durchgeführt wird.

- Die Lightbox registriert den Submit-Eventhandler nur noch genau für die
  Submit-Buttons, nicht für *alle* Buttons.

- Alle `test.py` nach `tests.py` umbenannt.

- Lokalisierung herausgelöst und nach ``zeit.locales`` verschoben. Dort werden
  Übersetzungen mit anderen Paketen zusammengefasst.

- JS Tab- und View-Klassen aus zeit.find extrahiert und generalisiert.

1.19.5 (2009-05-08)
-------------------

- TooltipMangager hinzugefügt, der den Tooltip-Text vom jeweiligen DOM-Element
  holt.

1.19.4 (2009-05-07)
-------------------

- Korrektes Verwenden des DAV-Such-Interfaces (repaiert Adaptieren eines
  UUID-Objektes auf ICMSContent liefert das Objekt zur UUID).

1.19.3 (2009-05-07)
-------------------

- Test-Basisklasse zeit.cms.testing.FunctionalTestCase hinzugefügt.

- Hilfsfunktion um beliebigen Ordner in Abhängigkeit von der aktuellen Ausgabe
  zu bekommen.

- Adaptieren eines UUID-Objektes auf ICMSContent liefert das Objekt zur UUID.

1.19.2 (2009-04-30)
-------------------

- Test-Hilfsfunktionen zeit.cms.testing ``set_site()`` und
  ``create_interaction()`` eingeführt.

- DragAndDrop von Content-Objekten refaktoriert, so dass unterscheidbar ist, ob
  ein Content-Objekt, oder etwas anderes gezogen wird.

1.19.1 (2009-04-29)
-------------------

- DragAndDrop aus Dateilisten und der Suche funktioniert wieder (fixes #5057).

1.19 (2009-04-23)
-----------------

- zeit.today in ein extra Paket verschoben.

- Hilfsfunktion zum korrekten "dragbar" machen von Boxen, die sich auf ein
  Content-Objekt beziehen.

1.18.2 (2009-04-21)
-------------------

- Lightbox verwendet keine DIVs mit id mehr. Dies ermöglicht mehrere Lightboxen
  auf der selben Seite.

1.18.1 (2009-04-17)
-------------------

- UUIDs leben jetzt in ``{http://namespaces.zeit.de/CMS/document}uuid`` und
  haben das Format ``{urn:uuid:3acb7948-9c83-439b-90ce-98426541ca80}``.

1.18 (2009-04-16)
----------------

- Beim öffnen des CMS wird den aktuellen Online-Arbeitsordner weitergeleitet
  (fixes #4995).

- UUIDs aben jetzt »ZEDE-« vorangestellt.


1.17.1 (2009-04-15)
-------------------

- LightboxForm kann neu geladen werden.

1.17 (2009-04-15)
-----------------

- Adapter von UniqueId auf ICMSContent hinzugefügt (fixes #4979).

- Es wird eine eindeutige ID als WebDAV-Property
  ``{http://namespaces.zeit.de/CMS/workflow}id`` geschrieben (fixes #4966).

1.16.5 (2009-04-07)
-------------------

- Drag-Panes refaktoriert, so dass sie schon vor dem Laden der vollständigen
  Pane die UniqueId des gezogenen Objektes kennen. Das erlaubt vor allem
  einfacheres Testen, stabilisiert aber auch das DragAndDrop für Benutzer.

1.16.4 (2009-04-06)
-------------------

- Event-Handler des Lightboxforms deregistrieren, wenn Lightbox geschlossen
  wird.

1.16.3 (2009-04-01)
-------------------

- Korrektes Verwenden der Zeitzone, so dass bei Sommerzeit auch Sommerzeit
  angezeigt wird.

1.16.2 (2009-03-31)
-------------------

- Lightbox flexibilisiert.


1.16.1 (2009-03-23)
-------------------

Technische Änderungen
~~~~~~~~~~~~~~~~~~~~~

- ZMI-Add-Menu und Rotterdam-Skin wieder hinzugefügt.


1.16 (2009-03-23)
-----------------

- Doppelclick in der Clipboard-Liste führt jetzt zum referenzierten Dokument
  (#4456).

Technische Änderungen
~~~~~~~~~~~~~~~~~~~~~

- Stabile Sortierung der abhängigen Objekte im Workflow.

- Hit-Importer sperrt nur noch für max. 10 Sekunden.



1.15.1 (2009-03-06)
-------------------

- Dateibrowser im WYSIWYG-Editor zum einfügen interner Links funktioniert
  wieder.


1.15 (2009-03-06)
-----------------

- Doppelclick auf Checkout (und andere Aktionen) führt die Aktion nur noch
  einmal aus (Bug #4499).

- Verlinkte Bildergruppe ohne Bild führt dazu, dass ein Artikel nicht
  eingecheckt werden kann (Bug #4746).

- Automatisches Veröffentlichen von Relateds, wenn diese veröffentlicht sind
  und keine semantische Änderung haben.

- Besseres Verschieben von Clips und Clipboardeinträgen: Wird etwas auf einen
  Clip gezogen der *geöffnet* ist, wird das gezogene Objekt *in* den Clip
  eingefügt. Ist der Clip *geschlossen* wird das Objekt *hinter* dem Clip
  eingefügt. Die Visualisierung ist entsprechend angepasst. (Bug #4757)

1.14.1 (2009-03-03)
-------------------

- 1.14-Release repariert.

1.14 (2009-03-03)
-----------------

- Entfernen aus Channeln beim Zurückzeiehen funktionierte nicht zuverlässig
  (bug #4722).

- Access Keys für Checkin (^I) und Checkout (^O).

- Property für letzte inhaltliche Änderung, die beim Checkin gesetzt wird. Dies
  kann durch die Aktion »Einchecken (Korrektur)« verhindert werden. (#4720)

1.13 (2009-02-15)
-----------------

- Channel stehen nach dem Syndizieren nicht mehr unter den bearbeiteten
  Dokumenten.
- Neue Aktion beim Syndizieren: »Syndizieren ohne Relateds«.

1.12 (2009-02-11)
-----------------

- Einchecken schneller: Automatisches aktualisieren der Dokumente, die sich auf
  das eingecheckte Dokument beziehen passiert jetzt asynchron.

1.11 (2009-02-09)
-----------------

- WYSIWYG-Editor: Es ist nicht mehr möglich ein Video so einzufügen, dass es
  nach dem Speichern weg ist (Bug #4652).
- WYSIWYG-Editor: Es ist jetzt möglich auch nach der Video-Box Text einzugeben,
  wenn die Video-Box hinten an das Dokument angefügt wird.
- Die Checkbox »Tages-NL« ist jetzt bei neuen Objekten automatisch aktiviert.
- WYSIWYG-Editor: Beim Bearbeiten von Audio/Video steht jetzt »mit Info« statt
  »mit Links« zur Auswahl (Bug #4650).

1.10.2 (2009-02-05)
-------------------

- Selenium-Tests können jetzt die Product-Config setzten.

1.10.1 (2009-02-01)
-------------------

- Selenium-Tests in extra ZCML-File.
- Browsing-Location-View/-Adapter auf IContained registriert.
- Zope-Pakete aktualisiert + abhängige Änderungen
- Lightboxen für Keywords und Kopieren repariert (+Test!)

1.10 (2009-01-31)
-----------------

- Suche: Anzeigen wenn es erweiterte Kriterien gibt, die erweiterte Suche aber
  eingeklappt ist (Bug #4388).
- Suche: Der Dateiname wird jetzt angezeigt (Bug #4440).
- Sperren: Es wird wieder angezeigt wer ein Objekt gesperrt hat.
- Bei ausgecheckten Dokumenten gibt es jetzt eine Aktion um zu dem Original in
  der Dateiverwaltung zu kommen (Bug #4419).
- Anzeige beim Text-Type ist jetzt Preformatted (Bug #4446).

1.9.1 (2009-01-21)
------------------

- Unterstützung von zope.app.renderer 3.5.0
- Checkout gesperrter Objekte konnte zu LockingError führen (Bug #4631).
- Biga Veröffentlichen mit nicht vorhandenem Bilderordner führte zu unklarer
  Fehlermeldung (Bug #4630).

1.9 (2009-01-19)
----------------

- Interface-Deklaration auf Objekten werden im DAV abgelegt und gehen nicht
  mehr verloren.
- Select-Box bei Bildergruppen entfernt.
- Bildergruppen haben ein Master-Bild von dem die Ausschnitte abgeleitet
  werden.

1.8.4 (2009-01-07)
------------------

- Repository funktioniert auch ohne Product-Config.

1.8.3 (2008-12-12)
------------------

- Sperren von nicht vorhandenen Objekten ist nicht mehr möglich. Das sorgt
  dafür, dass der Hit-Importer nicht mehr frei dreht wenn im Cache noch ein
  Objekt vorhanden ist, welches es aber nicht mehr gibt.

1.8.2 (2008-12-10)
------------------

- Kompatibel mit Python 2.5.
- Product-Config vor den Tests leeren.

1.8.1 (2008-12-08)
------------------

- WYSIWYG-Editor: Knopf zum Einfügen von Audio fügt jetzt ein Audio ein und
  nicht ein Video.

1.8 (2008-12-08)
----------------

- Einfügen aus Word in Kombination mit Firefox 3 verbessert (Bug #4529).
- WYSIWYG-Editor: Knopf zum Einfügen von Audio.
- WYSIWYG-Editor: Javascript-Fehler bei Bild-Einfügen entfernt.

1.7.1 (2008-11-27)
------------------

- Bilder können wieder innerhalb von Absätzen erzeugt werden.

1.7 (2008-11-27)
----------------

- Keyword-Suche sucht jetzt auch in Labels. Damit funktionieren auch Umlaute.
  (Bug #4520)
- Keyword-Vorschlags-Mail mit Betreff (Bug #4281).
- Hits-Spalte lässt sich sortieren (Bug #4487).
- Race-Condition beim Abfragen von Objektrelationen behoben: unter bestimmten
  Umständen wurden alle indizierten Objekte zurückgeliefert.
- Beim Hinzufügen von Bildern wird das dort sinnlose »Wird verwendet von« nicht
  mehr angezeigt.

1.6 (2008-11-26)
----------------

- WYSIWYG-Editor: Formular zum Bild-Bearbeiten vereinfacht (Bug #4170).
- WYSIWYG-Editor: Neues Feld »Format« im Video-Dialog.
- WYSIWYG-Editor: Möglichkeit RAW-Tags zu bearbeiten.
- Bei Bildern und Bildergruppen wird angezeig in welchen Objekten sie als Asset
  verwendet werden (Bug #4037).


1.5 (2008-11-20)
----------------

- Sicherheitsrichtlinien (securitypolicy)  ist aus dem Kern in ein separates
  Paket gewandert. Das sorgt für mehr Flexibilität.
- Permission-Deklaration für den Kalender entfernt (Bug #4511).

1.4 (2008-11-18)
----------------

- Bigas: Das Bild linkt jetzt zum Bearbeiten. Zum Bild kommt man mit dem
  Extralink »Bild zeigen«.
- Bigas: Die Bildunterschriften in den <image>- und <thumbnail>-Tags wurden
  auch nach dem »Synchronisieren« nicht aktualisiert. Unberührt bleibt hiervon
  das <caption>-Tag. (Bug #4530)
- Biga: Neues Layout »hidden« für die Bilder. Dies erlaubt das Ausblenden von
  nicht benötigten Bildern.
- Previews von ausgecheckten Dokumenten werden jetzt im Verzeichnis des
  Ursprungsobjekts erzeugt. Damit können contextabhängige Styles angesehen
  werden (v.a. Zuender). (Bug #4311)
- Löschen funktioniert wieder.


1.3 (2008-11-17)
----------------

- WYSIWYG-Editor: Formular für das Hinzufügen und Bearbeiten von Videos;
  unterstützen des <video>-Tags incl. expires-Attribut.
- WYSIWYG-Editor: Aktion für das Hinzufügen eines Mail-Formulars.
- Lightbox-Formulare: Nach dem ersten Submit wurden die Handler nicht
  aufgesetzt, so dass ein zweiter Submit nicht (korrekt) funktionierte.
  Unterstütung für Checkboxen.
- Massenänderung der Copyrights aller Bilder in einem Ordner.
- Bei Verlinkungen (z.B. Assets) wird jetzt ein größerer Tooltip angezeigt
  (bei Bildern auch mit Bild).


1.2.7 (2008-11-10)
------------------

- Übersetzungen korrigiert.

1.2.6 (2008-11-10)
------------------

- Syndizieren mit gleichzeitigem verstecken auf der Homepage (bug #4521).

1.2.5 (2008-10-29)
------------------

- Keywords werden alle 5 Minuten neu geladen (Bug #4501).
- SEO aus dem Kern entfernt.

1.2.4 (2008-10-24)
------------------

- Bei Link-Objekten kann jetzt »Neues Fenster« als Ziel ausgewählt werden (bug
  #4488).
- Beim Auschecken und Einchecken bleiben die Views stabil, d.h. wenn man sich
  z.B. die Assets anguckt und auscheckt, kann man danach direkt die Assets
  bearbeiten (bug #4357).
- Beim »Synchronisieren« des Bilderordners einer Galerie werden die Thumbnails
  neu erzeugt (bug #4496).
- Channels: Kein »Anzeigen«-Tab mehr bei ausgecheckten Channels; kein
  »Entfernen« mehr auf dem Anzeigen-Tab; die Checkboxen sind nicht mehr
  anclickbar (bug #4114).
- Channels: Checkbox um layout="big" einzustellen.
- Channels: Checkbox um Relateds zu verstecken (bug #4492).
- Channels: Positives ausdrücken der Checkboxen: »Versteckt auf HP« → »Auf HP
  anzeigen« und »Relateds verstecken« → »Relateds anzeigen«

1.2.3 (2008-10-17)
------------------

- Sicherstellen, dass Request-Objekte nicht ewig rumliegen und Speicher
  verbrauchen.

1.2.2 (2008-10-13)
------------------

- Standard-Copyright bei Bildern ist jetzt ein leeres Feld mit dem
  Copyright-Zeichen. Vor dem Speichern muss man das Feld löschen oder ein
  Copyright eintragen.

1.2.1 (2008-10-01)
------------------

- Locking erzeugt die richtige Exception.

1.2 (2008-10-01)
----------------

- Konzept des »Redaktionellen Inhalts« zur Unterscheidung verschiedener
  Workflows.
- Ordner können nicht mehr veröffentlich oder zurückgezogen werden.
- Channel, File, Portraitbox und Text sind jetzt Assets.
- Bilder gehen jetzt sinnvoll mit Arbeitsspeicher um (Bug #4410).
- Abhängiges Veröffentlichen: Wenn eine Bildergalerie veröffentlicht wird, wird
  ihr angehänger Bilderordner automatisch mitveröffentlicht. Beim Zurückziehen
  wird der Bilderordner auch entfernt.


1.1.11 (2008-09-18)
-------------------

- Wenn ein Bild von einem Artikel entfernt wird, wird dies jetzt auch im
  Channel reflektiert.
- Die Ausgabenummer ist generell kein Pflichtfeld mehr (Bug #4458).

1.1.10 (2008-09-16)
-------------------

- Zuweisen von Keywords sorgte im FF3 für Fehler.
- Scrollbar bei der R/O-Ansicht des Quelltexts (bug #4459).
- Syntax-Highliting in der R/O-Ansicht des Quelltexts.
- XML-Export der Standardeinstellungen für Jahr/Ausgabe (für Video-DB).

1.1.9 (2008-09-05)
------------------

- Die Größe und Skalierungsart (mit/ohne Boundingbox) der Thumbnails (für
  Bigas) ist jetzt konfigurierbar.
- Hit-Counter kommt jetzt besser mit Pfaden ala //index klar.
- XML-Editor: Styling-Fixes

1.1.8 (2008-08-28)
------------------

- Readonly-Ansicht für den Quelltext (Bug #4358).

1.1.7 (2008-08-26)
------------------

- Styling in  der Dateiliste korrigiert.

1.1.6 (2008-08-26)
------------------

- Asset-View: Read-Only-Ansicht zeigt jetzt die URL an, der Title wird als
  Tool-Tip angezeigt (bug #4219).
- Ressort muss jetzt vom Benutzer eingegeben werden, »Deutschland« ist nicht
  mehr vorausgewählt (bug #4387).
- Aussetzer um kurz nach Mitternacht behoben.
- Dateiliste zeigt mehr Informationen zum Workflow-Zustand.
- Widget zum referenzieren von Objekten zeigt Informationen zum
  Workflow-Zustand.

1.1.5 (2008-08-12)
------------------

- Links als Related Content fügen ihre Ziel-URL ins XML ein.
- Logs in Workflow-Ansicht werden auf die letzten 20 Einträge begrenzt.

1.1.4 (2008-08-06)
------------------

- WYSIWYG-Editor: Bilder, die nicht direkt unterhalb des <p> sind werden
  richtig in HTML konvertiert.

1.1.3 (2008-08-06)
------------------

- Korrektes Übersetzen des View-Titels.

1.1.2 (2008-08-04)
------------------

- Import der Vortagszugriffszahlen in mehreren Transaktionen.

1.1.1 (2008-08-01)
------------------

- Import der Vortagszugriffszahlen jetzt mit explizitem Locking. Zudem besseres
  Verhalten bei ungültigen Pfaden.

1.1 (2008-08-01)
----------------

- WYSIWYG-Editor kommt besser mit beliebigen ``article_extra``-Tags klar (bug
  #4442).
- Importieren und Speichern der Vortagszugriffszahlen.

1.0 (2008-07-29)
----------------

- Checkout/checkin während des Veröffentlichungsvorgangs funktioniert wieder
  immer (AttributeError: 'BaseResponse' object has no attribute 'getCookie')
- Sicherstellen, dass das automatische Related-Update aequivalente XMLs auch
  als gleich ansieht (sonst gibt es einen Recursion-Error beim Checkin).
- Ordner löschen dürfen nur noch Benutzer mit der Rolle "Producer".
- Templates können jetzt mit der Rolle "Producer" bearbeitet werden.
- Es kommen keine Daten mehr aus anderen Threads in den eigenen (via
  gocept.form>=0.7.5).
- Listing von Links robuster.
- Die Panels Clipboard und Bearbeitete Dokumente haben die Plaetze getauscht.
- WYSIWYG-Editor bei der Infobox (bug #4364).
- <a href> und <br/> in der BU (bug #4366).
- Sinnvolles Metadata-Preview bei Bildergallerien.
- Neuer Inhaltstyp: Datei
- Verbesserter Parser für das ISO8601-Datumsformat.
- Links fügen beim Syndizieren ihr Ziel in den Channel ein (als Attribut
  ``{http://namespaces.zeit.de/CMS/link}href``), bug #4407.
- "Kommentare erlaubt" jetzt bei den Standardmetadaten (bug #4385).
- Bei der Center-Page ist Ausgabe und Jahr kein Pflichtfeld mehr (bug #4408).
- Copyright-Default jetzt "ZEIT ONLINE" (bug #4409).
- WYSIWYG-Editor: Bilder, die nicht direkt unterhalb des <p> sind werden
  richtig erkannt.
- Content-Typ für Text, HTML oder sonstwie rohe Daten (bug #4360).

1.0b7 (2008-07-14)
------------------

- Automatisches Update der Bildmetadaten in Objekten, die das Bild
  referenzieren.
- Im Workflow-Log wird bei zeitgesteuerten Tasks die Zeit jetzt in CET
  angezeigt (nur bei neuen Einträgen; bug #4355).
- Beim Einchecken wird der Benutzer benachrichtigt, wenn die Related-Metadaten
  nicht aktualisiert werden konnten.
- Beim Einchecken wird der Benutzer benachrichtigt, wenn die Metadaten in nicht
  in den Channeln aktualisiert werden konnten.
- collapseTree liefert keinen sinnlosen KeyError mehr (bug #4308).


1.0b6 (2008-07-10)
------------------

- View zum Anzeigen der Objekte, die den meisten Speicher verbrauchen.
- Repository lädt jetzt Objekte auch per Pfad "/cms/work" und gibt das
  entsprechende "http://xml.zeit.de"-Objekt zurück.
- Portraitboxen haben jetzt noch einen <block> (bug #4325).
- Der Text von Portraitboxen wird richtig geladen.
- Biga: Text ist kein Pfichtfeld mehr (bug #4324).
- XML-RPC-Methode zum veröffentlichen (bug #4331).
- Align auf Bildern (bug #4349).
- Änderungsdatum in Dateilisten in CET statt GMT (bug #4354).
- Extra-BU bei Bildergallerien.
- Begrenzung des Veröffentlichungszeitruams auf Daten bis 2030, weil sonst der
  lovely.remotetask Mist baut.
- Konzept von temporären Checkouts um parallel veröffentlichen zu können.


1.0b5 (2008-06-30)
------------------

- TypeError beim laden der UnknownResource durch neue Subclass
  PersistentUnknownResource behoben.

1.0b4 (2008-06-30)
------------------

- CMS-Lock-Behandlung repariert wenn Resourcen in anderne System gesperrt
  werden (oder das CMS das denkt).
- Workflow: Fehler beim Veröffentlichen/Zurückziehen im Objectlog speichern
  und dem Benutzer anzeigen.
- Unknown resource ist jetzt ``Persistent``, damit klappt auch das Speichern.
- Repository entfernt Objekte im RAM an den Transaktionsgrenzen.
- View zum anzeigen der Refcounts.

1.0b3 (2008-06-28)
------------------

- Speichern von Assets stabiler (Persistenz-Problem).
- Bild-Metdaten-Anzeige: Titel wird jetzt angezeigt (bug #4304).
- CMS geht nicht mehr kaputt, wenn das today.xml leer ist (bug #4323).

1.0b2 (2008-06-28)
------------------

- Die Channel-Ansicht geht nicht mehr kaputt, wenn ein Objekt ohne Titel
  syndiziert wurde (bug #4312).
- Entfernen von Links aus Channels stabilisiert.
- Assets-Popup: Einklappen/Ausklappen des Baumens ohne Zugriff auf
  WebDAV-Server.
- Vernünftige Fehlermeldung, wenn ein Related nicht zum XML werden kann.
- Korrektes Löschen von Caches beim abort (bug #4299).
- Sperren von Resourcen beim Veröffentlichen.

1.0b1 (2008-06-26)
------------------

- Styling des globalen Drop-Down-Menus
- Menu im Metadaten-Preview funktioniert wieder.
- Sortieren bestimmter Channels geht wieder (bug #4302).
- Metadaten-Vorschau bei Bilderguppen zeigt Thumbnails der Bilder.
- Bildergruppe geht nicht kaputt, wenn ein Ordner zur Bildergruppe wird, der
  nicht nur Bilder enthält (bug #4301).
- Asset-Views bei Center-Page (bug #4306).
- SyndicatedIn-Source war optimistisch über den Inhalt und ging bei
  "unbekannten Resourcen" kaputt (bug #4300).
- DailyNL in den Standard-Metadaten (bug #4307).
- JS-Warnung, wenn kein Firefox verwendet wird (bug #4305).
- Popup-Asset/Image-Browser expandiert den automatisch Baum wenn man in einem
  Ordner drin ist.
- date-last-modified als webdav-property für XML-Inhalte (bug #4310).

0.9.22 (2008-06-23)
-------------------

- Die Relateds werden beim Ändern des relateds nicht mehr doppelt in den
  Channel eingetragen (bug #4293).
- Globale Menus umgebaut, so dass weniger wichtige Eintrage in einem Dropdown
  verfügbar sind.
- Manuelles einstellen von Jahr/Ausgabe (bug #4273).
- Bilderordner beim Asset-Bearbeiten wird jetzt durch manuell eingestelltes
  Jahr/Ausgabe bestimmt. Auf jedem Ordner kann durch die WebDAV-Property
  {http://namespaces.zeit.de/CMS/Image}base-folder bestimmt werden wo die
  Wurzel für den Bereich ist (z.B. /zuender ->
  http://xml.zeit.de/bilder/zuender/)
- Kein Fehler mehr beim Bearbeiten von Objekten, die nicht mehr im Repository
  existieren (bug #4291).
- Biga hat jetzt Assets (bug #4294).
- Biga hat jetzt <gallery> als Root-Tag (bug #4295).
- Metadaten bearbeiten: Spitzmarke füllt Kurzteasertitel und Titel füllt
  Kurzteasertext (bug #4251).

0.9.21 (2008-06-19)
-------------------

- Noch bessere Unterstützung für alte Bildergalerien, so dass auch der Text
  richtig übernommen wird.

0.9.20 (2008-06-18)
-------------------

- XML-Editor: <column> unterhalb von <block> erlaubt (Zuender)
- XML-Editor: <block> mit priority="" geht nicht mehr kaputt.
- XML-Editor: Lange URLs im <block href=... zerfetzen das Layout nicht mehr
- XML-Editor: Bearbeiten von hrefs im <block>
- XML-Editor: Besseres "Click-Verhalten" beim Anzeigen der Aktionen
- Bessere Unterstützung für alte Bildergelerie

0.9.19 (2008-06-16)
-------------------

- Re-added released_from/released_to to the Workflow interfaces.

0.9.18 (2008-06-16)
-------------------

- Rekursives veröffentlichen und zurückziehen.
- Lighbox-Überschrift überdeckt jetzt nicht mehr den Schließen-Knopf
- Homepage-Teaser werden jetzt auch per JS begrenzt.
- Das Verwenden verschiedener Formate in einer Bildergruppe ist jetzt erlaubt.
- Veröffentlichungs- und Zurückziehscript eingebunden.
- Spezieller Workflow für Assets (derzeit nur Bilder).
- Zeitgesteuertes veröffentlichen/zurückziehen.
- Unterressort auswählen funktioniert jetzt ohne vorherigem Speichern des
  Ressorts (bug #4268).
- Keyword-Typeahead rennt jetzt nicht mehr bei jedem Buchstaben zum Server;
  außerdem wird das Ergebnis vom Browser gecacht (bug 4270).
- "Unendlich"-Knopf bei Datumseingabe (leert das Feld).
- Bilder haben kein besonderes Löschdatum mehr, dafür ist der Workflow da.
- Formulare sind nicht mehr Denglisch (bug #3734).
- WYSIWYG-Editor: Popups zeigen jetzt den Cursor an (bug #4221).
- Tab "Syndizieren": Die Ziele sind jetzt nach der Id sortiert (bug #4269).
- XML-Daten werden jetzt mit Pretty-Print zum DAV gegeben (bug #4256).
- Dateiliste: Klick auf den Dateinamen selektiert die Zeile jetzt (bug #4255).
- Homepage-Teaser/-Text haben jetzt keine Längenbegrenzung mehr.
- Die Metadaten von Relateds und Bildern werden jetzt beim Checkin aktualisiert
  (bug #4226).
- Workgingcopy-Preview gibt Query-Argumente jetzt beim Rendern weiter, so dass
  man auch die Seiten durchblättern kann (bug #4286).


0.9.17 (2008-06-10)
-------------------

- Suche stirbt nicht mehr an Umlauten (bug #4195).
- WYSIWYG-Editor: Listen werden jetzt korrekt unterstützt (bug #4223).
- Datums/Zeit-Felder haben jetzt Knöpfe für "in einer Woche" und "in einem
  Monat".
- Neue Defaults für nicht-angezeigte Ordner (bug #4229).
- Defaults für Syndizierungsziele (bug #4229).
- Es gibt jetzt die Möglichkeit den Typ von Objekten im UI zu ändern.
- Beim Bearbeiten/Aus-/Einchecken werden Processing-Instructiongs nicht mehr
  gelöscht (bug #4258).
- Aktion zum expliziten invalidieren des Caches eines Ordners.
- Link-Objekt wird nach dem Anlegen auch automatisch ausgecheckt (bug #4254).
- Asset-View refaktoriert: Links haben jetzt auch einen Asset-View.
- Channels verstehen jetzt <block>s mit einem externen HREF. Diese Blöcke
  werden angezeigt und können sortiert/entfernt werden (bug #4259).

0.9.16 (2008-05-29)
-------------------

- Anlegen von Objekten mit Umlauten oder anderen wirren Zeichen führt nicht
  mehr zum Systemfehler sondern gibt "Einschrankung nicht erfüllt" aus (bug
  #4166).
- Zweite Biga-Referenz im Artikel
- Aus einem Channel können Objekte jetzt gelöscht werden (bug #4179).
- Wird ein falsches Objekt bei den Assets referenziert gibt es jetzt eine
  sinnvolle Fehlermeldung anstatt "Raised if Validaiont fails" (bug #4174).
- Objekte Referenzieren: Wenn der Pfeil -> mit aktivem Shift, Ctrl oder Meta
  gedrückt wird geht ein neues Tab/Fenster auf (bug #4175).
- Auf der Biga gibt es jetzt einen Link zum Bild (bug #4180).
- Der HTML-Titel im CMS beinhaltet jetzt den Titel des Objekts (bug #4152).
- ObjectBrowser zeigt jetzt den aktuellen Pfad an (bug #4058).
- ObjectBrowser gibt eine Meldung aus, wenn im Ordner nichts auswählbares
  vorhanden ist.

0.9.15 (2008-05-26)
-------------------

- Channels werden beim Syndizieren gesperrt.
- zeit.relation ist jetzt zeit.cms.relation.
- Teilweise wurde ein <head><relateds> implizit ereugt, bug #4183.
- Jedes Objekt weiß jetzt wohin es Syndiziert wurde (via zeit.cms.relation, bug
  #4178).
- Beim zurückziehen im Workflow wird ein Objekt aus den Channeln in denen es
  enthalten ist entfernt (bug #4177).
- Bildergalerie speichert ihre DAV-Properties jetzt auch im XML.
- Zurückziehen von Objekten muss nochmals bestätigt werden, incl. Warnung über
  die Konsequenzen.
- Nachrichten werden nur noch im Fehlerfall 5s angezeigt, sonst 0.5.
- Metadaten eines Bildes beim Referenzieren korrekt eingebunden (bug #4189).
- Wenn eine Bildergruppe eingebettet wird hat das <image>-Tag jetzt das
  Attribute "type", welches die Extension der Bilder angibt (bug #4188).
- Wenn der WYSIWYG-Editor <div>s oder andere falsche Tags produziert, wird ein
  <p> daraus (bug #4171).

0.9.14 (2008-05-20)
-------------------

- Ein Objekt kann nur noch einmal ausgecheckt werden.
- Sortierung des Panels "Ausgecheckte Dokumente" korrigiert: das zuletzt
  ausgecheckte ist oben.
- Diverse Typos, Wording
- Sub-Navigation: Ermöglicht, dass es mehrere Subnavigations mit dem selben
  Namen gibt.
- Bilder/Links sind im WYSIWYG-Editor jetzt interne CMS-Links, damit z.B.
  Bilder inline sofort angezeigt werden können (bug #4163).
- WYSIWYG-Editor: Bild im Absatz einfügen löscht nicht mehr den Rest des
  Textes.
- WYSIWYG-Editor: Paste from Word erzeugt zuverlässiger Absätze
- Im Preview von ausgecheckten Dokumenten kann man jetzt "reload" drücken (und
  das Preview wird auch aktualisiert, Bug #4173)
- Artikel ist jetzt in einem eigenen Package: zeit.content.article


0.9.13 (2008-05-13)
-------------------

- Properties mit dem Namespace "DAV:" werden jetzt nicht mehr in XML-Dokumente
  kopiert (bug #4126).
- Filter in Dateiliste reagiert jetzt auf Dateinamen (bug #4132).
- Videos können jetzt im WYSIWYG-Editor bearbeitet und eingefügt werden (bug
  #4149).
- Neuer Contenttype: Portraitboxen (bug #3852).
- Portraitbox in Artikel verlinken (bug #4051).
- Behandlung von Clipboard-Einträgen auf gelöschte Objekte verbessert.
- Sortierung nach Änderungsdatum ging nicht immer (bug #4150).
- Wenn ein Verzeichnis XML-Resourcen enthält, die kein valides XML enthalten
  werden sie jetzt als unbekannte Resource interpretiert (bug #4151).


0.9.12 (2008-04-30)
-------------------

- "Erstes Related als Box" (bug #4053).
- status=OK bei veröffentlichten Dokumenten (bug #4125).
- Sortierung der Suche (Jahr/Ausgabe) korrigiert (bug #4113).
- ehannels mit body/container liefert kein Forbidden mehr.

0.9.11 (2008-04-28)
-------------------

- Selten gebrauchte Aktionen in ein DropDown verschoben (derzeit umbenennen und
  löschen).
- Einige Menu-Titel wurden nicht übersetzt (bug #4115)
- Unterstützung für alte Channels mit body/container (bug #4109).
- Favicon im CMS jetzt mit rosa Hintergrund zur besseren Unterscheidung (bug
  #4127).
- Objekte können jetzt kopiert werden: Aktion auf Ordnern bei der man das zu
  kopierende Objekt aus dem Clipboard wählt (bug #4130).
- Breadcrumbs sind wieder draggable.
- Keine freie Eingabe von Keywords mehr (bug #4120).
- Doppelte Eingabe von Keywords nicht mehr möglich (bug #4119).
- Liste der Keywords bei Typeahead ist jetzt sortiert.

0.9.10 (2008-04-22)
-------------------

- Droppen von Objekten in einen Channel führt nicht mehr zum JS-Fehler (sondern
  zu einer richtigen Fehlermeldung), bug #4094.
- Horizontales scrollen in der Dateiliste erlaubt, wenn die Tabelle zu breit
  wird.
- Channel haben jetzt <channel> als Root-Tag (bug #4109).
- Relateds werden jetzt bei der Syndizierung mit eingefügt (bug #4106).
- Asset-Bearbeiten/Anzeigen-Seite produzierte einen Systemfehler, wenn es
  artbox_info als Property gab, diese aber leer war oder einen ungültigen Wert
  hatte (bug #4124)
- Formlayout bei geringer Breite nicht mehr zerpflückt (bug #4118).
- Homepage-Teaser hinzugefügt (bug #4122).
- Related werden jetzt mit Kurzteaser und HP-Teaser eingebettet.
- Factored out zeit.ldap into its own package.
- Im Workflowtab werden Statusänderungen jetzt als Log angezeigt (bug #4121).

0.9.9 (2008-04-14)
------------------

- Veraltete Einträge im Funktions-/Methodencache werden jetzt alle 100 Requests
  entfernt.
- Im Channel werden die Treffer/Hits (today.xml) des jeweiligen Dokuments
  angezeigt (bug #4093).
- Bildergalerie: Layout kann pro Bild eingestellt werden (bug #4048).
- Bildergallerie bei Artikel referenzieren (bug #4052).
- Workflowstatus "Bearbeitet" heißt jetzt "redigiert" (bug #4089).
- Draggen von Dokumenten in den Kalender funktioniert wieder (bug #4096).
- Kalender-Eintrag: Formular übersichtlicher
- Draggen von Elementen aus "Bearbeitete Dokumente" (bug #4095).
- Bearbeite Dokumente: Das zuletzt ausgecheckte Dokument steht jetzt oben (bug
  #4054).
- Verlinkte Objekte: 3-Punkte-Symbol mit Mouse over versehen (bug #4057).
- Verlinkte Objekte: Zusätzlicher Knopf (Pfeil nach rechts) um zum verlinkten
  Objekt zu gelangen (bug #4082).

0.9.8 (2008-04-09)
------------------

- Related konnte nicht mehr in der Lightbox ausgewählt werden
  (ScrollStateRestorer not defined).
- Bug beim Referenzieren von Objekten behoben, z.B. ging ein Image als Related
  nicht, unbekannte Resourcen konnten nicht verlinkt werden (Systemfehler).
- Titel der Workflow-Status-Suchfelder korrigiert (bug #4088).
- Besseres cachen der Datenquellen (in zeit.cms.content.sources).
- WYSIWYG-Editor: Auswählen von Objekten aus dem Clipboard repariert (bug
  #4097).
- Fließtext kann jetzt Bilder beinhalten. Diese sind vom Server per FCKEditor
  Filebrowser auswählbar (bug #4090)
- Text in der Gallery ist jetzt auch per WYSIWYG-Editor bearbeitbar (bug
  #4091).


0.9.7 (2008-04-07)
------------------

- Die Bedingungen für die Veröffentlichung werden explizit geprüft: Ein Objekt
  kann nur veröffentlicht werden, wenn es "eilig" ist oder die Status auf ja /
  nicht nötig stehen (bug #4068).
- Objekte können zurückgezogen werden (aus der Veröffentlichung, bug #4081)
- Suche kann die Workflowstatus "bearbeitet" und "Bilder hinzugefügt" suchen
  (bug #4083).
- Die Not Found (404) Seite sieht jetzt wieder ansprechend aus.
- Systemfehler werden jetzt etwas schöner und informativer angezeigt (bug
  #4033).
- Bilder haben jetzt eine URL (bug #4047).
- Bug in Clickcounter-Cache behoben: today.xml wird jetzt auch gecacht.
- Indikator im Dateilisting zeigt den Veröffentlichungszustand: nicht
  veröffentlicht (rot), veröffentlicht (grün) oder veröffentlicht mit
  Änderungen im CMS (gelb/orange). (bug #3954)
- Metadaten-Vorschau zeigt sämtliche Workflow-Attribute auf der rechten Seite
  (bug #3954).


0.9.6 (2008-04-03)
------------------

- DefaultView fuer Infobox hinzugefügt.
- Assets eines Artikels werden jetzt in eigenem Formular bearbeitet.
- Automatisches Anlegen des Ordners mit den Workingcopy-Vorschau-Daten (bug
  #4056)
- Standardlöschdatum eines Bildes "in 7 Tagen" (bug #4019)
- Das Unterressort ist jetzt auch eine Drop-Down. Es ist abhängig von der
  Auswahl des Ressorts (bug #4036).
- Wenn ein Artikel ein Ressort mit Umlaut hatte, welches nicht in der
  ressort.xml enthalten war ab es einen Systemfehler beim logging.


0.9.5 (2008-03-25)
------------------

- Besser sichtbar gemacht ob ein Objekt gesperrt ist (bug #4025)
- Sortierung in Listen: Jahres/Ausgaben-Ordner zuerst, Groß-/Kleinschreibung
  ignorieren (bug #3926)
- Bei Aktionen Nachricht an den User senden (bug #4022)
- "Sperre stehlen" gibt dem stehlenden jetzt den Lock.
- Fixed clipboard entry delete from action menu.
- Made context action icons lighter with hover effect.
- Using (x) delete icon instead of "Remove" in clipboard (bug #4045)
- Allowed-renaming of clips (bug #4063)
- Fixed a bug which prevented adding clips containing / or starting with @ or +
- Hide root nodes in repository and clipboard because those are redundant
  (panel header already shows this information). Also moved the trees to the
  left to save some space. As a side effect one now has to add a clip before
  adding anything to the clipboard.


zeit.connector CHANGES
======================

2.12.0 (2019-02-19)
-------------------

- MAINT: Guess MIME type in filesystem connector just like Apache does for DAV connector


2.11.0 (2018-07-06)
-------------------

- MAINT: Make cache sweep timeout configurable via parameter


2.10.4 (2018-01-19)
-------------------

- TMS-28: Support zeit.web tests by parsing `/head/rankedTags` into the
  TMS `keyword` property


2.10.3 (2017-11-01)
-------------------

- BUG-791: listCollection() no longer ignores childname entries that
  don't exist in the property cache, since we cannot decide whether
  they're actually gone at that point, only when they are actually
  accessed (so zeit.cms.repository values() takes over that duty).


2.10.2 (2017-08-18)
-------------------

- MAINT: Add package version to our user agent header


2.10.1 (2017-07-04)
-------------------

- FIX: Another stab at dealing with brokenly encoded filenames


2.10.0 (2017-06-12)
-------------------

- ZON-3997: Move Zope dependencies to setuptools extra


2.9.0 (2017-02-16)
------------------

- BUG-661: Support reading the DAV content type for raw files in
  filesystem connector


2.8.1 (2016-10-19)
------------------

- Add CLI script to set DAV properties from filesystem data.


2.8.0 (2016-09-09)
------------------

- Don't parse the meta files as metadata for itself.


2.7.8 (2016-08-11)
------------------

- Handle errors in utf-8 decoding properly.


2.7.7 (2016-08-10)
------------------

- Handle non-ascii filenames by assuming utf-8 encoding.


2.7.6 (2016-03-07)
------------------

- Catch strange "the bucket being iterated changed size" error in cache sweeper.


2.7.5 (2016-03-03)
------------------

- Ignore already gone entries in cache sweeper.


2.7.4 (2015-11-17)
------------------

- Ignore strange filenames like `._foo.jpg.meta` properly.


2.7.3 (2015-10-30)
------------------

- Change ``search()`` error to a log.warning instead of a NotImplementedError,
  so it does not disturb zeit.web production.


2.7.2 (2015-10-23)
------------------

- Cache canonical ids (transaction-bound) in filesystem connector.


2.7.1 (2015-10-23)
------------------

- Fix bug in childname cache (used wrong keys to store results).


2.7.0 (2015-10-22)
------------------

- Add transaction-bound caching to filesystem connector.

- Make canonicalizing directory uniqueIds configurable in filesystem connector
  via product config ``zeit.connector:canonicalize-directories = False``
  (defaults to True which is the behaviour since 2.4.0).


2.6.9 (2015-09-25)
------------------

- Fix off-by-one error in cache sweeper.


2.6.8 (2015-09-24)
------------------

- Parse empty attribute nodes as empty string in filesystem connector so it
  behaves like DAV connector.


2.6.7 (2015-09-23)
------------------

- Commit sweeps every 100 items to avoid conflict errors.


2.6.6 (2015-08-27)
------------------

- Catch bad request exceptions and terminate traversal (ZON-2062).


2.6.5 (2015-08-13)
------------------

- Generalize treatment of folder content-types in filesystem connector,
  instead of hard-coding a list of specific types.

- Undo not found logging, since we cannot differentiate between existence
  checking and actual resolving, this spams the logs for no benefit.


2.6.4 (2015-07-27)
------------------

- Log when a resource is not found.


2.6.3 (2015-06-23)
------------------

- Fix bug in moving collections: move all members before deleting the source
  (BUG-271).


2.6.2 (2015-05-22)
------------------

- Allow dynamic-collection folder types in the filesystem connector (ZON-1613)


2.6.1 (2015-03-19)
------------------

- Commit cache sweep one day's worth at a time.


2.6.0 (2015-02-04)
------------------

- Allow configuring repository path for mock connector via product config.


2.5.1 (2015-01-15)
------------------

- Don't perform data migration inside generation, it takes too long / never
  completes in production (VIV-584).

- Isolate tests against real DAV servers by using a dedicated, temporary test
  folder.


2.5.0 (2015-01-12)
------------------

- Store last access times for property and childname cache, too (VIV-584).


2.4.0 (2014-12-17)
------------------

- Filesystem connector now handles directory-type resources (especially:
  ImageGroups) like the DAV connector does: their uniqueId gets a trailing
  slash.


2.3.5 (2014-12-04)
------------------

- Brown-bag release.


2.3.4 (2014-10-21)
------------------

- Update dependency to ZODB-4.0.


2.3.3 (2014-03-26)
------------------

- Handle image groups in filesystem connector.


2.3.2 (2014-03-21)
------------------

- Fix bug in handling non-existent resources in filesystem connector:
  don't pass along OSError, but raise the proper KeyError.


2.3.1 (2014-03-14)
------------------

- Add a second image to the testcontent fixture, as they are really hard to create on the fly.


2.3 (2014-02-11)
----------------

- Fixed an interface declaration.

- Added a ZCML file for configuring a plain caching DAV connector.

- Replaced the non-caching DAV connector with one that uses transaction-bound
  caches. (#FRIED-31)


2.2 (2014-01-26)
----------------

- Add a non-caching DAV connector. (#FRIED-31)

- Add a read-only filesystem connector that uses a directory tree of XML files
  as its data storage. The mock connector now derives from the filesystem
  connector.


2.1.0 (2014-01-07)
------------------

- Make repository path configurable on mock connector.

- Add workaround for rankedTags property to mock connector.


2.0.4 (2013-11-17)
------------------

- Add ``testing`` folder to mock connector data for uniformity with real
  connector tests.


2.0.3 (2013-09-24)
------------------

- Fix test setup after removal of unittest2.


2.0.2 (2013-09-24)
------------------

- Fix quoting of entities (``&amp;``) in URLs (#8575).


2.0.1 (unreleased)
------------------

- Fix tests for Python 2.7


2.0 (2013-04-23)
----------------

- Added clean-up for MOVE on abort: A MOVE is un-done by the reverse MOVE
  operation on transaction abort. (#12252)

- Added automagic conflict resolution for MOVE (#12139)


1.26.0 (2012-12-17)
-------------------

- Include new required properties in the test content fixture.
- Silence the mock connector 'searching...' messages.


1.25.1 (2012-03-06)
-------------------

- Added random value to mock connector's etag generator as subsequent calls to
  ``time.time()`` may the same value.

(NOTE: This version should have bevome 1.24.1. But once released we are not
retracting).


1.24.0 (2012-03-01)
-------------------

- Update mock fixture: DailyNL has moved to the 'document' namespace (#10056).

- Fix connector.txt test which (probably) broker after the last DAV server
  update (#10337)

- Fix search test which expected a result from the server which is not strictly
  necessary (#10339).

- Removed flaky threading test which was not actually useful because of a
  different database behaviour in test vs. production (#10352)


1.23.1 (2012-01-18)
-------------------

- Fix unicode error in search by encoding unicode to utf8.


1.23.0 (2011-11-13)
-------------------

- Fix decoding of URLs in DAVResponse when there is raw UTF8 in the xml
  (instead of fully url encoded).
- Corrected Logging of query-server queries (#8308)
- Pass lock-token for MOVE (#8980).
- Fix query server integration: The API implemented ``range()`` while it must
  read ``between()``.
- Raise exception in connector when query server returns an error.
- Allow to store strucured (XML) values in properties (#9899)


1.22.2 (2010-08-30)
-------------------

- Connector invalidation event subscriber doesn't raise ValueError any longer
  for UniqueIds the connector isn't responsible for (#7933)


1.22.1 (2010-08-17)
-------------------

- Fixed cache invalidation for collections with non-collection ids (#7906).


1.22.0 (2010-08-16)
-------------------

- When the cache is invalidated it only causes write request when there
  actually was a change. Before cached data was thrown away and stored in any
  case (#7797).


1.21.0 (2010-07-06)
-------------------

- Set the UUID via a custom header on PUT (#7366).

- MOVE is now doing a MOVE instead of COPY+DELETE (#7440)


1.20.1 (2010-06-09)
-------------------

- Rename supports renaming to ids with non-us-ascii chars (#7405)
- Correctly escape # in ids (#6042).
- Using versions from the ZTK.


1.20.0 (2010-01-18)
-------------------

- Do not sweep cache automatically. This should be done via a cronjob.


1.19.3 (2009-10-08)
-------------------

- Don't raise a PreconditionFailedError when the body of the stored resource
  matches the to-be-written body. This is to support ZODB conflict errors
  without DAV having transactions.

- Fixed level 3 tests.


1.19.2 (2009-09-29)
-------------------

- Mock connector behaves more like the real one in regard to conflicts and
  etag preconditions.


1.19.1 (2009-09-28)
-------------------

- Removed a savepoint to avoid garbage collection which lead to LockingErrors.
  Note that this probably is a ZODB bug we're working around here.


1.19 (2009-09-24)
-----------------

- Honour the ETAG for PUT requests so there is a way to detect conflicts.

- Refactored DAV exceptions and exception handling to get this mor straight.

- Autolocks when adding content are immeadeately removed when there was an
  error during PUT or PROPPATCH.

1.18.4 (2009-09-21)
-------------------

- PROPPATCH on a locked resource raises correct DAVLockedError (#6237).


1.18.3 (2009-09-06)
-------------------

- Fixed test as content changes.


1.18.2 (2009-09-01)
-------------------

- Fixed Property conflict resolution with ZODB 3.9.0c


1.18.1 (2009-08-18)
-------------------

- Python 2.6 compatibility.

1.18 (2009-08-14)
-----------------

- There was a chance that cache inconsitencies could yield a KeyError: "The
  resource xzy does not exist." (#5993).

1.17.1 (2009-08-05)
-------------------

- Refactored body cache to no longer reuse blobs for even better conflict
  resolution.

1.17 (2009-07-24)
-----------------

- Fixed an issue with vanishing Blob files sending a POSKeyError to the user.

- Refactored body cache store Body objects which do conflict resolution. This
  way two threads storing the same body don't generate a conflict.

1.16.1 (2099-07-23)
-------------------

- Fixed a unicode bug in cache (related to #5580).

1.16 (2009-07-23)
-----------------

- Reuse Blobs instead of creating new ones when updating resources (#5580).

- Don't fail in abort clean up when a lock has timed out (#5578).

1.15.1 (2009-06-25)
-------------------

- Make sure no SecurityProxies are tried to be stored as cache keys.

1.15 (2009-06-24)
-----------------

- Support UTF8 characters in URLs (#5534).

- Make less HEAD requests.

- Don't send full URLs in the request to the DAV as HTTP/1.1 actually want's
  paths.

1.14.4 (2009-06-19)
-------------------

- SecurityProxy-Fehler im Cache behoben (maximum recursion depth exceeded)

1.14.3 (2009-06-18)
-------------------

- Repackaged (setupools/svn 1.6 problem).

1.14.2 (2009-06-18)
-------------------

- Fixed bug in mock connector: last-modified property is now set with timezone
  UTC.

- Use only one way to change properties.

1.14.1 (2009-06-15)
-------------------

- Make sure we really read all the bodies at the right time.

1.14 (2009-06-15)
-----------------

- Cache invalidaion is smarter now. This allows processing larger amounts of
  invalidation events without the knowledge about the kind of the change
  (delete, add, ...).

- Do not operate on paths and URLs but only pass URLs to the WebDAV server.

- When a PROPFIND is not finished by Apache because of an error, the connector
  waits a bit and retries the request.

- Refactored code to make it cleaner. Also do less HEAD requests.

1.13 (2009-06-04)
-----------------

- Made sure the {INTERNAL}cached-time is not stored on the DAV.

- Fixed a bug in the property cache conflict resolver which took the
  cached-time into account.

1.12 (2009-06-03)
-----------------

- Relatexed othersystem locks: If there is a lock the connector doesn't know
  about, but knows about the locking user id (principal), it considers the lock
  as if it was the connectors lock (#4996).

1.11.1 (2009-05-15)
-------------------

- Alle ``test.py`` nach ``tests.py`` umbenannt.

1.11 (2009-04-23)
-----------------

- The lock time out now works also with the property cache. Locks were just not
  timing out when using the fully integrated connector (fixes #4997).

1.10 (2009-04-09)
-----------------

- Fixed "AttributeError: 'BTrees.OOBTree.OOTreeSet' object has no attribute
  'add'" which occured on existing databases.

- Fixed refresh-cache to not fail with a bogus property cache.

- Improved ConflictResolution so equal states are kept instead of thrown away.

1.9 (2009-04-08)
----------------

- Added conflict resolution for the PropertyCache and ChildIdCache. This
  hopefully leads to less conflicts.

- Added an invalidtor runner which refreshes the whole property cache.

1.8 (2009-04-07)
----------------

- Connector knows of lock timeouts now (fixes #4914).

1.7 (2009-03-23)
----------------

- CachedResource now returns a read-only property object (fixes #3869).

1.6.5 (2009-03-04)
------------------

- Mock-Connector returns correct getlastmodified.

1.6.4 (2009-01-19)
------------------

- Fixed a bug in child-id cache which led to an invalid list of child ids in
  some circumstances (like with the preview objects).

1.6.3 (never released)
-----------------------

- 1.6.3 was never released because version was accidentally increased to 1.6.4.

1.6.2 (2008-12-12)
------------------

- Resources of null resource locks do not longer have the HTML 404 error
  message as body.
- Mock connector: Existing collections do have a getlastmodified property now.

1.6.1 (2008-11-28)
------------------

- Fixed threading test.

1.6 (2008-11-27)
----------------

- Set the referrer header to the URL the current interaction was created with.

1.5 (2008-11-24)
----------------

- Be smarter when invalidating folders when objects are added or deleted. This
  should lead to much better performance for adds/deletes.

1.4.7 (2008-11-20)
------------------

- No more test extra.
- Functional test layer can be torn down.

1.4.6 (2008-11-19)
------------------

- PropertyCache and ChildNameCache do not write data when the value is
  already stored in the cache. This should lead to fewer conflict errors.

1.4.5 (2008-08-12)
------------------

- Fixed a bug in the body cache which lead to a database write on cache read.

1.4.4 (2008-08-07)
------------------

- The discovery of the cannonical id of a resource does a HEAD request on the
  base url (w/o trailing slash) now. This leads to massively decreased 404's on
  the server.
- Removed auto-redirect in dav module as this was not required and just added
  complexity.
- Removed unnecessary PROPFIND's in dav module.
- Added a stress test which does property changes in parallel.

1.4.3 (2008-08-05)
------------------

- Changed the way the body cache keeps track of access times. The new way is
  hopefully less conflict prone.


1.4.2 (2008-08-05)
------------------

- When the connector invalidates resources, the're reloaded immedeately to
  have less conflict potential.

1.4.1 (2008-08-01)
------------------

- Made cache sweep more stable agains inconsistent data.

1.4 (2008-08-01)
----------------

- Empty WebDAV properties were returned as None and subsequently stored as
  'None' (fixes bug #4443).

1.3 (2008-07-29)
----------------

- Reverted changes from 1.2 and added a test to make sure the properties are in
  fact updated.

1.2 (2008-07-29)
----------------

- Do not re-set the property cache on ``changeProperties`` but just update.

1.1 (2008-07-24)
----------------

- Body-Cache doesn't store strings directly but via a persistent object.
- Use a Singleton class for webdav property keys.
- Body-Cache always returns an object which can be passed beyond the
  transaction boundary now.
- Mock stores Content-Type of resources now.

1.0 (2008-07-14)
----------------

- Only invalidate parent on adding resource when really necessary.

1.0b4 (2008-07-09)
------------------

- longrunning.txt did not reset DEBUG_CONNECTION.
- Removed conflict hotspot from property and child id cache.

1.0b3 (2008-07-04)
------------------

- Caches are using the plain unique id as cache key now (not reversed).
- Property-Cache reuses (name, namespace) tuples hand passes out references to
  the same tuples. This leads to having only one tuple instance per (name,
  namespace).
- PropertyCache stores the properties as OOBTree.
- ChildNameCache stores the childnames as TreeSet
- Small bodies (<=10 kB) are no longer stored as blob but as plain string.
- Fix for "BadStatusLine" which occours when the DAV server closes the
  connection.

1.0b2 (2008-06-28)
------------------

- Fixed handling on transaction abort so we're not writing to the database
  during "committing" phase.
- Removed property cache invalidation during server startup since this is just
  too heavy for production use.
- `changeProperties` doesn't invalidate the resource but updates the cache
  itself.
- Removed content migration script.

1.0b1 (2008-06-27)
------------------

- Using event system in ZopeConnector to invalidate caches.
- Fixed a bug when getting NULLResources or other resources w/o etag (bug
  #4315).
- Make sure connector continues to work when the connection gets into an
  inconsistent state (bug #4109).

0.22 (2008-06-23)
-----------------

- Mock: Allowed to get the root as resource.

0.21 (2008-06-16)
-----------------

- Make sure 'NoneType' object has no attribute 'group' doesn't occur anymore.
- Make sure XML-like content can be put in a property by prefixing it. This is
  a temporary fix until it is decided what the DAV server will do in this case.
- Added a DataManager where the connector can register things to clean up on
  transaction abort.
- Sending User-Agent "zeit.connector"

0.20 (2008-06-10)
-----------------

- General code cleanup
- Explicitly reading all data from response instead of brutally closing the
  connection.
- Use lxml to generate xml instead of string-concatenation in most places.

0.19 (2008-05-23)
-----------------

- Fixed better lock handling from 0.17
- Only invalidating parent of a resource when parent actually has changed.

0.18 (2008-05-19)
-----------------

- Fixed a bug in the cache sweeping which did not remove the actual data.
- Diversified cache keys by reversing unique_id. Objects which are close in the
  tree should now be in differend BTree buckets.

0.17 (2008-05-19)
-----------------

- Better lock handling: always look for definete information on the server
  before locking/unlocking or doing anything with a lock.
- Removed the live searching tests.

0.16 (2008-05-13)
-----------------

- Moved ZopeConnector to sperate module.
- Keep HTTP connection open for better performance. Connections will be closed
  at the end of the transaction (ZopeConnector).

0.15 (2008-04-28)
-----------------

- Fixed a bug in copy code which was not invalidating the caches correctly.

0.14 (2008-04-22)
-----------------

- `zeit.connector.connector.Connector` doesn't use the component architecture
  now. This makes it easier to use in console scripts.
- <feed> is now <channel> (mock connector).
- connector's move method uses copy+delete now
- Added copy method to IConnector which allows copying files and directories.
- Enabled move to move directories.

0.13 (2008-04-07)
-----------------

- Made DeleteProperty a rock in the zope.security.

0.12 (2008-03-25)
-----------------

- Moved locktoken storage to a separate utility, out of a cache.
- Added events to notify caches about invalidated resources.


zeit.content.advertisement changes
==================================

1.0.2 (2019-03-29)
------------------

- PERF: Don't grok browser packages by default


1.0.1 (2015-09-10)
------------------

- Make it possible to retrieve the image of the ad via
  ``z.c.image.interfaces.IImages`` (DEV-907)


1.0.0 (2015-08-24)
------------------

- Initial release.


zeit.content.article changes
============================

3.45.1 (2019-04-23)
-------------------

- ZON-5187: Add link object support for topicbox


3.45.0 (2019-04-03)
-------------------

- ZON-5187: Add topic box article module


3.44.5 (2019-04-02)
-------------------

- ZON-5168: Add additional Adplaces for ad-modul


3.44.4 (2019-03-29)
-------------------

- PERF: Don't grok browser packages by default


3.44.3 (2019-02-19)
-------------------

- ZON-2932: Style embed helptext field

- MAINT: Publish breaking news with the same priority as the homepage


3.44.2 (2019-02-13)
-------------------

- MAINT: Add `interfaces.articleSource` convenience instance


3.44.1 (2019-02-12)
-------------------

- ZON-5017: Add breaking news flag to facebook push


3.44.0 (2019-02-05)
-------------------

- ZON-2932: Add parameters to embed module form


3.43.1 (2019-02-05)
-------------------

- ZON-2932: Allow direct drag&drop for embed objects as well


3.43.0 (2019-01-11)
-------------------

- ZON-5075: Styling for additional twitter print fields

- ZON-5025: Add adplace module


3.42.2 (2019-01-07)
-------------------

- BUG-119: Fix error message positioning for teaser fields


3.42.1 (2018-12-20)
-------------------

- BUG-977: Handle the edge case that the node the user clicked on is one
  which we need to translate (em/i, strong/b).


3.42.0 (2018-12-18)
-------------------

- BUG-1010: Set default header_layout when template is changed

- OPS-955: Remove obsolete CDS functionality


3.41.2 (2018-11-20)
-------------------

- ZON-4957: Display separate read-only notice for author push


3.41.1 (2018-11-14)
-------------------

- FIX: brown-bag 3.41.0


3.41.0 (2018-11-14)
-------------------

- ZON-4999: Add `has_audio` property

- FIX: Treat empty CPs set as IArticle.layout as existing, not as missing


3.40.0 (2018-11-02)
-------------------

- MAINT: Remove unneeded dependency on obsolete zeit.content.video.asset

- ZON-4933: Add feedback question to genre source


3.39.3 (2018-10-05)
-------------------

- ZON-3312: Remove deprecated fields from ICommonMetadata, asset badges,
  aggregate comments, lead teaser assets


3.39.2 (2018-09-25)
-------------------

- HOTFIX: Don't break in liveblog version comparison for new articles

- FIX: Current FF throws JS exception when replacing a DOM node with an empty string


3.39.1 (2018-09-25)
-------------------

- FIX: We should not have changed the meaning of "no version in XML" from 2 to 3
  in 3.38.5


3.39.0 (2018-09-21)
-------------------

- ZON-3482: Use xml config instead of article for breaking news banner


3.38.5 (2018-08-06)
-------------------

- ZON-4773: Change default Liveblog version to 3


3.38.4 (2018-06-08)
-------------------

- SSL-160: Update test config for puzzleforms


3.38.3 (2018-05-31)
-------------------

- ZON-4720: Add checkbox to be able to show recent article comments first


3.38.2 (2018-05-29)
-------------------

- MAINT: Update to changed CP API


3.38.1 (2018-04-23)
-------------------

- ZON-4546: Add charlimit counter to division teaser

- ZON-4421: Put behind feature toggle `zeit.content.article.breakingnews-with-channel`


3.38.0 (2018-04-20)
-------------------

- ZON-4478: Add `findByline()` to genre source, adjusting the XML
  config format (remove display-frontend, change prose to byline)
  which is no problem as XSLT has been shutdown.


3.37.3 (2018-04-19)
-------------------

- ZON-4421: Add channels field to breaking news form


3.37.2 (2018-04-10)
-------------------

- BUG-837: Fix yet another browser edge case about whether the user
  has clicked outside of the editor, and thus it should be saved


3.37.1 (2018-04-09)
-------------------

- ZON-4581: Remove banner from product management form


3.37.0 (2018-04-03)
-------------------

- ZON-4476: Add "collapse" property for liveblog modules


3.36.0 (2018-03-22)
-------------------

- ZON-4541: Add new checkbox to hide ligatus recommendations


3.35.0 (2018-03-22)
-------------------

- SSL-159: Add puzzleform block


3.34.4 (2018-03-21)
-------------------

- ZON-4494: Style form field for twitter ressort tweet


3.34.3 (2018-03-15)
-------------------

- MAINT: Use generic, parameterized `checkin` worklist item instead of
  specialized `checkin_auto_lsc`


3.34.2 (2018-02-19)
-------------------

- TMS-156: No longer mark (tms-based) keywords required for articles
  (This reverts the requirements given in ZON-2881 and ZON-3305)


3.34.1 (2018-02-02)
-------------------

- MAINT: Remove Google News keyword suggestions, it's not used anymore


3.34.0 (2018-01-29)
-------------------

- Fix brown-bag release


3.33.1 (2018-01-26)
-------------------

- ZON-4296: Add version attribute to liveblog


3.33.0 (2018-01-19)
-------------------

- ZON-4289: Add constraint for news table box block


3.32.1 (2017-11-01)
-------------------

- MAINT: Extract grok-based element factory to zeit.edit


3.32.0 (2017-10-20)
-------------------

- ZON-4227: Implement mail module


3.31.0 (2017-10-19)
-------------------

- MAINT: Extract common modules to z.c.modules: rawtext, jobticker, quiz

- MAINT: Remove obsolete modules: audio, timeline, htmlblock

- MAINT: Remove obsolete video_2 setting


3.30.1 (2017-10-09)
-------------------

- ZON-4180: Use eta instead of countdown for scheduling


3.30.0 (2017-10-04)
-------------------

- ZON-3409: Move from remotetask to celery


3.29.0 (2017-09-28)
-------------------

- ARBEIT-116: Add box which is used as a profile_box in ZAR


3.28.4 (2017-09-27)
-------------------

- BUG-782: Be defensive about body structure and cursor positioning


3.28.3 (2017-09-14)
-------------------

- FIX: Add security declaration after introducing IArticle.header


3.28.2 (2017-09-08)
-------------------

- FIX: Fix typo in article edit view after introducing IArticle.body


3.28.1 (2017-09-07)
-------------------

- ZON-4206: Remove find_first_citation, replaced by `body.find_first(ICitation)`


3.28.0 (2017-09-07)
-------------------

- MAINT: Add `IArticle.body` and `header` convenience helpers


3.27.1 (2017-09-07)
-------------------

- ZON-3885: Remove ad placeholders


3.27.0 (2017-09-06)
-------------------

- ZON-4190: Add module for referencing a podcast


3.26.1 (2017-08-21)
-------------------

- ZON-4152: Add `commentsPremoderate` field to breaking news form

- ZON-4152: Set `is_amp` for breaking news articles


3.26.0 (2017-08-14)
-------------------

- ARBEIT-104: Add function to find first citation in article


3.25.2 (2017-08-08)
-------------------

- ZON-3677: Fill in default title from breaking news push payload template


3.25.1 (2017-08-07)
-------------------

- ARBEIT-86: Add citation layout source


3.25.0 (2017-08-07)
-------------------

- ZON-4006: Move mobile fields to their own form

- MAINT: Remove superfluous IEditable interface

- MAINT: Refactor markup for publishing


3.24.2 (2017-07-18)
-------------------

- BUG-133: Hide the whole "breaking news" info, not just the retract button
  when the banner doesn't match anymore

- BUG-500: Update to new dependency API


3.24.1 (2017-07-17)
-------------------

- MAINT: Remove obsolete feature toggle ``zeit.cms.rr-access``


3.24.0 (2017-07-05)
-------------------

- ZON-4054: Add marker interfaces for error pages


3.23.4 (2017-06-29)
-------------------

- BUG-743: Ignore empty imagegroups in IElementReferences


3.23.3 (2017-06-26)
-------------------

- MAINT: Remove obsolete banner control files (wrapper, ios-legacy)


3.23.2 (2017-06-22)
-------------------

- ZON-3950: Leave other workflow checkboxes alone when checking `urgent`


3.23.1 (2017-06-12)
-------------------

- ZON-3485: Reset local values when the referenced portraitbox is changed


3.23.0 (2017-06-09)
-------------------

- ZON-3810: Add IElementReferences Adapter


3.22.1 (2017-06-01)
-------------------

- Fix broken release


3.22.0 (2017-06-01)
-------------------

- ZON-3920: Disable FBIA if content is not free

- BUG-669: Set up portraitbox module properly


3.21.13 (2017-05-05)
--------------------

- FIX: unpublished volume reference does not trigger warning in AAD


3.21.12 (2017-03-15)
--------------------

- ZON-3792: Put ``access`` widget behind feature toggle ``zeit.cms.rr-access``


3.21.11 (2017-03-06)
--------------------

- BUG-669: Serialize empty local text in portraitbox module correctly


3.21.10 (2017-02-17)
--------------------

- Build release 3.21.9 again because it's broken.


3.21.9 (2017-02-16)
-------------------

- ZON-3485: Allow portraitbox to lack a reference and override fields locally.


3.21.8 (2017-01-31)
-------------------

- ZON-3430: Normalize quotation marks in teaser


3.21.7 (2017-01-31)
-------------------

- MAINT: Update to zeit.push API changes after parse.com shutdown


3.21.6 (2017-01-26)
-------------------

- ZON-3629: Add overscrolling option


3.21.5 (2017-01-18)
-------------------

- ZON-3576: Add commentsPremoderate property


3.21.4 (2016-10-19)
-------------------

- ZON-3323: Disable ``Article.is_amp`` if ``Article.access`` is not ``free``.


3.21.3 (2016-09-13)
-------------------

- Rename ``acquisition`` to ``access``.


3.21.2 (2016-09-12)
-------------------

- Make keywords optional in forms, too, not only validation.


3.21.1 (2016-09-07)
-------------------

- Add feature toggle `zeit.content.article.optional-keywords` to make keywords
  in articles optional. (ZON-3305)

- Only set main_image_variant_name on checkout when it's unset.


3.21.0 (2016-09-02)
-------------------

- Allow to drag volume in article editor. (ZON-3253)


3.20.7 (2016-08-22)
-------------------

- BUG-480: Assign default template on checkout when the current value is invalid

- ZON-2881: Make keywords required for Article (but not breaking news).


3.20.6 (2016-08-12)
-------------------

- Count `KEY_UNKNOWN` as dirty, since e.g. `-` or umlauts are mapped to this,
  thus they did not trigger a save previously.


3.20.5 (2016-08-09)
-------------------

- Implement fw-compat for mobile push notifications, since `parse` will be
  removed in 2017. (ZON-3213)


3.20.4 (2016-08-04)
-------------------

- Change default display mode for image blocks to "column-width".


3.20.3 (2016-08-01)
-------------------

- Fix ``available`` check for ``ImageDisplayModeSource`` and
  ``ImageVariantNameSource`` by adapting to ``IArticle``. (ZON-2927)

- Always edit keywords of an article in a separate fold. (ZON-2882)


3.20.2 (2016-07-26)
-------------------

- Extend product config to fix source configuration for testing. (ZON-3171)

- Adjust CSS for images to preview them more like Friedbert. (ZON-3216)

- Hide dropdown to choose variant name for Infographics, since Friedbert
  overwrites the variant name with `original`. (ZON-3216)


3.20.1 (2016-07-21)
-------------------

- Add acquisition attribute to CMS content


3.19 (2016-07-21)
-----------------

- Allow drag&drop for z.c.text objects (ZON-3018).

- Select default template/header_layout according to article
  interfaces (ZON-3088).


3.18.0 (2016-06-20)
-------------------

- Include first body image or video module as IHeaderArea.module (ZON-3088).

- Remove display mode from main image, make variant dependent on
  template/header (ZON-3088).


3.17.0 (2016-06-10)
-------------------

- Split image layout into two separate attributes to avoid combinatorial
  explosion (ZON-2927).


3.16.1 (2016-06-08)
-------------------

- Fix security declaration for IHeaderArea migration code.


3.16.0 (2016-06-08)
-------------------

- Implement separate editable area ``IHeaderArea`` to contain one
  module for the header (ZON-2871).


3.15.7 (2016-04-26)
-------------------

- Declare priority high for articles (ZON-2924).


3.15.6 (2016-04-20)
-------------------

- Make ``ICitation.attribution`` non-required (ZON-2962).


3.15.5 (2016-04-18)
-------------------

- Don't load Zope/UI specific ZCML in the model ZCML


3.15.4 (2016-04-15)
-------------------

- Fix styling of teaser image search button (BUG-146).


3.15.3 (2016-04-08)
-------------------

- Support separate facebook text for campus (ZON-2930).


3.15.2 (2016-04-07)
-------------------

- Add colorpicker for article teaser images (ZON-2898).


3.15.1 (2016-03-10)
-------------------

- Fix default value of infobox layout.


3.15.0 (2016-03-10)
-------------------

- Add ``layout`` to infobox block (ZON-2491).


3.14.2 (2016-03-10)
-------------------

- Improve wording (ZON-2826).


3.14.1 (2016-03-09)
-------------------

- Change ``is_instant_article`` default to False.


3.14 (2016-03-03)
-----------------

- Add a raw text module (ZON-2826).


3.13.0 (2016-02-16)
-------------------

- Support legacy ``<initial>`` paragraphs (BUG-320).


3.12.4 (2016-01-22)
-------------------

- Improve styling of social media form.


3.12.3 (2016-01-20)
-------------------

- Replace gocept.cache.method with dogpile.cache (ZON-2576).


3.12.2 (2015-12-17)
-------------------

- Update to zeit.push separating facebook texts (ZON-2397).


3.12.1 (2015-12-16)
-------------------

- Set instant_article default to true (ZON-2476).


3.12.0 (2015-12-02)
-------------------

- Add fields ``is_instant_article`` and ``is_amp`` (ZON-2476)


3.11.0 (2015-11-12)
-------------------

- Add block for referencing a quiz (ZON-2396).


3.10.1 (2015-10-29)
-------------------

- Simplify editor heading CSS, and make it apply to editor only (DEV-951).


3.10.0 (2015-09-12)
-------------------

- Add ``display_mode`` to ``z.c.article.edit.interfaces.IImage.layout``
  (DEV-923).


3.9.3 (2015-09-11)
------------------

- Prefill raw module with basic markup (DEV-936).


3.9.2 (2015-09-10)
------------------

- Add form for ``advertisement_title`` and ``advertisement_text`` (ZON-1340)


3.9.1 (2015-09-02)
------------------

- Add field `is_advertorial` to Cardstack. (DEV-892)

- Allow comparison of ``z.c.article.edit.interfaces.IImage.layout`` to a string
  for backward compatibility with ``zeit.web``. (DEV-923)


3.9.0 (2015-08-27)
------------------

- Unify checkin/correction wording (DEV-834).

- Add author block (DEV-913).

- Change ``z.c.article.edit.interfaces.IImage.layout`` to use an object,
  which has a ``image_variant`` property (DEV-923).


3.8.0 (2015-08-24)
------------------

- Add block for referencing a "card stack" (DEV-892).

- Add form for ``tldr`` fields (DEV-883).


3.7.0 (2015-07-24)
------------------

- Allow image groups as well as images in article body (DEV-882).

- Move ``template`` and ``layout`` settings to ``IArticle`` from
  ``zeit.magazin.interfaces.ITemplateSettings`` (DEV-801).
  * Product config moved from ``zeit.magazin:article-template-url``
    to ``zeit.content.article:template-url``.
  * Requires ZEO update due to new fields on ``Article``.


3.6.25 (2015-07-06)
-------------------

- Setting default channel has moved to zeit.cms (DEV-833).


3.6.24 (2015-06-25)
-------------------

- Remove feature toggle ``zeit.content.cp.automatic`` (DEV-832).


3.6.23 (2015-06-23)
-------------------

- Styling for z.c.image Variant UI (DEV-798).


3.6.22 (2015-06-11)
-------------------

- Bugfix for publish lightbox (DEV-22).


3.6.21 (2015-06-09)
-------------------

- Display validation errors in Lightbox / Popup during publish. (DEV-22)


3.6.20 (2015-05-18)
-------------------

- Save form when removing channel entries (BUG-254).


3.6.19 (2015-05-04)
-------------------

- Replace MochiKit $$ with jQuery, which is *much* faster in Firefox.

- Make ``browser.testing.create_block`` more resilient against timing issues.


3.6.18 (2015-04-28)
-------------------

- Update CheckBoxWidget API (DEV-745).


3.6.17 (2015-04-23)
-------------------

- Remove global push ``enabled`` setting (DEV-704).


3.6.16 (2015-04-15)
-------------------

- Undo 3.6.15, it was a misunderstanding.


3.6.15 (2015-04-15)
-------------------

- Add feature toggle ``zeit.push.social-form`` for social media form fields.


3.6.14 (2015-03-30)
-------------------

- Update content-to-module adapters to accept a position, since landing zones
  work with insert instead of add+updateOrder since zeit.edit-2.11 (DEV-53).


3.6.13 (2015-03-23)
-------------------

- Add ``commentsAllowed`` field to breaking news form (DEV-86).


3.6.12 (2015-03-18)
-------------------

- Adjust ReferenceFactory to new API of ElementFactory, which now accepts a new
  argument to insert at given position. (DEV-53)


3.6.11 (2015-03-13)
-------------------

- Use drag&drop sucess/failure API (DEV-60).


3.6.10 (2015-03-10)
-------------------

- Make search button styling work for centerpages, too (DEV-23).


3.6.9 (2015-02-16)
------------------

- Use readonly permission ``zeit.content.cp.ViewAutomatic`` (VIV-525).


3.6.8 (2015-01-12)
------------------

- Bugfix: Don't set has_last_semantic during publishing (VIV-534).


3.6.7 (2015-01-08)
------------------

- Extract body traverser mechanics to zeit.edit.


3.6.6 (2014-12-17)
------------------

- Fixed saving control when replacing text in editor.

- Update to API changes in zeit.cms, zeit.edit.


3.6.5 (2014-11-14)
------------------

- Set has_last_semantic for articles that contain liveblog blocks (VIV-534).

- Set default channels for CDS articles (VIV-547).

- Allow drag&drop of modules while in edit mode (VIV-405).

- When searching or replacing, ask to wrap around at end or beginning of text,
  resp. (VIV-10716).

- Fix validation rule that checks for unpublished images, which broke due to
  the introduction of reference objects for VIV-305.

- Use apply action from zope as hook instead of applyChanges hook that is not
  present in inline forms (VIV-516).

- Change shortcut for find/replace to Ctrl-Shift-F.


3.6.4 (2014-10-21)
------------------

- Don't display a retract button for breaking news banners that don't belong to
  the current article (VIV-532).

- Fix CSS bug that caused "new filename" input field to be wrongly positioned
  (VIV-530).

- Extract social media form to zeit.push (VIV-516).


3.6.3 (2014-10-07)
------------------

- Restrict access to auto-cp features to separate permission (VIV-525).


3.6.2 (2014-09-18)
------------------

- Add an empty main image to articles imported via CDS, so syncing the teaser
  image in the UI later on works (VIV-491).

- Fix position of SEO workflow checkbox (VIV-484).

- Fix CSS so the publish status of the teaser image is visible (VIV-504).

- Use trashcan icon for delete instead of cross (VIV-493).


3.6.1 (2014-09-03)
------------------

- Use feature toggle ``zeit.content.article.social-push-mobile`` (VIV-466).

- Use feature toggle ``zeit.content.cp.automatic``.

- Set channels to ressort if no channels are set yet (VIV-469).


3.6.0 (2014-08-29)
------------------

- Add UI for Channel selection and lead candidate (VIV-469, VIV-463).

- Add "push to mobile" to social media section, send breaking news on a
  separate parse.com channel (VIV-466).


3.5.3 (2014-08-27)
------------------

- Reactivate posting breaking news to Facebook.


3.5.2 (2014-07-30)
------------------

- Make create_article test helper do the same things that creating through the
  browser would do.


3.5.1 (2014-07-17)
------------------

- Move JS filename normalization to zeit.cms.

- Move JS character counter to zeit.cms.

- Change social media checkboxes default to unchecked.

- Make social media settings writeable only while checked out (VIV-451).


3.5.0 (2014-07-10)
------------------

- Add DAV-Property ``is_breaking`` to mark articles that were created as
  breaking news, so the frontend can do different things to them (WEB-319).

- Create separate banner file ``/eilmeldung/wrapper-banner`` when "Homepage"
  is enabled (WEB-318).

- Split off EditorHelper test baseclass, for reuse from other packages.


3.4.7 (2014-07-02)
------------------

- Temporarily removed posting of breaking news to Facebook as we cannot yet
  handle images correctly in that scenario.


3.4.6 (2014-06-20)
------------------

- Configure twitter/facebook main account for breaking news (VIV-416).


3.4.5 (2014-06-20)
------------------

- Reactivate social media section, implement Facebook (VIV-387, VIV-371).

- Reactivate breaking news feature (again), make title character limit soft,
  group checkboxes differently, add Twitter/Facebook (VIV-25).

- Shorten twitter text if it is too long (VIV-370).

- Add button to retract breaking news banner (VIV-418).

- Fix filename rewriting: handle multiple umlauts, remove special characters at
  the end of the name (VIV-409).


3.4.4 (2014-06-05)
------------------

- Fix icon position in sprite (VIV-359, VIV-407)


3.4.3 (2014-06-05)
------------------

- Restrict rewriting of filenames to articles and breaking news,
  don't accidentally rewrite image filenames, for example.


3.4.2 (2014-06-04)
------------------

- Disable breaking news feature for the time being (again).


3.4.1 (2014-06-03)
------------------

- Deactivate social media section until Facebook is implemented (VIV-387).


3.4.0 (2014-06-03)
------------------

- Fix save of WhYSIWYG editor when the user clicks on an input field (VIV-395)

- Reactivate breaking news feature; add max length to title field (VIV-25).

- Add social media section (VIV-387 / VIV-396).

- Add block for referencing an external Liveblog (WEB-246).

- Rewrite filenames to match the SEO expectations while typing (VIV-338).

- Register and cleanup keydown event handlers properly (VIV-381).

- Remove iPad/Desktop tabs from inline preview (VIV-393).


3.3.1 (2014-05-13)
------------------

- Disable breaking news feature for the time being.


3.3.0 (2014-05-09)
------------------

- Add separate form for breaking news that only requires minimal input and
  publishes automatically (VIV-367).

- Add "SEO optimized" workflow checkbox (VIV-329).

- Remove unicode line breaks when pasting (WEB-299).


3.2.1 (2014-04-28)
------------------

- Fix breaking editor on wysiwyg save after autosave.


3.2.0 (2014-04-22)
------------------

- Reload only those body blocks that were edited, not the whole body area
  (VIV-11795).

- Display Google news keyword suggestions (VIV-359).


3.1.5 (2014-03-14)
------------------

- Fix incomplete API change to using references as Article.main_image
  (VIV-305).


3.1.4 (2014-03-10)
------------------

- Position cursor at the click position when entering editable mode
  (VIV-11795).

- Make alt/title overridable in main article image too, not only in image
  blocks in the body (VIV-305).


3.1.3 (2014-02-18)
------------------

- Always generate block UUIDs on checkout (even when they might not be needed),
  since relying on a browser request to trigger this is too fragile (FRIED-23).


3.1.2 (2014-02-10)
------------------

- Use Fanstatic instead of zc.resourcelibrary (VIV-296).


3.1.1 (2014-01-20)
------------------

- Display "Deeplink URL" field (VIV-270).

- Implement EditableBody.values() so that it works without UUID attributes,
  this alleviates concurrency problems noted in zeit.frontend (FRIED-23).


3.1.0 (2014-01-07)
------------------

- Configure layouts for image and video blocks via external XML file (VIV-249,
  VIV-250).

- Implement block with title and (restricted) HTML contents (VIV-245).

- Add IZONArticle marker interface so we can show some settings only for
  non-ZMO articles (VIV-252).

- Fix bug from 3.0.12: Have ``title`` and ``alt`` attributes survive checkin
  (VIV-157).


3.0.12 (2013-11-15)
-------------------

- Allow setting ``title`` and ``alt`` attribute on image blocks (VIV-157).


3.0.11 (2013-10-02)
-------------------

- Make use of webdriver (#12573).

- Update to lxml-3.x (#11611).

- Fix bug with losing whitespace by properly configuring the lxml.objectify
  parser (#12016).


3.0.10 (2013-10-01)
-------------------

- Fix styling of rel="nofollow" checkbox on Mac (VIV-104).


3.0.9 (2013-09-24)
------------------

- Support rel="nofollow" for links in the article body (VIV-104).

- Display ``breadcrumb_title`` field (VIV-105).

- Handle inserting links across tags (#12558).

- Display proper name for "last published by" status.

- Add genre to XML references (WEB-35)

- Remove unittest2, we have 2.7 now


3.0.8 (2013-08-27)
------------------

- Add "genre" field for articles (#12725).

- Display "Mobile URL" field (#12749).

- Display overlay with edit button for images in repository mode, too (#12707).


3.0.7 (2013-08-14)
------------------

- Update to Python-2.7 and ZTK-1.1.5 (#11005).


3.0.6 (2013-07-11)
------------------

- Make keywords optional for the time being.


3.0.5 (2013-07-10)
------------------

- Require at least three keywords, not just one.


3.0.4 (2013-07-08)
------------------

- Include timezone when rendering last published date.

- Prevent editor from saving when nothing has changed to make UI more
  responsive. (#12555)


3.0.3 (2013-07-01)
------------------

- Display last_semantic_change with the user's timezone (#12396).

- Decouple character limit during entry of text from validation during
  check-in of article (#12462).

- Prevent accidental back button events when pressing backspace (#12461).

- Check if link in link editor has protocol, else add http. (#12557)


3.0.2 (2013-05-29)
------------------

- Newly created articles now have a last_semantic_change value set (#12398).


3.0.1 (2013-05-16)
------------------

- Remove obsolete content-editable workaround. This prevents text from being
  deleted accidentally after pasting (#12385).


3.0 (2013-04-23)
----------------

- Support advertorial hack and print byline (#11973, #12246)

- Support colorbox links (#11981)

- RAW-Block uses HTML parser and converts given HTML to XML now (#12267).

- Accomodated article to cope for the changed videos: videos are now full CMS
  objects and moved to zeit.content.video (for #8996)

- Articles are created without an addform now. A temporary file is created in
  DAV and automatically checked out. Upon checkin the temporary file is updated
  and renamed to the name given during editing the checked out article (#8080).

- Enable UI for author references (#7441, #7333).
- New Image layout and selectable layout for main_image(#12029)


2.9.6 (unreleased)
------------------

- Cleaned up dependencies on zope.app packages.


2.9.5 (2012-03-06)
------------------

- Update to new ConversionStep API. (#10251)


2.9.4 (2011-12-01)
------------------

- Update to use etree instead of objectify for HTML conversion/wysiwyg
  (via #10027).


2.9.3 (2011-11-24)
------------------

- Fix ordering issue with images: let the PageBreakStep before the
  XMLImageStructureStep because XMLImageStructureStep does not expect an extra
  level of tags (that is it gets confused by `<division><p><image>`).


2.9.2 (2011-06-20)
------------------

- Fix the usage of the product id (for #9033)

- Remove <p>, <intertitle> etc. from the module library (#9923).

- Removed 'preview' and 'live' links from the workflow form (#10660).

- Updated styling of items in the ObjectSequenceWidget (#10666).


2.9.1 (2010-08-09)
------------------

- Fix tests after product config changes in zeit.cms (#7549).


2.9.0 (2010-06-09)
------------------

- Hide new author_references field.


2.8.3 (2010-06-02)
------------------

- Extract all text content from the body (#7359).


2.8.2 (2010-04-13)
------------------

- Using versions from the ZTK.

- Rezensionsinformationen lassen sich wieder(?) bearbeiten (#7075)


2.8.1 (2010-03-10)
------------------

- Change the way asset interfaces are registered. This fixes isolation problems
  during tests (#6712).

- Fix tests after decentral syndication was disabled by default (#6878).

- Option "meistgelesene Artikel" entfernt (#6878).


2.8.0 (2009-12-18)
------------------

- NoAutomaticMetadataUpdate entfernt.
- Absätze werden wieder korrekt gezählt (#6197).
- Nur Artikel mit der product_id 'ZEDE' haben standardmäßig den Haken 'Export
  zum Tagesspiegel' gesetzt (#6184).


2.7.2 (2009-09-21)
------------------

- Keine Abhängigkeit zu zope.app.twisted mehr.


2.7.1 (2009-09-17)
------------------

- CDS-Pfade für Tag/Montag mit führender Null.


2.7 (2009-09-09)
----------------

- Es wird nur noch genau der veröffentlichte Artikel in die CDS exportiert und
  keine Artikel mehr, die durch Workflowabhängigkeiten veröffentlicht wurden.


2.6.1 (2009-09-05)
------------------

- Tests für Änderungen an zeit.cms angepasst.


2.6 (2009-08-26)
----------------

- Weitere Ersetzungsmöglichkeiten für den CDS-Import-Pfad: `real_year`,
  `real_month`, `real_day`, `ressort` und `sub_ressort`. Dies ermöglicht die
  neue Verzeichnisstuktur (#6045).


2.5 (2009-08-21)
----------------

- Templates für Artikel gibt es nicht mehr.

- Tests repariert (#5946).

2.4 (2009-08-11)
----------------

- Banner-Feld entfernt (nach zeit.cms gewandert, #5931)

2.3 (2009-08-03)
----------------

- »RemainingFields« benutzten, damit Erweiterungen an den Standardmetadaten
  korrekt angezeigt werden.

- Sicherstellen, dass Seitenumgbrüche nicht »None« als Teaser haben.

2.2 (2009-07-23)
----------------

- Adapter zur Volltextindizierung hinzugefügt.

- Abhängigkeiten zu anderen Paketen reduziert.

- CDS-Import von Artikeln mit ungültigem Ressort korrigiert, nach dem ungültige
  Ressorts jetzt im CMS angezeigt werden.

2.1 (2009-06-18)
----------------

- Ein Artikel kann eine CenterPage als sein Layout referenzieren (#5491).

- Tests für Hashed-Resources angepasst.

- CDS beim import weniger aggresiv (#5525).

- Nicht veröffentlichte CDS-Artikel werden jetzt in der Nacht gelöscht.

2.0 (2009-06-08)
----------------

- Divisions/Seitenumbrüche (#4707).

- TypeGrokker zum registrieren des Artikels verwendet.

1.7.9 (2009-05-28)
------------------

- Abhängigkeiten zu zeit.wysiwyg, zeit.content.infobox,
  zeit.content.portraitbox und zeit.content.gallery hinzugefügt.

1.7.8 (2009-05-27)
------------------

- CDS: Wird ein Artikel ein weiteres mal geliefert, und wurde er im CMS
  geändert, ist dies jetzt eine Warnung und kein Fehler mehr.

1.7.7 (2009-05-20)
------------------

- Aus der CDS importierte Artikel werden beim Veröffentlichen nicht mehr in die
  CDS exportiert.

1.7.6 (2009-05-18)
------------------

- Jetzt wirklich keine eigenen Translationdomain mehr.

1.7.5 (2009-05-18)
------------------

- »Zum Tagesspiegel exportieren« im Workflowtab ist jetzt initial »an«.

1.7.4 (2009-05-17)
------------------

- »Zum Tagesspiegel exportieren« jetzt im Workflowtab.

- Unterstützung für Änderungen aus zeit.cms 1.20.1.

1.7.3 (2009-05-15)
------------------

- Anpassungen für zeit.cms 1.20

- Alle ``test.py`` nach ``tests.py`` umbenannt.

- Keine eigene Translationdomain mehr, Übersetzungen via zeit.locales.

1.7.2 (2009-05-07)
------------------

- Wenn DAV-Propertys aus dem XML geladen werden, werden leere Propertys
  ignoriert. Das löst das "None" bei Autoren.

1.7.1 (2009-05-07)
------------------

- CDS importiert weiter, wenn eine Datei kein gültiges XML beinhaltet.

1.7 (2009-05-07)
----------------

- Content-Drehscheibe: Kommt ein veränderter Artikel mit der selben UUID noch
  mal aus der CDS, wird er im CMS überschrieben, wenn er noch nicht verändert
  wurde.

- Import-Pfade für die CDS sind konfigurierbar.

- Artikel, die aus der CDS importiert wurden, werden nach 2 Tagen gelöscht,
  wenn sie bis dahin nicht veröffentlich wurden.

1.6.2 (2009-04-22)
------------------

- Default der paragraphsperpage von 6 auf 7 geaendert.

1.6.1 (2009-04-17)
------------------

- Tests für ``urn:uuid:...`` Format angepasst.

1.6 (2009-04-17)
----------------

- Artikel in die Content-Drehscheibe (Tagesspiegel) exportieren (#4968)

- Import von Artikeln aus der Content-Drehscheibe. Diese werden mit einem
  Tagesspiegel-Icon versehen (#4967).


1.5.13 (2009-02-11)
-------------------

- Aktualisiert auf asynchrone Updates.

1.5.12 (2009-02-09)
-------------------

- TagesNL per default an.

1.5.11 (2008-12-12)
-------------------

- Entities in Textareas werden richtig angezeigt (nur Testbrowser).

1.5.10 (2008-11-20)
-------------------

- Kein Test-Extra
- Extra SecurityPolicy

1.5.9 (2008-11-17)
------------------

- Anpassungen für zeit.cms 1.3

1.5.8 (2008-11-10)
------------------

- Anpassungen für zeit.cms 1.2.6

1.5.7 (2008-10-24)
------------------

- Bearbeiten von Rezensionen klarer gemacht (bug #4437).
- Anpassungen für zeit.cms 1.2.4
- Rezensionsview beim checkin/checkout stabil halten.

1.5.6 (2008-10-13)
------------------

- Tests sind jetzt unabhängig vom Standardwert des Copyrights bei Bildern.

1.5.5 (2008-10-01)
------------------

- Article ist ein redaktioneller Inhalt.

1.5.4 (2008-10-01)
------------------

- Anpassungen an zeit.cms 1.2

1.5.3 (2008-08-26)
------------------

- Tests nochmal repariert.

1.5.2 (2008-08-26)
------------------

- Aktualisiert für zope.app.form 3.6.0 und zeit.cms 1.1.6

1.5.1 (2008-08-12)
------------------

- Aktualisiert für zeit.cms 1.1.5

1.5 (2008-07-29)
----------------

- "Kommentare erlaubt" ist in den Kern gewandert.

1.4 (2008-06-26)
----------------

- DailyNL in den Standard-Metadaten (bug #4307).

1.3 (2008-06-23)
----------------

- Tests auf zeit.cms 0.9.22 angepasst.

1.2 (2008-06-16)
----------------

- Asset-View refaktoriert: Verwenden des Asset-Supports aus dem Core.
- "Kommentare zusammenfassen" (bug #3734).

1.1 (2008-05-29)
----------------

- Compatible with zeit.cms 0.9.16


1.0 (2008-05-26)
----------------

- Removed special "syndicated in" which is done via relations now.
- Removed special syndication log, which will be done via zeit.objectlog.

0.9.14 (2008-05-20)
-------------------

- first release after moving article out of zeit.cms core


zeit.content.author changes
===========================

2.9.8 (2019-03-29)
------------------

- PERF: Don't grok browser packages by default


2.9.7 (2019-02-13)
------------------

- ZON-5047: Add occupation text field


2.9.6 (2019-01-25)
------------------

- FIX: Mark "duplicate" notification translatable


2.9.5 (2019-01-09)
------------------

- ZC-84: Add SSO-Id to author object


2.9.4 (2018-09-05)
------------------

- TMS-214: Remove dependency to zeit.solr (should have happened in 2.9.3)


2.9.3 (2018-08-14)
------------------

- TMS-214: Switch to elasticsearch for duplicate author detection


2.9.2 (2018-06-27)
------------------

- FIX: Use False as enable_feedback default in property as well


2.9.1 (2018-06-27)
------------------

- FIX: Use False as enable_feedback default


2.9.0 (2018-05-23)
------------------

- ZON-4699: Add enable_followpush field

- ZON-4258: Add enable_feedback field


2.8.2 (2018-01-29)
------------------

- HOTFIX: Don't try to copy authors during repository->repository copying


2.8.1 (2018-01-26)
------------------

- BUG-834: Fix copying to freetext author property on create


2.8.0 (2017-10-04)
------------------

- ZON-3409: Move from remotetask to celery


2.7.8 (2017-07-18)
------------------

- BUG-500: Update to new dependency API


2.7.7 (2017-05-22)
------------------

- BUG-562: Base author images implementation on the default IImages
  implementation, so all the mechanics works out properly

- BUG-708: Copy to freetext on create too, since that does not send modified


2.7.6 (2017-02-16)
------------------

- MAINT/PERF: Only publish an author object along with its article if
  it's not published yet


2.7.5 (2016-12-29)
------------------

- MAINT: Remove superfluous field `display_name` from context-free AddForm.


2.7.4 (2016-12-05)
------------------

- FIX: Use a proper schema field for ``display_name``, so
  ObjectPathProperty can return a missing value if nothing was set.


2.7.3 (2016-09-07)
------------------

- FIX: Adjust interface for ``Author`` references to expect the container for
  the ``Author`` reference rather the ``Author`` itself.


2.7.2 (2016-09-02)
------------------

- Fix brown-bag 2.7.1 and implement IXMLReference 'related' properly.


2.7.1 (2016-09-02)
------------------

- Change IXMLReference name to 'related' for referencing authors in articles.


2.7.0 (2016-04-07)
------------------

- Add ``IImages.fill_color`` (ZON-2898).


2.6.1 (2016-02-25)
------------------

- Copy author references to old freetext field for all content types.


2.6.0 (2016-02-12)
------------------

- Retrieve author images via standard interface instead of attribute.


2.5.1 (2016-02-03)
------------------

- Remove max length from biography questions (ZON-2717).


2.5.0 (2015-12-07)
------------------

- Add properties ``twitter``, ``facebook``, ``instagram``, ``summary``,
  ``favourite_content``, ``topiclink_label_1`` / ``topiclink_url_1`` 1 to 3,
  and ``bio_questions`` (ZON-2461).
  * New config file: ``/data/author-biography-questions.xml``, for
    ``zeit.content.author:biography-questions``


2.4.0 (2015-08-27)
------------------

- Add property ``biography`` and reference for overriding it (DEV-913).


2.3.1 (2015-06-18)
------------------

- Don't break display of old authors without ``display_name`` (BUG-265).


2.3.0 (2015-05-19)
------------------

- Upgrade column teaser image to a generic image group (ZON-1569).


2.2.3 (2015-02-26)
------------------

- Setup a column teaser image (ZON-1465).


2.2.2 (2015-01-29)
------------------

- Allow suppressing errors that are due to missing metadata files (VIV-629).


2.2.1 (2014-07-17)
------------------

- Use <div class="inline-form"> instead of a nested <form> for reference
  details (VIV-428).


2.2.0 (2014-06-16)
------------------

- Populate ``author`` attribute of references with author objects instead of
  freetext authors (VIV-410).


2.1.3 (2014-03-17)
------------------

- Add missing security handling for XMLReferenceUpdater (VIV-278).


2.1.2 (2014-03-10)
------------------

- Include authorship information in XMLReference to ICommonMetadata (VIV-278).


2.1.1 (2014-02-10)
------------------

- Use Fanstatic instead of zc.resourcelibrary (VIV-296).


2.1.0 (2014-01-20)
------------------

- References to authors can now carry location information (VIV-273).


2.0.3 (2013-10-01)
------------------

- Validate VGWort code format (#12615).


2.0.2 (2013-09-24)
------------------

- Remove unittest2, we have 2.7 now


2.0.1 (2013-07-01)
------------------

- New field: external author (#12460).


2.0 (2013-04-23)
----------------

- Remove the last author from freetext when the last author is removed from
  referenced authors (#9918).
- New field: Community-Profile (#10670).


0.4.0 (2011-11-13)
------------------

- Fix equality/comparison for authors (#9391).


0.3.0 (2011-06-20)
------------------

- Added ``vgwortcode`` (#9198)


0.2.1 (2011-06-07)
------------------

- Fix brown-bag 0.2.0: ZCML files were missing


0.2.0 (2011-06-02)
------------------

- Fix rendering of a folder listing with authors in it (#8763).
- Add fields ``email`` and ``status`` (#8953).


0.1.1 (2010-08-09)
------------------

- Fix tests after product config changes in zeit.cms (#7549).


0.1.0 (2010-06-09)
------------------

* first release


zeit.content.cp changes
=======================

3.29.0 (2019-04-16)
-------------------

- ZON-4655: Add RSS Automic Area


3.28.4 (2019-03-29)
-------------------

- PERF: Don't grok browser packages by default


3.28.3 (2019-03-05)
-------------------

- BUG-1065: Make header image variant for editor display configurable


3.28.2 (2019-02-19)
-------------------

- FIX: Be defensive about jobticker module that has not (yet) set a feed


3.28.1 (2019-02-06)
-------------------

- BUG-1045: Allow specifying a uniqueId for prewarming


3.28.0 (2019-02-05)
-------------------

- ZON-2932: Add parameters to embed module form


3.27.5 (2019-02-04)
-------------------

- BUG-1045: Add icon for pre-warm cache menu item


3.27.4 (2019-02-01)
-------------------

- BUG-1045: Add celery task to pre-warm DAV cache


3.27.3 (2019-01-24)
-------------------

- ZON-4896: Exclude inline gallery from elasticsearch area results,
  prevent dragging them as teasers


3.27.2 (2018-11-20)
-------------------

- ZON-4950: Create a rawtext module when a text object is dropped on an area

- MAINT: Use completely empty template to create new CPs


3.27.1 (2018-10-08)
-------------------

- ZON-3312: Move teaser image form field to metadata tab instead of separate asset tab


3.27.0 (2018-10-05)
-------------------

- ZON-4801: Add not-equal operator and content type to custom query

- ZON-3312: Remove obsolete fields `text_color` and `overlay_level` from ITeaserBlock

- OPS-309: Remove obsolete CP2009 bw-compat code


3.26.1 (2018-09-17)
-------------------

- ZON-4820: Skip TMS enrich for CPs


3.26.0 (2018-09-05)
-------------------

- ZON-4894: Remove solr support


3.25.4 (2018-08-14)
-------------------

- TMS-214: Move solr default result fields here from `zeit.find`


3.25.3 (2018-06-22)
-------------------

- MAINT: Add `access` as custom query condition


3.25.2 (2018-06-13)
-------------------

- FIX: Tweak landing zone styling for referenced cp on auto area


3.25.1 (2018-06-12)
-------------------

- FIX: Remove None uuids from ES query


3.25.0 (2018-06-11)
-------------------

- HOTFIX: Fix security declarations

- TMS-227: Implement dynamic input widget and ES query construction for
  different query conditions


3.24.2 (2018-06-08)
-------------------

- TMS-231: Really filter duplicates in TMS content query
  (we have to retrieve more results if too many were dropped as duplicate)


3.24.1 (2018-06-06)
-------------------

- TMS-234: Support comments and adding a title to the filter.json file

- MAINT: No longer rewrite ES raw queries on save


3.24.0 (2018-05-29)
-------------------

- TMS-226: Add `published: true` condition to all ES queries

- TMS-219: Switch "channel" queries to ES

- MAINT: Move source out of interfaces to prevent circular import with z.c.article.interfaces


3.23.3 (2018-05-22)
-------------------

- TMS-231: Filter duplicates in TMS content query


3.23.2 (2018-05-18)
-------------------

- FIX: Resolve TMS/ES results properly


3.23.1 (2018-05-14)
-------------------

- TMS-162: Update to API changes in zeit.cms


3.23.0 (2018-04-17)
-------------------

- ZON-4532: Remove feature toggle `zeit.retresco.tms`


3.22.2 (2018-03-20)
-------------------

- TMS-205: Specify filter.json as URL instead of uniqueId


3.22.1 (2018-03-20)
-------------------

- TMS-205: Parse filter.json directly instead of using an additional XML config file


3.22.0 (2018-03-19)
-------------------

- TMS-165: Support complex elasticsearch json queries


3.21.2 (2018-02-28)
-------------------

- TMS-38: Show topicpage filter field in UI


3.21.1 (2018-02-27)
-------------------

- TMS-162: Update to API changes in zeit.cms, zeit.retresco


3.21.0 (2018-02-05)
-------------------

- TMS-38: Implement configuring a filter for topicpage auto areas


3.20.0 (2017-11-08)
-------------------

- BUG-802: Introduce marker interface ``ISearchpage``


3.19.2 (2017-11-01)
-------------------

- MAINT: Update to simplified module registration API


3.19.1 (2017-10-27)
-------------------

- FIX: Add CP IBlock interface back to jobticker module


3.19.0 (2017-10-20)
-------------------

- ZON-4227: Implement mail module


3.18.1 (2017-10-19)
-------------------

- FIX: quiz serialization is historically different on CPs and articles


3.18.0 (2017-10-19)
-------------------

- MAINT: Extract common modules to z.c.modules: rawtext, jobticker, quiz

- MAINT: Remove free teaser model classes, they've been unused since 3.1.0

- MAINT: Remove obsolete modules: fullgraphical, audio, video, frame


3.17.0 (2017-10-04)
-------------------

- ZON-3409: Move from remotetask to celery


3.16.3 (2017-09-28)
-------------------

- MAINT: Raise an error if centpage references itself in an area


3.16.2 (2017-09-18)
-------------------

- FIX: Use first default layout for automatic cps as well


3.16.1 (2017-09-14)
-------------------

- FIX: Stop searching for default teaser layout on the first one we find


3.16.0 (2017-09-07)
-------------------

- ZON-4206: Use `IContainer.filter_values` instead of our own `select_modules`


3.15.0 (2017-09-06)
-------------------

- ZON-4190: Add module for referencing a podcast


3.14.1 (2017-09-04)
-------------------

- ARBEIT-108: Move jobbox source to zeit.cms, it is used by both cp and article


3.14.0 (2017-08-24)
-------------------

- ARBEIT-108: Add Jobbox with different feeds as module


3.13.9 (2017-08-21)
-------------------

- ARBEIT-104: Show citation text for quote teasers in cp editor


3.13.8 (2017-08-07)
-------------------

- MAINT: Remove unused RSS block and feed caching functionality

- MAINT: Remove superfluous IEditable interface

- MAINT: Use new method for publishing


3.13.7 (2017-07-18)
-------------------

- BUG-500: Update to new dependency API


3.13.6 (2017-06-09)
-------------------

- ZON-3810: Use IElementReferences instead of ICMSContentIterable


3.13.5 (2017-03-30)
-------------------

- ZON-3840: Make `all_modules` rule glob lazy, it's both expensive to
  compute and only rarely actually needed


3.13.4 (2017-02-15)
-------------------

- ZON-2855: Put CP body metadata update behind feature toggle
  ``zeit.content.cp.update_metadata`` (which is OFF by default)


3.13.3 (2017-02-15)
-------------------

- ZON-2855: Remove XSLT-support for autopilots (.lead files)


3.13.2 (2017-02-15)
-------------------

- MAINT: Remove obsolete free teaser guard on checkin (see 3.1.0)


3.13.1 (2016-12-07)
-------------------

- ZON-3441: Make requiring lead_candidate configurable on the layout
  and the area.


3.13.0 (2016-12-06)
-------------------

- BUG-585: Remove support for XSLT-based RSS feeds.


3.12.1 (2016-10-05)
-------------------

- Be defensive about broken content in IRenderedXML.


3.12.0 (2016-09-28)
-------------------

- ZON-3163: Add ability to use Elasticsearch for Autopilot.


3.11.1 (2016-09-26)
-------------------

- Update to `zeit.cms >= 2.90`.


3.11.0 (2016-09-14)
-------------------

- ZON-3236: Add ISitemap interface (will be manually applied).


3.10.3 (2016-09-02)
-------------------

- Ignore retresco feature toggle for zeit.web.


3.10.2 (2016-08-24)
-------------------

- Remove topic pages from sitecontrol, since sitecontrol is no more.


3.10.1 (2016-08-23)
-------------------

- Hide automatic area source TMS behind feature toggle ``zeit.retresco.tms``.


3.10.0 (2016-08-10)
-------------------

- Extract query logic from AutomaticArea into separate IContentQuery
  classes (ZON-3227).

- Implement IContentQuery for TMS topicpages (ZON-3120).


3.9.1 (2016-08-03)
------------------

- Register a specific UnknownBlock for CPs that has all expected
  attributes like `visible`.


3.9.0 (2016-04-29)
------------------

- Add ``animate`` property to IHeaderImage (ZON-3027).


3.8.0 (2016-04-28)
------------------

- Add rule globs ``centerpage`` and ``all_modules`` (ZON-3036).


3.7.6 (2016-04-28)
------------------

- Improve error message for teaser layout configuration errors.


3.7.5 (2016-04-27)
------------------

- Fix bug in region-config, set area.kind first so constraint checking works.


3.7.4 (2016-04-26)
------------------

- Consider publish priority in publish popup.


3.7.3 (2016-04-26)
------------------

- Declare priority high (and homepage) for centerpages (ZON-2924).

- Make cpextra source support ``available``.


3.7.2 (2016-04-18)
------------------

- Don't load Zope/UI specific ZCML in the model ZCML


3.7.1 (2016-04-13)
------------------

- Remove teasered content from references index (ZON-2764).


3.7.0 (2016-04-07)
------------------

- Move ``hex_literal`` to zeit.cms (ZON-2898).

- Make markup module alignable (ZON-2905).


3.6.0 (2016-03-21)
------------------

- Make arbitrary area attributes configurable via region-config (ZON-2931).


3.5.5 (2016-03-10)
------------------

- Improve wording (ZON-2826).


3.5.4 (2016-03-03)
------------------

- Add a rawtext block which allows references of plain text
  or plain text input form (ZON-2826)


3.5.3 (2016-02-22)
------------------

- AutomaticArea delegates only IArea properties, preventing unwanted
  interactions e.g. with zope.interface.


3.5.2 (2016-02-03)
------------------

- Display list representation title for non-ICommonMetadata objects in teaser
  modules (ZON-2613).


3.5.1 (2016-01-20)
------------------

- Replace gocept.cache.method with dogpile.cache (ZON-2576).


3.5.0 (2015-12-10)
------------------

- Deprecate homepage snapshot image (ZON-2429).


3.4.0 (2015-11-12)
------------------

- Change ``quiz`` block to store just an ID (new-style quizzes), not a
  reference to an (old-style) quiz content object (ZON-2396).


3.3.3 (2015-11-06)
------------------

- Be a little lazier with context value retrieval (ZON-2159).


3.3.2 (2015-10-30)
------------------

- Add action to materialize an automatic block (DEV-934).


3.3.1 (2015-10-08)
------------------

- Be more defensive about accessing content properties in auto areas.


3.3.0 (2015-10-05)
------------------

- Keep manually added blocks when enabling ``automatic`` (DEV-934).


3.2.3 (2015-09-30)
------------------

- Fully remove any "migration warning" between CP2009/CP2015; always raise
  CheckinCheckoutError (ZON-2239).


3.2.2 (2015-09-28)
------------------

- Add checkbox to update semantic change to workflow form (DEV-834).


3.2.1 (2015-09-13)
------------------

- Delegate select_modules first, otherwise subclassing AutomaticArea breaks it.


3.2.0 (2015-09-13)
------------------

- Introduce helper method ``IArea.select_modules(*interfaces)``.


3.1.7 (2015-09-12)
------------------

- Make force_mobile_image non-required, it breaks materialize_filled_values
  for some reason.


3.1.6 (2015-09-12)
------------------

- Add TeaserBlock fields (force_image_mobile etc.) to AutoBlock, too.


3.1.5 (2015-09-11)
------------------

- Add new default sort order date-last-published-semantic for automatic areas
  (DEV-944).


3.1.4 (2015-09-10)
------------------

- Write metadata that auto areas maybe delegate to the referenced CP into XML,
  since 7val needs it.


3.1.3 (2015-09-02)
------------------

- Add field `is_advertorial` to Cardstack. (DEV-892)

- Display title of the kind rather kind itself, so the information is more user
  friendly. (DEV-933)


3.1.2 (2015-08-27)
------------------

- Display kind for region/area again (DEV-807).


3.1.1 (2015-08-26)
------------------

- Update ITeaserBlockLayout interface, needed for security declaration (DEV-925).


3.1.0 (2015-08-24)
------------------

- Add ``force_mobile_image`` field to TeaserBlock (DEV-894).

- Add ``text_color`` and ``overlay_level`` to TeaserBlock (DEV-893).

- New module type ``cardstack``, ``zeit.content.cp.interfaces.ICardstackBlock``
  with property ``card_id`` (DEV-892).

- New add menu entry ``Storystream`` (DEV-884).

- Allow disabling/enabling teaser layouts using the CP type (DEV-884).

- Remove UI for in-place teaser editing, but keep the free teaser classes and
  handling for bw-compat (DEV-852).

- Reorder library tabs (DEV-853).

- Order r/a/m library according to their config files (DEV-853).


3.0.1 (2015-08-18)
------------------

- Fix bug in `isAvailable` treatment for teaser layouts.


3.0.0 (2015-08-18)
------------------

- Prevent manual checkout of wrong cp type (DEV-911).

- Implement IRenderedXML for new centerpages.


3.0.0b31 (2015-08-13)
---------------------

- Don't have TeaserBlock inherit from a content type, just its behaviour.


3.0.0b30 (2015-08-10)
---------------------

- Optimize: Cache areas for duplicate detection instead of parsing them again
  and again (ZON-2043).

- Optimize: Cache parsed objects of teaser block layout source (ZON-2046).


3.0.0b29 (2015-08-05)
---------------------

- Prevent any automated checkout of wrong cp type (2009/2015).


3.0.0b28 (2015-08-04)
---------------------

- Prevent checkout of wrong cp type (2009/2015) during publish.


3.0.0b27 (2015-08-03)
---------------------

- Handle errors raised by solr.


3.0.0b26 (2015-07-27)
---------------------

- Fix security declaration (DEV-850).


3.0.0b25 (2015-07-27)
---------------------

- Duplicate detection now also takes into account manual teasers below the
  current area (DEV-850).

- Don't close popups when clicking "save" button (DEV-108).


3.0.0b24 (2015-07-23)
---------------------

- Add ``visible_mobile`` field to R/A/M (DEV-845).

- New module type ``frame``, ``zeit.content.cp.interfaces.IFrame`` with
  property ``url`` (DEV-848).

- Add ``supertitle`` to ``IBlock``.

- New module type ``headerimage``,
  ``zeit.content.cp.interfaces.IHeaderImageBlock`` with property ``image``
  (DEV-846).

- New module type ``markup``, ``zeit.content.cp.interfaces.IMarkupBlock``
  with property ``text``, uses Markdown for editing (DEV-847).

- Ignore content that cannot be found for automatic/solr queries.


3.0.0b23 (2015-07-20)
---------------------

- Create RenderedXML for feed of auto-cps without evaluating automatic areas
  again, which cuts the render time in half (BUG-287).


3.0.0b22 (2015-07-07)
---------------------

- Don't keep on trying to retrieve additional teasers when there simply are no
  more (BUG-287).


3.0.0b21 (2015-07-06)
---------------------

- Make sort order of automatic areas configurable (DEV-836).

- Handle unicode uniqueIds.


3.0.0b20 (2015-06-25)
---------------------

- Remove feature toggle ``zeit.content.cp.automatic`` (DEV-832).


3.0.0b19 (2015-06-23)
---------------------

- Use separate config file for channels (DEV-634).


3.0.0b18 (2015-06-23)
---------------------

- Prefill IArea.read_more_url from referenced_cp if present, add image field
  (DEV-824).


3.0.0b17 (2015-06-18)
---------------------

- Put read_more and background_color back on IBlock, legacy content still needs
  it (DEV-822).


3.0.0b16 (2015-06-18)
---------------------

- Make overflow work across multiple areas (DEV-759).

- Remove overflow after drag&drop when order doesn't match anymore (DEV-759).

- Overflow excessive blocks when changing block_max (DEV-687).

- Retrieve more teasers on demand when skipping some due to duplicates (DEV-804)

- Fix duplicate detection for free teasers.

- Add read_more and read_more_url fields to IArea (DEV-824).

- Prefill IArea.supertitle from referenced_cp if present (DEV-824).

- Support both ``leader`` and ``zon-large`` for displaying lead_candidate
  content in automatic areas.

- Retrieve images for teaser modules using the new variant API (DEV-782).


3.0.0b15 (2015-06-09)
---------------------

- Restrict access to Article Flow by introducing new permission. (DEV-759)

- Update workflow and template to display validation errors on publish (DEV-22)

- Add new module `playlist` to hold a playlist for the video bar. (DEV-300)


3.0.0b14 (2015-05-20)
---------------------

- Add bw-compat for existing Auto-CPs which do not yet have a
  ``automatic_type`` setting that was introduced in 3.0.0b12, so that they
  still work in production (if raw query is present, that is used, else the
  configured channels).


3.0.0b13 (2015-05-19)
---------------------

- Replace MochiKit $$ with jQuery, which is *much* faster in Firefox.

- Preserve ZMO compat, add new kind descriptors (ZON-1710).


3.0.0b12 (2015-04-29)
---------------------

- Teach AutomaticAreas to retrieve teasers from referenced CP. (DEV-745)

- Prevent display of duplicate teasers in automatic regions (DEV-652).

- Preserve teaser module properties when changing ``automatic`` setting
  (DEV-745).

- Add draggable library elements for preconfigured regions (DEV-746).
  * New config file: ``/data/cp-regions.xml``, for ``zeit.content.cp:
    region-config-source``

- Replace `width` of Areas with `kind`, add `kind` property to Regions, remove
  `layout` property from Areas (DEV-746).
  * Config file removed: ``/data/cp-area-widths.xml``, was ``zeit.content.cp:
    area-config-source``

- Rename ``IAutomaticArea`` to ``IRenderedArea``, move properties to ``IArea``.


3.0.0b11 (2015-04-22)
---------------------

- Suppress second-level errors when generating CP Feed during rendering XML in
  Friedbert (VIV-629).


3.0.0b10 (2015-03-20)
---------------------

- Delegate only actual ``IContainer`` attributes from Centerpage to its Body,
  otherwise e.g. copy from clipboard is treated as move instead[!] (BUG-217).


3.0.0b9 (2015-03-18)
--------------------

- Don't generate ``xinclude`` for autopilots anymore, XSLT resolves them now
  (DEV-659).

- Suppress errors when generating CP Feed during rendering XML in Friedbert
  (VIV-629).

- Adjust ``BodyLandingZone`` to use new ``insert`` method, which fixes an issue
  with setting teaser layouts automatically for new blocks in first position,
  since the position was updated after adding rather before. (DEV-53)


3.0.0b8 (2015-03-13)
--------------------

- Make path to teaser layout preview images configurable.


3.0.0b7 (2015-03-13)
--------------------

- Make it possible to set a default layout for each area width. (DEV-639)

- Allow moving blocks inside and between areas (DEV-53).

- Allow moving areas inside and between regions (DEV-53).

- Allow sorting of regions by moving them inside body. (DEV-35)

- Create region with area when area is dragged from sidebar onto body. (DEV-35)

- Create region with area when area is moved onto body. (DEV-35)

- Auto-CP: Provide current feed items in ``IRenderedXML`` (DEV-621).

- Generalize Autopilots to use all areas, not just the lead area (DEV-75).
  (Note: The CP feed ``name.lead`` no longer grows/shrinks according to the
  length of the lead area.)

- Add URL input field to teaser list edit box (DEV-23).

- Areas can now return their width as a Fraction, so they can be summed up for
  width checks of a region. (DEV-589)

- Introduce an "is_region" rule to check if the context is a region. (DEV-589)

- Implement overflowing blocks from one area to another (DEV-16).

- Mark centerpages with interface to distinguish between master and 2.x branch
  (DEV-660).

- Allow toggle visibility for regions and areas (DEV-76).

- Auto-CP: Retrieve the configured number of teasers from solr (DEV-621).

- Auto-CP: Mark CP feed ``.lead`` with ``automatic`` attribute (DEV-659).


3.0.0b6 (2015-02-20)
--------------------

- Write free teasers in autopilots correctly to XML (BUG-107).


3.0.0b5 (2015-02-16)
--------------------

- Auto-CP: Treat content that is "published with changes" as "published", i.e.
  display it in Auto-CPs.

- Bugfix: Actually render the changed leader layout (VIV-436).


3.0.0b4 (2015-01-29)
--------------------

- Bugfix: if no result is a lead candidate, don't permanently change the leader
  layout (VIV-436).


3.0.0b3 (2015-01-26)
--------------------

- If no result is a lead candidate, fill the leader block with a normal result
  (VIV-436).


3.0.0.beta2 (2015-01-08)
------------------------

- Remove teasergroup functionality (VIV-624).

- Extract body traverser mechanics to zeit.edit.

- Fix bug in automatic regions that prevented checking in (automatic blocks
  need to mimic normal teaser blocks).


3.0.0.beta1 (2014-12-17)
------------------------

- Add extra container `IRegion` between `ICenterPage` and `IArea`. (VIV-621)

- `TeaserBar` is now an `IArea` and has no custom behaviour anymore. (VIV-627)

- Allow Modules in every `IArea` of a CP. (VIV-621)

- Separate layout and other properties of teaser blocks into separate tabs
  (VIV-624).

- Make available layouts of modules dependent on widths of its area. (VIV-635)

- No longer automatically insert relateds when dropping content (VIV-536).

- Add regions via an 'Add region' link. (VIV-611)

- Add areas via drag'n'drop. (VIV-612)

- Configure available areas via XML. (VIV-633)


2.10.10 (2015-08-05)
--------------------

- Prevent any automated checkout of wrong cp type (2009/2015).


2.10.9 (2015-08-04)
-------------------

- Prevent checkout of wrong cp type (2009/2015) during publish.


2.10.8 (2015-07-06)
-------------------

- Make sort order of automatic areas configurable (DEV-836).

- Handle unicode uniqueIds.


2.10.7 (2015-06-25)
-------------------

- Remove feature toggle ``zeit.content.cp.automatic`` (DEV-832).


2.10.6 (2015-06-23)
-------------------

- Use separate config file for channels (DEV-634).


2.10.5 (2015-06-19)
-------------------

- Require bw compat for old imagegroup names (DEV-783).


2.10.4 (2015-06-18)
-------------------

- Retrieve images for teaser modules using the new variant API (DEV-782).


2.10.3 (2015-06-09)
-------------------

- Back-port permission EditOverflow, even though that's a no-op here. (DEV-759)


2.10.2 (2015-06-09)
-------------------

- Update workflow and template to display validation errors on publish. (DEV-22)


2.10.1 (2015-04-30)
-------------------

- Bugfix in forward-compatibility code.


2.10.0 (2015-04-28)
-------------------

- Backport permission to edit IArea, which is used by zeit.securitypolicy,
  but has no meaning on the 2.x branch. (DEV-746)

- Forward-compatibility: Don't assume every CP has a lead, informatives and
  teaser-mosaic area.


2.9.4 (2015-03-23)
------------------

- Suppress second-level errors when generating CP Feed during rendering XML in
  Friedbert (VIV-629).


2.9.3 (2015-03-20)
------------------

- Don't generate ``xinclude`` for autopilots anymore, XSLT resolves them now
  (DEV-659).


2.9.2 (2015-03-17)
------------------

- Generate ``xinclude`` again, XSLT is not ready yet (DEV-659).


2.9.1 (2015-03-17)
------------------

- Suppress errors when generating CP Feed during rendering XML in Friedbert
  (VIV-629).


2.9.0 (2015-03-16)
------------------

- Don't generate ``xinclude`` for autopilots anymore, XSLT resolves them now
  (DEV-659).

- Mark centerpages with correct interface for this branch, ICP2009.

- Add cancel button to migration warning (DEV-660).

- Update to changed updateOrder event in zeit.edit.

- Auto-CP: Mark CP feed ``.lead`` with ``automatic`` attribute (DEV-659).


2.8.0 (2015-03-11)
------------------

- Mark centerpages with interface to distinguish between master and 2.x branch
  (DEV-660).


2.7.11 (2015-03-10)
-------------------

- Fix styling for teaser blocks / floating images (DEV-666).


2.7.10 (2015-03-10)
-------------------

- Auto-CP: Make ``count`` field required when ``automatic`` is True (BUG-213).


2.7.9 (2015-03-09)
------------------

- Auto-CP: Retrieve the configured number of teasers from solr (DEV-621).


2.7.8 (2015-03-09)
------------------

- Auto-CP: Make ``count`` field non-required (BUG-213).


2.7.7 (2015-03-04)
------------------

- Auto-CP: Provide current feed items in ``IRenderedXML`` (DEV-621).

- No longer automatically insert relateds when dropping content (VIV-536).


2.7.6 (2015-02-20)
------------------

- Write free teasers in autopilots correctly to XML (BUG-107).


2.7.5 (2015-02-16)
------------------

- Auto-CP: Treat content that is "published with changes" as "published", i.e.
  display it in Auto-CPs.

- Bugfix: Actually render the changed leader layout (VIV-436).


2.7.4 (2015-01-30)
------------------

- Bugfix: if no result is a lead candidate, don't permanently change the leader
  layout (VIV-436).


2.7.3 (2015-01-26)
------------------

- If no result is a lead candidate, fill the leader block with a normal result
  (VIV-436).

- Update tests since mock connector now yields trailing slashes for folder ids
  (FRIED-37).

- Every area can be configured for automatic contents using solr, not just the
  lead area anymore (VIV-620).


2.7.2 (2015-01-14)
------------------

- Bugfix: Update to current ``zeit.edit.sortable.Sortable`` API.


2.7.1 (2014-12-17)
------------------

- Suppress errors that are due to missing metadata files when rendering XML for
  Friedbert (VIV-629).

- Adapt query for channels so it works with both tokenized and non-tokenized
  indexing types (VIV-449).


2.7.0 (2014-11-14)
------------------

- Remove backwards-compatibility support for the ``href``/``{link}href``
  attribute convention of free teasers, only the new ``uniqueId``/``href``
  convention is supported anymore (VIV-546, VIV-322).

- Actually check delete and restrict permission of centerpages (VIV-496).


2.6.5 (2014-10-21)
------------------

- Update references when moving objects (WEB-298).

- Improve "automatic content" form styling (VIV-470).


2.6.4 (2014-10-07)
------------------

- Restrict access to auto-cp features to separate permission (VIV-525).

- Materialize current query result on turning automatic off on a CP (VIV-442).


2.6.3 (2014-09-18)
------------------

- Fix automatically changing teaser layout from leader to buttons now that
  leader is allowed everywhere (VIV-497).

- Restrict delete and retract of centerpages with special permissions (VIV-496).


2.6.2 (2014-09-03)
------------------

- Use feature toggle ``zeit.content.cp.automatic``.

- Improve "automatic content" form styling (VIV-470).


2.6.1 (2014-08-29)
------------------

- Fix brown-bag release.


2.6.0 (2014-08-28)
------------------

- Add UI to specify solr query by selecting channels (VIV-470).

- Make automatic blocks non-editable (VIV-447).

- Fill automatic "leader" block only with specially marked articles (VIV-436).

- Add rendering a centerpage as XML (while resolving automatic blocks and
  autopilot blocks) (VIV-445).


2.5.0 (2014-08-13)
------------------

- Introduce ILeadTime to store start and end timestamps for when an article is
  featured in the "leader" position (first teaser in the lead area) of a
  centerpage (WEB-325).


2.4.0 (2014-07-17)
------------------

- Introduce automatic regions that only store a solr query and fill in the
  actual content at rendering time in the frontend (VIV-434).

- Fix free teaser behaviour: delegate ICommonMetadata fields to the referenced
  content (VIV-433).


2.3.4 (2014-06-03)
------------------

- Remove "teaser supertitle" field from teaser edit form (TT-511).

- Use gocept.httpserverlayer.custom to avoid port collisions in tests.


2.3.3 (2014-03-24)
------------------

- Allow RSS blocks in lead area, too (WEB-262).


2.3.2 (2014-03-24)
------------------

- Use colorpicker widget (VIV-317).

- Allow teaserblock/bar layouts availability to be restricted according to the
  centerpage they are on (VIV-339).


2.3.1 (2014-03-19)
------------------

- Update metadata of free teasers correctly on checkin (VIV-322).


2.3.0 (2014-03-18)
------------------

- Add field ``background_color`` for blocks (VIV-317).

- Add fields ``supertitle``, ``teaserText``, ``background_color`` for teaser
  bar (VIV-318).

- Make teaserbar layouts configurable (VIV-318).

- Return schema default instead of None for unknown ICommonMetadata fields
  of free teasers (bug uncovered during testing of VIV-322).


2.2.7 (2014-03-10)
------------------

- Support ``uniqueId``/``href`` convention in free teasers, instead of
 ``href``/``{link}href``. (VIV-322)


2.2.6 (2014-02-11)
------------------

- Use correct @@raw URL for image views in fullgraphical block (VIV-306).


2.2.5 (2014-02-10)
------------------

- Use Fanstatic instead of zc.resourcelibrary (VIV-296).


2.2.4 (2014-01-20)
------------------

- Add toggle visibility icon for teaser blocks in mosaic (VIV-284).

- Pre-fill AutopilotTeaserBlock title and read more from referenced cp
  (VIV-280).

- RelatedBase is now based on MultiResource (VIV-282).


2.2.3 (2014-01-07)
------------------

- Store preview images and CSS rules for teaser block layouts in DAV instead of
  in our package (VIV-204).

- Use TypeDeclaration for legacy Teaser objects instead of the old
  two-separate-adapters API.


2.2.2 (2013-11-28)
------------------

- Fix bug in interaction of parquet image positions with lead multicolumn
  teasers (leads to "IndexError out of range").


2.2.1 (2013-11-25)
------------------

- Add ``parquet-break`` layout for teaser bars (VIV-166/VIV-188).

- Display blocks in parquet teaser bars below each other instead of in columns
  (VIV-182).

- Display title of referenced CP in teaser block (VIV-182).

- Update topiclinks of referenced CPs on checkin of the referencing CP.


2.2.0 (2013-11-15)
------------------

- Add ``parquet`` layout for teaser bars (VIV-164).

- Write topiclinks of the referenced centerpage into the teaser block's
  <container> (VIV-163/VIV-191).

- Add field ``display_amount`` to teaser blocks (VIV-164/VIV-183).

- Allow configuring which teaser positions should display an image (VIV-202).


2.1.3 (2013-10-02)
------------------

- Update to lxml-3.x (#11611).


2.1.2 (2013-09-24)
------------------

- Display ``breadcrumb_title`` field (VIV-105).


2.1.1 (2013-08-14)
------------------

- Update to Python-2.7 and ZTK-1.1.5 (#11005).


2.1.0 (2013-08-13)
------------------

- Add timeout for RSS downloads (#9560).


2.0.1 (2013-07-01)
------------------

- Mark keywords as non-required for CenterPages (#12478).


2.0 (2013-04-23)
----------------

- Register TeaserBlock only for CenterPages, when it shows up in an Article it
  causes nothing but trouble, since it doesn't belong there (#9914).


0.53.0 (2013-03-13)
-------------------

- Don't change lead teaser block layout to button when moving blocks around
  (#12199)

- Prefer teaserSuperTitle over superTitle (#11610).


0.52.0 (2012-05-10)
-------------------

- Applied a non-numerical prefix to generated ids that may be used as html ids
  for standards conformance and forward compatibility with webdriver.

- Fixed and re-enabled some tests (#10340, #10364).

- Maximize selenium test window on test start

- Cleaned up dependencies on zope.app packages.


0.51.0 (2012-03-06)
-------------------

- Introduced fall-back behaviour to the full-graphical block so that the
  teaser image and title, resp., of the referenced object are used when the
  block doesn't have its own image or title. Added the selection of a layout
  to choose an image from an image group (#10158).

- Adds fields for OG-metadata in CP-metadata-form

- Skip two flaky tests until we have the Selenium 2 API available.
  (#10340, #10364)


0.50.2 (2011-12-19)
-------------------

- Use low-priority queue for publishing RSS feeds (#10037).
- Use BeforeCheckin(while_publishing) instead of BeforePublish+cycle for
  update_feed_items to avoid the extra checkin/checkout-cycle (for #10068).


0.50.1 (2011-11-15)
-------------------

- Removed 4th topiclink


0.50.0 (2011-11-13)
-------------------

- Accomodated article to cope for the changed videos: videos are now full CMS
  objects and moved to zeit.content.video (for #8996)

- In den Metadaten für den Centerpage-Editor sind nun Felder für 4 sog. Topic-
  links (jeweils Linktext un URL) sowie ein Title-Feld (ohne Ticket)


0.43.3 (2011-06-23)
-------------------

- Compatibility fix for Firefox 5 (#9236).


0.43.2 (2011-06-22)
-------------------

- Compatibility fix for Firefox 5 (#9227).


0.43.1 (2011-03-24)
-------------------

- Bugfix: Raw-Modul im Aufmacher bekommt kein Layout mehr zugewiesen, das kann
  nämlich nicht funktionieren (#8844).

- is_published für Validation-Rules ignoriert NotPublishablePublishInfos
  (#8843).


0.43.0 (2011-03-23)
-------------------

- TeaserBockProxy adapts to ICommonMetadata now.

- Freie Teaser werden jetzt nur noch in der CP gespeichert. Es gibt keine extra
  Objekte im DAV mehr dafür (#7826)

- Das Raw-Modul kann jetzt auch im Aufmacher verwendet werden (#8781)

- Layout-Berechnung im Aufmacher korrigiert (#8844).


0.42.0 (2010-08-16)
-------------------

- Reichweite im CPE anzeigen (#7560).

- Für Teaserbilder wird als Fallback jetzt @@preview  verwendet (#7798).


0.41.0 (2010-08-09)
-------------------

- ``cms_content_iter`` funktioniert jetzt auch, wenn eine CP ein Modul enthält,
  welches das CMS nicht kennt (#7727).
- Für Selenium-Tests wird nun ``gocept.selenium`` verwendet (#7549).
- Auch gesperrte, oder anderweitig nicht auscheckbare Objekte, haben beim
  Bearbeiten einer Teaser-Liste jetzt das Icon "in neuem Fenster öffnen"
  (#7825).



0.40.0 (2010-07-07)
-------------------

- Warnung bei Änderungen, wenn ein freier Teaser zu einem Artikel existiert
  (#6415).


0.39.0 (2010-07-07)
-------------------

- Fehler bei Regeln ("cp_type is undefined") verhindern (#7444).
- Stabilieres Quick-Publish (#7433).
- Aktualisieren des RSS-Feeds in der CP führt nicht mehr zu ConflictError
  (#7587)


0.38.0 (2010-06-09)
-------------------

- Prevent error during refresh when feed cannot be checked out (#7313).
- Participate in the zeit.relation index (for #6160).
- New properties for RSS-Block: show_supertitle (#7390), time_format (#6936).
- Update Header-Image/Snapshot XML reference if image metadata change (#7402).


0.37.0 (2010-06-02)
-------------------

- Header-Image und Snapshot werden im XML anstatt im DAV gespeichert (#7325).
- Fehler bei Regeln ("cp_type is undefined") verhindern (#7192).


0.36.0 (2010-05-18)
-------------------

- RSS-Block: Felder für Feed-Icon und Teaserbild (#7259).


0.35.1 (2010-05-17)
-------------------

- Fixed test for zeit.brightcove >= 0.3.0 (#7241)


0.35.0 (2010-05-03)
-------------------

- Errors in editors actions are logged as warning now.

- Fullgraphical block doesn't break CPE if the referenced object is removed
  (#7093).

- Added Snapshot image (#7181)


0.34.0 (2010-04-09)
-------------------

- Brightcove-Videos integriert (#6881).

- Favicon zu RSS-Feed speichern (#6937).

- Using versions from the ZTK.


0.33.0 (2010-03-10)
-------------------

- »Doubletten vermeiden« kann wieder deaktiviert werden (#6731)

- Asset-Tab für CPs aktiviert (#6876).

- Die Felder CAP-Kontext und CAP-Titel von der Centerpage direkt entfernt und
  auf allen Objekten mit Standardmetadaten verfügbar gemacht (#6923).

- Ist ein Objekt im RSS-Feed kommt ein freier Teaser dieses Objekts nicht mehr
  in den RSS-Feed und umgekehrt (#6724).


0.32.1 (2010-02-23)
-------------------

- Anzahl der Feeditems mind. so groß wie der Aufmacher (#6865)

0.32.0 (2010-02-08)
-------------------

- ``cp_extra`` Block hinzugefügt: solr-month (#6749)

- ``cp_extra`` Block hinzugefügt: dwds-ticker (#6749)

- ``cp_extra`` Block hinzugefügt: recensionsearch

- ``cp_extra`` Block hinzugefügt: sportextra

0.31 (2009-12-18)
-----------------

- Bestätigung beim Löschen von Elementen entfernt (#6412).
- Neue Felder: CAP title, CAP context (#6598).


0.30.0 (2009-12-11)
-------------------

- ``cp_extra`` Block hinzugefügt: linkatory

- ``cp_extra`` Block hinzugefügt: homepage_news_pics

- Teaser-Block im Autopilot: Doubletten-Vermeidung ist standardmäßig aktiviert
  (#6243).

0.29.0 (2009-11-25)
-------------------

- Fehlerhaftes Markup im Raw-XML-Block wird repariert (#6431).


0.28.1 (2009-11-04)
-------------------

- Asynchronse Requests serialisiert damit das Löschen beim Verschieben von
  Teaseren zuverlässig funktioniert.

- Bild des ersten Teasers ist jetzt draggable.

- Wird ein Teaser im CPE verschoben und auf eine Landezone gezogen, werden die
  Relateds nicht mehr automatisch gezogen.

- Default für XML-Block geändert: der <container> beinhaltet ein offenes
  <raw>-Tag (#6051).


0.28.0 (2009-11-02)
-------------------

- Teasergruppen zum Zusammenfassen von Teasern (#6385).

- Der erste Teaser eines Teaserblocks lässt sich ziehen. Wird er innerhalb der
  CP fallen gelassen, wird der gezogene Teaser aus der „Quelle“ entfernt.
  (#6384).


0.27.1 (2009-10-26)
-------------------

- Darstellung der Layout-Auswahl der Teaserleisten korrigiert.


0.27.0 (2009-10-19)
-------------------

- Es werden jetzt 6 statt nur 4 Teaser in Autopilot-Blöcken angezeigt (#6354).

- Themenseiten werden in der Site-Steuerung angezeigt (#6350).

0.26.0 (2009-10-12)
-------------------

- Blöcke im Aufmacher sind jetzt nummeriert (#6273).

- Performance der Container-Implementation verbessert.

- Hinzufügen von Blöcken über die Landeflächen im Aufmacher schneller.

- Fehlerbehandlung asynchroner Requests repariert.

- Es werden nur noch 4 Teaser in Autopilot-Blöcken angezeigt um 1. die
  Geschwindigkeit zu erhöhen und 2. das Aussehen der Seite besser
  wiederzuspiegeln

- (De-)aktivieren von Autopiloten schneller.

- Icon für freie Teaser (#6063).

- Icon für RSS-Feeds.

0.25.1 (2009-10-07)
-------------------

- feed-Eelement der CP wird jetzt korrekt gekürzt.


0.25 (2009-10-06)
-----------------

- CPE in einigen Teilen schneller: Löschen von Blöcken, Hinzufügen von Inhalten


0.24 (2009-09-26)
-----------------

- Die Metadaten in der Centerpage werden jetzt beim einchecken direkt
  aktualisiert und nicht mehr asynchron.

- CPE ist i.A. schneller, weil nur noch Teilbereiche der Seite ersetzt werden.


0.23 (2009-09-21)
-----------------

- Die Sidebar wird nicht mehr automatisch ausgeblendet.

- Beim Teaser-Bearbeiten-Link zum Objekt wird nicht mehr automatisch
  ausgecheckt.

- Feld »Doubletten vermeiden« am Autopilot-Teaser-Block.


0.22 (2009-09-11)
-----------------

- Date-Last-Modified, Last-Semantic-Change, Date-First-Released und
  Date-Last-Published wird in die ``<block>`` Knoten auf eienr CP eingefügt.


0.21 (2009-09-10)
-----------------

- Eine CP erzeugt beim Einchecken einen »Lead-Channel«. Dieser wird für
  Autopiloten verwendet.


0.20.6 (2009-09-06)
-------------------

- Regel-Glob ``cp_type``


0.20.5 (2009-09-05)
-------------------

- Beinhaltete, nicht semantisch geänderte, Objekte werden auch nicht mehr mit
  veröffentlicht, weil es nicht performant genug ist.


0.20.4 (2009-09-05)
-------------------

- Freie Teaser werden nicht mehr veröffentlicht, weil das garnicht nötig. ist.


0.20.3 (2009-09-05)
-------------------

- Tests für Änderungen an zeit.cms angepasst.


0.20.2 (2009-09-05)
-------------------

- Ändern des Autopilots aktualisierte den xi:include nicht.


0.20.1 (2009-09-05)
-------------------

- Refresh auf einem RSS-Block ohne URL führt nicht mehr zu einem Fehler.


0.20 (2009-09-05)
-----------------

- Asynchrones aktualisieren der Metadaten der CP beim Checkin.

- Aktualisieren der Metadaten funktioniert auch, wenn ein Autopilot
  ein ungültiges Objekt referenziert.

- Beim Aufmachen des Editors wird zunächst ein Busy-Indicator gezeigt.


0.19 (2009-09-04)
-----------------

- Rule-Globs ``content`` und ``is_published`` (#6059).

- Korrekte Anzeige der Teaser und Spitzmarke im Editor (Teil von #5877).

- Teaser-Bearbeiten-Box ist wieder als Box erkennbar, die man auch zumachen
  kann.

0.18.2 (2009-09-04)
-------------------

- Feed-Updates repariert, wenn der Feed kein Feed sondern z.B. eine HTML-Seite
  ist.


0.18.1 (2009-09-04)
-------------------

- Feed-Updates repariert, wenn Feed noch nie aktualisiert wurde.


0.18 (2009-09-04)
-----------------

- Player (vid/pls) für Video (#6150).

- Principal mit dem die Feeds veröffentlicht werden ist jetzt konfigurierbar.

- Beim Umsortieren von Teasern kann man jetzt direkt das Objekt in einem neuen
  Fenster bearbeiten (#5820).

- Ein Mouseover beim Teaser-Sortieren zeigt die Id des Objekts.

- Quiz wird ohne xi:include eingebunden (#6022).

- Quiz-Metadaten werden in der CP aktualisiert (#6167).

0.17 (2009-09-01)
-----------------

- Bessere Texte beim Bearbeiten von Teasern in der CP (#6144)

- ``cp_extra`` Block hinzugefügt: authors-register


0.16 (2009-08-31)
-----------------

- Sortieren der Blöcke innerhalb eines MR funktioniert wieder (#6112).

- Teaser sortieren funktioniert, wenn zerbrochene Objekt-Referenzen im
  XML stehen (#6133).

- Autopilot funktioniert jetzt auch, wenn ein Channel eingebunden wurde, der
  Referenzen auf nicht (mehr) vorhandene Objekte enthält.

- ``cp_extra`` Block hinzugefügt: homepage_news


0.15.1 (2009-08-27)
-------------------

- I18N-Message-Id repariert.


0.15 (2009-08-26)
-----------------

- In der CP beinhaltete Objekte werden automatisch veröffentlicht (wenn lsc <=
  dlp <= dlm, #6057)

- Robusteres erstellen von freien Teasern.

- Centerpage kann eingecheckt werden, auch wenn (ganz) alte Feeds beinhaltet
  sind (#6064).

- Freie Teaser werden immer mit der CP veröffentlicht (#6060).

- ``cp_extra`` Blöcke entfernt: Relateds, Debug

- RSS-Feeds: Domain-Attribut bei <category> optional (#6074).

- Feed-Elemente in der Centerpage werden jetzt korrekt geschrieben.

- Bessere Fehlerbehandlung, wenn aysynchrone Requests fehlschlagen (#6061).

- CPE erzeugt einen sinnvollen Fehler, wenn ein Objekt in den Editor gezogen
  wird, das es garnicht gibg (#6062).

0.14 (2009-08-21)
-----------------

- ``cp_extra`` Block: dpa-News

- Layout für Printarchivseiten in Volume und Year unterteilt.

- Vorausgewähltes Layout abhängig von der Fläche (#5870).

- Block-Layouts kommen aus einer XML-Datei und stehen nicht mehr direkt im
  Quellcode. Damit stimmen jetzt auch die verwendeten Bilder (#5876).

- Veröffentlichen einer CP mit einem Click (#5661).


0.13 (2009-08-14)
-----------------

- Drop von Inhaltsobjekten in einen Teasermosaik-Platzhalter funktioniert
  wieder (#5972).

- Maximale Anzahl anzuzeigender Einträge im RSS-Block einstellbar (#5964).

- <category> wird in Feeds übernommen (#5967).

- Titel bei cpextras kann überschrieben werden (#5997).

- Quiz-Block enthält jetzt ein xi:include (#5974).

0.12 (2009-08-11)
-----------------

- JSON-Post statt GET mit langer URL (#5868).

- Layout für Printarchivseiten hinzugefügt.

- »Common«-Tab bei Blöcken erreichbar, die sonst keine Bearbeitungsmöglichkeit
  haben (#5955).

- ``cp_extra`` Blöcke: Neu im Ressort, Live-Search, Print Archiv, Relateds,
  Blindblock, Debug

- xi:includes werden jetzt mit dem richtigen Pfad ausgegeben (#5954).

0.11 (2009-08-03)
-----------------

- Weitere Layouts für den Teaserblock: Doppelspalter, Datumsteaser, Kleine
  Teaser (#5829).

0.10.1 (2009-07-28)
-------------------

- CP-Source zum Filtern per Suche angepasst (#4499).

0.10 (2009-07-20)
-----------------

- RSS-Block zeigt Fehler sinnvoller an (#5678).

- Speichern funktioniert zuverlässiger (#5707, #5669).

- Bessere Anzeige von Fehlern im RSS-Block (#5678).

- Modulnamen in der Modulbibliothek werden jetzt übersetzt (u.A. #5677).

- Vollgraphischer Block ist direkt nach dem Anlegen nicht mehr leer.

- LightboxForms aktivieren jetzt den Lightbox-Context.

0.9.1 (2009-06-24)
------------------

- »leader-upright«-Layout repariert (#5570).

- Die CenterPage enthält einen neuen Abschnitt ``<feed>``, in dem
  ``<reference>``s zu den n letzten Teasern aus dem Aufmacherbereich stehen;
  jeweils der erste Teaser eines Teaserblocks wird dort eingefügt (#4884).

  Die Einträge sind umgekehrt chronologisch geordnet, d. h. um den eigentlichen
  RSS-Feed zu erzeugen, kann das XSLT die ersten x Einträge nehmen.
  n ist konfigurierbar über product config ``cp-feed-max-items``
  (im Moment n=200).


0.9 (2009-06-18)
----------------

Neue Funktionen
~~~~~~~~~~~~~~~

- Modul-Bibliothek: Tab für »alle«.

- Die Sidebar wird beim Öffnen des Editors automatisch ausgeblendet (#5038).

Technische Änderungen
~~~~~~~~~~~~~~~~~~~~~

- Content-Source für CenterPages hinzugefügt.

0.8 (2009-06-09)
----------------

- ``type``-Attribut auf ``<centerpage>`` (#5030, #5480).

- Contextabhängige Layouts (#5034).

- Registrierung via Martian.

- Bessere Texte

0.7 (2009-05-26)
----------------

Neue Funktionen
~~~~~~~~~~~~~~~

- Neue Content Blöcke "Quiz" (#5279) und "Vollgraphisch" (#5278) wurden
  hinzugefügt.

- Beim Bearbeiten eines Teaserblocks können jetzt Teaser direkt in die Liste
  gezogen werden.

- Blockblibliothek

- Tabs im Block-Bearbeiten (#5323)

- Freie Teaser können im CMS direkt bearbeitet werden (#5059).

- Autopilot in der Aufmacherfläche nicht mehr möglich (verhindert Kreise,
  #5031).

Technische Änderungen
~~~~~~~~~~~~~~~~~~~~~

- Interface-Umstrukturierung um genauer zwischen Fläche, Region und Block
  unterscheiden zu können.


0.6 (2009-05-17)
----------------

Neue Funktionen
~~~~~~~~~~~~~~~

- Neue Content Blöcke "Audio" (#5276) und "Video" (#5051) wurden hinzugefügt.

- Automatische Teaserblöcke (Autopilot) können auch Channel referenzieren
  (#5290).

- Automatische Teaserblöcke erstellen korrektes <xi:include>.

- Blöcke in einer Teaserleiste sind alle gleich hoch.

- ``cp_extra`` Blöcke: Wetter, Börse, Meistgelesen, Meistkommentiert

- RSS-Block (für externe Feeds) hinzugefügt (#5273).

- Keine eigene Translationdomain mehr, Übersetzungen via zeit.locales.

- Umsortieren von Blöcken in Teaserleisten.

0.5 (2009-05-08)
----------------

Neue Funktionen
~~~~~~~~~~~~~~~

- Ein neuer Content Block "XML" wurde hinzugefügt (#5277)

- Validierungsregeln: Die unter
  http://zip6.zeit.de:9000/cms/forms/centerpage-validation-rules.py abgelegten
  Regeln werden auf die CenterPage angewandt. Fehler werden rot, Warnungen
  gelb. Gibt es einen fehlerhaften Bereich, kann die CP nicht veröffentlicht
  werden.

- Für die Teaserleiste kann nun das Layout MR (einspaltiger Werbeblock),
  DMR (zweispaltiger Werbeblock) und normal (keine Werbung) ausgewählt werden
  (#5001).


0.4 (2009-04-30)
----------------

Neue Funktionen
~~~~~~~~~~~~~~~

- Wird ein Objekt auf einem Autopilot-Block fallgen gelassen wird der Autopilot
  automatisch ausgeschaltet.

- Landefläche für Teaser in der Aufmacherfläche (#4883): Fallen lassen eines
  Content-Objekts bewirkt das Anlegen eines Teaser-Blocks mit dem Objekt und
  seinen Relateds.

- Beim Bearbeiten von Teasern können nun »freie Teaser« erzeugt werden. (#4788)

- Regeln für Layouts von Teaserlisten (#5033): Der erste Block bekommt das
  Layout mit dem großen Bild, alle anderen das Layout mit dem kleinen Bild.

- Beim Einchecken der Centerpage werden die Metadaten der referenzierten
  Artikel aktualisiert. (#4976)

- Umsortieren von Blöcken in der Aufmacher- und Informatives-Fläche (#5046).

Beseitigte Fehler
~~~~~~~~~~~~~~~~~

- Editor scrollt nicht mehr nach oben, wenn man etwas getan hat (fixes #5018).

- Nach geöffneter Lightbox ging Drag'n'Drop nicht mehr (fixes #5019).


0.3 (2009-04-23)
----------------

- Bearbeiten von Teasern in der CP (#4806).

- zeit.find integriert

- Löschen von Teaserleisten nach dem Verschieben funktioniert wieder (fixes
  #4999)

- Autopilot

- Layouts für Teaserblöcke


0.2 (2009-04-17)
----------------

- Teaser-Liste kann mit Teasern befüllt werden.

- Highlight der Boxen bei Mouse-Over.

- Sortieren von Teaserleisten (#4776).

- Löschen von Teasern aus der Teaserliste (#4805).

- Sortieren von Teasern im Bearbeiten-Dialog der Teaserliste (#4805).

0.1 (2009-04-03)
----------------

- Erstes release.


zeit.content.dynamicfolder changes
==================================

1.2.6 (2019-03-29)
------------------

- PERF: Don't grok browser packages by default


1.2.5 (2018-03-02)
------------------

- FIX: Make publishing dynamic folders work


1.2.4 (2017-10-04)
------------------

- ZON-3409: Move from remotetask to celery


1.2.3 (2017-07-18)
------------------

- BUG-500: Update to new dependency API


1.2.2 (2016-11-30)
------------------

- Support un-urlencoded non-ascii keys.


1.2.1 (2016-09-26)
------------------

- Don't copy the template's UUID into the virtual content created from
  it (BUG-391).


1.2.0 (2016-08-24)
------------------

- Remove unnecessary interfaces from ``IVirtualContent``

- Provide ``__parent__`` in template. (ZON-3254)


1.1.4 (2016-07-26)
------------------

- Make dynamic folders robust against erroneous configs.


1.1.3 (2015-12-16)
------------------

- Correctly combine parsing DAV properties from the XML template and
  materializing virtual content via checkout (BUG-325).


1.1.2 (2015-11-24)
------------------

- Register a workflow form for dynamic folders.


1.1.1 (2015-11-24)
------------------

- Configure a workflow for dynamic folders so they can be published.


1.1.0 (2015-09-29)
------------------

- Convert ``head/attribute`` XML nodes of the template into DAV properties.
  (This means we also support arbitrary content types via the meta:type
  attribute, and arbitrary interfaces via the meta:provides attribute.)


1.0.5 (2015-09-28)
------------------

- Handle templates both with vivi content-type ``rawxml`` and without.


1.0.4 (2015-09-21)
------------------

- Speed up configuration by appending included nodes at the end of the parent
  element instead of at precisely the position of the ``<include>`` node.


1.0.3 (2015-09-07)
------------------

- Decode non-ascii ``url_value`` correctly.


1.0.2 (2015-08-25)
------------------

- Use simplified folder view that does not instantiate all child objects
  (performance optimization).


1.0.1 (2015-06-09)
------------------

- Make text of content nodes available in template via the key `text`.


1.0.0 (2015-05-18)
------------------

- Initial release.


zeit.content.gallery changes
============================

2.9.1 (2019-03-29)
------------------

- PERF: Don't grok browser packages by default


2.9.0 (2019-01-09)
------------------

- ZON-5071: Remove max length restriction from gallery content


2.8.8 (2018-12-03)
------------------

- FIX: Fix JS expecting mult value copyrights


2.8.7 (2018-11-20)
------------------

- ZON-4106: Adjust code to new copyright api


2.8.6 (2018-10-08)
------------------

- ZON-3312: Move teaser image form field to metadata tab instead of separate asset tab


2.8.5 (2018-10-05)
------------------

- ZON-3312: Remove obsolete asset badges


2.8.4 (2018-07-26)
------------------

- FIX: Be defensive about XML body structure expectations
  (mostly since ITMSContent doesn't have a whole body)


2.8.3 (2018-04-11)
------------------

- BUG-894: Remove "crop entry" link after removing zeit.imp


2.8.2 (2018-01-26)
------------------

- FIX: Fix object details "edit" link after removing zeit.imp


2.8.1 (2018-01-09)
------------------

- MAINT: Remove dependency on zeit.imp permissions, so we can stop
  loading its ZCML completely in production (we've been on
  zeit.content.image.variants for quite some time now)


2.8.0 (2017-10-04)
------------------

- ZON-3409: Move from remotetask to celery


2.7.7 (2017-08-07)
------------------

- ZON-4006: Update to mobile field split


2.7.6 (2017-07-18)
------------------

- BUG-500: Update to new dependency API


2.7.5 (2017-05-22)
------------------

- ZON-3917 remove bigshare button checkbox


2.7.4 (2017-02-28)
------------------

- Add visible gallery entry count (Re: BUG-637)


2.7.3 (2016-10-04)
------------------

- Pass through ``suppress_errors`` in XMLReferenceUpdater.


2.7.2 (2016-09-26)
------------------

- Update to `zeit.cms >= 2.90`.


2.7.1 (2016-09-14)
------------------

- ZON-3318: Support bigshare buttons.


2.7.0 (2016-08-04)
------------------

- Add metadata and images adapters for gallery entries (ZON-1586)


2.6.15 (2015-04-15)
-------------------

- Undo 2.6.14, it was a misunderstanding.


2.6.14 (2015-04-15)
-------------------

- Add feature toggle ``zeit.push.social-form`` for social media form fields.


2.6.13 (2014-12-17)
-------------------

- Update tests since mock connector now yields trailing slashes for folder ids
  (FRIED-37).


2.6.12 (2014-11-14)
-------------------

- Fix bug in social media addform so it actually stores push configuration
  (VIV-516).


2.6.11 (2014-10-21)
-------------------

- Add social media section to edit form (VIV-516).


2.6.10 (2014-07-17)
-------------------

- Normalize image filenames during bulk upload (VIV-409).


2.6.9 (2014-06-05)
------------------

- Use plone.testing-based layers.


2.6.8 (2014-03-10)
------------------

- zeit.content.image has its own egg now.


2.6.7 (2014-02-10)
------------------

- Use Fanstatic instead of zc.resourcelibrary (VIV-296).


2.6.6 (2014-01-20)
------------------

- RelatedBase is now based on MultiResource (VIV-282).


2.6.5 (2014-01-07)
------------------

- Use default XMLSource implementation so we get ``available`` behaviour
  (VIV-247).


2.6.4 (2013-10-02)
------------------

- Update to lxml-3.x (#11611).


2.6.3 (2013-08-14)
------------------

- Update to Python-2.7 and ZTK-1.1.5 (#11005).


2.6.2 (2013-07-08)
------------------

- Fix tests to deal with required keywords (#12478).
- Adapt Javascript so it can always be loaded (#11290).


2.6.1 (2013-05-29)
------------------

- Fix handling of GalleryEntry.caption after removal of XMLSnippet (#12425).


2.6.0 (2013-04-23)
------------------

- Remove XMLSnippet, its functionality is not used anymore.


2.5.0 (2012-07-02)
------------------

- Introduced gallery types (standalone, inline) (#10761).



2.4.2 (2012-03-06)
------------------

- Removed unused import.


2.4.1 (2011-06-27)
------------------

- Längenbeschränktes Textfeld nun Teil von text_fields (Layout).


2.4.0 (2011-05-26)
------------------

- Gallerie-Einträge haben kein Feld "Text" mehr, dafür aber die Gallerie selbst
  ein längenbeschränktes (#8858, #8866).


2.3.0 (2010-08-09)
------------------

- Es gibt in den Assets nur noch eine Bildergalerie (#6248)


2.2.6 (2010-04-27)
------------------

- Using versions from the ZTK.


2.2.5 (2010-03-10)
------------------

- Change the way asset interfaces are registered. This fixes isolation problems
  during tests (#6712).

2.2.4 (2009-12-18)
------------------

- NoAutomaticMetadataUpdate entfernt.


2.2.3 (2009-10-05)
------------------

- Tests nach Änderungen in zeit.cms repariert.


2.2.2 (2009-09-06)
------------------

- Der Gallery-XMLReferenceUpdater erzeugte immer ein neues <gallery>-Element.


2.2.1 (2009-08-18)
------------------

- Beim Zuschneiden werden nicht mehr alle Thumbnails neu erzeugt.

2.2 (2009-08-17)
----------------

- Eine referenzierte Galerie wird in den Relateds mit ausgegeben (#5975).

2.1.1 (2009-08-03)
------------------

- Bilder werden nicht mehr versteckt, wenn man sie ein zweites Mal zuschneidet.

2.1 (2009-08-03)
----------------

- JavaScript-Fehler wegen nicht vorhandenem Uploader behoben.

- Styling

- Zuschneiden: Pro Zuschnitt gibt es nur noch genau ein Bild.

- Zuschneiden: Bild-Metadaten werden übertragen (Copyright, Titel, …), (#5869)

- Standardview einer ausgecheckten Galerie ist die Bilder-Übersicht.

2.0.3 (2009-07-28)
------------------

- Gallery-Source zum Filtern per Suche angepasst (#4499).

- Volltext-Indexer hinzugefügt.

2.0.2 (2009-07-23)
------------------

- Sicherstellen, dass auch Unicode-Principal-Ids unterstützt werden.

2.0.1 (2009-07-23)
------------------

- Kompatibilität für 64bit-Systeme

2.0 (2009-07-22)
----------------

- Skalieren von Bildern in der Bildergallerie (#4973).

- Bulkupload von Bildern (#5640).

- Hilfsfunktionen für Browser-Tests nach zeit.content.gallery.browser.testing
  extrahiert.

1.22.4 (2009-06-23)
-------------------

- Beim »Bilderordner synchronisieren« werden nur noch die Bilder im
  Thumbnail-Ordner gelöscht und nicht mehr der gesamte Thumbnail-Ordner.

1.22.3 (2009-06-17)
-------------------

- Veraltete Resource-Library zeit.content.Sortable nicht mehr verwenden.

1.22.2 (2009-06-08)
-------------------

- Text aus Captions wurde bei der Verarbeitung nicht immer richtig XML-escaped.
  Eine Galerie konnte hierduch teilweise unbearbeitbar werden.

1.22.1 (2009-06-05)
-------------------

- Registrierung via TypeDeclaration

1.22 (2009-05-28)
-----------------

- Aus zeit.cms extrahiert.


zeit.content.image changes
==========================

2.23.3 (2019-03-29)
-------------------

- PERF: Don't grok browser packages by default


2.23.2 (2019-02-27)
-------------------

- BUG-1066: Apply upload validation to image group as well


2.23.1 (2019-02-26)
-------------------

- BUG-1066: Ignore browser-sent MIME type, inspect uploaded data instead;
  reject unsupported MIME types (currently we handle only jpg and png)


2.23.0 (2019-02-18)
-------------------

- ZON-5136: Allow overriding output format when creating variant images, to support WEBP

- ZON-5134: Extract URL parsing into separate Traverser instead of ImageGroup.getitem


2.22.5 (2018-12-03)
-------------------

- FIX: Be more defensive about copyrights in single image view


2.22.4 (2018-11-29)
-------------------

- ZON-4106: Add more coprights via css


2.22.3 (2018-11-28)
-------------------

- ZON-4106: Adjust UI for copyrights


2.22.2 (2018-11-20)
-------------------

- FIX: Fix image references working with new default None for copyrights


2.22.1 (2018-11-15)
-------------------

- MAINT: Change image metadata api from 'copyrights' to 'copyright'


2.22.0 (2018-11-13)
-------------------

- ZON-4981: Be more strict when adding copyright information


2.21.7 (2018-10-05)
-------------------

- ZON-3312: Remove obsolete asset badges


2.21.6 (2018-07-16)
-------------------

- MAINT: Be more precise about when/how to update XML metadata


2.21.5 (2018-06-07)
-------------------

- TMS-213: Don't index images inside of image groups in TMS


2.21.4 (2018-05-09)
-------------------

- MAINT: Be defensive about broken/missing metatdata in image listing,
  e.g. when the parent image group has been deleted in the meantime


2.21.3 (2018-03-13)
-------------------

- TMS-162: Make `factory` available on TypeDeclaration


2.21.2 (2018-01-09)
-------------------

- MAINT: Remove feature toggle `zeit.content.image.variants` which has
  been in production for quite a long time now


2.21.1 (2017-11-09)
-------------------

- FIX: Restrict image upload to supported mime types


2.21.0 (2017-10-04)
-------------------

- ZON-3409: Move from remotetask to celery


2.20.4 (2017-09-18)
-------------------

- BUG-749: Fix formlib validation bug

- BUG-771: Don't break during deleting imagegroup due to deleted children


2.20.3 (2017-06-29)
-------------------

- FIX: Remove year+volume remnants


2.20.2 (2017-06-29)
-------------------

- MAINT: Make photographer non-required

- MAINT: Remove obsolete year+volume fields


2.20.1 (2017-06-28)
-------------------

- ZON-3174: Add heuristics for Reuters external IDs


2.20.0 (2017-06-26)
-------------------

- ZON-3174: Extend copyright field to include company (dropdown and freetext),
  add field for external ID


2.19.2 (2017-06-21)
-------------------

- BUG-719: Normalize uploaded image file names


2.19.1 (2017-06-21)
-------------------

- Fix brown-bag release


2.19.0 (2017-06-21)
-------------------

- MAINT: Recreate thumbnail sources when user triggers cache refresh

- ZON-4027: Ignore errors when rendering image details so they always
  render an edit button

- ZON-3940: Remove thumbnail images when their corresponding image is removed


2.18.1 (2016-12-06)
-------------------

- ZON-3363: Some UI/form field tweaks for infographics.

- ZON-3363: Hide thumbnails in content listing of ``ImageGroup``.


2.18.0 (2016-10-19)
-------------------

- ZON-3414: Add device pixel ratio to imageserver API


2.17.1 (2016-10-05)
-------------------

- Be defensive about zero-sized images.


2.17.0 (2016-09-28)
-------------------

- Deprecate automatic image link rewriting (VIV-263)

- Add nofollow flag to image links (ZON-3375)


2.16.3 (2016-09-26)
-------------------

- Update to `zeit.cms >= 2.90`.


2.16.2 (2016-09-12)
-------------------

- Handle non-ASCII uniqueIds in ``variant_url``.


2.16.1 (2016-09-05)
-------------------

- Be defensive about falling back to image metadata.


2.16.0 (2016-08-18)
-------------------

- Proxy image reference attribute access to its target and ignore
  copied metadata (unless, of cause the attribute is overriden locally).
  We still copy the XML on creation and update for compatibility. (Re ZON-1586)


2.15.1 (2016-08-11)
-------------------

- Have master_image_for_viewport() fall back on "the largest image" it
  can find if a nonexistent name is configured.


2.15.0 (2016-08-10)
-------------------

- Add ``IImageGroup.master_image_for_viewport()``.

- Determine ratio for "original" Variant from the actual source image
  during transform, so it is viewport-sensitive. This also means
  ``Variant.ratio`` for "original" is now None instead of a float,
  since at that point we do not have the viewport information.


2.14.4 (2016-08-04)
-------------------

- Bugfix: actually create thumbnail source when an imagegroup is added.


2.14.3 (2016-08-02)
-------------------

- Be defensive about invalid master image properties.


2.14.2 (2016-08-02)
-------------------

- Improve wording.


2.14.1 (2016-08-01)
-------------------

- Pass IImageMetadata of synthesized images through to the image group.


2.14.0 (2016-07-26)
-------------------

- Be defensive about zoom=0 settings.

- Allow viewport modifier inside URL of image variants. (ZON-3171)

- Store multiple master images and which viewport they should be used for,
  rather allowing a single master image for everything. (ZON-3171)

- Render variants using the master image for given viewport. (ZON-3171)

- Remove dependency to `zeit.imp`. (ZON-3171)

- Adjust image templates to preview them more similar to Friedbert. (ZON-3216)


2.13.5 (2016-06-27)
-------------------

- Be defensive about imagegroups with no master image.

- Be defensive about zero-sized images.


2.13.4 (2016-05-03)
-------------------

- Be defensive about invalid variant requests.


2.13.3 (2016-04-25)
-------------------

- Allow materialized images with legacy names to serve as source for
  size and fill color transformation. (ZON-2029)

- Apply maximum image size only for the requested size, not the size
  of the source/master image.


2.13.2 (2016-04-18)
-------------------

- Don't load Zope/UI specific ZCML in the model ZCML


2.13.1 (2016-04-18)
-------------------

- Set a maximum image size to protect against overload


2.13.0 (2016-04-07)
-------------------

- Deprecate image spoof protection signature (ZON-2878).

- Support rendering a fill color for images with alpha channel, e.g.
  ``cinema__100x200__0000ff`` (ZON-2878).
  * Add parameter ``fill_color`` to ``variant_url()``
  * Add property ``IImages.fill_color``


2.12.0 (2016-02-29)
-------------------

- Deprecate image alignment setting (ZON-2782).


2.11.8 (2016-02-25)
-------------------

- Determine XML reference attribute ``type`` from MIME if image filename has no
  extension (BUG-357).


2.11.7 (2016-02-22)
-------------------

- Move ``MemoryFile`` to zeit.cms.


2.11.6 (2015-11-17)
-------------------

- Be more defensive about missing meta files when creating variant images.


2.11.5 (2015-10-30)
-------------------

- Use `libmagic` instead of hand-coded zope.app.file heuristics, it supports
  a wider range of mimetypes (e.g. ico which z.c.cp uses for rss feeds).


2.11.4 (2015-10-30)
-------------------

- Use simple heuristic instead of PIL.image.open to determine mime-type
  (since reading PSD files with PIL has been seen to hang indefinitely).


2.11.3 (2015-10-29)
-------------------

- Fix syntax error in image view template (only appears when a copyright as
  ``nofollow`` set).


2.11.2 (2015-09-22)
-------------------

- Store transformed images in memory instead of tempfiles.


2.11.1 (2015-09-18)
-------------------

- Validate sizes in URLs (and ignore zero and negative numbers).


2.11.0 (2015-09-18)
-------------------

- Add setting ``size`` to ``legacy-variant-source`` so we don't deliver the
  original images to legacy clients (which don't know to ask for a specific,
  smaller size). (ZON-2236)


2.10.1 (2015-09-17)
-------------------

- Clean up temporary image blob files on abort as well as commit. (ZON-2237)


2.10.0 (2015-09-12)
-------------------

- Use variant image of `default` configuration as master image in frontend to
  preview image enhancements while ignoring cropping due to zoom. (DEV-826)

- Add UI and backend support to adjust variant images regarding their
  brightness, contrast, saturation and sharpness. (DEV-826)

- Disable transparency of variant previews when displaying the master (DEV-910)

- Increase the size of cropper handles, to make it easier to grab the edge of
  the canvas to resize a variant. (DEV-910)

- Automatically switch back to the master image, when the background of the
  variant editor was clicked. (DEV-910)

- Show that the focuspoint can be dragged by changing cursor to grab. (DEV-910)


2.9.0 (2015-09-08)
------------------

- Add ``fallback_size`` setting for variants, also available as
  ``fallback_width`` and ``fallback_height`` (ZON-2145).

- Avoid ``KeyError`` for Variants that are no longer valid, i.e. those that are
  missing from the XML config and are only present in the DAVProperty (DEV-910)


2.8.0 (2015-08-27)
------------------

- Support ``aspect_ration="original"`` in variant configuration (DEV-923).

- Handle missing dublincore times (ZON-2062).


2.7.2 (2015-08-14)
------------------

- Enable progressive jpeg encoding (ZON-2019).


2.7.1 (2015-08-04)
------------------

- Only change default tab to new editor if the feature toggle is present.


2.7.0 (2015-08-03)
------------------

- Set uniqueId on variant-generated images.


2.6.2 (2015-08-03)
------------------

- Handle wrongly mapped legacy variants.


2.6.1 (2015-07-31)
------------------

- Variants UI Styling updates by jpfn.


2.6.0 (2015-07-30)
------------------

- Ignore invalid image size specifications. (ZON-1586)

- Adjust variants and groups to friedbert's needs, e.g. limit default sizes
    to largest max_size, always produce a master_image, configure pillow
    encoder settings. (ZON-1586)


2.5.2 (2015-07-06)
------------------

- Set zoom and focuspoint of Variant sizes using a rectangular UI. (DEV-827)


2.5.1 (2015-06-23)
------------------

- Change name of thumbnail traverser so it does not conflict with the
  ``thumbnail`` view used by zeit.find.


2.5.0 (2015-06-19)
------------------

- Add bw-compat for CP editor: return old on-disk variants for new syntax
  (DEV-783).

- Go to edit UI after adding an image group (DEV-798).

- Add `IImage.ratio`.


2.4.0 (2015-06-18)
------------------

- Access size of a Variant by giving name and size in URL, e.g.
  ``cinema__100x200``, introduce ``variant_url`` method to generate such URLs.
  (DEV-782)
  * New product config setting ``zeit.content.image:variant-secret``. If given,
    variant URLs are generated and require a signature (to prevent URL
    spoofing).

- Resize (and reposition if target size has a different ratio than the variant)
  the generated variant image according to the target size parameter in the URL
  (DEV-796).

- Support bw-compat mapping of old cropped image names to variants (DEV-783).
  * New config file: ``/data/image-variants-legacy.xml``, for
    ``zeit.content.image:legacy-variant-source``

- Read attributes for ``z.c.image.variant.Variant`` from XML using it's schema
  rather relying on manual type conversion. (DEV-786)

- Generate thumbnail images (for variants editor, cp editor etc.) from a
  smaller image instead of the master image for better performance (DEV-797).


2.3.0 (2015-06-09)
------------------

- Introduce new cropping UI with focus points (UI has feature toggle
  ``zeit.content.image.variants``) (DEV-779).
  * New config file: ``/data/image-variants.xml``, for ``zeit.content.image:
    variant-source``

- Add validation rules for ImageGroup to check on publish that important
  image sizes were created. (DEV-790).

- Update workflow adapter to display validation errors on publish (DEV-22).


2.2.7 (2015-03-17)
------------------

- Add ``suppress_errors`` parameter to ``IReference.update_metadata`` (VIV-629).


2.2.6 (2014-12-17)
------------------

- Update tests since mock connector now yields trailing slashes for folder ids
  (FRIED-37).


2.2.5 (2014-12-17)
------------------

- Allow suppressing errors that are due to missing metadata files (VIV-629).


2.2.4 (2014-11-14)
------------------

- Extend behaviour of apply action in form by overwriting the action from zope,
  rather using our custom applyChanges semantic that we just removed (VIV-516).


2.2.3 (2014-10-21)
------------------

- Update references when moving objects (WEB-298).

- Update dependency to ZODB-4.0.


2.2.2 (2014-09-18)
------------------

- Put a ghost in the workingcopy for new imagegroups (VIV-489).


2.2.1 (2014-07-17)
------------------

- Use <div class="inline-form"> instead of a nested <form> for reference
  details (VIV-428).

- Fix "change copyright" icon.


2.2.0 (2014-05-22)
------------------

- Add ``IImage.format`` helper property (VIV-385).


2.1.1 (2014-05-09)
------------------

- Fix bug in IImageMetadata declaration: ``caption`` should not use a special
  missing value (VIV-377).


2.1.0 (2014-04-22)
------------------

- Display original caption in reference details (VIV-365).

- Rewrite links from www.zeit.de to xml.zeit.de (VIV-263).
  NOTE: This functionality is still disabled, since the frontend
  does not interpret rewritten links correctly yet.


2.0.0 (2014-03-10)
------------------

- Provide ImageReference that allows overriding caption, alt and title locally
  (VIV-305).

- Extracted from zeit.cms egg.


zeit.content.infobox changes
============================

1.25.3 (2019-03-29)
-------------------

- PERF: Don't grok browser packages by default


1.25.2 (2018-10-05)
-------------------

- ZON-3312: Remove obsolete asset badges


1.25.1 (2018-09-03)
-------------------

- BUG-953: Disable setting channel from ressort for infoboxes


1.25.0 (2017-08-10)
-------------------

- ARBEIT-96: Move debate interface und its dav property to z.c.infobox
  because it is use in z.arbeit und z.campus


1.24.1 (2016-08-23)
-------------------

- Use asset instead of content workflow for infoboxes. (ZON-3247)


1.24.0 (2016-04-21)
-------------------

- Add optional ``ressort`` setting to infobox, so they can be marked
  for Campus. (ZON-2491)


1.23.6 (2012-03-06)
-------------------

- Fixed the existence test for security declarations. (#10363)


1.23.5 (2011-11-24)
-------------------

- Make infobox an IXMLContent. It is expected from content to implement
  ICMSContent (which is implied in IXMLContent). (#10017)


1.23.4 (2011-11-13)
-------------------

- Fix brown bag release


1.23.3 (2011-11-13)
-------------------

- Define security for InfoboxReference (for #8412).


1.23.2 (2010-05-03)
-------------------

- Using versions from the ZTK.


1.23.1 (2010-03-10)
-------------------

- Change the way asset interfaces are registered. This fixes isolation problems
  during tests (#6712).

1.23 (2009-07-28)
-----------------

- Infobox-Source zum Filtern per Suche angepasst (#4499).

1.22.2 (2009-06-08)
-------------------

- Tests fÄĹşr neuen WYSIWYG-Konverter angepasst.

1.22.1 (2009-06-05)
-------------------

- Registrierung via TypeDeclaration

1.22 (2009-05-28)
-----------------

- Aus zeit.cms extrahiert.


zeit.content.link changes
=========================

2.2.5 (2019-03-29)
------------------

- PERF: Don't grok browser packages by default


2.2.4 (2018-10-05)
------------------

- ZON-3312: Remove deprecated fields from ICommonMetadata


2.2.3 (2018-08-20)
------------------

- FIX: Use default value for year und volume


2.2.2 (2018-08-20)
------------------

- FIX: Add 'year' and 'volume' fields to form


2.2.1 (2018-08-15)
------------------

- FIX: Use teaserTitle for title


2.2.0 (2018-08-06)
------------------

- ZON-4670: Restructure link object ui


2.1.8 (2017-08-07)
------------------

- ZON-4006: Update to mobile field split


2.1.7 (2017-05-22)
------------------

- ZON-3917 remove bigshare button checkbox


2.1.6 (2016-09-26)
------------------

- Update to `zeit.cms >= 2.90`.


2.1.5 (2016-09-16)
------------------

- ZON-3318: Remove bigshare buttons from link form.


2.1.4 (2016-09-14)
------------------

- ZON-3318: Support bigshare buttons.


2.1.3 (2016-08-09)
------------------

- Ensure fw-compat for mobile push notifications, since `parse` will be
  removed in 2017. (ZON-3213)


2.1.2 (2015-04-15)
------------------

- Undo 2.1.1, it was a misunderstanding.


2.1.1 (2015-04-15)
------------------

- Add feature toggle ``zeit.push.social-form`` for social media form fields.


2.1.0 (2015-03-05)
------------------

- Configure a source for blogs
- Add a property, which matches the URL with the blog source


2.0.4 (2014-12-17)
------------------

- Update XMLReferenceUpdater API (VIV-629).


2.0.3 (2014-11-14)
------------------

- Push the URL of the target object, not the link object itself (VIV-516).

- Remove ``deeplink_url`` from forms (VIV-553).


2.0.2 (2014-10-21)
------------------

- Add social media section to edit form (VIV-516).


2.0.1 (2014-05-22)
------------------

- Remove freetext author field from forms (VIV-394).


2.0.0 (2014-03-10)
------------------

- Extracted from zeit.cms egg.


zeit.content.modules changes
============================

1.3.5 (2019-03-29)
------------------

- PERF: Perform vivi-only import only when needed, to improve zeit.web
  startup performance


1.3.4 (2019-03-05)
------------------

- FIX: Don't apply lxml.objectify number heuristics to parameter values


1.3.3 (2019-02-21)
------------------

- FIX: Properly separate parameter XML access between embed module instances


1.3.2 (2019-02-19)
------------------

- ZON-2932: Display helptext field of referenced embed object

- ZON-2932: Inject CSS rules into module form (prefixed with module ID)


1.3.1 (2019-02-05)
------------------

- ZON-5113: Bypass zope.security for embed parameters


1.3.0 (2019-02-04)
------------------

- ZON-5113: Implement storing embed parameters in the XML of the module


1.2.0 (2019-01-28)
------------------

- ZON-5112: Allow referencing Embed objects from the rawtext module, not just Text


1.1.1 (2018-08-24)
------------------

- ZON-4843: Add mail_required to Mail module


1.1.0 (2017-10-20)
------------------

- ZON-4227: Implement mail module


1.0.0 (2017-10-19)
------------------

- Initial release, extracted from zeit.content.article and zeit.content.cp


zeit.content.portraitbox changes
================================

1.22.15 (2019-03-29)
--------------------

- PERF: Don't grok browser packages by default


1.22.14 (2018-10-05)
--------------------

- ZON-3312: Remove obsolete asset badges


1.22.13 (2016-09-26)
--------------------

- Update to `zeit.cms >= 2.90`.


1.22.12 (2014-12-17)
--------------------

- Update tests since mock connector now yields trailing slashes for folder ids
  (FRIED-37).


1.22.11 (2014-03-10)
--------------------

- zeit.content.image has its own egg now.


1.22.10 (2012-03-06)
--------------------

- Fixed the existence test for security declarations. (#10363)


1.22.9 (2011-12-01)
-------------------

- Update to use etree instead of objectify for HTML conversion/wysiwyg
  (via #10027).



1.22.8 (2011-11-24)
-------------------

- Make portraitbox an IXMLContent. It is expected from content to implement
  ICMSContent (which is implied in IXMLContent). (#10017)

1.22.7 (2011-11-13)
-------------------

- Fix brown bag release


1.22.6 (2011-11-13)
-------------------

- Define security for PortraitboxReference (for #8412).

- Simplified tests and removed footnote (#7844).

- Fix security related test (#9457).


1.22.5 (2010-05-03)
-------------------

- Using versions from the ZTK.


1.22.4 (2010-03-10)
-------------------

- Change the way asset interfaces are registered. This fixes isolation problems
  during tests (#6712).

1.22.3 (2009-08-18)
-------------------

- Tests repariert.

1.22.2 (2009-07-28)
-------------------

- Portraitbox-Source zum Filtern per Suche angepasst (#4499).

1.22.1 (2009-06-08)
-------------------

- Registrierung via TypeDeclaration

1.22 (2009-05-28)
-----------------

- Aus zeit.cms extrahiert.


zeit.content.rawxml changes
===========================

0.5.2 (2019-03-29)
------------------

- PERF: Don't grok browser packages by default


0.5.1 (2016-12-15)
------------------

- ZON-3393: Fix interface declaration to not exclude inherited interfaces


0.5.0 (2016-12-06)
------------------

- ZON-3393: Add marker interface ``IUserDashboard``.


0.4.3 (2015-06-09)
------------------

- Register RawXML as a CMS content type.


0.4.2 (2014-12-17)
------------------

- Update XMLReferenceUpdater API (VIV-629).


0.4.1 (2014-01-07)
------------------

- Use TypeDeclaration for RawXML objects instead of the old
  two-separate-adapters API.


0.4.0 (2011-06-20)
------------------

- RawXML implements the IDAVContent interface now which is required to put
  instances into the DAV (#8998).
- Remove unneeded omitRootOnSyndicate property (#9095).


0.3.5 (2010-05-03)
------------------

- Using versions from the ZTK.


0.3.4 (2010-03-10)
------------------

- Fix tests after decentral syndication was disabled by default (#6878).


0.3.3 (2009-08-18)
------------------

- Tests repariert.


0.3.2 (2009-05-15)
------------------

- Reigistrierung des locale-Verzeichnisses entfernt.

0.3.1 (2009-05-15)
------------------

- Alle ``test.py`` nach ``tests.py`` umbenannt.

- Keine eigene Translationdomain mehr, Übersetzungen via zeit.locales.

0.3 (2008-11-25)
----------------

- Icon wird in der richtigen Größe dargestellt (18x18).
- Default-View hinzugefügt (Bug #4463).

0.2.1 (2008-11-20)
------------------

- Kein Test-Extra
- Extra SecurityPolicy


0.2 (2008-09-16)
----------------

- Aktualisiert auf zeit.cms 1.1.10 mit Syntax-Highlighting

0.1 (2008-08-28)
----------------

- Erstes release.


zeit.content.text changes
=========================

2.4.7 (2019-03-29)
------------------

- PERF: Don't grok browser packages by default


2.4.6 (2019-02-26)
------------------

- ZON-2932: Restore filename field after 2.4.5


2.4.5 (2019-02-25)
------------------

- ZON-2932: Move parameter fields for embeds to their own tab


2.4.4 (2019-02-19)
------------------

- ZON-2932: Add fields for helptext (IMemo) and vivi_css to embed

- ZON-2932: Move IText display widget back here; zeit.cms had too many
  unwanted side effects


2.4.3 (2019-02-15)
------------------

- ZON-5113: Use unicode_literals for parameter definitions, since
  IDAVToken breaks on bytestrings (e.g. in Choice/source values)


2.4.2 (2019-02-07)
------------------

- MAINT: Move IText display widget to zeit.cms


2.4.1 (2019-02-07)
------------------

- ZON-5113: Allow declaring schema fields as OrderedDict


2.4.0 (2019-02-04)
------------------

- ZON-5113: Implement defining schema fields for embed parameters with
  a Python snippet


2.3.0 (2019-01-28)
------------------

- ZON-5112: Add own content type for embeds


2.2.1 (2018-01-09)
------------------

- TMS-134: Update content base class after zeit.cms API change


2.2.0 (2017-08-07)
------------------

- ZON-4007: Add jinja template content type.


2.1.0 (2016-10-19)
------------------

- ZON-3377: Add python script content type (without any UI so far).


2.0.4 (2016-03-22)
------------------

- Configure default view properly.


2.0.3 (2016-03-10)
------------------

- Improve wording (ZON-2826).


2.0.2 (2016-03-03)
------------------

- Add text source for references


2.0.1 (2014-10-21)
------------------

- Update dependency to ZODB-4.0.


2.0.0 (2014-03-10)
------------------

- Extracted from zeit.cms egg.


zeit.content.video changes
==========================

3.1.4 (2019-03-29)
------------------

- PERF: Don't grok browser packages by default


3.1.3 (2018-11-20)
------------------

- ZON-3312: Remove obsolete IVideoAsset


3.1.2 (2018-10-05)
------------------

- ZON-3312: Remove deprecated fields from ICommonMetadata, asset badges


3.1.1 (2018-09-05)
------------------

- ZON-4894: Remove solr support


3.1.0 (2018-06-18)
------------------

- MAINT: No longer use separate config file for video series


3.0.3 (2018-05-29)
------------------

- TMS-227: Update to changed CommonMetadata.serie implementation


3.0.2 (2018-01-30)
------------------

- BUG-841: Disable setting channel from ressort for videos/playlists


3.0.1 (2017-12-05)
------------------

- FIX: Repair solr tests


3.0.0 (2017-11-17)
------------------

- BUG-747: Read media urls (still image, rendition sources etc.) from
  a live API, since they are not infinitely valid (at least for Brightcove)


2.9.0 (2017-10-04)
------------------

- ZON-3409: Move from remotetask to celery


2.8.2 (2017-08-09)
------------------

- ZON-2752: Show `has_advertisement` in form


2.8.1 (2017-08-09)
------------------

- ZON-2752: Respect `has_advertisement` default True


2.8.0 (2017-08-08)
------------------

- ZON-2752: Add `has_advertisement` field


2.7.6 (2017-08-07)
------------------

- ZON-4006: Update to mobile field split


2.7.5 (2017-07-18)
------------------

- BUG-500: Update to new dependency API


2.7.4 (2017-07-07)
------------------

- ZON-3983: Update to SerieSource API change


2.7.3 (2017-05-22)
------------------

- ZON-3917 remove bigshare button checkbox


2.7.2 (2017-01-18)
------------------

- ZON-3576: Add commentsPremoderate property


2.7.1 (2016-09-29)
------------------

- Hide bigshare buttons.


2.7.0 (2016-09-27)
------------------

- ZON-3278: Allow to share video via social media.

- ZON-3278: Extract computation of SEO slug from zeit.web.


2.6.1 (2016-09-02)
------------------

- Fix brown-bag 2.6.0 that needlessly depended on an unreleased zeit.cms


2.6.0 (2016-09-02)
------------------

- Add ``video_still_copyright`` and ``authorships`` to ``IVideo``. (ZON-2409)


2.5.3 (2016-04-18)
------------------

- Don't load Zope/UI specific ZCML in the model ZCML


2.5.2 (2015-07-24)
------------------

- Use proper serie source for videos (ZON-1464).


2.5.1 (2015-06-25)
------------------

- Remove feature toggle ``zeit.content.cp.automatic`` (DEV-832).


2.5.0 (2015-06-09)
------------------

- Add a duration attribute to video renditions (ZON-1566).

- Add a source for playlists. (DEV-300)


2.4.0 (2015-04-17)
------------------

- Support serie objects for video series, too (ZON-1464).


2.3.3 (2015-04-15)
------------------

- Only automatically publish playlists, not any object referencing a video
  (BUG-235).


2.3.2 (2015-02-20)
------------------

- Enable auto-cp fields on video forms (VIV-654).


2.3.1 (2015-02-16)
------------------

- Register default view properly (BUG-86).


2.3.0 (2015-01-29)
------------------

- Set video duration as rendition property (ZON-1275).


2.2.11 (2015-01-21)
-------------------

- Add subtitle to form (VIV-648).


2.2.10 (2014-12-17)
-------------------

- Update XMLReferenceUpdater API (VIV-629).


2.2.9 (2014-10-21)
------------------

- When publishing a video, don't publish dependent content inside the test
  folder (VIV-289).


2.2.8 (2014-06-05)
------------------

- Use gocept.httpserverlayer.custom to avoid port collisions in tests.


2.2.7 (2014-04-22)
------------------

- Removed module file erroneously left over after an earlier merge.


2.2.6 (2014-01-20)
------------------

- Update to new MultiResource API (VIV-282).


2.2.5 (2014-01-08)
------------------

- Fix missing imports.


2.2.4 (2013-09-24)
------------------

- Remove unittest2, we have 2.7 now


2.2.3 (2013-08-14)
------------------

- Update to Python-2.7 and ZTK-1.1.5 (#11005).


2.2.2 (2013-07-08)
------------------

- Fix tests to deal with required keywords (#12478).


2.2.1 (2013-07-01)
------------------

- Don't use special declaration for keywords, this has become unnecessary since
  articles can get tags from the whitelist now, too (#11421).


2.2 (2013-04-23)
----------------

- Video uses autocomplete/whitelist keywords.
- UI improvements: specialized description for landing zone, use large image
  for object details (#11568, 11709).


2.1.1 (2012-01-18)
------------------

- Removed untested, non-working code which went accidentally into the last
  release.


2.1.0 (2012-01-17)
------------------

- Add IPublicationDependecies so that playlists are published when videos
  contained in them are published (#10042).
- Add renditions object and MultiBaseProperty to have different renditions for
  a video


2.0.4 (2011-12-01)
------------------

- Fix XMLReferenceUpdater so it doesn't grow lots of superfluous video-still
  nodes (#10028).


2.0.3 (2011-11-24)
------------------

- Fix access to `id_prefix` for videos and playlists (#10015)


2.0.2 (2011-11-23)
------------------

- Fix 2.0.1 which misses serie.xml file


2.0.1 (2011-11-23)
------------------

- Use special video series.

- Hide the subtitle field.


2.0 (2011-11-13)
----------------

- Total rewrite. For earlier versions, see the subversion repository at
  <https://code.gocept.com/svn/gocept-int/zeit.cms/zeit.content.video/>.


zeit.content.volume changes
===========================

1.11.4 (2019-03-29)
-------------------

- PERF: Don't grok browser packages by default


1.11.3 (2019-03-21)
-------------------

- FIX: Don't be too strict with urls of performing articles


1.11.2 (2019-03-05)
-------------------

- FIX: Add additional filter constraint correctly


1.11.1 (2019-03-05)
-------------------

- FIX: Fix elastic filter contstraint for volume access query


1.11.0 (2019-03-04)
-------------------

- ZON-4938: Don't change access for performing articles


1.10.0 (2018-08-20)
-------------------

- ZON-4806: Switch volume queries from solr to ES


1.9.1 (2018-02-01)
------------------

- MAINT: Make number of empty columns for toc configurable


1.9.0 (2017-10-04)
------------------

- ZON-3409: Move from remotetask to celery


1.8.1 (2017-08-09)
------------------

- BUG-757: Store multi publish errors in volume object objectlog


1.8.0 (2017-08-07)
------------------

- ZON-3860: Show lightbox with spinner while publishing content


1.7.7 (2017-07-18)
------------------

- BUG-500: Update to new dependency API


1.7.6 (2017-07-07)
------------------

- Add another tab to toc format


1.7.5 (2017-06-29)
------------------

- FIX: Add volume object to mass publication


1.7.4 (2017-06-09)
------------------

- ZON-3810: Publish boxes of articles as well, if the content of the volume is
  published

- ZON-3951: Make date_digital_published required


1.7.3 (2017-05-22)
------------------

- BUG-682: Add teaserSupertitle so displaying a volume object teaser
  in the CP editor looks nicer


1.7.2 (2017-05-04)
------------------

- BUG-711: Friedbert preview doesn't render article with wrong volume reference


1.7.1 (2017-05-03)
------------------

- ZON-3384: Don't publish content in change_contents_access


1.7.0 (2017-04-12)
------------------

- ZON-3384: Change access value after x weeks


1.6.1 (2017-04-07)
------------------

- FIX: if the product id wasn't found in the products.xml, the toc contained only an empty string

- Change toc format


1.6.0 (2017-04-04)
------------------

- ZON-3841: Add volume covers publication dependency

- ZON-3687: Move default string for volume teaser text here from zeit.web


1.5.1 (2017-03-22)
------------------

- ZON-3742: Add access field to table of contents entry


1.5.0 (2017-03-01)
------------------

- ZON-3447: Publish all content for volume


1.4.0 (2017-02-08)
------------------

- ZON-3533: Support dependent products

- ZON-3535: Covers per product

- BUG-633: Make teaserText overridable on volume reference


1.3.2 (2017-01-12)
------------------

- Minor improvements and changes to the table of contents


1.3.1 (2017-01-11)
------------------

- Store volume properties in DAV like CommonMetadata does, not in the
  XML body (unclear why that ever was different).


1.3.0 (2016-12-29)
------------------

-  ZON-3367: Table of content functionality


1.2.2 (2016-10-19)
------------------

- ZON-3377: Create CP along with the Volume object, using a Python
  template script configured in products.xml.


1.2.1 (2016-09-29)
------------------

- Be defensive about finding CP for volume.


1.2.0 (2016-09-26)
------------------

- ZON-3362: Implement ``previous`` and ``next`` using solr.

- ZON-3362: Allow adapting ``IVolume`` to ``ICenterPage`` to find the
  corresponding index page.


1.1.1 (2016-09-07)
------------------

- ZON-3304: Add ``Volume`` to location configured in ``products.xml``.

- ZON-3304: Show meaningful title for ``Volume`` in search results.

- FIX: Adjust interface for ``Volume`` references to expect the container for
  the ``Volume`` reference rather the ``Volume`` itself.


1.1.0 (2016-09-02)
------------------

- ZON-3253: Implement IReference with overridable teaserText.

- FIX: Make sure that the ``ICMSContent`` belongs to a print product before adapting
  it to the associated ``Volume``.


1.0.0 (2016-08-22)
------------------

- Initial release.


zeit.edit changes
=================

2.17.2 (2019-03-29)
-------------------

- PERF: Don't grok browser packages by default


2.17.1 (2018-06-06)
-------------------

- MAINT: Start busy indicator for "simple" editor reloads as well


2.17.0 (2017-11-01)
-------------------

- MAINT: Replace complicated register_element_factory with simpler
  grokked baseclass.
  The former could register one element for multiple containers in one go,
  but we don't use this anymore since the 2015 relaunch (all areas in
  z.c.cp are now the same).


2.16.2 (2017-10-20)
-------------------

- FIX: Enable sending no-cache headers for the article/cp main edit view


2.16.1 (2017-10-19)
-------------------

- MAINT: Remove superfluous i18n reimport


2.16.0 (2017-09-07)
-------------------

- ZON-4206: Introduce `IContainer.filter_values` and `find_first`


2.15.1 (2017-08-07)
-------------------

- MAINT: Remove superfluous IEditable interface, it's only used for
  registering one view, which can more clearly be done directly


2.15.0 (2017-06-09)
-------------------

- ZON-3948: Dont publish content if it is in a test folder

- ZON-3810: Add IElementReferences Interface


2.14.1 (2016-09-26)
-------------------

- Update to `zeit.cms >= 2.90`.


2.14.0 (2016-06-27)
-------------------

- Add reload() signal helper to forms, not only actions (ZON-3167).


2.13.6 (2016-06-06)
-------------------

- Move article-specific styles to z.c.article.


2.13.5 (2016-04-29)
-------------------

- Raise correct exception (KeyError) for failed container access via int


2.13.4 (2016-04-18)
-------------------

- Don't load Zope/UI specific ZCML in the model ZCML


2.13.3 (2016-01-22)
-------------------

- Fix overly generic CSS selector that messed up non-article fieldset/legend styling


2.13.2 (2016-01-20)
-------------------

- Replace gocept.cache.method with dogpile.cache (ZON-2576).


2.13.1 (2015-10-06)
-------------------

- Don't to dispatch events that happen to the content object (like being added
  to the Workingcopy) to their IElement children.


2.13.0 (2015-08-24)
-------------------

- Make library tabs accessible as ``zeit.edit.library.tabs`` (DEV-853).

- Make sorting of library adapters overridable (DEV-853).

- Use better repr for containers, too.


2.12.3 (2015-08-04)
-------------------

- Improve repr output.


2.12.2 (2015-08-04)
-------------------

- Add more descriptive repr to ``Element``.


2.12.1 (2015-07-31)
-------------------

- Support save without close in TabbedLightboxForm (DEV-108).


2.12.0 (2015-06-09)
-------------------

- Extend ValidatingWorkflow to forward validation errors to the Publish view
  that displays those errors to the user. (DEV-22)


2.11.2 (2015-05-04)
-------------------

- Replace MochiKit $$ with jQuery, which is *much* faster in Firefox.

- Implement shortcut in IElement.__eq__, use __name__ if present and use
  XML comparison only as a fallback.


2.11.1 (2015-04-28)
-------------------

- Add hashing methods to Areas, Regions and TeaserBlocks that utilize their
  respective uniqueIds (ZON-1541).

- Display form errors correctly in TabbedLightboxForm (don't lose the tabs).


2.11.0 (2015-03-18)
-------------------

- Implement ``IContainer.insert`` to fix issues with wrong order during
  ``ObjectAdded`` events. (DEV-53)


2.10.0 (2015-03-13)
-------------------

- Use special ``OrderUpdated`` event instead of generic ``ContainerModified``.


2.9.0 (2015-03-09)
------------------

- Implement landing zone behaviour for moving elements (DEV-53).

- Add ``IContainer.get_recursive`` and ``create_item`` (DEV-53).

- Send ObjectMovedEvent from ``IContainer.add`` if applicable (DEV-53).

- Do nothing when no signal was emitted rather reloading the whole editor.
  (Fixes issues with DEV-35 and DEV-53)

- Shorten wait time until the `busy` overlay is shown (DEV-641).


2.8.0 (2015-01-14)
------------------

- Re-introduce ``override_options`` parameter to
  ``zeit.edit.sortable.Sortable`` since zeit.content.cp-2.x still needs it.


2.7.0 (2015-01-08)
------------------

- Extract body traverser mechanics from article/cp.


2.6.1 (2014-12-17)
------------------

- Ignore missing ``block_params`` instead of breaking.


2.6.0 (2014-12-17)
------------------

- Extend API of ``zeit.edit.sortable.Sortable`` to make a difference between
  parent with meta data and child container. (VIV-627)

- Extend API of `zeit.edit.browser.LandingZone` to insert explicitly at the top
  or after a given UUID. (VIV-621)

- Extend CSS selector for landing areas to style landing zones of
  `zeit.content.cp.IRegion` and `zeit.content.cp.IArea`. (VIV-614)

- Fix bug in `IBlock` comparison, we need to do an in-depth xml comparison.

- Make it possible to overwrite the library name for landing zones. (VIV-612)

- Make it possible to use another JSON view to get all droppables. (VIV-612)

- Element factories can now tell which interface is implemented by the element
  that will be created. (VIV-633)

- Landing Zones accept block_params via request, which are written onto the
  created element. (VIV-633)

- Add fine grained control for configuration of block factories. (VIV-633)

- Add new step for landing zones which checks invariants of the object that
  will be created. (VIV-618)


2.5.0 (2014-11-14)
------------------

- Move the additional ``Droppables.prepare`` step to the article editor where
  it belongs, otherwise landing zones are not removed properly (VIV-405).


2.4.2 (2014-10-21)
------------------

- Add event when dragging modules, so the content-editable can save itself and
  restore its landing zones (VIV-405).


2.4.1 (2014-10-06)
------------------

- Fix CSS issue that caused some inline form input fields to be inaccessible,
  since they were overlayed by a div (VIV-524).

- Update dependency to ZODB-4.0.


2.4.0 (2014-09-18)
------------------

- Store folding state globally, not per article (VIV-481).

- Add rule function ``scheduled_for_publishing`` (VIV-494).

- Provide old order value in modified event on ``updateOrder`` (VIV-497).

- Use trashcan icon for delete instead of cross (VIV-493).


2.3.4 (2014-08-29)
------------------

- Exclude list widgets from ``get_all_input_even_if_invalid``.


2.3.3 (2014-06-20)
------------------

- Fix icon on retract button (VIV-361).


2.3.2 (2014-05-09)
------------------

- Styling tweak: Make CSS selector for object details toggle button more
  specific (VIV-359).


2.3.1 (2014-04-28)
------------------

- Add safety belt for replace to not return undefined.


2.3.0 (2014-04-22)
------------------

- Add IContainer.slice() method (VIV-11795).

- Fix CSS issue that caused wrong clipping of autocomplete lists (VIV-358).


2.2.1 (2014-03-14)
------------------

- Fix bug that added more and more signal handlers upon each block reload.


2.2.0 (2014-03-10)
------------------

- Implement uniqueId resolving for elements (VIV-305).


2.1.8 (2014-02-10)
------------------

- Use Fanstatic instead of zc.resourcelibrary (VIV-296).


2.1.7 (2014-01-20)
------------------

- Support nesting of InlineForms.

- Render tabs in lightboxes each time the tab is activated, otherwise the
  javascript for the forms is not updated and the form does not work after
  switching tabs (VIV-280).


2.1.6 (2014-01-07)
------------------

- Update tests to work with grokcore.component-2.5.


2.1.5 (2013-09-24)
------------------

- Remove unittest2, we have 2.7 now


2.1.4 (2013-08-27)
------------------

- Register an UnknownBlock as a catch-all for any tags we don't have an
  IElement registration (#12536).


2.1.3 (2013-07-08)
------------------

- Performance improvement: Determine globs only once per block, not everytime
  again for each rule. (#12555)


2.1.2 (2013-07-05)
------------------

- Catch errors in viewlet to prevent editor from breaking completely. (#12530)


2.1.1 (2013-07-01)
------------------

- Include "to top" links for foldable form groups into the markup (#12255).


2.1.0 (2013-05-29)
------------------

- Perform search on page load only inside workingcopy (#12404).


2.0 (2013-04-23)
----------------

- Initial release.



zeit.find changes
=================

3.0.9 (2019-03-29)
------------------

- PERF: Don't grok browser packages by default


3.0.8 (2019-02-04)
------------------

- BUG-1049: Also include the previously used type "text" when type
  "embed" is selected


3.0.7 (2019-01-30)
------------------

- BUG-1049: Replace type filter "text" with the new "embed"


3.0.6 (2019-01-14)
------------------

- BUG-1042: Don't treat bools like ints


3.0.5 (2019-01-10)
------------------

- BUG-1042: Apply string conversion only to numbers, otherwise it
  destroys other useful types like lists


3.0.4 (2019-01-09)
------------------

- BUG-1042: Convert all search result fields to string, since json-template breaks otherwise


3.0.3 (2018-12-18)
------------------

- BUG-1001: Remove z-index from resetbutton


3.0.2 (2018-09-03)
------------------

- TMS-239: Add z.c.advertisement to the list of filterable content types


3.0.1 (2018-08-16)
------------------

- TMS-214: Search for "all" given terms by default.


3.0.0 (2018-08-14)
------------------

- TMS-214: Switch to elasticsearch

- TMS-214: Add "reset form" button

- TMS-214: Remove related section, hit counter from search results


2.7.3 (2018-05-29)
------------------

- FIX: Replace obsolete filter `product_text:News` with `product_id` (dpa/afp/etc)

- MAINT: Move autocomplete source query view to zeit.cms


2.7.2 (2017-10-04)
------------------

- ZON-3409: Move from remotetask to celery


2.7.1 (2016-09-26)
------------------

- Update to `zeit.cms >= 2.90`.


2.7.0 (2016-08-04)
------------------

- ZON-3163: Expose zeit.find.search.DEFAULT_RESULT_FIELDS


2.6.3 (2016-07-18)
------------------

- MAINT: Change permission for simple_find to public


2.6.2 (2016-05-18)
------------------

- BUG-418: Fix dropdown handling for FF46.


2.6.1 (2016-04-18)
------------------

- Don't load Zope/UI specific ZCML in the model ZCML.


2.6.0 (2015-06-18)
------------------

- Pass additional keyword parameters to ``zeit.find.search.search`` through to
  pysolr.


2.5.0 (2015-05-04)
------------------

- Add date range for one day, as required by zeit.web (ZON-1667).

- Replace MochiKit $$ with jQuery, which is *much* faster in Firefox.


2.4.0 (2015-03-09)
------------------

- Add parameter for number of rows (DEV-621).


2.3.2 (2015-03-03)
------------------

- Adapt to zeit.cms series source API changes. (ZON-1464)


2.3.1 (2014-08-29)
------------------

- Fix brown-bag release.


2.3.0 (2014-08-28)
------------------

- Add ``additional_result_fields`` parameter to ``zeit.find.search.search``.


2.2.6 (2014-06-05)
------------------

- Use plone.testing-based layers.


2.2.5 (2014-05-22)
------------------

- Remove workaround for old solr version that replaced umlauts with normal
  characters (i.e. ä->a), so searching for authors with umlauts works again
  (VIV-238).


2.2.4 (2014-03-10)
------------------

- zeit.content.image has its own egg now.


2.2.3 (2014-02-10)
------------------

- Use Fanstatic instead of zc.resourcelibrary (VIV-296).


2.2.2 (2014-01-07)
------------------

- Don't calculate preview URL ourselves, simply redirect to the preview-view
  (VIV-251).

- Update to navigation source being contextual.


2.2.1 (2013-09-24)
------------------

- Remove unittest2, we have 2.7 now


2.2.0 (2013-05-29)
------------------

- Provide parameter whether to perform last search on pageload or not (#12404).


2.1 (2013-04-23)
----------------

- Replaced python-cjson with standard library equivalent.


2.0 (2013-04-23)
----------------

- Less flaky autocomplete source (#12082)
- Moved reusable styles to zeit.cms.
- Add 'type' field to search result (for #9390).
- Lowercase autocomplete query and use right truncation to improve search
  results.
- Provide JS-API to filter searches for types (for #10698).
- new suggest method in search model

0.23.0 (2011-08-12)
-------------------

- Newsticker no longer hold the ressort "News", therefore another filter was
  added to check for product_text as well.


0.22.0 (2011-06-20)
-------------------

- Filter for raw-tag content added (#9096).

- Update our usage of product, since it's a whole object now, not just an id
  (for #9033).


0.21.0 (2010-08-16)
-------------------

- Reichweite in der Suche anzeigen (#7860).

- Vorschau-Link funktioniert wieder und wird nur angezeigt, wenn eine Vorschau
  vorhanden ist (#7858).

0.20.3 (2010-08-09)
-------------------

- Für Selenium-Tests wird nun ``gocept.selenium`` verwendet (#7549).


0.20.2 (2010-07-12)
-------------------

- Updated to new API (#7030)


0.20.1 (2010-04-12)
-------------------

- URLs für grpahical-preivew-url können nun auch vollaufgelöst sein
- Using versions from the ZTK.


0.20.0 (2010-03-10)
-------------------

- Ticker-Meldungen werden normalerweise ausgeblendet (#6914).

- Die Datumsfilter hängen jetzt von der aktuellen Uhrzeit und nicht mehr von
  der Zeit des letzten Server-Neustarts ab (#6922).


0.19.0 (2009-12-18)
-------------------

- Im Volltext ist die vollständige Solr-Syntax verfügbar
  <http://lucene.apache.org/java/2_4_0/queryparsersyntax.html> (#5822).
- 'Für diese Seite' entfernt (#6379).

0.18.0 (2009-10-19)
-------------------

- Die Typen-Suche ist jetzt in einer eigenen Box (#6351).

- Die letzte Suche wird nur noch gespeichert, wenn sich auch etwas geändert
  hat. Durch weniger Schreiboperationen wird die Gesamtgeschwindigket erhöht.

- Suche initial nach Datum sortiert (#6352).

0.17.0 (2009-10-12)
-------------------

- Style-Fixes

- Ausklappzustand der erweiterten Suche und der Filter wird gespeichert und
  wiederhergestellt (#6272).

0.16 (2009-10-06)
-----------------

- Die Suche zeigt jetzt Thumbnails von Bildern an.
- Die Einstellungen der letzten Suche werden gespeichert (#6017).
- Wenn nach ``*:*`` gesucht wird, wird *immer* nach Datum sortiert.

0.15 (2009-09-21)
-----------------

- Erweiterte Suche nach Product

- Erweiterte Suche nach Serie (#5986)

- Es werden jetzt 50 statt 20 Ergebnisse angezeigt.


0.14 (2009-09-09)
-----------------

- Relateds an Suchergebnissen funktionieren wieder.


0.13 (2009-09-02)
-----------------

- Styling

- Es ist jetzt möglich einen Clip in den Favoriten zu haben, ohne dass die
  Suche kaputt geht (#6163).


0.12 (2009-08-21)
-----------------

- Serie, Teaser-Text und Subtitel wird mit angezeigt (#6024).

0.11 (2009-08-14)
-----------------

- Styling

- Favoriten robuster gegen nicht vorhandene Objekte.

0.10 (2009-08-10)
-----------------

- Die Suche ist nun Startseite des CMS (#5857)

0.9 (2009-08-03)
----------------

- Wenn die erweiterte Suche eingeklappt ist, werden die Kriterien klein, als
  Text dargestellt.

- lucenequery nach zeit.solr verschoben.

- Link zum Objekt im CMS

0.8 (2009-07-28)
----------------

- Objectchooser mit Suche (#4499).

- Suchfeld macht keine Phrasensuche mehr (#5792).

0.7 (2009-07-22)
----------------

- Moved solr connection (via pysolr) to zeit.solr

- Search for content types changed to not transmit all types on each search but
  none when all types should be found.

0.6.1 (2009-06-18)
------------------

- Repackaged (setupools/svn 1.6 problem).

0.6 (2009-06-18)
----------------

- Nur 20 Suchergebnisse anzeigen

- Styling


0.5 (2009-05-09)
----------------

- »Für diese Seite«

- Facetierte Suche

- Filter am Suchergebnis

- Korrekte Typ-Icons.

- Sytling

- Dropdown für Ressort-Auswahl

- Vollständige Typliste in der erweiterten Suche

0.4 (2009-05-26)
----------------

- Anzeige der Anzahl für die facetierte Suche.

- Enter-Taste startet die Suche.

- Relateds in Suchergebnissen

- Veröffentlichungs-Status anzeigen

- Vorschau-Links

- Erweiterte Suche

0.3 (2009-05-17)
-----------------

- Kommunikation mit Solr, d.h. es werden echte Daten angezeigt.

- Alle ``test.py`` nach ``tests.py`` umbenannt.

0.2 (2009-04-30)
----------------

- Suchergebnisse haben jetzt den »Favorite-Star«. Markierte Objekte tauchen im
  Tab »Favoriten« und im Clipboard auf.


0.1 (2009-04-23)
---------------

- Erstes Release: Such-UI mit statischen Daten


zeit.imp changes
================

0.18.1 (2016-09-29)
-------------------

- Only disable zeit.imp menu item, leave the view accessible for emergencies.


0.18.0 (2016-07-26)
-------------------

- Disable zeit.imp for image groups if new variant editor is enabled (ZON-3171)


0.17.2 (2016-01-22)
-------------------

- Fix overly generic CSS spacing selector for widgets


0.17.1 (2015-06-09)
-------------------

- Remove unicode symbol from i18n string, so it can be translated.


0.17.0 (2014-10-21)
-------------------

- Restrict minimum possible zoom to not be smaller than the size of the mask
  (VIV-500).

- Mark center of mask (VIV-501).

- Fix rounding error while zooming: round properly instead of flooring
  (VIV-502).


0.16.1 (2014-07-14)
-------------------

- Fix bug in 0.16.0 that rendered imp unusable for gallery entries.


0.16.0 (2014-05-22)
-------------------

- Support PNG (with alpha) image format (VIV-358).


0.15.2 (2014-03-10)
-------------------

- zeit.content.image has its own egg now.


0.15.1 (2014-02-10)
-------------------

- Use Fanstatic instead of zc.resourcelibrary (VIV-296).


0.15.0 (2014-01-07)
-------------------

- Make available scales and colors context dependent (VIV-260).


0.14.3 (2013-09-24)
-------------------

- Fix event binding for mousemove (#12756).


0.14.2 (2013-08-14)
-------------------

- Update to Python-2.7 and ZTK-1.1.5 (#11005).


0.14.1 (2013-08-07)
-------------------

- Adapt Javascript so it can always be loaded (#11290).


0.14.0 (2012-03-06)
-------------------

- Fixed a test concerning #9608.

- Fixed the expected values when testing the contrast filter. (#10355)

- Fixed the filter value mapping for slider values less than 0.

- Skip a flaky test until we have the Selenium 2 API available. (#10356)


0.13.0 (2010-08-30)
-------------------

- Do no longer try to create 0x0 images.

- Sliders have a much smaller zone of action to allow finer control over the
  result (#4969).

- The mask was usually 1 pixel too wide (#4971).

- When a mask is selected, the image is fit into it (#5549).


0.12.0 (2010-08-09)
-------------------

- Fix tests after product config changes in zeit.cms (#7549).

- Für Selenium-Tests wird nun ``gocept.selenium`` verwendet (#7549).


0.11.0 (2010-05-03)
-------------------

- Es ist jetzt möglich eine leere Rahmen-Datei (colors.xml) zu haben ohne, dass
  IMP kaputt geht (#6974).

- Using versions from the ZTK.


0.10.0 (2009-11-25)
------------------

- Das Bild kann nicht mehr außerhalb der Schnittmaske verschoben oder
  zugeschnitten werden (#4972).


0.9.0 (2009-11-04)
----------------

- Der Bild-Bereich kann gezoomt werden, damit auch sehr große Masken passen.


0.8 (2009-09-04)
----------------

- Palette-Images (#4980) und CMYK-Images (#6171) werden nach RGB konvertiert.

0.7.2 (2009-08-11)
------------------

- Skalieren von großen Bildern funktioniert jetzt zuverlässig (#5957).

0.7.1 (2009-08-11)
------------------

- Einstellungsbreich bekommt eine Scrollbar, wenn der Bildschirm zu klein ist.

0.7 (2009-07-20)
----------------

- Umbauten um IMP mehrfach verwenden zu können (z.B. in der Bildergalerie).

0.6.1 (2009-05-15)
------------------

- Alle ``test.py`` nach ``tests.py`` umbenannt.

- Keine eigene Translationdomain mehr, Übersetzungen via zeit.locales.

0.6 (2009-04-06)
----------------

- Höhere Qualität beim Speichern (80%, two-pass).

0.5 (2009-03-03)
----------------

- Bei Grau-Bildern kann jetzt ein Rahmen eingefügt werden. Bei einem farbigen
  Rahmen wird dieser in den entsprechenden Grauwert umgewandelt.

0.4 (2009-02-20)
----------------

- Es stehen mehrere Rahmenfarben zur Auswahl, die per XML-Datei anpassbar sind
  (colors.xml).
- Markierung auf den Slidern entfernt.
- Slider zeigen jetzt einen Wertebereich von -100 bis 100.
- Reset-Knopf für die Filter.

0.3 (2009-02-05)
----------------

- Selenium-Infrastruktur wurde in den Kern verschoben.
- Bei einem zu kleinen Bildschirm konnten keine Bilder zugeschnitten werden,
  weil die Bilderleiste sich über den Knopf gelegt hatte. Bei kleinen
  Bildschirmen funktioniert es jetzt, sieht aber nicht schön aus (Bug #4651).

0.2 (2009-01-22)
----------------

- Anpassen der Bildposition etc, wenn das Browserfenster die Größe ändert oder
  die Seitenleiste ein- oder ausgefahren wird.
- Extra Berechtigung für das Benutzen.
- Regler für Helligkeit, Kontrast, Schärfe und Farbe.

0.1 (2009-01-19)
----------------

- erstes Release.


zeit.invalidate changes
=======================

0.3.5 (2013-08-14)
------------------

- Update to Python-2.7 and ZTK-1.1.5 (#11005).


0.3.4 (2010-05-03)
------------------

- Using versions from the ZTK.


0.3.3 (2009-10-05)
------------------

- Tests repariert nach Typo-Fix in zeit.connector.

0.3.2 (2009-05-15)
------------------

- Alle ``test.py`` nach ``tests.py`` umbenannt.


0.3.1 (2008-11-20)
------------------

- No test extra.
- Test layer can be torn down.

0.3 (2008-04-04)
----------------

- Added @@invalidate_many to be able to invalidate may resources in one xml-rpc
  call.

0.2 (2008-04-02)
----------------

- @@invalidate returns True on success now.

0.1 (2008-03-25)
----------------

- First release


zeit.magazin changes
====================

1.5.2 (2019-03-29)
------------------

- PERF: Don't grok browser packages by default


1.5.1 (2018-08-06)
------------------

- ZON-4670: Restructrure link ui


1.5.0 (2018-06-26)
------------------

- ZON-4705: Also allow setting IZMOSection via ressort `zeit-magazin`,
  in addition to "everywhere below /zeit-magazin".


1.4.5 (2018-05-17)
------------------

- MAINT: Remove separate preview URL, has been obsolete since the 2015 relaunch


1.4.4 (2017-08-07)
------------------

- ZON-4006: Update to mobile field split


1.4.3 (2017-05-22)
------------------

- ZON-3917 remove bigshare button checkbox


1.4.2 (2016-09-26)
------------------

- Update to `zeit.cms >= 2.90`.


1.4.1 (2016-09-16)
------------------

- ZON-3318: Remove bigshare buttons from link form.


1.4.0 (2016-01-22)
------------------

- Add marker interfaces IZMOLink, IZMOGallery. Add facebook magazin fields to
  their forms (ZON-2397).


1.3.0 (2015-07-24)
------------------

- Move ``template`` and ``layout`` settings to
  ``zeit.content.article.IArticle`` (DEV-801).


1.2.0 (2015-03-11)
------------------

- Add section marker IHamburgSection and IHamburgContent (DEV-645).


1.1.1 (2014-06-05)
------------------

- Use plone.testing-based layers.


1.1.0 (2014-03-24)
------------------

- Add section interface IZMOCenterPage (VIV-345).


1.0.2 (2014-02-10)
------------------

- Fix typo that lead to infloop that prevented setting a header layout
  (VIV-308).

- Update tests to work with WSGI (VIV-295).


1.0.1 (2014-01-20)
------------------

- RelatedBase is now based on MultiResource (VIV-282).


1.0 (2014-01-07)
----------------

- Set up section interfaces: IZMOSection, IZMOContent, IZMOArticle, IZMOFolder,
  IZMOPortraitbox (VIV-252).

- Add fields for template and header layouts for ZMO articles (VIV-241).

- Add field for focussed nextread for ZMO articles (VIV-253).

- Add field longtext for ZMO portrait boxes (VIV-246).


zeit.newsletter changes
=======================

1.5.5 (2019-03-29)
------------------

- PERF: Don't grok browser packages by default


1.5.4 (2018-05-28)
------------------

- BUG-928: Remove separate preview type for newsletters, it's not
  necessary as everything uses zeit.web since 2015


1.5.3 (2018-04-19)
------------------

- OPS-874: Don't traverse newsletter category for indexing in tms/solr


1.5.2 (2017-11-20)
------------------

- BUG-747: Add testlayer for brightcoveplayer


1.5.1 (2017-11-01)
------------------

- MAINT: Update to simplified module registration API


1.5.0 (2017-10-04)
------------------

- ZON-3409: Move from remotetask to celery


1.4.1 (2017-08-07)
------------------

- MAINT: Remove superfluous IEditable interface


1.4.0 (2017-07-18)
------------------

- BUG-512: Mark content as sent even when an error occurs


1.3.6 (2017-07-13)
------------------

- MAINT: Rename navigation source


1.3.5 (2016-09-26)
------------------

- Update to `zeit.cms >= 2.90`.


1.3.4 (2015-06-09)
------------------

- Update to IPublishInfo API changes (DEV-22).


1.3.3 (2015-05-18)
------------------

- Improve renderer error message.


1.3.2 (2015-02-16)
------------------

- Use title of ressort, not machine-readable version (BUG-147).


1.3.1 (2014-11-14)
------------------

- Call apply changes of super class by direct call to the apply action, since
  our custom applyChanges hook is not present in inline forms (VIV-516).


1.3.0 (2014-10-21)
------------------

- Added a new advertisement section (VIV-514).


1.2 (2014-09-23)
----------------

- Honour DailyNL flag on content when populating a newsletter (VIV-506).

- Include all configured ressorts in newsletter even if they end up empty
  (VIV-512).

- Store the newsletter's creation date as the category's last_created marker
  when publishing the newsletter (VIV-510).

- Don't include videos from the playlist that are older than last_created
  (VIV-513).


1.1.0 (2014-07-17)
------------------

- Don't copy advertisement properties to the Newsletter, but always read it
  from the Category (VIV-414).


1.0.0 (2014-06-05)
------------------

- Use gocept.httpserverlayer.custom to avoid port collisions in tests.


1.0.0b2 (2014-05-12)
--------------------

- Add a video group at the end of the newsletter (VIV-349).

- Configure advertisement blocks through the newsletter category, include them
  with the editor (VIV-350).

- Made included ressorts configurable through the newsletter category's UI
  (VIV-351).

- Display teaser images in editor (VIV-356).


1.0.0b1 (2014-03-28)
--------------------

- Configure preview and rendering to use zeit.frontend (VIV-347).

- Use zeit.optivo for sending (VIV-342).

- Make metadata of newsletter category (e.g. Optivo Mandant ID, recipient list
  name, etc.) configurable.

- Prepopulate subject when creating a newsletter.

- Add INewsletter.body property; implement body.values() so that it works
  without keys() (since the ``__name__`` attributes are not present in the
  repository).


0.3.1 (2014-03-10)
------------------

- zeit.content.image has its own egg now.


0.3 (2014-02-10)
----------------

- Use Fanstatic instead of zc.resourcelibrary (VIV-296).


0.2 (2014-01-07)
----------------

- Add upper bound of "now" to query for new content.


0.1 (2013-11-22)
----------------

- first release.


zeit.objectlog changes
======================

1.1.0 (2017-07-18)
------------------

- BUG-345: Implement `IObjectLog.delete`


0.12 (2013-08-19)
-----------------

- Update to Python-2.7 and ZTK-1.1.5 (#11005).


0.11 (2012-12-17)
-----------------

- Added an optional timestamp parameter to the log() method.

- Refactored tests.


0.10 (2011-10-06)
-----------------

- Using versions from the ZTK.

- Added missing import.


0.9 (2009-09-05)
----------------

- Added a method on the log to clean it from old entries.

0.8.1 (2009-05-15)
------------------

- No `extras_require` for tests any more.

- Renamed all ``test.py`` to ``tests.py``

0.8 (2009-04-05)
----------------

- Added missing import in interfaces.

0.7 (2008-12-08)
----------------

- When an object which is passed to ``get_log`` isn't adaptable to
  IKeyReference it is consisdered to not have any logs. This used to raise a
  TypeError.


0.6 (2008-08-12)
----------------

- Added ILogProcessor to allow for registering adapters that process logs when
  accessed through the ILog.logs property.

0.5 (2008-07-10)
----------------

- Removed the global timeline as it is a conflict hotspot.

0.4 (2008-07-08)
----------------

- Fixed display of times in LogEntrySource: Times are now in the timezone
  defined by an adapter from request to ITZInfo (bug #4314).

0.3 (2008-06-05)
----------------

- The terms do not break when a principal is deleted (bug #4146).

0.2 (2008-04-28)
----------------

- Allow logging wich interaction but without principal. Required for logging in
  lovely.remotetask.
- Creating savepoint after creating a log entry, otherwise there are some
  problems with using the logentry in the same transaction.

0.1 (2008-04-21)
----------------

- first release


zeit.push changes
=================

1.28.2 (2019-03-29)
-------------------

- PERF: Don't grok browser packages by default


1.28.1 (2019-02-25)
-------------------

- MAINT: Publish homepage banner with higher priority


1.28.0 (2019-02-12)
-------------------

- ZON-5017: Support transmitting breaking_news flag to facebook


1.27.0 (2019-01-11)
-------------------

- ZON-5075: Add separate fields for print twitter account


1.26.1 (2018-11-30)
-------------------

- FIX: Repair bw/compat for urbanairship


1.26.0 (2018-11-20)
-------------------

- ZON-4957: Separate UA message for authors from the vivi-editable message


1.25.3 (2018-10-02)
-------------------

- FIX: Be defensive about broken banner file


1.25.2 (2018-09-26)
-------------------

- FIX: Stop raising exception, if banner not published


1.25.1 (2018-09-25)
-------------------

- MAINT: Add timeout to influx notifier


1.25.0 (2018-09-21)
-------------------

- ZON-3482: Use xml config instead of article for breaking news banner


1.24.0 (2018-06-08)
-------------------

- ZON-4709: Use author push for new articles as default


1.23.1 (2018-04-19)
-------------------

- ZON-4412: Transmit expiry information to UA, make configurable from template

- ZON-4546: Use textarea for twitter texts (like for facebook) to
  unify their styling


1.23.0 (2018-03-21)
-------------------

- ZON-4494: Add separate tweet text for twitter cross-posting


1.22.1 (2017-11-09)
-------------------

- MAINT: Increase twitter message limit to 280 characters


1.22.0 (2017-10-04)
-------------------

- ZON-3409: Move from remotetask to celery


1.21.3 (2017-09-28)
-------------------

- MAINT: Send UA errors to bugsnag

- MAINT: Send event notification to grafana for urbanairship pushes


1.21.2 (2017-08-14)
-------------------

- FIX: Repair bw-compat for twitter/ressort


1.21.1 (2017-08-08)
-------------------

- ZON-3677: Move `getDefaultTitle` to payload source


1.21.0 (2017-08-07)
-------------------

- ZON-4006: Split off mobile fields into their own form

- ZON-4007: Make UA Payload configurable via Templates

- BUG-674: Don't perform push-target-url replacement twice,
  and don't squash non-www.zeit.de URLs

- BUG-621: Log Twitter and Facebook account name to objectlog

- MAINT: Remove broken/unused ``IPushMessages.date_last_pushed``


1.20.6 (2017-06-27)
-------------------

- FIX: Make ConflictError workaround actually work


1.20.5 (2017-06-27)
-------------------

- Fix merge mistake in 1.20.3


1.20.4 (2017-06-26)
-------------------

- MAINT: Send uniqueId as banner URL, since zeit.web expects that


1.20.3 (2017-06-26)
-------------------

- BUG-201: Make homepage publisher safe from ConflictErrors

- MAINT: Remove obsolete banner control files (wrapper, ios-legacy)


1.20.2 (2017-05-22)
-------------------

- BUG-715: Append tracking query parameters correctly (without superflous `&`)

- ZON-3917: remove bigshare button checkbox


1.20.1 (2017-02-23)
-------------------

- ZON-3727: Fix override text not being used as alert text


1.20.0 (2017-02-23)
-------------------

- ZON-3727: Adjust to new urbanairship payload requirements


1.19.2 (2017-01-31)
-------------------

- Remove more parse.com remnants


1.19.1 (2017-01-31)
-------------------

- Remove parse.com production utility registration


1.19.0 (2017-01-31)
-------------------

- Remove parse.com, they have shut down


1.18.0 (2017-01-16)
-------------------

- MAINT: Make push base URL configurable (for staging)


1.17.5 (2016-11-08)
-------------------

- Remove iOS from Parse notifications.


1.17.4 (2016-10-19)
-------------------

- ZON-3437: Restrict urbanairship iOS to specific segment.


1.17.3 (2016-10-11)
-------------------

- ZON-3411: Remove app version restriction from urbanairship
  (Duplicates are prevented since only new apps have the tag group
  ``subscriptions``)

- MAINT: Log sucessful pushes to taskprocessor log.


1.17.2 (2016-10-05)
-------------------

- ZON-3411: Restrict pushing to parse and urbanairship to
  non-overlapping app versions. Retire feature toggle ``zeit.push.urbanairship``.

- Fix the urbanairship tag+group syntax.


1.17.1 (2016-09-28)
-------------------

- MAINT: Abort push to Urban Airship and display message in Log if no channel
  was given to avoid accidental push to *all* devices.


1.17.0 (2016-09-27)
-------------------

- ZON-3278: Refactor test infrastructure to make mock notifiers reusable.


1.16.0 (2016-09-26)
-------------------

- MAINT: Change audience group for Urban Airship to ``subscriptions`` by making
  it configurable via product config.


1.15.5 (2016-09-26)
-------------------

- Update to `zeit.cms >= 2.90`.


1.15.4 (2016-09-14)
-------------------

- ZON-3318: Add bigshare buttons checkbox to social form.


1.15.3 (2016-09-12)
-------------------

- MAINT: Put pushing to urbanairship behind feature toggle ``zeit.push.urbanairship``


1.15.2 (2016-09-07)
-------------------

- FIX: Repair tracking URLs for mobile push notifications for breaking news.


1.15.1 (2016-08-22)
-------------------

- Adjust payload for push notifications to iOS via Urban Airship. (ZON-3213)

- Improve log messages to include the message. (ZON-3213)


1.15.0 (2016-08-09)
-------------------

- Always disable push services on send to avoid the risk of re-sending a
  notification on publish, since information might not be relevant anymore.

- Add push notifications to mobile using Urban Airship (ZON-3213).


1.14.0 (2016-05-09)
-------------------

- Don't push to old mobile apps: Android<1.4 and iOS<20150914 (ZON-3069).


1.13.1 (2016-04-18)
-------------------

- Don't load Zope/UI specific ZCML in the model ZCML


1.13.0 (2016-04-08)
-------------------

- Add separate facebook fields for campus (ZON-2930).


1.12.0 (2016-01-22)
-------------------

- Remove facebook magazin fields from form, now handled by zeit.magazin.

- Fix facebook magazin field styling for non-articles.


1.11.2 (2016-01-08)
-------------------

- Adjust maximum twitter message length (t.co switched to https, so needs one
  more character)


1.11.1 (2016-01-04)
-------------------

- Fix brown-bag 1.11.0 (missing import).


1.11.0 (2015-12-17)
-------------------

- Store facebook texts per account in ``message_config`` instead of combined in
  ``long_text`` (ZON-2397).

- Make ``IAccountData`` helper available in domain, not just browser.


1.10.0 (2015-10-30)
-------------------

- Add new Payloads for Android 1.4 and iOS 20150914 that rewrite links to
  target Friedbert. (DEV-938)


1.9.2 (2015-06-23)
------------------

- Add web-based UI for generating a Facebook access token (DEV-767).


1.9.1 (2015-04-27)
------------------

- Make ``mobile_text`` required when ``mobile_enabled`` is set (DEV-704).

- Adapt parse.com payload for iOS apps (DEV-698).


1.9.0 (2015-04-23)
------------------

- Remove global ``enabled`` setting, we rely on ``enabled`` setting of
  the individual ``message_config`` entries instead (DEV-704).

- Add optional override field for the parse.com push text, remove feature
  toggle ``zeit.push.wichtige-nachrichten`` (DEV-704).

- Add checkbox for additional Twitter account (DEV-704).


1.8.1 (2015-04-15)
------------------

- Use feature toggle ``zeit.push.wichtige-nachrichten`` just for the one
  checkbox.


1.8.0 (2015-04-15)
------------------

- Increase minimum iOS version for headline API. (DEV-698)

- Display teaser title in `headline` and headline in `alert-title`. (DEV-698)

- Add feature toggle ``zeit.push.social-form`` for social media form fields.


1.7.4 (2015-03-30)
------------------

- Restrict changed payload to current iOS app versions (DEV-698).


1.7.3 (2015-03-30)
------------------

- Switch around parse.com metadata (DEV-698).


1.7.2 (2015-03-26)
------------------

- Add imageUrl and teaserText to parse.com payload (DEV-698).

- Add tracking parameters to parse.com urls (DEV-698).


1.7.1 (2014-11-18)
------------------

- Use title of article as text for push messages send to Parse (VIV-564).


1.7.0 (2014-11-14)
------------------

- Introduce ``IPushURL`` indirection so link objects can change the pushed url
  (VIV-516).

- Fix bug in social media addform so it actually stores push configuration.

- Translate parse.com title (VIV-552).


1.6.0 (2014-10-21)
------------------

- Set ``push_news`` flag on checkin (VIV-526).

- Extract social media form from zc.article, so we can reuse it for different
  content types (VIV-516).

- Only retract banners that match the current article (VIV-532).


1.5.3 (2014-09-30)
------------------

- Fixed brown-bag release.


1.5.2 (2014-09-30)
------------------

- Adjust parse.com-API payloads (VIV-517)


1.5.1 (2014-09-03)
------------------

- Fix our parse.com-API usage for ``channels``.

- Send additional "breaking news" notifications without a channel, for those
  mobile app versions that cannot handle channels (backwards compatibility).


1.5.0 (2014-08-29)
------------------

- Add ``channels`` for parse.com (VIV-466).
  Channels can either be given as a list of channel names, or as a string that
  is looked up from product config (the config setting is a whitespace
  separated list of channel names); if no channels are given or the product
  config setting is empty, the ``channels`` parameter is omitted.


1.4.2 (2014-07-30)
------------------

- Update last_semantic_change of banner files properly (VIV-460).


1.4.1 (2014-07-17)
------------------

- When a banner file is already checked out (by the same or another user),
  overwrite it anyway.

- Make long_text and short_text only writeable while checked out (VIV-451).


1.4.0 (2014-07-10)
------------------

- Send different payloads to android and ios devices on parse.com (VIV-426).

- Add separate banner file for the wrapper apps (WEB-318).

- Don't send a push when no text is configured.

- Log the text in the objectlog.


1.3.1 (2014-06-24)
------------------

- Fix unicode handling for Facebook.


1.3.0 (2014-06-20)
------------------

- Implement posting to Facebook (VIV-371).

- Use separate file /eilmeldung/homepage-banner (VIV-417).

- Add lightbox view to retract published "banner" articles (VIV-418).


1.2.1 (2014-06-04)
------------------

- Re-activate /eilmeldung/eilmeldung parse.com workaround.


1.2.0 (2014-06-03)
------------------

- Restructure public API to make the message text configurable on the content
  object (VIV-391).

- Add a link to the actual article to ``/eilmeldung/eilmeldung`` (VIV-382).

- Implement posting to Twitter (VIV-370).


1.1.0 (2014-05-09)
------------------

- Replace special case that pushes to parse.com when ``/eilmeldung/eilmeldung``
  is published with proper "push to homepage" mechanism. We still update and
  publish ``/eilmeldung/eilmeldung``, but the other push mechanisms are now
  separate. (VIV-372).

- Log push sending to objectlog (VIV-368).

- Fix push for not-yet-pushed eilmeldung (VIV-369)


1.0.0 (2014-04-22)
------------------

- first release.


zeit.retresco changes
=====================

1.32.2 (2019-03-29)
-------------------

- PERF: Don't grok browser packages by default


1.32.1 (2018-12-14)
-------------------

- FIX: Add posibility to get unpublished data to get body from tms


1.32.0 (2018-09-17)
-------------------

- ZON-4820: Add `ISkipEnrich` marker interface that skips automatic enrich on checkin

- ZON-4893: Index during publish for all content types,
  index after retract too.

- TMS-214: Remove `payload.teaser.title` from authors again to clean up the ES mapping


1.31.2 (2018-09-10)
-------------------

- MAINT: Change redirect syntax to zeit.web instead of nginx


1.31.1 (2018-08-16)
-------------------

- TMS-214: Revive `payload.teaser.title` to fix author auto-complete.


1.31.0 (2018-08-01)
-------------------

- ZON-4806: Add `date_range` query helper

- BUG-974: Index visible_entry_count for gallery objects

- FIX: Use ITMSRepresentation for keyword preview api


1.30.2 (2018-07-27)
-------------------

- PERF: Don't use IAbsoluteURL so as not to resolve any __parent__ DAV objects


1.30.1 (2018-07-27)
-------------------

- MAINT: Use requests-based ES connection instead of urllib3


1.30.0 (2018-07-27)
-------------------

- MAINT: Make elasticsearch connection class configurable via product config


1.29.1 (2018-07-26)
-------------------

- FIX: Change retresco mock to fix tests


1.29.0 (2018-07-26)
-------------------

- ZON-4742: Add topiclinks to retresco tagger implementation

- ZON-4788: Prefer payload body to payload teaser regarding zeit.find


1.28.0 (2018-07-18)
-------------------

- ZON-4788: Index SEO robots properties and push config explicitly

- ZON-4788: Add payload teaser fields for all content types

- ZON-4788: Index advertisement objects


1.27.0 (2018-06-26)
-------------------

- TMS-237: Index text and rawxml objects

- TMS-214: Remove unused vivi-only access counter data


1.26.0 (2018-06-25)
-------------------

- ZON-4571: Add get_article_keywords for preview retresco API


1.25.0 (2018-06-20)
-------------------

- TMS-235: Instantiate a pseudo Link object for blogpost entries


1.24.2 (2018-06-08)
-------------------

- TMS-213: Skip zeit.newsimport images


1.24.1 (2018-06-08)
-------------------

- TMS-213: Don't index images inside of image groups


1.24.0 (2018-06-06)
-------------------

- TMS-213: Index images and imagegroups, infoboxes and portraitboxes


1.23.3 (2018-06-04)
-------------------

- FIX: Make optional `sort_order` actually work (1.22.1)


1.23.2 (2018-05-30)
-------------------

- BUG-930: Fix bug, cutting off too many characters from keyword links


1.23.1 (2018-05-30)
-------------------

- TMS-227: Update to changed `channels` serialization (zeit.cms-3.12)


1.23.0 (2018-05-29)
-------------------

- TMS-224: Override image building for TMS authors

- TMS-227: Extract ``davproperty_to_es`` helper function


1.22.1 (2018-05-17)
-------------------

- MAINT: Make `sort_order` optional in elasticsearch.search()


1.22.0 (2018-05-17)
-------------------

- MAINT: Send user-agent on elasticsearch requests


1.21.6 (2018-05-16)
-------------------

- FIX: Move volume `covers` into payload where it belongs


1.21.5 (2018-05-14)
-------------------

- FIX: Make DAVPropertyConverter work with ITMSContent/DAVPropertiesAdapter


1.21.4 (2018-05-09)
-------------------

- TMS-200/BUG-911: Enrich during publish as well, so the body goes to TMS
  before publish (as the celery jobs may run later, see 1.20.5)

- MAINT: Allow explicit source field selection while maintaining compat with
  `include_payload` search flag.


1.21.3 (2018-04-27)
-------------------

- MAINT: Route TMS re-enrich jobs into their own queue


1.21.2 (2018-04-26)
-------------------

- FIX elasticsearch dependency to 2.x (which is what TMS uses)


1.21.1 (2018-04-19)
-------------------

- OPS-874: Do not traverse folders that are marked accordingly


1.21.0 (2018-04-17)
-------------------

- ZON-4532: Remove feature toggle `zeit.retresco.tms`, it's in production now.
  Also remove transitional/bw-compat code regarding zeit.intrafind.


1.20.6 (2018-04-09)
-------------------

- ZON-4561: Update keywords in re-enrich hook


1.20.5 (2018-03-20)
-------------------

- TMS-200: Index TMS synchronously during publishing; otherwise the
  publisher marking an object as published can happen before the TMS job ran


1.20.4 (2018-03-19)
-------------------

- PERF: Skip TMS request when content has no uuid


1.20.3 (2018-03-16)
-------------------

- TMS-189: Set principal for (anonymously available) re-enrich webhook


1.20.2 (2018-03-16)
-------------------

- TMS-200: Index TMS during publishing too, so it immediately receives
  the "published" timestamp information for newly published objects


1.20.1 (2018-03-13)
-------------------

- Also show keywords that are already intext-linked below article


1.20.0 (2018-03-13)
-------------------

- MAINT: Unify IConnection interface: get_article_keywords and _body
  now take ICMSContent like all the other methods, and resolve to uuid themselves

- PERF: Extract API call to `in-text-linked-documents` so zeit.web can cache it


1.19.0 (2018-03-13)
-------------------

- TMS-186: Declare ``zeit.retresco.UseTMS`` permission.


1.18.2 (2018-03-09)
-------------------

- FIX: Actually make re-enrich hook use async jobs (see 1.10.5)


1.18.1 (2018-02-28)
-------------------

- FIX: Adjust `get_article_keywords` to the changed payload structure


1.18.0 (2018-02-27)
-------------------

- TMS-162: Collect all DAV properties as payload, implement a CMS
  content base class that retrieves data from there instead of DAV


1.17.1 (2018-02-26)
-------------------

- TMS-170: Fix pre-launch production should already index to TMS


1.17.0 (2018-02-19)
-------------------

- TMS-156: Update keywords on checkin automatically if no keywords exist yet


1.16.3 (2018-02-15)
-------------------

- FIX: Don't break on rows=0 in get_topicpage_documents, which can
  happen with curated areas


1.16.2 (2018-02-15)
-------------------

- TMS-168: Fix bug that caused intrafinned pinned tags to be lost
  during TMS indexing


1.16.1 (2018-02-12)
-------------------

- MAINT: Skip obsolete `quiz` content in bulk indexing


1.16.0 (2018-01-29)
-------------------

- TMS-38: Add `filter` parameter to `get_topicpage_documents`


1.15.11 (2018-01-25)
--------------------

- TMS-136: Retry on ICMSContent resolution errors


1.15.10 (2018-01-24)
--------------------

- FIX: Handle missing DAV property without breaking


1.15.9 (2018-01-23)
-------------------

- Fix merge mistake


1.15.8 (2018-01-23)
-------------------

- TMS-149: Retry indexing on technical errors


1.15.7 (2018-01-22)
-------------------

- More typos


1.15.6 (2018-01-22)
-------------------

- Fix typo


1.15.5 (2018-01-22)
-------------------

- TMS-136: Create separate job for each entry instead of processing
  the contents of one folder at once


1.15.4 (2018-01-16)
-------------------

- TMS-136: Fix recursive descent through folders


1.15.3 (2018-01-16)
-------------------

- TMS-136: Don't stop parallel indexing on individual content errors


1.15.2 (2018-01-12)
-------------------

- TMS-145: Index ``section`` with hierachy (ressort and subressort)


1.15.1 (2018-01-11)
-------------------

- TMS-136: While ``index_on_checkin`` toggle is enabled, store the
  analyzed TMS keywords in vivi on checkin (like we would do in bulk indexing)


1.15.0 (2018-01-10)
-------------------

- TMS-136: Add feature toggle ``zeit.retresco.index_on_checkin`` so we
  can selectively start to index on checkin while still using intrafind


1.14.0 (2018-01-05)
-------------------

- TMS-133: Store TMS keywords in a different DAV property than Intrafind,
  so we can reindex while still using Intrafind.

- TMS-7: Log task duration, since celery only logs total wait time


1.13.3 (2017-10-27)
-------------------

- FIX: Really generate topicpage redirects


1.13.2 (2017-10-19)
-------------------

- MAINT: Add missing import


1.13.1 (2017-10-17)
-------------------

- BUG-796: Work around celery vs. DAV-cache race condition


1.13.0 (2017-10-04)
-------------------

- ZON-3409: Move from remotetask to celery


1.12.0 (2017-08-07)
-------------------

- ZON-4095: Generate nginx config file from TMS for topic page redirects

- ZON-3677: Remove `ICommonMetadata.push_news`, it's not used anymore


1.11.2 (2017-07-25)
-------------------

- MAINT: Optionally change content keywords on bulk index


1.11.1 (2017-07-25)
-------------------

- Use dlps as TMS date

- MAINT: Don't change content keywords on checkin

- MAINT: Preserve enriched body during no-enrich bulk reindex


1.11.0 (2017-07-19)
-------------------

- ZON-3994: Retrieve article keywords from TMS, putting pinned ones first

- MAINT: Use just path for TMS teaser images, TMS offers configurable
  prefix and suffix now


1.10.5 (2017-07-12)
-------------------

- PERF: Don't resolve anything in re-enrich hook,
  just create async jobs, so we can handle large content amounts


1.10.4 (2017-07-07)
-------------------

- MAINT: Add link to TMS to keyword widget


1.10.3 (2017-06-09)
-------------------

- FIX: Make DAV property access work in parallel indexing

- MAINT: Use variant URL for TMS teaser images


1.10.2 (2017-05-24)
-------------------

- ZON-3925: Remove metadata from topic page list which TMS now does
  not return anymore, but we didn't use anyway


1.10.1 (2017-05-10)
-------------------

- MAINT: Don't try to TMS-publish content that's missing required fields


1.10.0 (2017-05-10)
-------------------

- ZON-3896: Retrieve more metadata for topic page list

- Log complete TMS request on debug level


1.9.0 (2017-05-08)
------------------

- ZON-3173: Add endpoint for TMS reindexing


1.8.1 (2017-02-23)
------------------

- PERF: Don't update TMS during publishing.


1.8.0 (2016-12-05)
------------------

- ZON-3118: Add method to retrieve enriched article body with intext links.

- Patch requests library to rigorously enforce response timeouts.


1.7.4 (2016-11-04)
------------------

- Add option to load uniqueIds from file.


1.7.3 (2016-10-19)
------------------

- Optionally update content keywords from TMS result on bulk index,
  keeping intrafined pinned keywords.


1.7.2 (2016-10-06)
------------------

- Transmit existing intrafind keywords to TMS for indexing by mapping their
  entity_types properly.


1.7.1 (2016-09-30)
------------------

- Convert keywords to Tag objects for TMS and ES results.

- Implement an option to publish after index.


1.7.0 (2016-09-28)
------------------

- ZON-3362: Index properties of ``IVolume`` objects.

- Recognize ``--enrich`` CLI argument in the non-parallel case.

- Update to changed enrich TMS-API.


1.6.0 (2016-09-26)
------------------

- ZON-3364: Implement ``IWhitelist.locations()`` via TMS-API.

- ZON-3163: Implement the ``IElasticsearch`` utility.


1.5.0 (2016-09-16)
------------------

- ZON-3199: Add specific ``Whitelist`` and ``Tag`` to allow type-ahead with
  Retresco.

- ZON-3236: Implement ``ITopicpages`` via the TMS-API.


1.4.1 (2016-09-13)
------------------

- Update to changed enrich/index TMS-API.

- Revert: Index `startdate` year 9999 for unpublished content
  Retresco now offers an explicit API for publish, which we'll trigger
  from the publisher.

- Rename ``acquisition`` to ``access``.


1.4.0 (2016-09-07)
------------------

- Place ZCML under feature toggle `zeit.retresco.tms`.

- Enrich content on checkin.

- Index `startdate` year 9999 for unpublished content.


1.3.2 (2016-08-22)
------------------

- ZON-3241: Also index `acquisition`.


1.3.1 (2016-08-16)
------------------

- Change result key for TMS topic page content type to `doc_type`,
  since `type` is already used for CP/Gallery type


1.3.0 (2016-08-10)
------------------

- ZON-3120: Implement method to retrieve content that belongs to a TMS topic page


1.2.3 (2016-07-08)
------------------

- ZON-3188: Preemptively skip images when indexing


1.2.2 (2016-07-07)
------------------

- ZON-3153: Ignore content that's missing in TMS when deleting

- ZON-3188: Fix recursion bug in parallel index script


1.2.1 (2016-07-06)
------------------

- ZON-3153: Handle print published properly; synthesize teaser from title;
  index some more fields.


1.2.0 (2016-07-04)
------------------

- ZON-3188: First stab at parallel reindexing using Celery

- ZON-3153: Add xmlrpc method for indexing content in TMS (for invalidator)

- ZON-3153: Index content in Retresco TMS on create, checkin, delete, publish


1.1.0 (2016-06-27)
------------------

- ZON-3117: Retrieve list of topicpages, store as rawxml content


1.0.0 (2016-06-08)
------------------

- Initial release.


zeit.securitypolicy changes
===========================


2.2.10 (2018-10-17)
-------------------

- ZON-2694: Grant retractlog permission to seo


2.2.9 (2018-10-04)
------------------

- ZON-3312: Remove obsolete calendar


2.2.8 (2018-09-04)
------------------

- ZON-4854: Grant zeit.cms.admin.View to CvD


2.2.7 (2018-05-07)
------------------

- ZON-4455: Grant zeit.vgwort.RetryReport to Producer


2.2.6 (2018-05-03)
------------------

- MAINT: Grant ViewProperties to Producer


2.2.5 (2018-03-13)
------------------

- TMS-186: Grant UseTMS to Producer and SEO


2.2.4 (2018-03-01)
------------------

- MAINT: Grant ViewInTMS to Producer and SEO


2.2.3 (2018-02-12)
------------------

- MAINT: Remove obsolete zeit.content.quiz


2.2.2 (2018-01-09)
------------------

- MAINT: Remove zeit.imp, we've been on zeit.content.image.variants
  for quite some time now


2.2.1 (2017-07-07)
------------------

- ZON-4062: Set up Brightcove notification webhook


2.2.0 (2016-04-18)
------------------

- Don't load Zope/UI specific ZCML in the model ZCML


2.1.12 (2015-10-29)
-------------------

- Add permissions to date back semantic date to role Producer (DEV-951).


2.1.11 (2015-06-25)
-------------------

- Remove permission ``zeit.content.cp.View/EditAutomatic`` (DEV-832).


2.1.10 (2015-06-09)
-------------------

- Grant ``zeit.Producer`` permissions to edit Article-Flow (DEV-759).


2.1.9 (2015-04-28)
------------------

- Grant ``zeit.Producer`` permissions to create an move zeit.content.cp.IArea.
  (DEV-746)


2.1.8 (2015-01-29)
------------------

- Grant ``zeit.Producer`` Auto-CP permissions.


2.1.7 (2014-11-14)
------------------

- Grant ``zeit.content.cp.ViewAutomatic`` to ``zeit.Betatester`` (VIV-525).


2.1.6 (2014-10-07)
------------------

- Introduce role ``zeit.Betatester`` (VIV-525).


2.1.5 (2014-09-18)
------------------

- Allow only roles zeit.Producer and zeit.CvD to delete and retract centerpages
  (VIV-496).


2.1.4 (2014-07-17)
------------------

- Update to use zeit.seo.browser subpackage.


2.1.3 (2014-06-05)
------------------

- Use plone.testing-based layers.


2.1.2 (2014-03-10)
------------------

- zeit.content.image, zeit.content.link, and zeit.content.text have their own
  eggs now.


2.1.1 (2014-01-07)
------------------

- Update test setup to changes in zeit.content.article (VIV-249).


2.1.0 (2013-08-14)
------------------

- Update to Python-2.7 and ZTK-1.1.5 (#11005).


2.0.1 (2013-07-08)
------------------

- Fix tests to deal with required keywords (#12478).


2.0 (2013-04-23)
----------------

- Removed test for article asset view as it does not exist any more (#10428)

- Added test for article ``@@edit.html`` in repository which is accessible and
  renders the read-only view.


0.7.2 (unreleased)
------------------

- Updated test mechanics after refactoring zeit.cms.testing. (#10456)


0.7.1 (2010-08-09)
------------------

- Fix tests after product config changes in zeit.cms (#7549)


0.7.0 (2010-04-09)
------------------

- Using versions from the ZTK.

- Syndication-Manager (``@@syndication_manager``) ist nicht mehr verfügbar
  (#6878).

- Editors may edit Brightcove Videos/Playlists.

0.6.0 (2009-10-19)
------------------

- Nur Producer sehen Navigationsbaum in der Seitenspalte (#6353).


0.5.1 (2009-08-18)
------------------

- Tests repariert, nach dem sich der Name des Folder-Add-Views geändert hat.

0.5 (2009-05-17)
----------------

- Nur noch Producer dürfen Ordner umbenennen (#5319).

- Anpassungen für zeit.cms 1.20

- Alle ``test.py`` nach ``tests.py`` umbenannt.

- Keine eigene Translationdomain mehr, Übersetzungen via zeit.locales.


0.4 (2009-03-23)
----------------

- Auf zeit.cms 1.16.1 angepasst.

0.3 (2009-01-22)
----------------

- Grafiktool (zeit.imp) integriert.

0.2 (2008-11-24)
----------------

- Redakteure dürfen wieder Dinge im Repository ändern.

0.1 (2008-11-21)
----------------

- Extra Rolle für CvDs (kann Sperren stehlen).
- Extra Rolle für SEO (damit wird normalen Redakteuren das SEO-Tab nicht mehr
  angezeigt).


zeit.seo changes
================

1.8.0 (2016-12-05)
------------------

- Add checkbox for disabling tms intext link feature (ZON-3118).


1.7.0 (2016-02-25)
------------------

- Add DAV property ``keyword_entity_type`` (ZON-2779).


1.6.0 (2014-07-17)
------------------

- Add character counter to form fields.

- Move browser code to subpackage.


1.5.0 (2014-05-09)
------------------

- Add checkbox ``hide_timestamp`` (VIV-374).


1.4.2 (2010-08-09)
------------------

- Fix tests after product config changes in zeit.cms (#7549).


1.4.1 (2010-05-17)
------------------

- Using versions from the ZTK.


1.4.0 (2010-03-10)
------------------

- Felder »lexicalResourceQuery« und »linke Spalte« entfernt (#6878).


1.3.0 (2009-12-18)
------------------

- Neues Feld 'robots' (#5726).

1.2.7 (2009-05-15)
------------------

- Alle ``test.py`` nach ``tests.py`` umbenannt.

- Keine eigene Translationdomain mehr, Übersetzungen via zeit.locales.

1.2.6 (2008-11-20)
------------------

- Separate Permissions für das Ansehen/Bearbeiten von SEO-Daten. Das ermöglicht
  das Ausblenden des Tabs für die meisten Benutzer.

1.2.5 (2008-10-29)
------------------

- Neue Felder: »Lexical resource query« und »Left column«
- Erstes Release nach der Trennung von zeit.cms


zeit.sourcepoint changes
========================

1.0.0 (2019-01-24)
------------------

- Initial release.


zeit.vgwort changes
===================

2.4.1 (2019-03-29)
------------------

- PERF: Don't grok browser packages by default


2.4.0 (2018-05-07)
------------------

- ZON-4455: Add "report again" button


2.3.4 (2018-05-04)
------------------

- ZON-4455: Add projected report date to status tab


2.3.3 (2018-05-03)
------------------

- ZON-4455: Translate vivi-generated report error messages


2.3.2 (2018-05-03)
------------------

- ZON-4455: Add tab to inspect vgwort status


2.3.1 (2018-04-26)
------------------

- ZON-4455: Work around strange 401 errors


2.3.0 (2018-04-24)
------------------

- ZON-4455: Ignore errors during report and continue, instead of crashing

- ZON-4455: Don't try to report during API maintenance windows


2.2.8 (2017-10-06)
------------------

- ZON-3409: Move from remotetask to celery


2.2.7 (2016-09-26)
------------------

- Update to `zeit.cms >= 2.90`.


2.2.6 (2016-04-18)
------------------

- Don't load Zope/UI specific ZCML in the model ZCML


2.2.5 (2015-06-30)
------------------

- Make taskprocessor queue name for async functions configurable (DEV-816).


2.2.4 (2015-06-24)
------------------

- Make claiming tokens thread-safe (xmlrpclib.ServerProxy isn't, so don't
  instantiate it globally).


2.2.3 (2014-06-05)
------------------

- Use gocept.httpserverlayer.custom to avoid port collisions in tests.


2.2.2 (2014-03-10)
------------------

- Use py.test runner.


2.2.1 (2014-01-20)
------------------

- ICommonMetadata now uses author reference objects (VIV-273).


2.2.0 (2013-09-27)
------------------

- Lock vgwort report run to prevent parallel execution (VIV-1270)


2.1.1 (2013-09-24)
------------------

- Remove unittest2, we have 2.7 now


2.1.0 (2013-08-13)
------------------

- The report script reports synchronously now (#12640)

- Make error reporting more stable agains unicode errors (#12640)

- Strip short text for vgwort to 100 chars, as this is vgwort's limit (#12640)

- Invalid author references are ignored (and logged) #12640

- When a non common metadata objects should be reported to vgwort, this error
  is being marked in the `reported_error` property now, instead of trying to
  report again and again (#12640)

- Remote (VGWort) validation errors are now being reported to the
  `reported_error` property (#12640)


2.0 (2013-04-24)
----------------

- Copatibility with zeit.cms 2.0


0.4.4 (2012-03-06)
------------------

- Objects can be copied from clipboards again. (#9960)

- No longer log spurious errors when trying to fix up certain SOAP responses.
  (#10094)


0.4.3 (2011-11-14)
------------------

- Allow the token service to initialize even without product config. This is
  necessary for i18nextract to work correctly.


0.4.2 (2011-11-13)
------------------

- Remove VGWort properties after an object has been copied (#9451)


0.4.1 (2011-08-16)
------------------

- Store claimable tokens as str instead of some strange SOAP data type.


0.4.0 (2011-08-16)
------------------

- Report the freetext authors if no structured authors are available. VGWort
  will do some matching then.

- Report authors without vgwort id

- Added /komplettansicht to report url

- Removed the mostly useles CSV export. We need to find useful ways for
  reporting.

- Make claiming a token transaction-independent (#9430).


0.3.1 (2011-06-22)
------------------

- Fix reportable query so the query server actually returns results.


0.3.0 (2011-06-20)
------------------

- Consume less memory during the actual report to VGWort.
- Report all (otherwise applicable) documents, not only currently published
  ones (#9092).
- Transmit the "product" as an additional author (#9033).


0.2.0 (2010-07-07)
------------------

- Cronjob to automatically order new tokens (#7326).
- Cronjob to automatically report documents (#7216).
- UI to view reporting results (#7546)


0.1.0 (2010-05-17)
------------------

* first release


zeit.wysiwyg changes
====================

3.0.1 (2018-01-09)
------------------

- TMS-134: Be diligent about not creating duplicate slashes


3.0.0 (2017-10-04)
------------------

- Remove ``update_metadata_on_checkin()`` adapter as it is not supported by
  celery and not needed outside XSLT. (ZON-3724)


2.0.7 (2016-09-26)
------------------

- Update to `zeit.cms >= 2.90`.


2.0.6 (2016-07-26)
------------------

- Extend product config to fix source configuration for testing. (ZON-3171)


2.0.5 (2015-08-24)
------------------

- Remove obsolete image layout `infobox`.


2.0.4 (2015-05-04)
------------------

- Replace MochiKit $$ with jQuery, which is *much* faster in Firefox.


2.0.3 (2014-03-10)
------------------

- zeit.content.image has its own egg now.


2.0.2 (2014-02-10)
------------------

- Use Fanstatic instead of zc.resourcelibrary (VIV-296).


2.0.1 (2013-10-02)
------------------

- Update to lxml-3.x (#11611).


2.0 (2013-04-23)
----------------

- Use the new `@@raw` to display images (#12102)

- Fix call to ObjectReferenceWidget (#12102)

- Remove obsolete "relateds" feature (#12077).


1.42.1 (unreleased)
-------------------

- Remove obsolete "relateds" feature (#12077).


1.42.0 (2013-02-20)
-------------------

- Add timeline module (#12022).


1.41.1 (2012-12-17)
-------------------

- Fix bug in video conversion step: empty format could not be converted from
  HTML to XML (seen in #11695).


1.41.0 (2012-03-06)
-------------------

- Use separate ordering values instead of a single weight for conversion steps
  from XML to HTML and vice versa; protect raw HTML content from any
  conversions. (#10251)


1.40.3 (2011-12-08)
-------------------

- Fix handling of comments and empty video ids (#10038).


1.40.2 (2011-12-01)
-------------------

- Fix extracting image tags from paragraphs (#10027, #10033).


1.40.1 (2011-11-24)
-------------------

- Fix name of source with videos and playlists.


1.40.0 (2011-11-13)
-------------------

- Fixed bug: Empty citations caused xsi:nil when converted to HTML and an error when
  converted back to XML.

- ``<image>`` tages are not longer inside of a ``<p>``. That is there is no way
  to create those images with the WYSIWYG editor and any such image encountered
  is automatically migrated (#8158)

- Put out related list as ``<relateds/>`` as it was supposed to be (#8066).

- Drop backward compatibility for <video> tags with videoId and player
  attributes. Only href and href2 are supported now.

- Empty elements (like <gallery/>) are converted in a useful way now.


1.39.1 (2010-08-09)
-------------------

- Removed pointles selenium test (#7549).


1.39.0 (2010-06-09)
-------------------

- Add video-uniqueId to XML (#7381).


1.38.1 (2010-06-03)
-------------------

- A Video might have expires==None


1.38.0 (2010-06-02)
-------------------

- Removed support for ``article_extra`` (#5935).
- Take expires from video object if user entered no value (#7028).


1.37.1 (2010-04-14)
-------------------

- Anlegen von Playlisten funktioniert wieder (#7077).


1.37.0 (2010-04-12)
-------------------

- Using versions from the ZTK.

- Using object browser to select videos (#6912).


1.36.0 (2010-03-10)
-------------------

- Tabelle und Anker entfernt (#6878).


1.35.0 (2009-12-18)
-------------------

- Wenn Bilder referenziert werden, wird der Artikel aktualisiert, wenn die
  Bilder sich ändern (#6254).
- Unbekannte Tags werden nicht ins HTML übertragen (#6678).


1.34.0 (2009-11-25)
-------------------

- Fehlerhaftes Markup im Raw-Block wird repariert (#6430).


1.33.0 (2009-11-02)
-------------------

- Es gibt jetzt einen einfachen Weg das Artikel-Bild aus der einem Artikel
  zugewiesenen Bildergruppe einzubinden (#6108).


1.32.2 (2009-10-06)
-------------------

- DeprecationWarning (ISite) entfernt.

- Kleine Rechtschreibkorrekturen.


1.32.1 (2009-09-06)
-------------------

- Tests angepasst für Änderungen am Kern.


1.32 (2009-09-03)
-----------------

- Player (vid/pls) bei Video (#6151)

- Layout-Eigenschaft »Hochkant« für Bilder (#6172).

1.31.2 (2009-08-29)
-------------------

- URL zum FCKEditor repariert.


1.31.1 (2009-08-29)
-------------------

- Brown bag release.


1.31 (2009-08-21)
-----------------

- Zitate haben (je) ein Feld URL bekommen (#6043).


1.30 (2009-08-19)
-----------------

- FCKEditor wird via JavaScript instanziert, nicht mehr manuell mittels iframe
  (damit er für #5902 auch in einer Lightbox benutzbar wird).

1.29.1 (2009-08-18)
-------------------

- Tests repariert.

1.29 (2009-08-14)
-----------------

- Fehler im Video-Element behoben (#5983, #5984).

1.28 (2009-08-11)
-----------------

- Bild: Layoutauswahl klein, groß, Infobox (#5864)

- Audio: keine Layoutauswahl mehr (#5864)

- Mailform entfernt (#5864)

- neues Element: Related Liste (#5864)

- Diverste Styling und Wording-Fixes (#5864)


1.27 (2009-07-28)
-----------------

- Anlegen von Audio repariert (#5788).

- Nach Inline-Elementen wird jetzt immer ein leerer Absatz erzeugt damit der
  Cursor dort positioniert werden kann.

- Inline-Element werden jetzt immer an der Cursor-Position eingefügt. Dabei
  wird ein vorhandener Absatz ggf. aufgetrennt (#5572).

- Styling und kleinere andere Korrekturen.

1.26.1 (2009-07-20)
-------------------

- Der Konverter stirbt nicht mehr, wenn keine Konvertierungsschritte vorhanden
  sind.

1.26 (2009-06-25)
-----------------

- Referenzen auf Objekte werden jetzt mit der http://xml.zeit.de URL angezeigt.

- Invalidae Referenzen werden einfach gespeichert, statt einen Systemfehler zu
  erzeugen.


1.25 (2009-06-24)
-----------------

- Image-Konvertierung robuster, wenn keine URL im Tag enthalten ist.


1.24.1 (2009-06-18)
-------------------

- Repackaged (setupools/svn 1.6 problem).

1.24 (2009-06-18)
-----------------

- <table> wird gesäubert und nach XML konvertiert.
- Neue Inline-Elemente: Infobox, Portraitbox, Bildergallerie, Zitat
- Video-Element kann ein oder zwei Videos beinhalten.

1.23.1 (2009-06-08)
-------------------

- Sehr kleine Texte wurden nicht korrekt nach HTML konvertiert.

1.23 (2009-06-05)
-----------------

- Intern grundlegend umstrukturiert: Die Konvertierungsphasen sind jetzt
  einzelne Adapter.

1.22 (2009-05-28)
-----------------

- Aus zeit.cms extrahiert.
