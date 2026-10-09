import type {Project} from '../schema/index';

/** Includes dormant model snapshots and candidates that can later become active cuts. */
export function projectPieces(project:Project){
 return [...project.pieces,...(project.patternLibrary??[]).map(r=>r.piece),
  ...(project.modelLibrary??[]).flatMap(m=>m.pieces??[]),...(project.surfaceRun?.pieces??[]),
  ...(project.referenceRun?(project.referenceRun.pieces??[project.referenceRun.piece]):[])];
}
export function materialInUse(project:Project,materialId:string){
 return projectPieces(project).some(piece=>piece.materialId===materialId);
}
