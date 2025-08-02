import { useState, useEffect } from 'react';
import { User as AppUser } from '@/types';

// Local development auth that works with Django backend
export function useAuthProvider() {
  const [user, setUser] = useState<AppUser | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check if user is already logged in (check localStorage or make API call)
    const savedUser = localStorage.getItem('dev-user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const signIn = async (email: string, password: string) => {
    setLoading(true);
    
    // Bypass API - create mock user immediately
    const mockUser: AppUser = {
      id: '1',
      email,
      full_name: 'Local Dev User',
      role: 'analyst',
      team_name: 'Local Team',
      created_at: new Date().toISOString()
    };
    
    setUser(mockUser);
    localStorage.setItem('dev-user', JSON.stringify(mockUser));
    setLoading(false);
    return {};
  };

  const signUp = async (email: string, password: string, metadata?: any) => {
    // For local development, just sign them in
    return signIn(email, password);
  };

  const signOut = async () => {
    setUser(null);
    localStorage.removeItem('dev-user');
  };

  const resetPassword = async (email: string) => {
    return {};
  };

  return {
    user,
    loading,
    signIn,
    signUp,
    signOut,
    resetPassword
  };
}
