from util import hook, http
try:
    import feedparser
except:
    import imp
    feedparser = imp.load_source('feedparser', 'plugins/util/feedparser.py')

@hook.command
def rss(inp, input=None, say=None):
    "rss [<num>] [url] -- get newest feed or num item"
    num = 0
    if inp.count(" ") == 1:
        url = inp.split(" ")[1]
        num = int(inp.split(" ")[0])
    else:
        url = inp
    if not url.startswith("http://"): url = "http://"+url
    feed = feedparser.parse(url)
    if feed:
        if num:
            if len(feed["entries"])-1 >= num:
                newest = feed["entries"][num]
            else:
                return "Max number is %s"%str(len(feed["entries"])-1)
        else:
            newest = feed["entries"][0]
        if newest:
            output = "Title: \002%s\002"%newest["title"]
            #output += " Author: %s"%newest["author"]
            output += " Updated: \002%s\002"%newest["updated"]
            output += " Link: \00312%s\003"%newest["links"][0]["href"]
            say(output)
        else:
            say("Nothing found, try a lower number")
    else:
        say("Unable to parse feed")
