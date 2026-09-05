import { TrendingUp, CheckCircle2, Clock, Target, ArrowRight, Activity, Beaker, AlertTriangle, Award, BarChart3, Users } from 'lucide-react';
import { NewsWidget } from './widgets/NewsWidget';

interface DashboardProps {
  onOpenChat: () => void;
}

export function Dashboard({ onOpenChat }: DashboardProps) {
  return (
    <div className="p-8 space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-4xl mb-2">Welcome to DrugIQ</h1>
        <p className="text-gray-400">Your pharmaceutical intelligence operating system powered by AI</p>
      </div>

      {/* Start AI Chat Section */}
      <div className="bg-gradient-to-r from-[#4ade80] to-[#22d3ee] rounded-2xl p-8 shadow-2xl">
        <div className="flex items-center gap-6">
          <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center flex-shrink-0 shadow-lg">
            <Activity className="w-10 h-10 text-[#22d3ee]" />
          </div>
          <div className="flex-1">
            <h2 className="text-3xl text-white mb-2">Start AI Analysis</h2>
            <p className="text-white/90">
              Leverage 8 specialized AI agents for drug discovery, competitor analysis, clinical trials, market insights, and more...
            </p>
          </div>
          <button
            onClick={onOpenChat}
            className="bg-white text-[#22d3ee] px-8 py-4 rounded-xl flex items-center gap-3 hover:bg-gray-50 transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            <Activity className="w-6 h-6" />
            Launch AI Chat
          </button>
        </div>
      </div>

      {/* News Widget */}
      <NewsWidget />

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-[#0d1b2e] to-[#1a2942] border border-[#1e3a5f] rounded-xl p-6 hover:border-[#fbbf24] transition-all hover:shadow-xl">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-gray-400 text-sm mb-1">Active Projects</p>
              <p className="text-4xl mb-1">24</p>
              <p className="text-sm text-green-400 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                +8 this month
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-400/20 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-blue-400" />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-[#0d1b2e] to-[#1a2942] border border-[#1e3a5f] rounded-xl p-6 hover:border-[#fbbf24] transition-all hover:shadow-xl">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-gray-400 text-sm mb-1">Analyses Completed</p>
              <p className="text-4xl mb-1">1,247</p>
              <p className="text-sm text-green-400 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                +189 this week
              </p>
            </div>
            <div className="w-12 h-12 bg-green-400/20 rounded-lg flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6 text-green-400" />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-[#0d1b2e] to-[#1a2942] border border-[#1e3a5f] rounded-xl p-6 hover:border-[#fbbf24] transition-all hover:shadow-xl">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-gray-400 text-sm mb-1">Time Saved</p>
              <p className="text-4xl mb-1">4,280h</p>
              <p className="text-sm text-gray-400">vs. manual research</p>
            </div>
            <div className="w-12 h-12 bg-purple-400/20 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-purple-400" />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-[#0d1b2e] to-[#1a2942] border border-[#1e3a5f] rounded-xl p-6 hover:border-[#fbbf24] transition-all hover:shadow-xl">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-gray-400 text-sm mb-1">Avg Confidence Score</p>
              <p className="text-4xl mb-1">96.8%</p>
              <p className="text-sm text-green-400 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                +3.2% improvement
              </p>
            </div>
            <div className="w-12 h-12 bg-orange-400/20 rounded-lg flex items-center justify-center">
              <Award className="w-6 h-6 text-orange-400" />
            </div>
          </div>
        </div>
      </div>

      {/* AI Agents Overview */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-2xl mb-2">AI Agent Analytics</h3>
            <p className="text-gray-400">Performance metrics across all specialized agents</p>
          </div>
        </div>

        <div className="grid grid-cols-4 gap-4">
          <div className="bg-[#0d1b2e] border border-blue-400/30 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-blue-400/20 rounded flex items-center justify-center">
                <BarChart3 className="w-4 h-4 text-blue-400" />
              </div>
              <span className="text-sm">Clinical Trial</span>
            </div>
            <p className="text-2xl mb-1">287</p>
            <p className="text-xs text-gray-400">Analyses this month</p>
          </div>

          <div className="bg-[#0d1b2e] border border-green-400/30 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-green-400/20 rounded flex items-center justify-center">
                <TrendingUp className="w-4 h-4 text-green-400" />
              </div>
              <span className="text-sm">Market Insights</span>
            </div>
            <p className="text-2xl mb-1">156</p>
            <p className="text-xs text-gray-400">Reports generated</p>
          </div>

          <div className="bg-[#0d1b2e] border border-purple-400/30 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-purple-400/20 rounded flex items-center justify-center">
                <Beaker className="w-4 h-4 text-purple-400" />
              </div>
              <span className="text-sm">Drug Discovery</span>
            </div>
            <p className="text-2xl mb-1">423</p>
            <p className="text-xs text-gray-400">Compounds identified</p>
          </div>

          <div className="bg-[#0d1b2e] border border-orange-400/30 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-orange-400/20 rounded flex items-center justify-center">
                <Users className="w-4 h-4 text-orange-400" />
              </div>
              <span className="text-sm">Competitor Analysis</span>
            </div>
            <p className="text-2xl mb-1">198</p>
            <p className="text-xs text-gray-400">Insights delivered</p>
          </div>
        </div>
      </div>

      {/* Quick Start Analysis */}
      <div>
        <h3 className="text-2xl mb-2">Quick Start Analysis</h3>
        <p className="text-gray-400 mb-6">Launch a new AI-powered analysis in seconds</p>

        <div className="grid grid-cols-3 gap-6">
          <button className="bg-gradient-to-br from-[#0d1b2e] to-[#1a2942] border border-[#1e3a5f] rounded-xl p-6 text-left hover:border-[#fbbf24] transition-all hover:shadow-xl transform hover:scale-105 group">
            <div className="flex items-start justify-between mb-4">
              <TrendingUp className="w-10 h-10 text-blue-400" />
              <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-[#fbbf24] transition-colors" />
            </div>
            <h4 className="text-lg mb-2">Competitor Analysis</h4>
            <p className="text-sm text-gray-400">Track competitive landscape and pipeline intelligence</p>
          </button>

          <button className="bg-gradient-to-br from-[#0d1b2e] to-[#1a2942] border border-[#1e3a5f] rounded-xl p-6 text-left hover:border-[#fbbf24] transition-all hover:shadow-xl transform hover:scale-105 group">
            <div className="flex items-start justify-between mb-4">
              <Beaker className="w-10 h-10 text-purple-400" />
              <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-[#fbbf24] transition-colors" />
            </div>
            <h4 className="text-lg mb-2">Drug Discovery</h4>
            <p className="text-sm text-gray-400">Discover novel compounds and therapeutic targets</p>
          </button>

          <button className="bg-gradient-to-br from-[#0d1b2e] to-[#1a2942] border border-[#1e3a5f] rounded-xl p-6 text-left hover:border-[#fbbf24] transition-all hover:shadow-xl transform hover:scale-105 group">
            <div className="flex items-start justify-between mb-4">
              <Target className="w-10 h-10 text-green-400" />
              <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-[#fbbf24] transition-colors" />
            </div>
            <h4 className="text-lg mb-2">Drug Repurposing</h4>
            <p className="text-sm text-gray-400">Identify new therapeutic uses for existing drugs</p>
          </button>
        </div>
      </div>

      {/* Recent Analyses */}
      <div className="grid grid-cols-2 gap-6">
        <div>
          <h3 className="text-2xl mb-2">Recent Analyses</h3>
          <p className="text-gray-400 mb-6">Your latest AI-powered insights</p>

          <div className="space-y-4">
            <div className="bg-gradient-to-r from-[#0d1b2e] to-[#1a2942] border border-[#1e3a5f] rounded-xl p-6 hover:border-[#fbbf24] transition-all cursor-pointer group hover:shadow-xl">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="text-lg mb-2">Keytruda Competitive Landscape Q4 2024</h4>
                  <div className="flex items-center gap-3 text-sm text-gray-400">
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                      <span className="text-green-400">Competitor Analysis</span>
                    </span>
                    <span>•</span>
                    <span>Confidence: 97.2%</span>
                    <span>•</span>
                    <span>2h ago</span>
                  </div>
                </div>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-green-400/10 text-green-400 border border-green-400/30">
                  Complete
                </span>
              </div>
              <div className="flex items-center gap-2 pt-3 border-t border-[#1e3a5f]">
                <CheckCircle2 className="w-4 h-4 text-green-400" />
                <span className="text-xs text-gray-400">34 competitive insights • 12 pipeline updates</span>
              </div>
            </div>

            <div className="bg-gradient-to-r from-[#0d1b2e] to-[#1a2942] border border-[#1e3a5f] rounded-xl p-6 hover:border-[#fbbf24] transition-all cursor-pointer group hover:shadow-xl">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="text-lg mb-2">Novel KRAS G12C Inhibitor Discovery</h4>
                  <div className="flex items-center gap-3 text-sm text-gray-400">
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></span>
                      <span className="text-purple-400">Drug Discovery</span>
                    </span>
                    <span>•</span>
                    <span>Confidence: 91.8%</span>
                    <span>•</span>
                    <span>4h ago</span>
                  </div>
                </div>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-purple-400/10 text-purple-400 border border-purple-400/30">
                  Processing
                </span>
              </div>
              <div className="flex items-center gap-2 pt-3 border-t border-[#1e3a5f]">
                <Activity className="w-4 h-4 text-purple-400 animate-pulse" />
                <span className="text-xs text-gray-400">Analyzing 247 compounds • 68% complete</span>
              </div>
            </div>

            <div className="bg-gradient-to-r from-[#0d1b2e] to-[#1a2942] border border-[#1e3a5f] rounded-xl p-6 hover:border-[#fbbf24] transition-all cursor-pointer group hover:shadow-xl">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="text-lg mb-2">Metformin Repurposing: Alzheimer's Disease</h4>
                  <div className="flex items-center gap-3 text-sm text-gray-400">
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
                      <span className="text-blue-400">Drug Repurposing</span>
                    </span>
                    <span>•</span>
                    <span>Confidence: 94.5%</span>
                    <span>•</span>
                    <span>6h ago</span>
                  </div>
                </div>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-green-400/10 text-green-400 border border-green-400/30">
                  Complete
                </span>
              </div>
              <div className="flex items-center gap-2 pt-3 border-t border-[#1e3a5f]">
                <CheckCircle2 className="w-4 h-4 text-green-400" />
                <span className="text-xs text-gray-400">18 clinical studies reviewed • 5 opportunities identified</span>
              </div>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-2xl mb-2">Intelligence Alerts</h3>
          <p className="text-gray-400 mb-6">Critical updates and opportunities</p>

          <div className="space-y-4">
            <div className="bg-gradient-to-r from-red-400/5 to-transparent border border-red-400/30 rounded-xl p-6 hover:border-red-400 transition-all">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-red-400/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <AlertTriangle className="w-5 h-5 text-red-400" />
                </div>
                <div className="flex-1">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-red-400/10 text-red-400 mb-2">
                    CRITICAL
                  </span>
                  <h4 className="mb-2">FDA Breakthrough Therapy Designation</h4>
                  <p className="text-sm text-gray-400 mb-3">
                    Competitor drug BIO-123 received breakthrough designation for non-small cell lung cancer treatment
                  </p>
                  <p className="text-xs text-gray-500">30 minutes ago</p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-r from-[#fbbf24]/5 to-transparent border border-[#fbbf24]/30 rounded-xl p-6 hover:border-[#fbbf24] transition-all">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-[#fbbf24]/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <TrendingUp className="w-5 h-5 text-[#fbbf24]" />
                </div>
                <div className="flex-1">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-[#fbbf24]/10 text-[#fbbf24] mb-2">
                    OPPORTUNITY
                  </span>
                  <h4 className="mb-2">New Clinical Trial Data Published</h4>
                  <p className="text-sm text-gray-400 mb-3">
                    Phase III results for PD-1 inhibitors in melanoma show 23% improvement in progression-free survival
                  </p>
                  <p className="text-xs text-gray-500">2 hours ago</p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-r from-blue-400/5 to-transparent border border-blue-400/30 rounded-xl p-6 hover:border-blue-400 transition-all">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-blue-400/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <Target className="w-5 h-5 text-blue-400" />
                </div>
                <div className="flex-1">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-400/10 text-blue-400 mb-2">
                    MARKET INTEL
                  </span>
                  <h4 className="mb-2">Patent Expiration Alert</h4>
                  <p className="text-sm text-gray-400 mb-3">
                    Humira biosimilar opportunity in EU markets - patent expires Q2 2025
                  </p>
                  <p className="text-xs text-gray-500">5 hours ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}