from pathlib import Path
from copy import deepcopy
import json, re, zipfile
from lxml import etree as E

ROOT = Path('/Users/zhaojinlan/Desktop/Lann Projects/What-the-fingers-hear')
BUILD = ROOT / '.codex-build/peer-review'
SOURCE = Path('/Users/zhaojinlan/Documents/GitHub/MTEC-498-Capstone/Homework/PeerReview/presentation.pptx')
DATA = json.loads((BUILD / 'content.json').read_text())
NS = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'rel':'http://schemas.openxmlformats.org/package/2006/relationships',
      'ct':'http://schemas.openxmlformats.org/package/2006/content-types'}
def q(n):
    prefix, local = n.split(':')
    return '{'+NS[prefix]+'}'+local
def xml(b): return E.fromstring(b)
def dump(n): return E.tostring(n,xml_declaration=True,encoding='UTF-8',standalone=True)
with zipfile.ZipFile(SOURCE) as z: package={n:z.read(n) for n in z.namelist()}
with zipfile.ZipFile(BUILD/'new-slides.pptx') as z: added={n:z.read(n) for n in z.namelist()}

def visible(body):
    return '\n'.join(t for p in body.findall('a:p',NS) if (t:=''.join(p.xpath('.//a:t/text()',namespaces=NS))))
def replace_body(body,value):
    oldp=body.find('a:p',NS)
    props=deepcopy(oldp.find('a:pPr',NS)) if oldp is not None and oldp.find('a:pPr',NS) is not None else None
    rp=oldp.find('.//a:rPr',NS) if oldp is not None else None
    end=oldp.find('a:endParaRPr',NS) if oldp is not None else None
    for p in list(body.findall('a:p',NS)): body.remove(p)
    for line in value.split('\n'):
        p=E.SubElement(body,q('a:p'))
        if props is not None:p.append(deepcopy(props))
        r=E.SubElement(p,q('a:r'))
        if rp is not None:r.append(deepcopy(rp))
        E.SubElement(r,q('a:t')).text=line
        if end is not None:p.append(deepcopy(end))

changes=[]
for slide_num,replacements in DATA['replacements'].items():
    path=f'ppt/slides/slide{slide_num}.xml';root=xml(package[path]);seen=set()
    for body in root.xpath('//p:txBody|//a:txBody',namespaces=NS):
        old=visible(body)
        if old in replacements:
            replace_body(body,replacements[old]);seen.add(old)
    assert seen==set(replacements),f'Unmatched replacements on {slide_num}: {set(replacements)-seen}'
    package[path]=dump(root);changes.append(int(slide_num))

new_ids={'irb':14,'return':15,'silence':16,'compare':17,'later':18}
for i,(key,number) in enumerate(new_ids.items(),1):
    package[f'ppt/slides/slide{number}.xml']=added[f'ppt/slides/slide{i}.xml']
    # New pages use the original deck's existing blank layout and notes master.
    rel=E.Element(q('rel:Relationships'),nsmap={None:NS['rel']})
    E.SubElement(rel,q('rel:Relationship'),Id='rIdLayout',Type=NS['r']+'/slideLayout',Target='../slideLayouts/slideLayout6.xml')
    E.SubElement(rel,q('rel:Relationship'),Id='rIdNotes',Type=NS['r']+'/notesSlide',Target=f'../notesSlides/notesSlide{number}.xml')
    package[f'ppt/slides/_rels/slide{number}.xml.rels']=dump(rel)

def add_note_paragraph(body,line,bold=False):
    p=E.SubElement(body,q('a:p'))
    if not line:
        E.SubElement(p,q('a:endParaRPr'));return
    for i,chunk in enumerate(re.split(r'\*\*(.*?)\*\*',line)):
        if not chunk:continue
        r=E.SubElement(p,q('a:r'))
        rp=E.SubElement(r,q('a:rPr'),lang='en-US',sz='1200')
        if bold or i%2:rp.set('b','1')
        E.SubElement(rp,q('a:latin'),typeface='Helvetica Neue')
        t=E.SubElement(r,q('a:t'));t.text=chunk
        if chunk.startswith(' ') or chunk.endswith(' '):t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')

source_for_note={1:1,2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9,11:11,10:10,12:12,13:13}
source_notes=deepcopy(package)
script=['# What the Fingers Hear — Speaker Script','', 'Key points to emphasize appear in **bold**.','']
for position,(key,note) in enumerate(zip(DATA['order'],DATA['notes']),1):
    number=new_ids.get(key,key)
    path=f'ppt/slides/slide{number}.xml';root=xml(package[path])
    for body in root.xpath('//p:txBody',namespaces=NS):
        # The page marker is identified by the original upper-right location.
        shape=body.getparent();off=shape.find('p:spPr/a:xfrm/a:off',NS)
        if off is not None and int(off.get('x','0'))>=11000000 and int(off.get('y','9999999'))<700000:
            replace_body(body,f'{position:02d}')
    package[path]=dump(root)
    template_number=source_for_note.get(key,13)
    note_root=xml(source_notes[f'ppt/notesSlides/notesSlide{template_number}.xml'])
    body=note_root.xpath('//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]/p:txBody',namespaces=NS)[0]
    oldtext=visible(body)
    sources=note.get('sources') or oldtext.split('SOURCES\n')[-1].splitlines()
    for child in list(body.findall('a:p',NS)):body.remove(child)
    add_note_paragraph(body,'SPEAKER SCRIPT',True);add_note_paragraph(body,'')
    for line in note['script'].split('\n'):add_note_paragraph(body,line)
    add_note_paragraph(body,'');add_note_paragraph(body,'SOURCES',True)
    for line in sources:
        if line:add_note_paragraph(body,line)
    package[f'ppt/notesSlides/notesSlide{number}.xml']=dump(note_root)
    rel=E.Element(q('rel:Relationships'),nsmap={None:NS['rel']})
    E.SubElement(rel,q('rel:Relationship'),Id='rId1',Type=NS['r']+'/notesMaster',Target='../notesMasters/notesMaster1.xml')
    E.SubElement(rel,q('rel:Relationship'),Id='rId2',Type=NS['r']+'/slide',Target=f'../slides/slide{number}.xml')
    package[f'ppt/notesSlides/_rels/notesSlide{number}.xml.rels']=dump(rel)
    script += [f'## {position:02d}. {note["title"]}','',note['script'],'']
    if key=='later':
        script += ['Practice reference: [Amber Sound Touch, “Memorising music”](https://soundtouch.ambertrust.org/services/instrumental-and-vocal-tuition/strategies/memorising-music/).','']

# Preserve the embedded video and make its legacy video relationship internal.
rel_path='ppt/slides/_rels/slide8.xml.rels';root=xml(package[rel_path])
for rel in root:
    if rel.get('Type')==NS['r']+'/video':
        rel.set('Target','../media/current-prototype.mp4');rel.attrib.pop('TargetMode',None)
package[rel_path]=dump(root)
slide8=xml(package['ppt/slides/slide8.xml'])
for link in slide8.xpath('//a:hlinkClick[@action="ppaction://media"]',namespaces=NS):
    if link.get(q('r:id'))=='':link.attrib.pop(q('r:id'))
package['ppt/slides/slide8.xml']=dump(slide8)

presentation=xml(package['ppt/presentation.xml'])
rel_root=xml(package['ppt/_rels/presentation.xml.rels'])
slide_list=presentation.find('p:sldIdLst',NS)
old_slides=list(slide_list)
existing={i:deepcopy(old_slides[i-1]) for i in range(1,14)}
for key,num in new_ids.items():
    rid=f'rIdAddedSlide{num}'
    E.SubElement(rel_root,q('rel:Relationship'),Id=rid,Type=NS['r']+'/slide',Target=f'slides/slide{num}.xml')
    s=E.Element(q('p:sldId'),id=str(1000+num));s.set(q('r:id'),rid);existing[key]=s
for child in list(slide_list):slide_list.remove(child)
for key in DATA['order']:slide_list.append(existing[key])
package['ppt/presentation.xml']=dump(presentation)
package['ppt/_rels/presentation.xml.rels']=dump(rel_root)

ct=xml(package['[Content_Types].xml'])
for num in new_ids.values():
    for part,kind in [('slides/slide','slide'),('notesSlides/notesSlide','notesSlide')]:
        E.SubElement(ct,q('ct:Override'),PartName=f'/ppt/{part}{num}.xml',ContentType=f'application/vnd.openxmlformats-officedocument.presentationml.{kind}+xml')
package['[Content_Types].xml']=dump(ct)
if 'docProps/app.xml' in package:
    root=xml(package['docProps/app.xml']);ns={'e':'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'}
    element=root.find('e:Slides',ns)
    if element is not None:element.text=str(len(DATA['order']))
    package['docProps/app.xml']=dump(root)

candidate=BUILD/'candidate.pptx'
with zipfile.ZipFile(candidate,'w',zipfile.ZIP_DEFLATED) as z:
    for name,content in package.items():z.writestr(name,content)
(ROOT/'outputs/peer-review/speaker_script.md').write_text('\n'.join(script))
(BUILD/'assembly-audit.json').write_text(json.dumps({'slideCount':len(DATA['order']),'changedOriginalSlides':changes,'newSlides':new_ids,'speakerScriptWords':sum(len(re.sub(r'\*\*','',n['script']).split()) for n in DATA['notes']),'embeddedVideoPreserved':True},indent=2))
print((BUILD/'assembly-audit.json').read_text())
