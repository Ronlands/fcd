import {build} from 'esbuild';
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const name=process.argv[2]??'project',angle=Number(process.argv[3]??120),maxFaces=Number(process.argv[4]??400),runtime=resolve('.local/tests/cut-diagnostic-'+name+'.mjs');
await build({stdin:{contents:"export {cutPreview} from './apps/desktop/main/cut-preview';export {bindingIssues} from './apps/desktop/main/surface';export {analyze} from './apps/desktop/main/worker';export {surfaceRunSchema,markingSchema} from './packages/schema/index';",resolveDir:process.cwd()},bundle:true,platform:'node',format:'esm',outfile:runtime});
const api=await import(pathToFileURL(runtime)),p=JSON.parse(readFileSync('.local/tests/real-mapping-cut/'+name+'.json','utf8')),worker=resolve('target/release/fpcad-worker.exe');
const start=Date.now(),r=await api.cutPreview(worker,p.surface,p,{method:'arap',automaticCuts:true,colorBoundaryCuts:true,normalAngleDeg:angle,maxFacesPerPatch:maxFaces,iterations:30,optimizeCuts:true,searchPasses:3,maxPieces:500},resolve('dist/assets'));
writeFileSync('.local/tests/cut-boundary-success-'+name+'.json',JSON.stringify(r));api.surfaceRunSchema.parse(r.run);r.markings.forEach(m=>api.markingSchema.parse(m));
const candidate={...p,pieces:r.run.pieces,bindings:r.run.bindings,markings:r.markings},geometry=await api.analyze(worker,candidate),errors=geometry.flatMap(g=>g.issues.filter(i=>i.severity==='error')),bindingErrors=api.bindingIssues(candidate).filter(i=>i.severity==='error');
console.log(JSON.stringify({pieces:r.run.pieces.length,angle,maxFaces,report:r.run.colorCutReport,distortion:{mean:r.run.bindings.reduce((s,b)=>s+b.report.distortionMean,0)/r.run.bindings.length,max:Math.max(...r.run.bindings.map(b=>b.report.distortionMax)),needsReview:r.run.bindings.filter(b=>b.report.status==='needsReview').length},errors,bindingErrors,ms:Date.now()-start}));assert.deepEqual(errors,[]);assert.deepEqual(bindingErrors,[]);
const faces=new Map(p.surface.faces.map(f=>[f.id,f])),area=t=>Math.abs((t[1][0]-t[0][0])*(t[2][1]-t[0][1])-(t[2][0]-t[0][0])*(t[1][1]-t[0][1]))/2,seen=new Set();let expected=0,actual=0;
for(const b of r.run.bindings){const uv=new Map(b.report.uv.map(v=>[v.vertexId,[v.xMm,v.yMm]]));for(const id of b.report.faceIds)if(!seen.has(id)){seen.add(id);expected+=area(faces.get(id).vertices.map(id=>uv.get(id)));}if(b.trim){const xy=new Map(b.trim.vertices.map(v=>[v.id,[v.xMm,v.yMm]]));actual+=b.trim.triangles.reduce((s,t)=>s+area(t.vertices.map(id=>xy.get(id))),0);}else actual+=b.report.faceIds.reduce((s,id)=>s+area(faces.get(id).vertices.map(id=>uv.get(id))),0);}
console.log(JSON.stringify({expected,actual,delta:actual-expected}));assert(Math.abs(actual-expected)<Math.max(.001,expected*1e-8));assert(r.run.pieces.length<=500);
