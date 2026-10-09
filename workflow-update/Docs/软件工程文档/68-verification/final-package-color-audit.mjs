import {build} from 'esbuild';
import {readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const output=resolve('.local/tests/final-color-archive-reader.mjs');
await build({stdin:{contents:"export {readProject} from './apps/desktop/main/archive';",resolveDir:process.cwd()},bundle:true,platform:'node',format:'esm',outfile:output});
const {readProject}=await import(pathToFileURL(output)),release=JSON.parse(await readFile('release/latest.json','utf8'));
for(const [name,reportFile] of [['jpeg','real-artwork-cut.json'],['blue-white','real-blue-white-cut.json']]){
 const report=JSON.parse(await readFile('test-results/'+reportFile,'utf8'));assert(report.passed);assert.equal(report.build.executable,release.executable);
 const archive=resolve(report.directory,'real-artwork.fpcad'),project=await readProject(archive);assert(project.surfaceRun?.accepted);assert.equal(project.pieces.length,report.pieces);
 const sourceFile=resolve('.local/tests/final-color-'+name+'-project.json'),runFile=resolve('.local/tests/final-color-'+name+'-run.json'),resultFile=resolve('test-results/final-cut-color-'+name+'.json');
 await writeFile(sourceFile,JSON.stringify(project));await writeFile(runFile,JSON.stringify({run:project.surfaceRun}));
 const r=spawnSync(process.execPath,['.local/tests/design-cut/independent-final-trim-colors.mjs',sourceFile,runFile,resultFile],{encoding:'utf8',windowsHide:true,maxBuffer:1024*1024});assert.equal(r.status,0,r.stderr||r.stdout);
 const result=JSON.parse(await readFile(resultFile,'utf8'));Object.assign(result,{packageBuildHash:release.buildHash,archiveSha256:createHash('sha256').update(await readFile(archive)).digest('hex'),source:'Actual saved project produced by the final packaged public workflow',sampling:'Every actual trim triangle centroid against ordered original marking fragments; near-boundary allowance 1e-6 mm. Independent of the cutting material labels.'});await writeFile(resultFile,JSON.stringify(result,null,2));console.log(name,JSON.stringify(result.stats));
}
