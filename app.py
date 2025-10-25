from flask import Flask, render_template, request, send_file
import csv
import io
import ipaddress
import webbrowser
import threading

app = Flask(__name__)

# Function to generate IP pool
def generate_ip_pool(ip_subnet, gateway):
    try:
        network = ipaddress.ip_network(ip_subnet, strict=False)
        ips = [str(ip) for ip in network.hosts()]

        # Remove gateway (x.1) and start from x.2
        if gateway in ips:
            ips.remove(gateway)

        return ips, len(ips)
    except Exception as e:
        raise ValueError(f"Invalid subnet or IP format: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    ips = []
    total_ips = 0
    ip_subnet = ""
    gateway = ""
    error = None

    if request.method == "POST":
        ip_subnet = request.form.get("ip_subnet", "").strip()
        gateway = request.form.get("gateway", "").strip()

        try:
            ips, total_ips = generate_ip_pool(ip_subnet, gateway)
        except Exception as e:
            error = str(e)

    return render_template(
        "index.html",
        ips=ips,
        total_ips=total_ips,
        ip_subnet=ip_subnet,
        gateway=gateway,
        error=error
    )

@app.route("/download")
def download_csv():
    ip_subnet = request.args.get("ip_subnet")
    gateway = request.args.get("gateway")

    try:
        ips, _ = generate_ip_pool(ip_subnet, gateway)
    except Exception as e:
        return f"Error: {e}"

    output = io.StringIO()
    writer = csv.writer(output)

    # Write CSV (without headers)
    for ip in ips:
        writer.writerow([ip, gateway, "255.255.252.0"])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="ip_pool.csv"
    )

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    app.run(debug=False, port=5000)
