# REQUIRED MODULES
import os, sys, time, argparse
from platform import system
from itertools import chain

if os.name == "posix":
    import termios, tty
elif os.name == "nt":
    from msvcrt import getch as getch_encoded
else:
    sys.exit("Operating system not recognised")


# ARGUMENT PARSER
parser = argparse.ArgumentParser(prog="pyleManager", description="file manager written in Python")
parser.add_argument("-p", "--picker", action="store_true", help="use pyleManager as a file selector")
args = parser.parse_args() # args.picker contains the modality
picker = args.picker


# GLOBAL VARIABLES
local_folder = os.path.abspath(os.getcwd()) # save original path
dimension = False 
time_modified = False
hidden = False
beep = False
permission = False
index = 0  # dummy index
order = 0
current_directory = None
from_file = 0
rows_len = os.get_terminal_size().lines
instruction_string = None


# RETURN FILE SIZE AS A STRING
def file_size(path):
    size = os.lstat(path).st_size
    i = len(str(size)) // 3
    if len(str(size)) % 3 == 0:
        i -= 1
    if i > 3:
        i = 3
    size /= 1000**i
    return f'{size:.2f}{("b","kb","mb","gb")[i]}'


# UPDATE ORDER, 0 stay 1 next
def order_update(j):
    global order
    old_order = order
    # create a vector with (1,a,b) where a,b are one if dimension and time_modified are enabled
    vec = (1,
           dimension * (True in (os.path.isfile(x) for x in directory())),
           time_modified * (True in (os.path.isfile(x) for x in directory())))
    # search the next 1 and if not found return 0
    order = vec.index(1,order+j) if 1 in vec[order+j:] else 0
    if order != old_order:
        # only update if the previous order was changed
        global current_directory
        current_directory = None
    

# LIST OF FOLDERS AND FILES
def directory():
    # return the previous value if exists
    global current_directory
    if current_directory is None:
        # order by
        match order:
            # size
            case 1:
                dirs = list( chain( (x[0] for x in sorted({x:os.lstat(x).st_size for x in os.listdir()
                                                           if os.path.isdir(x) and (hidden or not x.startswith(".") )}.items(), key=lambda x:x[1])),
                                    (x[0] for x in sorted({x:os.lstat(x).st_size for x in os.listdir()
                                                           if os.path.isfile(x) and (hidden or not x.startswith(".") )}.items(), key=lambda x:x[1])) ) )
            # time modified
            case 2:
                dirs = list( chain( (x[0] for x in sorted({x:os.lstat(x).st_mtime for x in os.listdir()
                                                           if os.path.isdir(x) and (hidden or not x.startswith(".") )}.items(), key=lambda x:x[1])),
                                    (x[0] for x in sorted({x:os.lstat(x).st_mtime for x in os.listdir()
                                                           if os.path.isfile(x) and (hidden or not x.startswith(".") )}.items(), key=lambda x:x[1])) ) )
            # name
            case _: # 0 and unrecognised values
                dirs = list( chain( sorted((x for x in os.listdir()
                                            if os.path.isdir(x) and (hidden or not x.startswith(".") ) ), key=lambda s: s.lower()),
                                    sorted((x for x in os.listdir()
                                            if os.path.isfile(x) and (hidden or not x.startswith(".") )), key=lambda s: s.lower()) ) )
        current_directory = dirs
    return current_directory


# CLEAN TERMINAL
if os.name == "posix":
    def clear():
        os.system("clear")
elif os.name == "nt":
    def clear():
        os.system("cls")


# PRINTING FUNCTION
def dir_printer(position = True):
    clear()
    # length of columns
    columns_len = os.get_terminal_size().columns
    # path directory
    to_print = ["### pyleManager --- press i for instructions ###"[:columns_len], "\n"]
    # name folder
    to_print.append( f"{'... ' if  len(os.path.abspath(os.getcwd())) > columns_len else ''}{os.path.abspath(os.getcwd())[-columns_len+5:]}{os.sep}\n" )
    # folders and pointer
    if len(directory()) == 0:
        to_print.append( " **EMPTY FOLDER**" )
    else:
        order_update(0)
        l_size = max((len(file_size(x)) for x in directory()))
    
        to_print.append( f" {'v' if order == 0 else ' '}*NAME*" )
        columns = ""
        if dimension and True in (os.path.isfile(x) for x in directory()):
            columns += f" |{'v' if order == 1 else ' '}*SIZE*{' '*(l_size-6)}"
        if time_modified and True in (os.path.isfile(x) for x in directory()):
            columns += f" |{'v' if order == 2 else ' '}*TIME MODIFIED*{' '*4}"
        if permission: 
            columns += f" | *PERM*"

        to_print.append( f"{' '*(columns_len - len(columns)-8)}{columns}" )

        for x in directory()[from_file: from_file + rows_len - 3]:
            to_print.append( f"\n {'<' if os.path.isdir(x) else ' '}" )

            columns = ""
            if dimension and os.path.isfile(x):
                columns += f" | {file_size(x)}{' '*(l_size - len(file_size(x)))}"
            if time_modified and os.path.isfile(x):
                columns += f" | {time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(time.ctime(os.lstat(x).st_mtime)))}"
            if permission:
                permissions = os.stat(x).st_mode
                columns += f" | {'r' if permissions & 0o400 else '-'} {'w' if permissions & 0o200 else '-'} {'e' if permissions & 0o100 else '-'} "
                
            name_x = f"{f'... {x[-(columns_len - 6 - len(columns)):]}' if len(x) > columns_len - 2 - len(columns) else x}"
            to_print.append( f"{name_x}{' '*(columns_len-len(name_x)-len(columns) - 2)}{columns}" )

    print("".join(to_print), end = "\r")

    if position:
        sys.stdout.write(f'\033[{ min(len(directory()), rows_len-3)  }A')
        print()
    

# FETCH KEYBOARD INPUT
if os.name == "posix":
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    conv_arrows = {"D":"left", "C":"right", "A":"up", "B":"down"}
    def get_key():
        key_pressed = getch()
        match key_pressed:
            case "\r":
                return "enter"
            case "\x1b":
                if getch() == "[":
                    return conv_arrows.get(getch(), None)
            case _:
                return key_pressed
elif os.name == "nt":
    def getch():
        return getch_encoded().decode('UTF-8')
    
    conv_arrows = {"K":"left", "M":"right", "H":"up", "P":"down"}
    def get_key():
        key_pressed = getch()
        match key_pressed:
            case "\r":
                return "enter"
            case "\xe0":
                return conv_arrows.get(getch(), None)
            case _:
                return key_pressed


# INSTRUCTIONS
def instructions():
    clear()
    print(instruction_string, end = "")
    getch()


# BEEP
def beeper():
    if beep:
        sys.stdout.write('\033[2A')
        print("\a\n")


# RESET FOLDER SETTINGS
def print_folder(refresh = False):
    global from_file, index
    from_file = 0
    index = 0
    if refresh:
        global current_directory
        current_directory = None
    dir_printer()


# FILE MANAGER
def main(*args):
    global index, dimension, time_modified, from_file, hidden, rows_len, beep, instruction_string, permission
    
    if args and args[0] in ["-p", "--picker"]:
        global picker
        picker = True
    
    instruction_string = f"""INSTRUCTIONS:

the prefix \"<\" means folder

upArrow = up
downArrow = down
rightArrow = open folder
leftArrow = previous folder
q = quit
r = refresh
h = toggle hidden files
d = toggle file size
t = toggle time last modified
b = toggle beep
p = toggle permission
m = change ordering
enter = {
        'select file' if picker else 'open using the default application launcher'}
e = {'--disabled--' if picker else 'edit using command-line editor'}

def selection_permission(path):

press any button to continue"""

    dir_printer()

    while True:

        rows_len = os.get_terminal_size().lines
        
        if len(directory()) > 0:
            selection = directory()[index] # + file name if any

        match get_key():
            # up
            case "up":
                if len(directory()) > 0 and index > 0:
                    index -= 1
                    if index >= from_file:
                        # print up when we are in the range of visibility
                        sys.stdout.write('\033[2A')
                        print()
                    else:
                        # else print up one
                        from_file -= 1
                        dir_printer()
                else:
                    beeper()

            # down
            case "down":
                if len(directory()) > 0 and index < len(directory())-1:
                    index += 1
                    if index < rows_len - 3 + from_file:
                        # print down when we are in the range of visibility
                        print()
                    else:
                        # else print down 1
                        from_file += 1
                        dir_printer(position=False)
                else:
                    beeper()

            # right
            case "right":
                if len(directory()) > 0 and os.path.isdir(selection):
                    os.chdir(selection)
                    print_folder(refresh=True)
                else:
                    beeper()

            # left
            case "left":
                if os.path.dirname(os.getcwd()) != os.getcwd():
                    os.chdir("..")
                    print_folder(refresh=True)
                else:
                    beeper()

            # quit
            case "q":
                clear()
                os.chdir(local_folder)
                return
            
            # refresh
            case "r":
                print_folder(refresh = True)
            
            # toggle hidden
            case "h":
                hidden = not hidden
                print_folder(refresh = True)
            
            # size
            case "d":
                dimension = not dimension
                print_folder()

            # time
            case "t":
                time_modified = not time_modified
                print_folder()

            # beep
            case "b":
                beep = not beep

            # permission
            case "p":
                permission = not permission
                print_folder()

            # change order
            case "m":
                order_update(1)
                print_folder()
                
            # enter
            case "enter":
                if len(directory()) > 0:
                    if picker:
                        path = os.path.join(os.getcwd(), selection) #{os.sep if os.path.isdir(selection) else ''}"
                        clear()
                        os.chdir(local_folder)
                        return path
                    elif not picker:
                        selection = selection.replace("\"", "\\\"")
                        match system():
                            case "Linux":
                                os.system(f"xdg-open \"{selection}\"")
                            case "Windows":
                                os.system(selection)
                            case "Darwin":
                                os.system(f"open \"{selection}\"")
                            case _:
                                clear()
                                print("system not recognised, press any button to continue")
                                getch()
                else:
                    beeper()
            
            # command-line editor
            case "e":
                if len(directory()) > 0 and not picker:
                    selection = selection.replace("\"", "\\\"")
                    match system():
                        case "Linux":
                            os.system(f"$EDITOR \"{selection}\"")
                        case "Windows":
                            clear()
                            print(
                                "Windows does not have any built-in command line editor, press any button to continue")
                            getch()
                        case "Darwin":
                            os.system(f"open -e \"{selection}\"")
                        case _:
                            clear()
                            print(
                                "system not recognised, press any button to continue")
                            getch()
                else:
                    beeper()

            # instructions
            case "i":
                instructions()
                print_folder()
                
            case _:
                pass


if __name__ == "__main__":
    main()
