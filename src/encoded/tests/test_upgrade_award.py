import pytest


def test_award_upgrade_1_2(upgrader, award_base):
	award_base['focus'] = 'skin'
	value = upgrader.upgrade('award', award_base, current_version='1', target_version='2')
	assert value['focus'] == 'adipose, skin, breast'
	assert value['schema_version'] == '2'
