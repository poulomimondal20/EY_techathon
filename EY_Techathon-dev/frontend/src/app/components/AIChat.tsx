import { Activity, Sparkles, Zap, Globe, TrendingUp, FileText, Leaf, TestTube, Send, ShieldCheck } from 'lucide-react';
import { Agent } from '../App';
import { useState } from 'react';

interface AIChatProps {
  onSelectAgent: (agent: Agent) => void;
}

export function AIChat({ onSelectAgent }: AIChatProps) {
  const [hoveredAgent, setHoveredAgent] = useState<string | null>(null);

  const agents = [
    { id: 'clinical-trial' as Agent, icon: <TestTube className="w-5 h-5" />, name: 'Clinical Trial' },
    { id: 'market-insights' as Agent, icon: <TrendingUp className="w-5 h-5" />, name: 'Market Insights' },
    { id: 'drug-repurposing' as Agent, icon: <Zap className="w-5 h-5" />, name: 'Drug Repurposing' },
    { id: 'drug-discovery' as Agent, icon: <Sparkles className="w-5 h-5" />, name: 'Drug Discovery' },
    { id: 'competitor-analysis' as Agent, icon: <Globe className="w-5 h-5" />, name: 'Competitor Analysis' },
    { id: 'deep-research' as Agent, icon: <FileText className="w-5 h-5" />, name: 'Deep Research' },
    { id: 'esg' as Agent, icon: <Leaf className="w-5 h-5" />, name: 'ESG' },
    { id: 'medicine-validation' as Agent, icon: <ShieldCheck className="w-5 h-5" />, name: 'Medicine Validation' },
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-full p-8">
      <div className="max-w-4xl w-full space-y-12">
        {/* AI Icon */}
        <div className="flex justify-center">
          <div className="w-24 h-24 bg-gradient-to-br from-[#4ade80] to-[#22d3ee] rounded-full flex items-center justify-center shadow-2xl">
            <Activity className="w-12 h-12 text-white" />
          </div>
        </div>

        {/* Search Input */}
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-2xl p-2 shadow-xl">
          <textarea
            placeholder="Write your prompt here..."
            className="w-full bg-transparent px-4 py-4 resize-none outline-none min-h-[120px]"
            rows={4}
          />
          <div className="flex items-center justify-between px-2 pt-2 border-t border-[#2a3f5f]">
            <div className="flex items-center gap-2">
              {agents.map((agent) => (
                <div key={agent.id} className="relative">
                  <button
                    onClick={() => onSelectAgent(agent.id)}
                    onMouseEnter={() => setHoveredAgent(agent.id)}
                    onMouseLeave={() => setHoveredAgent(null)}
                    className="w-9 h-9 rounded-lg hover:bg-gradient-to-br hover:from-[#4ade80] hover:to-[#22d3ee] transition-all flex items-center justify-center text-gray-400 hover:text-white"
                  >
                    {agent.icon}
                  </button>
                  {hoveredAgent === agent.id && (
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1 bg-gradient-to-br from-[#2a3f5f] to-[#1e3a5f] text-white text-xs rounded-lg whitespace-nowrap shadow-lg z-10">
                      {agent.name}
                    </div>
                  )}
                </div>
              ))}
            </div>
            <button className="bg-gradient-to-r from-[#4ade80] to-[#22d3ee] hover:from-[#22d3ee] hover:to-[#4ade80] transition-all rounded-lg px-4 py-2 flex items-center gap-2 shadow-lg">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}