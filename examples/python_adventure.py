game "Python-Style Adventure"

var health = 100
var score = 0

def start():
    print("Welcome to the Pythonic Quest!")
    print("You are standing in a dark room.")
    choice "Go North" -> hallway
    choice "Go South" -> cellar

def hallway():
    print("The hallway is long and narrow.")
    set score = score + 10
    if score >= 20 goto ending
    print("You see a door.")
    choice "Open Door" -> room
    choice "Go Back" -> start

def cellar():
    print("It's cold here.")
    set health = health - 10
    print("Current Health: " + health)
    if health <= 0 goto death
    choice "Go Back" -> start

def room():
    print("You found the treasure!")
    set score = score + 50
    goto ending

def death():
    print("You perished in the cold.")
    end

def ending():
    print("Story Complete!")
    print("Final Score: " + score)
    return
