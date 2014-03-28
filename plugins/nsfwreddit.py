
from util import http, hook
import urllib2, json, commands, random
import httplib, re

@hook.event("PRIVMSG")
def do_rand(inp, input=None, conn=None):
    if input.chan.lower() in ["##free"]:
        words = inp[1]
        if "butt" in words:
            data = getJson(False,"r/ass")
        elif "boobies" in words or "boobs" in words:
            data = getJson(False,"r/boobies")
        if "boobies" in words or "boobs" in words or "butt" in words:
            if data:
                data = data["data"]["children"]
                if len(data) >= 1:
                    data = data[random.randint(0,len(data))]
                    linkurl = data["data"]["url"]
                    linktitle = data["data"]["title"]
                    linksub = data["data"]["subreddit"]
                    over_18 = data["data"]["over_18"]
                    #if over_18:
                    conn.cmd("PRIVMSG %s :%s: %s"%(input.chan,input.nick,linkurl))
                    #say("%s - \x02\x0304NSFW\x0f %s - r/%s"%(linktitle,linkurl,linksub))
                    #else:
                    #say("%s - %s - r/%s"%(linktitle,linkurl,linksub))

@hook.command(autohelp=False)
@hook.command('rr', autohelp=False)
def randreddit(inp, say=None):
    ".randreddit/randr/rr [nsfw] [r/sub] -- gets a random link from r/random (default), [nsfw] or from [r/sub]"
    if inp.startswith("r/"):
        try:
            data = getJson(False,inp)
        except:
            return "Nothing found"
    else:
        if inp == "nsfw":
            data = getJson(True,None)
        else:
            data = getJson(False,None)
    if "data" in data:
        data = data["data"]["children"]
        if len(data) >= 1:
            data = data[random.randint(0,len(data))]
            linkurl = data["data"]["url"]
            linktitle = data["data"]["title"]
            linksub = data["data"]["subreddit"]
            over_18 = data["data"]["over_18"]
            if over_18:
                say("%s - \x02\x0304NSFW\x0f \00312%s\003 - r/%s"%(linktitle,linkurl,linksub))
            else:
                say("%s - \00312%s\003 - r/%s"%(linktitle,linkurl,linksub))
        else:
            say("Nothing found")
    else:
        say("Nothing found")

def getJson(nsfw,sub):
    if nsfw and sub == None:
        conn = httplib.HTTPConnection("www.reddit.com")
        conn.request("HEAD", "/r/randnsfw")
        res = conn.getresponse()
        for header in res.getheaders():
            if header[0] == "location":
                url = header[1]
        if not url:
            return "Unable to connect"
    elif nsfw == False and sub:
        if sub is not None:
            url = "http://www.reddit.com/%s.json"%sub
        else:
            conn = httplib.HTTPConnection("www.reddit.com")
            conn.request("HEAD", "/r/random")
            res = conn.getresponse()
            for header in res.getheaders():
                if header[0] == "location":
                    url = header[1]
        if not url:
            return "Unable to connect"
    else:
        conn = httplib.HTTPConnection("www.reddit.com")
        conn.request("HEAD", "/r/random")
        res = conn.getresponse()
        for header in res.getheaders():
            if header[0] == "location":
                url = header[1]
        if not url:
            return "Unable to connect"
    if not sub: url += ".json"
    #print url
    try:
        return http.get_json(url)
    except IOError:
        return ("Unable to conenct to %s"%url)
