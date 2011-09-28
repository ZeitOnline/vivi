================================
Integrating Brightcove with vivi
================================

Videos and playlists are stored in the Brightcove system. While metadata gets
copied to, modified in and updated in Brightcove by vivi,the Brightcove
system's copy of the data is considered the master at any time.

Therefore, there are two independent ways of modifying video data and
metadata: through the Brightcove web interface, and through vivi. This makes
it necessary for vivi to keep its own copy up-to-date with the Brightcove
data. A cron job is responsible for this.

The cron job is careful not to overwrite vivi's copy of a piece of data if it
is newer than the data stored by Brightcove. This may happen shortly after
vivi wrote to Brightcove as there is some delay until Brightcove gives back
the new data.
