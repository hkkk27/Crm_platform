export type UserRole = 'Admin' | 'CRM / Marketing Team' | 'Store Team' | 'Management Team' | 'Customer Service Team';

export interface UserSession {
  name: string;
  role: UserRole;
  email: string;
}

export interface CustomerProfile {
  id: string;
  name: string;
  phone: string;
  email: string;
  tier: string;
  totalSpend: number;
  pointsBalance: number;
  whatsAppConsent: boolean;
  smsConsent: boolean;
}
