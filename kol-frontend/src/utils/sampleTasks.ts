import { Task, PlatformType, TaskStatus } from '../types';

// Generate a unique ID for sample tasks (negative to avoid conflicts with real tasks)
const generateSampleId = (): number => {
  return -Math.floor(Math.random() * 1000) - 1;
};

// Current date formatted as ISO string
const now = new Date().toISOString();

// Sample tasks data
export const sampleTasks: Task[] = [
  {
    id: generateSampleId(),
    title: 'Sonic 新产品宣发活动',
    description: 'Sonic项目需要对新款游戏耳机进行社交媒体宣传，重点突出其低延迟和高音质特性。',
    platform: PlatformType.TWITTER,
    commission: 400,
    requirements: '需要至少一张产品使用照片和一段视频展示产品特性。内容需包含官方标签 #SonicAudio #GamingRevolution',
    platform_requirements: '账户需有至少1000名粉丝，以往内容以科技或游戏为主。',
    word_count: 200,
    status: TaskStatus.OPEN,
    publisher_id: 0,
    created_at: now,
    updated_at: now
  },
  {
    id: generateSampleId(),
    title: 'CryptoWave 市场活动推广',
    description: 'CryptoWave平台寻找KOL推广其新的DeFi产品，需要解释产品功能并吸引潜在用户。',
    platform: PlatformType.YOUTUBE,
    commission: 600,
    requirements: '创建3-5分钟视频，详细介绍CryptoWave的DeFi产品功能和优势。包含注册链接。',
    platform_requirements: '频道订阅者至少5000人，内容以加密货币或金融为主。',
    word_count: 300,
    status: TaskStatus.OPEN,
    publisher_id: 0,
    created_at: now,
    updated_at: now
  },
  {
    id: generateSampleId(),
    title: 'FashionPlus 夏季系列宣传',
    description: 'FashionPlus寻找时尚博主推广其2023夏季服装系列，展示产品并分享搭配建议。',
    platform: PlatformType.INSTAGRAM,
    commission: 350,
    requirements: '发布至少3张高质量照片，展示FashionPlus夏季系列服装搭配。包含品牌标签和促销代码。',
    platform_requirements: '账户粉丝至少3000人，内容以时尚或生活方式为主。',
    word_count: 150,
    status: TaskStatus.OPEN,
    publisher_id: 0,
    created_at: now,
    updated_at: now
  }
];

// Function to get sample tasks
export const getSampleTasks = (count: number = 3): Task[] => {
  return sampleTasks.slice(0, count);
};
