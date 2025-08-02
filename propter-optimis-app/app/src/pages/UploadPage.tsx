import { useState } from 'react';
import { VideoUpload } from '@/components/upload/VideoUpload';
import { DebugPanel } from '@/components/debug/DebugPanel';
import { Button } from '@/components/ui/button';
import { Settings } from 'lucide-react';

export function UploadPage() {
  const [showDebug, setShowDebug] = useState(false);
  const isDevelopment = import.meta.env.VITE_AUTH_MODE === 'local';

  return (
    <div className="p-6">
      {isDevelopment && (
        <div className="mb-4">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setShowDebug(!showDebug)}
            className="mb-4"
          >
            <Settings className="mr-2 h-4 w-4" />
            {showDebug ? 'Hide' : 'Show'} Debug Panel
          </Button>
          {showDebug && <DebugPanel />}
        </div>
      )}
      <VideoUpload />
    </div>
  );
}