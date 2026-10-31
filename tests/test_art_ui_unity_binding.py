import tempfile
import unittest
from pathlib import Path
from frameforge.art_ui_unity_binding import review, validate

G1='a'*32
G2='b'*32
def fixture(root):
    base=root/'Assets/Settings/UI'
    groups=root/'Assets/AddressableAssetsData/AssetGroups'
    base.mkdir(parents=True);groups.mkdir(parents=True)
    config={}
    for key,guid,address in [('common',G1,'UI/Common/Assets'),('main',G2,'UI/Main/Assets')]:
        name='Common' if key=='common' else 'Main'
        asset=base/(name+'UIAssets.asset')
        asset.write_text('  common: {fileID: 11400000, guid: '+G1+', type: 2}\n' if key=='main' else 'ok\n')
        (base/(asset.name+'.meta')).write_text('guid: '+guid+'\n')
        group=groups/(name+'.asset')
        group.write_text('  - m_GUID: '+guid+'\n    m_Address: '+address+'\n')
        config[key]={'asset':asset.relative_to(root).as_posix(),
                     'group':group.relative_to(root).as_posix(),'address':address}
    return config

class ReviewTests(unittest.TestCase):
    def test_matched_and_broken_link(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);c=fixture(p)
            self.assertEqual([x['status'] for x in review(p,validate(c))],['reference_link_found']*3)
            g=p/c['main']['group'];g.write_text(g.read_text().replace(G2,G1))
            self.assertEqual(review(p,c)[1]['status'],'guid_mismatch')
    def test_missing_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);c=fixture(p)
            (p/c['common']['group']).unlink()
            self.assertEqual(review(p,c)[0]['status'],'source_unavailable')
            with tempfile.TemporaryDirectory() as o:
                (p/c['common']['group']).symlink_to(Path(o)/'outside')
                self.assertEqual(review(p,c)[0]['status'],'source_unavailable')
    def test_invalid_config(self):
        with self.assertRaises(ValueError):
            validate({'common':{'asset':'../escape','group':'x','address':'y'},'main':{'asset':'x','group':'y','address':'z'}})

    def test_duplicate_address_and_guid_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);c=fixture(p)
            group=p/c['common']['group']
            group.write_text(group.read_text()+'  - m_GUID: '+G2+'\n    m_Address: UI/Common/Assets\n')
            self.assertEqual(review(p,c)[0]['status'],'address_ambiguous')
            group.write_text('  - m_GUID: '+G1+'\n    m_Address: UI/Common/Assets\n'
                             +'  - m_GUID: '+G1+'\n    m_Address: UI/Common/Other\n')
            self.assertEqual(review(p,c)[0]['status'],'guid_ambiguous')

    def test_same_guid_for_two_assets_is_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);c=fixture(p)
            meta=p/(c['main']['asset']+'.meta')
            meta.write_text('guid: '+G1+'\n')
            statuses=review(p,c)
            self.assertTrue(all(x['status']=='asset_guid_conflict' for x in statuses))
