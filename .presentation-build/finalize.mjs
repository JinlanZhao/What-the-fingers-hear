import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { pathToFileURL } from 'node:url';
process.env.RUNTIME_NODE_MODULES='/Users/zhaojinlan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';

const root='/Users/zhaojinlan/Desktop/Lann Projects/What-the-fingers-hear';
const skill='/Users/zhaojinlan/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const fp=JSON.parse(await fs.readFile(path.join(root,'.presentation-build/font-policy.json'),'utf8'));
fp.referenceSha256=createHash('sha256').update(await fs.readFile(fp.referencePath)).digest('hex');
const final=path.join(root,'output/presentations/What_the_Fingers_Hear_Progress_Report_2.pptx');
const result=await finalizePresentation({
 workspaceDir:root,
 candidatePath:path.join(root,'.presentation-build/powerpoint-normalized.pptx'),
 finalPath:final,
 pythonExecutable:'/Users/zhaojinlan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[2,6,11].flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeTableOwnerSlides:[2,6,11],
 requiredNativeChartOwnerSlides:[],
 fontPolicy:fp,
 verifyArtifactToolImport:true,
 receiptPath:path.join(root,'.presentation-build/validation-native.json')
});
console.log(JSON.stringify(result));
