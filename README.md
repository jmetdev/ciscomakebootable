# ISO Bootable Maker

A web interface for creating bootable ISO files from existing ISO images. This application uses your bash script logic to process ISO files and make them bootable.

## Features

- Web-based upload interface for ISO files
- Automatic ISO processing using the provided bash script logic
- Progress indication during processing
- Download link for the generated bootable ISO
- Clean, modern UI using Tabler.io components
- Support for large ISO files (up to 16GB)

## Prerequisites

### Docker Requirements
- Docker and Docker Compose installed
- No additional system packages needed (all included in container)
- **Tested and working** - Container successfully built and running

### Local Requirements
- Python 3.7+
- sudo access (required for mounting ISO files)
- The following system packages:
  - `genisoimage` (or `xorrisofs`)
  - `rsync`
  - `isolinux` (for bootloader files)

## Installation

### Option 1: Docker (Recommended)

1. Ensure Docker and Docker Compose are installed
2. Clone or download this repository
3. Run the Docker startup script:
   ```bash
   ./docker-run.sh
   ```

### Option 2: Local Installation

1. Clone or download this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Docker Usage

1. Start the application:
   ```bash
   ./docker-run.sh
   ```

### Local Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to `http://localhost:5000`

3. Use the upload form to select an ISO file

4. Click "Process ISO" to start the conversion

5. Wait for processing to complete (this may take several minutes for large files)

6. Download the generated bootable ISO file

## How It Works

The application follows the same logic as your bash script:

1. **Mounts** the input ISO file as a read-only loop device
2. **Copies** all contents to a temporary directory using rsync
3. **Checks** for an `isofilename` file to determine the output filename
4. **Creates** isolinux directory and copies bootloader files if needed
5. **Generates** a new bootable ISO using genisoimage with proper boot options
6. **Unmounts** the original ISO and cleans up temporary files

## Security Notes

- The application requires sudo access to mount ISO files
- Temporary files are automatically cleaned up after processing
- Input files are removed after processing (success or failure)
- File uploads are restricted to .iso files only

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure the application has sudo access
2. **isolinux.bin not found**: Install the `isolinux` package or ensure it's in standard locations
3. **Mount failures**: Check that the ISO file is valid and not corrupted
4. **Large file timeouts**: The application supports files up to 16GB, but processing time will vary

### System Package Installation

On Ubuntu/Debian:
```bash
sudo apt-get install genisoimage rsync isolinux
```

On CentOS/RHEL:
```bash
sudo yum install genisoimage rsync syslinux
```

On macOS (using Homebrew):
```bash
brew install cdrtools rsync
```

## File Structure

```
makeBootable/
├── app.py              # Flask application
├── templates/
│   └── index.html     # Web interface template
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker container definition
├── docker-compose.yml  # Docker Compose configuration
├── docker-run.sh       # Docker startup script
├── test-docker.sh      # Docker functionality test script
├── test-upload.sh      # Upload and logging test script
├── test-tmp-mount.sh   # TMP directory mount test script
├── test-realtime-logs.sh # Real-time logging test script
├── run.sh              # Local startup script
├── README.md           # This file
├── uploads/            # Temporary upload directory (auto-created)
├── tmp/                # Temporary processing directory (auto-created)
└── output/             # Generated ISO files (auto-created)
```

## Docker

### Volume Mounts

The application uses three local directory mounts for optimal performance and debugging:

- **`./output:/app/output`** - Generated bootable ISO files
- **`./uploads:/app/uploads`** - Temporary storage for uploaded files
- **`./tmp:/tmp`** - Temporary processing directories (ISO mounting, content copying)

**Benefits of local tmp mount:**
- **Better Performance**: Faster I/O operations on local filesystem
- **Easy Debugging**: Inspect temporary files during processing
- **Resource Management**: Better control over disk space usage
- **Cross-Platform**: Consistent behavior across different systems

### Building the Image

```bash
docker build -t iso-bootable-maker .
```

### Running with Docker Compose

```bash
docker-compose up -d
```

### Running with Docker

```bash
docker run -d \
  --name iso-maker \
  -p 5000:5000 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/tmp:/tmp \
  --privileged \
  --cap-add SYS_ADMIN \
  iso-bootable-maker
```

### Stopping the Container

```bash
docker-compose down
# or
docker stop iso-maker && docker rm iso-maker
```

### Testing the Container

After starting the container, you can run the test script to verify everything is working:

```bash
./test-docker.sh
```

This will test:
- Web interface accessibility
- Container health
- File permissions
- Sudo access for mount operations
- Required tools availability

## API Endpoints

- `GET /` - Main upload interface
- `POST /upload` - File upload and processing
- `GET /download/<filename>` - Download processed ISO file

## License

This project is provided as-is for educational and development purposes.
