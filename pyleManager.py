import os, sys, termios, tty

local_folder = os.path.abspath(os.getcwd()) + '/' # save original path
index = 0 # dummy index
hidden = False # toggle hidden
instructions = 'INSTRUCTIONS:\n\n  leftArrow = previous folder\n  rightArrow = open folder\select file\n  upArrow = up\n  downArrow = down\n  q = quit\n  h = toggle hidden files\n  prefix * means folder\n\npress any button to continue'

def main():
    pass

if __name__ == "__main__":
    print('Press enter')

# LIST OF FOLDERS AND FILES
def directory():
    global hidden
    dirs = sorted([x for x in os.listdir() if os.path.isdir(os.path.abspath(os.getcwd()) + '/' + x) and (hidden or not x.startswith('.') )], key=lambda s: s.lower())
    files = sorted([x for x in os.listdir() if x not in dirs and (hidden or not x.startswith('.') )], key=lambda s: s.lower())
    return dirs + files

# CLEAN TERMINAL
def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

# INDEX UPDATER
def index_dir():
    global index
    if len(directory()) > 0:
        index = index % len(directory())
    else:
        index = 0

# PRINTING FUNCTION
def dir_printer():
    global index
    clear()
    # path directory
    print('press i for instructions\n\n' + os.path.abspath(os.getcwd()) + '/\n')
    # folders and pointer
    if len(directory()) == 0:
        print('**EMPTY FOLDER**')
    else:
        index_dir()
        temp_sel = directory()[index]
        for x in directory():
            if x == temp_sel:
                print('->', end='')
            else:
                print('  ', end='')
            if os.path.isdir(os.path.abspath(os.getcwd()) + '/' + x):
                print('*', end='')
            else:
                print(' ', end='')
            print(x)

# FETCH KEYBOARD INPUT
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

dir_printer()

# MAIN ROUTINE
while True:
    index_dir() # update index
    match getch():
        # quit
        case 'q':
            break
         # toggle hidden
        case 'h':
            hidden = not hidden
        # instructions
        case 'i':
            clear()
            print(instructions)
            getch()
        case '\x1b':
            if getch() == '[':
                match getch():
                    # left
                    case 'D':
                        os.chdir('..')
                    # up
                    case 'A' if len(directory()) > 0:
                        index = index - 1
                    # down
                    case 'B' if len(directory()) > 0:
                        index = index + 1
                    # right
                    case 'C' if len(directory()) > 0:
                        selection = os.path.abspath(os.getcwd()) + '/' + directory()[index]
                        if os.path.isdir(selection):
                            os.chdir(selection)
                        elif os.path.isfile(selection):
                            clear()
                            print(selection)
                            break
                    case _:
                        pass
        case _:
            pass
    dir_printer()

os.chdir(local_folder)
