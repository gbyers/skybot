from util import hook
import time

@hook.command
def traffic(inp,input=None,conn=None):
    global username
    global returnto
    username = inp
    returnto = input.chan
    conn.msg("*status","traffic")

@hook.event("PRIVMSG")
def on_privmsg(inp, input=None, conn=None):
    if input.nick == "*status":
        if username in inp[1]:
            conn.msg(returnto," Username  In       Out      Total   ")
            conn.msg(returnto,inp[1].replace("|",""))


@hook.singlethread
@hook.command
def test(inp, input=None, say=None):
    for i in range(5):
        if input.chan == "#test":
            say(inp+str(time.time()))
            time.sleep(1)
