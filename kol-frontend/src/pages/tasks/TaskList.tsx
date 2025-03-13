import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import { Task, TaskStatus } from '../../types';
import { getSampleTasks } from '../../utils/sampleTasks';
import toast from 'react-hot-toast';

const TaskList = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await api.get('/tasks');
        setTasks(response.data);
      } catch (error) {
        toast.error('Failed to load tasks');
      } finally {
        setLoading(false);
      }
    };
    
    fetchTasks();
  }, []);
  
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">ACF Spark Tasks</h1>
      </div>
      
      {loading ? (
        <div>Loading tasks...</div>
      ) : tasks.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tasks.map((task) => (
            <Link key={task.id} to={`/dashboard/tasks/${task.id}`} className="block">
              <div className="bg-white shadow rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                <div className="p-6">
                  <div className="flex justify-between items-start">
                    <h2 className="text-lg font-semibold text-blue-600 mb-2">{task.title}</h2>
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
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">{task.description}</p>
                  <div className="flex justify-between text-sm text-gray-500">
                    <span>Platform: {task.platform}</span>
                    <span>{task.commission} USDT</span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div>
          <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="text-lg font-medium text-blue-800 mb-2">示例营销任务</h3>
            <p className="text-sm text-blue-600 mb-2">以下是示例任务，展示平台上可能的营销需求。注册并完成个人资料后，您可以开始接受真实任务。</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {getSampleTasks().map((task) => (
              <div key={task.id} className="bg-white shadow rounded-lg overflow-hidden border border-blue-100">
                <div className="p-6">
                  <div className="flex justify-between items-start">
                    <h2 className="text-lg font-semibold text-blue-600 mb-2">{task.title}</h2>
                    <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                      示例
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">{task.description}</p>
                  <div className="mb-3">
                    <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">要求:</h3>
                    <p className="text-xs text-gray-600 line-clamp-2">{task.requirements}</p>
                  </div>
                  <div className="flex justify-between text-sm text-gray-500">
                    <span>Platform: {task.platform}</span>
                    <span>{task.commission} USDT</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskList;
