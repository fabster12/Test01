import React, { useContext, useRef } from 'react';
import './App.css';
import ObjectBrowser from './components/ObjectBrowser';
import Canvas from './components/Canvas';
import PropertiesPanel from './components/PropertiesPanel';
import { ModelContext } from './context/ModelContext';
import { DataModel } from './types';

function App() {
  const context = useContext(ModelContext);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!context) {
    return <div>Loading...</div>;
  }
  const { model, setModel } = context;

  const handleExport = () => {
    const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(model, null, 2)
    )}`;
    const link = document.createElement('a');
    link.href = jsonString;
    link.download = 'datamodel.json';
    link.click();
  };

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result;
      try {
        if (typeof text === 'string') {
          const importedModel = JSON.parse(text) as DataModel;
          // Basic validation
          if (importedModel && Array.isArray(importedModel.entities)) {
            setModel(importedModel);
          } else {
            alert('Invalid model file format.');
          }
        }
      } catch (error) {
        alert('Error parsing JSON file.');
        console.error(error);
      }
    };
    reader.readAsText(file);
    // Reset file input
    event.target.value = '';
  };

  return (
    <div className="app">
      <header className="header">
        <span>Hackolade Clone</span>
        <div style={{ marginLeft: 'auto' }}>
          <button onClick={handleImportClick} style={{ marginRight: '10px' }}>Import</button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
            accept=".json"
          />
          <button onClick={handleExport}>Export</button>
        </div>
      </header>
      <ObjectBrowser />
      <Canvas />
      <PropertiesPanel />
    </div>
  );
}

export default App;
