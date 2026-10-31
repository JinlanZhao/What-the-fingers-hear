from pathlib import Path
from copy import deepcopy
import json,re,zipfile
from lxml import etree as E

ROOT=Path('/Users/zhaojinlan/Desktop/Lann Projects/What-the-fingers-hear')
BUILD=ROOT/'.codex-build/peer-review'
SPEC=json.loads((BUILD/'compact.json').read_text())
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','rel':'http://schemas.openxmlformats.org/package/2006/relationships','ct':'http://schemas.openxmlformats.org/package/2006/content-types'}
def q(name):
    a,b=name.split(':');return '{'+NS[a]+'}'+b
def dump(node):return E.tostring(node,encoding='UTF-8',xml_declaration=True,standalone=True)
def parse(b):return E.fromstring(b)
def text(body):return '\n'.join(t for p in body.findall('a:p',NS) if (t:=''.join(p.xpath('.//a:t/text()',namespaces=NS))))
def replace(body,value):
    oldp=body.find('a:p',NS)
    pp=oldp.find('a:pPr',NS) if oldp is not None else None
    rp=oldp.find('.//a:rPr',NS) if oldp is not None else None
    ep=oldp.find('a:endParaRPr',NS) if oldp is not None else None
    for p in list(body.findall('a:p',NS)):body.remove(p)
    for line in value.split('\n'):
        p=E.SubElement(body,q('a:p'))
        if pp is not None:p.append(deepcopy(pp))
        r=E.SubElement(p,q('a:r'))
        if rp is not None:r.append(deepcopy(rp))
        E.SubElement(r,q('a:t')).text=line
        if ep is not None:p.append(deepcopy(ep))
def note_paragraph(body,line,bold=False):
    p=E.SubElement(body,q('a:p'))
    for i,chunk in enumerate(re.split(r'\*\*(.*?)\*\*',line)):
        if not chunk:continue
        r=E.SubElement(p,q('a:r'));rp=E.SubElement(r,q('a:rPr'),sz='1200',lang='en-US')
        if bold or i%2:rp.set('b','1')
        E.SubElement(rp,q('a:latin'),typeface='Helvetica Neue')
        t=E.SubElement(r,q('a:t'));t.text=chunk
        if chunk.startswith(' ') or chunk.endswith(' '):t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')

with zipfile.ZipFile(ROOT/'outputs/peer-review/presentation_revised.pptx') as z:pkg={n:z.read(n) for n in z.namelist()}
original=deepcopy(pkg)
deck=parse(pkg['ppt/presentation.xml']);rels=parse(pkg['ppt/_rels/presentation.xml.rels'])
relmap={r.get('Id'):r for r in rels}
slide_list=deck.find('p:sldIdLst',NS);oldslides=list(slide_list)
paths={i:'ppt/'+relmap[s.get(q('r:id'))].get('Target') for i,s in enumerate(oldslides,1)}
keep={s['old'] for s in SPEC['slides']}
with zipfile.ZipFile(BUILD/'voice-patch.pptx') as z:
    patches=[parse(z.read(f'ppt/slides/slide{i}.xml')).find('p:cSld/p:spTree/p:sp',NS) for i in [1,2]]
script=['# What the Fingers Hear — Speaker Script','','Key points to emphasize appear in **bold**.','']
for position,spec in enumerate(SPEC['slides'],1):
    part=paths[spec['old']];root=parse(pkg[part]);number=re.search(r'slide(\d+)\.xml$',part).group(1)
    title_count=0
    for body in root.xpath('//p:txBody',namespaces=NS):
        shape=body.getparent();off=shape.find('p:spPr/a:xfrm/a:off',NS);ext=shape.find('p:spPr/a:xfrm/a:ext',NS)
        if off is not None:
            x,y=int(off.get('x')),int(off.get('y'))
            if position>1 and x<1000000 and y<1000000 and ext is not None and int(ext.get('cx'))>9000000:
                replace(body,spec['title']);title_count+=1
            if x>=11000000 and y<700000:replace(body,f'{position:02d}')
        replacements=SPEC['replacements'].get(str(position),{})
        if text(body) in replacements:replace(body,replacements[text(body)])
    assert position==1 or title_count==1,(position,title_count)
    if position in [4,11]:
        shape=deepcopy(patches[0 if position==4 else 1]);maxid=max(int(i) for i in root.xpath('//p:cNvPr/@id',namespaces=NS))
        shape.find('p:nvSpPr/p:cNvPr',NS).set('id',str(maxid+1));root.find('p:cSld/p:spTree',NS).append(shape)
    pkg[part]=dump(root)
    note_path=f'ppt/notesSlides/notesSlide{number}.xml';note_root=parse(pkg[note_path])
    body=note_root.xpath('//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]/p:txBody',namespaces=NS)[0]
    sources=text(body).split('SOURCES\n')[-1].splitlines()
    if position==5:
        extra=parse(original['ppt/notesSlides/notesSlide9.xml'])
        extra_body=extra.xpath('//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]/p:txBody',namespaces=NS)[0]
        sources+=text(extra_body).split('SOURCES\n')[-1].splitlines()
    if position==7:sources.insert(0,'User-provided CITI and application status, October 28, 2026')
    for p in list(body.findall('a:p',NS)):body.remove(p)
    note_paragraph(body,'SPEAKER SCRIPT',True);note_paragraph(body,'')
    for line in spec['script'].split('\n'):note_paragraph(body,line)
    note_paragraph(body,'');note_paragraph(body,'SOURCES',True)
    for line in dict.fromkeys(sources):note_paragraph(body,line)
    pkg[note_path]=dump(note_root)
    script += [f'## {position:02d}. {spec["title"]}','',spec['script'],'']
    if position==11:script+=['Practice reference: [Amber Sound Touch, “Memorising music”](https://soundtouch.ambertrust.org/services/instrumental-and-vocal-tuition/strategies/memorising-music/).','']

remove=set()
for old,s in enumerate(oldslides,1):
    if old in keep:continue
    slide_list.remove(s);rels.remove(relmap[s.get(q('r:id'))])
    part=paths[old];num=re.search(r'slide(\d+)\.xml$',part).group(1)
    remove.update([part,f'ppt/slides/_rels/slide{num}.xml.rels',f'ppt/notesSlides/notesSlide{num}.xml',f'ppt/notesSlides/_rels/notesSlide{num}.xml.rels'])
for part in remove:pkg.pop(part,None)
ct=parse(pkg['[Content_Types].xml'])
for override in list(ct):
    if override.get('PartName','').lstrip('/') in remove:ct.remove(override)
pkg['[Content_Types].xml']=dump(ct)
pkg['ppt/presentation.xml']=dump(deck);pkg['ppt/_rels/presentation.xml.rels']=dump(rels)
app=parse(pkg['docProps/app.xml']);ns={'e':'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'}
app.find('e:Slides',ns).text='12';pkg['docProps/app.xml']=dump(app)
with zipfile.ZipFile(BUILD/'compact-candidate.pptx','w',zipfile.ZIP_DEFLATED) as z:
    for name,data in pkg.items():z.writestr(name,data)
(ROOT/'outputs/peer-review/speaker_script_compact.md').write_text('\n'.join(script))
print(json.dumps({'slides':12,'scriptWords':sum(len(s['script'].split()) for s in SPEC['slides']),'titles':[s['title'] for s in SPEC['slides']]}))
