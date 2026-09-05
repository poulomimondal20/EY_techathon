import { useState } from 'react';
import { Dashboard } from './components/Dashboard';
import { AIChat } from './components/AIChat';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { NotificationSystem } from './components/NotificationSystem';
import { Settings } from './components/Settings';
import { Profile } from './components/Profile';
import { AgentPage } from './components/AgentPage';

export type Agent = 'clinical-trial' | 'market-insights' | 'drug-repurposing' | 'drug-discovery' | 'competitor-analysis' | 'deep-research' | 'esg' | 'medicine-validation';
export type Page = 'dashboard' | 'chat' | 'settings' | 'profile' | Agent;

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');

  return (
    <div className="flex h-screen bg-[#0a1628] text-white">
      <Sidebar currentPage={currentPage} onNavigate={setCurrentPage} />
      
      <div className="flex-1 flex flex-col">
        <TopBar />
        
        <main className="flex-1 overflow-auto">
          {currentPage === 'dashboard' && <Dashboard onOpenChat={() => setCurrentPage('chat')} />}
          {currentPage === 'chat' && <AIChat onSelectAgent={(agent) => setCurrentPage(agent)} />}
          {currentPage === 'settings' && <Settings />}
          {currentPage === 'profile' && <Profile />}
          {(currentPage === 'clinical-trial' || 
            currentPage === 'market-insights' || 
            currentPage === 'drug-repurposing' || 
            currentPage === 'drug-discovery' || 
            currentPage === 'competitor-analysis' || 
            currentPage === 'deep-research' || 
            currentPage === 'esg' ||
            currentPage === 'medicine-validation') && (
            <AgentPage agent={currentPage} onBack={() => setCurrentPage('chat')} />
          )}
        </main>
      </div>

      <NotificationSystem />
    </div>
  );
}