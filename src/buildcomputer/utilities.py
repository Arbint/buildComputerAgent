import os

def GetAPIKey():
    return os.environ.get("CLAUDE_API_KEY", default ="Not Found")

def GetGreyBG():
    GREY_BG = "\033[48;5;252m\033[38;5;17m"
    return GREY_BG

def GetReset():
    RESET = "\033[0m"
    return RESET
