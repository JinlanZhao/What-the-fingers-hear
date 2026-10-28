from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E

base = Path(__file__).parent
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PR = 'http://schemas.openxmlformats.org/package/2006/relationships'
P14 = 'http://schemas.microsoft.com/office/powerpoint/2010/main'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
ns = {'p':P,'a':A,'r':R}

with ZipFile(base / 'draft.pptx') as z:
    parts = {n:z.read(n) for n in z.namelist()}
root = E.fromstring(parts['ppt/slides/slide8.xml'])
pic = root.find('.//p:pic', ns)
props = pic.find('p:nvPicPr/p:cNvPr', ns)
props.set('name', 'Current prototype demonstration')
props.set('descr', 'Recorded developer demonstration. Click to play the embedded video.')
props.insert(0, E.Element(f'{{{A}}}hlinkClick', {'action':'ppaction://media'}))
nv = pic.find('p:nvPicPr/p:nvPr', ns)
E.SubElement(nv, f'{{{A}}}videoFile', {f'{{{R}}}link':'rIdDemoVideo'})
ext = E.SubElement(E.SubElement(nv,f'{{{P}}}extLst'),f'{{{P}}}ext',uri='{DAA4B4D4-D01A-418F-89A0-4504762567E2}')
E.SubElement(ext,f'{{{P14}}}media',{f'{{{R}}}embed':'rIdDemoMedia'},nsmap={'p14':P14})

timing = E.Element(f'{{{P}}}timing')
slide_extensions = root.find(f'{{{P}}}extLst')
if slide_extensions is None:
    root.append(timing)
else:
    root.insert(root.index(slide_extensions), timing)
tn = E.SubElement(E.SubElement(E.SubElement(timing,f'{{{P}}}tnLst'),f'{{{P}}}par'),f'{{{P}}}cTn',id='1',dur='indefinite',restart='never',nodeType='tmRoot')
video = E.SubElement(E.SubElement(tn,f'{{{P}}}childTnLst'),f'{{{P}}}video')
media = E.SubElement(video,f'{{{P}}}cMediaNode',vol='100000')
ctn = E.SubElement(media,f'{{{P}}}cTn',id='2',fill='hold',display='0')
E.SubElement(E.SubElement(ctn,f'{{{P}}}stCondLst'),f'{{{P}}}cond',delay='indefinite')
E.SubElement(E.SubElement(media,f'{{{P}}}tgtEl'),f'{{{P}}}spTgt',spid=props.get('id'))

rel_name = 'ppt/slides/_rels/slide8.xml.rels'
rels = E.fromstring(parts[rel_name])
E.SubElement(rels,f'{{{PR}}}Relationship',Id='rIdDemoVideo',Type=R+'/video',Target='../media/current-prototype.mp4')
E.SubElement(rels,f'{{{PR}}}Relationship',Id='rIdDemoMedia',Type='http://schemas.microsoft.com/office/2007/relationships/media',Target='../media/current-prototype.mp4')
ct = E.fromstring(parts['[Content_Types].xml'])
E.SubElement(ct,f'{{{CT}}}Default',Extension='mp4',ContentType='video/mp4')
for key, xml in [('ppt/slides/slide8.xml',root),(rel_name,rels),('[Content_Types].xml',ct)]:
    parts[key]=E.tostring(xml,xml_declaration=True,encoding='UTF-8',standalone=True)
parts['ppt/media/current-prototype.mp4']=(base/'demo.mp4').read_bytes()
with ZipFile(base/'candidate.pptx','w',ZIP_DEFLATED) as z:
    for n,b in parts.items():z.writestr(n,b)
print('Embedded video in candidate.pptx')
