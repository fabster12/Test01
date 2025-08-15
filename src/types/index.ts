// Defines the basic data types a field can have.
export type DataType = 'string' | 'number' | 'boolean' | 'date' | 'object' | 'array';

// Represents a single field within an entity.
export interface Field {
  id: string;
  name: string;
  dataType: DataType;
  description?: string;
  required?: boolean;
  defaultValue?: any;
}

// Represents a data entity, which is a collection of fields.
// This will be a draggable node on the canvas.
export interface Entity {
  id: string;
  name:string;
  fields: Field[];
  // For positioning on the canvas
  position: {
    x: number;
    y: number;
  };
  // To support inheritance/reusability
  parentId?: string;
}

// Represents a relationship between two entities.
// This will be an edge on the canvas.
export interface Relationship {
  id: string;
  sourceId: string;
  targetId: string;
  label?: string;
}

// The top-level container for the entire data model.
export interface DataModel {
  entities: Entity[];
  relationships: Relationship[];
}
