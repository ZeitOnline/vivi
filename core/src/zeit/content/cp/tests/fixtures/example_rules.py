# flake8: noqa
applicable(is_area and area == 'teaser-mosaic' and position == 2)
error_unless(layout == 'dmr', 'Die zweite Teaserleiste muss ein DMR sein')

applicable(is_area and area == 'lead')
warning_unless(count > 6, 'In der Aufmacherfläche sollen mehr als 6 Teaserblöcke stehen')
error_unless(count > 2, 'In der Aufmacherfläche müssen mehr als 2 Teaserblöcke stehen')
