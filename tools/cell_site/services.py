from flask import current_app
from werkzeug.utils import secure_filename
import os
import time

# Import the renamed module (avoid conflict with Python's built-in 'site')
from . import cell_site_processing as site

class CellSiteService:
    
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def process_file(self, file, params):
        """Process uploaded cell site file"""
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        current_app.logger.info(f"File saved: {filepath}")
        
        # Create output directory
        timestamp = str(int(time.time()))
        outdir = os.path.join(
            current_app.config['OUTPUT_FOLDER'],
            f'cellsite_{timestamp}'
        )
        os.makedirs(outdir, exist_ok=True)
        
        current_app.logger.info(f"Output directory: {outdir}")
        
        # Setup logger from cell_site_processing.py
        site.setup_logger(outdir, tag=params['method'])
        
        # Process based on method
        try:
            if params['method'] == 'noml':
                results = site.run_noml(
                    input_path=filepath,
                    outdir=outdir,
                    min_samples=params.get('min_samples', 30),
                    bin_size=params.get('bin_size', 5),
                    soft_spacing=params.get('soft_spacing', False),
                    use_ta=params.get('use_ta', False),
                    make_map=params.get('make_map', False),
                    merge_sites=params.get('soft_spacing', False)
                )
            else:  # ML method
                results = site.run_ml(
                    train_path=params.get('train_path'),
                    model_path=params.get('model_path'),
                    input_path=filepath,
                    outdir=outdir,
                    min_samples=params.get('min_samples', 30),
                    bin_size=params.get('bin_size', 5),
                    soft_spacing=params.get('soft_spacing', False),
                    make_map=params.get('make_map', False)
                )
            
            # Local storage - convert results to relative paths
            relative_results = {}
            for key, path in results.items():
                if path and os.path.exists(path):
                    relative_results[key] = os.path.basename(path)
            
            return {
                'success': True,
                'results': relative_results,
                'output_dir': os.path.basename(outdir),
                'message': 'File processed successfully',
                'storage': 'local'
            }
        
        except Exception as e:
            current_app.logger.error(f"Processing error: {str(e)}", exc_info=True)
            raise
        
        finally:
            # Cleanup uploaded file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    current_app.logger.info(f"Cleaned up: {filepath}")
                except Exception as e:
                    current_app.logger.warning(f"Cleanup failed: {e}")