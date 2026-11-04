import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
import {PresentationFile,FileBlob} from '@oai/artifact-tool';

const ROOT='/Users/zhaojinlan/Desktop/Lann Projects/What-the-fingers-hear';
const SKILL='/Users/zhaojinlan/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations';
const BUILD=path.join(ROOT,'outputs/midterm/.build/iterations');
const INPUT=path.join(ROOT,'outputs/midterm/presentation/Jinlan_Zhao_MTEC345_Midterm.pptx');
const OUTPUT=path.join(ROOT,'outputs/midterm/presentation/Jinlan_Zhao_MTEC345_Midterm_v2.pptx');
process.env.RUNTIME_NODE_MODULES='/Users/zhaojinlan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
await fs.mkdir(BUILD,{recursive:true});
const p=await PresentationFile.importPptx(await FileBlob.load(INPUT));
if(p.slides.items.length!==11)throw Error('Source deck should have 11 slides');
const originalNotes=p.slides.items.map(s=>s.speakerNotes.text);
await fs.writeFile(path.join(BUILD,'source-inspect.ndjson'),(await p.inspect({kind:'slide,layout,textbox,table,chart,notes',maxChars:200000})).ndjson);
await fs.writeFile(path.join(BUILD,'before-slide-7.png'),new Uint8Array(await (await p.export({slide:p.slides.getItem(6),format:'png',scale:1})).arrayBuffer()));
p.slides.insert({after:p.slides.getItem(6)});
const s=p.slides.getItem(7);
s.background.fill='#FFFFFF';
const C={ink:'#182A34',teal:'#146C68',muted:'#53636B',light:'#EAF3F1',rule:'#DCE3E5'};
function text(value,x,y,w,h,size=26,bold=false,color=C.ink){
 const sh=s.shapes.add({geometry:'textbox',name:value.slice(0,48),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=value;sh.text.style={typeface:'Arial',fontSize:size,bold,color,insets:0,wrap:true,verticalAlignment:'middle'};return sh;
}
function table(values,x,y,w,h,widths){
 const t=s.tables.add({rows:values.length,columns:2,left:x,top:y,width:w,height:h,columnWidths:widths,values});
 t.styleOptions={headerRow:true,bandedRows:false};t.borders.assign({fill:C.rule,width:0.6,style:'solid'});
 t.cells.block({row:0,column:0,rowCount:values.length,columnCount:2}).assign({margins:{left:14,right:12,top:8,bottom:8},anchor:'center'});
 for(let r=0;r<values.length;r++){
  t.rows[r].height=h/values.length;
  for(let c=0;c<2;c++){
   const cell=t.getCell(r,c);cell.fill=r===0?C.light:'#FFFFFF';
   cell.text.style={typeface:'Arial',fontSize:24,bold:r===0,color:r===0?C.teal:C.ink,verticalAlignment:'middle'};
  }
 }
 return t;
}
text('Model Iterations',72,45,1136,66,44,true);
text('What improved pitch',72,143,540,44,29,true,C.teal);
table([
 ['Attempt','Validation top-1'],
 ['More data +\nmodest capacity','6.01% to 11.02%'],
 ['Masking +\nvoice conditioning','16.63%'],
 ['Pretrained\nM2BERT','61.32%'],
 ['Joint model +\ncontext branch','64.93%']
],72,205,540,342,[300,240]);
text('What I did not adopt',666,143,542,44,29,true,C.teal);
table([
 ['Attempt','Result'],
 ['Larger model\nfrom scratch','11.22%'],
 ['Dynamic masking','11.02%'],
 ['Target-note features','11.82%'],
 ['Candidate reranking','No gain in 10 epochs'],
 ['Expanded targets /\nunfreezing backbone','Below starting model']
],666,205,542,342,[302,240]);
text('I kept the frozen backbone and context branch.',72,584,1136,56,31,true,C.teal);
text('Pitch validation: n = 499',72,642,1136,24,19,false,C.muted);
text('Jinlan Zhao  /  MTEC-345',72,675,800,22,16,false,C.muted);
const speech=`I first increased the training data and model capacity, then added masking and voice information. My best model from scratch reached 16.6 percent pitch accuracy.

Pretrained M2BERT brought the biggest improvement, reaching 61.3 percent. The joint model with a context branch reached 64.9 percent.

I also tried a larger model, dynamic masking, extra target-note features, and candidate reranking. These stayed below my strongest model at each stage.

Finally, I expanded the training targets to 19,996 and tried unfreezing the backbone. Training loss fell, but validation accuracy dropped. I kept the frozen backbone and context branch.

I learned to judge each change by validation results, rather than model size or training loss.`;
s.speakerNotes.text=speech+'\n\nSources (not spoken)\nml/correction_all_experiments.md, Sections 1, 2, 3e, 3f, 3g and 3h.\nExpanded examples reuse the original 9,998 excerpts with an additional target note.\nTiming cue: allow about 55 seconds here and shorten the demo video by the same amount to keep the presentation within 12 minutes.';
await fs.writeFile(path.join(ROOT,'outputs/midterm/model_iterations_speaker_notes.md'),'# Slide 8 - Model Iterations\n\n'+speech+'\n');
// Only the page number changes on the original slides after the insertion.
for(let i=8;i<12;i++){
 const slide=p.slides.getItem(i);
 const page=slide.shapes.items.find(sh=>sh.position.left>=1100 && sh.position.top>=670 && /^\d{2}$/.test(String(sh.text)));
 if(!page)throw Error('Missing page footer '+i);
 page.text=String(i+1).padStart(2,'0');
}
text('08',1140,675,68,22,16,false,C.muted).text.alignment='right';
const expected=originalNotes.slice();expected.splice(7,0,s.speakerNotes.text);
for(let i=0;i<12;i++)if(p.slides.items[i].speakerNotes.text!==expected[i])throw Error('Notes changed on slide '+(i+1));
await fs.writeFile(path.join(BUILD,'expected-notes.json'),JSON.stringify(expected,null,2));
for(let i=0;i<12;i++){
 const slide=p.slides.getItem(i);
 await fs.writeFile(path.join(BUILD,`slide-${i+1}.png`),new Uint8Array(await (await p.export({slide,format:'png',scale:1})).arrayBuffer()));
}
const candidatePath=path.join(BUILD,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidatePath);
execFileSync('/Users/zhaojinlan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',[
 path.join(ROOT,'outputs/midterm/.build/restore_chart_parts.py'),INPUT,candidatePath
],{stdio:'inherit'});
await finalizePresentation({
 workspaceDir:ROOT,candidatePath,finalPath:OUTPUT,
 pythonExecutable:'/Users/zhaojinlan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
 integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 explicitTotalSlideCount:12,
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[3,7,8,9,10].flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeTableOwnerSlides:[3,7,8,9,10],requiredNativeChartOwnerSlides:[7],
 materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
 receiptPath:path.join(BUILD,'validation.json')
});
console.log(OUTPUT);
