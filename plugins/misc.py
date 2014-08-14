import re
import socket
import subprocess
import time
import os
import commands
import datetime
import math

from util import hook, http, timesince

socket.setdefaulttimeout(30)

def get_version():
    p = subprocess.Popen(['git', 'log', '--oneline'], stdout=subprocess.PIPE)
    stdout, _ = p.communicate()
    p.wait()
    revnumber = len(stdout.splitlines())
    shorthash = stdout.split(None, 1)[0]
    http.ua_skybot = 'Skybot/r%d %s (https://github.com/nathan0/skybot)' \
        % (revnumber, shorthash)
    return shorthash, revnumber, "(https://github.com/nathan0/skybot)"


#autorejoin channels
@hook.event('KICK')
def rejoin(paraml, conn=None, notice=None):
    if paraml[1] == conn.nick:
        if paraml[2] != "0":
            conn.join(paraml[0])
            notice("If you want me to leave the channel, /kick %s 0"%conn.nick)

#join channels when invited
#@hook.event('INVITE')
#def invite(paraml, conn=None):
#    conn.join(paraml[-1])


@hook.event('004')
def onjoin(paraml, conn=None):
    # identify to services
    nickserv_password = conn.conf.get('nickserv_password', '')
    nickserv_name = conn.conf.get('nickserv_name', 'nickserv')
    nickserv_command = conn.conf.get('nickserv_command', 'IDENTIFY %s')
    if nickserv_password:
        conn.msg(nickserv_name, nickserv_command % nickserv_password)
        time.sleep(6)

    # set mode on self
    mode = conn.conf.get('mode')
    if mode:
        conn.cmd('MODE', [conn.nick, mode])

    # join channels
    for channel in conn.channels:
        conn.join(channel)
        time.sleep(0.5)  # don't flood JOINs

    # set user-agent
    ident, rev, source = get_version()


@hook.regex(r'^\x01VERSION\x01$')
def version(inp, notice=None):
    ident, rev, source = get_version()
    notice('\x01VERSION %s-%s source: %s\x01' % (ident, rev, source))

@hook.regex(r'^\x01PING\s(.*)\x01$')
def ping(inp, notice=None, bot=None):
    reply = inp.group(1)
    notice('\x01PING %s\x01' % reply)
    bot.save


@hook.command("gi",autohelp=False)
@hook.command(autohelp=False)
def getinfo(inp, say=None, input=None):
    "getinfo -- returns PID, Threads and Virtual Memory"
    PID = os.getpid()
    ident, rev, source = get_version()
    threads = commands.getoutput("cat /proc/%s/status | grep Threads | awk '{print $2}'"%PID)
    memory = int(commands.getoutput("cat /proc/%s/status | grep VmRSS | awk '{print $2}'"%PID))/1000
    say("Version: %s-%s; PID: %s; Hostname: %s; Threads: %s; Virtual Memory: %s MB"%(ident,rev,os.getpid(),socket.gethostname(),threads,memory))

#@hook.command(autohelp=None)
#def update(inp, say=None):
#    p = subprocess.Popen(['git', 'log', '--oneline'], stdout=subprocess.PIPE)
#    stdout, _ = p.communicate()
#    p.wait()
#    curver = stdout.split(None, 1)[0]
#    page = http.get("https://github.com/nathan0/skybot/commits/master")
#    ver = re.search("""<span class="sha">(.*)<span class="octicon octicon-arrow-small-right"><\/span><\/span>""",page)
#    lupd = re.search("""<a href="\/nathan0\/skybot\/commit\/(.*)" class="message" data-pjax="true" title="(.*)">(.*)<\/a>""",page)
#    if ver and lupd:
#        if ver.group(1)[0:7] != curver:
#            say("Current: %s Newest changes: %s - %s"%(curver,lupd.group(3),lupd.group(1)[0:7]))
#            p = subprocess.Popen(['git', 'pull', 'origin', 'master'], stdout=subprocess.PIPE)
#            stdout, _ = p.communicate()
#            p.wait()
#            say("Updated")
#        else:
#            return "Already up-to-date."
#    else:
#        return "Unable to check current version."

@hook.command(autohelp=False)
def source(inp):
    "source -- https://github.com/nathan0/skybot"
    if inp:
        return "https://github.com/nathan0/skybot/blob/master/%s"%inp
    else:
        return "https://github.com/nathan0/skybot"
    
@hook.command
def howlongtillxpisdead(inp):
    return "Windows XP has been dead for %s"%(timesince.timesince(datetime.datetime(2014, 4, 8, 0, 0)))

@hook.command
def timetotheendofallthings(inp):
    return "There is %s left till the end of all things."%(timesince.timeuntil(datetime.datetime(2023, 8, 12, 0, 0)))

@hook.command
def metrictime(inp):
    "metrictime <hours(0-23)>:<minutes(0-59)>:<seconds(0-59)> -- convert 24-hour time into metric time"
    if inp.count(":") == 2:
        hours,minutes,seconds = inp.split(":")
        try:
            hours = int(hours)
            minutes = int(minutes)
            seconds = int(seconds)
        except:
            return "That's not a time"
        if hours < 0 or hours >= 24: return "Hours must be between 0 and 23"
        if minutes < 0 or minutes >= 60: return "Minutes must be between 0 and 59"
        if seconds < 0 or seconds >= 60: return "Seconds must be between 0 and 59"
        daysecs = 3600*hours + 60*minutes + seconds
        metricsecs = daysecs * 100000 / 86400
        metrichours = math.floor(metricsecs / 10000)
        metricsecs = metricsecs - 10000 * metrichours
        metricminutes = math.floor(metricsecs / 100)
        metricsecs = math.floor(metricsecs - 100 * metricminutes)
        if metrichours <= 9: metrichours = "0"+str(metrichours)
        if metricminutes <= 9: metricminutes = "0"+str(metricminutes)
        if metricsecs <= 9: metricsecs = "0"+str(metricsecs)
        metrichours = str(metrichours).split(".")[0]
        metricminutes = str(metricminutes).split(".")[0]
        metricsecs = str(metricsecs).split(".")[0]
        metric = metrichours+":"+metricminutes+":"+metricsecs
        return "%s in metric: %s"%(inp,metric)
    else:
        return "Usage: metrictime <hours(0-23)>:<minutes(0-59)>:<seconds(0-59)>"

@hook.command
def list(inp, conn=None, input=None):
    conn.cmd("KICK %s %s :You suck, go away"%(input.chan,input.nick))

@hook.command("uptime",autohelp=False)
def showuptime(inp):
    "uptime -- shows how long I have been connected for"
    f = open("uptime","r")
    uptime = f.read()
    f.close()
    uptime = timesince.timesince(float(uptime))
    return "I have been online for %s"%uptime

#@hook.command
#def restart(inp, conn=None):
#    conn.cmd("QUIT :Restarting")
#    PID = os.getpid()
#    commands.getoutput("kill %s;python2 bot.py"%PID)
