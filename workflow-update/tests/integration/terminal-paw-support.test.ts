import {it,expect} from 'vitest';
import sharp from 'sharp';
import {illustrationRegions} from '../../packages/reference/illustration';
import {terminalPawSupport} from '../../packages/reference/terminal-paw-support';
import {createHash,randomUUID} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {splitReferences} from '../../apps/desktop/main/automatic-reference';
import type {Reference} from '../../packages/schema/index';
const baseline=JSON.parse(readFileSync(new URL('../fixtures/terminal-paw-baseline.json',import.meta.url),'utf8')),sha=(v:unknown)=>createHash('sha256').update(JSON.stringify(v)).digest('hex');

it.each([['front',609,666,390,435,410,451,378,455],['back',0,609,560,265,586,244,600,269]] as const)('recovers the actual %s missing neutral hand and separate claws without swallowing its cuff',async(view,left,width,x,y,cx,cy,dx,dy)=>{
 const rgba=new Uint8Array(await sharp('tests/fixtures/character-front-back.jpg').extract({left,top:0,width,height:750}).ensureAlpha().raw().toBuffer()),r=illustrationRegions(width,750,rgba),owner=(x:number,y:number)=>r.regions.find(p=>p.indices.includes(y*width+x))!;
 expect(owner(x,y).part).toBe('paw');expect(owner(x,y).side).toBe('right');
 expect(owner(cx,cy).part).toBe('paw');expect(owner(dx,dy).part).toBe('paw');
 const cuff=view==='front'?owner(390,384):owner(551,307);expect(cuff.part).toBe('arm');expect(cuff.side).toBe('right');
 const frame=r.partBounds.find(p=>p.part==='paw'&&p.side==='right')!;expect(frame).toBeDefined();expect(frame.minX).toBeLessThanOrEqual(x);expect(frame.maxX).toBeGreaterThan(x);expect(frame.minY).toBeLessThanOrEqual(y);expect(frame.maxY).toBeGreaterThan(y);
 const all=r.regions.flatMap(p=>p.indices);expect(new Set(all).size).toBe(all.length);expect(all.length).toBe(r.foregroundPixels-r.discardedPixels);expect(r.regions.length).toBe(view==='front'?56:46);
});

function supportedHand(){
 const width=260,height=360,span=340,saturation=new Float32Array(width*height),value=new Float32Array(width*height),rect=(left:number,top:number,right:number,bottom:number,v:number)=>{const indices:number[]=[];for(let y=top;y<bottom;y++)for(let x=left;x<right;x++){const i=y*width+x;indices.push(i);saturation[i]=.1;value[i]=v;}return indices;},region=(indices:number[])=>({part:'arm' as const,side:'right' as const,confidence:.6,indices}),regions=[region(rect(185,100,215,135,.85)),region(rect(192,92,199,101,.05)),region(rect(216,110,223,119,.05))],arm:number[]=[];
 for(let y=125;y<185;y++)for(let x=165+185-y-10;x<165+185-y+10;x++)arm.push(y*width+x);
 return {width,span,top:0,head:{minX:80,minY:20,maxX:150,maxY:90},regions,saturation,value,arms:new Map<'left'|'right',number[]>([['right',arm]]),existing:new Set<'left'|'right'>()};
}
it('requires an independently supported distal neutral hand and two spatially separate compatible claw tips, without mutating material inputs',()=>{
 const input=supportedHand(),before=structuredClone(input.regions);expect(terminalPawSupport(input).map(h=>h.regionIndices)).toEqual([[0,1,2]]);expect(input.regions).toEqual(before);
 expect(terminalPawSupport({...input,regions:input.regions.slice(0,2)})).toEqual([]);
 expect(terminalPawSupport({...input,regions:input.regions.slice(1)})).toEqual([]);
 expect(terminalPawSupport({...input,existing:new Set(['right'])})).toEqual([]);
});
it.each(['head','tail','unknown','other-side'] as const)('does not infer a hand from nearby %s dark components',kind=>{
 const input=supportedHand(),regions=input.regions.map((r,i)=>i?{...r,part:kind==='other-side'?'arm' as const:kind,side:kind==='other-side'?'left' as const:r.side}:r);expect(terminalPawSupport({...input,regions})).toEqual([]);
});
it.each([['head',-70,-65],['tail',0,145]] as const)('rejects a neutral and two-tip cluster near the %s instead of borrowing an arm PCA frame',(_,dx,dy)=>{
 const input=supportedHand(),regions=input.regions.map(r=>({...r,indices:r.indices.map(i=>i+dy*input.width+dx)})),saturation=new Float32Array(input.saturation.length),value=new Float32Array(input.value.length);input.regions.forEach((r,j)=>r.indices.forEach((i,k)=>{const target=regions[j].indices[k];saturation[target]=input.saturation[i];value[target]=input.value[i];}));expect(terminalPawSupport({...input,regions,saturation,value})).toEqual([]);
});

it.each([['jpeg','character-front-back.jpg',[['front',609,666],['back',0,609]],750],['blueWhite','character-blue-white-front-back.png',[['front',0,803],['back',803,733]],1024]] as const)('%s hand metadata repair leaves every original material owner and saved contour byte-for-byte unchanged',async(name,file,crops,height)=>{
 const refs:Reference[]=[];for(const[view,left,width]of crops){const png=await sharp('tests/fixtures/'+file).extract({left,top:0,width,height}).png().toBuffer(),rgba=new Uint8Array(await sharp(png).ensureAlpha().raw().toBuffer()),r=illustrationRegions(width,height,rgba);expect(sha(r.regions.map(p=>({color:p.color,indices:p.indices})))).toBe(baseline[name][view].pixels);if(name==='blueWhite'){expect(sha(r.regions.map(({indices,...p})=>p))).toBe(baseline[name][view].metadata);expect(sha(r.partBounds)).toBe(baseline[name][view].partBounds);}refs.push({id:randomUUID(),name:view,view,width,height,png:'data:image/png;base64,'+png.toString('base64'),resources:{} as Reference['resources']});}
 const r=splitReferences(refs,1800,6,true);expect(sha(r.regions.map(({piece:p})=>({nodes:p.nodes.map(n=>[n.xMm,n.yMm]),holes:p.holes?.map(h=>h.map(n=>[n.xMm,n.yMm])),curves:p.curves?.map(c=>({start:p.nodes.findIndex(n=>n.id===c.startNodeId),end:p.nodes.findIndex(n=>n.id===c.endNodeId),c1:[c.c1.xMm,c.c1.yMm],c2:[c.c2.xMm,c.c2.yMm]}))})))).toBe(baseline[name].geometry);
},120000);
