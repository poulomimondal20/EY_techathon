import { ArrowLeft, Send, Download, FileText } from 'lucide-react';
import { Agent } from '../App';
import { useState } from 'react';
import { ClinicalTrialView, ClinicalTrialData } from './agents/ClinicalTrialView';
import { MarketInsightsView, MarketInsightsData } from './agents/MarketInsightsView';
import { CompetitorAnalysisView, CompetitorAnalysisData } from './agents/CompetitorAnalysisView';
import { DrugRepurposingView, DrugRepurposingData } from './agents/DrugRepurposingView';
import { MedicineValidationView, MedicineValidationData } from './agents/MedicineValidationView';
import { DrugDiscoveryView, DrugDiscoveryData } from './agents/DrugDiscoveryView';
import { DeepResearchView, DeepResearchData } from './agents/DeepResearchView';
import { ChatView } from './agents/ChatView';
import { ESGView } from './agents/ESGView';

const API_BASE_URL = 'http://localhost:8000';

interface AgentPageProps {
  agent: Agent;
  onBack: () => void;
}

const agentConfig = {
  'clinical-trial': {
    name: 'Clinical Trial Intelligence',
    description: 'Analyze clinical trial data, protocols, and outcomes',
    color: 'text-blue-400',
    bgColor: 'bg-blue-400/10',
    borderColor: 'border-blue-400/30',
  },
  'market-insights': {
    name: 'Market Insights',
    description: 'Get market analysis, pricing trends, and forecasts',
    color: 'text-green-400',
    bgColor: 'bg-green-400/10',
    borderColor: 'border-green-400/30',
  },
  'drug-repurposing': {
    name: 'Drug Repurposing',
    description: 'Identify new therapeutic uses for existing drugs',
    color: 'text-purple-400',
    bgColor: 'bg-purple-400/10',
    borderColor: 'border-purple-400/30',
  },
  'drug-discovery': {
    name: 'Drug Discovery',
    description: 'Discover novel compounds and therapeutic targets',
    color: 'text-orange-400',
    bgColor: 'bg-orange-400/10',
    borderColor: 'border-orange-400/30',
  },
  'competitor-analysis': {
    name: 'Competitor Analysis',
    description: 'Track competitive landscape and pipeline intelligence',
    color: 'text-red-400',
    bgColor: 'bg-red-400/10',
    borderColor: 'border-red-400/30',
  },
  'deep-research': {
    name: 'Deep Research',
    description: 'Comprehensive literature and patent analysis',
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-400/10',
    borderColor: 'border-cyan-400/30',
  },
  'esg': {
    name: 'ESG Analysis',
    description: 'Environmental, Social, and Governance insights',
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-400/10',
    borderColor: 'border-emerald-400/30',
  },
  'medicine-validation': {
    name: 'Medicine Validation',
    description: 'Verify regulatory status and safety information',
    color: 'text-teal-400',
    bgColor: 'bg-teal-400/10',
    borderColor: 'border-teal-400/30',
  },
};

export function AgentPage({ agent, onBack }: AgentPageProps) {
  const [input, setInput] = useState('');
  const [hasQuery, setHasQuery] = useState(false);
  const [queryText, setQueryText] = useState('');

  // Clinical Trial state
  const [clinicalTrialData, setClinicalTrialData] = useState<ClinicalTrialData | null>(null);
  const [clinicalTrialLoading, setClinicalTrialLoading] = useState(false);
  const [clinicalTrialError, setClinicalTrialError] = useState<string | null>(null);

  // Drug Repurposing state
  const [drugRepurposingData, setDrugRepurposingData] = useState<DrugRepurposingData | null>(null);
  const [drugRepurposingLoading, setDrugRepurposingLoading] = useState(false);
  const [drugRepurposingError, setDrugRepurposingError] = useState<string | null>(null);

  // Market Insights state
  const [marketInsightsData, setMarketInsightsData] = useState<MarketInsightsData | null>(null);
  const [marketInsightsLoading, setMarketInsightsLoading] = useState(false);
  const [marketInsightsError, setMarketInsightsError] = useState<string | null>(null);

  // Competitor Analysis state
  const [competitorData, setCompetitorData] = useState<CompetitorAnalysisData | null>(null);
  const [competitorLoading, setCompetitorLoading] = useState(false);
  const [competitorError, setCompetitorError] = useState<string | null>(null);

  // Medicine Validation state
  const [medicineData, setMedicineData] = useState<MedicineValidationData | null>(null);
  const [medicineLoading, setMedicineLoading] = useState(false);
  const [medicineError, setMedicineError] = useState<string | null>(null);

  // Drug Discovery state
  const [drugDiscoveryData, setDrugDiscoveryData] = useState<DrugDiscoveryData | null>(null);
  const [drugDiscoveryLoading, setDrugDiscoveryLoading] = useState(false);
  const [drugDiscoveryError, setDrugDiscoveryError] = useState<string | null>(null);

  // Deep Research state
  const [deepResearchData, setDeepResearchData] = useState<DeepResearchData | null>(null);
  const [deepResearchLoading, setDeepResearchLoading] = useState(false);
  const [deepResearchError, setDeepResearchError] = useState<string | null>(null);

  const config = agentConfig[agent];

  const handleSend = async () => {
    if (!input.trim()) return;

    const query = input.trim();
    setQueryText(query);
    setHasQuery(true);
    setInput('');

    // Handle Clinical Trial API call
    if (agent === 'clinical-trial') {
      setClinicalTrialLoading(true);
      setClinicalTrialError(null);
      setClinicalTrialData(null);

      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/clinical-trials/analyze`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.status === 'error') {
          throw new Error(result.error || 'Analysis failed');
        }

        setClinicalTrialData(result.data);
      } catch (error) {
        console.error('Clinical trial analysis error:', error);
        setClinicalTrialError(error instanceof Error ? error.message : 'Failed to analyze clinical trials');
      } finally {
        setClinicalTrialLoading(false);
      }
    }

    // Handle Drug Repurposing API call
    if (agent === 'drug-repurposing') {
      setDrugRepurposingLoading(true);
      setDrugRepurposingError(null);
      setDrugRepurposingData(null);

      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/drug-repurposing/analyze`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ drug_name: query, full_analysis: true }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.error) {
          throw new Error(result.error);
        }

        setDrugRepurposingData(result);
      } catch (error) {
        console.error('Drug repurposing analysis error:', error);
        setDrugRepurposingError(error instanceof Error ? error.message : 'Failed to analyze drug repurposing');
      } finally {
        setDrugRepurposingLoading(false);
      }
    }

    // Handle Market Insights API call
    if (agent === 'market-insights') {
      setMarketInsightsLoading(true);
      setMarketInsightsError(null);
      setMarketInsightsData(null);

      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/market-insights/analyze`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.status === 'error') {
          throw new Error(result.error || 'Analysis failed');
        }

        setMarketInsightsData(result.data);
      } catch (error) {
        console.error('Market insights analysis error:', error);
        setMarketInsightsError(error instanceof Error ? error.message : 'Failed to analyze market');
      } finally {
        setMarketInsightsLoading(false);
      }
    }

    // Handle Competitor Analysis API call
    if (agent === 'competitor-analysis') {
      setCompetitorLoading(true);
      setCompetitorError(null);
      setCompetitorData(null);

      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/competitor-analysis/analyze`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.status === 'error') {
          throw new Error(result.error || 'Analysis failed');
        }

        setCompetitorData(result.data);
      } catch (error) {
        console.error('Competitor analysis error:', error);
        setCompetitorError(error instanceof Error ? error.message : 'Failed to analyze competitors');
      } finally {
        setCompetitorLoading(false);
      }
    }

    // Handle Medicine Validation API call
    if (agent === 'medicine-validation') {
      setMedicineLoading(true);
      setMedicineError(null);
      setMedicineData(null);

      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/medicine-validation/validate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ medicine_name: query }),
        });

        if (!response.ok) {
          const err = await response.json().catch(() => ({}));
          throw new Error(err.detail || `HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.status === 'error') {
          throw new Error(result.error || 'Validation failed');
        }

        setMedicineData(result.data);
      } catch (error) {
        console.error('Medicine validation error:', error);
        setMedicineError(error instanceof Error ? error.message : 'Failed to validate medicine');
      } finally {
        setMedicineLoading(false);
      }
    }

    // Handle Drug Discovery API call
    if (agent === 'drug-discovery') {
      setDrugDiscoveryLoading(true);
      setDrugDiscoveryError(null);
      setDrugDiscoveryData(null);

      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/drug-discovery/execute`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.status === 'error') {
          throw new Error(result.error || 'Drug discovery failed');
        }

        // The response has workflow data at root level or in structured_output
        setDrugDiscoveryData(result.structured_output || result);
      } catch (error) {
        console.error('Drug discovery error:', error);
        setDrugDiscoveryError(error instanceof Error ? error.message : 'Failed to run drug discovery');
      } finally {
        setDrugDiscoveryLoading(false);
      }
    }

    // Handle Deep Research API call
    if (agent === 'deep-research') {
      setDeepResearchLoading(true);
      setDeepResearchError(null);
      setDeepResearchData(null);

      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/deep-research/execute`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.status === 'error') {
          throw new Error(result.error || 'Deep research failed');
        }

        // The response itself is the data (research_id, query, synthesis, papers, trials, etc.)
        setDeepResearchData(result.structured_output || result);
      } catch (error) {
        console.error('Deep research error:', error);
        setDeepResearchError(error instanceof Error ? error.message : 'Failed to run deep research');
      } finally {
        setDeepResearchLoading(false);
      }
    }
  };

  // Chat-style agents (markdown output) - only ESG uses chat now
  const chatAgents: string[] = [];

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-[#2a3f5f] bg-gradient-to-r from-[#0f1722] to-[#1a2533] px-6 py-4 shadow-lg">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="w-10 h-10 rounded-lg hover:bg-[#2a3f5f] transition-colors flex items-center justify-center"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-xl">{config.name}</h2>
            <p className="text-sm text-gray-400">{config.description}</p>
          </div>
        </div>
      </div>

      {/* Content Area */}
      {chatAgents.includes(agent) ? (
        <ChatView
          agent={agent}
          config={config}
          input={input}
          setInput={setInput}
          handleSend={handleSend}
          hasQuery={hasQuery}
        />
      ) : agent === 'esg' ? (
        <ESGView
          config={config}
          input={input}
          setInput={setInput}
          handleSend={handleSend}
          hasQuery={hasQuery}
        />
      ) : (
        <div className="flex-1 flex overflow-hidden">
          {/* Left Panel - Structured Output */}
          <div className="flex-1 overflow-auto p-6 border-r border-[#2a3f5f]">
            {!hasQuery ? (
              <div className="h-full flex items-center justify-center">
                <div className="text-center text-gray-400">
                  <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>Submit a query to see structured results</p>
                </div>
              </div>
            ) : (
              <>
                {agent === 'clinical-trial' && (
                  <ClinicalTrialView
                    data={clinicalTrialData}
                    isLoading={clinicalTrialLoading}
                    error={clinicalTrialError}
                  />
                )}
                {agent === 'drug-repurposing' && (
                  <DrugRepurposingView
                    data={drugRepurposingData}
                    isLoading={drugRepurposingLoading}
                    error={drugRepurposingError}
                  />
                )}
                {agent === 'market-insights' && (
                  <MarketInsightsView
                    data={marketInsightsData}
                    isLoading={marketInsightsLoading}
                    error={marketInsightsError}
                  />
                )}
                {agent === 'competitor-analysis' && (
                  <CompetitorAnalysisView
                    data={competitorData}
                    isLoading={competitorLoading}
                    error={competitorError}
                  />
                )}
                {agent === 'medicine-validation' && (
                  <MedicineValidationView
                    data={medicineData}
                    isLoading={medicineLoading}
                    error={medicineError}
                  />
                )}
                {agent === 'drug-discovery' && (
                  <DrugDiscoveryView
                    data={drugDiscoveryData}
                    isLoading={drugDiscoveryLoading}
                    error={drugDiscoveryError}
                  />
                )}
                {agent === 'deep-research' && (
                  <DeepResearchView
                    data={deepResearchData}
                    isLoading={deepResearchLoading}
                    error={deepResearchError}
                  />
                )}
              </>
            )}
          </div>

          {/* Right Panel - Input/Chat */}
          <div className="w-96 flex flex-col bg-gradient-to-br from-[#0f1722] to-[#1a2533]">
            <div className="flex-1 overflow-auto p-6">
              {hasQuery && (
                <div className="space-y-4">
                  <div className="bg-gradient-to-br from-[#4ade80] to-[#22d3ee] text-white px-4 py-3 rounded-xl">
                    <p className="text-sm">{queryText}</p>
                  </div>
                  {agent === 'clinical-trial' && (
                    <div className="bg-[#1a2533] border border-[#2a3f5f] px-4 py-3 rounded-xl">
                      {clinicalTrialLoading ? (
                        <p className="text-sm text-gray-300">Analyzing clinical trial pipeline...</p>
                      ) : clinicalTrialError ? (
                        <p className="text-sm text-red-400">Error: {clinicalTrialError}</p>
                      ) : clinicalTrialData ? (
                        <p className="text-sm text-gray-300">Analysis complete. View structured results in the left panel.</p>
                      ) : (
                        <p className="text-sm text-gray-300">Processing your query...</p>
                      )}
                    </div>
                  )}
                  {agent === 'drug-repurposing' && (
                    <div className="bg-[#1a2533] border border-[#2a3f5f] px-4 py-3 rounded-xl">
                      {drugRepurposingLoading ? (
                        <p className="text-sm text-gray-300">Analyzing drug repurposing opportunities...</p>
                      ) : drugRepurposingError ? (
                        <p className="text-sm text-red-400">Error: {drugRepurposingError}</p>
                      ) : drugRepurposingData ? (
                        <p className="text-sm text-gray-300">Analysis complete. View structured results in the left panel.</p>
                      ) : (
                        <p className="text-sm text-gray-300">Processing your query...</p>
                      )}
                    </div>
                  )}
                  {agent === 'market-insights' && (
                    <div className="bg-[#1a2533] border border-[#2a3f5f] px-4 py-3 rounded-xl">
                      {marketInsightsLoading ? (
                        <p className="text-sm text-gray-300">Analyzing market data...</p>
                      ) : marketInsightsError ? (
                        <p className="text-sm text-red-400">Error: {marketInsightsError}</p>
                      ) : marketInsightsData ? (
                        <p className="text-sm text-gray-300">Analysis complete. View structured results in the left panel.</p>
                      ) : (
                        <p className="text-sm text-gray-300">Processing your query...</p>
                      )}
                    </div>
                  )}
                  {agent === 'competitor-analysis' && (
                    <div className="bg-[#1a2533] border border-[#2a3f5f] px-4 py-3 rounded-xl">
                      {competitorLoading ? (
                        <p className="text-sm text-gray-300">Analyzing competitive landscape...</p>
                      ) : competitorError ? (
                        <p className="text-sm text-red-400">Error: {competitorError}</p>
                      ) : competitorData ? (
                        <p className="text-sm text-gray-300">Analysis complete. View structured results in the left panel.</p>
                      ) : (
                        <p className="text-sm text-gray-300">Processing your query...</p>
                      )}
                    </div>
                  )}
                  {agent === 'medicine-validation' && (
                    <div className="bg-[#1a2533] border border-[#2a3f5f] px-4 py-3 rounded-xl">
                      {medicineLoading ? (
                        <p className="text-sm text-gray-300">Validating medicine...</p>
                      ) : medicineError ? (
                        <p className="text-sm text-red-400">Error: {medicineError}</p>
                      ) : medicineData ? (
                        <p className="text-sm text-gray-300">Analysis complete. View structured results in the left panel.</p>
                      ) : (
                        <p className="text-sm text-gray-300">Processing your query...</p>
                      )}
                    </div>
                  )}
                  {agent === 'drug-discovery' && (
                    <div className="bg-[#1a2533] border border-[#2a3f5f] px-4 py-3 rounded-xl">
                      {drugDiscoveryLoading ? (
                        <p className="text-sm text-gray-300">Running drug discovery pipeline...</p>
                      ) : drugDiscoveryError ? (
                        <p className="text-sm text-red-400">Error: {drugDiscoveryError}</p>
                      ) : drugDiscoveryData ? (
                        <p className="text-sm text-gray-300">Analysis complete. View structured results in the left panel.</p>
                      ) : (
                        <p className="text-sm text-gray-300">Processing your query...</p>
                      )}
                    </div>
                  )}
                  {agent === 'deep-research' && (
                    <div className="bg-[#1a2533] border border-[#2a3f5f] px-4 py-3 rounded-xl">
                      {deepResearchLoading ? (
                        <p className="text-sm text-gray-300">Conducting deep research analysis...</p>
                      ) : deepResearchError ? (
                        <p className="text-sm text-red-400">Error: {deepResearchError}</p>
                      ) : deepResearchData ? (
                        <p className="text-sm text-gray-300">Analysis complete. View structured results in the left panel.</p>
                      ) : (
                        <p className="text-sm text-gray-300">Processing your query...</p>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Input Area */}
            <div className="border-t border-[#2a3f5f] p-4">
              <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-xl p-2 flex items-center gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder={`Ask ${config.name} a question...`}
                  className="flex-1 bg-transparent px-4 py-2 outline-none text-sm"
                />
                <button
                  onClick={handleSend}
                  className="bg-gradient-to-r from-[#4ade80] to-[#22d3ee] hover:from-[#22d3ee] hover:to-[#4ade80] transition-all rounded-lg px-4 py-2 flex items-center gap-2 shadow-lg"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
