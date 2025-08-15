import React, { createContext, useState, ReactNode } from 'react';
import { DataModel, Entity } from '../types';

// Define the shape of the context data
import { Field, Relationship } from '../types';

interface IModelContext {
  model: DataModel;
  setModel: (model: DataModel) => void; // To replace the model on import
  selectedElementId: string | null;
  setSelectedElementId: (id: string | null) => void;
  addEntity: (entity: Entity) => void;
  updateEntity: (entityId: string, updatedProperties: Partial<Entity>) => void;
  addField: (entityId: string, field: Omit<Field, 'id'>) => void;
  updateField: (entityId: string, fieldId: string, updatedProperties: Partial<Field>) => void;
  removeField: (entityId: string, fieldId: string) => void;
  addRelationship: (relationship: Omit<Relationship, 'id'>) => void;
  removeRelationship: (relationshipId: string) => void;
}

// Create the context with a default value
export const ModelContext = createContext<IModelContext | undefined>(undefined);

// Create a provider component
interface ModelProviderProps {
  children: ReactNode;
}

// Some initial mock data to visualize the UI
const initialModel: DataModel = {
  entities: [
    {
      id: '1',
      name: 'User',
      position: { x: 100, y: 100 },
      fields: [
        { id: 'f1', name: 'id', dataType: 'string', required: true },
        { id: 'f2', name: 'email', dataType: 'string', required: true },
        { id: 'f3', name: 'createdAt', dataType: 'date' },
      ],
    },
    {
      id: '2',
      name: 'UserProfile',
      position: { x: 400, y: 150 },
      parentId: '1', // Inherits from User
      fields: [
        { id: 'f4', name: 'firstName', dataType: 'string' },
        { id: 'f5', name: 'lastName', dataType: 'string' },
      ],
    },
  ],
  relationships: [
      { id: 'r1', sourceId: '1', targetId: '2', label: 'has profile' }
  ],
};

export const ModelProvider = ({ children }: ModelProviderProps) => {
  const [model, setModel] = useState<DataModel>(initialModel);
  const [selectedElementId, setSelectedElementId] = useState<string | null>(null);

  const addEntity = (entity: Entity) => {
    setModel((prevModel) => ({
      ...prevModel,
      entities: [...prevModel.entities, entity],
    }));
  };

  const updateEntity = (entityId: string, updatedProperties: Partial<Entity>) => {
    setModel((prevModel) => ({
      ...prevModel,
      entities: prevModel.entities.map((entity) =>
        entity.id === entityId ? { ...entity, ...updatedProperties } : entity
      ),
    }));
  };

  const addField = (entityId: string, field: Omit<Field, 'id'>) => {
    setModel((prevModel) => ({
      ...prevModel,
      entities: prevModel.entities.map((entity) => {
        if (entity.id === entityId) {
          const newField = { ...field, id: `f${Date.now()}` };
          return { ...entity, fields: [...entity.fields, newField] };
        }
        return entity;
      }),
    }));
  };

  const updateField = (entityId: string, fieldId: string, updatedProperties: Partial<Field>) => {
    setModel((prevModel) => ({
      ...prevModel,
      entities: prevModel.entities.map((entity) => {
        if (entity.id === entityId) {
          return {
            ...entity,
            fields: entity.fields.map((field) =>
              field.id === fieldId ? { ...field, ...updatedProperties } : field
            ),
          };
        }
        return entity;
      }),
    }));
  };

  const removeField = (entityId: string, fieldId: string) => {
    setModel((prevModel) => ({
      ...prevModel,
      entities: prevModel.entities.map((entity) => {
        if (entity.id === entityId) {
          return { ...entity, fields: entity.fields.filter((field) => field.id !== fieldId) };
        }
        return entity;
      }),
    }));
  };

  const addRelationship = (relationship: Omit<Relationship, 'id'>) => {
    setModel((prevModel) => ({
      ...prevModel,
      relationships: [...prevModel.relationships, { ...relationship, id: `r${Date.now()}` }],
    }));
  };

  const removeRelationship = (relationshipId: string) => {
    setModel((prevModel) => ({
      ...prevModel,
      relationships: prevModel.relationships.filter((rel) => rel.id !== relationshipId),
    }));
  };

  const contextValue = {
    model,
    setModel,
    selectedElementId,
    setSelectedElementId,
    addEntity,
    updateEntity,
    addField,
    updateField,
    removeField,
    addRelationship,
    removeRelationship,
  };

  return (
    <ModelContext.Provider value={contextValue}>
      {children}
    </ModelContext.Provider>
  );
};
