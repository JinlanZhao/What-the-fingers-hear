import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation, PresentationFile} from '@oai/artifact-tool';

const ROOT='/Users/zhaojinlan/Desktop/Lann Projects/What-the-fingers-hear';
const BUILD=path.join(ROOT,'outputs/midterm/.build');
const OUT=path.join(ROOT,'outputs/midterm/presentation');
const SKILL='/Users/zhaojinlan/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations';
const PY='/Users/zhaojinlan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';
process.env.RUNTIME_NODE_MODULES='/Users/zhaojinlan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {applyPresentationChartFont,finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const source=(await fs.readFile(path.join(ROOT,'outputs/midterm/speaker_script_by_slide_en.md'),'utf8')).split('\n---\n')[0];
const notes=source.split(/\n## Slide \d+[^\n]*\n/).slice(1).map(s=>s.trim());
if(notes.length!==11)throw Error('Expected 11 script sections');
await fs.writeFile(path.join(BUILD,'expected_notes.json'),JSON.stringify(notes,null,2));
const C={ink:'#182A34',teal:'#146C68',muted:'#53636B',light:'#EAF3F1',rule:'#DCE3E5',white:'#FFFFFF',amber:'#956A27'};
const FONT='Arial';
const p=Presentation.create({slideSize:{width:1280,height:720}});
p.theme.defaultFont=FONT;
function txt(s,text,x,y,w,h,size=28,bold=false,color=C.ink,align='left'){
 const sh=s.shapes.add({geometry:'textbox',name:text.slice(0,48),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=text;sh.text.style={typeface:FONT,fontSize:size,bold,color,alignment:align,verticalAlignment:'middle',wrap:true,insets:0};return sh;
}
function box(s,text,x,y,w,h,{fill=C.light,size=26,bold=false,color=C.ink}={}){
 const sh=s.shapes.add({geometry:'rect',name:text.slice(0,40),position:{left:x,top:y,width:w,height:h},fill,line:{fill:C.rule,width:1}});
 sh.text=text;sh.text.style={typeface:FONT,fontSize:size,bold,color,alignment:'center',verticalAlignment:'middle',insets:12};return sh;
}
function connect(s,a,b,from='right',to='left'){
 return s.shapes.connect(a,b,{kind:'straight',fromSide:from,toSide:to,line:{fill:C.teal,width:2},tail:{type:'triangle',width:'sm',length:'sm'}});
}
function base(title,n){
 const s=p.slides.add();s.background.fill=C.white;
 if(title)txt(s,title,72,45,1136,66,44,true);
 txt(s,'Jinlan Zhao  /  MTEC-345',72,675,800,22,16,false,C.muted);
 txt(s,String(n).padStart(2,'0'),1140,675,68,22,16,false,C.muted,'right');
 s.speakerNotes.text=notes[n-1];return s;
}
function table(s,values,x,y,width,height,colWidths,fontSize=24){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width,height,values,columnWidths:colWidths});
 t.styleOptions={headerRow:true,bandedRows:false};t.borders.assign({fill:C.rule,width:0.6,style:'solid'});
 const all=t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length});
 all.assign({textStyle:{typeface:FONT,fontSize,color:C.ink},margins:{left:16,right:14,top:12,bottom:12},anchor:'center'});
 for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
  const cell=t.getCell(r,c);cell.fill=r===0?C.light:C.white;
  cell.text.style={typeface:FONT,fontSize,color:r===0?C.teal:C.ink,bold:r===0,verticalAlignment:'middle'};
 }
 for(let r=0;r<values.length;r++)t.rows[r].height=height/values.length;
 return t;
}
function lineText(s,head,body,y){txt(s,head,72,y,300,45,28,true,C.teal);txt(s,body,398,y,810,72,28);}

// 1. Cover.
{
 const s=base('',1);
 txt(s,'Context-Aware Correction\nof OMR Errors\nfor Braille Music',72,138,1110,260,58,true);
 txt(s,'Musical context for pitch, duration, and accidental correction',76,438,1100,64,28,false,C.teal);
 txt(s,'Jinlan Zhao\nMTEC-345: Machine Learning for Musicians\nNovember 4, 2026',76,546,1050,92,23,false,C.muted);
}
// 2. Motivation.
{
 const s=base('Why this Project?',2);
 txt(s,'Recognition errors travel into playback and Braille scores.',72,140,1110,85,36,true);
 const labels=['Printed score / PDF','OMR','MusicXML','Playback / Braille'];
 const xs=[72,380,575,920],ws=[254,140,290,288];
 const nodes=labels.map((l,i)=>box(s,l,xs[i],282,ws[i],88,{fill:i===2?C.light:C.white,size:26,bold:i===2}));
 for(let i=0;i<3;i++)connect(s,nodes[i],nodes[i+1]);
 txt(s,'My goal',72,437,220,40,27,true,C.teal);
 txt(s,'Correct musical symbols before they enter the transcription workflow.',72,491,1100,62,31);
 txt(s,'What the Fingers Hear connects a physical Braille score with audio playback.',72,587,1120,45,24,false,C.muted);
}
// 3. Related work.
{
 const s=base('Related Work',3);
 table(s,[
 ['Work','Contribution','My connection'],
 ['OMR Spellchecker\nde Reuse & Fujinaga, 2022','Flags suspicious\nmusical symbols','Predict a replacement\nat the selected location'],
 ['OLiMPiC / LMX\nMayer et al., 2024','Aligned score data\nand symbolic sequences','Create controlled errors\nwith known answers'],
 ['Audiveris','Score images to MusicXML','Provide real OMR examples\nfor the final project']
 ],72,159,1136,364,[330,400,406],24);
 txt(s,'My contribution: context-aware correction between detection and Braille transcription.',72,569,1115,70,28,true,C.teal);
}
// 4. Architecture.
{
 const s=base('System Architecture',4);
 txt(s,'Input: MusicXML, target note, correction task',72,139,1100,45,28);
 const ns=[['Parse notes',72,216,228],['Encode attributes',358,216,245],['M2BERT',661,216,235],['Candidates',954,216,254]];
 const shapes=ns.map(([t,x,y,w])=>box(s,t,x,y,w,88));
 for(let i=0;i<3;i++)connect(s,shapes[i],shapes[i+1]);
 txt(s,'Task routing',72,353,680,42,27,true,C.teal);
 txt(s,'Pitch: joint backbone + head + context\nDuration: joint backbone + head\nAccidentals: separate fine-tuned model',72,410,735,122,25);
 const output=box(s,'Corrected MusicXML\nMIDI\nPrediction record',954,377,254,153,{fill:C.white,size:24});
 connect(s,shapes[3],output,'bottom','top');
 txt(s,'Python   PyTorch   Transformers   lxml   mido',72,577,1120,35,23,false,C.muted);
 txt(s,'Local Mac with MPS acceleration',72,618,1120,30,23,false,C.muted);
}
// 5. Technical approach.
{
 const s=base('Technical Approach',5);
 txt(s,'Model',72,143,260,40,28,true,C.teal);
 txt(s,'12 encoder layers\n768-dimensional hidden states\n52 pitch / 28 duration / 5 accidental classes',72,196,1130,112,27);
 txt(s,'Data',72,344,240,40,28,true,C.teal);
 txt(s,'Pitch + duration: 9,998 train / 499 validation\n66.6% of the OLiMPiC training split\nAccidentals: 15,012 train / 1,437 validation',72,395,610,118,26);
 txt(s,'Note representation',760,344,448,40,28,true,C.teal);
 txt(s,'Bar boundary\nPosition\nPitch\nDuration',760,395,440,145,27);
 txt(s,'Pitch context: key, time signature, voice, staff',72,551,1136,39,25,false,C.teal);
 txt(s,'Training: last 2 layers + task heads, then a frozen backbone with a pitch context branch.',72,600,1136,60,25,false,C.muted);
}
// 6. Editable video space.
{
 const s=base('Demo!',6);
 const ph=s.shapes.add({geometry:'rect',name:'DEMO_VIDEO_PLACEHOLDER',position:{left:187,top:132,width:906,height:510},fill:'#F6F7F7',line:{fill:'#B9C7CA',width:1.5,style:'dashed'}});
 txt(s,'Demo video',257,300,766,70,44,true,C.muted,'center');
 txt(s,'Pitch correction   /   Duration correction   /   Accidentals',237,394,806,52,24,false,C.muted,'center');
}
// 7. Quantitative results: native table and chart.
{
 const s=base('Results: Quantitative',7);
 table(s,[['Task / model','Top-1'],['Pitch: custom Transformer','16.63%'],['Pitch: M2BERT + context','64.93%'],['Duration: joint model','87.78%'],['Accidentals: v2','87.68%']],72,169,550,326,[405,145],23);
 txt(s,'Pitch experiment progression',675,145,530,42,25,true,C.teal);
 const chart=s.charts.add('bar',{
  position:{left:652,top:199,width:570,height:325},categories:['Custom','M2BERT','Joint','Context'],
  series:[{name:'Pitch validation top-1',values:[0.1663,0.6132,0.6212,0.6493],fill:C.teal}],
  hasLegend:false,barOptions:{direction:'column',grouping:'clustered',gapWidth:85},
  xAxis:{textStyle:{fontSize:21,fill:C.ink},line:{fill:C.rule,width:1}},
  yAxis:{min:0,max:1,majorUnit:0.25,numberFormatCode:'0%',textStyle:{fontSize:20,fill:C.muted},majorGridlines:{fill:C.rule,width:0.7}},
  dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.0%',textStyle:{fontSize:21,bold:true,fill:C.ink}},
  chartFill:C.white,plotAreaFill:C.white,chartLine:{fill:'none',width:0}
 });
 applyPresentationChartFont(chart,{fontFamily:FONT});
 txt(s,'Pitch top-5: 87.98%',72,544,1136,48,30,true,C.teal);
 txt(s,'Validation: pitch / duration n = 499. Accidentals n = 1,437.',72,610,1136,35,22,false,C.muted);
}
// 8. Qualitative results.
{
 const s=base('Results: Qualitative',8);
 table(s,[['Example','Reference','Prediction','Observation'],['Pitch','E4','E4','Restores reference pitch'],['Duration','Eighth note','Eighth note','Restores reference length'],['Pitch ranking','D4','E4','D4 appears third']],72,171,1136,316,[235,220,220,461],26);
 txt(s,'Pitch candidates for the ranking example',72,534,1100,40,26,true,C.teal);
 txt(s,'1  E4               2  C4               3  D4',72,588,1100,46,30);
}
// 9. Challenges.
{
 const s=base('Challenges and Solutions',9);
 table(s,[['Challenge','My solution','Result'],['Low pitch accuracy\nfrom scratch','Adapt pretrained\nM2BERT','Initial pitch accuracy\n61.32%'],['Incorrect exported\nduration','Use quarter-note units\nconsistently','Correct eighth-note\nexport'],['Rare accidental\nclasses','Add 400 double-flat /\ndouble-sharp examples','Macro F1\n0.512 to 0.542']],72,171,1136,386,[350,410,376],25);
 txt(s,'I track overall accuracy and performance across classes.',72,596,1136,46,27,false,C.teal);
}
// 10. Accomplishments.
{
 const s=base('Accomplishments',10);
 txt(s,'Completed',72,164,530,48,31,true,C.teal);
 txt(s,'Correction data and model comparisons\nPitch, duration, and accidental prediction\nMusicXML and MIDI export',72,237,1090,140,30);
 txt(s,'Next milestones',72,426,530,48,31,true,C.teal);
 txt(s,'Connect the error detector\nEvaluate the resulting Braille notation',72,490,1090,92,30);
 txt(s,'My lesson: improve representation and training strategy before increasing model size.',72,608,1136,42,24,false,C.muted);
}
// 11. Final project.
{
 const s=base('Future Work',11);
 const top=[['Score image',72,172,190],['Audiveris',307,172,190],['Error detector',542,172,234],['Correction',821,172,190]];
 const ns=top.map(([t,x,y,w])=>box(s,t,x,y,w,72,{size:25}));
 for(let i=0;i<3;i++)connect(s,ns[i],ns[i+1]);
 const out=box(s,'MusicXML\nMIDI / Braille',821,292,300,100,{size:26});connect(s,ns[3],out,'bottom','top');
 txt(s,'Braille comparison',72,303,660,45,31,true,C.teal);
 txt(s,'Reference score\nRaw OMR output\nCorrected output',72,366,660,128,30);
 txt(s,'Evaluate detection, correction, and the resulting Braille notation.',72,534,1110,64,28);
 txt(s,'Questions?',72,613,1050,43,30,true,C.teal);
}

// Source metadata follows the verbatim script without changing it.
const refs={
 2:['Course proposal: Context-Aware Correction of OMR Errors for Braille Music, Jinlan Zhao.'],
 3:['de Reuse & Fujinaga (2022): https://zenodo.org/records/7316782','Mayer et al. (2024): https://arxiv.org/abs/2403.13763','Audiveris MusicXML export: https://audiveris.github.io/audiveris/_pages/tutorials/quick/export/'],
 5:['M2BERT, Wang & Su (2025): https://arxiv.org/abs/2507.04776','Official implementation: https://github.com/york135/M2BERT','Local model configuration and data: ml/m2bert_finetune_comparison.ipynb; ml/dataset/olimpic-1.0-synthetic/samples.*.txt'],
 7:['Experiment record: ml/correction_all_experiments.md','Counts: context v3 pitch 324/499, top-5 439/499; joint duration 438/499; accidental v2 1260/1437.'],
 8:['Local examples: ml/demo/inference_demo; context v3 validation prediction index 57.'],
 9:['Local records: ml/cleanup_summary.md; ml/data/runs/m2bert_acc_v2_20261102_115241/config.json'],
 11:['Final-project goals: MTEC-345 course proposal, Jinlan Zhao, Sections 1, 2 and 5.']
};
const expected=notes.map((n,i)=>n+(refs[i+1]?'\n\nSources (not spoken)\n'+refs[i+1].join('\n'):''));
for(let i=0;i<11;i++)p.slides.items[i].speakerNotes.text=expected[i];
await fs.writeFile(path.join(BUILD,'expected_notes_with_sources.json'),JSON.stringify(expected,null,2));
await fs.mkdir(path.join(BUILD,'renders'),{recursive:true});
for(let i=0;i<11;i++){
 const slide=p.slides.items[i];
 await fs.writeFile(path.join(BUILD,'renders',`slide-${i+1}.png`),new Uint8Array(await (await p.export({slide,format:'png',scale:1})).arrayBuffer()));
 await fs.writeFile(path.join(BUILD,'renders',`slide-${i+1}.json`),await (await slide.export({format:'layout'})).text());
}
await (await PresentationFile.exportPptx(p)).save(path.join(BUILD,'candidate.pptx'));
const finalPath=path.join(OUT,'Jinlan_Zhao_MTEC345_Midterm.pptx');
const result=await finalizePresentation({
 workspaceDir:ROOT,candidatePath:path.join(BUILD,'candidate.pptx'),finalPath,pythonExecutable:PY,
 integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[3,7,8,9].flatMap(n=>['--require-native-table-slide',String(n)])],
 explicitTotalSlideCount:11,requiredNativeTableOwnerSlides:[3,7,8,9],requiredNativeChartOwnerSlides:[7],
 materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,
 receiptPath:path.join(BUILD,'validation.json')
});
console.log(JSON.stringify({finalPath,result},null,2));
