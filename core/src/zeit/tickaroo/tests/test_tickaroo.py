import pytest

from zeit.tickaroo.tickaroo import get_teaser_title


@pytest.mark.parametrize(
    'html, title',
    [
        ('<div><strong>Strong title</strong><br><br>and another text!</div>', 'Strong title'),
        ('<h2>H2 title</h2><div>another <strong>strong</strong> text!</div>', 'H2 title'),
        (
            '<h2><strong>Strong within h2 at the beginning</strong> with some text after</h2>',
            'Strong within h2 at the beginning with some text after',
        ),
        (
            '<h2>Strong <strong>in the middle with some <i>italics</i> and</strong> some text after'
            '</h2>',
            'Strong in the middle with some italics and some text after',
        ),
        (
            '<div>In case there is no strong or h2 tag at the beginning we choose this text to be'
            'the teaser title.',
            'In case there is no strong or h2 tag at the …',
        ),
        (
            '<h1>Litauens, Lettlands und Estlands Stromnetz nicht mehr mit Russland verbunden'
            '</h1><div>Die drei baltischen Staaten haben ihre<strong>⎵Stromnetzverbindungen zu '
            'Russland getrennt</strong>. Estland, Lettland und Litauen wollen sich morgen mit dem '
            'EU-Netz synchronisieren.⎵</div><div><br><em>Lesen Sie hier alle Details:</em></div>',
            'Litauens, Lettlands und Estlands Stromnetz nicht mehr mit Russland verbunden',
        ),
    ],
)
def test_block_liveblog_highlighted_events_title(html, title):
    assert get_teaser_title(html, 50) == title
