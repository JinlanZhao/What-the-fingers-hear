import fs from 'node:fs/promises';
import { FileBlob,PresentationFile,Presentation } from '@oai/artifact-tool';
const root='/Users/zhaojinlan/Desktop/Lann Projects/What-the-fingers-hear';
const build=`${root}/.codex-build/peer-review`;
const spec=JSON.parse(await fs.readFile(`${build}/compact.json`,'utf8'));
const p=await PresentationFile.importPptx(await FileBlob.load(`${root}/outputs/peer-review/presentation_revised.pptx`));
p.slides.keep(spec.slides.map(s=>s.old-1));
for(let i=0;i<p.slides.items.length;i++){
  const slide=p.slides.items[i];
  const title=slide.shapes.items.find(s=>s.position.top<100&&s.position.left<100&&s.position.width>900);
  if(i>0&&title)title.text=spec.slides[i].title;
  for(const [oldText,newText] of Object.entries(spec.replacements[String(i+1)]??{})){
    for(const shape of slide.shapes.items)shape.text?.replace(oldText,newText);
  }
  slide.speakerNotes.text=spec.slides[i].script;
}
await (await PresentationFile.exportPptx(p)).save(`${build}/compact-authored.pptx`);

// The added text remains native and matches the source deck's typography.
const patch=Presentation.create({slideSize:{width:1280,height:720}});
const s=patch.slides.add();
const shape=s.shapes.add({name:'clarification-summary',geometry:'textbox',position:{left:74,top:600,width:700,height:76},fill:'none',line:{fill:'none',width:0}});
shape.text='Clarification keeps the selected measure.\n“Flute one, flute two, or both?”';
shape.text.style={fontSize:24,typeface:'Helvetica Neue',color:'#CFEA79',insets:0,bold:true,autoFit:'none'};
const n=patch.slides.add();
const tracking=n.shapes.add({name:'tracking-summary',geometry:'textbox',position:{left:76,top:609,width:1124,height:36},fill:'none',line:{fill:'none',width:0}});
tracking.text='Measure tracking accuracy, response time and recovery.';
tracking.text.style={fontSize:24,typeface:'Helvetica Neue',color:'#171A1D',insets:0,bold:true,autoFit:'none'};
await (await PresentationFile.exportPptx(patch)).save(`${build}/voice-patch.pptx`);
console.log(JSON.stringify({slides:p.slides.items.length}));
