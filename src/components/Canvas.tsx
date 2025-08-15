import React, { useContext, useMemo, useCallback } from 'react';
import ReactFlow, { Node, Edge, Connection } from 'reactflow';
import 'reactflow/dist/style.css';

import { ModelContext } from '../context/ModelContext';
import EntityNode from './EntityNode'; // Import the custom node

const Canvas = () => {
  const context = useContext(ModelContext);

  // Register the custom node type
  const nodeTypes = useMemo(() => ({ entity: EntityNode }), []);

  if (!context) {
    return <div>Loading...</div>;
  }

  const { model, addEntity, addRelationship, setSelectedElementId } = context;

  const onConnect = useCallback(
    (params: Connection) => {
      if (params.source && params.target) {
        addRelationship({ sourceId: params.source, targetId: params.target, label: 'new relationship' });
      }
    },
    [addRelationship]
  );

  const handleAddEntity = () => {
    const newEntity = {
      id: `e${Date.now()}`,
      name: 'NewEntity',
      fields: [],
      position: {
        // Position it roughly in the center of the current view
        x: Math.random() * 400,
        y: Math.random() * 400,
      },
    };
    addEntity(newEntity);
  };

  // Transform our data model into the format React Flow expects
  const nodes: Node[] = model.entities.map(entity => ({
    id: entity.id,
    type: 'entity', // Use our custom node type
    position: entity.position,
    data: { name: entity.name, fields: entity.fields }, // Pass the correct data
  }));

  // Create edges for regular relationships
  const relationshipEdges: Edge[] = model.relationships.map(rel => ({
    id: rel.id,
    source: rel.sourceId,
    target: rel.targetId,
    label: rel.label,
    markerEnd: {
      type: 'arrowclosed',
    },
  }));

  // Create edges for inheritance relationships
  const inheritanceEdges: Edge[] = model.entities
    .filter(e => e.parentId)
    .map(e => ({
      id: `inheritance-${e.id}-${e.parentId}`,
      source: e.parentId!,
      target: e.id,
      label: 'inherits',
      type: 'straight',
      style: { stroke: '#9ca3af', strokeDasharray: '5,5' }, // Dashed line for inheritance
      markerEnd: {
        type: 'arrow', // Open arrow for inheritance
        color: '#9ca3af',
      },
    }));

  const edges = [...relationshipEdges, ...inheritanceEdges];

  return (
    <div className="panel canvas" style={{ height: '100%', width: '100%', position: 'relative' }}>
      <button onClick={handleAddEntity} style={{ position: 'absolute', top: 10, left: 10, zIndex: 10 }}>
        Add Entity
      </button>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onConnect={onConnect}
        onNodeClick={(_, node) => setSelectedElementId(node.id)}
        onPaneClick={() => setSelectedElementId(null)}
        fitView
      >
        {/* We can add controls, a minimap, etc. here later */}
      </ReactFlow>
    </div>
  );
};

export default Canvas;
