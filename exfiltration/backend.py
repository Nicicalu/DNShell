import pyinotify

# Define the path to the BIND log file
BIND_LOG_FILE = "/var/log/named/query.log"

# Create a class that handles the events triggered by pyinotify
class QueryEventHandler(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        # Perform your desired action here
        print("New query arrived!")

# Create an instance of the QueryEventHandler
handler = QueryEventHandler()

# Create a WatchManager object and initialize a notifier
wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm, handler)

# Add a watch for modifications on the BIND log file
wm.add_watch(BIND_LOG_FILE, pyinotify.IN_MODIFY)

# Start the notifier loop
notifier.loop()