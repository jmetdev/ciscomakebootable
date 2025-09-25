import os
import subprocess
import tempfile
import shutil
import logging
import datetime
import time
import re
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import uuid

# Global variable to store step status
step_status = {
    'upload': {'status': 'pending', 'message': 'Awaiting file upload...'},
    'setup': {'status': 'pending', 'message': 'Setting up temporary directories...'},
    'extract': {'status': 'pending', 'message': 'Extracting ISO contents...'},
    'copy': {'status': 'pending', 'message': 'Copying ISO contents...'},
    'analyze': {'status': 'pending', 'message': 'Analyzing product information...'},
    'bootloader': {'status': 'pending', 'message': 'Checking bootloader...'},
    'generate': {'status': 'pending', 'message': 'Generating bootable ISO...'},
    'cleanup': {'status': 'pending', 'message': 'Cleaning up temporary files...'},
    'complete': {'status': 'pending', 'message': 'Processing complete!'}
}

# Global variable to store parsed product info
parsed_product_info = None

# Product detection regex and labels
FILENAME_RE = re.compile(
    r'^(?:UCSInstall_|PCD_)([A-Z0-9]+)_(\d+)\.(\d+)\.(\d+)\.(\d+)(?:-[A-Za-z0-9._-]+)?\.iso$'
)

PRODUCT_LABELS = {
    "UCOS": "Cisco Unified Communications Manager",
    "CUC":  "Cisco Unity Connection",
    "CER":  "Cisco Emergency Responder",
    "CUP":  "Cisco IM and Presence",
    "UCCX": "Cisco Unified Contact Center Express",
    "UCCE": "Cisco Unified Contact Center Enterprise",
    "PCCE": "Cisco Packaged Contact Center Enterprise",
    "ECE":  "Cisco Enterprise Chat and Email",
}

def parse_uc_iso(filename: str):
    """Parse Cisco UC ISO filename to extract product information"""
    m = FILENAME_RE.match(filename)
    if not m:
        return None
    code, major, minor, maint, build = m.groups()
    
    # Parse SU version from build number
    # For format like 13900, extract SU number (3 in this case)
    su = None
    if build == "10000":
        su = 0  # GA release
    else:
        # Check for pattern like 13900 (SU3), 12900 (SU2), etc.
        su_match = re.match(r'^1(\d)900$', build)
        if su_match:
            su = int(su_match.group(1))
    
    # Format version string
    version_string = f"{major}.{minor}.{maint}"
    if su is not None:
        if su == 0:
            version_string += " (GA)"
        else:
            version_string += f" (SU{su})"
    
    return {
        "code": code,
        "product": PRODUCT_LABELS.get(code, code),
        "major": int(major),
        "minor": int(minor),
        "maint": int(maint),
        "build": int(build),
        "su": su,
        "version_string": version_string,
        "full_version": f"{major}.{minor}.{maint}.{build}"
    }

def update_step(step_key, status, message=None):
    """Update a step status"""
    global step_status
    if step_key in step_status:
        step_status[step_key]['status'] = status
        if message:
            step_status[step_key]['message'] = message
        
        # Log to console for debugging
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        status_icon = '✅' if status == 'completed' else '❌' if status == 'error' else '⏳'
        print(f"[{timestamp}] {status_icon} {step_key.upper()}: {step_status[step_key]['message']}")

def reset_steps():
    """Reset all steps to pending status"""
    global step_status, parsed_product_info
    for key in step_status:
        step_status[key]['status'] = 'pending'
    parsed_product_info = None  # Clear previous product info

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024  # 16GB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'iso'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_iso(input_path, output_dir):
    """Process the ISO file using the bash script logic with milestone tracking"""
    try:
        # Ensure output_dir is absolute
        output_dir = os.path.abspath(output_dir)
        
        # Create temporary directories
        update_step('setup', 'in_progress', 'Creating temporary directories...')
        try:
            # Try /app/tmp first (for Docker), fallback to system temp
            tmp_base = '/app/tmp' if os.path.exists('/app/tmp') else None
            tmpdir1 = tempfile.mkdtemp(dir=tmp_base, prefix='iso_mount_')
            tmpdir2 = tempfile.mkdtemp(dir=tmp_base, prefix='iso_work_')
            update_step('setup', 'completed', 'Temporary directories created successfully')
        except Exception as e:
            update_step('setup', 'error', f'Failed to create temp directories: {str(e)}')
            return False, f"Failed to create temporary directories: {str(e)}"
        
        # Extract ISO contents using 7z only
        update_step('extract', 'in_progress', 'Extracting ISO contents using 7zip...')
        
        try:
            extract_cmd = ['7z', 'x', input_path, f'-o{tmpdir1}', '-y']
            result = subprocess.run(extract_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                update_step('extract', 'completed', 'ISO extracted successfully using 7zip')
            else:
                update_step('extract', 'error', f"7z extraction failed: {result.stderr}")
                return False, f"Failed to extract ISO using 7zip: {result.stderr}"
                        
        except FileNotFoundError:
            update_step('extract', 'error', '7zip not found. Please ensure 7zip is installed.')
            return False, "7zip not found. Please ensure 7zip is installed."
        except Exception as e:
            update_step('extract', 'error', f"Failed to extract ISO: {str(e)}")
            return False, f"Failed to extract ISO: {str(e)}"
        
        try:
            # Debug: List contents of extracted ISO
            update_step('copy', 'in_progress', 'Analyzing ISO contents...')
            try:
                iso_contents = []
                for root, dirs, files in os.walk(tmpdir1):
                    for d in dirs[:5]:  # Limit to first 5 directories per level
                        rel_path = os.path.relpath(os.path.join(root, d), tmpdir1)
                        iso_contents.append(f"DIR: {rel_path}")
                    for f in files[:10]:  # Limit to first 10 files per level
                        rel_path = os.path.relpath(os.path.join(root, f), tmpdir1)
                        iso_contents.append(f"FILE: {rel_path}")
                    if len(iso_contents) > 20:  # Limit total output
                        iso_contents.append("... (truncated)")
                        break
                
                update_step('copy', 'in_progress', f'ISO contents: {", ".join(iso_contents[:10])}')
            except Exception as e:
                update_step('copy', 'in_progress', f'Could not list ISO contents: {str(e)}')
            
            # Copy contents
            update_step('copy', 'in_progress', 'Copying ISO contents...')
            rsync_cmd = ['rsync', '-av', f'{tmpdir1}/', f'{tmpdir2}/']
            result = subprocess.run(rsync_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                update_step('copy', 'error', f"Failed to copy ISO contents: {result.stderr}")
                return False, f"Failed to copy ISO contents: {result.stderr}"
            
            update_step('copy', 'completed', 'ISO contents copied successfully')
            
            # Change to temp directory first
            original_dir = os.getcwd()
            os.chdir(tmpdir2)
            
            try:
                # Product detection and analysis
                update_step('analyze', 'in_progress', 'Analyzing product information...')
                product_info = None
                isofilename = None
                global parsed_product_info
                
                # Check for isofilename file
                if os.path.exists('isofilename'):
                    with open('isofilename', 'r') as f:
                        isofilename = f.read().strip()
                    
                    # Parse product information
                    product_info = parse_uc_iso(isofilename)
                    if product_info:
                        parsed_product_info = product_info  # Store globally
                        update_step('analyze', 'completed', f"Product detected: {product_info['product']} ({product_info['code']}) - {product_info['version_string']}")
                    else:
                        parsed_product_info = None
                        update_step('analyze', 'completed', "Product analysis completed (unrecognized format)")
                    
                    # Always use the isofilename content for output
                    outfile = os.path.abspath(os.path.join(output_dir, f"Bootable_{isofilename}"))
                else:
                    # Fallback to input filename if no isofilename exists
                    input_filename = os.path.basename(input_path)
                    
                    # Try to parse from input filename
                    product_info = parse_uc_iso(input_filename)
                    if product_info:
                        parsed_product_info = product_info  # Store globally
                        update_step('analyze', 'completed', f"Product detected from filename: {product_info['product']} ({product_info['code']}) - {product_info['version_string']}")
                    else:
                        parsed_product_info = None
                        update_step('analyze', 'completed', "Product analysis completed (using input filename)")
                    
                    outfile = os.path.abspath(os.path.join(output_dir, f"Bootable_{input_filename}"))
                
                # Check for isolinux folder in extracted ISO
                update_step('bootloader', 'in_progress', 'Looking for isolinux folder in extracted ISO...')
                
                
                # Look for isolinux directory in the extracted ISO
                isolinux_source = None
                found_isolinux = False
                
                for root, dirs, files in os.walk(tmpdir1):
                    if 'isolinux' in dirs:
                        isolinux_source = os.path.join(root, 'isolinux')
                        rel_path = os.path.relpath(isolinux_source, tmpdir1)
                        update_step('bootloader', 'in_progress', f'Found isolinux folder at: {rel_path}')
                        found_isolinux = True
                        break
                
                if found_isolinux and isolinux_source and os.path.exists(isolinux_source):
                    # Copy the entire isolinux directory
                    if os.path.exists('isolinux'):
                        shutil.rmtree('isolinux')
                    shutil.copytree(isolinux_source, 'isolinux')
                    update_step('bootloader', 'completed', 'Bootloader files copied from source ISO')
                else:
                    error_msg = 'Could not find isolinux folder in extracted ISO'
                    update_step('bootloader', 'error', error_msg)
                    return False, error_msg
                
                # Ensure we have boot.cat file for bootable ISO
                if not os.path.exists('isolinux/boot.cat'):
                    update_step('bootloader', 'in_progress', 'Creating boot catalog...')
                    # boot.cat will be generated by genisoimage if it doesn't exist
                    update_step('bootloader', 'completed', 'Boot catalog will be generated')
                
                # Generate new ISO
                update_step('generate', 'in_progress', 'Generating bootable ISO...')
                geniso_cmd = [
                    'genisoimage',
                    '-J', '-no-emul-boot', '-boot-info-table', '-boot-load-size', '4',
                    '-b', 'isolinux/isolinux.bin', '-c', 'isolinux/boot.cat',
                    '-v',  # Add verbose flag like your working command
                    '-o', outfile,
                    '.'
                ]
                
                result = subprocess.run(geniso_cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    update_step('generate', 'error', f"Failed to generate ISO: {result.stderr}")
                    return False, f"Failed to generate ISO: {result.stderr}"
                
                update_step('generate', 'completed', f'ISO generated successfully: {os.path.basename(outfile)}')
                return True, outfile
                
            finally:
                os.chdir(original_dir)
                
        finally:
            # Cleanup temporary files
            try:
                shutil.rmtree(tmpdir1)
                shutil.rmtree(tmpdir2)
            except Exception as cleanup_error:
                pass  # Cleanup errors are handled in upload route
                
    except Exception as e:
        update_step('generate', 'error', f"Unexpected error: {str(e)}")
        return False, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if file and allowed_file(file.filename):
        # Reset steps for new processing
        reset_steps()
        
        filename = secure_filename(file.filename)
        
        # Add unique identifier to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{unique_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            update_step('upload', 'in_progress', 'Uploading ISO file...')
            file.save(filepath)
            update_step('upload', 'completed', 'File uploaded successfully')
            
            # Process the ISO
            success, result = process_iso(filepath, app.config['OUTPUT_FOLDER'])
            
            # Update cleanup step
            update_step('cleanup', 'completed', 'Cleanup completed successfully')
            
            if success:
                update_step('complete', 'completed', 'Processing completed successfully!')
                # Clean up input file
                os.remove(filepath)
                return jsonify({
                    'success': True,
                    'message': 'ISO processed successfully',
                    'output_file': os.path.basename(result),
                    'download_url': f'/download/{os.path.basename(result)}'
                })
            else:
                update_step('complete', 'error', f'Processing failed: {result}')
                # Clean up input file on failure
                os.remove(filepath)
                return jsonify({'success': False, 'error': result})
                
        except Exception as e:
            update_step('upload', 'error', f'Upload failed: {str(e)}')
            # Clean up input file on error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': False, 'error': 'Invalid file type'})

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'success': False, 'error': 'File not found'}), 404

@app.route('/step-status')
def get_step_status():
    """Get current step status"""
    return jsonify(step_status)


@app.route('/product-info')
def get_product_info():
    """Get current product information from step status"""
    global parsed_product_info
    
    # Check for UNRST warning in the analyze message
    analyze_message = step_status.get('analyze', {}).get('message', '')
    has_unrst_warning = "UNRESTRICTED" in analyze_message.upper()
    
    # Use the globally stored parsed product info
    product_info = parsed_product_info
    
    return jsonify({
        'product_info': product_info,
        'has_unrst_warning': has_unrst_warning
    })

if __name__ == '__main__':
    print("Starting ISO Bootable Maker Flask application...")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Output folder: {app.config['OUTPUT_FOLDER']}")
    print("Application will be available at http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
