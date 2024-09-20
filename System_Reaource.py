import tkinter as tk
from tkinter import ttk
import psutil
import matplotlib.pyplot as  plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore
import threading
import time

class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("System Resource Monitor")
        self.root.geometry("1200x800")

        #setup frame
        self.info.frame = ttk.LabelFrame(self.root, text = "System Infomation")
        self.info_frame.pack(fill = "both", expend= True, padx = 10, pady= 10)

        self.graph_frame = ttk.LabelFrame(self.root, text="Real-Time Graphs")
        self.graph_frame.pack(fill="both", expend=True, padx=10, pady=10)

        self.graph_frame = ttk.LabelFrame(self.root, text="Real-TTop Proccess")
        self.graph_frame.pack(fill="both", expend=True, padx=10, pady=10)

        self.graph_frame = ttk.LabelFrame(self.root, text="Disk Patritions")
        self.graph_frame.pack(fill="both", expend=True, padx=10, pady=10)

        #CPU Memory Disk Network Battery GPU Labels
        self.cpu_label = ttk.Label(self.info_frame, text="CPU Usage: ", font=("Helvetica", 12))
        self.cpu_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.cpu_label = ttk.Label(self.info_frame, text="Memory Usage: ", font=("Helvetica", 12))
        self.cpu_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        self.cpu_label = ttk.Label(self.info_frame, text="Disk Usage: ", font=("Helvetica", 12))
        self.cpu_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.cpu_label = ttk.Label(self.info_frame, text="Network Usage(Down/Up): ", font=("Helvetica", 12))
        self.cpu_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

        self.cpu_label = ttk.Label(self.info_frame, text="CPU Temperature: ", font=("Helvetica", 12))
        self.cpu_label.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)

        self.cpu_label = ttk.Label(self.info_frame, text="Battery Usage: ", font=("Helvetica", 12))
        self.cpu_label.grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)

        self.cpu_label = ttk.Label(self.info_frame, text="GPU Usage: ", font=("Helvetica", 12))
        self.cpu_label.grid(row=6, column=0, padx=10, pady=10, sticky=tk.W)


        # Initilize matplotlib figures for CPU , Memory, Disk, and Network graphs
        self.fig, (self.ax1, self.ax2,self.ax3, self.ax4) = plt.subplots(4, 1, figsize=(10,12))
        self.fig.tight_layout(pad=3)

        self.canvas = FigureCanvasTkAgg(self.fig, master = self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expend=True)

        self.cpu_usage_data = []
        self.memory_usage_data = []
        self.disk_usage_data = []
        self.network_down_data = []
        self.network_up_data = []

        # Listbox for display top process
        self.process_listbox = tk.Listbox(self.process_frame, height=10, font=("Helvatica", 12))
        self.process_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Listbox for disk partitions
        self.partition_listbox = tk.Listbox(self.partition_frame, height=5, font=("Helvatica", 12))
        self.partition_listbox.pack(fill="both", expand=True, padx=10, pady=10)     

        # Start Update thread
        self.update_thread = threading.Thread(target=self.update_data)
        self.update_thread.daemon = True
        self.update_thread.start()

    def update_data(self):
        last_net = psutil.net_io_counters()
        while True:
            #Gather system infomation
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
            disk_info = psutil.disk_usage('/')
            net_info = psutil.net_io_counters()
            network_down = (net_info.bytes_recv - last_net.bytes_recv) / 1024 /1024 #MB/s
            network_down = (net_info.bytes_sent - last_net.bytes_sent) / 1024 /1024 #MB/s
            last_net = net_info
            try:
                #Get CPU temperature (some system may not support this)
                temp_info = psutil.sensors_temperatures().get('coretemp',[])[0]
                temp = temp_info.current if temp_info else None
                self.temp_label.config(text=f"CPU Temperature: {temp:.1f}°C" if temp else "CPU Temperature : N/A")
            except:
                self.temp_label.config(text="CPU Temperature: N/A")

            # Get battery status
            battery = psutil.sensors_battery()
            if battery:
                battery_status = f"{battery.percent}% {'Charging' if battery.power_plugged else 'Discharging'}"
                self.battery_label.config(text="Battery Status: {battery_status}")
            else:
                self.battery_lebel.config(text="Battery Status: N/A")
            time.sleep(1)

    def update_process_listbox(self):
        #Clear the listbox
        self.process_listbox.delete(0, tk.END)

        #Getthe 5 process by CPU usage
        processes = [(p.info['cpu_percent'], p.info['name']) for p in psutil.process_iter(['name', 'cpu_percent'])]
        top_processes = sorted(processes, key=lambda x:x[0], reverse=True)[:5]

        for cpu_percent, name in top_processes:
            self.process_listbox.insert(tk.END, f"{name}: {cpu_percent}% CPU")

    def show_alarm(self, message):
        alarm_window = tk.Toplevel(self.root)
        alarm_window.title("Alarm")
        alarm_label = ttk.Label(alarm_window, text=message, font=("Helvetica", 14))
        alarm_label.pack(padx=20, pady=20)
        ok_button = ttk.Button(alarm_label, text="OK",command=alarm_label.destroy)
        ok_button.pack(pady=10)