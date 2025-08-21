import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';
import { ModelProvider } from './context/ModelContext';

test('renders the add entity button', () => {
  render(
    <ModelProvider>
      <App />
    </ModelProvider>
  );
  const buttonElement = screen.getByText(/Add Entity/i);
  expect(buttonElement).toBeInTheDocument();
});
