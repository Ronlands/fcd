import {beforeAll,expect,it} from 'vitest';
import sharp from 'sharp';
import {splitReferences} from '../../apps/desktop/main/automatic-reference';
import {edgeArcPoints} from '../../packages/pattern/edit';
import {pigmentFamily} from '../../packages/reference/illustration';
import type {Piece,Reference} from '../../packages/schema/index';

let rgba:Uint8Array,width:number,regions:ReturnType<typeof splitReferences>['regions'];
beforeAll(async()=>{
 const original=await sharp('tests/fixtures/character-front-back.jpg').ensureAlpha().raw().toBuffer({resolveWithObject:true});
 rgba=new Uint8Array(original.data);width=original.info.width;
 const references:Reference[]=[];
 for(const [view,left,w] of [['front',609,666],['back',0,609]] as const){
  const png=await sharp('tests/fixtures/character-front-back.jpg').extract({left,top:0,width:w,height:750}).png().toBuffer();
  references.push({id:view,name:view,view,width:w,height:750,png:'data:image/png;base64,'+png.toString('base64'),resources:{} as Reference['resources'],calibration:{a:{x:0,y:750},b:{x:0,y:0},distanceMm:750},calibrationMode:'manual'});
 }
 regions=splitReferences(references,750,6,true).regions;
},120000);

function crossings(piece:Piece,y:number){
 const ring=piece.nodes.flatMap(n=>edgeArcPoints(piece,n.id).slice(0,-1)).map(p=>({x:p.xMm+609,y:750-p.yMm})),xs:number[]=[];
 for(let i=0;i<ring.length;i++){const a=ring[i],b=ring[(i+1)%ring.length];if((a.y<=y&&b.y>y)||(b.y<=y&&a.y>y))xs.push(a.x+(y-a.y)*(b.x-a.x)/(b.y-a.y));}
 return xs;
}
function yellowChroma(x:number,y:number){const i=(y*width+x)*4,r=rgba[i],g=rgba[i+1],b=rgba[i+2];return (r+g-2*b)/(r+g+b+1);}
function descendingGradient(x:number,y:number){return (yellowChroma(x-2,y)+2*yellowChroma(x-1,y)-2*yellowChroma(x+1,y)-yellowChroma(x+2,y))/8;}

it('the screenshot yellow thigh follows the original JPEG pigment edge rather than only its classified mask',()=>{
 // This is the imageLEFT front thigh shown by the user, not the opposite
 // x839..1009 fixture used by the earlier contour-to-mask regression.
 const candidates=regions.filter(r=>r.view==='front'&&pigmentFamily(r.piece.color!)===2).map(r=>r.piece);
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
 // Permit JPEG ridge variation, but reject multi-pixel systematic drift.
 expect(distances[Math.floor(distances.length*.95)]).toBeLessThanOrEqual(1.8);
 expect(distances.at(-1)).toBeLessThanOrEqual(2.5);
});
