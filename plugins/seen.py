import time

from util import hook, timesince


def db_init(db):
    "check to see that our db has the the seen table and return a connection."
    db.execute("create table if not exists seen(name, time, quote, chan, event, primary key(name, chan))")
    db.commit()

def add_to_database(db,input,event):
    time.sleep(1)
    db_init(db)
    db.execute("delete from seen where name = (?) and chan = (?)",(input.nick,input.chan))
    db.execute("insert or replace into seen(name, time, quote, chan, event) values(?,?,?,?,?)", (input.nick, time.time(), input.msg, input.chan, event))
    db.commit()

@hook.event('PRIVMSG', ignorebots=False)
def seenprivmsg(paraml, input=None, db=None, bot=None, say=None):
    add_to_database(db,input,"privmsg")

@hook.event('JOIN', ignorebots=False)
def seenjoin(paraml, input=None, db=None, bot=None, say=None):
    add_to_database(db,input,"join")

@hook.event('PART', ignorebots=False)
def seenpart(paraml, input=None, db=None, bot=None, say=None):
    add_to_database(db,input,"part")

@hook.event('QUIT', ignorebots=False)
def seenquit(paraml, input=None, db=None, bot=None, say=None):
    add_to_database(db,input,"quit")

@hook.event('KICK', ignorebots=False)
def seenkick(paraml, input=None, db=None, bot=None, say=None):
    add_to_database(db,input,"kick")

@hook.command
def seen(inp, nick='', chan='', db=None, input=None):
    "seen <nick> -- Tell when a nickname was last on active in irc"

    if input.conn.nick == inp:
        return "You need to get your eyes checked."
    inp = inp.split(" ")[0]
    db_init(db)
    last_seen = db.execute("select name, time, quote, chan, event from seen where name like (?) order by time desc", (inp.replace("*","%"),)).fetchone()

    if last_seen:
        reltime = timesince.timesince(last_seen[1])
        if last_seen[0] != inp.lower():  # for glob matching
            inp = last_seen[0]
        if last_seen[4] == "privmsg":
            if last_seen[2][0:1]=="\x01":
                return '%s was last seen %s ago in %s: *%s %s*' % (last_seen[0], reltime, last_seen[3], inp, last_seen[2][8:-1])
            else:
                return '%s was last seen %s ago in %s saying: %s' % (last_seen[0], reltime, last_seen[3], last_seen[2])
        if last_seen[4] == "join":
            return '%s was last seen %s ago joining %s' % (last_seen[0], reltime, last_seen[3])
        if last_seen[4] == "part":
            return '%s was last seen %s ago parting %s' % (last_seen[0], reltime, last_seen[3])
        if last_seen[4] == "quit":
            return '%s was last seen %s ago quitting (%s)' % (last_seen[0], reltime, last_seen[2])
        if last_seen[4] == "kick":
            return '%s was last seen %s ago getting kicked from %s' % (last_seen[0], reltime, last_seen[3])
    else:
        return "I've never seen %s" % inp

@hook.command(autohelp=False)
def active(inp, db=None, notice=None, input=None, say=None):
    db_init(db)
    if not inp:
        count = db.execute("select name, time, event from seen where time > (?) and chan = (?)",(time.time()-1800,input.chan.lower(),)).fetchall()
        chan = input.chan
    else:
        if inp[0] == "#":
            count = db.execute("select name, time, event from seen where time > (?) and chan = (?)",(time.time()-1800,inp.lower(),)).fetchall()
            chan = inp.lower()
        else:
            return "Not a channel, did you mean #%s?"%inp
    if len(count) == 0:
        return "I am not in that channel"
    if len(count) == 1: c = "%s user"%len(count)
    else: c = "%s users"%len(count)
    users = []
    for user in count:
        if user[2] == "join": t = "joined"
        elif user[2] == "part": t = "parted"
        elif user[2] == "quit": t = "quitted"
        elif user[2] == "kick": t = "kicked"
        elif user[2] == "privmsg": t = "spoke"
        else: t = "n/a"
        users.append("%s (%s)"%(user[0],t))
    say("%s: %s active in %s in the last 30 minutes."%(input.nick,c,chan))
    if users:
        notice("Active nicks: "+", ".join(users))
