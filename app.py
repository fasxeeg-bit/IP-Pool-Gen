from flask import Flask, request, render_template, Response
import io
import csv

app = Flask(__name__)


def cidr_to_subnet_mask(cidr):
    cidr = int(cidr)
    mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
    return f"{(mask >> 24) & 255}.{(mask >> 16) & 255}.{(mask >> 8) & 255}.{mask & 255}"


def generate_ip_pool(ip_subnet, gateway=None):
    try:
        ip, subnet = ip_subnet.split('/')
        subnet = int(subnet)
        
        parts = list(map(int, ip.split('.')))
        ip_int = (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
        
        total = 2 ** (32 - subnet)
        
        ips = []
        for i in range(1, total - 1):
            v = ip_int + i
            generated_ip = f"{(v >> 24) & 255}.{(v >> 16) & 255}.{(v >> 8) & 255}.{v & 255}"
            
            if gateway and generated_ip == gateway:
                continue
            
            ips.append(generated_ip)
        
        return ips
    except Exception as e:
        raise ValueError(f"Error generating IPs: {str(e)}")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ip_subnet = request.form.get('ip_subnet', '').strip()
        gateway = request.form.get('gateway', '').strip()
        
        try:
            ips = generate_ip_pool(ip_subnet, gateway)
            return render_template('index.html', 
                                 ips=ips, 
                                 ip_subnet=ip_subnet, 
                                 gateway=gateway,
                                 total_ips=len(ips))
        except Exception as e:
            error = f"Error: {str(e)}"
            return render_template('index.html', error=error)
    
    return render_template('index.html')


@app.route('/download')
def download():
    ip_subnet = request.args.get('ip_subnet', '')
    gateway = request.args.get('gateway', '')
    
    if not ip_subnet:
        return "No IP/Subnet provided", 400
    
    try:
        ip, subnet_cidr = ip_subnet.split('/')
        subnet_mask = cidr_to_subnet_mask(subnet_cidr)
        
        ips = generate_ip_pool(ip_subnet, gateway)
        
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        
        for ip in ips:
            writer.writerow([ip, gateway, subnet_mask])
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment; filename=ip_pool.csv"}
        )
    except Exception as e:
        return f"Error generating CSV: {str(e)}", 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
