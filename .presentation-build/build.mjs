import fs from 'node:fs/promises';
import path from 'node:path';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const root = '/Users/zhaojinlan/Desktop/Lann Projects/What-the-fingers-hear';
const build = path.join(root, '.presentation-build');
const C = { ink:'#171A1D', dark:'#262A2E', paper:'#FFFDF8', coral:'#F06C5B', lime:'#CFEA79', blue:'#6AB7D6', muted:'#7C776F', light:'#D8D1C5', white:'#FFFFFF', rule:'#D8D1C5' };
const font = 'Helvetica Neue';
const p = Presentation.create({slideSize:{width:1280,height:720}});
p.theme.defaultFont = font;
p.comments.setSelf({displayName:'Jinlan Zhao', initials:'JZ'});
let count=0;
const scripts=[];

function rect(s,x,y,w,h,color,name='accent') {
 return s.shapes.add({geometry:'rect',name,position:{left:x,top:y,width:w,height:h},fill:color,line:{fill:'none',width:0}});
}
function txt(s,text,x,y,w,h,size=26,color=C.ink,bold=false,name='text') {
 const a=s.shapes.add({geometry:'textbox',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 a.text=text; a.text.style={fontFamily:font,typeface:font,fontSize:size,color,bold,verticalAlignment:'top',wrap:true}; a.text.insets=0;
 return a;
}
function slide(title,dark=false,folio=true) {
 const s=p.slides.add(); count++; s.background.fill=dark?C.ink:C.paper;
 if(title){txt(s,title,72,48,1100,68,45,dark?C.white:C.ink,true,'slide-title');rect(s,72,126,54,5,C.coral);}
 if(folio)txt(s,String(count).padStart(2,'0'),1190,45,45,30,17,dark?C.light:C.muted,true,'page-number');
 return s;
}
function notes(s,title,script,sources=[]) {
 s.speakerNotes.text='SPEAKER SCRIPT\n\n'+script+'\n\nSOURCES\n'+sources.map(x=>path.isAbsolute(x)?x:root+'/'+x).join('\n');
 s.speakerNotes.setVisible(true);
 p.comments.addThread({slide:s},script,{position:{x:1200,y:50}});
 scripts.push({slide:count,title,script,sources});
}
async function pic(s,file,x,y,w,h,fit='contain',name='project-photo'){
 const b=await fs.readFile(path.isAbsolute(file)?file:path.join(root,file));
 return s.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:file.endsWith('.png')?'image/png':'image/jpeg',alt:name,name,fit,position:{left:x,top:y,width:w,height:h}});
}
function row(s,n,heading,body,y,dark=false){
 const color=dark?C.white:C.ink;
 txt(s,String(n).padStart(2,'0'),80,y,90,65,58,C.coral,true);
 rect(s,217,y+1,4,108,n===2?C.blue:C.coral);
 txt(s,heading,260,y+2,330,94,30,color,true);
 txt(s,body,610,y+5,575,105,25,dark?C.light:C.ink);
}
function table(s,values,x,y,w,h,widths,size=25){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values});
 t.styleOptions={headerRow:false,bandedRows:false};
 t.borders.assign({fill:C.rule,width:0.6,style:'solid'});
 for(let r=0;r<values.length;r++)for(let c=0;c<values[r].length;c++){
  const cell=t.getCell(r,c);cell.fill=r===0?C.ink:C.paper;
  cell.text.style={fontFamily:font,typeface:font,fontSize:r===0?21:size,color:r===0?C.white:C.ink,bold:r===0||c===0};
 }
 t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({margins:{left:16,right:16,top:14,bottom:10},anchor:'center'});
 return t;
}

// 01
{
 const s=slide('',true);
 await pic(s,'.presentation-build/reference/llm40.jpg',0,0,690,720,'cover','Current prototype with Braille score and physical controls');
 rect(s,690,0,9,720,C.coral);
 txt(s,'WHAT THE\nFINGERS HEAR',750,91,460,164,57,C.white,true,'deck-title');
 txt(s,'Touch-anchored playback\nand voice-selected instruments',750,292,455,110,28,C.paper);
 rect(s,750,430,350,4,C.coral);
 txt(s,'Jinlan Zhao\nElectronic Production and Design\nBerklee College of Music',750,463,450,105,22,C.light);
 txt(s,'PROGRESS REPORT 2',750,618,440,28,18,C.lime,true);
 txt(s,'MTEC-498 Peer Review\nOctober 2026',750,653,440,47,17,C.light);
 notes(s,'What the Fingers Hear',"Hi everyone. I'm Jinlan Zhao, and I study Electronic Production and Design at Berklee. My project, What the Fingers Hear, explores audio navigation from a physical Braille music score. A reader selects a measure with their finger and uses an explicit command to hear the music. I'm interested in how music technology can support that connection between touch and listening. In my last report, the camera and gesture playback path worked, while voice-selected instruments were still planned. Today I'll focus on the physical controls and voice interaction I have added since then, the changes that helped, and what I still need to test.",['demo/Videos/Add-LLM-Parser.MOV','Documentation/Proposal/README.md']);
}
// 02
{
 const s=slide('Since the last report');
 table(s,[['Area','Previous report','Current prototype'],['Voice-selected instruments','Planned','Connected to Max playback'],['Physical controls','Proposed after demo','RECORD, PLAY and STOP'],['Spoken feedback','Needed','Clarification and some errors'],['Reader evaluation','Not yet validated','Research protocol drafted']],72,180,1136,360,[298,350,488],25);
 txt(s,'The score, page map, camera tracking and Max playback remain the starting point.',75,585,1110,65,25,C.muted);
 notes(s,'Since the last report',"This table shows the change since Progress Report One. The prepared score, page map, camera tracking and Max playback were already connected, so I'm treating them as the starting point. The main new work is voice-selected playback, three physical controls, and spoken clarification. Feedback is still partial. The system can ask which instrument part I mean, but it does not yet provide all the measure and score information discussed last time. I have also drafted a research protocol. That is preparation for evaluation, rather than a completed user study.",['/Users/zhaojinlan/Documents/DocumentMe/Berklee Study/7th Semester/MTEC-498/Progress Report 1/What_the_Fingers_Hear_Progress_Report_1 .pptx','Documentation/Process-Report/Voice-MVP-Report.md','Documentation/Process-Report/LLM-Parser-Report.md','Research Study/Research Protocol.docx']);
}
// 03
{
 const s=slide('Physical controls',false,false);
 await pic(s,'.presentation-build/reference/hardware8.jpg',840,0,440,720,'cover','Teensy button prototype during hardware testing');
 rect(s,830,0,8,720,C.coral);
 txt(s,'03',1190,45,45,30,17,C.ink,true,'photo-page-number');
 const ys=[188,337,486];
 [['RECORD','Hold to speak\nRelease to submit'],['PLAY','Start the Full Mix\nfrom the selected measure'],['STOP','Stop playback\nCancel a pending request']].forEach(([a,b],i)=>{
  txt(s,a,74,ys[i],185,60,29,C.ink,true);txt(s,b,270,ys[i]+1,515,90,27);
  if(i<2)rect(s,74,ys[i]+118,700,1,C.rule);
 });
 txt(s,'Teensy 4.0 with three push buttons',74,653,720,35,21,C.muted);
 notes(s,'Physical controls',"The last demonstration raised a problem with repeated or unclear gesture activation. I added physical buttons as another input method to test. RECORD works as push-to-talk. I hold it while speaking, and releasing it submits the request. PLAY starts the Full Mix from the selected measure. STOP stops playback and cancels recording or a pending request. The controls use a Teensy board with debounced button events. These buttons give me a more explicit control path for development. I still need to compare them with gestures before deciding which method works better for Braille music readers.",['Hardware/Buttons/Buttons.ino','Documentation/Process-Report/Voice-MVP-Report.md','Documentation/Process-Report/Braille-Score-Design-Review1.md','demo/Videos/Hardware-testing.mov']);
}
// 04
{
 const s=slide('Current system',true);
 const xs=[74,370,666,962];
 const heads=['Page and finger','Record and speech','Command parsing','Audio playback'];
 const bodies=['OpenCV and ArUco\nMediaPipe fingertip\nPage-map lookup','Freeze the measure\nHold RECORD\nLocal Whisper ASR','Local Qwen2.5:7b\nPython validation\nClarify if needed','OSC to Max/MSP\nFull Mix or Stems\nSelected range'];
 for(let i=0;i<4;i++){
  txt(s,String(i+1).padStart(2,'0'),xs[i],200,210,70,58,[C.coral,C.lime,C.blue,C.white][i],true);
  txt(s,heads[i],xs[i],295,246,83,30,C.white,true);
  txt(s,bodies[i],xs[i],393,246,156,24,C.light);
  if(i<3)rect(s,xs[i]+94,245,196,2,'#62676A','data-flow-link');
 }
 rect(s,74,584,1134,1,'#62676A');
 txt(s,'Direct PLAY and gestures can send playback commands without speech recognition.',74,610,1120,61,25,C.light);
 notes(s,'Current system',"The prototype now connects position selection, speech and playback. OpenCV and ArUco establish page coordinates, while MediaPipe estimates the fingertip position. A prepared page map converts that position into a measure number. When RECORD begins, the controller freezes the selected measure for that request. Local Whisper transcribes the speech, and a local Qwen model interprets it. Python checks the command before sending OSC to Max. Max handles the audio and synchronization. Direct PLAY and gestures can bypass speech recognition. The current setup runs on my Mac, and the spoken responses use macOS speech output. I haven't validated portability or measured end-to-end latency yet.",['camera/finger_measure_test.py','camera/shared_state.py','camera/voice_mvp.py','camera/llm_parser.py','Documentation/Process-Report/Max-Playback-Current-Architecture.md']);
}
// 05
{
 const s=slide('Voice-selected playback',true);
 txt(s,'Single instrument',74,183,610,42,23,C.lime,true);
 txt(s,'“Play violin one.”',74,228,670,69,36,C.white,true);
 txt(s,'Uses the measure captured when RECORD begins.',74,303,690,70,25,C.light);
 rect(s,74,398,690,1,'#62676A');
 txt(s,'Several instruments and a range',74,432,690,42,23,C.blue,true);
 txt(s,'“Play flute one and cello\nfrom measure eight to twelve.”',74,480,690,110,32,C.white,true);
 await pic(s,'demo/OSC-message-in-max.png',837,176,355,472,'contain','Max console showing single and multiple stem commands');
 txt(s,'OSC messages received in Max',833,659,380,30,18,C.light);
 notes(s,'Voice-selected playback',"Voice-selected playback was still future work in the previous report. It now supports a single instrument, several instruments, and an explicit measure range. For example, play violin one uses the measure captured when recording begins. Play flute one and cello from measure eight to twelve specifies both the instruments and the range. The screenshot shows Max receiving single-stem and multistem commands during development. Full Mix still uses its separate stereo player. Selected stems share a signal-rate playhead, which keeps them aligned. This currently works with the prepared sixteen-measure piece and its registered page map.",['Documentation/Process-Report/LLM-Parser-Report.md','Documentation/Process-Report/Max-Playback-Current-Architecture.md','demo/OSC-message-in-max.png']);
}
// 06
{
 const s=slide('Parser revisions');
 table(s,[['Attempt','Problem observed','Current approach'],['Regex parser','Rigid phrase patterns','Keep as an error fallback'],['Rules-only prompt','Missing fields and\nwrong clarification','Decision steps with\n34 examples'],['Model-only corrections','Kept both instruments\nafter a correction','Python handles corrections\nand exclusions']],72,183,1136,366,[257,394,485],25);
 txt(s,'The parser now runs locally through Ollama with Qwen2.5:7b.',75,590,1100,42,27);
 txt(s,'Local inference replaced the API path after development hit rate limits.',75,641,1100,37,22,C.muted);
 notes(s,'Parser revisions',"The first voice parser used regular expressions. It handled fixed phrases, but it struggled with natural variation and corrections. I then tried a language model. A rules-only prompt still produced missing fields and unnecessary clarification. The current prompt uses ordered decision steps and thirty-four examples. I also found that the model did not reliably remove an earlier instrument after a self-correction, so Python now handles corrections and exclusions. I moved from the planned API path to local Ollama inference after hitting development rate limits. The deterministic parser remains an error fallback. These changes helped the recorded development cases, but they still need broader testing.",['Documentation/Process-Report/LLM-Parser-Report.md','camera/llm_parser.py','camera/voice_parser.py']);
}
// 07
{
 const s=slide('Spoken clarification');
 txt(s,'Selected measure 2',75,171,800,42,23,C.muted);
 const turns=[['Reader','“Play flute.”',C.coral],['System','“Flute one, flute two, or both?”',C.blue],['Reader','“Flute one.”',C.coral]];
 turns.forEach(([who,words,col],i)=>{
  const y=242+i*109;
  txt(s,who,75,y+5,170,42,23,col,true);
  txt(s,words,262,y,930,78,34,C.ink,i===1);
  if(i<2)rect(s,262,y+85,920,1,C.rule);
 });
 rect(s,75,593,1130,4,C.coral);
 txt(s,'The answer keeps the original measure and starts Flute 1.',75,621,1120,60,28,C.ink,true);
 notes(s,'Spoken clarification',"This is a supported example of the clarification flow. If I select measure two and say play flute, the system asks whether I mean flute one, flute two, or both. I can hold RECORD again and answer flute one. The controller keeps the original measure while it waits for that answer, so moving my finger during the conversation does not change this request. STOP clears the pending question. At present, spoken feedback is mainly for clarification and some errors. Successful playback requests print feedback in the terminal, so a complete nonvisual confirmation interface is still unfinished.",['Documentation/Process-Report/LLM-Parser-Report.md','camera/voice_mvp.py']);
}
// 08
{
 const s=slide('Recorded demonstration',true);
 await pic(s,'.presentation-build/reference/llm76.jpg',72,171,852,479,'contain','demo-video-poster');
 rect(s,72,165,852,5,C.coral);
 txt(s,'Current prototype',960,183,260,75,30,C.white,true);
 txt(s,'Measure selection\nPhysical controls\nVoice requests\nMax playback',960,292,250,200,25,C.light);
 txt(s,'Click the video to play',960,558,250,83,25,C.lime,true);
 notes(s,'Recorded demonstration',"I'll now show a recording of the current prototype. It brings together the prepared Braille score, the physical controls, voice requests and Max playback. Please listen for how the requested instruments change, and watch the button interaction alongside the score. This is a developer demonstration of the implemented pipeline. The earlier Wizard of Oz video explored proposed behavior, so I am keeping that separate from this recording. [Click the video and let it play. Resume on the next slide.]",['demo/Videos/Add-LLM-Parser.MOV','Documentation/Process-Report/LLM-Parser-Report.md']);
}
// 09
{
 const s=slide('Current evidence');
 txt(s,'31',74,182,255,133,113,C.coral,true);
 txt(s,'development cases\nreported passing',80,322,270,115,29,C.ink,true);
 txt(s,'October 12 report\nTranscript inputs, not reader trials',80,495,310,115,22,C.muted);
 rect(s,432,184,1,438,C.rule);
 txt(s,'Hardware tests',487,187,710,55,32,C.ink,true);
 txt(s,'Buttons, voice requests and the camera anchor\nwere connected in developer tests.',487,251,710,110,27);
 txt(s,'Remaining errors',487,399,710,55,32,C.ink,true);
 txt(s,'Whisper can hear “full mix” as “four mix”.\nTerminal feedback can disagree with corrected tracks.',487,463,710,118,26);
 txt(s,'Reader usability, selection accuracy and latency still need measurement.',74,654,1125,42,24,C.muted);
 notes(s,'Current evidence',"The October twelfth development report records thirty-one parser cases as passing. Those cases use transcript inputs, so this number does not measure speech recognition accuracy or usability with readers. The report also documents hardware tests with the buttons and then the connected camera anchor. There are still known errors. Whisper can hear full mix as four mix. After Python corrects an instrument selection, the terminal feedback can still name the earlier instrument even when playback uses the corrected track. I also still need measurements of measure-selection accuracy, response time and interaction errors. I do not yet have a formal reader evaluation.",['Documentation/Process-Report/LLM-Parser-Report.md','camera/test_llm_parser.py']);
}
// 10
{
 const s=slide('Remaining work');
 row(s,1,'Nonvisual information','Selected-measure queries, instrument information\nand silent-part feedback remain unfinished.',184);
 rect(s,260,313,925,1,C.rule);
 row(s,2,'Tracking and setup','Measure selection and page-placement tolerance\nstill need repeated trials.',348);
 rect(s,260,477,925,1,C.rule);
 row(s,3,'Study readiness','Finish task scripts and event logging.\nIdentify live features and scripted demonstrations.',512);
 notes(s,'Remaining work',"Three areas remain before a useful evaluation. First, the reader still needs more nonvisual information. Position queries, instrument information and silent-part feedback are unfinished. Second, I need repeated trials of measure selection and page placement, including recovery when the setup changes. Third, I need consistent study tasks and event logs. The protocol distinguishes live features from scripted demonstrations, and I will keep that distinction in the study records. Reading-behavior inference also remains outside the current implementation. My immediate focus is the interaction and the evidence needed to evaluate it.",['Documentation/Process-Report/Braille-Score-Design-Review1.md','Documentation/Process-Report/LLM-Parser-Report.md','Research Study/Research Protocol.docx']);
}
// 11
{
 const s=slide('Study plan');
 txt(s,'Research protocol drafted on October 14',74,170,1120,45,26,C.muted);
 table(s,[['Study','Comparison or task','Evidence to collect'],['Usability','Touch and voice tasks','Success, errors and recovery'],['Input methods','Buttons versus gestures','Unintended activation,\ninterruption and preference'],['Interaction rules','Fixed defaults versus\nuser customization','Understanding, settings use\nand perceived effort']],72,240,1136,343,[232,430,474],24);
 txt(s,'Planned comparisons use the same participants with counterbalanced order.',75,620,1115,59,25);
 notes(s,'Study plan',"I drafted a protocol with three related studies. The first examines usability through touch and voice tasks. The second compares buttons and gestures for equivalent Play and Stop operations. The third examines fixed interaction defaults and user customization. The controlled comparisons are planned within participants, with counterbalanced order. I want to collect task outcomes, errors, interruptions, recovery behavior and participant feedback. I will only compare autonomous system performance when both conditions are implemented and checked. Proposed behaviors shown through a script will be labeled and analyzed separately. These studies are planned, and participant data collection has not started.",['Research Study/Research Protocol.docx']);
}
// 12
{
 const s=slide('Next steps',true);
 const xs=[80,480,880];
 const heads=['IRB application','Controlled study','More data'];
 const bodies=['Finalize the protocol\nand consent materials.\nSubmit for review.','After approval, compare\nbuttons and gestures,\nthen interaction defaults.','Collect task logs,\nrepeated trials and\nreader feedback.'];
 for(let i=0;i<3;i++){
  txt(s,String(i+1).padStart(2,'0'),xs[i],202,285,85,66,[C.coral,C.lime,C.blue][i],true);
  txt(s,heads[i],xs[i],322,320,82,31,C.white,true);
  txt(s,bodies[i],xs[i],437,315,145,26,C.light);
 }
 rect(s,80,614,1120,1,'#62676A');
 txt(s,'Participant recruitment and data collection will follow written IRB approval.',80,640,1120,46,23,C.light);
 notes(s,'Next steps',"My next steps are the IRB application, a controlled study, and collecting more data. First, I need to finalize the research protocol and consent materials and submit them for review. Recruitment and participant data collection will begin after written IRB approval. Then I plan to compare buttons and gestures under equivalent tasks, followed by comparisons of interaction defaults and customization. I also want more repeated trials, system logs and reader feedback. That evidence should help me decide what to keep, what needs revision, and whether later work on reading behavior is justified.",['Research Study/Research Protocol.docx']);
}
// 13
{
 const s=slide('Questions for discussion');
 txt(s,'1',80,193,85,98,80,C.coral,true);
 txt(s,'What would make the input comparison fair?',211,192,980,85,34,C.ink,true);
 txt(s,'Equivalent tasks, enough practice and comparable feedback\nfor buttons and gestures.',211,294,970,99,27,C.muted);
 rect(s,211,426,970,1,C.rule);
 txt(s,'2',80,475,85,98,80,C.blue,true);
 txt(s,'Which feedback is needed before reader testing?',211,475,985,86,34,C.ink,true);
 txt(s,'Selected measure, available parts or a warning about silence?',211,578,970,77,27,C.muted);
 notes(s,'Questions for discussion',"I would appreciate feedback on two questions. First, what would make the comparison between buttons and gestures fair? I want both methods to have equivalent tasks, enough practice and comparable feedback. Second, which nonvisual information should I finish before reader testing? The selected measure, available instrument parts and a warning about silence are all possible priorities. I would like to understand which would most help a reader complete the tasks and recover from errors. Thank you. I'm happy to discuss the current prototype or the study plan.",['Research Study/Research Protocol.docx','Documentation/Process-Report/Braille-Score-Design-Review1.md']);
}

await fs.writeFile(path.join(build,'scripts.json'),JSON.stringify(scripts,null,2));
for(let i=0;i<p.slides.items.length;i++){
 const s=p.slides.items[i];
 const b=await p.export({slide:s,format:'png',scale:1});
 await fs.writeFile(path.join(build,'previews',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await b.arrayBuffer()));
 console.log(`Rendered ${i+1}`);
}
await (await PresentationFile.exportPptx(p)).save(path.join(build,'draft.pptx'));
await fs.writeFile(path.join(build,'font-policy.json'),JSON.stringify({basis:'reference',families:[font],referencePath:'/Users/zhaojinlan/Documents/DocumentMe/Berklee Study/7th Semester/MTEC-498/Progress Report 1/What_the_Fingers_Hear_Progress_Report_1 .pptx'}));
console.log('Draft exported with '+p.slides.items.length+' slides');
