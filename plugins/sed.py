# -- coding: utf-8 --
from util import hook
import re, time, sqlite3
"""
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
    db.execute("CREATE TABLE IF NOT EXISTS sed(nick, text, time, CONSTRAINT primarykey PRIMARY KEY (nick, time))")
    m = re.search("s\/(.*)\/(.*)\/?",inp[1])
    if not m:
        time.sleep(0.3)
        db.execute("insert into sed(nick, text, time) values (?,?,?)", (input.nick, inp[1], time.time()))
        db.commit()
        db.execute("delete from sed where time > (?)",(time.time()-65))
        db.commit()
"""
@hook.command
def sqlite(inp, input=None, db=None):
    if input.nick.lower() == "nathan":
        try:
            output = db.execute(inp).fetchall()
            db.commit()
            return str(output)
        except sqlite3.Error as e:
            return "sql error "+e.args[0]

