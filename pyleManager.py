import os, sys, termios, tty
from platform import system

local_folder = os.path.abspath(os.getcwd()) + '/' # save original path
from settings import *
index = 0 # dummy index
modalities = ['-picker','-manager']

def instructions(mode):
    if mode == '-manager':
        print('''file manager - INSTRUCTIONS:

    leftArrow = previous folder
    rightArrow = open folder\select file
    upArrow = up
    downArrow = down
    q = quit
    h = toggle hidden files
    d = toggle file size
    p = print path
    e = edit using command-line editor
    enter = open using the default application launcher

    prefix ■ means folder

press any button to continue''')
    elif mode == '-picker':
        print('''file picker - INSTRUCTIONS:

    leftArrow = previous folder
    rightArrow = open folder\select file
    upArrow = up
    downArrow = down
    h = toggle hidden files
    d = toggle file size
    p = print path
    
    prefix ■ means folder

press any button to continue''')

# RETURN FILE SIZE AS A STRING
def file_size(path):
    size = os.stat(path).st_size
    i = 0
    while size > 999:
        size = size / 1000
        i = i+1
    metric = ['b','kb','mb','gb']
    return str(round(size,2)) + ' ' + metric[i]

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
        l = max([len(x) for x in directory()]) + 4 # max length file
        for x in directory():
            if x == temp_sel:
                print('->', end='')
            else:
                print('  ', end='')
            if os.path.isdir(os.path.abspath(os.getcwd()) + '/' + x):
                print('■', end='')
            else:
                print(' ', end='')
            print(x, end=' ')
            if dimension and os.path.isfile(os.path.abspath(os.getcwd()) + '/' + x):
                print(' '*(l-len(x)) + file_size(os.path.abspath(os.getcwd()) + '/' + x))
            else:
                print()

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

# file manager
def main(mode = '-manager'):
    global local_folder
    global index
    global hidden
    global dimension
    global modalities
    if mode not in modalities:
        input('mode not recognized, selecting manager..\npress enter to continue')
        mode = '-manager'
    dir_printer()
    while True:
        index_dir() # update index
        match getch():
            # quit
            case 'q' if mode == '-manager':
                open(local_folder + 'settings.py','w').write('hidden = ' + str(hidden) + '\ndimension = ' + str(dimension)) # save config
                clear()
                break
            # toggle hidden
            case 'h':
                temp_name = directory()[index]
                hidden = not hidden
                if temp_name in directory(): # update index
                    index = directory().index(temp_name)
                else:
                    index = 0
            # instructions
            case 'i':
                clear()
                instructions(mode)
                getch()
            # size
            case 'd':
                dimension = not dimension
            # print
            case 'p':
                selection = os.path.abspath(os.getcwd()) + '/' 
                if len(directory()) > 0:
                    selection = selection + directory()[index]
                clear()
                print(selection)
                open(local_folder + 'settings.py','w').write('hidden = ' + str(hidden) + '\ndimension = ' + str(dimension))
                break
            # command-line editor
            case 'e' if len(directory()) > 0 and mode == '-manager':
                if system() == 'Linux':
                    os.system("$EDITOR " + os.path.abspath(os.getcwd()) + '/' + directory()[index])
            case '\r' if len(directory()) > 0 and mode == '-manager':
                if system() == 'Linux':
                    os.system("xdg-open " + os.path.abspath(os.getcwd()) + '/' + directory()[index])
            case '\x1b':
                if getch() == '[':
                    match getch():
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
                        # left
                        case 'D':
                            os.chdir('..')
                        case _:
                            pass
            case _:
                pass
        dir_printer()
    os.chdir(local_folder)

if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except:
        main()
    