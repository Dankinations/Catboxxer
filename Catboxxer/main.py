from catbox import catboxAPI
import sys
from pathlib import Path
import colorama

arguments = sys.argv
apikeylocation = Path(__file__).resolve().parent / "catboxhash.txt"

NO_HASH_ERROR = f"{colorama.Fore.RED}No hash key set. Please set it using 'catboxxer sethash <your_hash_key>'{colorama.Fore.RESET}"
API_KEY = ""

if apikeylocation.exists():
    with open(apikeylocation, "r") as f:
        API_KEY = f.read().strip()
else:
    with open(apikeylocation, "w") as f:
        f.write("")

def upload_file_to_catbox(file_path):
    catbox = catboxAPI(API_KEY)
    response = catbox.upload_file(file_path)
    if response:
        return f"File uploaded successfully: {response.text}"
    else:
        raise Exception("Invalid file uploaded or failed to upload.")

## COMMAND FUNCS ##

def CMD_upload():
    if not API_KEY:
        print(NO_HASH_ERROR)
        return
    if len(arguments) <= 2:
        print("Usage: catboxxer upload <file_path>")
        return
    file_path = arguments[2]
    try:
        result = upload_file_to_catbox(file_path)
        print(result)
    except Exception as e:
        print(f"Error: {e}")

def CMD_help():
    print(f"{colorama.Fore.GREEN}== Catboxxer Help =={colorama.Fore.RESET}")
    print(f"{colorama.Fore.CYAN}upload{colorama.Fore.RESET} - Uploads the specified file to Catbox.moe and returns the URL")
    print(f"{colorama.Fore.CYAN}help{colorama.Fore.RESET} - Displays this help message")
    print(f"{colorama.Fore.CYAN}====================={colorama.Fore.RESET}")

def CMD_sethash():
    if len(arguments) <= 2:
        print("Usage: catboxxer sethash <hash key from https://catbox.moe/user/manage.php>")
        return
    global API_KEY
    API_KEY = arguments[2]
    open(apikeylocation, "w").write(API_KEY)
    print(f"{colorama.Fore.GREEN}Hash key set successfully{colorama.Fore.RESET}")

cmds = {
    "upload": CMD_upload,
    "help": CMD_help,
    "sethash": CMD_sethash,
}

for i in cmds:
    if len(arguments) <= 2:
        cmds["help"]()
        break
    if arguments[1] == i:
        cmds[i]()

