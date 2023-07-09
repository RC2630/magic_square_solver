Colour: type = str

ANSI_NORMAL: str = "\033[0m"

ANSI_BLACK: str = "\033[30m"
ANSI_RED: str = "\033[31m"
ANSI_GREEN: str = "\033[32m"
ANSI_YELLOW: str = "\033[33m"
ANSI_BLUE: str = "\033[34m"
ANSI_MAGENTA: str = "\033[35m"
ANSI_CYAN: str = "\033[36m"
ANSI_WHITE: str = "\033[37m"

ANSI_BACKGROUND_BLACK: str = "\033[40m"
ANSI_BACKGROUND_RED: str = "\033[41m"
ANSI_BACKGROUND_GREEN: str = "\033[42m"
ANSI_BACKGROUND_YELLOW: str = "\033[43m"
ANSI_BACKGROUND_BLUE: str = "\033[44m"
ANSI_BACKGROUND_MAGENTA: str = "\033[45m"
ANSI_BACKGROUND_CYAN: str = "\033[46m"
ANSI_BACKGROUND_WHITE: str = "\033[47m"

ANSI_UNDERLINE: str = "\033[4m"
ANSI_BOLD: str = "\033[1m"
ANSI_ITALIC: str = "\033[3m"
ANSI_INVERSE: str = "\033[7m"
ANSI_STRIKETHROUGH: str = "\033[9m"

def input_coloured(prompt: str, colour: Colour, orig_colour: Colour = ANSI_NORMAL) -> str:
    print(prompt + colour, end = "")
    inp: str = input()
    print(orig_colour, end = "")
    return inp