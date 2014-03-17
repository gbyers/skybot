# -- coding: utf8 --
from util import hook, http
import HTMLParser

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
        cloak = inp.lower()
        user = input.nick
        #conn.cmd("PRIVMSG #services :\002%s\002 change cloak to \002%s\002"%(user,cloak))
        if cloak == "masked":
            conn.cmd("PRIVMSG NickServ :vhost %s on pond/%s"%(user,user))
            return "Done"
        elif cloak == "user":
            conn.cmd("PRIVMSG NickServ :vhost %s on %s.pond.sx"%(user,user))
            return "Done"
        else:
            if cloak == "": return "Usage: cloak masked/user/<custom>"
            else:
                conn.cmd("PRIVMSG NickServ :vhost %s on %s"%(user,cloak))
                return "Done"
    else:
        return "Usage: cloak masked/user/<custom>"
