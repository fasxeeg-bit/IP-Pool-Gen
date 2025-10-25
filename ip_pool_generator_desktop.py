import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import csv
import re


class IPPoolGenerator:

    def __init__(self, root):
        self.root = root
        self.root.title("IP Pool Generator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.generated_ips = []
        self.gateway = ""

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)

        title_label = ttk.Label(main_frame,
                                text="IP Pool Generator - SF - NOC",
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        ttk.Label(main_frame, text="IP/Subnet:",
                  font=('Arial', 10)).grid(row=1,
                                           column=0,
                                           sticky=tk.W,
                                           pady=5)
        self.ip_subnet_entry = ttk.Entry(main_frame,
                                         width=30,
                                         font=('Arial', 10))
        self.ip_subnet_entry.grid(row=1,
                                  column=1,
                                  sticky="we",
                                  pady=5,
                                  padx=(5, 10))
        self.ip_subnet_entry.insert(0, "192.168.1.0/22")

        ttk.Label(main_frame, text="Gateway:",
                  font=('Arial', 10)).grid(row=2,
                                           column=0,
                                           sticky=tk.W,
                                           pady=5)
        self.gateway_entry = ttk.Entry(main_frame,
                                       width=30,
                                       font=('Arial', 10))
        self.gateway_entry.grid(row=2,
                                column=1,
                                sticky="we",
                                pady=5,
                                padx=(5, 10))
        self.gateway_entry.insert(0, "192.168.1.1")

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)

        self.generate_btn = ttk.Button(button_frame,
                                       text="Generate IPs",
                                       command=self.generate_ips)
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        self.export_btn = ttk.Button(button_frame,
                                     text="Export to CSV",
                                     command=self.export_csv,
                                     state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(button_frame,
                                    text="Clear",
                                    command=self.clear_results)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        result_frame = ttk.LabelFrame(main_frame,
                                      text="Generated IP Addresses",
                                      padding="5")
        result_frame.grid(row=4,
                          column=0,
                          columnspan=3,
                          sticky="nsew",
                          pady=(10, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(1, weight=1)

        self.info_label = ttk.Label(result_frame,
                                    text="",
                                    font=('Arial', 9, 'italic'))
        self.info_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.result_text = scrolledtext.ScrolledText(result_frame,
                                                     wrap=tk.WORD,
                                                     width=70,
                                                     height=20,
                                                     font=('Courier', 9))
        self.result_text.grid(row=1, column=0, sticky="nsew")

        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=5,
                          column=0,
                          columnspan=3,
                          sticky="we",
                          pady=(5, 0))

        self.status_label = ttk.Label(status_frame,
                                      text="Ready",
                                      font=('Arial', 9),
                                      foreground='green')
        self.status_label.pack(side=tk.LEFT)

    def validate_ip(self, ip):
        pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        match = re.match(pattern, ip)
        if not match:
            return False
        return all(0 <= int(part) <= 255 for part in match.groups())

    def validate_subnet(self, subnet):
        try:
            subnet_int = int(subnet)
            return 8 <= subnet_int <= 30
        except ValueError:
            return False

    def generate_ip_pool(self, ip_subnet):
        try:
            ip, subnet = ip_subnet.split('/')
            subnet = int(subnet)

            parts = list(map(int, ip.split('.')))
            ip_int = (parts[0] << 24) + (parts[1] << 16) + (
                parts[2] << 8) + parts[3]

            total = 2**(32 - subnet)

            ips = []
            for i in range(1, total - 1):
                v = ip_int + i
                generated_ip = f"{(v >> 24) & 255}.{(v >> 16) & 255}.{(v >> 8) & 255}.{v & 255}"
                ips.append(generated_ip)

            return ips
        except Exception as e:
            raise ValueError(f"Error generating IPs: {str(e)}")

    def generate_ips(self):
        ip_subnet = self.ip_subnet_entry.get().strip()
        gateway = self.gateway_entry.get().strip()

        if not ip_subnet or '/' not in ip_subnet:
            messagebox.showerror(
                "Input Error",
                "Please enter IP/Subnet in format: 192.168.1./22")
            return

        try:
            ip, subnet = ip_subnet.split('/')

            if not self.validate_ip(ip):
                messagebox.showerror(
                    "Input Error",
                    "Invalid IP address format. Please use format: 192.168.1.0"
                )
                return

            if not self.validate_subnet(subnet):
                messagebox.showerror("Input Error",
                                     "Subnet must be between 8 and 30")
                return

            if gateway and not self.validate_ip(gateway):
                messagebox.showerror("Input Error",
                                     "Invalid Gateway IP address format")
                return

            self.status_label.config(text="Generating IPs...",
                                     foreground='orange')
            self.root.update()

            self.generated_ips = self.generate_ip_pool(ip_subnet)
            self.gateway = gateway

            self.result_text.delete('1.0', tk.END)

            info_text = f"Total IPs Generated: {len(self.generated_ips)}"
            if gateway:
                info_text += f" | Gateway: {gateway}"
            info_text += f" | Subnet: {ip_subnet}"
            self.info_label.config(text=info_text)

            for ip in self.generated_ips:
                self.result_text.insert(tk.END, ip + '\n')

            self.export_btn.config(state=tk.NORMAL)
            self.status_label.config(
                text=f"Generated {len(self.generated_ips)} IPs successfully",
                foreground='green')

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.config(text="Error occurred", foreground='red')

           def export_csv(self):
        if not self.generated_ips:
            messagebox.showwarning(
                "No Data", "No IPs to export. Please generate IPs first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="ip_pool.csv"
        )

        if file_path:
            try:
                # Extract subnet mask from IP/Subnet entry
                ip_subnet = self.ip_subnet_entry.get().strip()
                _, subnet = ip_subnet.split('/')
                subnet_mask = subnet.strip()

                # Skip first usable IP (gateway)
                ip_list = self.generated_ips[1:] if len(self.generated_ips) > 1 else []

                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    for ip in ip_list:
                        writer.writerow([ip, self.gateway, subnet_mask])

                messagebox.showinfo(
                    "Export Successful",
                    f"IP pool exported successfully to:\n{file_path}")
                self.status_label.config(
                    text=f"Exported {len(ip_list)} IPs to CSV",
                    foreground='green')
            except Exception as e:
                messagebox.showerror("Export Error",
                                     f"Failed to export CSV: {str(e)}")
                self.status_label.config(text="Export failed",
                                         foreground='red')



    def clear_results(self):
        self.result_text.delete('1.0', tk.END)
        self.generated_ips = []
        self.gateway = ""
        self.info_label.config(text="")
        self.export_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Cleared", foreground='green')


def main():
    root = tk.Tk()
    app = IPPoolGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
