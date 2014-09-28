from util import hook
import time

pings = {}
versions = {}

@hook.command(autohelp=False)
def ping(inp, input=None, conn=None):
    "ping [nick] -- returns ping time for you or [nick]"
    ptime = time.time()
    if inp[0] != "#":
        if inp:
            pings[inp.lower()] = "%s;%s"%(input.chan,ptime)
            conn.send("PRIVMSG %s :\001PING %s\001"%(inp,ptime))
        else:
            pings[input.nick.lower()] = "%s;%s"%(input.chan,ptime)
            conn.send("PRIVMSG %s :\001PING %s\001"%(input.nick,ptime))
    else:
        return "Cannot CTCP channels"

@hook.command(autohelp=False)
def version(inp, input=None, conn=None):
    "version [nick] -- returns version for you or [nick]"
    if inp[0] != "#":
        if inp:
            versions[inp.lower()] = input.chan
            conn.send("PRIVMSG %s :\001VERSION\001"%(inp))
        else:
            versions[input.nick.lower()] = input.chan
            conn.send("PRIVMSG %s :\001VERSION\001"%(input.nick))
    else:
        return "Cannot CTCP channels"

@hook.event('NOTICE')
def _ping(inp, input=None, conn=None):
    if input.nick.lower() in pings:
        _p = pings[input.nick.lower()]
        chan = _p.split(";")[0]
        _ptime = str(time.time() - float(_p.split(";")[1]))[0:5]
        conn.send("PRIVMSG %s :PING reply from %s: %s seconds"%(chan,input.nick,_ptime))
        del pings[input.nick.lower()]
    if input.nick.lower() in versions:
        version = input.msg.replace("\001VERSION ","").replace("\001","")
        chan = versions[input.nick.lower()]
        conn.send("PRIVMSG %s :VERSION reply from %s: %s"%(chan,input.nick,version))
        del versions[input.nick.lower()]
