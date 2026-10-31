"""Optional, bounded Unity UI asset GUID/address relation review; not a runtime verdict."""
import re
from pathlib import Path

def _read(root, rel):
    p = root
    for part in Path(rel).parts:
        p /= part
        if p.is_symlink():
            return None
    if not p.is_file() or p.stat().st_size > 250_000:
        return None
    try:
        return p.read_text(encoding='utf-8')
    except (OSError, UnicodeError):
        return None

def review(root, config):
    assets = {key: config[key]['asset'] for key in ('common','main')}
    texts = {k:_read(root,v) for k,v in assets.items()}
    metas = {k:_read(root,v+'.meta') for k,v in assets.items()}
    groups = {key:_read(root, config[key]['group']) for key in assets}
    statuses=[]
    guids={}
    for key in assets:
        match=re.search(r'^guid: ([a-f0-9]{32})$',metas[key] or '',re.M)
        guids[key]=match.group(1) if match else None
        address = config[key]['address']
        entries=re.findall(r'^  - m_GUID: ([a-f0-9]{32})\n    m_Address: ([^\n]+)',groups[key] or '',re.M)
        hits=[guid for guid,addr in entries if addr==address]
        # Never report success when the same GUID is assigned to conflicting addresses.
        guid_addresses=[addr for guid,addr in entries if guid==guids[key]]
        duplicate_guid=len(guid_addresses)>1
        status=('source_unavailable' if not texts[key] or not metas[key] or not groups[key]
                else 'guid_unavailable' if not guids[key]
                else 'address_ambiguous' if len(hits)>1
                else 'guid_ambiguous' if duplicate_guid
                else 'address_missing' if not hits
                else 'guid_mismatch' if hits[0]!=guids[key] else 'reference_link_found')
        statuses.append({'check_id':key+'-ui-asset-address','status':status,
                         'source':assets[key],'address':address,
                         'asset_guid':guids[key], 'group_guids':hits,
                         'blocking':False})
    if guids['common'] and guids['main'] and guids['common']==guids['main']:
        for result in statuses:
            result['status']='asset_guid_conflict'
    common_ref=re.search(r'^  common: \{fileID: 11400000, guid: ([a-f0-9]{32}), type: 2\}$',
                         texts['main'] or '', re.M)
    target=common_ref.group(1) if common_ref else None
    statuses.append({'check_id':'main-common-reference',
                     'status':('source_unavailable' if not texts['main'] or not metas['common']
                               else 'reference_missing' if not target
                               else 'guid_mismatch' if target!=guids['common']
                               else 'reference_link_found'),
                     'source':assets['main'], 'referenced_guid':target, 'expected_guid':guids['common'],
                     'blocking':False})
    if guids['common'] and guids['main'] and guids['common']==guids['main']:
        statuses[-1]['status']='asset_guid_conflict'
    return statuses

def validate(config):
    if not isinstance(config, dict) or set(config) != {'common', 'main'}:
        raise ValueError('invalid art_ui_unity_binding')
    for item in config.values():
        if not isinstance(item, dict) or set(item) != {'asset', 'group', 'address'}:
            raise ValueError('invalid binding fields')
        for field in ('asset', 'group'):
            value = item[field]
            if (not isinstance(value, str) or not value or len(value) > 240
                or Path(value).is_absolute() or '..' in Path(value).parts):
                raise ValueError('invalid binding path')
        if not isinstance(item['address'], str) or not item['address'] or len(item['address']) > 240:
            raise ValueError('invalid binding address')
    return config
