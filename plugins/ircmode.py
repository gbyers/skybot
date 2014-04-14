# -- coding: utf8 --
from util import hook, timesince
import time, commands, re, random, base64

users = []
channels = {}

def getPerms(input,db):
    db.execute("create table if not exists permissions (user,level,added,time)")
    db.commit()
    #return 101
    #user = input.user+"@"+input.host
    user = "%@"+input.host
    data = db.execute("select user,level from permissions where user LIKE (?)",(user,)).fetchone()
    if data:
        return int(data[1])
    else:
        return 0

@hook.command
def permlist(inp, input=None, db=None):
    if getPerms(input,db) == 101:
        l = db.execute("select user,level from permissions where user like (?)",(inp.replace("*","%"),)).fetchall()
        h = []
        if l:
            for _h in l:
                h.append(_h[0]+": "+str(_h[1]))
            return ", ".join(h)
        else:
            return "No matches"

@hook.command
def say(inp, input=None, db=None, conn=None):
    if getPerms(input,db) >= 5:
        f = {
            "nick":     input.nick,
            "me":       conn.nick,
            "server":   conn.server,
            "date":     commands.getoutput("date"),
            "uptime":   commands.getoutput("uptime"),
            "ident":    input.user,
            "host":     input.host,
            "fullhost": input.prefix[1:],
            "channel":  input.chan,
        }
        out = inp.encode("utf8","ignore").format(**f)
        conn.msg(input.chan,out.decode("utf8","ignore"))

@hook.command(autohelp=False)
def getop(inp, input=None, conn=None, db=None):
    "getop -- gets op in channel"
    if getPerms(input,db) == 101:
        conn.cmd("MODE %s +o %s"%(input.chan,conn.nick))
        conn.cmd("PRIVMSG ChanServ :OP %s"%input.chan)

@hook.singlethread
@hook.command("sh")
def runshell(inp, input=None, say=None, db=None, notice=None, conn=None):
    "runshell/sh <code> -- runs code in a shell. Needs 101 permission"
    if getPerms(input,db) == 101:
        if "sudo" in inp: conn.cmd("PRIVMSG @& :-%s using sudo command: %s"%(input.nick,inp))
        #output = commands.getoutput(inp)
        if input.nick not in ["Ducky","cups","cup","nathan","doge"]:
            inp = re.sub("^(rm|killall|kill|dd|nc|shred|pkill|cat config)\s?","echo ",inp)
        status, output = commands.getstatusoutput(inp.encode("utf8","ignore"))
        if output:
            output = output.split("\n")
            if len(output) <= 4:
                for line in output:
                     say(line.decode('utf8','ignore'))
            else:
                fname = "/srv/http/nathan.uk.to/sh/"+str(base64.b64encode(str(int(time.time()))).strip("="))+".txt"
                f = open(fname,"w")
                f.write("Output of %s\n------------------------------------------\n\n"%inp.encode("utf8","ignore"))
                for line in output:
                    f.write(line.decode('utf8','ignore')+"\n")
                    #notice(line.decode('utf8','ignore'))
                f.close()
                return "http://"+fname.replace("/srv/http/","")
        else: return status

@hook.command(autohelp=False)
def drink(inp, conn=None, say=None, input=None):
    if "cup" in inp or "cups" in inp:
        say("\001ACTION give %s a cup of water\001"%input.nick)
    else:
        say("\001ACTION throws water at %s\001"%input.nick)

@hook.event('352')
def event_352(inp, conn=None, say=None, db=None):
    me, chan, ident, host, server, nick, status, info = inp
    jtime = int(time.time())
    if nick.lower() not in users: users.append(nick.lower())
    if not channels.has_key(chan.lower()):
        channels[chan.lower()] = {}
    channels[chan.lower()][nick.lower()] = {"nick":nick,"ident":ident,"host":host,"chan":chan,"status":status,"jtime":jtime}

@hook.command
def checkban(inp, input=None, notice=None, db=None):
    "checkban <nick!ident@host> -- checks how many people will be banned in current channel"
    if getPerms(input,db) >= 30:
        c = 0
        willbeaffected = []
        for nick in channels[input.chan.lower()]:
            fullhost = "%s!%s@%s"%(channels[input.chan.lower()][nick]["nick"],channels[input.chan.lower()][nick]["ident"],channels[input.chan.lower()][nick]["host"])
            m =  re.match(inp.replace("*","(.*?)"),fullhost)
            if m:
                c=c+1
                willbeaffected.append(channels[input.chan.lower()][nick]["nick"])
        if c == 0: notice("Nobody will be affected.")
        elif c == 1:
            notice("1 user will be affected.")
            notice("; ".join(willbeaffected))
        else:
            notice("%s users will be affected."%str(c))
            notice("; ".join(willbeaffected))

@hook.command(autohelp=False)
def cycle(inp, input=None, conn=None, db=None):
    "cycle [channel] -- cycles active channel or channel"
    if getPerms(input,db) >= 50:
        if inp:
                conn.cmd("PART %s"%inp)
                conn.cmd("JOIN %s"%inp)
        else:
            conn.cmd("PART %s"%input.chan)
            conn.cmd("JOIN %s"%input.chan)

@hook.command
def raw(inp, conn=None, input=None, db=None):
    if getPerms(input,db) == 101:
        f = {
            "nick":     input.nick,
            "me":       conn.nick,
            "server":   conn.server,
            "date":     commands.getoutput("date"),
            "uptime":   commands.getoutput("uptime"),
            "ident":    input.user,
            "host":     input.host,
            "fullhost": input.prefix[1:],
            "channel":  input.chan,
        }
        out = inp.format(**f)
        conn.cmd(out)

@hook.command
def action(inp, conn=None, input=None, db=None):
    if getPerms(input,db) >= 10:
        conn.cmd("PRIVMSG %s :\001ACTION %s\001"%(input.chan,inp))

@hook.command("perm")
@hook.command
def permissions(inp, input=None, db=None):
    "permissions <nick@host> [level] -- adds nick@host at level to permissions"
    if inp.count(" ") == 1 and getPerms(input,db) == 101:
        user = inp.split(" ")[0]
        level = inp.split(" ")[1]
        try:
            level = int(inp.split(" ")[1])
        except:
            return ("level is not a number")
        if "@" in user:
            db.execute("delete from permissions where user == (?)", (user,))
            db.commit()
            db.execute("insert or replace into permissions(user,level,added,time) values(?,?,?,?)", (user,level,input.nick,int(time.time())))
            db.commit()
            return ("Added \002%s\002 at \002%s\002"%(user,level))
        else:
            return ("must be in format of nick@host")
    elif inp.count(" ") == 0 and getPerms(input,db) >= 50:
        perm = db.execute("select user, level, added, time from permissions where user=(?)", (inp,)).fetchone()
        if perm:
            return ("\002%s\002 has \002%s\002 access and was added by \002%s\002 %s ago"%(perm[0],perm[1],perm[2],timesince.timesince(perm[3])))

@hook.command
def mode(inp, input=None, conn=None, say=None, db=None):
    "mode <channel/nick> <modes> -- sets modes on channel or self"
    if getPerms(input,db) >= 60:
        if inp: conn.cmd("MODE %s"%(inp))

@hook.command(autohelp=False)
def op(inp, input=None, conn=None, say=None, db=None):
    "op [nick] -- gives op to nick on active channel or self"
    if getPerms(input,db) >= 40:
        if inp:
            conn.cmd("MODE %s +oooo %s"%(input.chan,inp))
        else:
            conn.cmd("MODE %s +o %s"%(input.chan,input.nick))

@hook.command(autohelp=False)
def deop(inp, input=None, conn=None, db=None):
    "deop [nick] -- takes op from nick on active channel or self"
    if getPerms(input,db) >= 40:
        if inp:
            conn.cmd("MODE %s -oooo %s"%(input.chan,inp))
        else:
            conn.cmd("MODE %s -o %s"%(input.chan,input.nick))

@hook.command(autohelp=False)
def voice(inp, input=None, conn=None, say=None, db=None):
    "voice [nick] -- gives voice to nick on active channel or self"
    if getPerms(input,db) >= 20:
        if inp:
            conn.cmd("MODE %s +vvvv %s"%(input.chan,inp))
        else:
            conn.cmd("MODE %s +v %s"%(input.chan,input.nick))

@hook.command(autohelp=False)
def devoice(inp, input=None, conn=None, say=None, db=None):
    "devoice [nick] -- takes voice to nick on active channel or self"
    if getPerms(input,db) >= 20:
        if inp:
            conn.cmd("MODE %s -vvvv %s"%(input.chan,inp))
        else:
            conn.cmd("MODE %s -v %s"%(input.chan,input.nick))

@hook.event("KICK")
def _kick(inp, input=None, conn=None):
    if inp[1] in ["cups","cup","c[_]"]:
        time.sleep(1)
        conn.cmd("REMOVE %s %s :Don't kick any cups"%(input.chan,input.nick))

@hook.command("k",autohelp=False)
@hook.command(autohelp=False)
def kick(inp, conn=None, input=None, db=None):
    "kick <nick> [reason] -- kicks nick with a reason from the current channel"
    if getPerms(input,db) >= 50:
        if inp:
            if inp.count(" ") != 0:
                reason = inp.split(" ",1)[1]
            else:
                reason = ""
            if "," in inp.split(" ")[0]:
                u = inp.split(" ")[0].split(",")
                for user in u: conn.cmd("KICK %s %s :%s"%(input.chan,user,reason))
            else:
                conn.cmd("KICK %s %s :%s"%(input.chan,inp.split(" ")[0],reason))

@hook.command
def mute(inp, conn=None, input=None, db=None):
    "mute <user> -- quiets nick in current channel"
    if inp.count(" ") >= 1:
        user = inp.split(" ")[0]
    else:
        user = inp
    if user.lower() in users and getPerms(input,db) >= 50:
        if channels[input.chan.lower()].has_key(user.lower()):
            mask = "*!"+channels[input.chan.lower()][user.lower()]["ident"]+"@"+channels[input.chan.lower()][user.lower()]["host"]
            conn.send("MODE %s +b ~q:%s"%(input.chan,mask))
        else:
            conn.send("MODE %s +b ~q:%s"%(input.chan,user))
    elif getPerms(input,db) >= 50:
        conn.send("MODE %s +b ~q:%s"%(input.chan,user))

@hook.command
def unmute(inp, conn=None, input=None, db=None):
    "unmute <user> -- unquiets nick in current channel"
    if inp.count(" ") >= 1:
        user = inp.split(" ")[0]
    else:
        user = inp
    if user.lower() in users and getPerms(input,db) >= 50:
        if channels[input.chan.lower()].has_key(user.lower()):
            mask = "*!"+channels[input.chan.lower()][user.lower()]["ident"]+"@"+channels[input.chan.lower()][user.lower()]["host"]
            conn.send("MODE %s -b ~q:%s"%(input.chan,mask))
        else:
            conn.send("MODE %s -b ~q:%s"%(input.chan,user))
    elif getPerms(input,db) >= 50:
        conn.send("MODE %s -b ~q:%s"%(input.chan,user))

@hook.command
def quiet(inp, conn=None, input=None, db=None):
    "mute <user> -- quiets nick in current channel"
    if inp.count(" ") >= 1:
        user = inp.split(" ")[0]
    else:
        user = inp
    if user.lower() in users and getPerms(input,db) >= 50:
        if channels[input.chan.lower()].has_key(user.lower()):
            mask = "*!"+channels[input.chan.lower()][user.lower()]["ident"]+"@"+channels[input.chan.lower()][user.lower()]["host"]
            conn.send("MODE %s +q %s"%(input.chan,mask))
        else:
            conn.send("MODE %s +q %s"%(input.chan,user))
    elif getPerms(input,db) >= 50:
        conn.send("MODE %s +q %s"%(input.chan,user))

@hook.command
def unquiet(inp, conn=None, input=None, db=None):
    "mute <user> -- unquiets nick in current channel"
    if inp.count(" ") >= 1:
        user = inp.split(" ")[0]
    else:
        user = inp
    if user.lower() in users and getPerms(input,db) >= 50:
        if channels[input.chan.lower()].has_key(user.lower()):
            mask = "*!"+channels[input.chan.lower()][user.lower()]["ident"]+"@"+channels[input.chan.lower()][user.lower()]["host"]
            conn.send("MODE %s -q %s"%(input.chan,mask))
        else:
            conn.send("MODE %s -q %s"%(input.chan,user))
    elif getPerms(input,db) >= 50:
        conn.send("MODE %s -q %s"%(input.chan,user))

autoOpNicks = ["chintu","nathan","ducky","google","nathan_"]
autoOpChans = ["#","&fuxi"]
@hook.event('JOIN')
def doJoin(inp, input=None, conn=None):
    conn.cmd("WHO %s"%input.chan)
    if input.nick.lower() in autoOpNicks and input.chan.lower() in autoOpChans:
        conn.cmd("MODE %s +o %s"%(input.chan,input.nick))

@hook.command
def ban(inp, conn=None, input=None, db=None):
    "ban <user/host> -- sets a ban for the user/host"
    if inp.count(" ") >= 1:
        user = inp.split(" ")[0]
    else:
        user = inp
    if user.lower() in users and getPerms(input,db) >= 50:
        if channels[input.chan.lower()].has_key(user.lower()):
            mask = "*!"+channels[input.chan.lower()][user.lower()]["ident"]+"@"+channels[input.chan.lower()][user.lower()]["host"]
            conn.send("MODE %s +b %s"%(input.chan,mask))
        else:
            conn.send("MODE %s +b %s"%(input.chan,user))
    elif getPerms(input,db) >= 50:
        conn.send("MODE %s +b %s"%(input.chan,user))

@hook.command
def unban(inp, conn=None, input=None, db=None):
    "unban <user/host> -- removes a ban for the user/host"
    user = inp
    if user.lower() in users and getPerms(input,db) >= 50:
        if channels[input.chan].has_key(user.lower()):
            mask = "*!"+channels[input.chan][user.lower()]["ident"]+"@"+channels[input.chan][user.lower()]["host"]
            conn.send("MODE %s -b %s"%(input.chan,mask))
        else:
            conn.send("MODE %s -b %s"%(input.chan,user))
    elif getPerms(input,db) >= 50:
        conn.send("MODE %s -b %s"%(input.chan,user))

@hook.command('kban')
@hook.command('kb')
@hook.command
def kickban(inp, conn=None, input=None, db=None):
    "kickban/kban/kb <nick> [reason] -- kicks and bans a nick from the channel"
    ban(inp,conn,input,db)
    kick(inp,conn,input,db)

@hook.command
def remove(inp, input=None, conn=None, db=None):
    if getPerms(input,db) >= 50:
        if inp.count(" ") >= 1:
            nick = inp.split(" ")[0]
            reason = inp.split(" ",1)[1]
        else:
            nick = inp
            reason = input.nick
        conn.send("REMOVE %s %s :%s"%(input.chan,nick,reason))

