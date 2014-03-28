# -- coding: utf8 --
from util import hook, http
import HTMLParser, re

@hook.command
def motd(inp, conn=None, input=None):
    if input.nick.lower() in ["ducky","nathan"]:
        pid = inp.split(" ")[0]
        p = http.get_json("http://p.rly.sx/api/paste/%s"%pid)
        if "paste" in p:
            h = HTMLParser.HTMLParser()
            paste = h.unescape(p["raw"])
            title = p["title"]
            if "motd" in title.lower():
                f = open("/home/nathan/.irc-ssl/etc/ircd.motd","w")
                f.write(paste.encode("utf8","ignore"))
                f.close()
                #commands.getoutput("echo %s > /home/nathan/.irc/etc/ircd.motd"%paste)
                conn.cmd("REHASH motd")
                return "Updated to \"%s\""%p["title"]
            else:
                return "Not a valid MOTD paste"
        else:
            return "Not found"

@hook.command
def cloak(inp, conn=None, input=None):
    if inp.count(" ") == 0:
        cloak = inp.lower().replace(".net",".not").replace(".com",".c0m").replace(".org",".0rg").replace(".overdrive.pw","user").replace("service","user").replace("overdrive-irc/","user/")
        cloak = re.sub("(staff\/|services?|overdrive\.pw|overdrive-irc\/)","",inp.lower())
        user = input.nick
        #return cloak
        conn.cmd("PRIVMSG HostServ :vhost %s %s"%(user,cloak))
    else:
        return "Usage: cloak <cloak>"
