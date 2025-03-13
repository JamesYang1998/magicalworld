import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Task, UserRole } from '../types';

const SampleTasksPage = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const navigate = useNavigate();
  const selectedRole = localStorage.getItem('selectedRole') as UserRole || UserRole.KOL;
  
  useEffect(() => {
    // Load sample tasks
    setTasks(getSampleTasks());
  }, []);
  
  const handleBackToHome = () => {
    navigate('/');
  };
  
  const handleRegister = () => {
    navigate('/register');
  };
  
  // Function to generate sample tasks
  const getSampleTasks = (): Task[] => {
    return [
      {
        id: -1, // Negative IDs for sample tasks
        title: 'Sonic 新产品宣发活动',
        description: 'Sonic项目需要对新款游戏机进行社交媒体宣传，重点突出其低延迟和高音质特性。',
        requirements: '需要至少一条产品使用图片和一条视频展示产品特性。内容需包含官方标签 #SonicAudio #GamingRevolution',
        platform: 'TWITTER',
        platform_requirements: '账户粉丝至少1000名粉丝，以社交内容以科技游戏为主。',
        commission: 400,
        status: 'OPEN',
        created_at: new Date().toISOString(),
        publisher_id: -1,
        deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: -2,
        title: 'CryptoWave 市场活动推广',
        description: 'CryptoWave平台寻找KOL推广其新的DeFi产品，需要解释产品功能并吸引潜在用户。',
        requirements: '创建3-5分钟视频，详细介绍CryptoWave的DeFi产品功能和优势。包含注册链接。',
        platform: 'YOUTUBE',
        platform_requirements: '频道订阅者至少5000人，内容以加密货币或金融为主。',
        commission: 600,
        status: 'OPEN',
        created_at: new Date().toISOString(),
        publisher_id: -2,
        deadline: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: -3,
        title: 'FashionPlus 夏季系列宣传',
        description: 'FashionPlus寻找时尚博主推广其2023夏季服装系列，展示产品并分享配搭建议。',
        requirements: '发布至少3张高质量照片，展示FashionPlus夏季系列搭配。包含品牌标签和专属代码。',
        platform: 'INSTAGRAM',
        platform_requirements: '账户粉丝至少3000人，内容以时尚生活方式为主。',
        commission: 350,
        status: 'OPEN',
        created_at: new Date().toISOString(),
        publisher_id: -3,
        deadline: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
      }
    ];
  };
  
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <button onClick={handleBackToHome} className="text-xl font-bold text-blue-600">ACF Spark</button>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Link to="/login" className="text-sm text-gray-700 hover:text-gray-900">
                登录
              </Link>
              <button 
                onClick={handleRegister}
                className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                注册
              </button>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main>
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold">示例营销任务</h1>
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                {selectedRole === UserRole.KOL ? '我是 KOL' : '我是发布者'}
              </span>
            </div>
            <p className="mt-2 text-gray-600">
              {selectedRole === UserRole.KOL 
                ? '以下是您可以接受的示例任务，注册后即可开始接单赚取佣金。' 
                : '以下是平台上的示例任务，注册后您可以发布类似的营销需求。'}
            </p>
          </div>
          
          <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="text-lg font-medium text-blue-800 mb-2">ACF Spark 平台优势</h3>
            <p className="text-sm text-blue-600 mb-2">
              {selectedRole === UserRole.KOL 
                ? '作为KOL，您可以在平台上接受来自各品牌的营销任务，展示您的影响力并获得报酬。' 
                : '作为发布者，您可以轻松找到合适的KOL为您的产品或服务进行推广，提高品牌知名度。'}
            </p>
            <div className="mt-3">
              <button
                onClick={handleRegister}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
              >
                立即注册
              </button>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tasks.map((task) => (
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
                  <div className="mb-3">
                    <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">平台要求:</h3>
                    <p className="text-xs text-gray-600 line-clamp-2">{task.platform_requirements}</p>
                  </div>
                  <div className="flex justify-between text-sm text-gray-500">
                    <span>Platform: {task.platform}</span>
                    <span>{task.commission} USDT</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-8 text-center">
            <p className="text-gray-600 mb-4">注册 ACF Spark 开始您的内容创作之旅</p>
            <button
              onClick={handleRegister}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
            >
              立即注册
            </button>
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            &copy; {new Date().getFullYear()} ACF Spark. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default SampleTasksPage;
