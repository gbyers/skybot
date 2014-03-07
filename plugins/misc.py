import re
import socket
import subprocess
import time
import os
import commands

from util import hook, http

socket.setdefaulttimeout(10)  # global setting

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
#@hook.event('KICK')
#def rejoin(paraml, conn=None):
#    if paraml[1] == conn.nick:
#        if paraml[0].lower() in conn.channels:
#            conn.join(paraml[0])


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
    notice('\x01VERSION %s %s source: %s\x01' % (ident, rev, source))

@hook.regex(r'^\x01PING\s(.*)\x01$')
def ping(inp, notice=None):
    reply = inp.group(1)
    notice('\x01PING %s\x01' % reply)


@hook.command(autohelp=None)
def getinfo(inp, say=None, input=None):
    "getinfo -- returns PID, Threads and Virtual Memory"
    PID = os.getpid()
    ident, rev, source = get_version()
    threads = commands.getoutput("cat /proc/%s/status | grep Threads | awk '{print $2}'"%PID)
    memory = int(commands.getoutput("cat /proc/%s/status | grep VmRSS | awk '{print $2}'"%PID))/1000
    say("Version: %s %s; PID: %s; Hostname: %s; Threads: %s; Virtual Memory: %s MB"%(ident,rev,os.getpid(),socket.gethostname(),threads,memory))

@hook.command(autohelp=None)
def update(inp, say=None):
    p = subprocess.Popen(['git', 'log', '--oneline'], stdout=subprocess.PIPE)
    stdout, _ = p.communicate()
    p.wait()
    curver = stdout.split(None, 1)[0]
    page = http.get("https://github.com/nathan0/skybot/commits/master")
    ver = re.search("""<span class="sha">(.*)<span class="octicon octicon-arrow-small-right"><\/span><\/span>""",page)
    lupd = re.search("""<a href="\/nathan0\/skybot\/commit\/(.*)" class="message" data-pjax="true" title="(.*)">(.*)<\/a>""",page)
    if ver and lupd:
        if ver.group(1)[0:7] != curver:
            say("Current: %s Newest changes: %s - %s"%(curver,lupd.group(3),lupd.group(1)[0:7]))
            p = subprocess.Popen(['git', 'pull', 'origin'], stdout=subprocess.PIPE)
            stdout, _ = p.communicate()
            p.wait()
            say("Updated")
        else:
            return "Already up-to-date."
    else:
        return "Unable to check current version."

@hook.command(autohelp=False)
def source(inp):
    return "https://github.com/nathan0/skybot"
    
