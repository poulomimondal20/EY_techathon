import { Send, Download, FileText, Leaf, Loader2, AlertCircle, CheckCircle, ExternalLink } from 'lucide-react';
import { useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

// Types matching backend schema
export interface ESGScores {
  environmental_score?: number;
  social_score?: number;
  governance_score?: number;
  overall_score?: number;
  [key: string]: any;
}

export interface ESGReportData {
  success: boolean;
  company_name: string;
  message: string;
  pdf_filename: string | null;
  download_url: string | null;
  view_url: string | null;
  scores: ESGScores | null;
  timestamp: string;
}

interface ESGViewProps {
  config: any;
  input: string;
  setInput: (value: string) => void;
  handleSend: () => void;
  hasQuery: boolean;
}

// Helper to convert score to letter grade
function getLetterGrade(score: number): string {
  if (score >= 90) return 'A+';
  if (score >= 85) return 'A';
  if (score >= 80) return 'A-';
  if (score >= 75) return 'B+';
  if (score >= 70) return 'B';
  if (score >= 65) return 'B-';
  if (score >= 60) return 'C+';
  if (score >= 55) return 'C';
  if (score >= 50) return 'C-';
  return 'D';
}

// Helper to get score color
function getScoreColor(score: number): string {
  if (score >= 80) return 'text-green-400';
  if (score >= 60) return 'text-yellow-400';
  return 'text-red-400';
}

// Pretty label from snake_case keys
function formatLabel(key: string): string {
  return key.replace(/_/g, ' ');
}

// Generic renderer for nested metric values
function MetricValue({ value }: { value: any }) {
  if (value === null || value === undefined) return <span className="text-gray-400">—</span>;
  if (typeof value === 'number') return <span>{Number.isInteger(value) ? value : value.toFixed(1)}</span>;
  if (typeof value === 'boolean') return <span>{value ? 'Yes' : 'No'}</span>;
  if (typeof value === 'string') return <span>{value}</span>;
  if (Array.isArray(value)) {
    if (value.length === 0) return <span className="text-gray-400">None</span>;
    return (
      <div className="flex flex-wrap gap-1">
        {value.map((item, idx) => (
          <span
            key={idx}
            className="text-xs px-2 py-0.5 rounded-full bg-[#0f1722] border border-[#2a3f5f] text-gray-300"
          >
            {typeof item === 'number' ? (Number.isInteger(item) ? item : item.toFixed(1)) : String(item)}
          </span>
        ))}
      </div>
    );
  }
  // Object
  const entries = Object.entries(value as Record<string, any>);
  if (entries.length === 0) return <span className="text-gray-400">—</span>;
  return (
    <div className="space-y-1">
      {entries.map(([k, v]) => (
        <div key={k} className="flex items-start justify-between gap-3">
          <span className="text-xs text-gray-500 whitespace-nowrap">{formatLabel(k)}</span>
          <div className="text-sm text-white flex-1 text-right">
            <MetricValue value={v} />
          </div>
        </div>
      ))}
    </div>
  );
}

export function ESGView({ config, input, setInput, handleSend: parentHandleSend, hasQuery }: ESGViewProps) {
  const [reportData, setReportData] = useState<ESGReportData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [queryText, setQueryText] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;

    const companyName = input.trim();
    setQueryText(companyName);
    setIsLoading(true);
    setError(null);
    setReportData(null);
    setInput('');
    parentHandleSend();

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/esg/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          company_name: companyName,
          reporting_period: '2024'
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.message || 'Report generation failed');
      }

      setReportData(result);
    } catch (err) {
      console.error('ESG report generation error:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate ESG report');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    if (reportData?.download_url) {
      window.open(`${API_BASE_URL}${reportData.download_url}`, '_blank');
    }
  };

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* Left Panel - Report Display */}
      <div className="flex-1 overflow-auto p-6 border-r border-[#2a3f5f]">
        {!hasQuery && !isLoading && !reportData ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center text-gray-400">
              <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Enter a company name to generate ESG report</p>
              <p className="text-xs text-gray-500 mt-2">e.g., "Pfizer", "Johnson & Johnson"</p>
            </div>
          </div>
        ) : isLoading ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <Loader2 className="w-12 h-12 mx-auto mb-4 text-emerald-400 animate-spin" />
              <p className="text-gray-400">Generating ESG Report...</p>
              <p className="text-xs text-gray-500 mt-2">This may take a minute</p>
            </div>
          </div>
        ) : error ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-400" />
              <p className="text-gray-400">Report Generation Failed</p>
              <p className="text-sm text-red-400 mt-2">{error}</p>
            </div>
          </div>
        ) : reportData ? (
          <div className="space-y-6">
            {/* Success Header */}
            <div className="flex items-center justify-between bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-4 shadow-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-emerald-400/20 rounded-lg flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                  <h4 className="text-white">ESG Report Generated</h4>
                  <p className="text-xs text-gray-400">{reportData.company_name} • {reportData.timestamp?.split('T')[0]}</p>
                </div>
              </div>
              {reportData.download_url && (
                <button 
                  onClick={handleDownload}
                  className="flex items-center gap-2 bg-gradient-to-r from-[#4ade80] to-[#22d3ee] px-4 py-2 rounded-lg hover:from-[#22d3ee] hover:to-[#4ade80] transition-all shadow-lg text-sm"
                >
                  <Download className="w-4 h-4" />
                  Download PDF
                </button>
              )}
            </div>

            {/* Company Info Card */}
            <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 bg-emerald-400/20 rounded-xl flex items-center justify-center">
                  <Leaf className="w-8 h-8 text-emerald-400" />
                </div>
                <div>
                  <h3 className="text-2xl text-white">{reportData.company_name}</h3>
                  <p className="text-gray-400">ESG Analysis Report • 2024</p>
                </div>
              </div>
              <p className="text-gray-300">{reportData.message}</p>
            </div>

            {/* ESG Scores */}
            {reportData.scores && (
              <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
                <h4 className="mb-6 flex items-center gap-2 text-white">
                  <Leaf className="w-5 h-5 text-emerald-400" />
                  ESG Scores
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {reportData.scores.environmental_score !== undefined && (
                    <div className="bg-[#1a2533] border border-emerald-400/30 rounded-xl p-4 text-center">
                      <div className={`text-3xl font-bold mb-1 ${getScoreColor(reportData.scores.environmental_score)}`}>
                        {reportData.scores.environmental_score.toFixed(0)}
                      </div>
                      <div className="text-xs text-gray-400 uppercase tracking-wider">Environmental</div>
                      <div className="text-lg text-emerald-400 mt-1">
                        {getLetterGrade(reportData.scores.environmental_score)}
                      </div>
                    </div>
                  )}
                  {reportData.scores.social_score !== undefined && (
                    <div className="bg-[#1a2533] border border-blue-400/30 rounded-xl p-4 text-center">
                      <div className={`text-3xl font-bold mb-1 ${getScoreColor(reportData.scores.social_score)}`}>
                        {reportData.scores.social_score.toFixed(0)}
                      </div>
                      <div className="text-xs text-gray-400 uppercase tracking-wider">Social</div>
                      <div className="text-lg text-blue-400 mt-1">
                        {getLetterGrade(reportData.scores.social_score)}
                      </div>
                    </div>
                  )}
                  {reportData.scores.governance_score !== undefined && (
                    <div className="bg-[#1a2533] border border-purple-400/30 rounded-xl p-4 text-center">
                      <div className={`text-3xl font-bold mb-1 ${getScoreColor(reportData.scores.governance_score)}`}>
                        {reportData.scores.governance_score.toFixed(0)}
                      </div>
                      <div className="text-xs text-gray-400 uppercase tracking-wider">Governance</div>
                      <div className="text-lg text-purple-400 mt-1">
                        {getLetterGrade(reportData.scores.governance_score)}
                      </div>
                    </div>
                  )}
                  {reportData.scores.overall_score !== undefined && (
                    <div className="bg-gradient-to-br from-emerald-400/10 to-cyan-400/10 border border-emerald-400/30 rounded-xl p-4 text-center">
                      <div className={`text-3xl font-bold mb-1 ${getScoreColor(reportData.scores.overall_score)}`}>
                        {reportData.scores.overall_score.toFixed(0)}
                      </div>
                      <div className="text-xs text-gray-400 uppercase tracking-wider">Overall</div>
                      <div className="text-lg bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent mt-1">
                        {getLetterGrade(reportData.scores.overall_score)}
                      </div>
                    </div>
                  )}
                </div>

                {/* Additional Scores if present */}
                {Object.keys(reportData.scores).filter(key => 
                  !['environmental_score', 'social_score', 'governance_score', 'overall_score'].includes(key)
                ).length > 0 && (
                  <div className="mt-6 pt-6 border-t border-[#2a3f5f]">
                    <h5 className="text-sm text-gray-400 mb-4">Additional Metrics</h5>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {Object.entries(reportData.scores)
                        .filter(([key]) => !['environmental_score', 'social_score', 'governance_score', 'overall_score'].includes(key))
                        .map(([key, value]) => (
                          <div key={key} className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-3">
                            <div className="text-xs text-gray-500 capitalize mb-2">
                              {formatLabel(key)}
                            </div>
                            <div className="text-white font-medium text-sm">
                              <MetricValue value={value} />
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Download Section */}
            {reportData.download_url && (
              <div className="bg-gradient-to-br from-emerald-400/5 to-cyan-400/5 border border-emerald-400/30 rounded-xl p-6 shadow-lg">
                <h4 className="mb-4 flex items-center gap-2 text-white">
                  <FileText className="w-5 h-5 text-emerald-400" />
                  Download Full Report
                </h4>
                <p className="text-gray-400 text-sm mb-4">
                  The complete ESG report has been generated as a PDF document. Click below to download.
                </p>
                <div className="flex items-center gap-4">
                  <button 
                    onClick={handleDownload}
                    className="flex items-center gap-2 bg-gradient-to-r from-[#4ade80] to-[#22d3ee] px-6 py-3 rounded-lg hover:from-[#22d3ee] hover:to-[#4ade80] transition-all shadow-lg"
                  >
                    <Download className="w-5 h-5" />
                    Download PDF Report
                  </button>
                  <div className="text-sm text-gray-500">
                    <p>Filename: {reportData.pdf_filename}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Report Preview Link */}
            {reportData.view_url && (
              <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <ExternalLink className="w-5 h-5 text-gray-400" />
                  <span className="text-sm text-gray-400">View report in browser</span>
                </div>
                <a 
                  href={`${API_BASE_URL}${reportData.view_url}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-emerald-400 hover:text-emerald-300 transition-colors"
                >
                  Open PDF →
                </a>
              </div>
            )}
          </div>
        ) : null}
      </div>

      {/* Right Panel - Chat/Input */}
      <div className="w-96 flex flex-col bg-gradient-to-br from-[#0f1722] to-[#1a2533]">
        <div className="flex-1 overflow-auto p-6">
          {(hasQuery || reportData) && (
            <div className="space-y-4">
              {queryText && (
                <div className="bg-gradient-to-br from-[#4ade80] to-[#22d3ee] text-white px-4 py-3 rounded-xl">
                  <p className="text-sm">Generate ESG report for: {queryText}</p>
                </div>
              )}
              <div className="flex gap-3">
                <div className="w-8 h-8 bg-emerald-400/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <Leaf className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="flex-1 bg-[#1a2533] border border-[#2a3f5f] px-4 py-3 rounded-xl">
                  {isLoading ? (
                    <p className="text-sm text-gray-300">Generating ESG report... This involves analyzing environmental, social, and governance metrics.</p>
                  ) : error ? (
                    <p className="text-sm text-red-400">Error: {error}</p>
                  ) : reportData ? (
                    <div className="text-sm text-gray-300">
                      <p className="mb-2">✅ ESG report generated successfully for <strong>{reportData.company_name}</strong>.</p>
                      {reportData.scores?.overall_score && (
                        <p className="mb-2">Overall ESG Score: <strong className="text-emerald-400">{reportData.scores.overall_score.toFixed(0)}/100</strong></p>
                      )}
                      {reportData.download_url && (
                        <p>Click the download button to get the full PDF report.</p>
                      )}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-300">Enter a company name to generate an ESG analysis report.</p>
                  )}
                </div>
              </div>
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
              onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSend()}
              placeholder="Enter company name..."
              className="flex-1 bg-transparent px-4 py-2 outline-none text-sm"
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={isLoading}
              className="bg-gradient-to-r from-[#4ade80] to-[#22d3ee] hover:from-[#22d3ee] hover:to-[#4ade80] transition-all rounded-lg px-4 py-2 flex items-center gap-2 shadow-lg disabled:opacity-50"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
