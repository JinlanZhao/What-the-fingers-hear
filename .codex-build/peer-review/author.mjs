import fs from 'node:fs/promises';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const root = '/Users/zhaojinlan/Desktop/Lann Projects/What-the-fingers-hear';
const build = `${root}/.codex-build/peer-review`;
const p = Presentation.create({slideSize:{width:1280,height:720}});
const c = {paper:'#FFFDF8',ink:'#171A1D',muted:'#7C776F',coral:'#F06C5B',blue:'#6AB7D6',lime:'#CFEA79',line:'#D8D1C5'};

function text(slide, name, value, x,y,w,h,size=26,color=c.ink,bold=false) {
  const s=slide.shapes.add({name,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  s.text=value;
  s.text.style={fontSize:size,typeface:'Helvetica Neue',color,bold,verticalAlignment:'top',alignment:'left',autoFit:'none',insets:0};
  return s;
}
function rule(slide,x,y,w,color=c.line,h=1){
  slide.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill:color,line:{fill:'none',width:0}});
}
function slide(title,num,dark=false){
  const s=p.slides.add();s.background.fill=dark?c.ink:c.paper;
  text(s,'title',title,72,48,1100,72,45,dark?'#FFFFFF':c.ink,true);
  rule(s,72,126,54,c.coral,5);
  text(s,'page-number',String(num).padStart(2,'0'),1190,45,45,30,17,dark?c.line:c.muted,true);
  return s;
}

// New slide 10: status and sequence, using the original deck's column rhythm.
{
 const s=slide('IRB progress',10,true);
 text(s,'status','CITI training in progress · IRB application in preparation',76,168,1120,48,27,c.lime,true);
 const cols=[
   ['01','CITI training','Complete the current\ntraining course.',c.coral],
   ['02','Application','Prepare the protocol,\nconsent materials\nand study tasks.',c.lime],
   ['03','Three studies','Begin recruitment and\nparticipant data collection\nafter written approval.',c.blue]
 ];
 cols.forEach(([n,t,b,col],i)=>{const x=80+i*400;text(s,`step-${i}`,n,x,260,100,70,62,col,true);text(s,`heading-${i}`,t,x,360,350,54,32,'#FFFFFF',true);text(s,`body-${i}`,b,x,440,350,125,27,c.line);});
 rule(s,80,614,1120,'#5D6264');
 text(s,'takeaway','During IRB review: develop interactions for reading and ensemble listening.',80,644,1120,42,25,c.line);
}

// New slide 13: distinguish the saved audio state from paper reorientation.
{
 const s=slide('Returning to the reading position',13);
 text(s,'scenario','Planned interaction · Violin, measure 5',76,172,1120,36,23,c.muted);
 text(s,'command','“Remember here.”   “Play cello.”   “Go back.”',76,230,1120,66,35,c.ink,true);
 rule(s,76,320,1124);
 text(s,'audio-heading','Playback state',76,354,500,50,31,c.ink,true);
 text(s,'audio-body','Save the piece, part and range.\nRestore the selected parts\nand playback position.',76,417,500,135,27);
 text(s,'paper-heading','Position on paper',670,354,530,50,31,c.ink,true);
 text(s,'paper-body','Save the page and measure.\nGive spoken cues to find the spot.\nExplore optional audio navigation.',670,417,530,135,27);
 rule(s,76,586,1124,c.coral,4);
 text(s,'takeaway','Page Map: measures 1 and 16 continue across pages. Save the continuation.',76,613,1124,65,25,c.ink,true);
}

// New slide 14: three concrete states and their actionable feedback.
{
 const s=slide('Silence and instrument entry',14);
 text(s,'context','Planned feedback · Different states need different responses',76,164,1120,36,23,c.muted);
 const rows=[
  ['Part is resting','“Flute one rests here. Next entry: measure eight.”',c.coral],
  ['Request failed','“Please repeat the instrument request.”',c.blue],
  ['Position unknown','“Steady the page, or say a measure number.”',c.coral]
 ];
 rows.forEach(([a,b,col],i)=>{const y=226+i*93;text(s,`state-${i}`,a,76,y,300,60,27,col,true);text(s,`feedback-${i}`,b,404,y,800,70,27);if(i<2)rule(s,404,y+74,796);});
 text(s,'offer','“Hear the two measures before the flute enters?”',76,522,1124,65,31,c.ink,true);
 rule(s,76,602,1124,c.coral,4);
 text(s,'data-source','MusicXML supplies rests, active instruments and the next entry.',76,630,1124,46,25,c.ink,true);
}

// New slide 15: preserve one selection while comparing ensemble layers.
{
 const s=slide('Comparing parts in the same passage',15,true);
 text(s,'context','Planned interaction · Keep the same measure range',76,166,1120,40,25,c.line);
 const steps=[['01','My part','“Play my part.”',c.coral],['02','Add cello','“Add cello.”',c.lime],['03','Full ensemble','“Play the Full Mix.”',c.blue]];
 steps.forEach(([n,t,b,col],i)=>{const x=80+i*400;text(s,`number-${i}`,n,x,253,100,75,62,col,true);text(s,`heading-${i}`,t,x,361,360,50,31,'#FFFFFF',true);text(s,`command-${i}`,b,x,433,360,72,28,c.line);});
 text(s,'restore','“Restore the previous combination.”',80,539,1120,60,34,c.lime,true);
 rule(s,80,614,1120,'#5D6264');
 text(s,'purpose','Compare shared rhythms, musical responses and the melody in context.',80,644,1120,43,25,c.line);
}

// New slide 16: later directions, kept secondary to the three priorities.
{
 const s=slide('Further interaction directions',16);
 const rows=[
  ['04','Practice loop','Lock the selection. Hear a model, wait and repeat.\nUser-set interval, count-in and immediate Stop.',c.coral],
  ['05','Voice annotations','Save the original recording by piece, part and measure.\nChoose query, arrival cue or pre-practice review.',c.blue],
  ['06','Independent setup','Announce page and tracking status. Give recovery cues.\nAllow a spoken measure number to continue.',c.coral]
 ];
 rows.forEach(([n,t,b,col],i)=>{const y=188+i*145;text(s,`number-${i}`,n,80,y,105,72,54,col,true);text(s,`heading-${i}`,t,260,y+5,335,90,30,c.ink,true);text(s,`body-${i}`,b,610,y+6,590,108,25);if(i<2)rule(s,260,y+124,940);});
 text(s,'source','Practice reference: Amber Sound Touch, “Memorising music”',76,656,1124,32,19,c.muted);
}

const data=JSON.parse(await fs.readFile(`${build}/content.json`,'utf8'));
for(const [i,n] of [9,12,13,14,15].entries()) p.slides.items[i].speakerNotes.text=data.notes[n].script;
await (await PresentationFile.exportPptx(p)).save(`${build}/new-slides.pptx`);
for (let i=0;i<p.slides.items.length;i++) {
 const b=await p.export({slide:p.slides.items[i],format:'png',scale:1});
 await fs.mkdir(`${build}/new-render`,{recursive:true});
 await fs.writeFile(`${build}/new-render/slide-${i+1}.png`,new Uint8Array(await b.arrayBuffer()));
}
console.log(JSON.stringify({newSlides:p.slides.items.length}));
