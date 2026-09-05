import { Bell, Shield, Database, Zap, Globe } from 'lucide-react';

export function Settings() {
  return (
    <div className="max-w-4xl mx-auto p-8">
      <div className="mb-8">
        <h1 className="text-3xl mb-2">Settings</h1>
        <p className="text-gray-400">Manage your DrugIQ preferences and account settings</p>
      </div>

      <div className="space-y-6">
        {/* Notifications */}
        <div className="bg-[#0d1b2e] border border-[#1e3a5f] rounded-xl p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-[#1e3a5f] rounded-lg flex items-center justify-center flex-shrink-0">
              <Bell className="w-6 h-6 text-[#fbbf24]" />
            </div>
            <div className="flex-1">
              <h3 className="mb-2">Notifications</h3>
              <p className="text-sm text-gray-400 mb-4">Configure how you receive intelligence alerts and updates</p>
              
              <div className="space-y-3">
                <label className="flex items-center justify-between p-3 bg-[#0a1628] rounded-lg cursor-pointer hover:bg-[#0f1f35] transition-colors">
                  <span className="text-sm">Real-time analysis alerts</span>
                  <input type="checkbox" defaultChecked className="w-5 h-5" />
                </label>
                <label className="flex items-center justify-between p-3 bg-[#0a1628] rounded-lg cursor-pointer hover:bg-[#0f1f35] transition-colors">
                  <span className="text-sm">Competitor activity updates</span>
                  <input type="checkbox" defaultChecked className="w-5 h-5" />
                </label>
                <label className="flex items-center justify-between p-3 bg-[#0a1628] rounded-lg cursor-pointer hover:bg-[#0f1f35] transition-colors">
                  <span className="text-sm">Clinical trial results</span>
                  <input type="checkbox" defaultChecked className="w-5 h-5" />
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Privacy & Security */}
        <div className="bg-[#0d1b2e] border border-[#1e3a5f] rounded-xl p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-[#1e3a5f] rounded-lg flex items-center justify-center flex-shrink-0">
              <Shield className="w-6 h-6 text-[#fbbf24]" />
            </div>
            <div className="flex-1">
              <h3 className="mb-2">Privacy & Security</h3>
              <p className="text-sm text-gray-400 mb-4">Control your data and security preferences</p>
              
              <div className="space-y-3">
                <label className="flex items-center justify-between p-3 bg-[#0a1628] rounded-lg cursor-pointer hover:bg-[#0f1f35] transition-colors">
                  <span className="text-sm">Two-factor authentication</span>
                  <input type="checkbox" defaultChecked className="w-5 h-5" />
                </label>
                <label className="flex items-center justify-between p-3 bg-[#0a1628] rounded-lg cursor-pointer hover:bg-[#0f1f35] transition-colors">
                  <span className="text-sm">Data encryption</span>
                  <input type="checkbox" defaultChecked className="w-5 h-5" />
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Data Preferences */}
        <div className="bg-[#0d1b2e] border border-[#1e3a5f] rounded-xl p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-[#1e3a5f] rounded-lg flex items-center justify-center flex-shrink-0">
              <Database className="w-6 h-6 text-[#fbbf24]" />
            </div>
            <div className="flex-1">
              <h3 className="mb-2">Data Sources</h3>
              <p className="text-sm text-gray-400 mb-4">Manage which data sources are used in analysis</p>
              
              <div className="space-y-3">
                <label className="flex items-center justify-between p-3 bg-[#0a1628] rounded-lg cursor-pointer hover:bg-[#0f1f35] transition-colors">
                  <span className="text-sm">PubMed</span>
                  <input type="checkbox" defaultChecked className="w-5 h-5" />
                </label>
                <label className="flex items-center justify-between p-3 bg-[#0a1628] rounded-lg cursor-pointer hover:bg-[#0f1f35] transition-colors">
                  <span className="text-sm">ClinicalTrials.gov</span>
                  <input type="checkbox" defaultChecked className="w-5 h-5" />
                </label>
                <label className="flex items-center justify-between p-3 bg-[#0a1628] rounded-lg cursor-pointer hover:bg-[#0f1f35] transition-colors">
                  <span className="text-sm">FDA Databases</span>
                  <input type="checkbox" defaultChecked className="w-5 h-5" />
                </label>
                <label className="flex items-center justify-between p-3 bg-[#0a1628] rounded-lg cursor-pointer hover:bg-[#0f1f35] transition-colors">
                  <span className="text-sm">Patent databases</span>
                  <input type="checkbox" defaultChecked className="w-5 h-5" />
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* AI Model Settings */}
        <div className="bg-[#0d1b2e] border border-[#1e3a5f] rounded-xl p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-[#1e3a5f] rounded-lg flex items-center justify-center flex-shrink-0">
              <Zap className="w-6 h-6 text-[#fbbf24]" />
            </div>
            <div className="flex-1">
              <h3 className="mb-2">AI Model Preferences</h3>
              <p className="text-sm text-gray-400 mb-4">Customize AI analysis behavior</p>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm mb-2 block">Analysis Depth</label>
                  <select className="w-full bg-[#0a1628] border border-[#1e3a5f] rounded-lg px-4 py-2 outline-none">
                    <option>Standard</option>
                    <option>Deep</option>
                    <option>Comprehensive</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm mb-2 block">Confidence Threshold</label>
                  <input 
                    type="range" 
                    min="70" 
                    max="99" 
                    defaultValue="85" 
                    className="w-full"
                  />
                  <p className="text-xs text-gray-400 mt-1">Minimum: 85%</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Language & Region */}
        <div className="bg-[#0d1b2e] border border-[#1e3a5f] rounded-xl p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-[#1e3a5f] rounded-lg flex items-center justify-center flex-shrink-0">
              <Globe className="w-6 h-6 text-[#fbbf24]" />
            </div>
            <div className="flex-1">
              <h3 className="mb-2">Language & Region</h3>
              <p className="text-sm text-gray-400 mb-4">Set your language and regional preferences</p>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm mb-2 block">Language</label>
                  <select className="w-full bg-[#0a1628] border border-[#1e3a5f] rounded-lg px-4 py-2 outline-none">
                    <option>English (US)</option>
                    <option>English (UK)</option>
                    <option>German</option>
                    <option>French</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm mb-2 block">Region</label>
                  <select className="w-full bg-[#0a1628] border border-[#1e3a5f] rounded-lg px-4 py-2 outline-none">
                    <option>United States</option>
                    <option>European Union</option>
                    <option>Asia Pacific</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
