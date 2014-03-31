# -- coding: utf-8 --
from util import hook
import re, time

@hook.regex('^s\/(.*?)\/(.*?)\/')
def sed(inp, db=None, say=None):
    if inp.group(1).startswith("^"): search = inp.group(1)[1:]
    else: search = inp.group(1)
    m = db.execute("select nick, text from sed where text like (?) order by time desc", ("%"+search+"%",)).fetchone()
    if m:
        nick = m[0].split(".")[0]
        out = "<%s> %s"%(nick,re.sub(search,"\002"+inp.group(2)+"\002",m[1]))
        return out

@hook.singlethread
@hook.event('PRIVMSG')
def sed_save(inp,input=None,conn=None,db=None):
    db.execute("create table if not exists sed(nick, text, time)")
    nick = input.nick+"."+str(int(time.time()))
    time.sleep(1)
    db.execute("insert into sed(nick, text, time) values (?,?,?)", (nick, inp[1], int(time.time())))
    db.commit()
