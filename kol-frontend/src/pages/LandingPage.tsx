import { useNavigate } from 'react-router-dom';
import { UserRole } from '../types';

const LandingPage = () => {
  const navigate = useNavigate();
  
  const handleCardClick = (role: UserRole) => {
    // Store the selected role in localStorage for registration
    localStorage.setItem('selectedRole', role);
    // Navigate to sample tasks view
    navigate('/sample-tasks');
  };
  
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100">
      <div className="max-w-4xl w-full p-6">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-extrabold text-blue-600">ACF Spark</h1>
          <p className="mt-3 text-xl text-gray-600">
            Connect KOLs with publishers for content creation
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* KOL Card */}
          <div 
            className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow cursor-pointer"
            onClick={() => handleCardClick(UserRole.KOL)}
          >
            <div className="p-8">
              <h2 className="text-2xl font-bold text-blue-600 mb-4">我是 KOL</h2>
              <p className="text-gray-600 mb-6">
                作为意见领袖，您可以接受品牌任务，在社交媒体上分享内容并获得报酬。
              </p>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">支持 Twitter, Instagram, YouTube 等平台</span>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                  查看任务
                </button>
              </div>
            </div>
          </div>
          
          {/* Publisher Card */}
          <div 
            className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow cursor-pointer"
            onClick={() => handleCardClick(UserRole.PUBLISHER)}
          >
            <div className="p-8">
              <h2 className="text-2xl font-bold text-blue-600 mb-4">我是发布者</h2>
              <p className="text-gray-600 mb-6">
                作为品牌或营销机构，您可以发布任务，寻找合适的KOL为您的产品或服务进行推广。
              </p>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">轻松管理营销活动</span>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                  发布任务
                </button>
              </div>
            </div>
          </div>
        </div>
        
        {/* Removed login/register links as per user request */}
      </div>
    </div>
  );
};

export default LandingPage;
