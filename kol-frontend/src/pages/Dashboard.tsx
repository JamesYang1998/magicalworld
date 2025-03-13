import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { Task, UserRole, TaskStatus } from '../types';
import { getSampleTasks } from '../utils/sampleTasks';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        let endpoint = '/tasks';
        
        // For KOLs, get their submissions
        if (user?.role === UserRole.KOL) {
          endpoint = '/tasks/kol';
        }
        // For publishers, get their created tasks
        else if (user?.role === UserRole.PUBLISHER) {
          endpoint = '/tasks/publisher';
        }
        
        const response = await api.get(endpoint);
        setTasks(response.data.slice(0, 5)); // Get only the first 5 tasks
      } catch (error) {
        toast.error('Failed to load tasks');
      } finally {
        setLoading(false);
      }
    };
    
    if (user) {
      fetchTasks();
    }
  }, [user]);
  
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      
      {/* Welcome Section */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold mb-2">Welcome, {user?.username}!</h2>
        <p className="text-gray-600">
          {user?.role === UserRole.KOL && 'Find and complete tasks from publishers.'}
          {user?.role === UserRole.PUBLISHER && 'Create tasks for KOLs to complete.'}
          {user?.role === UserRole.ADMIN && 'Manage the platform and review submissions.'}
        </p>
        
        {/* Quick Actions */}
        <div className="mt-4 flex flex-wrap gap-2">
          {user?.role === UserRole.KOL && (
            <>
              <Link
                to="/dashboard/tasks"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
              >
                Browse Tasks
              </Link>
              <Link
                to="/dashboard/profile"
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
              >
                Update Profile
              </Link>
            </>
          )}
          
          {user?.role === UserRole.PUBLISHER && (
            <>
              <Link
                to="/dashboard/publisher/create-task"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
              >
                Create Task
              </Link>
              <Link
                to="/dashboard/publisher/profile"
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
              >
                Update Profile
              </Link>
            </>
          )}
          
          {user?.role === UserRole.ADMIN && (
            <>
              <Link
                to="/dashboard/admin/submissions"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
              >
                Review Submissions
              </Link>
              <Link
                to="/dashboard/admin/dashboard"
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
              >
                Admin Dashboard
              </Link>
            </>
          )}
        </div>
      </div>
      
      {/* Recent Tasks Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">
            {user?.role === UserRole.KOL && 'Your Recent Tasks'}
            {user?.role === UserRole.PUBLISHER && 'Your Published Tasks'}
            {user?.role === UserRole.ADMIN && 'Recent Tasks'}
          </h2>
          <Link
            to="/dashboard/tasks"
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            View All
          </Link>
        </div>
        
        {loading ? (
          <div>Loading tasks...</div>
        ) : tasks.length > 0 ? (
          <div className="overflow-hidden">
            <ul className="divide-y divide-gray-200">
              {tasks.map((task) => (
                <li key={task.id} className="py-4">
                  <Link to={`/dashboard/tasks/${task.id}`} className="block hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-blue-600">{task.title}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          Platform: {task.platform} | Commission: {task.commission} USDT
                        </p>
                      </div>
                      <div>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          task.status === TaskStatus.OPEN 
                            ? 'bg-green-100 text-green-800' 
                            : task.status === TaskStatus.IN_PROGRESS 
                            ? 'bg-yellow-100 text-yellow-800' 
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {task.status}
                        </span>
                      </div>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="text-center py-4">
            <p className="text-gray-500 mb-4">No tasks available.</p>
            
            <div className="mt-4">
              <h3 className="text-md font-medium text-blue-800 mb-2">示例营销任务</h3>
              <div className="grid grid-cols-1 gap-4 mt-4">
                {getSampleTasks(2).map((task) => (
                  <div key={task.id} className="bg-gray-50 p-4 rounded-lg border border-blue-100 text-left">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-blue-600">{task.title}</p>
                      <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                        示例
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Platform: {task.platform} | Commission: {task.commission} USDT
                    </p>
                    <p className="text-xs text-gray-600 mt-2 line-clamp-2">{task.description}</p>
                  </div>
                ))}
              </div>
            </div>
            
            {user?.role === UserRole.PUBLISHER && (
              <Link
                to="/dashboard/publisher/create-task"
                className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
              >
                Create Your First Task
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
