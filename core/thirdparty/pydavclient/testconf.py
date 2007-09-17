import dav

## URL_1='http://nova:5081/test/upload/data/'
## URL_2='http://cosmos.infrae.com/repo/'
## URL_3='http://nova.infrae/rrr/'
URL_4='http://nova.infrae:83/test/'

conn_1 = dav.DAVConnection('nova', 83)
conn_1.set_auth('gst', 'gst')

conn_2 = dav.DAVConnection('cosmos.infrae.com')
conn_2.set_auth('gst','naggle')

CONN = conn_1
URL = URL_4
