from util import hook, timesince
import time

def db_init(db):
    db.execute("create table if not exists msg (id,touser,fromuser,msg,time,read,readtime)")
    db.commit()

def getMsgCount(db,nick):
    return db.execute("select count(*) from msg where touser = (?)",(nick,)).fetchone()[0]

def sendMessage(db,id,touser,msg,fromuser,t):
    db.execute("insert into msg values (?,?,?,?,?,0,0)",(id,touser,fromuser,msg,t))
    db.commit()

def getMsgs(db,user):
    return db.execute("select * from msg where touser = (?)",(user,)).fetchall()

@hook.command
def msg(inp, input=None, db=None, notice=None, conn=None):
    db_init(db)
    m = inp.split(" ")
    n = m[0]
    m = " ".join(m[1:])
    c = getMsgCount(db,n)
    sendMessage(db,c,n,m,input.nick,time.time())
    notice("You have 1 new message. Type /msg %s ~~read to read it."%conn.nick)
    notice("Your message has been sent")

@hook.command(autohelp=False)
def read(inp, input=None, db=None, notice=None):
    db_init(db)
    m = getMsgs(db,input.nick)
    if len(m) > 0:
        if len(m) == 1: notice("You have %s new message."%len(m))
        elif len(m) > 1: notice("You have %s new messages."%len(m))
        if len(m) > 0:
            for m in m:
                string = "Sent: %s ago; From: %s;"%(timesince.timesince(m[4]),m[2])
                notice(string)
                notice(m[3])
                db.execute("delete from msg where touser = (?)",(input.nick,))
                db.commit()
    else:
        return "You have no new messages."

@hook.event("JOIN")
def onJoinMsg(inp, input=None, db=None, notice=None, conn=None):
    c = getMsgCount(db,input.nick)
    if c > 0:
        notice("You have %s new messages. Type /msg %s ~~read to read them"%(str(c),conn.nick))
