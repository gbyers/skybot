from util import hook, timesince
import time, commands, re

@hook.command
def add(inp, input=None, db=None):
    "add <info> -- add info about yourself"
    db.execute("create table if not exists info (nick,info,time)")
    db.commit()
    db.execute("delete from info where nick == (?)", (input.nick,))
    db.commit()
    db.execute("insert or replace into info(nick, info, time) values (?,?,?)", (input.nick, inp, int(time.time())))
    db.commit()
    return "Added info: %s"%inp

@hook.command("asl")
@hook.command
def info(inp, inpt=None, db=None):
    "info <nick> -- return info for a nick"
    db.execute("create table if not exists info (nick,info,time)")
    db.commit()
    i = db.execute("select nick,info from info where nick LIKE (?) order by time desc",(inp,)).fetchone()
    if i:
        return "%s || %s"%(i[0],i[1])
    else:
        return "No info for %s"%inp
