import { DataModel, Entity, DataType } from "../types";

// A simplified mapping from our internal DataType to JSON Schema types
const mapDataTypeToJsonSchemaType = (dataType: DataType): string => {
  switch (dataType) {
    case 'string':
    case 'date':
      return 'string';
    case 'number':
      return 'number';
    case 'boolean':
      return 'boolean';
    case 'object':
      return 'object';
    case 'array':
      return 'array';
    default:
      return 'string';
  }
};

// Converts a single entity into a JSON Schema definition
const convertEntityToJsonSchema = (entity: Entity) => {
  const properties = entity.fields.reduce((acc, field) => {
    acc[field.name] = {
      type: mapDataTypeToJsonSchemaType(field.dataType),
      description: field.description || '',
    };
    return acc;
  }, {} as any);

  const requiredFields = entity.fields
    .filter(field => field.required)
    .map(field => field.name);

  return {
    type: 'object',
    title: entity.name,
    properties,
    required: requiredFields,
  };
};

// Main function to convert our entire DataModel to a JSON Schema
export const convertModelToJsonSchema = (model: DataModel) => {
  const schema = {
    $schema: 'http://json-schema.org/draft-07/schema#',
    title: 'Data Model',
    type: 'object',
    definitions: {},
    properties: {},
  };

  // Convert each entity and add it to the 'definitions' section
  model.entities.forEach(entity => {
    schema.definitions[entity.name] = convertEntityToJsonSchema(entity);
  });

  // Here you could define top-level properties based on relationships,
  // but for now, we'll just keep them in definitions.

  return schema;
};
