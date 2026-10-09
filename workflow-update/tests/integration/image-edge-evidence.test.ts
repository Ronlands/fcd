import {beforeAll,expect,it,vi} from 'vitest';
import sharp from 'sharp';
import {splitReferences} from '../../apps/desktop/main/automatic-reference';
import {edgeArcPoints} from '../../packages/pattern/edit';
import {pigmentFamily} from '../../packages/reference/illustration';
import type {IllustrationRegion} from '../../packages/reference/illustration';
import {refineImageEdgeOwnership} from '../../packages/reference/image-edge-evidence';
import * as imageEdges from '../../packages/reference/image-edge-evidence';
import {traceMask} from '../../apps/desktop/main/reference-segmentation';
import {recoverSharedContours} from '../../packages/reference/shared-contour';
import type {Piece,Reference} from '../../packages/schema/index';

let rgba:Uint8Array,width:number,regions:ReturnType<typeof splitReferences>['regions'],refinedPieces:Piece[];
beforeAll(async()=>{
 const original=await sharp('tests/fixtures/character-front-back.jpg').ensureAlpha().raw().toBuffer({resolveWithObject:true});
 rgba=new Uint8Array(original.data);width=original.info.width;
 const references:Reference[]=[];
 for(const [view,left,w] of [['front',609,666],['back',0,609]] as const){
  const png=await sharp('tests/fixtures/character-front-back.jpg').extract({left,top:0,width:w,height:750}).png().toBuffer();
  references.push({id:view,name:view,view,width:w,height:750,png:'data:image/png;base64,'+png.toString('base64'),resources:{} as Reference['resources'],calibration:{a:{x:0,y:750},b:{x:0,y:0},distanceMm:750},calibrationMode:'manual'});
 }
 let captured:{rgba:Uint8Array;regions:IllustrationRegion[]}|undefined;
 const refine=refineImageEdgeOwnership;
 const observe=vi.spyOn(imageEdges,'refineImageEdgeOwnership').mockImplementation((w,h,pixels,input)=>{if(w===666&&h===750)captured={rgba:pixels,regions:input};return refine(w,h,pixels,input);});
 try{regions=splitReferences(references,750,6,true).regions;}finally{observe.mockRestore();}
 expect(captured).toBeDefined();
 const corrected=refineImageEdgeOwnership(666,750,captured!.rgba,captured!.regions);
 const originals=corrected.regions.map(r=>{const mask=new Uint8Array(666*750);r.indices.forEach(i=>{mask[i]=1;});return traceMask(666,750,mask,{a:{x:0,y:750},b:{x:0,y:0},distanceMm:750},666,750,r.color,true).piece;});
 refinedPieces=recoverSharedContours(originals,.8,()=>crypto.randomUUID()).pieces;
},120000);

function crossings(piece:Piece,y:number){
 const ring=piece.nodes.flatMap(n=>edgeArcPoints(piece,n.id).slice(0,-1)).map(p=>({x:p.xMm+609,y:750-p.yMm})),xs:number[]=[];
 for(let i=0;i<ring.length;i++){const a=ring[i],b=ring[(i+1)%ring.length];if((a.y<=y&&b.y>y)||(b.y<=y&&a.y>y))xs.push(a.x+(y-a.y)*(b.x-a.x)/(b.y-a.y));}
 return xs;
}
function yellowChroma(x:number,y:number){const i=(y*width+x)*4,r=rgba[i],g=rgba[i+1],b=rgba[i+2];return (r+g-2*b)/(r+g+b+1);}
function descendingGradient(x:number,y:number){return (yellowChroma(x-2,y)+2*yellowChroma(x-1,y)-2*yellowChroma(x+1,y)-yellowChroma(x+2,y))/8;}

function thighDistances(pieces:Piece[]){
 // This is the imageLEFT front thigh shown by the user, not the opposite
 // x839..1009 fixture used by the earlier contour-to-mask regression.
 const candidates=pieces.filter(p=>pigmentFamily(p.color!)===2);
 const thigh=candidates.find(p=>crossings(p,530.5).some(x=>x>775&&x<798));expect(thigh).toBeDefined();
 const distances:number[]=[];
 for(let y=500;y<=570;y++){
  // Fixed image-space search corridor selected from the original image;
  // it is independent of the reconstructed contour and pigment mask.
  const center=y<540?791-(y-500)*.32:780-(y-540)*.55;
  let peak=-Infinity,px=0;for(let x=Math.floor(center)-6;x<=Math.ceil(center)+6;x++){const d=descendingGradient(x,y);if(d>peak){peak=d;px=x;}}
  expect(peak).toBeGreaterThan(.04);
  const a=descendingGradient(px-1,y),c=descendingGradient(px+1,y),offset=(a-c)/(2*(a-2*peak+c));
  const observed=px+.5+(Number.isFinite(offset)&&Math.abs(offset)<.6?offset:0),xs=crossings(thigh!,y+.5);
  expect(xs.length).toBeGreaterThanOrEqual(2);distances.push(Math.abs(Math.max(...xs)-observed));
 }
 distances.sort((a,b)=>a-b);
 return distances;
}
it('the screenshot yellow thigh follows the original JPEG pigment edge rather than only its classified mask',()=>{
 const distances=thighDistances(regions.filter(r=>r.view==='front').map(r=>r.piece));
 // Permit JPEG ridge variation, but reject multi-pixel systematic drift.
 expect(distances[Math.floor(distances.length*.95)]).toBeLessThanOrEqual(1.8);
 expect(distances.at(-1)).toBeLessThanOrEqual(2.5);
});
it('image-supported ownership refinement removes the actual multi-pixel image-edge drift through the same joint contour pipeline',()=>{
 const distances=thighDistances(refinedPieces);
 expect(distances[Math.floor(distances.length*.95)]).toBeLessThanOrEqual(1.8);expect(distances.at(-1)).toBeLessThanOrEqual(2.5);
});

const colors=['#ede7ea','#f9e33c','#08060a'];
function scene(w:number,h:number,ownership:(x:number,y:number)=>number,image:(x:number,y:number)=>number[]){
 const pixels=new Uint8Array(w*h*4),groups=colors.map((color):IllustrationRegion=>({color,part:'unknown',side:'unknown',indices:[],confidence:0}));
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){const i=y*w+x,owner=ownership(x+.5,y+.5);if(owner>=0)groups[owner].indices.push(i);pixels.set([...image(x+.5,y+.5),255],i*4);}
 return {pixels,groups};
}
function componentCount(w:number,h:number,ids:number[],eight=false){
 const remaining=new Set(ids);let count=0;while(remaining.size){const first=remaining.values().next().value!;remaining.delete(first);count++;const queue=[first];for(let q=0;q<queue.length;q++){const i=queue[q],x=i%w,y=Math.floor(i/w);for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){if(!dx&&!dy||!eight&&Math.abs(dx)+Math.abs(dy)!==1||x+dx<0||x+dx>=w||y+dy<0||y+dy>=h)continue;const n=(y+dy)*w+x+dx;if(remaining.delete(n))queue.push(n);}}}return count;
}
const rgb=(id:number)=>[1,3,5].map(i=>parseInt(colors[id].slice(i,i+2),16));
it('refinement keeps foreground partition, components, enclosed holes and complete thin dark tips',()=>{
 const w=80,h=70,dark=(x:number,y:number)=>x>=39&&x<42&&y>=4&&y<18,hole=(x:number,y:number)=>(x-40)**2+(y-37)**2<49;
 const owner=(x:number,y:number)=>x<4||x>=76||y<3||y>=67?-1:dark(x,y)?2:hole(x,y)?0:x>=20&&x<60&&y>=12&&y<61?1:0;
 const actual=(x:number,y:number)=>dark(x,y)?2:hole(x,y)?0:x>=23&&x<57&&y>=12&&y<61?1:0;
 const {pixels,groups}=scene(w,h,owner,(x,y)=>rgb(actual(x,y))),result=refineImageEdgeOwnership(w,h,pixels,groups);
 expect(result.report.movedPixels).toBeGreaterThan(0);
 expect(result.regions[2].indices).toEqual(groups[2].indices);
 const before=groups.flatMap(r=>r.indices).sort((a,b)=>a-b),after=result.regions.flatMap(r=>r.indices).sort((a,b)=>a-b);
 expect(after).toEqual(before);expect(new Set(after).size).toBe(after.length);
 for(let id=0;id<groups.length;id++){
  expect(componentCount(w,h,result.regions[id].indices)).toBe(componentCount(w,h,groups[id].indices));
  const complement=(ids:number[])=>{const occupied=new Set(ids);return Array.from({length:w*h},(_,i)=>i).filter(i=>!occupied.has(i));};
  expect(componentCount(w,h,complement(result.regions[id].indices),true)).toBe(componentCount(w,h,complement(groups[id].indices),true));
 }
});
it.each([1,2,3])('native-scale %s sharp diagonal edges and narrow stripes stay stationary',scale=>{
 const w=80*scale,h=60*scale,owner=(x:number,y:number)=>x>20*scale+y*.3&&x<60*scale?1:0;
 const {pixels,groups}=scene(w,h,owner,(x,y)=>rgb(owner(x,y))),result=refineImageEdgeOwnership(w,h,pixels,groups);
 expect(result.regions.map(r=>r.indices)).toEqual(groups.map(r=>r.indices));
 const stripe=(x:number)=>x>=38*scale&&x<40*scale?1:0,thin=scene(w,h,(x)=>stripe(x),(x)=>rgb(stripe(x)));
 expect(refineImageEdgeOwnership(w,h,thin.pixels,thin.groups).regions.map(r=>r.indices)).toEqual(thin.groups.map(r=>r.indices));
});
it.each([1,2,3])('native-scale %s biased diagonal ownership follows antialiased original color transitions',scale=>{
 const w=80*scale,h=60*scale,boundary=(y:number)=>25*scale+y*.33;
 const owner=(x:number,y:number)=>x>=boundary(y)+2?1:0,neutral=rgb(0),yellow=rgb(1);
 const {pixels,groups}=scene(w,h,owner,(x,y)=>{const coverage=Math.max(0,Math.min(1,.5+(x-boundary(y))/2));return neutral.map((v,c)=>Math.round(v+(yellow[c]-v)*coverage));});
 const result=refineImageEdgeOwnership(w,h,pixels,groups);expect(result.report.movedPixels).toBeGreaterThan(h/2);
 for(let y=10;y<h-10;y++){
  const row=result.regions[1].indices.filter(i=>Math.floor(i/w)===y),first=Math.min(...row)%w;
  expect(Math.abs(first-boundary(y+.5))).toBeLessThanOrEqual(.85);
 }
});
