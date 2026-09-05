import { User, Mail, Building2, Briefcase, Calendar, Award } from 'lucide-react';

export function Profile() {
  return (
    <div className="max-w-4xl mx-auto p-8">
      <div className="mb-8">
        <h1 className="text-3xl mb-2">Profile</h1>
        <p className="text-gray-400">Manage your personal information and preferences</p>
      </div>

      <div className="space-y-6">
        {/* Profile Header */}
        <div className="bg-[#0d1b2e] border border-[#1e3a5f] rounded-xl p-6">
          <div className="flex items-start gap-6">
            <div className="w-24 h-24 bg-[#fbbf24] rounded-full flex items-center justify-center flex-shrink-0">
              <User className="w-12 h-12 text-black" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl mb-2">Dr. Sarah Chen</h2>
              <p className="text-gray-400 mb-4">R&D Director • Pharmaceutical Corp</p>
              <button className="bg-[#1e3a5f] hover:bg-[#2a4a7f] px-4 py-2 rounded-lg transition-colors">
                Upload Photo
              </button>
            </div>
          </div>
        </div>

        {/* Personal Information */}
        <div className="bg-[#0d1b2e] border border-[#1e3a5f] rounded-xl p-6">
          <h3 className="mb-6">Personal Information</h3>
          
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="text-sm text-gray-400 mb-2 block flex items-center gap-2">
                <User className="w-4 h-4" />
                Full Name
              </label>
              <input 
                type="text" 
                defaultValue="Dr. Sarah Chen"
                className="w-full bg-[#0a1628] border border-[#1e3a5f] rounded-lg px-4 py-2 outline-none focus:border-[#fbbf24] transition-colors"
              />
            </div>
            
            <div>
              <label className="text-sm text-gray-400 mb-2 block flex items-center gap-2">
                <Mail className="w-4 h-4" />
                Email
              </label>
              <input 
                type="email" 
                defaultValue="sarah.chen@pharmcorp.com"
                className="w-full bg-[#0a1628] border border-[#1e3a5f] rounded-lg px-4 py-2 outline-none focus:border-[#fbbf24] transition-colors"
              />
            </div>
            
            <div>
              <label className="text-sm text-gray-400 mb-2 block flex items-center gap-2">
                <Building2 className="w-4 h-4" />
                Company
              </label>
              <input 
                type="text" 
                defaultValue="Pharmaceutical Corp"
                className="w-full bg-[#0a1628] border border-[#1e3a5f] rounded-lg px-4 py-2 outline-none focus:border-[#fbbf24] transition-colors"
              />
            </div>
            
            <div>
              <label className="text-sm text-gray-400 mb-2 block flex items-center gap-2">
                <Briefcase className="w-4 h-4" />
                Job Title
              </label>
              <input 
                type="text" 
                defaultValue="R&D Director"
                className="w-full bg-[#0a1628] border border-[#1e3a5f] rounded-lg px-4 py-2 outline-none focus:border-[#fbbf24] transition-colors"
              />
            </div>
          </div>
        </div>

        {/* Professional Details */}
        <div className="bg-[#0d1b2e] border border-[#1e3a5f] rounded-xl p-6">
          <h3 className="mb-6">Professional Details</h3>
          
          <div className="space-y-6">
            <div>
              <label className="text-sm text-gray-400 mb-2 block flex items-center gap-2">
                <Award className="w-4 h-4" />
                Areas of Expertise
              </label>
              <div className="flex flex-wrap gap-2">
                <span className="bg-[#1e3a5f] px-3 py-1 rounded-full text-sm">Oncology</span>
                <span className="bg-[#1e3a5f] px-3 py-1 rounded-full text-sm">Immunotherapy</span>
                <span className="bg-[#1e3a5f] px-3 py-1 rounded-full text-sm">Drug Discovery</span>
                <span className="bg-[#1e3a5f] px-3 py-1 rounded-full text-sm">Clinical Trials</span>
                <button className="border border-[#1e3a5f] px-3 py-1 rounded-full text-sm hover:bg-[#1e3a5f] transition-colors">
                  + Add
                </button>
              </div>
            </div>
            
            <div>
              <label className="text-sm text-gray-400 mb-2 block">Bio</label>
              <textarea 
                rows={4}
                defaultValue="Experienced R&D director specializing in oncology drug development with over 15 years in pharmaceutical research. Led multiple successful Phase III trials."
                className="w-full bg-[#0a1628] border border-[#1e3a5f] rounded-lg px-4 py-2 outline-none focus:border-[#fbbf24] transition-colors resize-none"
              />
            </div>
          </div>
        </div>

        {/* Account Stats */}
        <div className="bg-[#0d1b2e] border border-[#1e3a5f] rounded-xl p-6">
          <h3 className="mb-6">Account Activity</h3>
          
          <div className="grid grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl text-[#fbbf24] mb-2">847</div>
              <p className="text-sm text-gray-400">Analyses Completed</p>
            </div>
            <div className="text-center">
              <div className="text-3xl text-[#fbbf24] mb-2">2,340h</div>
              <p className="text-sm text-gray-400">Time Saved</p>
            </div>
            <div className="text-center">
              <div className="text-3xl text-[#fbbf24] mb-2">94.2%</div>
              <p className="text-sm text-gray-400">Avg Confidence</p>
            </div>
          </div>
        </div>

        {/* Member Since */}
        <div className="bg-[#0d1b2e] border border-[#1e3a5f] rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Calendar className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-400">Member Since</p>
                <p>January 2024</p>
              </div>
            </div>
            <button className="bg-red-500/10 text-red-400 hover:bg-red-500/20 px-4 py-2 rounded-lg transition-colors">
              Delete Account
            </button>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end gap-4">
          <button className="border border-[#1e3a5f] px-6 py-2 rounded-lg hover:bg-[#1e3a5f] transition-colors">
            Cancel
          </button>
          <button className="bg-[#fbbf24] text-black px-6 py-2 rounded-lg hover:bg-[#f59e0b] transition-colors">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
