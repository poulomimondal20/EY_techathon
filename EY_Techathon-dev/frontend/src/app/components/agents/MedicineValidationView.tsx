import { Download, CheckCircle, AlertTriangle, Building2, ShieldCheck, Loader2, AlertCircle, FileText } from 'lucide-react';

// Types matching backend schema
export interface MedicineValidationData {
  medicine_name: string;
  is_approved: boolean;
  regulatory_status: string;
  approved_indications: string[];
  safety_warnings: string[];
  manufacturers: string[];
  prescription_status: string;
  summary: string;
}

interface MedicineValidationViewProps {
  data?: MedicineValidationData | null;
  isLoading?: boolean;
  error?: string | null;
}

export function MedicineValidationView({ data = null, isLoading = false, error = null }: MedicineValidationViewProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 mx-auto mb-4 text-green-400 animate-spin" />
          <p className="text-gray-400">Validating medicine...</p>
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
          <p className="text-gray-400">Validation Failed</p>
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
          <p>Enter a medicine name to validate</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl">{data.medicine_name}</h3>
          <div className="flex items-center gap-3 mt-2">
            {data.is_approved ? (
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-400/10 text-green-400 border border-green-400/30 rounded-full text-xs">
                <CheckCircle className="w-3 h-3" />
                FDA Approved
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-red-400/10 text-red-400 border border-red-400/30 rounded-full text-xs">
                <AlertTriangle className="w-3 h-3" />
                Not Approved
              </span>
            )}
            <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-400/10 text-blue-400 border border-blue-400/30 rounded-full text-xs">
              <ShieldCheck className="w-3 h-3" />
              {data.prescription_status}
            </span>
          </div>
        </div>
        <button className="flex items-center gap-2 bg-gradient-to-r from-[#4ade80] to-[#22d3ee] px-4 py-2 rounded-lg hover:from-[#22d3ee] hover:to-[#4ade80] transition-all shadow-lg">
          <Download className="w-4 h-4" />
          Export PDF
        </button>
      </div>

      {/* Clinical Summary */}
      <div className="bg-gradient-to-br from-[#4ade80]/5 to-[#22d3ee]/5 border border-[#4ade80]/30 rounded-xl p-6 shadow-lg">
        <h4 className="mb-4 flex items-center gap-2">
          <span className="w-5 h-5 bg-gradient-to-br from-[#4ade80] to-[#22d3ee] rounded-full"></span>
          Clinical & Regulatory Summary
        </h4>
        <p className="text-gray-300 leading-relaxed">{data.summary}</p>
      </div>

      {/* Regulatory Status */}
      <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
        <h4 className="mb-4 flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-green-400" />
          Regulatory Status
        </h4>
        <p className="text-gray-300 leading-relaxed">{data.regulatory_status}</p>
      </div>

      {/* Manufacturers */}
      {data.manufacturers && data.manufacturers.length > 0 && (
      <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
        <h4 className="mb-4 flex items-center gap-2">
          <Building2 className="w-5 h-5 text-blue-400" />
          Authorized Manufacturers
          <span className="ml-2 text-xs bg-blue-400/20 text-blue-400 px-2 py-0.5 rounded-full">
            {data.manufacturers.length}
          </span>
        </h4>
        <div className="space-y-2">
          {data.manufacturers.map((manufacturer, idx) => (
            <div key={idx} className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-3 hover:border-blue-400/50 transition-all">
              <p className="text-sm text-gray-300">{manufacturer}</p>
            </div>
          ))}
        </div>
      </div>
      )}

      {/* Approved Indications */}
      {data.approved_indications && data.approved_indications.length > 0 && (
      <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
        <h4 className="mb-4 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-green-400" />
          Approved Indications
          <span className="ml-2 text-xs bg-green-400/20 text-green-400 px-2 py-0.5 rounded-full">
            {data.approved_indications.length}
          </span>
        </h4>
        <div className="grid grid-cols-2 gap-3">
          {data.approved_indications.map((indication, idx) => (
            <div key={idx} className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-3 hover:border-green-400/50 transition-all">
              <div className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-green-400 rounded-full mt-1.5 flex-shrink-0"></div>
                <p className="text-xs text-gray-300">{indication}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
      )}

      {/* Safety Warnings */}
      {data.safety_warnings && data.safety_warnings.length > 0 && (
      <div className="bg-gradient-to-br from-red-400/5 to-transparent border border-red-400/30 rounded-xl p-6 shadow-lg">
        <h4 className="mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-red-400" />
          Safety Warnings & Contraindications
          <span className="ml-2 text-xs bg-red-400/20 text-red-400 px-2 py-0.5 rounded-full">
            {data.safety_warnings.length}
          </span>
        </h4>
        <div className="space-y-2">
          {data.safety_warnings.map((warning, idx) => (
            <div key={idx} className="flex items-start gap-3 bg-[#1a2533]/50 border border-red-400/20 rounded-lg p-3">
              <div className="w-2 h-2 bg-red-400 rounded-full mt-1.5 flex-shrink-0"></div>
              <p className="text-sm text-gray-300 flex-1">{warning}</p>
            </div>
          ))}
        </div>
      </div>
      )}
    </div>
  );
}
