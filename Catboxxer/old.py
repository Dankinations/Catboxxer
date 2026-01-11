# from catbox import catboxAPI
# import sys
# from pathlib import Path
# import colorama
# from ui import UI

# MAIN_UI = UI()

# arguments = sys.argv
# apikeylocation = Path(__file__).resolve().parent / "catboxhash.txt"
# API_KEY = ""

# if getattr(sys, 'frozen', False):
#     apikeylocation = Path(sys.executable).parent / "catboxhash.txt"

# if apikeylocation.exists():
#     with open(apikeylocation, "r") as f:
#         API_KEY = f.read().strip()
# else:
#     with open(apikeylocation, "w") as f:
#         f.write("")

# NO_HASH_ERROR = f"{colorama.Fore.RED}No hash key set. Please set it using 'catboxxer sethash <your_hash_key>'{colorama.Fore.RESET}"

# def upload_file_to_catbox(file_path):
#     catbox = catboxAPI(API_KEY)
#     response = catbox.upload_file(file_path)
#     if response:
#         return f"File uploaded successfully: {response.text}"
#     else:
#         raise Exception("Invalid file uploaded or failed to upload.")

# ## COMMAND FUNCS ##

# def CMD_upload():
#     if not API_KEY:
#         print(NO_HASH_ERROR)
#         return
#     if len(arguments) <= 2:
#         print(f"{colorama.Fore.CYAN}Usage: catboxxer upload <file_path>{colorama.Fore.RESET}")
#         return
#     file_path = arguments[2]
#     try:
#         result = upload_file_to_catbox(file_path)
#         print(result)
#     except Exception as e:
#         print(f"Error: {e}")

# def CMD_help():
#     print(f"{colorama.Fore.GREEN}== Catboxxer Help =={colorama.Fore.RESET}")
#     print(f"{colorama.Fore.CYAN}help{colorama.Fore.RESET} - Displays this help message")
#     print(f"{colorama.Fore.CYAN}upload <file path>{colorama.Fore.RESET} - Uploads the specified file to catbox and returns the URL")
#     print(f"{colorama.Fore.CYAN}sethash <hash>{colorama.Fore.RESET} - Sets the user hash for accessing catbox api, get your hash from https://catbox.moe/user/manage.php")
#     print(f"{colorama.Fore.GREEN}====================={colorama.Fore.RESET}")

# def CMD_sethash():
#     if len(arguments) <= 2:
#         print(f"{colorama.Fore.CYAN}Usage: catboxxer sethash <hash key from https://catbox.moe/user/manage.php>{colorama.Fore.RESET}")
#         return
#     global API_KEY
#     API_KEY = arguments[2]
#     open(apikeylocation, "w").write(API_KEY)
#     print(f"{colorama.Fore.GREEN}Hash key set successfully{colorama.Fore.RESET}")

# cmds = {
#     "upload": CMD_upload,
#     "help": CMD_help,
#     "sethash": CMD_sethash,
# }

# for i in cmds:
#     if len(arguments) <= 1:
#         cmds["help"]()
#         break
#     if arguments[1] == i:
#         cmds[i]()

