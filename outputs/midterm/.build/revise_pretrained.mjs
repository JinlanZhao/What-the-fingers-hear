import fs from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {PresentationFile,FileBlob} from '@oai/artifact-tool';
const ROOT='/Users/zhaojinlan/Desktop/Lann Projects/What-the-fingers-hear';
const SKILL='/Users/zhaojinlan/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations';
const BUILD=path.join(ROOT,'outputs/midterm/.build/pretrained');
const INPUT=path.join(ROOT,'outputs/midterm/presentation/Jinlan_Zhao_MTEC345_Midterm_v2.pptx');
const OUTPUT=path.join(ROOT,'outputs/midterm/presentation/Jinlan_Zhao_MTEC345_Midterm_v3.pptx');
const PY='/Users/zhaojinlan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';
process.env.RUNTIME_NODE_MODULES='/Users/zhaojinlan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
await fs.mkdir(BUILD,{recursive:true});
const p=await PresentationFile.importPptx(await FileBlob.load(INPUT));
if(p.slides.items.length!==12)throw Error('Expected 12 source slides');
const originalNotes=p.slides.items.map(s=>s.speakerNotes.text);
const s=p.slides.getItem(7);
const found=await p.inspect({select:'$.slides[7].elements[*]',include:['id','kind']});
p.delete(found.records.map(r=>r.id));
const C={ink:'#182A34',teal:'#146C68',muted:'#53636B',light:'#EAF3F1',rule:'#DCE3E5'};
function text(value,x,y,w,h,size=26,bold=false,color=C.ink){
 const sh=s.shapes.add({geometry:'textbox',name:value.slice(0,48),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=value;sh.text.style={typeface:'Arial',fontSize:size,bold,color,insets:0,wrap:true,verticalAlignment:'middle'};return sh;
}
function table(values,x,y,w,h,widths,font=23){
 const t=s.tables.add({rows:values.length,columns:2,left:x,top:y,width:w,height:h,columnWidths:widths,values});
 t.styleOptions={headerRow:true,bandedRows:false};t.borders.assign({fill:C.rule,width:0.6,style:'solid'});
 t.cells.block({row:0,column:0,rowCount:values.length,columnCount:2}).assign({margins:{left:12,right:10,top:6,bottom:6},anchor:'center'});
 for(let r=0;r<values.length;r++){
  t.rows[r].height=h/values.length;
  for(let c=0;c<2;c++){
   const cell=t.getCell(r,c);cell.fill=r===0?C.light:'#FFFFFF';
   cell.text.style={typeface:'Arial',fontSize:font,bold:r===0,color:r===0?C.teal:C.ink,verticalAlignment:'middle'};
  }
 }
 return t;
}
text('Iterations After M2BERT Pretraining',72,45,1136,66,43,true);
text('Fine-tuning and task expansion',72,143,550,44,28,true,C.teal);
table([
 ['Experiment','Result'],
 ['Pitch continuation','312/499\n62.53%'],
 ['Duration head','434/499\n86.97%'],
 ['Joint pitch + duration','P: 310/499\nD: 438/499'],
 ['Accidental augmentation','Accuracy: 87.68%\nMacro F1: 0.542']
],72,201,545,360,[301,244],24);
text('Longer pitch extension: no gain\nAccidental macro F1: 0.512 to 0.542',72,582,545,66,23,false,C.muted);
text('Pitch context and further experiments',667,143,541,44,27,true,C.teal);
table([
 ['Experiment','Result'],
 ['Context v1\nTrain backbone + branch','318/499\n63.73%'],
 ['Context v2\nFreeze + cache','323/499\n64.73%'],
 ['Context v3\nLonger budget','324/499\n64.93%'],
 ['Top-5 reranker\nEarly stop / 10 epochs','No gain'],
 ['Expand targets\n9,998 to 19,996','312–313/499'],
 ['Unfreeze backbone\nExpanded-data runs','Below initial\ncheckpoint']
],667,201,541,440,[309,232],23);
text('Jinlan Zhao  /  MTEC-345',72,675,800,22,16,false,C.muted);
const footer=text('08',1140,675,68,22,16,false,C.muted);footer.text.alignment='right';
const speech=`After switching to pretrained M2BERT, I tested several ways to adapt it.

One pitch continuation reached 62.53 percent at epoch five. A separate longer run stayed below its starting checkpoint.

I added duration correction, then trained pitch and duration together. The joint model reached 62.12 percent for pitch and 87.78 percent for duration from one checkpoint.

For accidentals, I added rare-class examples. Macro F1 rose from 0.512 to 0.542, with a small drop in overall accuracy.

Then I focused on pitch context. Training the backbone and context branch together reached 63.73 percent. Freezing the backbone and training only the branch reached 64.73 percent. Caching the backbone outputs made those experiments much faster. A longer-budget version reached 64.93 percent, with its best checkpoint at epoch two.

I also trained a top-five reranker using interval, register, and harmony features. Both early stopping and a full ten-epoch run gave no improvement.

Finally, I doubled target examples to 19,996 and tested frozen and unfrozen backbones. Those runs stayed below the starting model, so I kept the frozen backbone with context v3.`;
s.speakerNotes.text=speech+`\n\nSources (not spoken)\nml/m2bert_finetune_comparison.ipynb: Markdown cells 17, 19, 23 and 28; saved continuation output in code cells 14 and 18.\nml/correction_experiment_archive.ipynb: Part B, Markdown cells 76, 78, 82, 87, 96, 99 and 101; accidental v1/v2 records in code cells 97 and 98.\nThe current archive has 103 cells. Context v3, reranker 10-epoch, expanded-target and unfreezing results are cross-checked against ml/correction_all_experiments.md Sections 3e–3h and saved run configs/metrics.\nContext v2: train only 227,380 branch parameters. Cache build 175 seconds, training 2.6 seconds.\nTime-signature recovery was checked in MusicXML: 11.6% of dev excerpts contain the time-signature element; missing entries retain an unknown category.\nThe successful pitch continuation and unsuccessful longer extension are separate runs with different starting checkpoints.\nPitch/duration validation n=499. Accidental validation n=1,437. Expanded examples select a second target in the same 9,998 excerpts.\nTiming cue: allow about 90 seconds for this page. Keep the demo video to about 2 minutes 30 seconds to stay within the 12-minute presentation.`;
const expected=originalNotes.slice();expected[7]=s.speakerNotes.text;
await fs.writeFile(path.join(BUILD,'expected-notes.json'),JSON.stringify(expected,null,2));
await fs.writeFile(path.join(ROOT,'outputs/midterm/model_iterations_speaker_notes.md'),'# Slide 8 - Iterations After M2BERT Pretraining\n\n'+speech+'\n');
for(let i=0;i<12;i++){
 if(p.slides.items[i].speakerNotes.text!==expected[i])throw Error('Unexpected notes change '+(i+1));
 await fs.writeFile(path.join(BUILD,`slide-${i+1}.png`),new Uint8Array(await (await p.export({slide:p.slides.items[i],format:'png',scale:1})).arrayBuffer()));
}
const candidatePath=path.join(BUILD,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidatePath);
execFileSync(PY,[path.join(ROOT,'outputs/midterm/.build/restore_chart_parts.py'),INPUT,candidatePath],{stdio:'inherit'});
await finalizePresentation({
 workspaceDir:ROOT,candidatePath,finalPath:OUTPUT,pythonExecutable:PY,
 integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 explicitTotalSlideCount:12,
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[3,7,8,9,10].flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeTableOwnerSlides:[3,7,8,9,10],requiredNativeChartOwnerSlides:[7],materializeLiteralChartWorkbooks:true,
 fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(BUILD,'validation.json')
});
console.log(OUTPUT);
