from flask import Flask, render_template_string, request, send_file
import io
import csv
import ipaddress

app = Flask(__name__)

# Inline HTML (same UI as Replit)
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>IP Pool Generator - SF - NOC</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f6fa; }
        h1 { color: #2f3640; }
        input, button { padding: 10px; margin: 5px 0; }
        button { cursor: pointer; background: #40739e; color: white; border: none; border-radius: 5px; }
        button:hover { background: #273c75; }
        textarea { width: 100%; height: 250px; margin-top: 15px; }
    </style>
</head>
<body>
    <h1>IP Pool Generator - SF - NOC</h1>
    <form method="POST" action="/generate">
        <label>IP/Subnet:</label><br>
        <input type="text" name="ip_subnet" value="192.168.1.0/22" required><br>
        <label>Gateway:</label><br>
        <input type="text" name="gateway" value="192.168.1.1" required><br>
        <button type="submit">Generate</button>
    </form>

    {% if result %}
    <h3>Generated IPs ({{ count }})</h3>
    <form method="POST" action="/export">
        <input type="hidden" name="ip_subnet" value="{{ ip_subnet }}">
        <input type="hidden" name="gateway" value="{{ gateway }}">
        <textarea readonly>{{ result }}</textarea><br>
        <button type="submit">Export CSV</button>
    </form>
    {% endif %}
</body>
</html>
"""

def cidr_to_netmask(cidr):
    """Convert CIDR (e.g. /22) to subnet mask (255.255.252.0)."""
    try:
        network = ipaddress.ip_network(f"0.0.0.0/{cidr}", strict=False)
        return str(network.netmask)
    except Exception:
        return None

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML)

@app.route('/generate', methods=['POST'])
def generate():
    ip_subnet = request.form['ip_subnet'].strip()
    gateway = request.form['gateway'].strip()

    try:
        network = ipaddress.ip_network(ip_subnet, strict=False)
        all_hosts = list(network.hosts())

        # Skip gateway (first usable IP)
        usable_ips = all_hosts[1:] if len(all_hosts) > 1 else []

        ip_list = [str(ip) for ip in usable_ips]
        result = "\n".join(ip_list)

        return render_template_string(
            HTML,
            result=result,
            count=len(ip_list),
            ip_subnet=ip_subnet,
            gateway=gateway
        )
    except Exception as e:
        return f"<h3 style='color:red;'>Error: {str(e)}</h3>"

@app.route('/export', methods=['POST'])
def export():
    ip_subnet = request.form['ip_subnet'].strip()
    gateway = request.form['gateway'].strip()

    try:
        network = ipaddress.ip_network(ip_subnet, strict=False)
        all_hosts = list(network.hosts())
        usable_ips = all_hosts[1:] if len(all_hosts) > 1 else []

        subnet_mask = cidr_to_netmask(ip_subnet.split('/')[-1])

        output = io.StringIO()
        writer = csv.writer(output, lineterminator='\n')

        # Write IP, Gateway, Subnet Mask (no header)
        for ip in usable_ips:
            writer.writerow([str(ip), gateway, subnet_mask])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='ip_pool.csv'
        )
    except Exception as e:
        return f"<h3 style='color:red;'>Error exporting CSV: {str(e)}</h3>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
