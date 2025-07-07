import logging
import json
import tempfile
import os
import pandas as pd
from datetime import datetime
from models import Dataset, Analysis, ModelTraining
from services.data_processor import DataProcessor
from services.eda_engine import EDAEngine
from services.statistical_tests import StatisticalTestEngine
from services.visualization_engine import VisualizationEngine
# For now, just save as JSON and return the path
# In production, this would generate an actual PDF


class ReportGenerator:
    """Service for generating comprehensive reports"""
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self.eda_engine = EDAEngine()
        self.stats_engine = StatisticalTestEngine()
        self.viz_engine = VisualizationEngine()
    
    def generate_comprehensive_report(self, dataset_id):
        """Generate a comprehensive analysis report for a dataset"""
        try:
            dataset = Dataset.query.get_or_404(dataset_id)
            
            # Load dataset
            df, _ = self.data_processor.load_file(dataset.file_path)
            if df is None:
                return {'error': 'Could not load dataset'}
            
            report = {
                'dataset_info': dataset.to_dict(),
                'generated_at': datetime.now().isoformat(),
                'summary': {},
                'eda_results': {},
                'statistical_tests': {},
                'visualizations': {},
                'models': []
            }
            
            # Basic dataset summary
            report['summary'] = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values': df.isnull().sum().sum(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'data_types': df.dtypes.astype(str).to_dict()
            }
            
            # EDA Results
            try:
                eda_results = self.eda_engine.perform_eda(df)
                report['eda_results'] = eda_results
            except Exception as e:
                logging.warning(f"EDA analysis failed: {str(e)}")
                report['eda_results'] = {'error': str(e)}
            
            # Statistical Tests
            try:
                stats_results = self.stats_engine.comprehensive_statistical_analysis(df)
                report['statistical_tests'] = stats_results
            except Exception as e:
                logging.warning(f"Statistical analysis failed: {str(e)}")
                report['statistical_tests'] = {'error': str(e)}
            
            # Get stored analyses
            analyses = Analysis.query.filter_by(dataset_id=dataset_id).all()
            report['stored_analyses'] = [analysis.to_dict() for analysis in analyses]
            
            # Get trained models
            models = ModelTraining.query.filter_by(dataset_id=dataset_id).all()
            for model in models:
                model_info = model.to_dict()
                model_info['performance_metrics'] = model.get_performance_metrics()
                report['models'].append(model_info)
            
            return report
            
        except Exception as e:
            logging.error(f"Error generating comprehensive report: {str(e)}")
            return {'error': str(e)}
    
    def generate_pdf_report(self, dataset_id):
        """Generate PDF report (placeholder - would need additional libraries)"""
        try:
            # This is a placeholder implementation
            # In a real application, you would use libraries like reportlab, weasyprint, etc.
            
            report_data = self.generate_comprehensive_report(dataset_id)
            

            
            temp_dir = tempfile.mkdtemp()
            pdf_path = os.path.join(temp_dir, f'report_{dataset_id}.json')
            
            with open(pdf_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            return pdf_path
            
        except Exception as e:
            logging.error(f"Error generating PDF report: {str(e)}")
            raise e
    
    def generate_summary_report(self, dataset_id):
        """Generate a shorter summary report"""
        try:
            dataset = Dataset.query.get_or_404(dataset_id)
            
            # Load dataset
            df, _ = self.data_processor.load_file(dataset.file_path)
            if df is None:
                return {'error': 'Could not load dataset'}
            
            # Generate basic summary
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            summary = {
                'dataset_info': dataset.to_dict(),
                'basic_stats': {
                    'total_rows': len(df),
                    'total_columns': len(df.columns),
                    'numeric_columns': len(numeric_cols),
                    'categorical_columns': len(categorical_cols),
                    'missing_values': df.isnull().sum().sum(),
                    'duplicated_rows': df.duplicated().sum()
                },
                'column_info': []
            }
            
            # Add column information
            for col in df.columns:
                col_info = {
                    'name': col,
                    'type': str(df[col].dtype),
                    'missing_count': df[col].isnull().sum(),
                    'unique_count': df[col].nunique()
                }
                
                if col in numeric_cols:
                    col_info.update({
                        'mean': float(df[col].mean()) if pd.notna(df[col].mean()) else None,
                        'std': float(df[col].std()) if pd.notna(df[col].std()) else None,
                        'min': float(df[col].min()) if pd.notna(df[col].min()) else None,
                        'max': float(df[col].max()) if pd.notna(df[col].max()) else None
                    })
                
                summary['column_info'].append(col_info)
            
            return summary
            
        except Exception as e:
            logging.error(f"Error generating summary report: {str(e)}")
            return {'error': str(e)}