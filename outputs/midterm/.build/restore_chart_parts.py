import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

source, candidate = map(Path, sys.argv[1:])
with zipfile.ZipFile(source) as z:
    original = {n: z.read(n) for n in z.namelist()}
with zipfile.ZipFile(candidate) as z:
    edited = {n: z.read(n) for n in z.namelist()}
parts = {n: b for n, b in original.items()
         if n.startswith('ppt/slides/charts/') or n.startswith('ppt/embeddings/')}
assert 'ppt/slides/charts/chart1.xml' in parts
assert 'ppt/embeddings/chart-data-snapshot-001.xlsx' in parts
edited.update(parts)
ns = 'http://schemas.openxmlformats.org/package/2006/content-types'
ET.register_namespace('', ns)
ct = ET.fromstring(edited['[Content_Types].xml'])
keys = {(el.tag, el.get('Extension'), el.get('PartName')) for el in ct}
for el in ET.fromstring(original['[Content_Types].xml']):
    key = (el.tag, el.get('Extension'), el.get('PartName'))
    if key not in keys and (el.get('Extension') == 'xlsx' or el.get('PartName', '').lstrip('/') in parts):
        ct.append(el)
        keys.add(key)
edited['[Content_Types].xml'] = ET.tostring(ct, encoding='utf-8', xml_declaration=True)
staged = candidate.with_name('restored-chart.pptx')
with zipfile.ZipFile(staged, 'w', zipfile.ZIP_DEFLATED) as z:
    for n, data in edited.items():
        z.writestr(n, data)
staged.replace(candidate)
print('Preserved the original editable chart and its original embedded workbook.')
