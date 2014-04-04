import time

from util import hook, timesince


def db_init(db):
    "check to see that our db has the the seen table and return a connection."
    db.execute("create table if not exists seen(name, time, quote, chan, "
                 "primary key(name, chan))")
    db.commit()


#@hook.singlethread
@hook.event('PRIVMSG', ignorebots=False)
def seeninput(paraml, input=None, db=None, bot=None, say=None):
    db_init(db)
    db.execute("insert or replace into seen(name, time, quote, chan)"
        "values(?,?,?,?)", (input.nick.lower(), time.time(), input.msg,
            input.chan))
    db.commit()

@hook.command
def seen(inp, nick='', chan='', db=None, input=None):
    "seen [nick] -- Tell when a nickname was last on active in irc"

    inp = inp.lower()

    if input.conn.nick.lower() == inp:
        # user is looking for us, being a smartass
        return "You need to get your eyes checked."

    if inp == nick.lower():
        return "Have you looked in a mirror lately?"

    db_init(db)

    #last_seen = db.execute("select name, time, quote from seen where"
    #                       " name = ? and chan = ?", (inp, chan)).fetchone()
    last_seen = db.execute("select name, time, quote, chan from seen where name like (?) order by time desc", (inp.replace("*","%"),)).fetchone()

    if last_seen:
        reltime = timesince.timesince(last_seen[1])
        if last_seen[0] != inp.lower():  # for glob matching
            inp = last_seen[0]
        if last_seen[2][0:1]=="\x01":
            return '%s was last seen %s ago in %s: *%s %s*' % \
                    (last_seen[0], reltime, last_seen[3], inp, last_seen[2][8:-1])
        else:
            return '%s was last seen %s ago in %s saying: %s' % \
                    (last_seen[0], reltime, last_seen[3], last_seen[2])
    else:
        return "I've never seen %s" % inp

