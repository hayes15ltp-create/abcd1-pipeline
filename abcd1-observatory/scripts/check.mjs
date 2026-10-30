import {readFile,access} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';
const root=path.resolve(fileURLToPath(new URL('../dist',import.meta.url)));
const data=JSON.parse(await readFile(path.join(root,'data/project.json'),'utf8'));
assert.equal(data.cohort.requiredClassification,'Pathogenic');
assert.equal(data.cohort.imported,false);assert.equal(data.cohort.variantCount,null);
assert.equal(data.automation.active,false);assert.equal(data.runs.length,0);
assert.equal(new Set(data.workstreams.map(s=>s.id)).size,data.workstreams.length);
assert.equal(new Set(data.milestones.map(s=>s.id)).size,data.milestones.length);
const html=await readFile(path.join(root,'index.html'),'utf8');
for(const page of ['overview','workstreams','roadmap','registry','tools','resources'])assert(html.includes(`id="page-${page}"`));
for(const local of ['assets/app.js','assets/style.css','assets/mark.svg','documents/research-specification.md','documents/tool-stack.md'])await access(path.join(root,local));
for(const item of [...data.tools,...data.sources])assert(new URL(item.url).protocol==='https:');
for(const doc of ['documents/research-specification.md','documents/tool-stack.md']){
  const text=await readFile(path.join(root,doc),'utf8');
  assert(!/C:\\Users\\|Bearer\s+[A-Za-z0-9_-]{20}|sk-[A-Za-z0-9]{20}/i.test(text),'Unexpected private path or credential-like string');
}
console.log(`Snapshot checks passed: ${data.workstreams.length} workstreams, ${data.tools.length} tool groups, ${data.milestones.length} milestones, zero published research runs.`);
