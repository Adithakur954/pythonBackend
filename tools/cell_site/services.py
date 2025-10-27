from flask import current_app
from werkzeug.utils import secure_filename
import os
import time

# Import your existing site.py module
try:
    from . import site
except ImportError:
    import site

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
        
        # Setup logger
        site.setup_logger(outdir, tag=params['method'])
        
        # Process based on method
        try:
            if params['method'] == 'noml':
                results = site.run_noml(
                    input_path=filepath,
                    outdir=outdir,
                    min_samples=params['min_samples'],
                    bin_size=params['bin_size'],
                    soft_spacing=params['soft_spacing'],
                    use_ta=params['use_ta'],
                    make_map=params['make_map'],
                    merge_sites=params['soft_spacing']
                )
            else:  # ML method
                results = site.run_ml(
                    train_path=params.get('train_path'),
                    model_path=params.get('model_path'),
                    input_path=filepath,
                    outdir=outdir,
                    min_samples=params['min_samples'],
                    bin_size=params['bin_size'],
                    soft_spacing=params['soft_spacing'],
                    make_map=params['make_map']
                )
            
            # If using S3, upload results
            if current_app.config.get('USE_S3'):
                from utils.storage import S3Storage
                storage = S3Storage()
                s3_results = storage.upload_directory(outdir, f'cellsite_{timestamp}')
                
                return {
                    'success': True,
                    'results': s3_results,
                    'output_dir': f'cellsite_{timestamp}',
                    'message': 'File processed and uploaded to S3',
                    'storage': 's3'
                }
            else:
                # Local storage
                relative_results = {}
                for key, path in results.items():
                    if path and os.path.exists(path):
                        relative_results[key] = os.path.basename(path)
                
                return {
                    'success': True,
                    'results': relative_results,
                    'output_dir': os.path.basename(outdir),
                    'message': 'File processed successfully',
                    'storage': 'local',
                    'note': 'Files stored temporarily and will be deleted after 24 hours'
                }
        
        finally:
            # Cleanup uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
                current_app.logger.info(f"Cleaned up: {filepath}")