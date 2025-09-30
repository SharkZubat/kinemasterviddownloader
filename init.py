import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
import re
import os
import threading
import subprocess

def find_kinemaster_template_videos(url):
    def worker():
        TARGET_URL = url
        SOURCE_DOMAIN = "https://cdn-project-feed.kinemasters.com/"
        DOWNLOAD_DIR = "cache"

        status.config(text="Status: Searching for videos...")

        def find_video_sources(url, domain_prefix):
            matching_sources = set()
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                pattern = re.compile(f"^{re.escape(domain_prefix)}.*")
                for attr in ['src', 'href']:
                    for tag in soup.find_all(**{attr: pattern}):
                        matching_sources.add(tag[attr])
            except requests.exceptions.RequestException as e:
                status.config(text="Status: Error fetching URL")
                print(f"An error occurred while fetching the URL: {e}")
            return matching_sources

        def download_file(url, download_folder):
            if not url:
                return
            local_filename = url.split('/')[-1]
            if '?' in local_filename:
                local_filename = local_filename.split('?')[0]
            if not local_filename:
                print(f"[SKIPPED] Could not determine filename for {url}")
                return
            filepath = os.path.join(download_folder, local_filename)
            try:
                print(f"  -> Downloading {local_filename}...")
                status.config(text=f"Status: Downloading {local_filename}...")
                with requests.get(url, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    with open(filepath, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Successfully saved to {filepath}")
            except requests.exceptions.RequestException as e:
                status.config(text=f"Status: Failed to download {local_filename}")
                print(f"FAILED to download {local_filename}: {e}")

        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
            print(f"Created download directory: {DOWNLOAD_DIR}")

        print(f"\nSearching for videos starting with '{SOURCE_DOMAIN}' on {TARGET_URL}...")
        video_links = find_video_sources(TARGET_URL, SOURCE_DOMAIN)

        if video_links:
            print(f"**Found {len(video_links)} unique video sources. Starting download...**")
            status.config(text=f"Status: Found {len(video_links)} videos. Downloading...")
            for i, link in enumerate(video_links, 1):
                print(f"\n[{i}/{len(video_links)}] Attempting to download: {link}")
                download_file(link, DOWNLOAD_DIR)
            print("\n**Download process complete.**")
            status.config(text="Status: Download complete!")
            if auto_open_var.get() and video_links:
                first_video = os.path.join(DOWNLOAD_DIR, os.path.basename(list(video_links)[0].split('?')[0]))
                try:
                    if os.name == 'nt':
                        os.startfile(first_video)
                    elif os.name == 'posix':
                        subprocess.Popen(['xdg-open', first_video])
                except Exception as e:
                    print(f"Failed to auto-open video: {e}")
        else:
            print("\nNo video source URLs were found matching the criteria. Nothing to download.")
            status.config(text="Status: No videos found/Invalid URL.")

    threading.Thread(target=worker, daemon=True).start()


root = tk.Tk()
root.geometry("400x300")
root.title("KMVD by TheSharkGuy")
root.iconbitmap("favicon.ico")
root.resizable(False, False)

title = tk.Label(root, text="KineMaster Video Downloader", font=("Segoe UI SemiBold", 16))
title.pack()
bywhat = tk.Label(root, text="""By TheSharkGuy

A basic KineMaster Video Downloader tool
that you can download anything videos from KineMaster.""")
bywhat.pack()

inputurl = ttk.Entry(root, width=30)
inputurl.pack()

forex = tk.Label(root, text="For example, http://www.kinemaster.com/kinespace/detail/...", fg="#808080")
forex.pack()

downloadbutton = ttk.Button(root, text="Download!", command=lambda: find_kinemaster_template_videos(inputurl.get()))
downloadbutton.pack(side=tk.BOTTOM, pady=6)

status = tk.Label(root, text="Status: Idle")
status.pack(side=tk.BOTTOM)

auto_open_var = tk.BooleanVar()
auto_open_var.set(True)
checkoptionautoopen = ttk.Checkbutton(root, text="Auto-open video when it's completed", variable=auto_open_var)
checkoptionautoopen.pack(side=tk.BOTTOM)

root.mainloop()