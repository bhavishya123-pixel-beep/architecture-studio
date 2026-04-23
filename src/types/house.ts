export type PlanOrientation = 'long-side' | 'short-side' | 'square';
export type ArchitecturalStyle =
  | 'Ranch'
  | 'Craftsman'
  | 'Prairie'
  | 'Mid-Century Modern'
  | 'Mediterranean'
  | 'Colonial'
  | 'Contemporary';

export type RoofType = 'Hip' | 'Gable' | 'Flat' | 'Shed' | 'Butterfly' | 'Cross-Gable';
export type FacadeCategory = 'Exterior' | 'Interior' | 'Structural' | 'Landscape' | 'Roof';

export interface DesignElement {
  id: string;
  name: string;
  category: FacadeCategory;
  description: string;
  whyItFits: string;
}

export interface HousePlan {
  id: string;
  name: string;
  style: ArchitecturalStyle;
  orientation: PlanOrientation;
  /** Width (along street-facing facade) in feet */
  width: number;
  /** Depth (perpendicular to facade) in feet */
  depth: number;
  squareFootage: number;
  bedrooms: number;
  bathrooms: number;
  roofType: RoofType;
  yearBuilt: number;
  location: string;
  description: string;
  suggestedElements: DesignElement[];
  imageUrl: string;
  tags: string[];
}
