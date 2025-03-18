import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import SEODashboard from './components/dashboard/SEODashboard';

function App() {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<SEODashboard />} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;