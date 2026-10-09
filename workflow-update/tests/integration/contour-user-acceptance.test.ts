import {beforeAll,expect,it} from 'vitest';
import sharp from 'sharp';
import {randomUUID} from 'node:crypto';
import {splitReferences} from '../../apps/desktop/main/automatic-reference';
import {traceMask} from '../../apps/desktop/main/reference-segmentation';
import {recoverSharedContours} from '../../packages/reference/shared-contour';
import type {Piece,Point,Reference} from '../../packages/schema/index';

// Independent observations on the user's exact original JPEG. These open
// intervals contain the broad painted bend only; tips, fur notches, material
// junctions and pad creases are deliberately outside the acceptance interval.
// A mask-distance check alone accepted the visible alternating polygon turns.
const rois=[
 {name:'left yellow thigh broad outer bend',color:'#f9e33c',minX:776,maxX:789,minY:515,maxY:543},
 {name:'raised pink paw lower pad broad outer bend',color:'#f9b2b3',minX:635,maxX:653,minY:292,maxY:306}
];
const angle=(a:{x:number;y:number},b:{x:number;y:number})=>Math.abs(Math.atan2(a.x*b.y-a.y*b.x,a.x*b.x+a.y*b.y));
function tangentTurn(piece:Piece,id:string){
 const i=piece.nodes.findIndex(n=>n.id===id),p=piece.nodes[i],previous=piece.nodes[(i+piece.nodes.length-1)%piece.nodes.length],next=piece.nodes[(i+1)%piece.nodes.length],incoming=piece.curves?.find(c=>c.endNodeId===id),outgoing=piece.curves?.find(c=>c.startNodeId===id);
 const a=incoming?.c2??previous,b=outgoing?.c1??next;
 return angle({x:p.xMm-a.xMm,y:p.yMm-a.yMm},{x:b.xMm-p.xMm,y:b.yMm-p.yMm});
}
// Sample cubic coordinates directly, independent of production flatteners.
function sample(piece:Piece){return piece.nodes.flatMap((a,i)=>{const b=piece.nodes[(i+1)%piece.nodes.length],c=piece.curves?.find(c=>c.startNodeId===a.id&&c.endNodeId===b.id);return Array.from({length:64},(_,k)=>{const t=k/64,s=1-t;return c?{xMm:s*s*s*a.xMm+3*s*s*t*c.c1.xMm+3*s*t*t*c.c2.xMm+t*t*t*b.xMm,yMm:s*s*s*a.yMm+3*s*s*t*c.c1.yMm+3*s*t*t*c.c2.yMm+t*t*t*b.yMm}:{xMm:a.xMm+s*0+t*(b.xMm-a.xMm),yMm:a.yMm+t*(b.yMm-a.yMm)};});});}
let imported:Piece[]=[];
beforeAll(async()=>{
 const refs:Reference[]=[];
 for(const[view,left,width]of[['back',0,609],['front',609,666]] as const){const png=await sharp('tests/fixtures/character-front-back.jpg').extract({left,top:0,width,height:750}).png().toBuffer();refs.push({id:randomUUID(),name:view,view,width,height:750,png:'data:image/png;base64,'+png.toString('base64'),calibration:{a:{x:0,y:750},b:{x:0,y:0},distanceMm:750},calibrationMode:'manual',resources:{} as Reference['resources']});}
 imported=splitReferences(refs,750,12,true).regions.filter(p=>p.view==='front').map(p=>p.piece);
},20000);
it.each(rois)('original JPEG $name has no artificial sharp heading changes',roi=>{
 const candidates=imported.filter(p=>p.color===roi.color&&p.nodes.some(n=>n.xMm+609>=roi.minX&&n.xMm+609<=roi.maxX&&750-n.yMm>=roi.minY&&750-n.yMm<=roi.maxY));
 expect(candidates.length).toBeGreaterThan(0);
 const turns=candidates.flatMap(p=>p.nodes.filter(n=>n.xMm+609>=roi.minX&&n.xMm+609<=roi.maxX&&750-n.yMm>=roi.minY&&750-n.yMm<=roi.maxY).map(n=>({x:n.xMm+609,y:750-n.yMm,turn:tangentTurn(p,n.id)})));
 // 20 degrees is a geometric discontinuity bound at an observed broad bend,
 // not a demand for G1 at true corners or a prescribed cubic/node count.
 expect(Math.max(...turns.map(t=>t.turn)),JSON.stringify(turns)).toBeLessThanOrEqual(Math.PI/9);
});

it.each([.05,1,10].flatMap(scale=>[0,.37,1.1].map(rotation=>({scale,rotation}))))('recovers an analytic curved interface at scale $scale rotation $rotation without polygon heading spikes',({scale,rotation})=>{
 const width=220,height=180,masks=[new Uint8Array(width*height),new Uint8Array(width*height)];
 for(let y=10;y<170;y++)for(let x=10;x<210;x++)masks[((x+.5-110)/85)**2+((y+.5-90)/60)**2<1?0:1][y*width+x]=1;
 const raw=masks.map(mask=>traceMask(width,height,mask,{a:{x:0,y:height},b:{x:0,y:0},distanceMm:height},width,height,'#123456',true).piece),transform=(p:Point)=>({...p,xMm:1000+scale*(p.xMm*Math.cos(rotation)-p.yMm*Math.sin(rotation)),yMm:-1000+scale*(p.xMm*Math.sin(rotation)+p.yMm*Math.cos(rotation))}),originals=raw.map(p=>({...p,nodes:p.nodes.map(transform),holes:p.holes?.map(h=>h.map(transform))})),piece=recoverSharedContours(originals,.8*scale,randomUUID).pieces[0];
 const untransform=(p:{xMm:number;yMm:number})=>{const x=(p.xMm-1000)/scale,y=(p.yMm+1000)/scale;return{x:x*Math.cos(rotation)+y*Math.sin(rotation),y:-x*Math.sin(rotation)+y*Math.cos(rotation)}};
 // The known analytic boundary is an oracle distinct from classified pixels.
 const normalized=sample(piece).map(untransform);
 const radialError=normalized.map(p=>{const theta=Math.atan2((p.y-90)/60,(p.x-110)/85),x=110+85*Math.cos(theta),y=90+60*Math.sin(theta);return Math.hypot(p.x-x,p.y-y);});
 expect(Math.max(...radialError)).toBeLessThanOrEqual(1.2);
 expect(Math.max(...piece.nodes.map(n=>tangentTurn(piece,n.id)))).toBeLessThanOrEqual(Math.PI/9);
 expect(piece.holes?.length??0).toBe(0);
});
