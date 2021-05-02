import time
import py7zr
import threading
from datetime import date, datetime
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

backupWaitTime = 10
delayTime = 4
isBackupThreadAlive = False

lastTick = datetime.now()
lastBackup = None
threads = []

save_location = "C:\\Users\\alexm\\AppData\\Local\\kenshi\\save\\quicksave"
backup_location = "C:\\Users\\alexm\\AppData\\Local\\kenshi\\save"

def generate_datestring() -> str:
    # dd/mm/YY H:M:S
    return datetime.now().strftime("%d-%m-%Y_%H.%M.%S")


def threadJob():
    global isBackupThreadAlive
    global lastTick
    global save_location
    global delayTime

    print(f"Doing backup... Waiting {delayTime}s before executing.")
    time.sleep(delayTime)
    with py7zr.SevenZipFile(f'{backup_location}\\quicksave_{generate_datestring()}.7z', 'w') as archive:
        archive.writeall(save_location)
    isBackupThreadAlive = False

    lastTick = datetime.now()
    print("Backup done.")


def launchThread():
    global threads
    t = threading.Thread(target=threadJob)
    threads.append(t)
    t.start()


def do_backup():
    global isBackupThreadAlive

    if not isBackupThreadAlive:
        isBackupThreadAlive = True
        launchThread()


def tickle_backuper():
    global lastTick
    global backupWaitTime

    if (datetime.now() - lastTick).total_seconds() > backupWaitTime:
        lastTick = datetime.now()
        do_backup()


def on_any(event):
    tickle_backuper()


def on_created(event):
    on_any(event)
    print(f" CREATION: {event.src_path} has been created")


def on_deleted(event):
    on_any(event)
    print(f"DELETED: {event.src_path} has been deleted")


def on_modified(event):
    on_any(event)
    print(f"MODIFIED: {event.src_path} has been modified")


def on_moved(event):
    on_any(event)
    print(f"MOVED: {event.src_path} to {event.dest_path}")


if __name__ == "__main__":

    patterns = "*"
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(
        patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved

    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, save_location, recursive=go_recursively)
    my_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()
