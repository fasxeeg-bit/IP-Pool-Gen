# IP Pool Generator - Web Application

## Overview
A Flask-based web application for generating IP address pools from CIDR notation with custom non-strict CIDR alignment logic. Features a modern, responsive interface and CSV export functionality.

## Purpose
This application allows network administrators and ISPs to generate usable IP addresses from any starting point (e.g., 10.15.31.0/22) without being forced into strict CIDR alignment. Unlike standard libraries that would convert 10.15.31.0/22 to 10.15.28.0/22, this tool respects the exact IP address you provide and generates the pool starting from that point.

## Key Features
- Custom IP generation logic (non-strict CIDR alignment)
- Modern web interface with gradient design
- Input fields for IP/Subnet and Gateway
- Real-time IP generation and display
- Export to CSV without column headings
- Responsive design works on desktop and mobile
- Generates accurate IP pools for ISP-style allocation

## Technical Details
- **Language**: Python 3.11
- **Framework**: Flask (web application)
- **Template Engine**: Jinja2
- **IP Generation**: Custom bit-manipulation algorithm
- **Export Format**: CSV without headers
- **Port**: 5000

## Recent Changes
- **2025-10-25**: Added gateway IP exclusion and updated CSV format to include three columns (IP, Gateway, Subnet Mask)
- **2025-10-25**: Converted to Flask web application for immediate browser testing
- **2025-10-25**: Initial project creation with desktop version (ip_pool_generator_desktop.py)

## Project Structure
- `app.py` - Main Flask application with routes and IP generation logic
- `templates/index.html` - Web interface template with modern design
- `ip_pool_generator_desktop.py` - Desktop version (Tkinter) for local Windows use

## Usage
Open the web application in your browser and:
1. **IP/Subnet**: Enter in CIDR format (e.g., 10.15.31.0/22)
2. **Gateway**: Enter gateway IP address (e.g., 10.15.31.1)
3. Click "Generate IP Pool" to see all generated IPs
4. Click "Download CSV" to save the IP list (no headers)

## IP Generation Logic
The custom algorithm:
1. Parses the IP address and subnet mask
2. Calculates total IPs based on subnet (2^(32-subnet))
3. Starts from IP+1 (first usable host) and ends at IP+total-2 (last usable host)
4. Skips network address (IP+0), gateway IP, and broadcast address (IP+total-1)
5. Generates continuous IP addresses without strict CIDR boundary enforcement
6. Produces 1021 usable IPs for a /22 subnet when gateway is excluded (e.g., 10.15.31.2 through 10.15.34.254 for 10.15.31.0/22 with gateway 10.15.31.1)

### Example for 10.15.31.0/22 with Gateway 10.15.31.1:
- Network address: 10.15.31.0 (skipped)
- Gateway: 10.15.31.1 (skipped)
- First usable IP: 10.15.31.2
- Last usable IP: 10.15.34.254
- Broadcast address: 10.15.34.255 (skipped)
- Total usable IPs: 1021 (excluding gateway)

### CSV Export Format:
Each line contains three fields:
- IP Address
- Gateway
- Subnet Mask (e.g., 255.255.252.0 for /22)

Example CSV output:
```
10.15.31.2,10.15.31.1,255.255.252.0
10.15.31.3,10.15.31.1,255.255.252.0
10.15.31.4,10.15.31.1,255.255.252.0
...
```
