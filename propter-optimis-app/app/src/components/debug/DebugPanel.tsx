import { useState, useRef } from 'react';
import { TestService } from '@/services/testService';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { 
  Server, 
  Upload, 
  CheckCircle, 
  AlertCircle, 
  RefreshCw,
  FileText,
  Bug
} from 'lucide-react';

interface TestResult {
  success: boolean;
  message: string;
  details?: any;
}

export function DebugPanel() {
  const [connectionTest, setConnectionTest] = useState<TestResult | null>(null);
  const [endpointTest, setEndpointTest] = useState<TestResult | null>(null);
  const [uploadTest, setUploadTest] = useState<TestResult | null>(null);
  const [testing, setTesting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const runConnectionTest = async () => {
    setTesting(true);
    const result = await TestService.testConnection();
    setConnectionTest(result);
    setTesting(false);
  };

  const runEndpointTest = async () => {
    setTesting(true);
    const result = await TestService.testUploadEndpoint();
    setEndpointTest(result);
    setTesting(false);
  };

  const runDebugUpload = async () => {
    const fileInput = fileInputRef.current;
    if (!fileInput?.files?.[0]) {
      setUploadTest({
        success: false,
        message: 'Please select a test file first'
      });
      return;
    }

    setTesting(true);
    const result = await TestService.debugUpload(fileInput.files[0]);
    setUploadTest(result);
    setTesting(false);
  };

  const runAllTests = async () => {
    await runConnectionTest();
    await runEndpointTest();
  };

  const TestResultDisplay = ({ result, title }: { result: TestResult | null; title: string }) => {
    if (!result) return null;

    return (
      <Alert className={result.success ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
        <div className="flex items-center gap-2">
          {result.success ? (
            <CheckCircle className="h-4 w-4 text-green-600" />
          ) : (
            <AlertCircle className="h-4 w-4 text-red-600" />
          )}
          <div className="flex-1">
            <div className="font-medium">{title}</div>
            <AlertDescription className="mt-1">
              {result.message}
            </AlertDescription>
            {result.details && (
              <details className="mt-2">
                <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800">
                  View Details
                </summary>
                <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto max-h-32">
                  {JSON.stringify(result.details, null, 2)}
                </pre>
              </details>
            )}
          </div>
        </div>
      </Alert>
    );
  };

  return (
    <Card className="mb-6 border-orange-200 bg-orange-50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-orange-800">
          <Bug className="h-5 w-5" />
          Debug Panel - Django Backend Testing
        </CardTitle>
        <CardDescription>
          Test connectivity and troubleshoot upload issues with your local Django backend
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Environment Info */}
        <div className="flex flex-wrap gap-2">
          <Badge variant="outline">Mode: {import.meta.env.VITE_AUTH_MODE || 'production'}</Badge>
          <Badge variant="outline">API: {import.meta.env.VITE_API_URL || 'http://localhost:8000'}</Badge>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap gap-2">
          <Button 
            onClick={runAllTests} 
            disabled={testing}
            size="sm"
            variant="outline"
          >
            {testing ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Server className="mr-2 h-4 w-4" />}
            Test Backend
          </Button>
          
          <Button 
            onClick={runConnectionTest} 
            disabled={testing}
            size="sm"
            variant="outline"
          >
            <Server className="mr-2 h-4 w-4" />
            Test Connection
          </Button>

          <Button 
            onClick={runEndpointTest} 
            disabled={testing}
            size="sm"
            variant="outline"
          >
            <Upload className="mr-2 h-4 w-4" />
            Test Upload Endpoint
          </Button>
        </div>

        {/* File Upload Test */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              className="flex-1 text-sm text-gray-500 file:mr-4 file:py-1 file:px-2 file:rounded-md file:border-0 file:text-sm file:bg-orange-100 file:text-orange-700 hover:file:bg-orange-200"
            />
            <Button 
              onClick={runDebugUpload} 
              disabled={testing}
              size="sm"
              variant="outline"
            >
              <FileText className="mr-2 h-4 w-4" />
              Debug Upload
            </Button>
          </div>
        </div>

        {/* Test Results */}
        <div className="space-y-3">
          <TestResultDisplay result={connectionTest} title="Django Server Connection" />
          <TestResultDisplay result={endpointTest} title="Upload Endpoint Test" />
          <TestResultDisplay result={uploadTest} title="Debug Upload Test" />
        </div>

        {/* Troubleshooting Tips */}
        <details className="mt-4">
          <summary className="cursor-pointer font-medium text-orange-800 hover:text-orange-900">
            Common Issues & Solutions
          </summary>
          <div className="mt-2 text-sm text-gray-700 space-y-2">
            <div><strong>Django server not running:</strong> Run <code>python manage.py runserver</code></div>
            <div><strong>CORS errors:</strong> Install django-cors-headers and configure CORS_ALLOWED_ORIGINS</div>
            <div><strong>404 Not Found:</strong> Check URL patterns in Django urls.py</div>
            <div><strong>403 CSRF:</strong> Add @csrf_exempt decorator to upload view</div>
            <div><strong>JSON mime type error:</strong> Django view should handle FormData, not JSON</div>
          </div>
        </details>
      </CardContent>
    </Card>
  );
}