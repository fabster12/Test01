import React, { useContext } from 'react';
import { ModelContext } from '../context/ModelContext';
import { getResolvedFields } from '../utils/modelUtils';
import { Entity } from '../types';

const ObjectBrowser = () => {
  const context = useContext(ModelContext);

  if (!context) {
    return <div>Loading...</div>;
  }

  const { model, selectedElementId, setSelectedElementId } = context;

  const styles = {
    tree: {
      listStyle: 'none',
      paddingLeft: '0',
    },
    entityItem: {
      padding: '5px 10px',
      cursor: 'pointer',
      borderRadius: '3px',
    },
    entityItemSelected: {
      backgroundColor: '#dbeafe',
    },
    fieldList: {
      listStyle: 'none',
      paddingLeft: '20px',
    },
    fieldItem: {
      padding: '2px 5px',
      fontSize: '0.9em',
      color: '#555',
    },
    inheritedFieldItem: {
      padding: '2px 5px',
      fontSize: '0.9em',
      color: '#9ca3af', // Lighter color for inherited fields
      fontStyle: 'italic',
    }
  };

  // A recursive component to render the entity tree
  const renderEntityTree = (entities: Entity[], parentId: string | null = null) => {
    return entities
      .filter(e => (parentId === null ? !e.parentId : e.parentId === parentId))
      .map(entity => {
        const resolvedFields = getResolvedFields(entity.id, model);
        return (
          <li key={entity.id}>
            <div
              style={{
                ...styles.entityItem,
                ...(entity.id === selectedElementId ? styles.entityItemSelected : {}),
              }}
              onClick={() => setSelectedElementId(entity.id)}
            >
              {entity.name}
            </div>
            <ul style={styles.fieldList}>
              {resolvedFields.map(field => {
                const isInherited = !entity.fields.some(f => f.id === field.id);
                return (
                  <li key={field.id} style={isInherited ? styles.inheritedFieldItem : styles.fieldItem}>
                    {field.name}: {field.dataType}
                  </li>
                );
              })}
            </ul>
            {/* Recursively render children */}
            <ul style={{ listStyle: 'none', paddingLeft: '20px' }}>
              {renderEntityTree(entities, entity.id)}
            </ul>
          </li>
        );
      });
  };

  return (
    <div className="panel object-browser">
      <h2>Object Browser</h2>
      <ul style={styles.tree}>
        {renderEntityTree(model.entities)}
      </ul>
    </div>
  );
};

export default ObjectBrowser;
