vivi.core changes
=================

.. towncrier release notes start

7.148.0 (2025-07-30)
--------------------

- WCM-983: Publish premium audio objects with collective publication


MAINT:
- Be dilligent about closing filehandles in connector setitem


7.147.0 (2025-07-29)
--------------------

FIX:
- ingredients collect should work with empty recipes without ingredients


7.146.0 (2025-07-29)
--------------------

- WCM-987: add new module podcastheader


MAINT:
- Be dilligent about closing filehandles in connector setitem

- Remove obsolete cardstack and xml modules


7.145.0 (2025-07-28)
--------------------

- ES-275: Add release_frequency & contact_email attributes to Podcast


7.144.0 (2025-07-28)
--------------------

- WCM-982: Integrate KPI import cronjobs with connector cache


7.143.0 (2025-07-23)
--------------------

- WCM-1005: More article+cp module icons


7.142.0 (2025-07-23)
--------------------

- WCM-1005: Update article+cp module icons


7.141.0 (2025-07-23)
--------------------

- WCM-999: premium audio does not change article header automatically


7.140.0 (2025-07-21)
--------------------

FIX:
- Prevent DetachedInstanceError when querying reportable vgwort articles


7.139.0 (2025-07-21)
--------------------

- ENG-232: fix faulty parameter name in publisher"


7.138.0 (2025-07-21)
--------------------

- ENG-232: send followings to publisher


FIX:
- WCM-954: Parent_path no longer provides trailing slash by default


7.137.0 (2025-07-18)
--------------------

- WCM-1003: Remove DAV-ism "folders have trailing slash" from mock connector


MAINT:
- MAINT: Remove unused encoded/video attribute from Series


7.136.0 (2025-07-17)
--------------------

- WCM-982: Implement cronjob to import KPI data from BigQuery


7.135.0 (2025-07-16)
--------------------

- WCM-989: Order "context views" tabs explicitly


7.134.0 (2025-07-16)
--------------------

- WCM-954: Preserve content objectlog during copy and move


7.133.0 (2025-07-15)
--------------------

FIX:
- FIX: Correctly set copyright in imageupload

- FIX: Accept images with missing creator or copyright notice in @@edit-images


7.132.0 (2025-07-09)
--------------------

- - WCM-938: Polish image edit form (Add cancel button, don't fail if files are not renamed, support more metadata formats, remove whitespace around copyright slash)

- WCM-933: Apply thumbnail size after focuspoint has been calculated, not before

- WCM-973: Use title from metadata for filename in @@edit-images if not uploading from an article etc.


7.132.0 (2025-07-09)
--------------------

- failed release


7.130.0 (2025-07-04)
--------------------

- WCM-936: Implement batch image upload


FIX:
- Try to avoid negative focus point coordinates


7.129.0 (2025-07-02)
--------------------

MAINT:
- Update dependencies


7.128.0 (2025-07-02)
--------------------

MAINT:
- Do not send retract request if text to speech player is deactivated


7.127.0 (2025-07-01)
--------------------

- WCM-959: Do not add categories during checkout which depend on the recipe module and might have changed during edit

- WCM-950: get podcast image cover directly from podcast object same way as audio object


7.126.0 (2025-06-27)
--------------------

- WCM-911: ZEIT ONLINE -> DIE ZEIT


7.125.0 (2025-06-26)
--------------------

- WCM-960: Ignore elasticsearch server verification, we only talk to known servers


7.124.0 (2025-06-26)
--------------------

- WCM-960: Update to current elasticsearch API


7.123.0 (2025-06-26)
--------------------

- WCM-933: Calculate variant preview images in editor directly from the source image without an intermediary thumbnail

- WCM-940: Add explicit input field for MDB ID


7.122.0 (2025-06-24)
--------------------

MAINT:
- Show embed preview thumbnail immediately during editing


7.121.0 (2025-06-24)
--------------------

- WCM-953: Add system user for bulk operations


7.120.0 (2025-06-20)
--------------------

MAINT:
- Add preview thumbnail to datawrapper easy embed module


7.119.0 (2025-06-20)
--------------------

- ES-196: Support differrent product title for vivi and zeit.web


MAINT:
- Remove obsolete content template implementation


7.118.0 (2025-06-18)
--------------------

MAINT:
- Dependency protobuf security fix


7.117.0 (2025-06-18)
--------------------

- WCM-862: Store empty properties as null instead of empty list


7.116.0 (2025-06-18)
--------------------

- WCM-862: Remove recipe toggles that are active in production

- WCM-870: Extract recipe fields to IRecipeArticle adapter


7.115.0 (2025-06-17)
--------------------

- WCM-901: keep XMP metadata of image when resizing it


7.114.0 (2025-06-17)
--------------------

- WCM-874: Support "enable crawler" workflow also for unpublished content

- WCM-928: only add automated categories within the first checkin


7.113.0 (2025-06-16)
--------------------

- WCM-841: Extract ingredients in used from content-storage instead of elasticsearch


7.112.0 (2025-06-16)
--------------------

- WCM-901: keep image exif metadata when resizing it


7.111.0 (2025-06-10)
--------------------

- WCM-875: Mark recipe module title as required


7.110.0 (2025-06-10)
--------------------

- ES-145: Ignore product IDs during publish, based on setting


7.109.0 (2025-06-06)
--------------------

- Download kilkaya teaser splittests config


7.108.0 (2025-06-06)
--------------------

- WCM-874: Skip some fields when copying metadata to link object

- WCM-888: Add metric to count unreported but reportable vgwort content

- WCM-889: Store recipe metadata as IDs instead of titles


7.107.0 (2025-06-05)
--------------------

- WCM-874: Move button next to the checkbox

- WCM-875: Add article title to recipe_titles for searching

- WCM-907: Initialize vgwort status fields to None


MAINT:
- Remove long-obsolete content template functionality


7.106.0 (2025-06-03)
--------------------

- WCM-874: Implement "enable crawler" button on SEO tab

- WCM-888: commit transaction for vgwort report


7.105.0 (2025-05-28)
--------------------

- WCM-598: Implement various search functions for categories and ingredients


7.104.0 (2025-05-27)
--------------------

- WCM-840: Save special categories in recipe_categories

- WCM-856: add category based on recipe ingredient diet


7.103.0 (2025-05-22)
--------------------

FIX:
- Update vgwort report query - errors should be null not empty string


7.102.0 (2025-05-20)
--------------------

MAINT:
- Update python package tornado to fix vulnerability with priority high


7.101.0 (2025-05-20)
--------------------

MAINT:
- Staging sync


7.100.0 (2025-05-20)
--------------------

- WCM-838: Implement recipe ingredients column

- WCM-389: Implement recipe title column


7.99.0 (2025-05-19)
-------------------

- WCM-406: Add --force-conditions flag to publish-content script to override can_publish

- WCM-867: publisher ignores completely set by config instead of hardcoded conditions


7.98.0 (2025-05-15)
-------------------

- OPS-2829: Apply ssl monkeypatch for celery commands that do not load ZCML (metrics, flower)


7.97.0 (2025-05-08)
-------------------

FIX:
- Call the ingredients source with factory


7.96.0 (2025-05-08)
-------------------

FIX:
- Use proper widget for cms autocomplete


7.95.0 (2025-05-08)
-------------------

FIX:
- reactivate agencies autocomplete


MAINT:
- Add --include-user argument for export-import-workingcopy


7.94.0 (2025-05-07)
-------------------

- WCM-837: Store recipe categories in property (and db column) instead of XML body

- WCM-838: add column for recipe ingredients

- WCM-839: add column for recipe titles

- WCM-853: Remove `videotagesschau` article module


7.93.0 (2025-05-05)
-------------------

- WCM-832: move campus study course into content modules


7.92.0 (2025-04-29)
-------------------

- WCM-832: removal of zeit.campus package


7.91.0 (2025-04-28)
-------------------

- OPS-2829: Fix ssl monkeypatch mechanics


7.90.0 (2025-04-28)
-------------------

- OPS-2829: Work around changed python 3.13 ssl verify defaults that clash with GCP redis certs


7.89.0 (2025-04-28)
-------------------

MAINT:
- Update Python from 3.12.7 to 3.13.3


7.88.0 (2025-04-28)
-------------------

- failed release


7.87.0 (2025-04-25)
-------------------

- WCM-832: unregister zeit.campus package


7.86.0 (2025-04-24)
-------------------

- WCM-836: Ignore empty hdok ids in deleted authors report


7.85.0 (2025-04-23)
-------------------

FIX:
- Broken git ssh call


7.84.0 (2025-04-23)
-------------------

- WCM-831: add filter for print ressort in webhooks


FIX:
- WCM-693: Fix publish volume articles after access change


7.83.0 (2025-04-22)
-------------------

- WCM-693: Update volume content access using storage

- WCM-830: make confighistory work with non-root user account


7.82.0 (2025-04-22)
-------------------

- WCM-785: remove feature toggle WCM-785

- WCM-823: remove toc.csv from volumes


7.81.0 (2025-04-16)
-------------------

MAINT:
- docker image security updates


7.80.0 (2025-04-10)
-------------------

- WCM-611: Switch publish volume content from elasticsearch to content-storage

- WCM-785: storage query for previous/next for volume


7.79.1 (2025-04-10)
-------------------

- WCM-179: Move delete button so it can be reached


7.79.0 (2025-04-10)
-------------------

- failed release


7.78.0 (2025-04-08)
-------------------

- WCM-791: Improve security for docker containers


7.77.0 (2025-04-03)
-------------------

MAINT:
- Be precise about evaluating toggle xml config file: ignore empty root node


7.76.0 (2025-04-03)
-------------------

- WCM-26: Remove migration toggle

- WCM-547: Remove migration toggle


7.75.0 (2025-04-03)
-------------------

- WCM-692, WCM-694, WCM-695, WCM-758: Remove migration toggles


7.74.0 (2025-04-03)
-------------------

- WCM-695: Add toggle for metrics between elastic/sql


7.73.0 (2025-04-03)
-------------------

- MAINT: more verbose logging, no csv input in delete-from-tms-index-script

- WCM-692: Switch image purchase report from elasticsearch to content-storage

- WCM-695: Switch imported content metrics from elasticsearch to content-storage


7.72.0 (2025-04-02)
-------------------

- WCM-694: allow scheduled publish to republish content


7.71.0 (2025-04-02)
-------------------

- WCM-694: restrict days also for retract timeframe


7.70.0 (2025-04-02)
-------------------

- WCM-694: add timeout setting for scheduled publish/retract query


7.69.0 (2025-04-01)
-------------------

- WCM-694: remove option to restrict time range in scheduled query because it does not improve performance

- WCM-807: Implement OR operator in DAV-style connector search

- WCM-808: Transmit None as False to publisher for comments bool fields

- ZO-5382: Remove unused grafana connection, has moved to publisher


7.68.0 (2025-03-31)
-------------------

- WCM-694: skip scheduled publish/retract if pre-conditions not satisfied


7.67.0 (2025-03-28)
-------------------

- WCM-694: improve query for scheduled publish/retract

- WCM-736: Adjust keyword widget to separate TMS API and UI URLs


7.66.0 (2025-03-28)
-------------------

- WCM-694: add new column date_last_retracted

- WCM-736: Remove secondary TMS, migration is now complete


7.65.0 (2025-03-27)
-------------------

- WCM-694: only publish if retract is in the future


7.64.0 (2025-03-26)
-------------------

- WCM-547: Add article_template column


7.63.0 (2025-03-26)
-------------------

- WCM-694: scheduled publish/retract with info from storage


7.62.1 (2025-03-25)
-------------------

- WCM-801: Recursive deletion of folders must only delete content in that folder


7.62.0 (2025-03-25)
-------------------

- WCM-133, WCM-200: Activate preview.zeit.de for production

- WCM-636: Use email instead of userDisplayName to avoid requesting it from AD every time


7.61.0 (2025-03-20)
-------------------

- WCM-694: add scheduled publish/retract columns


7.60.0 (2025-03-19)
-------------------

- WCM-789: Continue publish if TMS fails, retry it asynchronously


7.59.0 (2025-03-18)
-------------------

- WCM-786: Explicitly specify the content types we publish in TMS


7.58.0 (2025-03-18)
-------------------

- WCM-753: add cli interface to run individual publish tasks/services


7.57.0 (2025-03-17)
-------------------

FIX:
- Called wrong method for vgwort metrics


7.56.0 (2025-03-14)
-------------------

- WCM-525: vgwort candidates read from internal database instead of elastic

- WCM-737: Remove authordashboard from publishing


7.55.0 (2025-03-12)
-------------------

- WCM-767: Display ingredients autocomplete list fully instead of cutting of at the module border


7.54.0 (2025-03-12)
-------------------

- WCM-767: Actually save entered ingredients parameters when adding another ingredient

- WCM-767: Remove height restriction on recipelist modules


7.53.0 (2025-03-11)
-------------------

- WCM-525: support empty dates for nullable date columns


7.52.0 (2025-03-11)
-------------------

- WCM-473: Add index to support searching for authors by umlaut-normalized lastname first-letter

- WCM-749: Wire up celery worker healthcheck


7.51.0 (2025-03-07)
-------------------

- WCM-657: Promote searching for ICMSContent by SQL to IRepository.search()


7.50.0 (2025-03-05)
-------------------

- WCM-26: Remove author properties in XML body, fully switch to DAV


7.49.0 (2025-03-04)
-------------------

- WCM-758: add vgwort columns


MAINT:
- Staging sync


7.48.0 (2025-03-04)
-------------------

- WCM-16: Implement setitem and changeProperties in FilesystemConnector, to help migrating zeit.web testcontent

- WCM-743: config cache time set to 60s


MAINT:
- MAINT: allow caching time for all content types


7.47.0 (2025-02-26)
-------------------

- WCM-750: Update to forked fanstatic version to remove pkg_resources dependency


7.46.0 (2025-02-26)
-------------------

FIX:
- Update zodburi to get rid of pkg_resources


7.45.0 (2025-02-25)
-------------------

- WCM-742: Use materialize celery queue for dynamic folders

- WCM-745: Record image source format for tracing


7.44.0 (2025-02-21)
-------------------

- WCM-742: Add recursive cache refresh action for dynamic folders


7.43.0 (2025-02-20)
-------------------

- WCM-723: remove obsolete toggles


7.42.0 (2025-02-18)
-------------------

- ZO-7096: Move dogpile cache to zeit.tickaroo


7.41.0 (2025-02-17)
-------------------

- ZO-7097: Do not load zeit.tickaroo by default, only when required for vivi UI


7.40.0 (2025-02-17)
-------------------

- ZO-7096: Allow selecting liveblog events


7.39.0 (2025-02-17)
-------------------

- WCM-669: add feature toggles to disable tms and elasticsearch completely

- WCM-719: trace search query


7.38.0 (2025-02-13)
-------------------

- WCM-649: remove IZARContent and IZARArticle


7.37.0 (2025-02-12)
-------------------

- WCM-26: Fix more TMS field name bw-compat for author objects


7.36.0 (2025-02-12)
-------------------

- WCM-324: remove unused nextread code


7.35.0 (2025-02-12)
-------------------

- WCM-26: Fix TMS field name bw-compat for author objects


MAINT:
- Invalidate connector cache in bulk scripts


7.34.0 (2025-02-10)
-------------------

- WCM-704: Catch even more zodb errors in connector cache


7.33.0 (2025-02-10)
-------------------

- WCM-704: Handle 'body is not cached' situation gracefully


7.32.0 (2025-02-10)
-------------------

- WCM-704: Catch even more zodb errors in connector cache


7.31.0 (2025-02-07)
-------------------

- WCM-704: Catch more zodb errors in connector cache


7.30.0 (2025-02-06)
-------------------

- WCM-649: Unregister ZAR package


7.29.0 (2025-02-06)
-------------------

FIX:
- Update prometheus metrics to otel 1.30 API


7.28.0 (2025-02-06)
-------------------

- failed release due to GAR pypi error

7.27.0 (2025-02-06)
-------------------

- failed release due to GAR pypi error

7.26.0 (2025-02-06)
-------------------

- WCM-26: Store main author fields in metadata instead of body

- WCM-699: Remove social fields from link form

- WCM-702: Remove unused topicbox automatic_type "preconfigured elastic query"


7.25.0 (2025-02-04)
-------------------

- WCM-690: Record event type and uuid for tracing in webhooks (brightcove, simplecast, speechbert)

- WCM-698: Implement exists, order, limit, offset for dav-style search


7.24.0 (2025-02-03)
-------------------

FIX:
- Remove temporary variables from CommonMetadata classes


7.23.0 (2025-02-03)
-------------------

- WCM-670: Load TMS filter config from /data


7.22.0 (2025-01-31)
-------------------

- WCM-423: Show editor as busy instead of trying to display a lightbox when saving before leaving


7.21.0 (2025-01-31)
-------------------

- failed release due to concurrent changes


7.20.0 (2025-01-30)
-------------------

- WCM-676: Transmit audio objects to data bigquery on publish


7.19.0 (2025-01-29)
-------------------

- WCM-633: catch more generous the object log sweep exception


7.18.0 (2025-01-28)
-------------------

- WCM-605: Remove metric labels we don't care about, this also prevents combinatoric issues with prometheus more static label allocations


7.17.0 (2025-01-28)
-------------------

- WCM-35: Disable elasticsearch version check


7.16.0 (2025-01-28)
-------------------

- WCM-8: Content from reach is no longer resolved via elasticsearch, don't declare it as such


7.15.0 (2025-01-27)
-------------------

- WCM-605: Separate tracing instrumentors mechanics and policy


7.14.0 (2025-01-27)
-------------------

- WCM-659: Remove bugsnag integration, replaced by opentelemetry


7.13.0 (2025-01-27)
-------------------

- WCM-423: Ensure changed inlineforms are saved before leaving the page


7.12.0 (2025-01-27)
-------------------

- WCM-605: Report server/client duration as seconds instead of ms

- WCM-633: handle property cache loss

- WCM-656: Revert "Support smaller viewports for article editing" (7.8.0)


7.11.0 (2025-01-23)
-------------------

- WCM-124: Nightwatch test vivi ui

- WCM-195: fix keyword widget design


FIX:
- FIX: Set LSC for tickaroo liveblogs

- FIX: Set use_default for collapse_preceding_content in liveblogs


MAINT:
- MAINT: Remove legacy liveblog


7.10.0 (2025-01-22)
-------------------

- WCM-124: Add secrets to nightwatch in k8s

- WCM-575: Mock connector search with empty resultset by default

- WCM-614: Return manual "player data" for youtube videos


7.9.0 (2025-01-22)
------------------

- WCM-614: Reorder video form fields

- ZO-6982: Add collapse_highlighted_events setting


7.8.0 (2025-01-21)
------------------

- WCM-614: Support manually creating video objects

- ZO-2426: Add visual submit indicator


7.7.0 (2025-01-16)
------------------

MAINT:
- Gracefully handle empty social embed URLs


7.6.0 (2025-01-16)
------------------

- WCM-575: remove feature flag contentquery_custom_as_sql


7.5.0 (2025-01-16)
------------------

- WCM-195: truncate keywords using ellipsis and show them on hover in full height


7.4.0 (2025-01-14)
------------------

- WCM-626: resolve load dynamic content with removed config


7.3.0 (2025-01-13)
------------------

- WCM-195: display link next to tag title


7.2.0 (2025-01-09)
------------------

- WCM-498: WCM-489: add functionality to ignore uniqueids on publish


MAINT:
- WCM-610: Remove zeit.ldap from deploy depencencies


7.1.0 (2025-01-07)
------------------

- WCM-608: company purchase report with date range input

- WCM-617: provide fake root querysearchview


7.0.0 (2025-01-02)
------------------

- WCM-533: hide legend for access entitlements if field is not available

- WCM-610: Integrate zeit.ldap package as zeit.authentication


6.99.0 (2024-12-27)
-------------------

- WCM-111: Remove undeclared but optional prometheus dependency


6.98.0 (2024-12-27)
-------------------

- WCM-562: Christmas is over

- WCM-609: Remove zeit.cms.relation usage and persistent utility


6.97.0 (2024-12-23)
-------------------

- WCM-111: Make prometheus metrics export fully opt-in


6.96.0 (2024-12-19)
-------------------

FIX:
- Unify IVolume/ICommonMetadata validation settings


6.95.0 (2024-12-19)
-------------------

FIX:
- Unify volume/year validation settings


6.94.0 (2024-12-19)
-------------------

FIX:
- Increase volumes per year validation to 60


6.93.0 (2024-12-19)
-------------------

FIX:
- Use wrong argument in telemetry span


6.92.0 (2024-12-19)
-------------------

- WCM-599: Retract news images instead of deleting them.

- WCM-102: actually respect audio_speechbert flag

- WCM-559: add tts references to articles even if the checksum does not match


6.91.0 (2024-12-18)
-------------------

- WCM-326: add new celery queue for revisions


6.90.0 (2024-12-18)
-------------------

- WCM-175: Remove broken newsimport metrics

- WCM-326: create revision after every checkin


6.89.0 (2024-12-17)
-------------------

- ZO-6758: Resolve account name in Bluesky post url

- WCM-574: remove toggle add_content_permissions and use new content permissions for embeds


MAINT:
- MAINT: Remove vivi logo for deprecated ZAR vertical


6.88.0 (2024-12-12)
-------------------

- FIX: publish script not working when info.date_last_published is None

- WCM-533: added new column for custom access entitlements

- WCM-574: remove more obsolete toggles


MAINT:
- Make text in property table selectable/copyable


6.86.0 (2024-12-10)
-------------------

- WCM-327: collective publication in a single task for dynamic folders


6.85.0 (2024-12-09)
-------------------

- WCM-463: remove obsolete content cache


6.84.0 (2024-12-06)
-------------------

- WCM-327: improve dynamic folder publication

- WCM-574: remove obsolete feature toggles


6.83.0 (2024-12-04)
-------------------

- WCM-532: Add zeit.entitlements.accepted() API to calculate required entitlements


6.82.0 (2024-12-04)
-------------------

- WCM-477: Do not bulk-publish content with semantic change by default

- WCM-540: Extend attributes of IPodcast for Spotify RSS feed


6.81.0 (2024-12-02)
-------------------

- WCM-257: Improve news import handling


6.80.0 (2024-12-02)
-------------------

- WCM-456: Include column name in sql converter error messages

- WCM-474: Hide elastic-query option in UI except for ZMO

- WCM-568: Ignore brightcove change events that were triggered by our own checkin handler

- ZO-6370: add image row module


6.79.0 (2024-11-28)
-------------------

- WCM-566: only publish tts once in creation process


6.78.0 (2024-11-28)
-------------------

- WCM-563: Include lock info when updating connector cache in sql contentquery

- WCM-563-update: Only prefill cache with missing entries from search_sql, don't (needlessly) update


6.77.0 (2024-11-28)
-------------------

- WCM-558: Update bulk publish script to ignore airship again after ZO-5382

- WCM-563-message: Add more known data to the LockingError message


MAINT:
- PERF: Skip query if count is zero anyway (e.g. in zeit.web pagination)


6.76.0 (2024-11-25)
-------------------

- WCM-477: Update content channels from urbanairship template channels


6.75.0 (2024-11-22)
-------------------

- WCM-551: Update body cache when loading content anyway (prevents an extra sql query for each load)


6.74.0 (2024-11-22)
-------------------

- WCM-551: Cache analyzed toggles, not just their XML nodes (5% performance gain)


6.73.0 (2024-11-22)
-------------------

- WCM-544: read centerpage type from properties and not from xml body

- WCM-466: remove free/dynamic access toggle


6.72.0 (2024-11-20)
-------------------

- WCM-468: Only freeze staging sql time interval old end, not today end as well

- WCM-490: Trace errors, result count for sql contentquery

- WCM-542: Add option to force sql filter before sort

- WCM-543: Remove obsolete DAV-style etag-based conflict resolution in connector body cache


6.71.0 (2024-11-19)
-------------------

- WCM-527: sort by print_page not page


6.70.0 (2024-11-18)
-------------------

- WCM-520: Fix total_hits sqlalchemy error in SQL queries

- WCM-539: SQL custom query handles NULL in not-equal comparisons


FIX:
- Use correct field name to sort elastic raw queries by dlps (belongs to 6.66.0)


MAINT:
- Allow using zc.form Combination field in pembeds


6.69.0 (2024-11-18)
-------------------

- WCM-527: add content query fields print-volume, -year and -ressort


6.68.0 (2024-11-15)
-------------------

- WCM-401: Auto area with CP source now also hides dupes of the source CP


6.67.0 (2024-11-14)
-------------------

- WCM-519: Redirect clipboard to index instead of view to open the working copy if available

- WCM-526: Encapsulate raw sql query in parens, so adding more clauses works if it uses OR

- ZO-6156: Restore show_timeline liveblog checkbox in UI, until zeit.web is updated


6.66.0 (2024-11-13)
-------------------

MAINT:
- Consistency: sort elastic raw queries by dlps like eveything else, not dfr


6.65.0 (2024-11-12)
-------------------

- WCM-471: Add columns required for raw queries

- WCM-523: Allow excluding custom query from being switched to sql via toggle

- ZO-6156: Add liveblog teaser setting for timeline


6.64.0 (2024-11-08)
-------------------

- WCM-507: elastic search returns authors field


6.63.0 (2024-11-08)
-------------------

- WCM-507: show author infos in search results


6.62.0 (2024-11-07)
-------------------

- WCM-490: Record explicit span for sql contentquery


6.61.0 (2024-11-07)
-------------------

- WCM-153: make page writeable and add interred fields

- WCM-511: Return actually complete content objects from SQL areas


FIX:
- Bring back variable resolution for error messages in log


6.60.0 (2024-11-04)
-------------------

- WCM-445: Add galery_type column

- WCM-506: Load teaser images lazy in CP editor


6.59.0 (2024-10-23)
-------------------

- WCM-462: Toggle column access in batches, to support future migrations


6.58.0 (2024-10-23)
-------------------

- WCM-468: Restrict time interval for SQL queries

- WCM-468: Remove unused custom query order "last semantic change"


6.57.0 (2024-10-22)
-------------------

- WCM-411: Fix property name for 'volume_number'

- WCM-456: Keep WebDAVProperties API consistent, operate with string values independent of connector toggles. Instead convert property values only, when metadata columns are origin or source.


MAINT:
- Use pendulum datetime library everywhere


6.56.0 (2024-10-18)
-------------------

- WCM-464: Support separate timeout for search_sql


6.55.0 (2024-10-15)
-------------------

- WCM-20: Retrieve a configurable minimum of rows, to force sql query planner to use indexes

- WCM-295: Remove deprecated authors freetext property


6.54.0 (2024-10-14)
-------------------

FIX:
- Apply TMS type conversion for datetime in both directions


6.53.0 (2024-10-14)
-------------------

FIX:
- Remove development model class remnants


6.52.0 (2024-10-11)
-------------------

- WCM-452: Handle empty channels in type conversion


6.51.0 (2024-10-11)
-------------------

- FIX: manual audio publish was not working

- WCM-411: Set published column not nullable


6.50.0 (2024-10-10)
-------------------

- WCM-401: add new audio object type 'custom'

- WCM-434: convert native types in retresco

- WCM-448: Make type conversion work when only write toggle is active, but not read


6.49.0 (2024-10-09)
-------------------

- WCM-433: Set column to None for DeleteProperty


6.48.0 (2024-10-08)
-------------------

- WCM-20: Implement evaluating custom query with SQL

- WCM-411: Move important search fields to columns for custom query


6.47.0 (2024-10-08)
-------------------

- WCM-433: Support multiple databases in sql testlayer


6.46.0 (2024-10-07)
-------------------

- WCM-433: Make zodb support (for connector caches) optional in SQL db testlayer


6.45.0 (2024-10-07)
-------------------

- WCM-285: Custom type for sql/jsonb to work with channels tuple type

- WCM-435: simultaneous write into dedicated columns and unsorted


6.44.0 (2024-10-04)
-------------------

- FIX: replace deprecated attach_span with attach_context


6.43.0 (2024-10-04)
-------------------

- WCM-3: add e-paper publish webhook

- WCM-285: Disable zope.security proxy for tuples, they are immutable anyway

- WCM-292: Remove custom query order random, it was basically never used


MAINT:
- Python 3.12.6 -> 3.12.7


6.42.0 (2024-09-30)
-------------------

- WCM-291: Add forgotten date_last_modified column

- WCM-408: remove fallback logic of teaserText


6.41.0 (2024-09-26)
-------------------

- WCM-291: Add indexes so we can sort by timestamp columns


6.40.0 (2024-09-26)
-------------------

- WCM-22: Suppress errors during automatic area sql queries

- WCM-285: bring back the old behavior for the connector and write data as read if enabled


6.39.0 (2024-09-24)
-------------------

- WCM-414: Escape json field names in generic search function


6.38.0 (2024-09-23)
-------------------

- WCM-115: More visible sidebar toggler

- WCM-22: Implement automatic content query with raw SQL query


6.37.0 (2024-09-18)
-------------------

- WCM-285: remove the development columns from the standard dav converter


6.36.0 (2024-09-18)
-------------------

- WCM-285: add new columns channel and subchannels

- WCM-291: move timestamps into columns


6.35.0 (2024-09-17)
-------------------

- WCM-316: add teaser title, teaser text and background color to volume


6.34.0 (2024-09-11)
-------------------

- ZO-6198: Remove liveblog config intersection_type


MAINT:
- Update dependencies (Python 3.12.6)


6.33.0 (2024-09-06)
-------------------

- MAINT-20240902tb: upgrade script template in vivi-deployment


MAINT:
- MAINT: Remove obsolete dav connector and zope dav connector


6.32.0 (2024-09-02)
-------------------

- WCM-248: Use feature_toggle.xml source in zeit.conntector


6.31.0 (2024-09-02)
-------------------

- ZO-6159: Allow choosing gallery teaser in animation


FIX:
- make resource_class for mock connector configurable


6.30.0 (2024-08-27)
-------------------

FIX:
- WCM-268: No hook, no hook id obviously


6.29.0 (2024-08-27)
-------------------

FIX:
- Revert Remove delay from inline form save, to avoid overlapping with other actions (that were triggered immediately)


6.28.0 (2024-08-26)
-------------------

- WCM-268: Celery must search for the hook object itself


6.27.0 (2024-08-26)
-------------------

- WCM-268: Notify webhook conditionally

- ZO-883: remove avif format due to incompabilities of greyscale with browsers


6.26.0 (2024-08-19)
-------------------

- ZO-5819: add export to datascience


6.25.0 (2024-08-16)
-------------------

- WCM-248: vivi feature-toggles are now in github/zeitonline/config.git


6.24.0 (2024-08-14)
-------------------

- WCM-59: Remove delay from inline form save, to avoid overlapping with other actions (that were triggered immediately)


6.23.0 (2024-08-14)
-------------------

- WCM-271: Use entirely separate model classes for developing columns


6.22.0 (2024-08-13)
-------------------

- WCM-271: Implement mechanics to move metadata from json into individual columns


6.21.0 (2024-08-12)
-------------------

- WCM-187: Record spans for cli entrypoints/cronjobs and background=False publish tasks


6.20.0 (2024-08-08)
-------------------

MAINT:
- ZO-141: Switch newsimport pushgateway from VMs to k8s


6.19.0 (2024-08-07)
-------------------

MAINT:
- Update opentelemetry library to 1.26


6.18.0 (2024-08-07)
-------------------

- WCM-276: Create index to support parent_path prefix matches


6.17.0 (2024-08-07)
-------------------

- WCM-247: Remove obsolete table paths


6.16.0 (2024-08-06)
-------------------

- ZO-5697: Revert explicit paths table joining, it does not actually give us more information


6.15.0 (2024-08-06)
-------------------

- ZO-5697: Make usage of paths table fully explicit

- ZO-5809: Add show_timeline_in_teaser option to liveblog module

- ZO-5817-5885: script for replacing region/areas with/in kind=parquet


6.14.0 (2024-07-31)
-------------------

- ZO-5697: Read from new properties colummns parent_path and name


6.13.0 (2024-07-30)
-------------------

- ZO-5407_ZO-5408: script for replacing deprecated teaser layouts (vivi-depl)

- ZO-5817-5884: script rm-outdated-parquet-areas.py


6.12.0 (2024-07-25)
-------------------

- ZO-5830: paste settings are case sensitive


FIX:
- Fix image-encoders.xml config file format so it actually works


MAINT:
- DEV-852, ZO-5801: Remove obsolete namespaces


6.11.0 (2024-07-22)
-------------------

- ZO-5659: Fix programming mistake in vgwort report cronjob

- ZO-5830: Give environment variables precendence over paste.ini settings


6.10.0 (2024-07-19)
-------------------

- ZO-883: add pillow-avif-plugin to requirements.txt


6.9.0 (2024-07-19)
------------------

- ZO-5548: add IndexNow implementation for publish article and publish centerpage


6.8.0 (2024-07-17)
------------------

FIX:
- Be defensive when no product config exists for a package


6.7.0 (2024-07-16)
------------------

- ZO-5850: Don't wait if the DB revision is newer than what we know on disk


6.6.0 (2024-07-15)
------------------

- ZO-4165: Replace commentjson with rapidjson and support comments


MAINT:
- MAINT: remove needless class


6.5.0 (2024-07-15)
------------------

- ZO-4617: Only allow imagegroups as teasers, not single images

- ZO-5737: rename field 'Ressort (Druck)' to 'Print-Ressort' and make editable, remove byline


6.4.0 (2024-07-11)
------------------

- ZO-5176: rename feature toggle to write-to-new-columns-name-parent-path


6.3.0 (2024-07-11)
------------------

- ZO-5176: add parent_path and name column to table properties


6.2.0 (2024-07-10)
------------------

MAINT:
- MAINT: Remove feature toggle `disable_connector_body_checksum`


6.1.0 (2024-07-09)
------------------

- ZO-5779: Skip XML comments in BigQuery JSON serialization


6.0.0 (2024-07-09)
------------------

- ZO-4281: Set up alembic for database migrations

- ZO-5613: Remove slowlog, it triggers python segfaults

- ZO-5470: Always provide now timestamp with timezone information


5.195.0 (2024-07-04)
--------------------

FIX:
- Retry zodb conflict errors in objectlog sweep and other cronjobs


5.194.0 (2024-06-28)
--------------------

- ZO-4274: Remove copy and paste xml mechanic for metadata

- ZO-4275: removed deprecated zeit.cms.redirect

- ZO-5659: Commit content cache after each document in vgwort report, to avoid conflict errors


MAINT:
- Add uuid to UI HTML as body/data attribute


5.193.0 (2024-06-26)
--------------------

- ZO-5573: Update opentelemetry to 1.25/0.46, including prometheus adjustments


5.192.1 (2024-06-25)
--------------------

- ZO-5637: Move helper function to interfaces to avoid importing SOAP machinery


5.192.0 (2024-06-25)
--------------------

- ZO-5665: Allow accessing IAudioReferences of IAnimation objects


5.191.0 (2024-06-25)
--------------------

- ZO-5471: Reactivate sql checksum/conflict validation

- ZO-4275: Remove XMLReferenceUpdater

- ZO-5193: handle also whitespaces including XML for Big Query JSON transformation

- ZO-5421: Add CLI entrypoints that used to be deployment scripts

- ZO-5599: Prevent ConflictError in confighistory job

- ZO-5637: Silently ignore maintenance window in vgwort order token cronjob


5.190.0 (2024-06-20)
--------------------

- ZO-5471: Disable sql checksum implementation


5.189.0 (2024-06-17)
--------------------

- ZO-5560: add proxy staging proxy service


5.188.0 (2024-06-12)
--------------------

- ZO-5471: Connector add must check for inconsistencies before overwrite


5.187.0 (2024-06-11)
--------------------

- ZO-5567: continue news import even if 1 article fails


5.186.0 (2024-06-11)
--------------------

- ZO-5482: do not check for tasks in multi publish


5.185.0 (2024-06-11)
--------------------

- ZO-5181: Script for removing kpi tables

- ZO-5482: move multi publish into per article celery task


5.184.0 (2024-06-07)
--------------------

- ZO-5409: Remove "platform" configuration axis


5.183.0 (2024-06-06)
--------------------

- ZO-5454: newsimport retract works even if called multiple times for the same article

- ZO-5484: Skip retracting currently locked objects


FIX:
- Fix nondeterministic runtime error in metrics collection


5.182.0 (2024-05-31)
--------------------

- ZO-5477: explicitly associates the lock with the content object


5.181.0 (2024-05-29)
--------------------

- ZO-5475: Prevent superfluous duplicate TMS index tasks for breaking news


5.180.0 (2024-05-28)
--------------------

- ZO-3458: Update to Python-3.12

- ZO-5477: fix image import for dpa news


5.179.0 (2024-05-28)
--------------------

- ZO-5456: move zeit.newsimport into vivi

- ZO-5457: Raise exceptions from cli.runner


5.178.0 (2024-05-27)
--------------------

- ZO-5455: Create git branch after origin is set up


5.177.0 (2024-05-27)
--------------------

- ZO-5455: Explicitly create git branch


5.176.0 (2024-05-27)
--------------------

- ZO-5461: fix steal lock


5.175.0 (2024-05-27)
--------------------

- ZO-5455: set config history upstream branch

- ZO-5460: Restore IZMOGallery+IZMOLink interfaces


5.174.0 (2024-05-26)
--------------------

- ZO-4751: Remove unused facebook newstab integration

- ZO-5394: Calculate requests client duration metric as ms


FIX:
- Refresh topicpages iterator on retry due to conflict


5.173.0 (2024-05-22)
--------------------

- ZO-5138: remove social media channels for ze.tt, campus and magazin

- ZO-5138: remove facebook metric account expires

- ZO-5138: Remove checkbox in breaking news "social media" that posts to facebook and twitter

- ZO-5138: remove facebook api calls from push


5.172.0 (2024-05-21)
--------------------

- ZO-5209: Make sql resource class overridable


5.171.0 (2024-05-17)
--------------------

- ZO-5272: Return celery failure correctly


5.170.0 (2024-05-16)
--------------------

- ZO-5382: Call Airship via publisher instead of zeit.push AfterPublishEvent (toggle: `push_airship_via_publisher`)


5.169.0 (2024-05-16)
--------------------

- ZO-5196: switch vivi staging to internal ingress


5.168.0 (2024-05-16)
--------------------

- ZO-5378: if checksum is missing in AUDIO_CREATED event return 400 BAD_REQUEST to speechbert


5.167.0 (2024-05-14)
--------------------

- ZO-5138: simplify Social Media connections and configuration

- ZO-5358: Replace invalidate-based wait_for_commit helper with commit_with_retry


MAINT:
- Allow disabling video export with feature toggle


5.166.0 (2024-05-10)
--------------------

- ZO-5192: Report complete video url including seo slug to google pub/sub


FIX:
- Actually exclude healthcheck from tracing


MAINT:
- Convert publish/retract helper scripts to entrypoints


5.165.0 (2024-05-08)
--------------------

MAINT:
- Instrument publish for tracing


5.164.0 (2024-05-08)
--------------------

- ZO-5306: Persist locks for publish/retract as soon as possible, to prevent concurrent access


MAINT:
- Instrument transaction commit/abort for tracing


5.163.0 (2024-05-08)
--------------------

- BEM-204: Make use of prometheus multiprocess support for celery

- ZO-5274: make staging available through external ingress


5.162.0 (2024-05-07)
--------------------

- ZO-4933: Retry failed ARD API calls and less misleading error message for them


5.161.0 (2024-05-06)
--------------------

- ZO-5306: Work around atomicity issues by issuing an explicit commit before calling the external publisher system


5.160.0 (2024-05-06)
--------------------

- ZO-5186: make all article modules foldabele

- ZO-5259: Respect meta:type property in sql connector

- ZO-5282: retract overdue images

- ZO-5305: commit transactions before running publish inside celery tasks


5.159.0 (2024-05-02)
--------------------

- ZO-5302: Return uuid from sql search correctly


5.158.0 (2024-05-02)
--------------------

- ZO-5295: Return one item per search result (not per attribute) in sql connector


5.157.0 (2024-05-02)
--------------------

- ZO-5276: Use sql index to query unsorted properties


5.156.0 (2024-05-02)
--------------------

- ZO-5253: Preserve existing properties in sql setitem


5.155.0 (2024-04-29)
--------------------

- ZO-5236: Trigger image build with updated zeit.newsimport


5.154.0 (2024-04-29)
--------------------

- BEM-204: Switch to custom metrics provider to work in multiprocess conditions


5.153.0 (2024-04-25)
--------------------

- ZO-5231: use correct namespace for property renameable


5.152.0 (2024-04-24)
--------------------

- ZO-4966: force_mobile_image default value should be true in automatic teasers


5.151.0 (2024-04-23)
--------------------

MAINT:
- Update Python from 3.10.7 to 3.10.14


5.150.0 (2024-04-23)
--------------------

- ZO-4966: fix: force_mobile_image in auto areas is saved correctly (again)


5.149.0 (2024-04-22)
--------------------

- ZO-4613: remove video playlist content type

- ZO-4983: Move summy attribute `avoid_create_summary` to non admin area

- ZO-5089: Remove all but one twitter message option


5.148.0 (2024-04-22)
--------------------

- ZO-4940: invalidate cache of article if tts is created


5.147.0 (2024-04-18)
--------------------

- ZO-4640: Entrypoint to sync /data folder to git

- ZO-4919: Use batch APIs for sql connector where possible


5.146.0 (2024-04-16)
--------------------

- ZO-5166: Update to current IR MDB drag/drop protocol


5.145.0 (2024-04-15)
--------------------

- ZO-5142: Allow disabling publisher services with feature toggle "disable_publisher_NAME"


5.144.0 (2024-04-11)
--------------------

- ZO-4974: remove feature toggle publish_bigquery_json

- ZO-5050: read facebook credentials from secret store instead of config file

- ZO-5125: Cache lock data in property cache for sql connector, just like dav does


FIX:
- ZO-4800: Remove obsolete class


5.143.0 (2024-04-10)
--------------------

FIX:
- ZO-4886: Do not break on missing ui dependencies


5.142.0 (2024-04-10)
--------------------

- ZO-5022: Apply samplerate for both, sql and zodb


5.141.0 (2024-04-09)
--------------------

- ZO-5022: Enable tracing with sampling for sql connector


5.140.0 (2024-04-09)
--------------------

- ZO-4940: feature toggle to disable transaction commit workaround for multi publish

- ZO-5085: support loading config files from storage api


5.139.0 (2024-04-08)
--------------------

- ZO-5086: Update default filename


5.138.0 (2024-04-08)
--------------------

- ZO-5017: remove push directly toggles from twitter social form


5.137.0 (2024-04-05)
--------------------

- ZO-5017: do not send push to twitter


5.136.0 (2024-04-04)
--------------------

- ZO-5017: restore ui but remove the API integration to twitter


5.135.0 (2024-03-28)
--------------------

- ZO-4917: Make lock cleanup cronjob work

- ZO-5027: Implement body cache for SQL connector


5.134.0 (2024-03-27)
--------------------

- ZO-4627: Pretty print XML at least for display

- ZO-5001: Use global configuration for invalid link targets in article editor as well

- ZO-5020: Implement listing the root folder in SQL connector

- ZO-5028: Implement child name caching for SQL connector


5.133.0 (2024-03-27)
--------------------

- ZO-4800: Don't copy internal properties to XML


5.132.0 (2024-03-26)
--------------------

- ZO-4800: Replace unused IResource.contentType with IResource.is_collection

- ZO-5026: Introduce SQL/Zope connector with zodb-based caching


5.131.0 (2024-03-25)
--------------------

MAINT:
- Create workingcopy URLs with -2 less often


5.130.0 (2024-03-25)
--------------------

- ZO-4917: implementation of locking timeout

- ZO-4982: remove dav specific code from LockStorage


5.129.0 (2024-03-21)
--------------------

- ZO-4726: Adds summy publish task

- ZO-4886: Do not write to locked object


5.128.0 (2024-03-20)
--------------------

- ZO-4053: Update to current openapi-schema-validator API

- ZO-4557: further options for accelerating publish_content.py

- ZO-4724: Implement 'avoid create summary' article attribute

- ZO-4967: Don't create an empty/broken image group if brightcove provides none


5.127.0 (2024-03-12)
--------------------

- ZO-4915: copy optimzation, clone row

- ZO-4916: copy blob directly on cloud storage


5.126.0 (2024-03-11)
--------------------

- ZO-4267: Implement copy, move and lock in zeit.connector

- ZO-4799: Remove obsolete rules about force_mobile_image defaults

- ZO-4881: update table locks, foreign key to content table instead of paths

- ZO-4882: remove locks after deletion of collection from children

- ZO-4913: Add tags to XML only once


5.125.0 (2024-03-06)
--------------------

- ZO-4607: Make DAV resource class configurable, for migration


5.124.0 (2024-03-06)
--------------------

FIX:
- Handle XML comments in article body


5.123.0 (2024-03-05)
--------------------

- ZO-4880: Fix unlock API for zope cache connector


5.122.0 (2024-03-04)
--------------------

- ZO-4880: Prevent unlocking a resource that was locked externally

- ZO-4549: script for deleting contents in TMS indexes

- ZO-4776: replace rankings.zeit.de URLs by studiengaenge.zeit.de (vivi-deployment)


5.121.0 (2024-03-04)
--------------------

- ZO-4867: Update topicpage whitelist to use etree instead of objectify API


5.120.0 (2024-02-29)
--------------------

- ZO-4627: Fix edge cases discovered via bugsnag


MAINT:
- Remove opentelemetry metrics workaround, has been fixed in 1.23


5.119.0 (2024-02-29)
--------------------

- ZO-4783: Require properties as strings in mock connector, like DAV


5.118.0 (2024-02-28)
--------------------

- ZO-4783: Don't change properties when adding a resource in mock connector, just like DAV connector


5.117.0 (2024-02-27)
--------------------

FIX:
- Handle empty lines etc correctly, e.g. in markdown fields


5.116.0 (2024-02-27)
--------------------

- ZO-4801: Fix saving audio reference on article

- ZO-4801: Display request errors that occur in JS forms (toggle: `inlineform_alert_error`)


5.115.0 (2024-02-26)
--------------------

- ZO-4712: Add xmlrpc user for content-storage-api


5.114.0 (2024-02-23)
--------------------

- ZO-4651: remove podcast block and header (everything podigee related)


5.113.0 (2024-02-21)
--------------------

- ZO-4627: Replace lxml.objectify with plain lxml.etree usage


5.112.0 (2024-02-21)
--------------------

- ZO-4467: deprecate cook profiles


5.111.0 (2024-02-20)
--------------------

- ZO-4751: Deactivate publishing to facebooknewstab


5.110.0 (2024-02-19)
--------------------

- ZO-4683: Only publish article after referencing tts audio if it is unchanged

- ZO-4687: Store our own date_last_modified instead of relying on DAV

- ZO-859: Log XML body after checkout to aid debugging


5.109.0 (2024-02-15)
--------------------

- ZO-3967: Consolidate importer metrics into vivi_recent_content_published_total wit label content (news, video, podcast, tts)


5.108.0 (2024-02-13)
--------------------

- ZO-4333: vivi-deployment: script: retract zett images with unknown copyright and write memo for them in articles

- ZO-4649: Configure max retries for speech webhook celery task


5.107.0 (2024-02-09)
--------------------

- ZO-4457: TTS migration: do not add tts to articles that are published-with-changes


5.106.0 (2024-02-09)
--------------------

MAINT:
- increase retry delay to 5min for speech webhook


5.105.0 (2024-02-09)
--------------------

- ZO-4649: calculate checksum of article body and compare against tts audio before adding audio reference


5.104.0 (2024-02-08)
--------------------

- ZO-3972: changefile for fix podcast migrate script

- ZO-4226: checkin notification hooks deactivated by default for tts migration and publish scripts


5.103.0 (2024-02-06)
--------------------

- ZO-4612: Create publisher payload per content object and catch errors


5.102.0 (2024-02-05)
--------------------

- ZO-4226: update tts migration script, write non-migratable articles to a file


5.101.0 (2024-02-05)
--------------------

- ZO-4226: migrate TTS script in vivi-deployment


5.100.0 (2024-02-01)
--------------------

FIX:
- ZO-4549: wait_for_commit required an extra argument which was never added


MAINT:
- use audio type translation in object detail view


5.99.0 (2024-01-31)
-------------------

- ZO-4225: print checksum object as checksum


5.98.0 (2024-01-30)
-------------------

- ZO-4225: filter audio references by type

- ZO-4460: Ensure audio article reference and do not enrich audio objects

- ZO-4461: Delete tts audio via speech webhook


5.97.0 (2024-01-25)
-------------------

- ZO-4460: Connect tts audio object with corresponding article


5.96.0 (2024-01-22)
-------------------

- ZO-4496: Retry celery task on simplecast 429 error


5.95.0 (2024-01-19)
-------------------

- ZO-4223: use short article uuid from speechbert to get content


FIX:
- Audio: filename in navigation layout


MAINT:
- Use live URL for bigquery instead of uniqueId


5.94.0 (2024-01-19)
-------------------

- ZO-4483: Set series if podcast episode is dropped into article


5.93.0 (2024-01-18)
-------------------

- ZO-4223: Create TTS audio object from speechbert payload


5.92.0 (2024-01-15)
-------------------

- ZO-4090: Remove ZEO support


FIX:
- ZO-1156: Fix checkout for broken ghost entries in clipboard and remove body delegates

- ZO-4321: Tuple required


MAINT:
- Make pendulum-3.x work with zodbpickle


5.91.0 (2024-01-09)
-------------------

- ZO-4318: Increase padding for delete icon to move it away from macOS scrollbars


5.90.0 (2024-01-09)
-------------------

- ZO-4455: Add year field to CP admin menu


5.89.0 (2024-01-08)
-------------------

- ZO-4449: Create explicit contenthub user instead of reusing the internal invalidate user


5.88.0 (2024-01-08)
-------------------

- ZO-4015: Support rediss in longterm scheduler


5.87.0 (2024-01-05)
-------------------

- ZO-4091: Set up RelStorage tracing

- ZO-4321: Save tts audio specific data


5.86.0 (2024-01-02)
-------------------

FIX:
- Happy new year


5.85.0 (2023-12-27)
-------------------

- ZO-4369: Add complete audio episode notes html to article body


5.84.0 (2023-12-20)
-------------------

- ZO-4224: add celery queue speech


5.83.0 (2023-12-19)
-------------------

- ZO-4104: improve error handling for can_retract, fix tests

- ZO-4224: add webhook for text to speech


5.82.0 (2023-12-18)
-------------------

- ZO-4370: add rss feed to podcasts.xml


5.81.0 (2023-12-14)
-------------------

FIX:
- Christmas


5.80.0 (2023-12-14)
-------------------

- ZO-4214: add search filter for audio content type

- ZO-4384: handle simplecast event transcode_finished


5.79.0 (2023-12-12)
-------------------

FIX:
- ZO-4220: cli module add missing import


5.78.0 (2023-12-11)
-------------------

- ZO-4220: grant producer rights to publish audio


5.77.0 (2023-12-08)
-------------------

- ZO-4104: retract workflow validation for podcast episodes


5.76.0 (2023-12-07)
-------------------

- ZO-4329: add adapter for podcast setting to real image

- ZO-862: add zope shell convenience function and add wait_for_commit
  and login functions


5.75.0 (2023-12-06)
-------------------

- ZO-4262: Support deleting properties in sql connector


5.74.0 (2023-12-04)
-------------------

- ZO-4293: `load` event is being triggered for both tabs therefore check which tab we are in before setting form


5.73.0 (2023-12-01)
-------------------

- ZO-3830: manual trigger for simplecast update should also publish changes

- ZO-4328: Add color and image attributes to Podcast class


5.72.0 (2023-11-29)
-------------------

- ZO-3897: filter for podcasts in search


5.71.0 (2023-11-28)
-------------------

- ZO-4254: index audio objects


5.70.0 (2023-11-27)
-------------------

- ZO-3830: Show simplecast update button only for checked in audio


5.69.0 (2023-11-24)
-------------------

- ZO-3830: Allow manual update of audio object from simplecast


5.68.0 (2023-11-22)
-------------------

- ZO-4201: Return short uuid without any adornments


5.67.0 (2023-11-22)
-------------------

FIX:
- ZO-4198: publish audio object episode update even if it's published already


5.66.0 (2023-11-21)
-------------------

- ZO-3967: Record metric vivi_recent_audios_published_total

- ZO-4057: Truncate temporary table before running zodbpack


MAINT:
- MAINT: lint and autoformat code with ruff


5.65.0 (2023-11-15)
-------------------

- ZO-3764: article title, teasertext and body automatically edited if audio is added


5.64.0 (2023-11-14)
-------------------

- ZO-3967: Update opentelemetry metrics patch to version 1.21


5.63.0 (2023-11-14)
-------------------

- ZO-4057: Handle configuration defensively, e.g. for publisher


5.62.0 (2023-11-13)
-------------------

- ZO-3688: Save ad-free podcast link to audio object

- ZO-4071: Save simplecast dashboard link to audio object


5.61.0 (2023-11-08)
-------------------

- ZO-3812: remove unused feature 'Fläche verknüpfen'

- ZO-3967: Work around opentelemetry histogram bug


5.60.0 (2023-11-07)
-------------------

- ZO-4145: Shrink teaser drag handle so it does not include the edit bar


5.59.0 (2023-11-07)
-------------------

- ZO-3967: Expose otel metrics for prometheus


5.58.0 (2023-11-03)
-------------------

- ZO-4130: Revert "Merge pull request #546 from ZeitOnline/ZO-3967"


5.57.0 (2023-11-03)
-------------------

- ZO-3904: Audio reference gives article podcast type

- ZO-3967: Expose otel metrics for prometheus


MAINT:
- ZO-3967: add test for regular conformity check of simplecast response we get

- IAudios renamed to IAudioReferences


5.56.0 (2023-10-30)
-------------------

FIX:
- Cast Simplecast timeout into int

- Skip update if audio is locked


5.55.0 (2023-10-27)
-------------------

- ZO-4033: Make all modules scrollable

- ZO-4037: Only inflate the current landing zone in article, just like in cp editor


5.54.0 (2023-10-26)
-------------------

- ZO-4033: Repair folding of article modules


5.53.0 (2023-10-26)
-------------------

- ZO-4063: Use whole teaser module insides as draggable


5.52.0 (2023-10-26)
-------------------

- ZO-3997: Audio object form without publish or retract actions

- ZO-4033: Adjust module heights for pembed, topicbox

- ZO-4051: Remove undo functionality from cp+article editor

- ZO-4096: sync publish state even if episode is just added


5.51.0 (2023-10-26)
-------------------

- ZO-4033: Set fixed heights for all article modules to prevent scroll jumping


5.50.0 (2023-10-25)
-------------------

- ZO-4081: Support packing relstorage via zodburi

- ZO-4091: Implement tracing for RelStorage


5.49.0 (2023-10-25)
-------------------

- ZO-4081: Add support for psql://servicename zodburi


5.48.0 (2023-10-25)
-------------------

- ZO-3999: display audio duration in format hh:mm:ss on object details page

- ZO-4063: Restore dragging content from teaser module to clipboard


FIX:
- ZO-1810: Remove `urn:uuid:` prefix before passing UUIDs to PostgreSQL


5.47.0 (2023-10-24)
-------------------

- ZO-3998: Check if publish dependencies can be published before publishing them

- ZO-4019: Simplecast event 'Update Episode' can create a new episode if the episode does not exist

- ZO-4057: Make DAV body cache blob threshold configurable


5.46.0 (2023-10-20)
-------------------

- ZO-4055: Log stack trace of nested publish errors, don't swallow them inside MulitPublishError


5.45.0 (2023-10-18)
-------------------

MAINT:
- Remove obsolete feature toggle push_airship_com/eu, eu is the production default for quite some time now


5.44.0 (2023-10-18)
-------------------

MAINT:
- Remove unused sourcepoint js file import


5.43.0 (2023-10-17)
-------------------

- ZO-3997: restrict retract and delete permissions for audio


5.42.0 (2023-10-17)
-------------------

- ZO-3846: ensure podcast episode type is always 'podcast'


5.41.0 (2023-10-16)
-------------------

- ZO-3996: Import simplecast updated timestamp as last_semantic_change


5.40.0 (2023-10-16)
-------------------

- ZO-4017: Collect metric for available kpi values in TMS


5.39.0 (2023-10-12)
-------------------

- ZO-3579: Record external podcast id


5.38.0 (2023-10-12)
-------------------

MAINT:
- Unconditionally record DAV spans


5.37.0 (2023-10-12)
-------------------

- ZO-3987: Create ZODB connection only after fork


5.36.0 (2023-10-11)
-------------------

- ZO-147: Support repoze.vhm instead of requiring vh traverser


5.35.0 (2023-10-11)
-------------------

- ZO-3824: Fix simplecast webhook body tracing


5.34.0 (2023-10-11)
-------------------

- ZO-1939: Flatten all XML mixed content cases


FIX:
- Restore display of publish-state circle in directory listings


5.33.0 (2023-10-10)
-------------------

- ZO-1939: Send properties and body as json to bigquery, when toggle 'publish_bigquery_json' is set


5.32.1 (2023-10-10)
-------------------

- ZO-3978: Include test config files in release, since zeit.web uses them


5.32.0 (2023-10-10)
-------------------

- ZO-3960: Apply free/dynamic access toggle only to articles


5.31.6 (2023-10-10)
-------------------

- ZO-3824: add http.body of simplecast webhook to tracing


5.31.5 (2023-10-09)
-------------------

MAINT:
- Update ZEO instrumentation to 5.4 API


5.31.4 (2023-10-09)
-------------------

- ZO-3822: implement retract for audio objects

- ZO-3846: show details about the audio element inside the article


FIX:
- Increase size for article landing zone

- align details heading and publish state vertically

- move 'remove'-button for object references to prevent preview and cms button being on top of each other


MAINT:
- Update dependencies


5.31.3 (2023-09-28)
-------------------

- MAINT: Run tests on multiple cores.

- ZO-3822: implement publish for audio objects

- ZO-3851: refactor simplecast requests

- ZO-3933: podigee_id attribute to podcast source, ensure parallel operation of podcast hosts


5.31.2 (2023-09-25)
-------------------

- ZO-3771: Set audio_type during import

- ZO-3821: Display title in audio object details


5.31.1 (2023-09-22)
-------------------

- ZO-3771: Improve Audio object layout in code

- ZO-3821: Audio objects provide ICommonMetadata, so they are indexed in TMS


5.31.0 (2023-09-20)
-------------------

- ZO-3844: Move audio form below teaser form

- ZO-3845: Add audio module for article body


5.30.4 (2023-09-15)
-------------------

- ZO-3771: Add series subtitle and description to audio object


5.30.3 (2023-09-14)
-------------------

- ZO-3770: added new properties to audio interface

- ZO-3771: Add distribution channels to audio object for spotify, google etc.


FIX:
- ZO-3814: layout fix for topiclinks and teaser landing zone


MAINT:
- MAINT: Refactor simplecast celery tasks and clean up imports


5.30.2 (2023-09-11)
-------------------

- ZO-215: Restore edit tab with landing zone for teaser modules


5.30.1 (2023-09-11)
-------------------

- ZO-3759: offer uuid for urbanairship payload


5.30.0 (2023-09-08)
-------------------

- ZO-3782: Transmit samplerate for downsampled modules


5.29.15 (2023-09-07)
--------------------

- ZO-215: Add a content landing zone to the edit tab of local-teaser


5.29.14 (2023-09-06)
--------------------

- ZO-3744: Move simplecast webhook duties to celery tasks


5.29.13 (2023-09-06)
--------------------

- ZO-3758: Remove fb library remnants


5.29.12 (2023-09-06)
--------------------

- ZO-3578: Simplecast audios are automatically saved in the correct folder

- ZO-3758: Allow configuring facebook graph api version


FIX:
- ZO-3438: correct id type for opentelemetry span to avoid errormessages in logs


5.29.11 (2023-08-31)
--------------------

- ZO-215: Switch teaser block UI to single referenced content instead of list

- ZO-3629: Log all errors (e.g. locking, not just publisher) on multi publish origin

- ZO-3708: add social push messages to article validation


FIX:
- Improve layout for error messages

  - now the box and the arrow below point directly at the widget
  - when more than one message appears, the message no longer shifts


5.29.10 (2023-08-29)
--------------------

- ZO-3662: Use correct dict entries


5.29.9 (2023-08-28)
-------------------

- ZO-3662: Add more logging


5.29.8 (2023-08-28)
-------------------

- ZO-3662: Update event names


5.29.7 (2023-08-25)
-------------------

- ZO-3718: Save podcast episodes in new folder


5.29.6 (2023-08-25)
-------------------

- ZO-3576: Ensure audio works

- ZO-3661: Connect to simplecast api

- ZO-3662: Create/update/delete Audio objects via webhook


5.29.5 (2023-08-11)
-------------------

FIX:
- ZO-3671: author ssoid is too big


5.29.4 (2023-08-08)
-------------------

- ZO-3578: Bump webhook log level to info


5.29.3 (2023-08-04)
-------------------

- ZO-2997: Redirect from repository to workingcopy if one exists for all content types


5.29.2 (2023-08-04)
-------------------

- ZO-3175: Move comment options into their own form group

- ZO-3576: Add Audioobjekt

- ZO-3578: Add Simplecast webhook(s)


5.29.1 (2023-08-02)
-------------------

- ZO-3188: Restrict publish/retract of folders to producing

- ZO-3449: Support searching for videos from e.g. Animation object

- ZON-2996: Hide delete menu item when prohibited, instead of requiring opening the popup first


5.29.0 (2023-07-28)
-------------------

MAINT:
- Switch to PEP420 namespace packages


5.28.2 (2023-07-24)
-------------------

- ZO-3550: Implement path prefix exclude for checkin webhook

- ZO-3568: Improve publish error handling


5.28.1 (2023-07-21)
-------------------

- ZO-1949: no need to post uuid and uniqueId generally and in service payload


5.28.0 (2023-07-20)
-------------------

- ZO-3262: Set target for RSS feed links (wiwo parquet)


MAINT:
- Move request timeout handling into zeit.cms instead of zeit.retresco


5.27.7 (2023-07-11)
-------------------

- ZO-3478: Reimplement as a single DAVProperty, so zeit.contentquery still works


5.27.6 (2023-07-10)
-------------------

- ZO-2613: Remove rotterdam skin


5.27.5 (2023-07-06)
-------------------

- ZO-3478: Introduce toggle `access_treat_free_as_dynamic`


5.27.4 (2023-07-03)
-------------------

- ZO-3172: Update Twitter API to v2


5.27.3 (2023-06-30)
-------------------

- ZO-2483: ignore 3rd party services list as parameter for publisher


5.27.2 (2023-06-30)
-------------------

- ZO-2683: Add checksum to Speechbert payload


5.27.1 (2023-06-23)
-------------------

- ZO-3452: No longer publish Video objects on checkin


5.27.0 (2023-06-22)
-------------------

- ZO-2808: display teaser preview for markup in centerpage
  ZO-2808: display markup preview in folder list view

- ZO-3415: Collect text of nested tags for speechbert payload

- ZO-3443: Update to sqlalchemy-2 API


5.26.13 (2023-06-20)
--------------------

MAINT:
- Log debug timing for new publisher


5.26.12 (2023-06-19)
--------------------

- ZO-3351: Update keywords during publish, to support "checkin+publish immediately" usecase


5.26.11 (2023-06-16)
--------------------

- ZO-3351: Revert asynchronous to synchronous tasks during checkout/publish


5.26.10 (2023-06-14)
--------------------

- ZO-3351: fix race condition for asynchronous index tasks on publish

- ZO-3394: Vivi devel should have its own logo


5.26.9 (2023-06-12)
-------------------

FIX:
- ZO-3351: Revert lock and unlock for every function that requires the lock


5.26.8 (2023-06-09)
-------------------

- ZO-3351: lock and unlock for every function that requires the lock


5.26.7 (2023-06-08)
-------------------

- ZO-3351: handle checkin before starting the publisher process


FIX:
- ZO-3351: Revert zeit.connector property update should invalidate cache


5.26.6 (2023-06-08)
-------------------

FIX:
- ZO-3351: zeit.connector property update should invalidate cache


5.26.5 (2023-06-07)
-------------------

- ZO-3364: Renames 'AnimatedHeader' modul to 'Animation'


5.26.4 (2023-06-06)
-------------------

- ZO-3351: revert sleep before publish, because it is not working


5.26.3 (2023-06-06)
-------------------

FIX:
- ZO-3351: Educated guess, wait for checkin completion before publish to avoid race condition


5.26.2 (2023-05-30)
-------------------

- ZO-1992: Control publish to tms in vivi


5.26.1 (2023-05-23)
-------------------

- ZO-2452: Add animation to article header module


5.26.0 (2023-05-22)
-------------------

MAINT:
- Separate forked dependency declarations per extra


5.25.1 (2023-05-17)
-------------------

- ZO-3159: Ignore news articles in speechbert


5.25.0 (2023-05-12)
-------------------

- ZO-3245: Use pure python mime detection library


5.24.1 (2023-05-12)
-------------------

- ZO-2808: Rename 'Markup Inhalt' to 'Markup' & and Markup to Typ Filter

- ZO-2874: Changed strategy to handle quotes in articles


5.24.0 (2023-05-02)
-------------------

MAINT:
- MAINT: Update to current opentelemetry sqlalchemy API


5.23.9 (2023-04-28)
-------------------

- ZO-3164: Record vivi_facebook_token_expires_timestamp_seconds metric


5.23.8 (2023-04-25)
-------------------

- ZO-2850: Add IArticle.comments_sorting


FIX:
- ZO-3028: import entity type for topicpages


5.23.7 (2023-04-19)
-------------------

- ZO-1642: Support available for series source


5.23.6 (2023-04-14)
-------------------

- ZO-2032: Provide ICommonMetadata attributes even if article ref is broken

- ZO-2555: view for csv download of images with single purchase

- ZO-2757: avoid failures if missing unimportant informations; different datetime


5.23.5 (2023-04-11)
-------------------

- ZO-2417: Enable Animation.genre attribute


MAINT:
- Add environment label to importer metrics


5.23.4 (2023-03-31)
-------------------

- ZO-2775: Record user and client ip for tracing

- ZO-2846: Fix cronjob config parsing

- ZO-2856: Remove slug from Speechbert image URL


5.23.3 (2023-03-15)
-------------------

- ZO-2655: CSV with invalid Authors (gcids) as browser view instead of mail


FIX:
- ZO-2757: FIX: uri paramamteter for tagesschau request includes www.zeit.de


5.23.2 (2023-03-06)
-------------------

- ZO-2463: Include all necessary otlp exporter dependencies


5.23.1 (2023-03-06)
-------------------

- ZO-2552: New content object markup for das wichtigste in kuerze

- ZO-2716: Export incoming http requests as traces


5.23.0 (2023-02-22)
-------------------

- ZO-2645: Add IAnimation.gallery field


5.22.19 (2023-02-21)
--------------------

- ZO-2132: Don't break on empty nodes


5.22.18 (2023-02-21)
--------------------

- ZO-2672: Log TMS reindex in objectlog


5.22.17 (2023-02-21)
--------------------

- ZO-2132: Normalize quotes to angled instead of inch if toggle `normalize_quotes` is set


5.22.16 (2023-02-20)
--------------------

FIX:
- ZO-2522: Fix speechbert namespace


5.22.15 (2023-02-17)
--------------------

- ZO-2522: Use checksome to validate speechbert audio against article text


5.22.14 (2023-02-14)
--------------------

- ZO-2233: Fix retract cronjob entrypoint principal


5.22.13 (2023-01-25)
--------------------

- ZO-2498: Add two new topiclink_[url|label] fields to centerpages


5.22.12 (2023-01-24)
--------------------

- ZO-2233: Fix cronjob entrypoint principal


5.22.11 (2023-01-24)
--------------------

- ZO-2233: Fix configuration parsing when there are no additional HTTP headers


5.22.10 (2023-01-13)
--------------------

- ZO-2233: Implement AdDefend JS-Code as vivi object


5.22.9 (2023-01-12)
-------------------

- ZO-2136: Don't display spurious "updated on" notifications on article forms after saving


5.22.8 (2023-01-11)
-------------------

- ZO-2136: Fix brown-bag release


5.22.7 (2023-01-11)
-------------------

- ZO-2136: Move UI-only exception to browser package


5.22.6 (2023-01-11)
-------------------

- ZO-2136: render error message for users for no tagesschau recommendations


5.22.5 (2023-01-05)
-------------------

- ZO-2388: Remove christmas tree and spirit


5.22.4 (2023-01-04)
-------------------

FIX:
- ZO-1847: Seriesheader preview should not cover Vivi UI


5.22.3 (2022-12-23)
-------------------

MAINT:
- Update python libraries


5.22.2 (2022-12-15)
-------------------

- ZO-2324: Switch container registry


5.22.1 (2022-12-15)
-------------------

- BEM-113: Make overriding toggles for tests work again

- ZO-2226: Display publish date in video selection


5.22.0 (2022-12-08)
-------------------

- BEM-113: Support categorizing feature-toggle.xml with intermediary tags


5.21.12 (2022-11-29)
--------------------

- ZO-2132: Roll back changes, they're causing data loss for some users, even though they use a toggle


5.21.11 (2022-11-24)
--------------------

- ZO-2215: Don't try to reposition the toolbar while the article editor is still initializing


FIX:
- ZO-2104: Mark unstable test as xfail


5.21.10 (2022-11-23)
--------------------

- ZO-1471: No longer copy teaserText to twitter push text (ZO-920)

- ZO-2042: usage of ard sync api


5.21.9 (2022-11-18)
-------------------

- ZO-2132: Normalize quotes to angled instead of inch if toggle `normalize_quotes` is set

- ZO-2179: Prohibit writing the root object to IConnector


5.21.8 (2022-11-16)
-------------------

FIX:
- FIX: Don't immediately break when we encounter a BMP image (even though officically we only support jpg+png)

- Ignore nonexistent GCS blobs during delete


5.21.7 (2022-10-28)
-------------------

FIX:
- rm imported but unused module


5.21.6 (2022-10-21)
-------------------

- ZO-1583: ARD Tagesschau video module


5.21.5 (2022-10-20)
-------------------

- ZO-1998: Support zonaudioapp-id in series.xml


5.21.4 (2022-10-18)
-------------------

- ZO-1428: Index dynamic folders in TMS, as publisher requires it


5.21.3 (2022-10-17)
-------------------

FIX:
- FIX: Be defensive about publisher url config trailing slash


5.21.2 (2022-10-17)
-------------------

- ZO-1420: Specific errors for new publisher


5.21.1 (2022-10-12)
-------------------

MAINT:
- Include currently used vivi version as data-attribute on HTML tag


5.21.0 (2022-10-07)
-------------------

- ZO-1422: Send all dependencies to new publisher

- ZO-1890: Add marker for switching to new comments 'rebrush' frontend

- ZO-1909: Use vivi API in publisher speechbert adapter


5.20.8 (2022-10-04)
-------------------

- ZO-1921: Instrument DAV requests for tracing


5.20.7 (2022-09-28)
-------------------

- ZO-1857: Implement retract with new publisher


MAINT:
- Allow https://www.staging.zeit.de URLs to be adapted to ICMSContent


5.20.6 (2022-09-20)
-------------------

FIX:
- Properly create a non-recording trace span


5.20.5 (2022-09-20)
-------------------

MAINT:
- Only record tracing data if the zeit.connector.postgresql logger is set to debug


5.20.4 (2022-09-15)
-------------------

- ZO-1864: Remove orphaned entries from property cache during invalidate


5.20.3 (2022-09-14)
-------------------

- ZO-1865: Send celery failures to bugsnag


MAINT:
- Update navi topics wording/translations


5.20.2 (2022-09-13)
-------------------

- ZO-1716: Add fields for three liveblogs (title and url) to Centerpage meta infos


MAINT:
- Speed up bw-compat code for image group without master images


5.20.1 (2022-09-13)
-------------------

MAINT:
- Update libraries


5.20.0 (2022-09-12)
-------------------

MAINT:
- Support configuring OTLP headers for tracing


5.19.9 (2022-09-06)
-------------------

FIX:
- Be defensive when no psql binary-types are configured


5.19.8 (2022-09-06)
-------------------

- ZO-1663: Add additional contact fields to author (one for title and one for it's content)


5.19.7 (2022-08-24)
-------------------

- ZO-1472: Also accept vivi.staging as uniqueId

- ZO-1747: Adjust article image variant on checkout if vertical has changed

- ZO-1748: Prevent spurious "None" values in inline forms


5.19.6 (2022-08-23)
-------------------

- ZO-605: Tweak UI wording


5.19.5 (2022-08-22)
-------------------

MAINT:
- MAINT: Update opentelemetry libraries


5.19.4 (2022-08-18)
-------------------

FIX:
- Only consider template objects for UA payload


5.19.3 (2022-08-17)
-------------------

FIX:
- Move contenttype icons into folders where they are included in releases


5.19.2 (2022-08-17)
-------------------

FIX:
- Include content template files in release


5.19.1 (2022-08-17)
-------------------

FIX:
- Apply testing zcml statements only in tests, not always


5.19.0 (2022-08-17)
-------------------

FIX:
- Always include translation in releases


5.18.6 (2022-08-17)
-------------------

- ZO-1408: Implement 3rdparty services for new publisher

MAINT:
- Update python from 3.10.5 to 3.10.6


5.18.5 (2022-08-09)
-------------------

- ZO-1663: Add jabber, pgp, signal and threema to author profiles


5.18.4 (2022-08-01)
-------------------

FIX:
- Be defensive about body=None in sql


5.18.3 (2022-07-28)
-------------------

- ZO-1629: Work around NonRecordingSpan opentelemetry bug


5.18.2 (2022-07-28)
-------------------

MAINT:
- Declare required elasticsearch libary version (belongs to 5.18.0)


5.18.1 (2022-07-28)
-------------------

- ZO-1629: Instrument sql connector for tracing

- ZO-605: Include `consider_for_duplicate` checkbox in area form


5.18.0 (2022-07-27)
-------------------

MAINT:
- Update to non-deprecated elasticsearch API


5.17.8 (2022-07-27)
-------------------

- ZO-1576: Implement hostname denylist for link targets

- ZO-605: Add `consider_for_dupes` flag to exclude area content from duplicate checking


5.17.7 (2022-07-25)
-------------------

- ZO-1298: Remove automatic area lead candidate mechanic

- ZO-1564: Adjust vgwort rights flags


MAINT:
- Publish breaking news banner directly together with its article


5.17.6 (2022-07-21)
-------------------

- ZO-1608: Reconnect to psql on error


5.17.5 (2022-07-21)
-------------------

- ZO-1603: Add "last indexed" field to TMS


5.17.4 (2022-07-18)
-------------------

MAINT:
- Update python libraries


5.17.3 (2022-07-14)
-------------------

- ZO-1564: Add various "rights granted" flags to vgwort report API call


5.17.2 (2022-07-13)
-------------------

- ZO-856: Use non-deprecated jinja API


5.17.1 (2022-07-13)
-------------------

- ZO-633: Optimize sql connector search for uuid


5.17.0 (2022-07-13)
-------------------

- ZO-856: Make compatible with Python-3.10


5.16.14 (2022-07-12)
--------------------

- ZO-1375: Handle queries without search string


5.16.13 (2022-07-12)
--------------------

- ZO-1375: search in configurable fields only to simplify result set


5.16.12 (2022-07-05)
--------------------

- ZO-1550: Remove `breaking_news` flag from facebook push data


5.16.11 (2022-06-29)
--------------------

- ZO-339: Actually allow users with EditEmbed permission to edit embeds


5.16.10 (2022-06-27)
--------------------

FIX:
- FIX: Differentiate missing and empty tag in newsletter.xml config file


5.16.9 (2022-06-24)
-------------------

- ZO-858: Update celery to 5.x


5.16.8 (2022-06-23)
-------------------

- ZO-1351: Publish content to new publisher, if toggle enabled. For development purposes

- ZO-1475: Remove obsolete `IArticle.is_amp` and `IEmbed.amp_code` fields

- ZO-1478: Update Pillow from version 6 to current 9


5.16.7 (2022-06-20)
-------------------

- ZO-1118: More airship error logging fixes


5.16.6 (2022-06-16)
-------------------

- ZO-1118: Fix airship error logging


5.16.5 (2022-06-15)
-------------------

- ZO-1211: Simplify CP metadata form


5.16.4 (2022-06-14)
-------------------

- ZO-1118: Send all push device types in a single request to airship, send to both US and EU instance


5.16.3 (2022-06-02)
-------------------

- ZO-1286: Add status message with total object count


5.16.2 (2022-06-02)
-------------------

- ZO-1261: Remove obsolete field ICommonMetadata.dailyNewsletter

- ZO-1286: Add objectlog entry after dynamic folder contents have been published


5.16.1 (2022-05-30)
-------------------

- ZO-1286: Use already existing `manual` queue for materialize

- ZO-1367: Store body of non-binary objects in SQL instead of GCS

- ZO-1395: No longer publish thumbnail images of imagegroups and galleries


5.16.0 (2022-05-25)
-------------------

- ZO-1261: Remove unused package zeit.newsletter

- ZO-1286: Use dedicated queue for publish as well


5.15.14 (2022-05-25)
--------------------

- ZO-1286: Use a dedicated celery queue for materialize and publish of dynamic folders


5.15.13 (2022-05-24)
--------------------

- ZO-1226: Restore edit link on regions (after 5.15.9)


5.15.12 (2022-05-23)
--------------------

- ZO-1286: Form batches properly

- ZO-1367: Remove unused field IText.encoding


5.15.11 (2022-05-23)
--------------------

- ZO-1094: Validate json against schema given schema url

- ZO-1161: Update advertising translations


5.15.10 (2022-05-18)
--------------------

- ZO-38: Display entity type for tags in repository as well


5.15.9 (2022-05-18)
-------------------

- ZO-1226: Make CP region+area foldable

- ZO-1330: Remove area_color_theme from code

- ZO-1339: Index TMS when workflow properties are edited while checked-in

- ZO-339: Require special permission to check out embed objects (when feature toggle `add_content_permissions` is active)

- ZO-38: Display entity type for tags

- ZO-648: Add checkbox on SEO form to set ISkipEnrich

- ZO-809: Genereate volume TOC for the volume object products, not a global config


5.15.8 (2022-05-17)
-------------------

FIX:
- FIX: Be liberal about `<image/>` in newsletter.xml config file


5.15.7 (2022-05-11)
-------------------

- ZO-1286: Materialize dynamic folder content in batches as well


5.15.6 (2022-05-10)
-------------------

- ZO-721: Ignore obsolete storystream metadata when indexing to TMS


5.15.5 (2022-05-09)
-------------------

- ZO-721: Remove any storystream code


5.15.4 (2022-05-09)
-------------------

- ZO-1286: Actually display the total entry count in the status log message


5.15.3 (2022-05-09)
-------------------

- ZO-114: UI tweaks for Animation object

- ZO-1286: Publish dynamicfolder content in batches


FIX:
- Constrain height of textareas generally again, after 5.15.2


5.15.2 (2022-05-04)
-------------------

FIX:
- Fix height of xml textarea (e.g. when editing feature-toggles)


5.15.1 (2022-05-03)
-------------------

- ZO-121: Add missing translation


5.15.0 (2022-05-02)
-------------------

- ZO-1255: Remove visible_mobile from vivi

- ZO-633: Implement search for postgresql connector


5.14.2 (2022-04-29)
-------------------

- ZO-1212: Improve label and restrict number of characters of area background color field


MAINT:
- Make `available` work for article template header and header color


5.14.1 (2022-04-28)
-------------------

- ZO-121: Make sort order in topicpagelist autoarea work


5.14.0 (2022-04-27)
-------------------

- ZO-1249: Support loading config files given as `http://xml.zeit.de` via connector


5.13.4 (2022-04-26)
-------------------

- ZO-1212: Background color for areas

- ZO-165: Publish dynamic folders without virtual content


5.13.3 (2022-04-14)
-------------------

- ZO-121: Support retrieving all available topicpages (for the register in zeit.web)

- ZO-920: Copy teaserText to twitter push text for genre=nachrichten


5.13.2 (2022-04-14)
-------------------

- ZO-121: Re-add `title` to ITopicpages results (mostly relevant for zeit.web)


5.13.1 (2022-04-13)
-------------------

- ZO-786: Fix GCS upload body size determination


5.13.0 (2022-04-13)
-------------------

- ZO-121: Implement automatic area query source "list of topicpages"


5.12.0 (2022-03-31)
-------------------

- ZO-1132: Add ILink.status_code (301 or 307)


5.11.9 (2022-03-28)
-------------------

- ZO-786: Pass body size to GCS upload, this reduces runtime by 2/3


5.11.8 (2022-03-28)
-------------------

- ZO-815: Properly delete all psql rows


5.11.7 (2022-03-28)
-------------------

FIX:
- Provide consistent Resource/CachedResource API


5.11.6 (2022-03-25)
-------------------

FIX:
- ZO-365: resize uploaded single images


5.11.5 (2022-03-24)
-------------------

- ZO-1113: Change log level


5.11.4 (2022-03-23)
-------------------

- ZO-1108: Support kicker in newslettersignup configuration, too

- ZO-786: Delete GCS blob


5.11.3 (2022-03-21)
-------------------

- ZO-929: Add `genre` and `authorships` to articles via Add-URL


MAINT:
- ZO-541: Remove old newsimport fallbacks


5.11.2 (2022-03-08)
-------------------

FIX:
- Revert merge of ZO-365 (https://github.com/ZeitOnline/vivi/pull/29)6 to unblock master branch


5.11.1 (2022-03-04)
-------------------

- ZO-815: Trigger container image build to fix psycopyg dependency


5.11.0 (2022-03-04)
-------------------

- - ZO-815, ZO-786: First implementation of new storage IConnector


FIX:
- ZO-365: resize uploaded single images


5.10.0 (2022-02-24)
-------------------

- ZO-365: Resize too large images on upload

- ZO-987: Add prefix field to newslettersignups


5.9.4 (2022-02-10)
------------------

MAINT:
- MAINT: Extract ImageGroup.from_image from zeit.brightcove


5.9.3 (2022-02-07)
------------------

- ZO-889: Grant zeit.MoveContent to zeit.CvD


5.9.2 (2022-02-03)
------------------

- ZO-538: Dummy changelog to force container rebuild with current zeit.newsimport release


5.9.1 (2022-02-02)
------------------

MAINT:
- Include the locked uniqueId in publish errormessage


5.9.0 (2022-01-20)
------------------

MAINT:
- Support logging.capture_warnings setting


5.8.1 (2022-01-18)
------------------

- ZO-764: Store local values uniformly in nodes, not attributes


MAINT:
- MAINT: Update to zope.publisher-6.0


5.8.0 (2022-01-14)
------------------

- ZO-764: Implement teaser module that supports local overrides


5.7.7 (2022-01-07)
------------------

- ZO-742: Do not remove XML schema type annotations


5.7.6 (2022-01-05)
------------------

- ZO-731: Add vertical code/ config for ZEIT am Wochenende


5.7.5 (2022-01-04)
------------------

- ZO-303: Download image from BC on update if vivi has no image reference

- ZO-614: Remove unused IVideo.thumbnail

- ZO-616: Delete video still image when video is deleted


5.7.4 (2022-01-04)
------------------

- ZO-727: Don't use a configuration file for image viewports anymore


5.7.3 (2022-01-03)
------------------

- ZO-727: Remove obsolete bw-compat support for "materialized variants"


5.7.2 (2022-01-03)
------------------

MAINT:
- Christmas is over


5.7.1 (2021-12-20)
------------------

MAINT:
- Add christmas logo


5.7.0 (2021-12-17)
------------------

- ZO-697: Use IImages API for video still, make available in TMS


5.6.1 (2021-12-17)
------------------

- ZO-680: Add z.c.article module ITickarooLiveblog.intersection


5.6.0 (2021-12-14)
------------------

- ZO-687: Allow zeit.web to cache content objects with their marker interface assignment included


5.5.3 (2021-12-08)
------------------

MAINT:
- Don't send None to opentelemetry, it doesn't like it


5.5.2 (2021-12-06)
------------------

- ZO-582: Use vivi API for volume toc, this correctly includes author names


5.5.1 (2021-12-01)
------------------

- ZO-143: Add mock connector setup for zeit.web tests


MAINT:
- Clean up XML namespaces and objectify `pytype` on checkin


5.5.0 (2021-11-30)
------------------

- ZO-143: Allow zeit.web to reuse zeit.cms.zope


5.4.11 (2021-11-26)
-------------------

- ZO-585: Report "no thirdparty" for already retracted references


5.4.10 (2021-11-22)
-------------------

- ZO-488: Include interred article-id in volume toc entries

- ZO-555: Add ICommonMetadata.color_scheme

- ZO-566: Add IVideo.type and import from BC custom field


5.4.9 (2021-11-18)
------------------

- ZO-146: Make paste.ini optional for CLI scripts

- ZO-146: Provide entrypoints for various cronjobs


5.4.8 (2021-11-15)
------------------

- ZO-145: Consider zcml.feature settings value (not just exists->true)


5.4.7 (2021-11-12)
------------------

- ZO-303: Use built-in mechanics for publishing image with video


5.4.6 (2021-11-11)
------------------

FIX:
- ZO-496: Prevent reach from cache poisoning vivi cp-editor


5.4.5 (2021-11-10)
------------------

FIX:
- Don't break when changing a template/header of article without an image


5.4.4 (2021-11-05)
------------------

FIX:
- ZO-352: Update libffi6->7


5.4.3 (2021-11-04)
------------------

MAINT:
- ZO-496: Add logging


5.4.2 (2021-11-02)
------------------

MAINT:
- ZO-188: Remove feature toggle


5.4.1 (2021-10-27)
------------------

- ZO-466: Include publisher script here, make configurable via env


5.4.0 (2021-10-26)
------------------

- ZO-441: Support configuring external utilities via settings instead of explicit ZCML includes

- ZO-442: Support setting system principal passwords via settings


5.3.2 (2021-10-21)
------------------

- OPS-1864: Make SSO functionality optional in normal workflows

- ZO-356: Set up logging for non-worker celery commands as well


5.3.1 (2021-10-21)
------------------

- FIX: Provide ZCML context under well-known API, where e.g. CP checkin expects it


5.3.0 (2021-10-19)
------------------

- ZO-356: Configure celery via environment


5.2.0 (2021-10-19)
------------------

- ZO-355: Support configuring product config and zodb via environment


5.1.0 (2021-10-19)
------------------

- ZO-354: Support configuring logging via environment


5.0.1 (2021-10-19)
------------------

- ZO-353: Fix fanstatic wsgi pipeline order


5.0.0 (2021-10-19)
------------------

- ZO-353: Make bugsnag setup reusable
  ZO-353: Support configuring wsgi pipeline stages via combined settings


4.65.1 (2021-10-15)
-------------------

- ZO-286: Materialize dialog and security updates for dynamic folders
  ZO-286: Remote metadata for articles

- ZO-346: Make year optional

- ZO-392: Validate teaser image fields before checkin as well


4.65.0 (2021-10-07)
-------------------

- ZO-142: Implement health check that respects a stopfile


4.64.1 (2021-09-29)
-------------------

- ZO-118: Add provider field to podcast module (on cp and articles)


4.64.0 (2021-09-28)
-------------------

- ZO-142: Support setting celery config file via paste.ini


4.63.6 (2021-09-27)
-------------------

- ZO-62: New entries for volume toc export


4.63.5 (2021-09-20)
-------------------

- ZO-156: Update previously materialized content


4.63.4 (2021-09-14)
-------------------

- ZO-188: Toogle webtrekk cp30 value format for wall status.
- ZO-163: Publish materialized content in dynamic folders


4.63.3 (2021-09-09)
-------------------

- ZO-156: Implement "materialize dynamic folder" UI action



4.63.2 (2021-09-02)
-------------------

- ZO-200: Do not modify rawxml body with DAV properties


4.63.1 (2021-09-02)
-------------------

- ZO-200: Support <rankedTags> in dynamicfolder templates

- ZO-142: Fix `zopeshell myscript.py` handling


4.63.0 (2021-09-02)
-------------------

- ZO-51: Implement "move object" UI action

- ZO-51: Implement "create linkobject" action

- ZO-169: Support `is_news` attribute in products.xml


4.62.0 (2021-08-31)
-------------------

- ZON-6764: Calculate uuid of dynamic folder content from uniqueId

- ZO-142: Provide `@zeit.cms.cli.runner` that wraps `@gocept.runner`
  and retrieves the config file from argv instead of buildout injection


4.61.3 (2021-08-20)
-------------------

- BUG-1430: gracefully handle locked images during brightcove import


4.61.2 (2021-08-20)
-------------------

- ZON-6316: Ensure that the audio_speechbert property occurs in XML


4.61.1 (2021-08-19)
-------------------

- TOPIC-15: Make TMS kpi field names configurable


4.61.0 (2021-08-19)
-------------------

- FIX: Make z.c.cp.BlockLayout default constructor conform to its interface


4.60.3 (2021-08-18)
-------------------

- TOPIC-15: Preserve externally populated `kpi` fields during TMS indexing


4.60.2 (2021-08-05)
-------------------

- TOPIC-42: Fix IndexError when trying to request related topicpages


4.60.1 (2021-08-02)
-------------------

- ZON-6301: Adds checkbox on CPs in SEO tab, to enable RSS-Feed single tracking
- FIX: Do not fail to rerurn related topics if we receive a nonexisting one


4.60.0 (2021-07-28)
-------------------

- TOPIC-39: Hide hide_dupes checkbox for reach as automatic area source
- TOPIC-39: Enable autopilot checkbox when automatic area source is changed
- BUG-1437: Skip tests with non expected TechnicalErrors
- TOPIC-19: Fix multiple sort order possibilities and be more defensive


4.59.4 (2021-07-22)
-------------------

- MAINT: Add base KPI Implementation to ensure adapting it never fails


4.59.3 (2021-07-21)
-------------------

- ZON-6371: Fix invalid host matching for @ containig urls.


4.59.2 (2021-07-20)
-------------------

- ZON-6371: Do not set links with internal hosts like vivi.zeit.de.


4.59.1 (2021-07-20)
-------------------

- ZON-6482: Enable speechbert by default for articles with no genre


4.59.0 (2021-07-19)
-------------------

- TOPIC-36: Add reach as automatic area source

- OPS-2077: Log failed celery tasks, so we can debug them
- TOPIC-19: Randomly sorted content for automatic areas

- FIX: Return correct result count for related topicpages


4.58.1 (2021-07-16)
-------------------

- OPS-2058: Move logout redirect to zeit.ldap
- TOPIC-36: Add Reach as automatic area source


4.58.0 (2021-07-13)
-------------------

- TOPIC-31: Move zeit.web.core.reach to zeit.reach


4.57.7 (2021-07-13)
-------------------

- MAINT: Display principal id if no principal was found


4.57.6 (2021-07-13)
-------------------

- FIX: Use correct form name for autoreload with genre


4.57.5 (2021-07-12)
-------------------

- TOPIC-11: Sort automatic areas by date_last_published


4.57.4 (2021-07-09)
-------------------

- ZON-6316: Speechbert Checkbox: Moving to options and rename label

- OPS-2024: Handles invalid variant size

- TOPIC-16: Add ITMS methods get_content_containing_topicpages and get_content_related_topicpages

- TOPIC-9: Implement TMS order in a way that does not break the related API

- MAINT: Move zeit.retresco.tag to zeit.cms.tagging.tag


4.57.3 (2021-07-05)
-------------------

- BUG-1415: Be more defensive during BC video import

- TOPIC-9: Store topicpage_order abstracted from the concrete TMS fieldnames


4.57.2 (2021-06-30)
-------------------

- FIX: Hide Topicpage sort option when anything else is selected


4.57.1 (2021-06-30)
-------------------

- ZON-6710: Changes topicbox default automatic_type value



4.57.0 (2021-06-29)
-------------------

- ZON-5970: Remove clickcounter integration

- OPS-1985: Use opentelemetry for tracing


4.56.0 (2021-06-28)
-------------------

- TOPIC-9: Provide access to TMS kpi data with `IKPI` adapter


4.55.0 (2021-06-23)
-------------------

- TOPIC-9: Add possibility to sort TMS entries
- TOPIC-9: Add related topics as automatic source

- ZON-6655: Improve wording


4.54.2 (2021-06-21)
-------------------

- OPS-2001: Restrict "change type" to producing+cvd


4.54.1 (2021-06-16)
-------------------

- BEM-54: Be defensive about analyzing the BC response


4.54.0 (2021-06-16)
-------------------

- OPS-1984: Conform to real `Span` API in FakeTracer


4.53.3 (2021-06-07)
-------------------

- BEM-54: Improve Error-Logging for not playable videos


4.53.2 (2021-06-03)
-------------------

- MAINT: Use own converter for RecipeArticles
- OPS-1852: Markdown modules must not be empty

- ZON-6539: remove option for editors to include articles in daily newsletter


4.53.1 (2021-05-31)
-------------------

- STO-185: Handle indeterminable mtime gracefully


4.53.0 (2021-05-27)
-------------------

- ZON-6655: Fix related API, support multiple topicboxes per article

- OPS-1892: Add sample_rate parameter to honeycomb tracer


4.52.2 (2021-05-18)
-------------------

- BUG-1392: Avoid PIL resize with 0 values

- OPS-1359: Conform to field naming scheme for tracing


4.52.1 (2021-04-29)
-------------------

- MAINT: Add feature toggle 'show_automatic_type_in_topicbox'


4.52.0 (2021-04-27)
-------------------

- ZON-5576: Add automatic sources to article topicbox modules


4.51.1 (2021-04-26)
-------------------

- MAINT: Exclude JSON objects from SEO filename rules


4.51.0 (2021-04-23)
-------------------

- ZON-6637: Introduce JSON content object

- ZON-6377: Fix rendering of teaser images with `fill_color=None` parameters


4.50.6 (2021-04-21)
-------------------

- ZON-6614: Support caching time attribute on centerpages


4.50.5 (2021-04-08)
-------------------

- STO-185: Cache content & DAV properties based on file modification times


4.50.4 (2021-04-07)
-------------------

- ZON-6573: Support legal_text attribute on newslettersignups


4.50.3 (2021-03-30)
-------------------

- OPS-1684: Avoid zero division on image ratio calculations

- FIX: Ignore XML comments when parsing article modules


4.50.2 (2021-03-22)
-------------------

- ZON-6478: Follow up, refactor existing_teasers attribute for CP ContentQueries


4.50.1 (2021-03-17)
-------------------

- ZON-6521: Support theme in liveblogs


4.50.0 (2021-03-16)
-------------------

- ZON-6478: Move content query functionality to its own module

- BUG-1250: Hide no more needed 'external' author checkbox


4.49.2 (2021-03-10)
-------------------

- BUG-1366: Make sorting volume listings work again for py3


4.49.1 (2021-03-10)
-------------------

- ZON-6346: Make tickaroo liveblog status required

- BUG-1311: Show "steal lock" button only if user has the required permission

- BUG-1366: Make sorting listings work again for py3


4.49.0 (2021-02-24)
-------------------

- MAINT: Add status code to retresco TechnicalError


4.48.8 (2021-02-10)
-------------------

- ZON-6383: Handle Markdown using python libraries

- ZON-6346: Add article module for tickaroo liveblog


4.48.7 (2021-02-01)
-------------------

- ZON-6275: Urbanairship open channel support


4.48.6 (2021-01-29)
-------------------

- ZETT-98: Provide social channels facebook and twitter for zett


4.48.5 (2021-01-25)
-------------------

- STO-179: Handle changed "total hits" ES search API response


4.48.4 (2021-01-21)
-------------------

- STO-179: Remove overspecific `type` restriction from ES queries


4.48.3 (2021-01-21)
-------------------

- STO-59: Keep internal API of TMS connection stable for zeit.web


4.48.2 (2021-01-19)
-------------------

- STO-59: Upgrade elastic client library to 7.x (it's bw-compat to 2.x)


4.48.1 (2021-01-12)
-------------------

- STO-172: Don't send obsolete DAV properties to TMS


4.48.0 (2021-01-11)
-------------------

- STO-59: Allow Vivi to talk to two TMS instances


4.47.1 (2021-01-06)
-------------------

- BUG-1324: Handle image/author/volume modules correctly during checkin


4.47.0 (2021-01-06)
-------------------

- BUG-1315: Fix Update-Token-Tool for Facebook

- OPS-1516: Make image encoder parameters configurable


4.46.1 (2020-12-18)
-------------------

- BUG-1342: Fix accessing dotted property names in TMSContent


4.46.0 (2020-12-18)
-------------------

- BUG-1342: Apply provided interfaces to TMSContent


4.45.6 (2020-12-18)
-------------------

- ZON-6306: Fix text/bytes handling in MDB interface


4.45.5 (2020-12-16)
-------------------

- ZON-6319: Fix behavior for select the 'no genre' option

- BEM-70: mock is included in the stdlib in py3


4.45.4 (2020-12-16)
-------------------

- OPS-1490: Allow volume to be set to 54 (everywhere)


4.45.3 (2020-12-16)
-------------------

- OPS-1490: Allow volume to be set to 54


4.45.2 (2020-12-10)
-------------------

- OPS-1480: Log pickle on unpickling errors


4.45.1 (2020-12-10)
-------------------

- OPS-1480: Log error when unpickling lxml


4.45.0 (2020-12-04)
-------------------

- ZETT-90: Add vivi logo for ze.tt

- ZON-6162: Update to jinja-2.11


4.44.5 (2020-12-01)
-------------------

- ZON-6214: Sends article to the ContentHub, even if it was "only published"

- STO-57: Add type declarations for countings and foldable


4.44.4 (2020-11-25)
-------------------

- ZON-6213: Fix zeit.cms newsimport test setup.


4.44.3 (2020-11-25)
-------------------

- MAINT: Update product-config in test setup.


4.44.2 (2020-11-19)
-------------------

- STO-82: Make MemoryFile pickleable


4.44.1 (2020-11-18)
-------------------

- PERF: Cache immutable values while calculating image variants


4.44.0 (2020-11-13)
-------------------

- MAINT: Move tracing implementation from zeit.web here so we can
  instrument vivi code paths as well


4.43.3 (2020-11-05)
-------------------

- ZON-6140: Support additional attributes from newslettersignup config


4.43.2 (2020-10-22)
-------------------

- ZON-6149: Pass url during image traversal


4.43.1 (2020-10-22)
-------------------

- ZON-5577: Set default for `force_mobile_images` to true


4.43.0 (2020-10-13)
-------------------

- ZETT-46: Add color theme selection to area settings

- BEM-62: Remove obsolete `IArticle.is_instant_article`

- ZON-6149: Allow to specify imagegroup variants via query parameters


4.42.0 (2020-10-08)
-------------------

- STO-82: Make MemoryFile usable as a context manager


4.41.1 (2020-10-06)
-------------------

- BUG-1291: Set up timebased retract for videos according to the BC
  expires field (take two, after 4.40.3)


4.41.0 (2020-10-01)
-------------------

- PERF: Make mime type detection optional in filesystem connector.
  We actually only need this for the vivi tests, but not in zeit.web,
  and it causes significant overhead.


4.40.3 (2020-09-30)
-------------------

- BUG-1302: Don't overzealously remove invalid field values

- Revert BUG-1291 for now, newly added videos cannot set up timebased
  retract currently


4.40.2 (2020-09-30)
-------------------

- BUG-1291: Set up timebased retract for videos according to the BC
  expires field


4.40.1 (2020-09-30)
-------------------

- BUG-1307: Don't notify HDok during retract


4.40.0 (2020-09-28)
-------------------

- ZON-6068: Implement IArticle.header_color


4.39.5 (2020-09-22)
-------------------

- WOMA-181: Add notification for empty recipe title

- WOMA-204: Add aggregations to retresco.ElasticSearch query api


4.39.4 (2020-09-21)
-------------------

- WOMA-240: Add diet to wochenmarkt ingredients.


4.39.3 (2020-09-10)
-------------------

- MAINT: Update zeit.connector to current zope.generations API


4.39.2 (2020-09-03)
-------------------

- BUG-1283: Size of images in image gallery editor is max 500 px x 500 px

- ZON-6108: Remove legacy ``type`` attribute from content editor line breaks


4.39.1 (2020-08-06)
-------------------

- BUG-1273: Handle toplevel `br` nodes that can appear when pasting content


4.39.0 (2020-08-05)
-------------------

- WOMA-143: Add "special ingredient" to recipelist module


4.38.4 (2020-08-03)
-------------------

- ZON-5981: Restrict retract/delete for authors to producing

- FIX: Catch vgwort connection errors, raising a TechnicalError


4.38.3 (2020-07-31)
-------------------

- BUG-1205: Prevent creating several <br> when pressing enter in content-editable


4.38.2 (2020-07-29)
-------------------

- WOMA-133: Fetch ingredient units from configuration file

- ZON-6041: Add campaign parameters to twitter/facebook push URLs

- ZON-6006: Add article main image url to volume toc.csv


4.38.1 (2020-07-28)
-------------------

- BUG-1255: Prevent adding the same author to an article twice


4.38.0 (2020-07-28)
-------------------

- ZON-6037: Introduce zeit.zett.interfaces.IZTTContent

- ZON-5959: Implement querying HDok for blacklisted entries


4.37.2 (2020-07-28)
-------------------

- MAINT: Make date_print_published writeable via admin tab


4.37.1 (2020-07-24)
-------------------

- FIX: Import necessary packages for pembeds


4.37.0 (2020-07-24)
-------------------

- WOMA-111: Provide plural property from ingredients whitelist

- MAINT: Support variables in pembed parameter definitions


4.36.7 (2020-07-23)
-------------------

- WOMA-141: Update portion range validation for servings


4.36.6 (2020-07-20)
-------------------

- WOMA-136_2: Update list of ingredient units

- WOMA-137: Allow duplicate ingredients in recipe list module


4.36.5 (2020-07-14)
-------------------

- FIX: Handle zope.interface now inheriting getTaggedValues(),
  which broke IBreakingNews type/token in the AddableCMSContentTypeSource


4.36.4 (2020-07-13)
-------------------

- MAINT: Make forward-compatible with zope.interface-5.0


4.36.3 (2020-07-10)
-------------------

- WOMA-96: Don't change access for non performing articles in channel 'wochenmarkt'

- FIX: Remove optional chaining for better browser support

- WOMA-136: Update list of ingredient units


4.36.2 (2020-07-08)
-------------------

- WOMA-126: Remove duplicates in recipe from ES payload.

- WOMA-130: Use ids for ingredient units


4.36.1 (2020-07-07)
-------------------

- FIX: Make `available` work for article modules


4.36.0 (2020-07-03)
-------------------

- ZON-5643: Quote users comments in article


4.35.3 (2020-07-02)
-------------------

- WOMA-116: Validate servings to allow a portion range


4.35.2 (2020-07-02)
-------------------

- WOMA-4: Add defaults for ingredient amount and unit.

- WOMA-115: Add free text details to ingredients in recipelist

- WOMA-120: Add new values to ingredient unit list


4.35.1 (2020-06-30)
-------------------

- MAINT: Ensure we don't use browser-specific directives in
  non-browser ZCML files

- WOMA-99: Polish recipelist module


4.35.0 (2020-06-25)
-------------------

- WOMA-114: Read ingredient and category names from whitelist
  instead of article xml

- WOMA-108: Add ingredientdice article module


4.34.3 (2020-06-24)
-------------------

- MAINT: Derive WOMA whitelists from z.c.c.sources.CachedXMLBase


4.34.2 (2020-06-23)
-------------------

- STO-49: Use default filename mechanics for z.c.cp.TopicpageFilterSource as well


4.34.1 (2020-06-22)
-------------------

- BUG-1247: Fix toc listing content type filter

- MAINT: Move browser imports from zeit.wochenmarkt to zeit.wochenmarkt.browser


4.34.0 (2020-06-18)
-------------------

- STO-49: Support setting a default filename for source config files


4.33.5 (2020-06-18)
-------------------

- MAINT: Remove unused imports


4.33.4 (2020-06-17)
-------------------

- WOMA-66: Add recipe categories to articles

- WOMA-103: Add checkbox to instruct merging multiple recipe list modules

- WOMA-104: Add subheading to recipe list

- WOMA-85: Extract recipe attributes and write it to destination fields in
  ElasticSearch

- STO-49: Support setting a default filename for source config files


4.33.3 (2020-06-09)
-------------------

- OPS-1214: No longer update zeit.cms.relation "who references whom" index


4.33.2 (2020-06-04)
-------------------

- MAINT: Sort teaser formgroup below options in article editor


4.33.1 (2020-06-04)
-------------------

- ZON-5861: Remove `commentsAPIv2` property from `ICommonMetadata`

- BUG-1216: Allow referencing gallery objects in article topicbox module


4.33.0 (2020-05-29)
-------------------

- WOMA-65: Introduce module: recipe list
- MAINT: Log hdok create calls


4.32.11 (2020-05-27)
--------------------

- MAINT: Sort access above authors in article form


4.32.10 (2020-05-25)
--------------------

- PY3: Make workflow timing logging work under py3


4.32.9 (2020-05-25)
-------------------

- FIX: Just filter frame-less renditions completely


4.32.8 (2020-05-25)
-------------------

- PY3: Be defensive about brightcove renditions without frame size


4.32.7 (2020-05-19)
-------------------

- PY3: Fix text/bytes handling in DAV property parsing


4.32.6 (2020-05-18)
-------------------

- ZON-5886: Make FluentRecordFormatter py3-compatible


4.32.5 (2020-05-11)
-------------------

- ZON-5758: Display hdok result list even if there's only one match,
  since the new name could be a single-hit-substring of an existing name


4.32.4 (2020-05-11)
-------------------

- IR-51: Translate filter values

- MAINT: Update to changed hdok create API yet again


4.32.3 (2020-05-11)
-------------------

- ZON-5869: Add manual link to article embed form


4.32.2 (2020-05-08)
-------------------

- BUG-1238: Fix volume zplus webtrekk query


4.32.1 (2020-05-06)
-------------------

- ZON-5758: Make IAuthor.status optional


4.32.0 (2020-05-05)
-------------------

- ZON-4945: Provide TMSContentQuery._fetch() extension point for zeit.web


4.31.3 (2020-05-05)
-------------------

- MAINT: Don't break when running test in zeit.web, when pytest option
  `--visible` will be added by both vivi.core and zeit.web


4.31.2 (2020-05-05)
-------------------

- WOMA-68: Set IAuthor.is_author use_default=True


4.31.1 (2020-05-04)
-------------------

- IR-51: Volume table of contents


4.31.0 (2020-04-29)
-------------------

- IR-73: Look up author in HDok before creating it in vivi


4.30.3 (2020-04-28)
-------------------

- ZON-5869: Update social embed wording


4.30.2 (2020-04-28)
-------------------

- BUG-1234: Ignore `DeleteProperty` in tms reindex


4.30.1 (2020-04-27)
-------------------

- BUG-1234: Handle security properly in "re-report to vgwort" view


4.30.0 (2020-04-23)
-------------------

- ZON-5728: Upgrade to selenium-3.x with geckodriver


4.29.2 (2020-04-03)
-------------------

- MAINT: Update wording of IConsentInfo.thirdparty_vendors (via @holger)


4.29.1 (2020-04-02)
-------------------

- OPS-1192: Replace stdlib cookie parser with webob,
  so it doesn't break on non-ASCII characters


4.29.0 (2020-03-27)
-------------------

- ZON-5447: Generalize vendor source API to access all config attributes


4.28.0 (2020-03-23)
-------------------

- ZON-5488: Provide IConsentInfo also for z.c.article.IRawXML


4.27.0 (2020-03-16)
-------------------

- MAINT: Use JWT for our "SSO" cookie


4.26.5 (2020-03-12)
-------------------

- WOMA-33: Add cook ability  to authors.


4.26.4 (2020-03-11)
-------------------

- ZON-5635: Handle updates from Brightcove for teaser images


4.26.3 (2020-03-09)
-------------------

- ZON-5635: Put importing video images behind feature toggle
  ``video_import_images``


4.26.2 (2020-03-09)
-------------------

- BUG-1207: Don't try to write DAV cache in webhook notify job

- PY3: Fix text/bytes handling in zeit.connector.filesystem


4.26.1 (2020-03-04)
-------------------

- BUG-1205: Revert bugfix 4.25.15, it causes a different misbehaviour

- ZON-5635: Add teaser images for videos as CMS content


4.26.0 (2020-02-18)
-------------------

- OPS-786: Extract fluent logging helper so zeit.web can reuse it


4.25.15 (2020-02-14)
--------------------

- ZON-5651 etc: Make zeit.edit, zeit.vgwort py3 compatible

- BUG-1205: Remove obsolete browser workaround that inserted
  an additional br element in article editor.


4.25.14 (2020-02-07)
--------------------

- ZON-5679 etc: Make packages py3 compatible:
  z.c.article, cp, dynamicfolder, gallery, image, modules,
  zeit.retresco, wysiwyg

- FIX: Remove influxdb remnants (4.25.10)


4.25.13 (2020-02-03)
--------------------

- HOTFIX: Explicitly specify UTF8 as our encoding


4.25.12 (2020-02-03)
--------------------

- ZON-5659: Use bytes for resource body in z.c.text
  so it conforms to the zeit.connector behaviour


4.25.11 (2020-01-31)
--------------------

- FIX: Turns out zope.app.folder is not a ui-only dependency


4.25.10 (2020-01-31)
--------------------

- ZON-5653: Make zeit.connector, zeit.imp, zeit.content.volume py3 compatible

- OPS-908: Remove notifying influxdb for pushes, has been replaced
  by grafana


4.25.9 (2020-01-30)
-------------------

- BUG-1206: Restrict product-related vgwort author fallback to
  articles without agencies

- ZON-5649 etc: Make packages py3 compatible:
  zeit.cms, zeit.workflow, zeit.find, z.c.author, text, link

- FIX: Index in ES after marking an article as vgwort-todo


4.25.8 (2020-01-20)
-------------------

- BUG-1199: Patch bug in zeep SOAP client so it serializes agency
  authors (only code, no firstname/lastname) correctly

- FIX: Add missing import, log end of vgwort report job

- FIX: Don't double-b64encode vgwort text


4.25.7 (2020-01-07)
-------------------

- FIX: Make xmldiff work with objectify for further cases


4.25.6 (2020-01-07)
-------------------

- ZON-5693: Try different MDB fields for copyright


4.25.5 (2020-01-07)
-------------------

- FIX: Add missing import

- MAINT: Remove obsolete IArticle.layout property


4.25.4 (2020-01-06)
-------------------

- ZON-5645: Make source-code (hopefully) py3 compatible

- ZON-5771: Make RTE toolbar compatible for Google Chrome

- FIX: Make xmldiff work with objectify



4.25.3 (2019-12-18)
-------------------

- OPS-1163: Remove connector lockinfo cache


4.25.2 (2019-12-17)
-------------------

- MAINT: Display different vivi logo on loginform too


4.25.1 (2019-12-17)
-------------------

- MAINT: Display different vivi logo in staging


4.25.0 (2019-12-16)
-------------------

- ZON-5560: Implement `Animation` content type

- ZON-5590: Remove z3c.conditionalviews

- ZON-5748: Replace xml_compare with xmldiff

- MAINT: Update wording of IConsentInfo.thirdparty_vendors (via @milan)


4.24.1 (2019-12-10)
-------------------

- HOTFIX: Don't require special permission to add embed when toggle is off


4.24.0 (2019-12-09)
-------------------

- ZON-5694: Implement NewsletterSignup Module


4.23.2 (2019-12-09)
-------------------

- FIX: Declare dependency that friedbert-preview needs


4.23.1 (2019-12-09)
-------------------

- ZON-5594: Honor separated UI dependencies by not needlessly importing UI code


4.23.0 (2019-12-06)
-------------------

- ZON-5586: Finally remove unused XMLSnippet field (since zeit.cms-2.35.1)

- ZON-5585: Replace SilverCity with Pygments for syntax highlighting

- ZON-5603: Replace suds with zeep as our SOAP client library

- ZON-5615: Require special permission to add embed objects,
  set feature toggle `add_content_permissions` to enable

- ZON-5615: Removed inline code entry from rawtext module

- ZON-5593, ZON-5594: Declare test-only and UI dependencies separately


4.22.3 (2019-11-26)
-------------------

- BUG-1136: Don't show admin checked-out for objects without ICommonMetadata,
  implement a basic SEO tab for them.


4.22.2 (2019-11-22)
-------------------

- BUG-1156: Only count teasers, not all modules when adjusting auto block count
  (reprise of 4.17.4)


4.22.1 (2019-11-22)
-------------------

- FIX: Restore translations that were lost in 4.22.0

- MAINT: Also pre-warm folder entries


4.22.0 (2019-11-21)
-------------------

- ZON-5614: Make social embed labels and texts more explainable

- ZON-5472: Add `IAuthor.show_letterbox_link` field


4.21.7 (2019-11-15)
-------------------

- MAINT: Apply enrich toggle also on publish


4.21.6 (2019-11-15)
-------------------

- MAINT: Add feature toggle `tms_enrich_on_checkin` so we can disable
  it in overload situations


4.21.5 (2019-11-15)
-------------------

- OPS-1133: Modify DAV cache conflict resolution rules
  to avoid deleting cache entries (doing that was definitely correct,
  but it caused thundering herd issues e.g. for often-used folders)
  Set feature toggle `dav_cache_delete_property_on_conflict` (or `childname`)
  to revert to the previous behaviour.


4.21.4 (2019-11-13)
-------------------

- HOTFIX: brown-bag 4.21.3 due to syntax error


4.21.3 (2019-11-13)
-------------------

- OPS-1133: Don't write traceback into the property cache anymore


4.21.2 (2019-11-13)
-------------------

- OPS-1133: Write the traceback into the property cache


4.21.1 (2019-11-12)
-------------------

- ZON-5473: Set force_mobile_image=True for gallery teasers

- OPS-1133: More diagnostics for DAV cache deletes


4.21.0 (2019-11-11)
-------------------

- OPS-1133: Implement a DAV cache (properties and childnames) with
  dogpile/redis as the storage backend


4.20.5 (2019-11-08)
-------------------

- OPS-1133: Allow setting a connector referrer for non-http requests


4.20.4 (2019-11-06)
-------------------

- OPS-1133: More diagnostics for DAV cache deletes


4.20.3 (2019-11-05)
-------------------

- OPS-1133: Add diagnostics to DAV cache deletes


4.20.2 (2019-10-29)
-------------------

- MAINT: Put article image `animation` behind feature toggle `article_image_animation`


4.20.1 (2019-10-25)
-------------------

- FIX: Set dlps to dlp instead of yet another separate "now"


4.20.0 (2019-10-23)
-------------------

- ZON-5447: Translate vendor IDs to external CMP values


4.19.0 (2019-10-22)
-------------------

- ZON-5523: Add additional amp_code field to embeds


4.18.0 (2019-10-22)
-------------------

- ZON-5464: Add `animation` field to article image module

- OPS-1133: Add diagnostics to DAV cache conflict resolution


4.17.5 (2019-10-02)
-------------------

- BUG-1156: Roll back change for now, it breaks autopilots


4.17.4 (2019-10-02)
-------------------

- BUG-1156: Only count teasers, not all modules when adjusting auto block count


4.17.3 (2019-10-02)
-------------------

- BUG-1155: Display topiclink fields below each other in area edit form


4.17.2 (2019-10-02)
-------------------

- ZON-5432: Provide agencies in ITMSContent


4.17.1 (2019-09-26)
-------------------

- ZON-5480: Store mime type in a location that's actually writeable


4.17.0 (2019-09-26)
-------------------

- ZON-5480: Make mime type editable for text objects


4.16.1 (2019-09-25)
-------------------

- MAINT: Make article module library configurable just like CP


4.16.0 (2019-09-24)
-------------------

- ZON-5490: Add module to embed thirdparty content by pasting an URL

- OPS-1116: Add an explicit commit to separate the two retresco files


4.15.7 (2019-09-19)
-------------------

- ZC-450: Remove diagnostics, we found out what we needed


4.15.6 (2019-09-19)
-------------------

- ZC-450: More diagnostics


4.15.5 (2019-09-19)
-------------------

- ZC-450: Add diagnostics to the requests timeout signal handler setup


4.15.4 (2019-09-17)
-------------------

- FIX: Make admin form work for articles again after 4.8.4


4.15.3 (2019-09-16)
-------------------

- FIX: Require CMP vendors to be unique


4.15.2 (2019-09-16)
-------------------

- ZON-5453: Use dropdown instead of checkbox widget for CMP vendors

- FIX: Put display of CMP fields behind feature toggle as well


4.15.1 (2019-09-12)
-------------------

- HOTFIX: Fix error in author object-details view
  (wrong source base class)


4.15.0 (2019-09-11)
-------------------

- ZON-5488: Implement IConsentInfo for the rawtext module

- ZON-5483: Allow configuring which authorship roles to report to vgwort

- FIX: Don't break when creating a volume without a `centerpage` setting

- MAINT: Don't show supertitle in volume toc


4.14.0 (2019-09-05)
-------------------

- ZON-5453: Add dropdown with `IConsentInfo.has_thirdparty` to embed form

- ZON-5447: Add multiselect with `IConsentInfo.thirdparty_vendors` to embed form


4.13.0 (2019-09-04)
-------------------

- FIX: Display label "Author" when role is None

- MAINT: Move runtime feature toggle source here from zeit.web

- MAINT: Put `agencies` field on article UI behind feature toggle


4.12.2 (2019-09-04)
-------------------

- ZON-5394: Do not report authorships with role to vgwort


4.12.1 (2019-09-03)
-------------------

- OPS-1106: Switch vgwort report to query elasticsearch instead of queryserver


4.12.0 (2019-08-29)
-------------------

- ZON-5432: Add value `Agentur` to `IAuthor.status` source;
  add `ICommonMetadata.agencies` field;
  add `IAuthor.initials` field


4.11.1 (2019-08-27)
-------------------

- ZON-5394: Styling to put role field on the same line as location


4.11.0 (2019-08-27)
-------------------

- ZON-5394: Add IAuthorReference.role field


4.10.0 (2019-08-26)
-------------------

- ZON-5376: Add `IArticle.prevent_ligatus_indexing` property


4.9.4 (2019-08-09)
------------------

- BUG-1101: Fix CSS for "to top" link


4.9.3 (2019-08-09)
------------------

- BUG-1094: Retrieve the number of actually available hits if a TMS/ES
  query hits the configured ES result limit.


4.9.2 (2019-08-09)
------------------

- ZON-5338: Explicitly set defaults declared in IVideo during BC-import

- ZON-5380: Add "access" filter to search form

- ZON-5378: Display the embed name instead of its raw code in CP editor

- ZON-5321: Make article ITopicbox.supertitle required

- ZON-5241: Update to changed zope.viewlet sorting behaviour


4.9.1 (2019-08-08)
------------------

- HOTFIX: Fix paragraph handling after beautifulsoup udpate


4.9.0 (2019-08-05)
------------------

- IR-163: Add preview link to volume toc

- IR-68: Support importing image group images (and minimal metadata)
  via drag&drop from the IR MDB UI

- MAINT: Revert __name__ handling from 4.8.3, Producing members often
  massage the source code to fix formatting issues, and these
  attributes get in the way of that


4.8.4 (2019-07-30)
------------------

- HOTFIX: Fix typo in admin "checked-in" form

- HOTFIX: Not all ressorts in TOC now come from k4 anymore


4.8.3 (2019-07-29)
------------------

- MAINT: Keep __name__ attributes in article


4.8.2 (2019-07-29)
------------------

- FIX: Exclude temporary articles from checkin webhooks


4.8.1 (2019-07-29)
------------------

- IR-95: Add hdok id to ICommonMetadata.authorships XML reference

- IR-41: Add `has_audio` field to the checked-out admin form


4.8.0 (2019-07-25)
------------------

- IR-71: Add IAuthor.honorar_id

- MAINT: Increase favicon resolution


4.7.0 (2019-07-17)
------------------

- IR-54: Also allow IR article_id, not just uuid to query the lock status


4.6.3 (2019-07-11)
------------------

- ZC-90: Move field to activate new comments backend to article form


4.6.2 (2019-07-10)
------------------

- BUG-1074: Index TMS on rename


4.6.1 (2019-07-10)
------------------

- BUG-1069: Don't index imagegroup or gallery thumbnail images in TMS

- FIX: Don't try to nonexistent content in TMS re-enrich hook

- IR-142: Also collect articles imported from InterRed for volume table of contents


4.6.0 (2019-07-10)
------------------

- ZON-5239: Topicbox improvments

- ZON-5291: Rename content marketing teaser adplace

- ZON-5347: Set 'is_amp' default to true

- BUG-1121: Enable RSS-Teaser objects as lead candidate


4.5.5 (2019-07-08)
------------------

- FIX: Fix volume title listing breaking with non ascii char


4.5.4 (2019-07-05)
------------------

- BUG-1096: Allow storing `False` for embed parameters with default=True


4.5.3 (2019-07-04)
------------------

- IR-67: Display different error for still published objects when lock is set


4.5.2 (2019-07-04)
------------------

- FIX: Use correcter syntax for tags in push to influxdb


4.5.1 (2019-07-04)
------------------

- MAINT: Exclude connector test content from released egg


4.5.0 (2019-07-04)
------------------

- IR-66: Retry webhook on errors

- IR-67: Add `locked` flag to workflow info that prevents publishing


4.4.1 (2019-07-03)
------------------

- FIX: Use correct syntax for tags in push to influxdb

- MAINT: Send info about UA pushes to both grafana and influxdb,
  so we can hopefully shut down the influxdb soon


4.4.0 (2019-06-20)
------------------

- MAINT: Add linkSource (mostly for pembeds)


4.3.0 (2019-06-12)
------------------

- ZON-4585: Add topiclink fields to areas


4.2.0 (2019-06-06)
------------------

- ZON-5260: Add background color to cardstacks

- MAINT: Clean up whitespace from rss feeds


4.1.0 (2019-06-03)
------------------

- IR-77: Add `mdb_id` field to images

- IR-77: Add `setup_timebased_jobs` xmlrpc method

- PERF: Determine image mime type only on demand, not always upfront on resolve


4.0.5 (2019-05-22)
------------------

- FIX: Exclude rss teaser from referenced cp content


4.0.4 (2019-05-20)
------------------

- IR-36: Notify checkin webhooks also for newly created objects

- FIX: Declare brightcove console script properly


4.0.3 (2019-05-16)
------------------

- IR-59: Allow configuring excludes for checkin webhook


4.0.2 (2019-05-08)
------------------

- FIX: Fix xml.zeit.de being able to render rss feed objects


4.0.1 (2019-05-02)
------------------

- FIX: Fix RSS Content query breaking hide dupes clause


4.0.0 (2019-04-29)
------------------

- Initial monorepo release.
