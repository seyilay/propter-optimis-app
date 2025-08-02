import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Analysis, OpenStarLabResults, AIInsights } from '@/types';
import { 
  Download,
  FileText,
  Table,
  Video,
  Package,
  Settings,
  Share2,
  Mail,
  Copy,
  CheckCircle
} from 'lucide-react';
import { toast } from 'sonner';

interface IntelligenceExportProps {
  analysis: Analysis;
  openstarResults?: OpenStarLabResults;
  aiInsights?: AIInsights;
}

export function IntelligenceExport({ 
  analysis, 
  openstarResults, 
  aiInsights 
}: IntelligenceExportProps) {
  const [exportType, setExportType] = useState<string>('pdf_report');
  const [exportOptions, setExportOptions] = useState({
    include_charts: true,
    include_heatmaps: true,
    include_timeline: true,
    include_player_stats: true,
    include_tactical_analysis: true,
    include_predictions: true,
    include_raw_data: false,
    include_confidence_scores: true,
  });
  const [isExporting, setIsExporting] = useState(false);
  const [shareDialogOpen, setShareDialogOpen] = useState(false);

  const exportTypes = [
    {
      value: 'pdf_report',
      label: 'PDF Report',
      description: 'Comprehensive analysis report',
      icon: <FileText className="h-4 w-4" />,
      size: '~2-5 MB'
    },
    {
      value: 'csv_data',
      label: 'CSV Data',
      description: 'Raw data and metrics',
      icon: <Table className="h-4 w-4" />,
      size: '~100-500 KB'
    },
    {
      value: 'video_clips',
      label: 'Video Highlights',
      description: 'Key moment video clips',
      icon: <Video className="h-4 w-4" />,
      size: '~50-200 MB'
    },
    {
      value: 'full_analysis',
      label: 'Complete Package',
      description: 'All formats combined',
      icon: <Package className="h-4 w-4" />,
      size: '~100-300 MB'
    }
  ];

  const handleExport = async () => {
    setIsExporting(true);
    
    try {
      // Simulate export process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const exportData = {
        analysis_id: analysis.id,
        export_type: exportType,
        customization: exportOptions
      };

      // In production, this would call the actual export API
      console.log('Exporting:', exportData);
      
      toast.success('Export completed successfully!');
      
      // Simulate download
      const fileName = `analysis_${analysis.id}_${exportType}.${
        exportType === 'pdf_report' ? 'pdf' : 
        exportType === 'csv_data' ? 'csv' : 
        exportType === 'video_clips' ? 'zip' : 'zip'
      }`;
      
      // Create a mock download
      const link = document.createElement('a');
      link.href = '#';
      link.download = fileName;
      link.click();
      
    } catch (error) {
      toast.error('Export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const handleShare = async (method: string) => {
    try {
      if (method === 'copy_link') {
        await navigator.clipboard.writeText(window.location.href);
        toast.success('Link copied to clipboard!');
      } else if (method === 'email') {
        const mailTo = `mailto:?subject=Football Analysis Results&body=Check out this AI-powered football analysis: ${window.location.href}`;
        window.open(mailTo);
      }
      setShareDialogOpen(false);
    } catch (error) {
      toast.error('Sharing failed. Please try again.');
    }
  };

  const selectedExportType = exportTypes.find(type => type.value === exportType);

  return (
    <div className="space-y-4">
      {/* Export Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Export Intelligence Results
          </CardTitle>
          <CardDescription>
            Download your AI analysis in various formats
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Export Type Selection */}
          <div>
            <label className="text-sm font-medium mb-2 block">Export Format</label>
            <div className="grid gap-3 md:grid-cols-2">
              {exportTypes.map(type => (
                <div
                  key={type.value}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    exportType === type.value 
                      ? 'border-purple-500 bg-purple-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setExportType(type.value)}
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded ${
                      exportType === type.value ? 'bg-purple-100 text-purple-600' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {type.icon}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-sm">{type.label}</div>
                      <div className="text-xs text-gray-500">{type.description}</div>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {type.size}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Export Options */}
          <div>
            <label className="text-sm font-medium mb-3 block">Include in Export</label>
            <div className="grid gap-3 md:grid-cols-2">
              {Object.entries(exportOptions).map(([key, value]) => (
                <div key={key} className="flex items-center space-x-2">
                  <Checkbox
                    id={key}
                    checked={value}
                    onCheckedChange={(checked) => 
                      setExportOptions(prev => ({ ...prev, [key]: checked as boolean }))
                    }
                  />
                  <label 
                    htmlFor={key} 
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 capitalize"
                  >
                    {key.replace('_', ' ')}
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Export Actions */}
          <div className="flex items-center gap-3 pt-4 border-t">
            <Button 
              onClick={handleExport}
              disabled={isExporting}
              className="flex-1"
            >
              {isExporting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Exporting...
                </>
              ) : (
                <>
                  <Download className="mr-2 h-4 w-4" />
                  Export {selectedExportType?.label}
                </>
              )}
            </Button>
            
            <Dialog open={shareDialogOpen} onOpenChange={setShareDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline">
                  <Share2 className="mr-2 h-4 w-4" />
                  Share
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Share Analysis Results</DialogTitle>
                  <DialogDescription>
                    Share this intelligence analysis with your team
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-3">
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    onClick={() => handleShare('copy_link')}
                  >
                    <Copy className="mr-2 h-4 w-4" />
                    Copy Link
                  </Button>
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    onClick={() => handleShare('email')}
                  >
                    <Mail className="mr-2 h-4 w-4" />
                    Share via Email
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardContent>
      </Card>

      {/* Export Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Export Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Analysis ID:</span>
              <span className="font-mono">{analysis.id}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Format:</span>
              <span className="font-medium">{selectedExportType?.label}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Estimated Size:</span>
              <span>{selectedExportType?.size}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Components:</span>
              <span>{Object.values(exportOptions).filter(Boolean).length} selected</span>
            </div>
            
            {openstarResults && (
              <div className="pt-2 border-t">
                <div className="text-xs text-gray-500 mb-2">Intelligence Data Available:</div>
                <div className="flex flex-wrap gap-1">
                  <Badge variant="outline" className="text-xs">
                    {openstarResults.events.length} Events
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {Object.keys(openstarResults.player_evaluations.player_metrics).length} Players
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {openstarResults.tactical_analysis.strategic_insights.length} Insights
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {Math.round(openstarResults.confidence_scores.overall_intelligence_confidence * 100)}% Confidence
                  </Badge>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}