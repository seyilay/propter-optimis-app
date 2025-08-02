"""
OpenStar Lab Integration Package for Propter-Optimis Sports Analytics Platform.

This package provides integration with OpenStar Lab AI analysis services
for sports video analysis and tactical insights generation.
"""

__version__ = '1.0.0'
__author__ = 'Propter-Optimis Development Team'

from .processors.event_modeling import EventModelingProcessor
from .processors.preprocessing import PreprocessingPipeline
from .processors.rlearn_analysis import ReinforcementLearningAnalyzer
from .processors.ste_labeling import STELabelingSystem
from .utils.video_processing import VideoProcessor
from .utils.data_formatting import DataFormatter


class OpenStarLabClient:
    """Main client for OpenStar Lab integration."""
    
    def __init__(self, api_key=None, base_url=None):
        """Initialize OpenStar Lab client."""
        self.api_key = api_key
        self.base_url = base_url or 'https://api.openstarlab.com'
        
        # Initialize processors
        self.preprocessing = PreprocessingPipeline(self)
        self.event_modeling = EventModelingProcessor(self)
        self.rlearn_analysis = ReinforcementLearningAnalyzer(self)
        self.ste_labeling = STELabelingSystem(self)
        
        # Initialize utilities
        self.video_processor = VideoProcessor()
        self.data_formatter = DataFormatter()
    
    def analyze_video(self, video_path, analysis_intent='full_match', **kwargs):
        """Main method to analyze a video with OpenStar Lab."""
        try:
            # Step 1: Preprocessing
            preprocessed_data = self.preprocessing.process_video(video_path)
            
            # Step 2: Event modeling
            events = self.event_modeling.detect_events(
                preprocessed_data, 
                analysis_intent
            )
            
            # Step 3: Tactical analysis
            tactical_insights = self.rlearn_analysis.analyze_tactics(
                events, 
                analysis_intent
            )
            
            # Step 4: STE labeling
            labeled_data = self.ste_labeling.label_events(
                events, 
                tactical_insights
            )
            
            # Step 5: Format results
            results = self.data_formatter.format_analysis_results({
                'events': events,
                'tactical_insights': tactical_insights,
                'labeled_data': labeled_data,
                'analysis_intent': analysis_intent
            })
            
            return results
            
        except Exception as e:
            raise OpenStarLabException(f"Analysis failed: {str(e)}")


class OpenStarLabException(Exception):
    """Custom exception for OpenStar Lab errors."""
    pass


# Default client instance
client = None

def get_client(api_key=None, base_url=None):
    """Get or create OpenStar Lab client instance."""
    global client
    if client is None:
        client = OpenStarLabClient(api_key, base_url)
    return client
