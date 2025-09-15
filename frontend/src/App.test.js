import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Shadow SEC application', () => {
  render(<App />);
  const titleElement = screen.getByText(/Shadow SEC/i);
  expect(titleElement).toBeInTheDocument();
});