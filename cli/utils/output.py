from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

def colorize_output(text, color):
    color_map = {
        "green": Fore.LIGHTGREEN_EX,
        "yellow": Fore.YELLOW,
        "white": Fore.WHITE
    }
    return f"{color_map[color]}{text}"