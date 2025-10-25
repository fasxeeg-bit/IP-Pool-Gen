from flask import Flask, render_template, request, send_file
import csv
import io
import ipaddress
import webbrowser
import threading

app = Flask(__name__)

def generate_ip_pool(ip_subnet, gateway):
    try:
        network = ipaddress.ip_network(ip_subnet, strict=False)
        ips = [str(ip) for ip in network.hosts()]
        if gateway in ips:
            ips.remove(gateway)
        return ips
    except Exception as e:
        raise ValueError(f"Invalid input: {e}")

def subnet_to_mask(cidr):
    try:
        return str(ipaddress.IPv4Network(f"0.0.0.0/{cidr}", strict=False).netmask)
    except:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ip_subnet = request.form.get("ip_subnet").strip()
        gateway = request.form.get("gateway").strip()

        try:
            ips = generate_ip_pool(ip_subnet, gateway)
            total_ips = len(ips)
            return render_template(
                "index.html",
                ips=ips,
                total_ips=total_ips,
                ip_subnet=ip_subnet,
                gateway=gateway,
            )
        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")

@app.route("/download")
def download_csv():
    ip_subnet = request.args.get("ip_subnet")
    gateway = request.args.get("gateway")
    try:
        network = ipaddress.ip_network(ip_subnet, strict=False)
        cidr = ip_subnet.split("/")[1]
        subnet_mask = subnet_to_mask(cidr)
        ips = [str(ip) for ip in network.hosts()]
        if gateway in ips:
            ips.remove(gateway)

        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        for ip in ips:
            writer.writerow([ip, gateway, subnet_mask])
        output.seek(0)

        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8")),
            as_attachment=True,
            download_name="ip_pool.csv",
            mimetype="text/csv",
        )
    except Exception as e:
        return f"Error creating CSV: {str(e)}", 400

def open_browser():
    """Automatically open browser after Flask starts"""
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
