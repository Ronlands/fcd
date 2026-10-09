import type {IllustrationRegion} from './illustration';

/** Experimental conservative ownership refinement. Material labels remain a
 * complete partition; only confidently located internal color transitions can
 * move. No coordinate averaging, region closing or contour smoothing occurs. */
export function refineImageEdgeOwnership(width:number,height:number,rgba:Uint8Array,regions:IllustrationRegion[]){
 const size=width*height;if(!Number.isInteger(width)||!Number.isInteger(height)||width<1||height<1||size>4096*4096||rgba.length!==size*4)throw Error('IMAGE_LIMIT');
 const labels=new Int32Array(size).fill(-1);regions.forEach((r,id)=>r.indices.forEach(i=>{labels[i]=id;}));
 const initial=labels.slice(),chroma=new Float32Array(size*3),palette=regions.map(r=>{const rgb=[1,3,5].map(i=>parseInt(r.color.slice(i,i+2),16)),sum=rgb.reduce((a,b)=>a+b,0)||1;return {rgb:rgb.map(v=>v/sum),dark:Math.max(...rgb)<80};});
 for(let i=0;i<size;i++){const sum=rgba[i*4]+rgba[i*4+1]+rgba[i*4+2]+1;for(let c=0;c<3;c++)chroma[i*3+c]=rgba[i*4+c]/sum;}
 const targets=new Int32Array(size).fill(-1),scores=new Float32Array(size);
 let supportedEdges=0;
 function probe(i:number,j:number,stride:number,coordinate:number,limit:number){
  const a=initial[i],b=initial[j];if(a<0||b<0||a===b||palette[a].dark||palette[b].dark||coordinate<7||coordinate+7>=limit)return;
  const delta=palette[a].rgb.map((v,c)=>v-palette[b].rgb[c]),norm=Math.hypot(...delta);if(norm<.12)return;const dir=delta.map(v=>v/norm);
  // Confirm broad support on both sides. A third owner, exterior, an ink
  // separator, or a narrow tip excludes the search corridor entirely.
  for(let t=-6;t<=7;t++){const owner=initial[i+t*stride];if(owner!==a&&owner!==b)return;}
  if(initial[i-6*stride]!==a||initial[i+7*stride]!==b)return;
  const value=(t:number)=>dir.reduce((s,d,c)=>s+d*chroma[(i+t*stride)*3+c],0),gradient=(t:number)=>(value(t-2)+2*value(t-1)-2*value(t+1)-value(t+2))/8;
  const contrast=value(-5)-value(6);if(contrast<.08)return;
  let peak=0,position=0;for(let t=-3;t<=4;t++){const g=gradient(t);if(g>peak){peak=g;position=t;}}
  if(peak<.025||peak<contrast*.18||position===-3||position===4)return;
  const l=gradient(position-1),r=gradient(position+1),denominator=2*(l-2*peak+r),offset=denominator?(l-r)/denominator:0;
  if(!Number.isFinite(offset)||Math.abs(offset)>.6)return;
  const edge=position+.5+offset,original=1;if(Math.abs(edge-original)>3.5)return;supportedEdges++;
  for(let t=-3;t<=4;t++){const p=i+t*stride,target=t+.5<edge?a:b;if(initial[p]===target)continue;if(peak>scores[p]){scores[p]=peak;targets[p]=target;}}
 }
 for(let y=0;y<height;y++)for(let x=0;x<width;x++){const i=y*width+x;if(x+1<width&&initial[i]!==initial[i+1])probe(i,i+1,1,x,width);if(y+1<height&&initial[i]!==initial[i+width])probe(i,i+width,width,y,height);}
 const offsets=[[-1,-1],[0,-1],[1,-1],[-1,0],[1,0],[-1,1],[0,1],[1,1]];
 function localComponents(i:number,owner:number,equal:boolean,eight:boolean){
  const active=offsets.map(([dx,dy])=>(labels[i+dy*width+dx]===owner)===equal),seen=new Set<number>();let count=0;
  for(let a=0;a<8;a++){if(!active[a]||seen.has(a))continue;count++;const queue=[a];seen.add(a);for(let q=0;q<queue.length;q++){const p=queue[q];for(let b=0;b<8;b++){const dx=Math.abs(offsets[p][0]-offsets[b][0]),dy=Math.abs(offsets[p][1]-offsets[b][1]);if(active[b]&&!seen.has(b)&&(eight?Math.max(dx,dy)===1:dx+dy===1)){seen.add(b);queue.push(b);}}}}
  return count;
 }
 const proposals=Array.from(targets.keys()).filter(i=>targets[i]>=0).sort((a,b)=>scores[b]-scores[a]);let movedPixels=0;
 for(let pass=0;pass<5;pass++){let changed=0;for(const i of proposals){const a=labels[i],b=targets[i];if(a===b)continue;const x=i%width,y=Math.floor(i/width);if(x<1||x>=width-1||y<1||y>=height-1)continue;
   // Four-connected regions and eight-connected complements must both retain
   // one local component. These simple-point tests preserve holes, components
   // and junctions throughout sequential ownership changes.
   if(![i-1,i+1,i-width,i+width].some(n=>labels[n]===b))continue;
   if(localComponents(i,a,true,false)!==1||localComponents(i,a,false,true)!==1||localComponents(i,b,true,false)!==1||localComponents(i,b,false,true)!==1)continue;
   labels[i]=b;changed++;movedPixels++;
  }if(!changed)break;
 }
 const indices=regions.map(()=>[] as number[]);for(let i=0;i<size;i++)if(labels[i]>=0)indices[labels[i]].push(i);
 return {regions:regions.map((r,id)=>({...r,indices:indices[id]})),labels,report:{supportedEdges,movedPixels}};
}
