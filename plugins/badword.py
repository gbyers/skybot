from util import hook
import time, re

privmsg = {}
badwords = ["\007"]

@hook.command
def addbadword(inp, input=None):
    if input.nick in ["nathan","cups"]:
        if inp.lower() not in badwords:
            time.sleep(1)
            badwords.append(inp)
            return "Done"
        else:
            return "%s already in badwords"%inp.lower()

@hook.command
def delbadword(inp, input=None):
    if input.nick in ["nathan","cups"]:
        badwords.remove(inp)
        return "Done"

@hook.command
def badwordlist(inp, input=None):
    if input.nick in ["nathan","cups"]:
        return ", ".join(badwords)

@hook.event('PRIVMSG')
def _privmsg(inp, input=None, conn=None):
    chan = input.chan.lower()
    nick = input.nick.lower()
    bad = "("
    bad+= "|".join(badwords)
    bad+= ")"
    m = re.search(bad,inp[1],re.I)
    if m: conn.cmd("KICK %s %s :Badword detected"%(input.chan,input.nick))
