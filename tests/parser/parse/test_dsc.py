# Synthetic offline fixtures only: ABC123 and DSCDEMO are not allocated.
from datetime import datetime, timezone
import pytest
from ogn.parser import parse

BASE = "OGNABC123>OGNDSC,qAR,DSCDEMO:/123456h4530.00N/00915.00E'360/021/A=000394 !W00! id37ABC123 +197fpm"

@pytest.mark.parametrize('code,source,reconstructed', [('O','device_fix',False),('G','android_gnss_clock',True),('N','android_network_clock',True),('R','other_reconstruction',True)])
def test_dsc_timestamp_provenance(code, source, reconstructed):
    value=parse(BASE+' dscT'+code, datetime(2026,10,26,12,34,56,tzinfo=timezone.utc), use_server_timestamp=False)
    assert value['beacon_type']=='dsc'
    assert value['dsc_time_source']==source
    assert value['dsc_time_reconstructed'] is reconstructed
    assert value['address']=='ABC123'
    assert value['timestamp'].isoformat()=='2026-10-26T12:34:56+00:00'
    assert value['receiver_name']=='DSCDEMO'

@pytest.mark.parametrize('suffix',['',' dscTX',' dscTG dscTN',' xdscTG',' dscTGjunk',' dscTG dscTX',' dscTG dscTG',' dscT',' dscTG dscT'])
def test_absent_invalid_or_ambiguous_quality_not_invented(suffix):
    assert 'dsc_time_source' not in parse(BASE+suffix)

def test_dsc_field_does_not_change_other_feeders():
    value=parse(BASE.replace('OGNDSC','OGNTRK')+' dscTG')
    assert value['beacon_type']=='tracker'
    assert 'dsc_time_source' not in value

@pytest.mark.parametrize('path',['qOR','qAR,DSCDEMO','qAS,DSCDEMO'])
def test_optional_altitude_and_motion(path):
    value=parse("OGNABC123>OGNDSC,"+path+":/123456h4530.00N/00915.00E' !W00! id37ABC123 dscTG")
    assert value['beacon_type']=='dsc'
    assert 'altitude' not in value
    assert 'ground_speed' not in value
