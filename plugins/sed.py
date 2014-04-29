# -- coding: utf-8 --
from util import hook
import re, time

@hook.regex('^s\/(.*)\/(.*)\/')
def sed(inp, db=None, say=None, input=None):
    if input.chan.lower() not in ["##powder-bots"]:
        search = inp.group(1).lstrip(".")
        if search == "": return ""
        d = db.execute("select nick, text from sed where time > (?) order by time desc",(time.time()-60,)).fetchall()
        if d:
            for m in d:
                r = re.search(search,m[1])
                if r:
                    nick = m[0]
                    msg = m[1]
                    sub = re.sub(search,inp.group(2),msg)
                    if "\001ACTION" in sub:
                            out = "* -%s %s"%(nick,sub.replace("\001ACTION ","").replace("\001",""))
                    else:
                        out = "<-%s> %s"%(nick,sub)
                    return out

@hook.event('PRIVMSG')
def sed_save(inp,input=None,conn=None,db=None):
    #db.execute("CREATE TABLE IF NOT EXISTS sed(nick, text, time, CONSTRAINT primarykey PRIMARY KEY (nick, time))")
    m = re.search("s\/(.*)\/(.*)\/?",inp[1])
    if not m:
        time.sleep(0.3)
        db.execute("insert into sed(nick, text, time) values (?,?,?)", (input.nick, inp[1], time.time()))
        db.commit()

