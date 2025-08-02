import { useState, useRef } from 'react';
import { VideoService } from '@/services/videoService';
import { AnalysisIntent, UploadProgress } from '@/types';
import { AnalyticsService } from '@/services/analyticsService';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Upload, File, CheckCircle, AlertCircle, Play } from 'lucide-react';
import { cn } from '@/lib/utils';

export function VideoUpload() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    analysisIntent: '' as AnalysisIntent
  });
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({
    progress: 0,
    status: 'idle'
  });
  const [dragActive, setDragActive] = useState(false);

  const analysisIntentOptions = AnalyticsService.getAnalysisIntentConfig();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    if (files[0]) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = (file: File) => {
    // Validate file type
    const allowedTypes = ['video/mp4', 'video/mov', 'video/avi', 'video/quicktime'];
    if (!allowedTypes.includes(file.type)) {
      setUploadProgress({
        progress: 0,
        status: 'error',
        message: 'Please select a valid video file (MP4, MOV, or AVI)'
      });
      return;
    }

    // Validate file size (2GB limit)
    const maxSize = 2 * 1024 * 1024 * 1024; // 2GB in bytes
    if (file.size > maxSize) {
      setUploadProgress({
        progress: 0,
        status: 'error',
        message: 'File size must be less than 2GB'
      });
      return;
    }

    setSelectedFile(file);
    setUploadProgress({ progress: 0, status: 'idle' });
    
    // Auto-fill title if not already set
    if (!formData.title) {
      const fileName = file.name.replace(/\.[^/.]+$/, ""); // Remove extension
      setFormData(prev => ({ ...prev, title: fileName }));
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile || !formData.title || !formData.analysisIntent) {
      setUploadProgress({
        progress: 0,
        status: 'error',
        message: 'Please fill in all required fields and select a video file'
      });
      return;
    }

    const result = await VideoService.uploadVideo(
      selectedFile,
      {
        title: formData.title,
        description: formData.description,
        analysisIntent: formData.analysisIntent
      },
      setUploadProgress
    );

    if (result.success && result.videoId) {
      // Auto-create analysis
      await AnalyticsService.createAnalysis(result.videoId, formData.analysisIntent);
      
      // Reset form
      setSelectedFile(null);
      setFormData({ title: '', description: '', analysisIntent: '' as AnalysisIntent });
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getProgressColor = () => {
    switch (uploadProgress.status) {
      case 'completed': return 'bg-green-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-purple-600';
    }
  };

  const getStatusIcon = () => {
    switch (uploadProgress.status) {
      case 'completed': return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'error': return <AlertCircle className="h-5 w-5 text-red-600" />;
      default: return <Upload className="h-5 w-5 text-purple-600" />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Video</h1>
        <p className="text-gray-600">
          Upload your match footage for AI-powered analysis. Reduce analysis time from 4+ hours to 15 minutes.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Form */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Video Details</CardTitle>
              <CardDescription>
                Provide information about your video and select analysis type
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* File Upload Area */}
                <div className="space-y-2">
                  <Label className="text-sm font-medium">Video File *</Label>
                  <div
                    className={cn(
                      'border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer',
                      dragActive ? 'border-purple-400 bg-purple-50' : 'border-gray-300 hover:border-purple-400',
                      selectedFile ? 'border-green-400 bg-green-50' : ''
                    )}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      className="hidden"
                      accept="video/mp4,video/mov,video/avi,video/quicktime"
                      onChange={handleFileInputChange}
                    />
                    
                    {selectedFile ? (
                      <div className="space-y-2">
                        <File className="h-8 w-8 text-green-600 mx-auto" />
                        <div>
                          <p className="font-medium text-green-700">{selectedFile.name}</p>
                          <p className="text-sm text-green-600">{formatFileSize(selectedFile.size)}</p>
                        </div>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedFile(null);
                            if (fileInputRef.current) fileInputRef.current.value = '';
                          }}
                        >
                          Change File
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <Upload className="h-8 w-8 text-gray-400 mx-auto" />
                        <div>
                          <p className="font-medium text-gray-600">Drop your video here or click to browse</p>
                          <p className="text-sm text-gray-500">
                            Supports MP4, MOV, AVI • Max size: 2GB
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Title */}
                <div className="space-y-2">
                  <Label htmlFor="title" className="text-sm font-medium">Title *</Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="e.g., Team vs Opposition - Match Analysis"
                    required
                  />
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <Label htmlFor="description" className="text-sm font-medium">Description</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Additional notes about the match or specific areas of focus..."
                    rows={3}
                  />
                </div>

                {/* Analysis Intent */}
                <div className="space-y-2">
                  <Label className="text-sm font-medium">Analysis Type *</Label>
                  <Select
                    value={formData.analysisIntent}
                    onValueChange={(value: AnalysisIntent) => 
                      setFormData(prev => ({ ...prev, analysisIntent: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select analysis type" />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(analysisIntentOptions).map(([key, config]) => (
                        <SelectItem key={key} value={key}>
                          <div className="text-left">
                            <div className="font-medium">{config.label}</div>
                            <div className="text-xs text-gray-500">{config.estimatedTime}</div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  
                  {formData.analysisIntent && (
                    <div className="mt-2 p-3 bg-purple-50 rounded-lg">
                      <p className="text-sm text-purple-700 mb-2">
                        {analysisIntentOptions[formData.analysisIntent].description}
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {analysisIntentOptions[formData.analysisIntent].features.map((feature, index) => (
                          <span
                            key={index}
                            className="inline-block px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full"
                          >
                            {feature}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Upload Progress */}
                {uploadProgress.status !== 'idle' && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon()}
                        <span className="text-sm font-medium">
                          {uploadProgress.status === 'uploading' && 'Uploading...'}
                          {uploadProgress.status === 'processing' && 'Processing...'}
                          {uploadProgress.status === 'completed' && 'Upload Complete!'}
                          {uploadProgress.status === 'error' && 'Upload Failed'}
                        </span>
                      </div>
                      <span className="text-sm text-gray-500">{uploadProgress.progress}%</span>
                    </div>
                    <Progress value={uploadProgress.progress} className={getProgressColor()} />
                    {uploadProgress.message && (
                      <Alert className={uploadProgress.status === 'error' ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'}>
                        <AlertDescription className={uploadProgress.status === 'error' ? 'text-red-700' : 'text-green-700'}>
                          {uploadProgress.message}
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                )}

                {/* Submit Button */}
                <Button
                  type="submit"
                  disabled={!selectedFile || !formData.title || !formData.analysisIntent || uploadProgress.status === 'uploading'}
                  className="w-full bg-purple-600 hover:bg-purple-700"
                >
                  {uploadProgress.status === 'uploading' ? 'Uploading...' : 'Upload & Start Analysis'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Analysis Info */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Play className="h-5 w-5 text-purple-600" />
                <span>AI Analysis</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-700 mb-1">15 min</div>
                <div className="text-sm text-purple-600">Average Analysis Time</div>
              </div>
              
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900">What you'll get:</h4>
                <ul className="text-sm text-gray-600 space-y-2">
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>Automated event detection</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>Player performance metrics</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>Tactical pattern analysis</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>AI-generated insights</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>Exportable reports</span>
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}