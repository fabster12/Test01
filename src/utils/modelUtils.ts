import { DataModel, Entity, Field } from '../types';

/**
 * Recursively traverses the inheritance chain to collect all fields for a given entity.
 * @param entityId The ID of the entity to resolve.
 * @param model The full data model.
 * @param visited A set to keep track of visited entities to prevent infinite loops.
 * @returns A map of field names to field objects, ensuring no duplicates.
 */
const collectFields = (
  entityId: string,
  model: DataModel,
  visited: Set<string> = new Set()
): Map<string, Field> => {
  if (visited.has(entityId)) {
    // Prevent infinite recursion in case of circular dependencies
    return new Map();
  }
  visited.add(entityId);

  const entity = model.entities.find(e => e.id === entityId);
  if (!entity) {
    return new Map();
  }

  // Get fields from parent first, so child fields override parent fields if names conflict.
  const parentFields = entity.parentId
    ? collectFields(entity.parentId, model, visited)
    : new Map<string, Field>();

  // Add the entity's own fields
  const ownFields = new Map<string, Field>();
  entity.fields.forEach(field => ownFields.set(field.name, field));

  const combinedMap = new Map(parentFields);
  ownFields.forEach((value, key) => {
    combinedMap.set(key, value);
  });
  return combinedMap;
};

/**
 * Gets the full list of fields for an entity, including inherited fields.
 * @param entityId The ID of the entity.
 * @param model The full data model.
 * @returns An array of fields.
 */
export const getResolvedFields = (entityId: string, model: DataModel): Field[] => {
  const fieldMap = collectFields(entityId, model);
  return Array.from(fieldMap.values());
};

/**
 * A simple utility to get an entity by its ID.
 * @param entityId The ID of the entity.
 * @param model The full data model.
 * @returns The entity object or undefined if not found.
 */
export const getEntityById = (entityId: string, model: DataModel): Entity | undefined => {
    return model.entities.find(e => e.id === entityId);
}
