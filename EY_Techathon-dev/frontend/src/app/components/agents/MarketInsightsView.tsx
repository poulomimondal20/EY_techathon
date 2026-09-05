import { Download, TrendingUp, Users, DollarSign, Target, Loader2, AlertCircle, FileText } from 'lucide-react';

// Types matching backend schema
export interface MarketInsightsData {
  market_overview: string;
  market_size: string | null;
  key_players: string[];
  pricing_analysis: string;
  competitive_landscape: string[];
  strategic_recommendations: string[];
}

interface MarketInsightsViewProps {
  data: MarketInsightsData | null;
  isLoading: boolean;
  error: string | null;
}

// Helper to extract market metrics from market_size text
function extractMetrics(marketSize: string | null): { current: string; projected: string; cagr: string } | null {
  if (!marketSize) return null;
  
  // Patterns for current market value: "$68.1B", "USD 68.1 billion", "$68.1 billion", "68.1 billion USD"
  const currentPatterns = [
    /(?:estimated at|valued at|size was|is)\s*(?:USD\s*)?\$?([\d.]+)\s*(?:billion|B)/i,
    /(?:USD\s*)?\$?([\d.]+)\s*(?:billion|B)\s*(?:in\s*20\d{2})/i,
    /\$?([\d.]+)\s*(?:billion|B)\s*(?:market|in\s*20)/i,
  ];
  
  // Patterns for projected value: "reach $97.4B by 2030", "projected to reach USD 97.4 billion"
  const projectedPatterns = [
    /(?:reach|projected to|expected to reach)\s*(?:USD\s*)?\$?([\d.]+)\s*(?:billion|B)/i,
    /(?:USD\s*)?\$?([\d.]+)\s*(?:billion|B)\s*(?:by\s*20\d{2})/i,
  ];
  
  // Patterns for CAGR
  const cagrPatterns = [
    /CAGR\s*(?:of\s*)?([\d.]+)\s*%/i,
    /([\d.]+)\s*%\s*CAGR/i,
    /growing\s*(?:at\s*)?(?:a\s*)?([\d.]+)\s*%/i,
  ];
  
  let current = 'N/A';
  let projected = 'N/A';
  let cagr = 'N/A';
  
  // Try each pattern for current value
  for (const pattern of currentPatterns) {
    const match = marketSize.match(pattern);
    if (match && match[1]) {
      current = `$${match[1]}B`;
      break;
    }
  }
  
  // Try each pattern for projected value
  for (const pattern of projectedPatterns) {
    const match = marketSize.match(pattern);
    if (match && match[1]) {
      projected = `$${match[1]}B`;
      break;
    }
  }
  
  // Try each pattern for CAGR
  for (const pattern of cagrPatterns) {
    const match = marketSize.match(pattern);
    if (match && match[1]) {
      cagr = `${match[1]}%`;
      break;
    }
  }
  
  // Only return if at least one value was found
  if (current !== 'N/A' || projected !== 'N/A' || cagr !== 'N/A') {
    return { current, projected, cagr };
  }
  return null;
}

export function MarketInsightsView({ data, isLoading, error }: MarketInsightsViewProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 mx-auto mb-4 text-green-400 animate-spin" />
          <p className="text-gray-400">Analyzing market data...</p>
          <p className="text-xs text-gray-500 mt-2">This may take a moment</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-400" />
          <p className="text-gray-400">Analysis Failed</p>
          <p className="text-sm text-red-400 mt-2">{error}</p>
        </div>
      </div>
    );
  }

  // No data state
  if (!data) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-gray-400">
          <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p>Submit a query to see market analysis</p>
        </div>
      </div>
    );
  }

  const metrics = extractMetrics(data.market_size);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-2xl">Market Intelligence Report</h3>
        <button className="flex items-center gap-2 bg-gradient-to-r from-[#4ade80] to-[#22d3ee] px-4 py-2 rounded-lg hover:from-[#22d3ee] hover:to-[#4ade80] transition-all shadow-lg">
          <Download className="w-4 h-4" />
          Export PDF
        </button>
      </div>

      {/* Market Overview */}
      <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
        <h4 className="mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-green-400" />
          Market Overview
        </h4>
        <p className="text-gray-300 leading-relaxed">{data.market_overview}</p>
      </div>

      {/* Market Size */}
      {data.market_size && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-green-400" />
            Market Size & Growth
          </h4>
          <p className="text-gray-300 leading-relaxed">{data.market_size}</p>
          {metrics && (
            <div className="grid grid-cols-3 gap-4 mt-6">
              <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 text-center">
                <p className="text-2xl text-green-400 mb-1">{metrics.current}</p>
                <p className="text-xs text-gray-400">Current Market Value</p>
              </div>
              <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 text-center">
                <p className="text-2xl text-green-400 mb-1">{metrics.projected}</p>
                <p className="text-xs text-gray-400">Projected Value</p>
              </div>
              <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 text-center">
                <p className="text-2xl text-green-400 mb-1">{metrics.cagr}</p>
                <p className="text-xs text-gray-400">CAGR</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Key Players */}
      {data.key_players && data.key_players.length > 0 && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-blue-400" />
            Key Market Players
            <span className="ml-2 text-xs bg-blue-400/20 text-blue-400 px-2 py-0.5 rounded-full">
              {data.key_players.length} players
            </span>
          </h4>
          <div className="space-y-3">
            {data.key_players.map((player, idx) => (
              <div key={idx} className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 hover:border-blue-400/50 transition-all">
                <p className="text-sm text-gray-300">{player}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pricing Analysis */}
      <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
        <h4 className="mb-4 flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-orange-400" />
          Pricing Analysis
        </h4>
        <p className="text-gray-300 leading-relaxed">{data.pricing_analysis}</p>
      </div>

      {/* Competitive Landscape */}
      {data.competitive_landscape && data.competitive_landscape.length > 0 && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-red-400" />
            Competitive Landscape
          </h4>
          <div className="space-y-3">
            {data.competitive_landscape.map((item, idx) => (
              <div key={idx} className="flex items-start gap-3">
                <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-sm text-gray-300 flex-1">{item}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strategic Recommendations */}
      {data.strategic_recommendations && data.strategic_recommendations.length > 0 && (
        <div className="bg-gradient-to-br from-[#4ade80]/5 to-[#22d3ee]/5 border border-[#4ade80]/30 rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <span className="w-5 h-5 bg-gradient-to-br from-[#4ade80] to-[#22d3ee] rounded-full"></span>
            Strategic Recommendations
          </h4>
          <div className="space-y-3">
            {data.strategic_recommendations.map((rec, idx) => (
              <div key={idx} className="flex items-start gap-3">
                <div className="w-6 h-6 bg-gradient-to-br from-[#4ade80] to-[#22d3ee] rounded-full flex items-center justify-center flex-shrink-0 text-xs">
                  {idx + 1}
                </div>
                <p className="text-sm text-gray-300 flex-1">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
