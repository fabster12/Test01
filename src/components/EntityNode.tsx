import React from 'react';
import { Handle, Position } from 'reactflow';
import { Field } from '../types';

interface EntityNodeData {
  name: string;
  fields: Field[];
}

interface EntityNodeProps {
  data: EntityNodeData;
}

const EntityNode = ({ data }: EntityNodeProps) => {
  return (
    <div style={{
      background: 'white',
      border: '1px solid #ddd',
      borderRadius: '5px',
      padding: '10px',
      minWidth: '200px',
      fontSize: '12px',
    }}>
      <Handle type="target" position={Position.Left} />
      <div style={{
        background: '#555',
        color: 'white',
        padding: '5px 10px',
        borderRadius: '3px 3px 0 0',
        fontWeight: 'bold',
        textAlign: 'center',
      }}>
        {data.name}
      </div>
      <div style={{ padding: '10px' }}>
        {data.fields.map((field) => (
          <div key={field.id} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #eee', padding: '5px 0' }}>
            <span>{field.name}</span>
            <span style={{ color: '#888' }}>{field.dataType}</span>
          </div>
        ))}
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
};

export default EntityNode;
