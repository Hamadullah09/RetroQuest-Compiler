game "Loop Termination Demo"

var counter = 0
var limit = 5

def start():
    print("Starting loop...")
    print("Current Counter: " + counter)
    
    # Check termination condition
    if counter >= limit goto finish
    
    set counter = counter + 1
    print("Incrementing...")
    choice "Repeat Loop" -> start
    choice "Exit Now" -> finish

def finish():
    print("Loop terminated because counter reached limit or user exited.")
    print("Final Count: " + counter)
    return
