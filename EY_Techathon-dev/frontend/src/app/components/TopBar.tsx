import { Building2 } from 'lucide-react';

export function TopBar() {
  return (
    <div className="h-16 border-b border-[#2a3f5f] bg-gradient-to-r from-[#0f1722] to-[#1a2533] flex items-center justify-between px-6 shadow-lg">
      <div className="flex items-center gap-3">
        <h1 className="text-xl">
          <span className="text-white">DRUG</span>
          <span className="bg-gradient-to-r from-[#4ade80] to-[#22d3ee] bg-clip-text text-transparent"> IQ</span>
        </h1>
        <p className="text-sm text-gray-400">Your AI-powered pharmaceutical intelligence system</p>
      </div>

      <div className="flex items-center gap-3 bg-gradient-to-r from-[#2a3f5f] to-[#1e3a5f] px-4 py-2 rounded-lg shadow-md">
        <div className="w-8 h-8 bg-gradient-to-br from-[#4ade80] to-[#22d3ee] rounded flex items-center justify-center">
          <Building2 className="w-5 h-5 text-white" />
        </div>
        <div className="flex flex-col">
          <span className="text-sm">COMPANY NAME</span>
          <span className="text-xs text-gray-400">Pharmaceutical Corp</span>
        </div>
      </div>
    </div>
  );
}