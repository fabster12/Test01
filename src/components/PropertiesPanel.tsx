import React, { useContext } from 'react';
import { ModelContext } from '../context/ModelContext';
import { DataType } from '../types';
import { getResolvedFields, getEntityById } from '../utils/modelUtils';

const PropertiesPanel = () => {
  const context = useContext(ModelContext);

  if (!context) {
    return <div>Loading...</div>;
  }

  const { model, selectedElementId, updateEntity, addField, updateField, removeField } = context;

  const selectedEntity = getEntityById(selectedElementId || '', model);

  if (!selectedEntity) {
    return (
      <div className="panel properties-panel">
        <h2>Properties</h2>
        <p>Select an entity to see its properties.</p>
      </div>
    );
  }

  const resolvedFields = getResolvedFields(selectedEntity.id, model);

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateEntity(selectedEntity.id, { name: e.target.value });
  };

  const handleAddField = () => {
    const newField = {
      name: 'newField',
      dataType: 'string' as DataType,
    };
    addField(selectedEntity.id, newField);
  };

  return (
    <div className="panel properties-panel">
      <h2>Properties</h2>
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Entity Name:</label>
        <input
          type="text"
          value={selectedEntity.name}
          onChange={handleNameChange}
          style={{ width: '90%', padding: '5px' }}
        />
      </div>
      {selectedEntity.parentId && (
        <div style={{ fontSize: '0.9em', color: '#555', marginTop: '10px' }}>
          Inherits from: <strong>{getEntityById(selectedEntity.parentId, model)?.name || 'Unknown'}</strong>
        </div>
      )}
      <hr style={{ margin: '20px 0' }} />
      <div>
        <h3 style={{ marginBottom: '10px' }}>Fields</h3>
        {resolvedFields.map(field => {
          const isInherited = !selectedEntity.fields.some(f => f.id === field.id);
          return (
            <div key={field.id} style={{ border: '1px solid #eee', padding: '10px', marginBottom: '10px', borderRadius: '5px', background: isInherited ? '#f9f9f9' : 'white' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
                <input
                  type="text"
                  value={field.name}
                  onChange={(e) => !isInherited && updateField(selectedEntity.id, field.id, { name: e.target.value })}
                  placeholder="Field Name"
                  style={{ border: '1px solid #ccc', padding: '3px', background: isInherited ? '#eee' : 'white' }}
                  disabled={isInherited}
                />
                <select
                  value={field.dataType}
                  onChange={(e) => !isInherited && updateField(selectedEntity.id, field.id, { dataType: e.target.value as DataType })}
                  style={{ border: '1px solid #ccc', padding: '3px', background: isInherited ? '#eee' : 'white' }}
                  disabled={isInherited}
                >
                  <option value="string">string</option>
                  <option value="number">number</option>
                  <option value="boolean">boolean</option>
                  <option value="date">date</option>
                  <option value="object">object</option>
                  <option value="array">array</option>
                </select>
                <button
                  onClick={() => !isInherited && removeField(selectedEntity.id, field.id)}
                  style={{ border: 'none', background: 'transparent', color: isInherited ? '#ccc' : 'red', cursor: isInherited ? 'not-allowed' : 'pointer' }}
                  disabled={isInherited}
                >
                  X
                </button>
              </div>
              {isInherited && <div style={{fontSize: '0.8em', color: '#777'}}>Inherited</div>}
            </div>
          );
        })}
        <button onClick={handleAddField} style={{ marginTop: '10px' }}>
          Add Field
        </button>
      </div>
    </div>
  );
};

export default PropertiesPanel;
