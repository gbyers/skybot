from util import http, hook

@hook.command
def isup(inp):
    "isup <url> -- checks if the website is up or not"
    data = http.get("http://isup.me/%s"%inp)
    if "If you can see this page and still think we're down, it's just you." in data:
        return ("If you can see this text and still think we're down, it's just you.")
    elif "It's just you." in data:
        return ("It's just you.")
    else:
        return ("It's not just you")
