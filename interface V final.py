import tkinter as tk
from tkinter import ttk
import subprocess
import threading




def start_program():
    ip = ip_entry.get()
    community = community_entry.get()
    time_from_user = time_entry.get()
    
    error_label.config(text="")
  
    try:
        return_code = subprocess.call(["python", "tool V final.py", ip, community])
        if return_code == 0:
            print("Program successfully completed")
            error_label.config(text="The tool will run again in " + time_from_user + " sec")
            # Create a new thread to call start_program() after the specified time
            threading.Timer(int(time_from_user), start_program).start()
        else:
            error_label.config(text="Sorry, an error occurred while creating the graph.")
    except:
        error_label.config(text="Sorry, an error occurred while creating the graph.")

 

root = tk.Tk()
root.title("Network Topology Discovery")
root.geometry("400x250")

style = ttk.Style(root)
style.theme_use('vista')

ip_label = ttk.Label(root, text="IP Address:")
ip_label.pack(pady=5)
ip_entry = ttk.Entry(root)
ip_entry.pack(pady=5)

community_label = ttk.Label(root, text="Community Name:")
community_label.pack(pady=5)
community_entry = ttk.Entry(root)
community_entry.pack(pady=5)

time_label = ttk.Label(root, text="Time in sec:")
time_label.pack(pady=5)
time_entry = ttk.Entry(root)
time_entry.pack(pady=5)

submit_button = ttk.Button(root, text="Create Graph", command=start_program)
submit_button.pack(pady=10)


error_label = ttk.Label(root, foreground="red")
error_label.pack(pady=5)

root.mainloop()