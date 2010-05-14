VGWort 
======

Tokens
++++++


>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> import zeit.vgwort.interfaces
>>> import zope.component
>>> tokens = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)


Load tokens
-----------

>>> import StringIO
>>> csv = StringIO.StringIO("""\
... Öffentlicher Identifikationscode;Privater Identifikationscode
... c0063bcfb7234b35b145af20dccf5e2a;8018af9154bd4b60b0ee4a6891b85583
... 4c47ec781b5b4a288b9a1ab8b2c5ab3c;82e7bb658f75444a9bf74273641f2c29
... 3b787da5b75846e2b39bd814b55a9512;c32e3e163d874e7d8da0d21f96bfeb47
... """)
>>> tokens.load(csv)
>>> len(tokens)
3


Get tokens
----------

Getting tokens is randomized to mostly avoid conflicts.

Seed the random generator with a fixed value to get predictable results:

>>> import random
>>> random.seed(0)
>>> tokens.claim()
('3b787da5b75846e2b39bd814b55a9512', 'c32e3e163d874e7d8da0d21f96bfeb47')
>>> len(tokens)
2
>>> tokens.claim()
('4c47ec781b5b4a288b9a1ab8b2c5ab3c', '82e7bb658f75444a9bf74273641f2c29')
>>> len(tokens)
1
>>> tokens.claim()
('c0063bcfb7234b35b145af20dccf5e2a', '8018af9154bd4b60b0ee4a6891b85583')
>>> len(tokens)
0
>>> tokens.claim()
Traceback (most recent call last):
ValueError: No tokens available.

Restore random-nes: 

>>> random.seed()
