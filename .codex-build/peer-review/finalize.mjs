import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {finalizePresentation} from '/Users/zhaojinlan/.codex/plugins/cache/openai-primary-runtime/presentations/26.1025.11240/skills/presentations/container_tools/artifact_tool_utils.mjs';
const root='/Users/zhaojinlan/Desktop/Lann Projects/What-the-fingers-hear';
const skill='/Users/zhaojinlan/.codex/plugins/cache/openai-primary-runtime/presentations/26.1025.11240/skills/presentations';
const source='/Users/zhaojinlan/Documents/GitHub/MTEC-498-Capstone/Homework/PeerReview/presentation.pptx';
const result=await finalizePresentation({
 workspaceDir:root,
 candidatePath:`${root}/.codex-build/peer-review/candidate.pptx`,
 finalPath:`${root}/outputs/peer-review/presentation_revised.pptx`,
 pythonExecutable:'/Users/zhaojinlan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[2,6,11].flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeTableOwnerSlides:[2,6,11],
 requiredNativeChartOwnerSlides:[],
 fontPolicy:{basis:'reference',families:['Helvetica Neue'],referencePath:source,referenceSha256:createHash('sha256').update(await fs.readFile(source)).digest('hex')},
 verifyArtifactToolImport:true,
 receiptPath:`${root}/.codex-build/peer-review/validation.json`
});
console.log(JSON.stringify(result,null,2));
