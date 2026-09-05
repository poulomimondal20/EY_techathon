import { Bot, LayoutDashboard, Settings, User } from 'lucide-react';
import { Page } from '../App';

interface SidebarProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
}

export function Sidebar({ currentPage, onNavigate }: SidebarProps) {
  const isAgentPage = ['clinical-trial', 'market-insights', 'drug-repurposing', 'drug-discovery', 'competitor-analysis', 'deep-research', 'esg', 'medicine-validation'].includes(currentPage);
  
  return (
    <div className="w-16 bg-gradient-to-b from-[#0f1722] to-[#1a2533] border-r border-[#2a3f5f] flex flex-col items-center py-6 gap-4 shadow-2xl">
      <div className="mb-8">
        <div className="w-10 h-10 bg-gradient-to-br from-[#4ade80] to-[#22d3ee] rounded-lg flex items-center justify-center shadow-lg">
          <LayoutDashboard className="w-6 h-6 text-white" />
        </div>
      </div>

      <button
        onClick={() => onNavigate('dashboard')}
        className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all ${
          currentPage === 'dashboard'
            ? 'bg-gradient-to-br from-[#4ade80] to-[#22d3ee] text-white shadow-lg'
            : 'text-gray-400 hover:bg-[#2a3f5f]'
        }`}
        title="Dashboard"
      >
        <LayoutDashboard className="w-6 h-6" />
      </button>

      <button
        onClick={() => onNavigate('chat')}
        className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all ${
          currentPage === 'chat' || isAgentPage
            ? 'bg-gradient-to-br from-[#4ade80] to-[#22d3ee] text-white shadow-lg'
            : 'text-gray-400 hover:bg-[#2a3f5f]'
        }`}
        title="AI Chat"
      >
        <Bot className="w-6 h-6" />
      </button>

      <div className="flex-1" />

      <button
        onClick={() => onNavigate('settings')}
        className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all ${
          currentPage === 'settings'
            ? 'bg-gradient-to-br from-[#4ade80] to-[#22d3ee] text-white shadow-lg'
            : 'text-gray-400 hover:bg-[#2a3f5f]'
        }`}
        title="Settings"
      >
        <Settings className="w-5 h-5" />
      </button>

      <button
        onClick={() => onNavigate('profile')}
        className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all ${
          currentPage === 'profile'
            ? 'bg-gradient-to-br from-[#4ade80] to-[#22d3ee] text-white shadow-lg'
            : 'text-gray-400 hover:bg-[#2a3f5f]'
        }`}
        title="Profile"
      >
        <User className="w-5 h-5" />
      </button>
    </div>
  );
}