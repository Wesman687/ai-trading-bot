import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SyncHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(('.py', '.js', '.ts', '.html')):
            # Upload or send the file content to me here
            with open(event.src_path, 'r') as f:
                code = f.read()
                # You could paste this into a chat here, or automate sending via API
                print(f"Modified: {event.src_path}\n{code[:200]}...")

path = "C:\Code\cryptobot\crypto-trading-bot"
observer = Observer()
observer.schedule(SyncHandler(), path=path, recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()