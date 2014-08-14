# -- coding: utf8 --
from util import hook, timesince
import time, commands, re, random, base64

users = []
channels = {}

@hook.event("PING")
@hook.event("PONG")
def test(inp,bot=None,conn=None,input=None):
    bot.save

@hook.command
def ignore(inp,bot=None,input=None,db=None):
    if getPerms(input,db) == 101:
        if inp.lower() not in bot.config["ignored"]:
            bot.config["ignored"].append(inp.lower())
            return "Ignoring %s"%inp
        else:
            bot.config["ignored"].remove(inp.lower())
            return "Unignored %s"%inp

@hook.command
def ignorelist(inp,bot=None,input=None,db=None):
    if getPerms(input,db) == 101:
        return "; ".join(bot.config["ignored"])

@hook.command
def ignorecommand(inp,bot=None,input=None,db=None):
    if getPerms(input,db) == 101:
        if " " in inp:
            disabledcmds = []
            enabledcmds = []
            for cmd in inp.split(" "):
                if cmd.lower() not in bot.config["disabled_commands"]:
                    bot.config["disabled_commands"].append(cmd.lower())
                    disabledcmds.append(cmd)
                else:
                    bot.config["disabled_commands"].remove(cmd.lower())
                    enabledcmds.append(cmd)
            if not disabledcmds: disabledcmds.append("None")
            if not enabledcmds: enabledcmds.append("None")
            return "\00304Disabled\003: "+", ".join(disabledcmds)+"; \00309Enabled\003: "+", ".join(enabledcmds)
        if inp:
            if inp.lower() not in bot.config["disabled_commands"]:
                bot.config["disabled_commands"].append(inp.lower())
                return "Disabled %s"%inp
            else:
                bot.config["disabled_commands"].remove(inp.lower())
                return "Enabled %s"%inp
        else:
            return "Disabled commands: "+", ".join(bot.config["disabled_commands"])
"""
@hook.event("PRIVMSG")
def privmsg_debug(inp,input=None,conn=None,bot=None):
    if input.nick == input.chan: input.chan = "PM"
    if conn.server == "b0rked.ducky.ws" and inp[1][0:2] == "~~" and len(inp[1]) > 2:
        conn.cmd("PRIVMSG #services :-\00306%s\003@%s/\00312%s\003 used command: %s"%(input.nick,input.host,input.chan,inp[1]))
    elif conn.server == "freenode.ducky.ws" and inp[1][0:2] == "~~" and len(inp[1]) > 2:
        conn.cmd("PRIVMSG @##cup-bot :-\00306%s\003@%s/\00312%s\003 used command: %s"%(input.nick,input.host,input.chan,inp[1]))
    elif conn.server == "opera.ducky.ws" and inp[1][0:2] == "~~" and len(inp[1]) > 2:
        conn.cmd("PRIVMSG &#here :-\00306%s\003@%s/\00312%s\003 used command: %s"%(input.nick,input.host,input.chan,inp[1]))
"""
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

@hook.command("sh")
def runshell(inp, input=None, say=None, db=None, notice=None, conn=None):
    "runshell/sh <code> -- runs code in a shell. Needs 101 permission"
    if getPerms(input,db) == 101:
        status, output = commands.getstatusoutput(inp.encode("utf8","ignore"))
        if output:
            output = output.split("\n")
            if len(output) == 1 and len(output[0]) <= 100:
                say(output[0].decode('utf8','ignore'))
            elif len(output) == 1 and len(output[0]) >= 101:
                fname = "/srv/http/nathan.uk.to/sh/"+str(base64.b64encode(str(int(time.time()))).strip("="))+".txt"
                f = open(fname,"w")
                f.write("Output of `%s`\n------------------------------------------\n\n"%inp.encode("utf8","ignore"))
                f.write(output[0].decode('utf8','ignore')+"\n")
                f.close()
                return "http://were.up.all.night.to.get.ducky.ws"+fname.replace("/srv/http/nathan.uk.to","")
            elif len(output) <= 4:
                for line in output:
                     say(line.decode('utf8','ignore'))
            else:
                fname = "/srv/http/nathan.uk.to/sh/"+str(base64.b64encode(str(int(time.time()))).strip("="))+".txt"
                f = open(fname,"w")
                f.write("Output of `%s`\n------------------------------------------\n\n"%inp.encode("utf8","ignore"))
                for line in output:
                    f.write(line.decode('utf8','ignore')+"\n")
                    #notice(line.decode('utf8','ignore'))
                f.close()
                return "http://were.up.all.night.to.get.ducky.ws"+fname.replace("/srv/http/nathan.uk.to","")
        else: return status

@hook.command(autohelp=False)
def drink(inp, conn=None, say=None, input=None):
    if "cup" in inp or "cups" in inp:
        say("\001ACTION gives itself to %s\001"%input.nick)
    else:
        n = random.randint(1,10)
        if n == 1: say("\001ACTION throws water at %s\001"%input.nick)
        elif n == 2: say("\001ACTION throws water at %s\001"%input.nick)
        elif n == 3: say("\001ACTION throws a cup at %s\001"%input.nick)
        elif n == 4: say("\001ACTION throws vodka at %s\001"%input.nick)
        elif n == 5: say("\001ACTION gives %s a cup of tea\001"%input.nick)
        elif n == 6: say("\001ACTION gives %s some whisky\001"%input.nick)
        elif n == 7: say("\001ACTION gives %s an empty cup\001"%input.nick)
        elif n == 8: say("\001ACTION throws itself at %s\001"%input.nick)
        elif n == 9: say("\001ACTION throws %s a bottle of cola\001"%input.nick)
        elif n == 10: return "Sorry, i'm all out of drinks"


# >> :sunrise.overdrive.pw 352 nathan #chat Iota uga.electrocode.net kawaii.overdrive.pw Iota` H :2 This is my happy face.. 3:
@hook.command
def who(inp, conn=None):
    #commands.getoutput("rm www/test.html")
    conn.cmd("WHO %s"%inp)

@hook.event('352')
def event_352(inp, conn=None, say=None, db=None):
    me, chan, ident, host, server, nick, status, info = inp
    jtime = int(time.time())
    if nick.lower() not in users: users.append(nick.lower())
    if not channels.has_key(chan.lower()):
        channels[chan.lower()] = {}
    channels[chan.lower()][nick.lower()] = {"nick":nick,"ident":ident,"host":host,"chan":chan,"status":status,"jtime":jtime}
    output = ""
    if "G" in status: away = "yes"
    else: away = "no"
    if "@" in status: rank = "@"
    elif "+" in status: rank = "+"
    else: rank = "&nbsp;"
    if "*" in status: ircop = "yes"
    else: ircop = "no"
    #output+= """<table border="1" width="100%"><tr><td>chan</td><td>usermode</td><td>user</td><td>away</td><td>ircop</td></tr>"""
    #output+= """<tr><td>%s</td><td>%s</td><td>%s!%s@%s</td><td>%s</td><td>%s</td></tr>"""%(chan,rank,nick,ident,host,away,ircop)
    #output+= "</table>"
    #f = open("www/test.html","a+")
    #f.write(output)
    #f.close()

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
    "permissions <nick@host> <level> -- adds nick@host at level to permissions"
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
            if level > 0:
                db.execute("insert or replace into permissions(user,level,added,time) values(?,?,?,?)", (user,level,input.nick,int(time.time())))
                db.commit()
                return ("Added \002%s\002 at \002%s\002"%(user,level))
            return ("Deleted \002%s\002"%(user))
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

@hook.command
def acl(inp, input=None, conn=None, db=None):
    if inp.split()[0] == "add":
        return str(conn.server)

autoOpNicks = ["chintu","nathan","ducky","google","nathan_","ddl","dragondemonlord"]
autoOpChans = ["#","&","&torrent"]
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

