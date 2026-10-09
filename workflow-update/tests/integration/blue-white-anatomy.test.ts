import {it,expect} from 'vitest';
import sharp from 'sharp';
import {illustrationRegions} from '../../packages/reference/illustration';

it('retains actual white chest and blue shoulder joint candidates without projecting a lower forearm patch onto the torso',async()=>{
 const width=803,rgba=new Uint8Array(await sharp('tests/fixtures/character-blue-white-front-back.png').extract({left:0,top:0,width,height:1024}).ensureAlpha().raw().toBuffer()),r=illustrationRegions(width,1024,rgba),owner=(x:number,y:number)=>r.regions.find(s=>s.indices.includes(y*width+x))!;
 const chest=owner(423,321);expect(chest.color).toBe('#fefaf8');expect(chest.contexts?.map(c=>c.part).sort()).toEqual(['body','head']);
 for(const [x,y,side]of [[345,330,'left'],[510,330,'right']]as const)expect(owner(x,y).contexts?.map(c=>c.part+':'+c.side).sort()).toEqual(['arm:'+side,'body:center']);
 const lower=rgba.slice();for(let y=440;y<475;y++)for(let x=290;x<320;x++)lower.set([25,170,70,255],(y*width+x)*4);
 const tested=illustrationRegions(width,1024,lower),patch=tested.regions.find(s=>s.indices.includes(455*width+305))!;expect(patch.part).toBe('arm');expect(patch.contexts?.some(c=>c.part==='body')??false).toBe(false);
});

it('retains both torso and leg candidates for the actual continuous black flanks crossing the supported hip',async()=>{
 const width=803,rgba=new Uint8Array(await sharp('tests/fixtures/character-blue-white-front-back.png').extract({left:0,top:0,width,height:1024}).ensureAlpha().raw().toBuffer()),result=illustrationRegions(width,1024,rgba);
 for(const [x,y,side]of [[367,455,'left'],[486,455,'right']]as const){const flank=result.regions.find(r=>r.indices.includes(y*width+x))!;expect(flank).toBeDefined();expect(flank.color).toBe('#282b30');expect(flank.contexts?.map(c=>c.part+':'+c.side).sort()).toEqual(['body:center','leg:'+side]);expect(flank.indices.length).toBeGreaterThan(3000);}
});

it('recognizes the actual back-view paired heel pigment despite a connected lower silhouette without cutting any source',async()=>{
 const width=733,height=1024,rgba=new Uint8Array(await sharp('tests/fixtures/character-blue-white-front-back.png').extract({left:803,top:0,width,height}).ensureAlpha().raw().toBuffer()),result=illustrationRegions(width,height,rgba);
 expect(result.anatomical,'a ground-shadow connection must not erase all reliable back-view anatomy').toBe(true);
 expect(result.regions).toHaveLength(46);
 const owner=(x:number,y:number)=>result.regions.find(r=>r.indices.includes(y*width+x));
 const diamond=owner(260,350)!;
 expect(diamond.indices).toHaveLength(1813);expect(diamond.part).toBe('body');expect(diamond.side).toBe('center');expect(diamond.confidence).toBeGreaterThan(.7);
 for(const [x,y,side,pixels]of[[178,925,'left',4919],[320,925,'right',4713]] as const){const heel=owner(x,y)!;expect(heel.indices).toHaveLength(pixels);expect(heel.part).toBe('foot');expect(heel.side).toBe(side);expect(heel.confidence).toBeGreaterThan(.7);}
 expect(result.regions.some(r=>r.part==='unknown')).toBe(true); // Cross-head/torso and ear ambiguity still need review.
 const all=result.regions.flatMap(r=>r.indices);expect(new Set(all).size).toBe(all.length);expect(all.length).toBe(result.foregroundPixels-result.discardedPixels);
});

function connectedFigure(extraTail=false){
 const width=180,height=320,rgba=new Uint8Array(width*height*4).fill(255);
 const paint=(left:number,top:number,right:number,bottom:number,rgb:number[])=>{for(let y=top;y<bottom;y++)for(let x=left;x<right;x++)rgba.set([...rgb,255],(y*width+x)*4);};
 // A tall multicolour figure without separately supported feet. The whole
 // lower white shape is connected, and one coloured end cannot imply two legs.
 paint(55,15,125,305,[215,215,215]);paint(65,25,115,75,[35,105,190]);paint(75,100,110,150,[220,155,50]);
 paint(65,276,82,303,[35,105,190]);
 if(extraTail)paint(133,278,175,304,[35,105,190]);
 return {width,height,rgba};
}
it.each([false,true])('a single supported lower pigment and detached lateral tail do not force whole-body classification (tail=%s)',tail=>{
 const {width,height,rgba}=connectedFigure(tail),result=illustrationRegions(width,height,rgba);
 expect(result.anatomical).toBe(false);expect(result.regions.every(r=>r.part==='unknown'&&r.confidence===0)).toBe(true);
});

it.each([128,512])('the actual back-view foot support is scale-relative at %spx proxy height',async height=>{
 const {data,info}=await sharp('tests/fixtures/character-blue-white-front-back.png').extract({left:803,top:0,width:733,height:1024}).resize({height}).ensureAlpha().raw().toBuffer({resolveWithObject:true}),result=illustrationRegions(info.width,info.height,new Uint8Array(data));
 expect(result.anatomical).toBe(true);expect(result.partBounds.some(b=>b.part==='body')).toBe(true);
 expect(result.partBounds.filter(b=>b.part==='foot'&&b.side)).toHaveLength(2);
 expect(result.regions.some(r=>r.part==='unknown')).toBe(true);
});

it('the real back-view compact bilateral black hands must not be attached as tail pigment',async()=>{
 const width=733,height=1024,rgba=new Uint8Array(await sharp('tests/fixtures/character-blue-white-front-back.png').extract({left:803,top:0,width,height}).ensureAlpha().raw().toBuffer()),result=illustrationRegions(width,height,rgba);
 for(const [x,y,side,pixels]of[[75,560,'left',3281],[440,560,'right',3144]] as const){const hand=result.regions.find(r=>r.indices.includes(y*width+x))!;expect(hand.indices).toHaveLength(pixels);expect(hand.part).toBe('paw');expect(hand.side).toBe(side);expect(hand.confidence).toBeGreaterThan(.7);}
});
it('a single dark lateral tail does not become a paw even when paired feet independently support the character',()=>{
 const {width,height,rgba}=connectedFigure(false);
 const paint=(left:number,top:number,right:number,bottom:number,rgb:number[])=>{for(let y=top;y<bottom;y++)for(let x=left;x<right;x++)rgba.set([...rgb,255],(y*width+x)*4);};
 paint(100,276,117,303,[35,105,190]);paint(136,180,175,210,[25,25,25]);
 const result=illustrationRegions(width,height,rgba);expect(result.anatomical).toBe(true);
 const tail=result.regions.find(r=>r.indices.includes(190*width+150))!;expect(tail.part).not.toBe('paw');expect(result.partBounds.some(b=>b.part==='paw')).toBe(false);
});
it.each([['front',0,803],['back',803,733]] as const)('retains supported minor white limb contexts, paired exterior ears and the central collar in the real %s view',async(_view,left,width)=>{
 const height=1024,rgba=new Uint8Array(await sharp('tests/fixtures/character-blue-white-front-back.png').extract({left,top:0,width,height}).ensureAlpha().raw().toBuffer()),result=illustrationRegions(width,height,rgba);
 const owner=(x:number,y:number)=>result.regions.find(r=>r.indices.includes(y*width+x))!;
 const white=owner(left===0?400:250,450);
 for(const part of ['arm','leg','foot'] as const)for(const side of ['left','right'] as const)expect(white.contexts?.some(c=>c.part===part&&c.side===side),`${_view} continuous white ${part}:${side}`).toBe(true);
 for(const [x,y,side]of(left===0?[[325,80,'left'],[535,80,'right']]:[[160,80,'left'],[355,80,'right']])as [number,number,string][]){const ear=owner(x,y);expect(ear.part).toBe('ear');expect(ear.side).toBe(side);expect(ear.confidence).toBeGreaterThan(.5);}
 const collar=owner(left===0?428:260,left===0?350:410);expect(collar.contexts?.some(c=>c.part==='body'&&c.side==='center')).toBe(true);expect(collar.contexts?.some(c=>c.part==='head'&&c.side==='center')).toBe(true);
 expect(result.regions).toHaveLength(left===0?87:46);const all=result.regions.flatMap(r=>r.indices);expect(new Set(all).size).toBe(all.length);expect(all.length).toBe(result.foregroundPixels-result.discardedPixels);
});
it.each([['front',0,803,[[345,330,'left'],[510,330,'right']],[[325,620,'left'],[525,620,'right']]],['back',803,733,[[175,330,'left'],[345,330,'right']],[[163,620,'left'],[355,620,'right']]]] as const)('uses supported shoulder and hip seams for real %s registration while retaining every source pixel',async(_view,left,width,shoulders,thighs)=>{
 const rgba=new Uint8Array(await sharp('tests/fixtures/character-blue-white-front-back.png').extract({left,top:0,width,height:1024}).ensureAlpha().raw().toBuffer()),r=illustrationRegions(width,1024,rgba),owner=(x:number,y:number)=>r.regions.find(a=>a.indices.includes(y*width+x))!;
 for(const [x,y,side]of shoulders){expect(owner(x,y).part).toBe('arm');expect(owner(x,y).side).toBe(side);}
 for(const [x,y,side]of thighs){const source=owner(x,y);expect(source.part).toBe('leg');expect(source.side).toBe(side);}
 // Light blue and navy are now separate physical pigments. Probe the actual
 // cross-hip component, rather than expecting a contained navy drop to reach
 // the torso as its formerly merged light-blue parent did.
 for(const [x,y,side]of (left===0?[[330,670,'left'],[525,670,'right']]:[[205,450,'left'],[310,450,'right']])as [number,number,string][]){const source=owner(x,y);expect(source.contexts?.some(c=>c.part==='body'&&c.side==='center')).toBe(true);expect(source.contexts?.some(c=>c.part==='leg'&&c.side===side)).toBe(true);}
 const legs=r.partBounds.filter(b=>b.part==='leg'&&b.side);expect(legs).toHaveLength(2);for(const b of legs){expect(b.minY).toBeGreaterThan(480);expect(b.minY).toBeLessThan(570);expect(b.maxY).toBeGreaterThan(830);}
 const widths=legs.map(b=>b.maxX-b.minX);expect(Math.max(...widths)/Math.min(...widths)).toBeLessThan(1.4);
 const arms=r.partBounds.filter(b=>b.part==='arm'&&b.side);for(const b of arms)expect(b.minY).toBeLessThan(330);
 const tail=owner(left===0?660:460,800);expect(tail.part).not.toBe('leg');
});
it.each(['single','narrow-pair'] as const)('does not classify unsupported dark upper protrusions as ears (%s)',mode=>{
 const {width,height,rgba}=connectedFigure(false),paint=(l:number,t:number,r:number,b:number)=>{for(let y=t;y<b;y++)for(let x=l;x<r;x++)rgba.set([25,25,25,255],(y*width+x)*4);};
 for(let y=276;y<303;y++)for(let x=100;x<117;x++)rgba.set([35,105,190,255],(y*width+x)*4);
 if(mode==='single')paint(30,5,54,55);else{paint(57,5,65,55);paint(115,5,123,55);}
 const result=illustrationRegions(width,height,rgba);expect(result.anatomical).toBe(true);const dark=result.regions.filter(r=>r.color.startsWith('#19'));expect(dark.length).toBeGreaterThan(0);for(const r of dark)expect(r.part).not.toBe('ear');
});
