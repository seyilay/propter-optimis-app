import { ReactNode } from 'react';
import { useAuth } from '@/components/providers/AuthProvider';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { PageLoader } from './LoadingSpinner';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { user, loading } = useAuth();

  if (loading) {
    return <PageLoader />;
  }

  if (!user) {
    return children; // Auth pages
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}