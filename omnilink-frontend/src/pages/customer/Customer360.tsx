import { useAuth } from '../../context/AuthContext';
import type { CustomerProfile } from '../../types/crm';

const MOCK_PROFILE: CustomerProfile = {
  id: '#8204-ML',
  name: 'Aarav Sharma',
  phone: '+91 98450 13821',
  email: 'aarav.sharma@gmail.com',
  tier: 'Gold',
  totalSpend: 42800,
  pointsBalance: 2450,
  whatsAppConsent: true,
  smsConsent: true
};

export const Customer360 = () => {
  const { user } = useAuth();
  const isStoreStaff = user?.role === 'Store Team';

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-white p-4 border border-gray-200 rounded-lg shadow-sm">
        <div>
          <h2 className="text-xl font-bold text-gray-800">Customer 360 Ledger View</h2>
          <p className="text-xs text-gray-500 mt-0.5">Unified data profile compilation interface.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white p-5 border border-gray-200 rounded-lg shadow-sm space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 border-b border-gray-100 pb-2">Client Demographics</h3>
          <div>
            <span className="text-[11px] text-gray-400 block font-medium">Full Name</span>
            <p className="text-sm font-bold text-gray-800">{MOCK_PROFILE.name}</p>
          </div>
          <div>
            <span className="text-[11px] text-gray-400 block font-medium">Phone Number</span>
            <p className="text-sm font-bold text-gray-800">
              {isStoreStaff ? "******3821 [Field Mask Active]" : MOCK_PROFILE.phone}
            </p>
          </div>
          <div>
            <span className="text-[11px] text-gray-400 block font-medium">Email Address</span>
            <p className="text-sm font-bold text-gray-800">
              {isStoreStaff ? "a****a@domain.com [Field Mask Active]" : MOCK_PROFILE.email}
            </p>
          </div>
        </div>

        <div className="bg-white p-5 border border-gray-200 rounded-lg shadow-sm space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 border-b border-gray-100 pb-2">Loyalty Tracking Ledger</h3>
          <span className="bg-amber-100 text-amber-800 border border-amber-200 px-2.5 py-1 rounded font-bold text-xs inline-block">
            {MOCK_PROFILE.tier.toUpperCase()} MEMBER TIER
          </span>
          <div className="grid grid-cols-2 gap-2 pt-1">
            <div className="bg-gray-50 p-2 rounded border border-gray-100">
              <span className="text-[9px] text-gray-400 font-bold block uppercase">Points Balance</span>
              <span className="text-sm font-black text-gray-800">{MOCK_PROFILE.pointsBalance} pts</span>
            </div>
            <div className="bg-gray-50 p-2 rounded border border-gray-100">
              <span className="text-[9px] text-gray-400 font-bold block uppercase">Total Spend</span>
              <span className="text-sm font-black text-gray-800">₹{MOCK_PROFILE.totalSpend.toLocaleString('en-IN')}</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-5 border border-gray-200 rounded-lg shadow-sm space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 border-b border-gray-100 pb-2">Channel Opt-Ins</h3>
          <div className="space-y-2 text-xs font-semibold">
            <div className="flex items-center justify-between p-2 bg-gray-50 border border-gray-100 rounded">
              <span className="text-gray-600">WhatsApp Gateway</span>
              <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${MOCK_PROFILE.whatsAppConsent ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                {MOCK_PROFILE.whatsAppConsent ? 'OPTED IN' : 'EXCLUDED'}
              </span>
            </div>
            <div className="flex items-center justify-between p-2 bg-gray-50 border border-gray-100 rounded">
              <span className="text-gray-600">SMS Gateway</span>
              <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${MOCK_PROFILE.smsConsent ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                {MOCK_PROFILE.smsConsent ? 'OPTED IN' : 'EXCLUDED'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};