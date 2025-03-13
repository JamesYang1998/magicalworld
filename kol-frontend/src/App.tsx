import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useAuth } from './contexts/AuthContext';
import { UserRole } from './types';

// Auth Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';

// KOL Pages
import KOLProfile from './pages/kol/Profile';
import TaskList from './pages/tasks/TaskList';
import TaskDetail from './pages/tasks/TaskDetail';

// Publisher Pages
import PublisherProfile from './pages/publisher/Profile';
import CreateTask from './pages/tasks/CreateTask';

// Admin Pages
import AdminDashboard from './pages/admin/Dashboard';
import SubmissionsList from './pages/admin/SubmissionsList';
import SubmissionReview from './pages/admin/SubmissionReview';

// Layout Components
import Layout from './components/Layout';

// Protected Route Component
interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

const ProtectedRoute = ({ children, allowedRoles }: ProtectedRouteProps) => {
  const { user, loading, isAuthenticated } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/" />;
  }
  
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    // Redirect based on user role
    if (user.role === UserRole.KOL) {
      return <Navigate to="/dashboard/tasks" />;
    } else if (user.role === UserRole.PUBLISHER) {
      return <Navigate to="/dashboard/publisher/create-task" />;
    } else if (user.role === UserRole.ADMIN) {
      return <Navigate to="/dashboard/admin/dashboard" />;
    }
    
    return <Navigate to="/" />;
  }
  
  return <>{children}</>;
};

// Import the LandingPage component
import LandingPage from './pages/LandingPage';
import SampleTasksPage from './pages/SampleTasksPage';

function App() {
  return (
    <Router>
      <Toaster position="top-right" />
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/sample-tasks" element={<SampleTasksPage />} />
        
        {/* Protected Routes */}
        <Route path="/dashboard" element={
          <Layout />
        }>
          {/* KOL Routes */}
          <Route path="" element={<Navigate to="tasks" />} />
          <Route path="profile" element={
            <ProtectedRoute allowedRoles={[UserRole.KOL]}>
              <KOLProfile />
            </ProtectedRoute>
          } />
          <Route path="tasks" element={
            <ProtectedRoute>
              <TaskList />
            </ProtectedRoute>
          } />
          <Route path="tasks/:id" element={
            <ProtectedRoute>
              <TaskDetail />
            </ProtectedRoute>
          } />
          
          {/* Publisher Routes */}
          <Route path="publisher/profile" element={
            <ProtectedRoute allowedRoles={[UserRole.PUBLISHER]}>
              <PublisherProfile />
            </ProtectedRoute>
          } />
          <Route path="publisher/create-task" element={
            <ProtectedRoute allowedRoles={[UserRole.PUBLISHER]}>
              <CreateTask />
            </ProtectedRoute>
          } />
          
          {/* Admin Routes */}
          <Route path="admin/dashboard" element={
            <ProtectedRoute allowedRoles={[UserRole.ADMIN]}>
              <AdminDashboard />
            </ProtectedRoute>
          } />
          <Route path="admin/submissions" element={
            <ProtectedRoute allowedRoles={[UserRole.ADMIN]}>
              <SubmissionsList />
            </ProtectedRoute>
          } />
          <Route path="admin/submissions/:id" element={
            <ProtectedRoute allowedRoles={[UserRole.ADMIN]}>
              <SubmissionReview />
            </ProtectedRoute>
          } />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
