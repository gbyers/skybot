# -- coding: utf-8 --
import re, urllib, HTMLParser, time

from util import hook, http

@hook.event('PRIVMSG')
def pandora(paraml, input=None, say=None):
    if paraml[0] == "#botter-test" and "doge" in paraml[1].split(" ")[0]:
        x = http.get("http://pandorabots.com/pandora/talk-xml?"+urllib.urlencode({'botid':'f5d922d97e345aa1','skin':'custom_input','custid':"bot",'input':paraml[1].split(" ",1)[1]}))
        match = re.search("<that>(.*?)<\/that>", x, re.M|re.I)
        if match:
            #time.sleep(3)
            return HTMLParser.HTMLParser().unescape(match.group(1))

relaychans = {"from":[],"to":None}
ignoreNicks = []

trusted = [
    "unaffiliated/cups",
    "F86D1CB7.E7072F54.A84B1A07.IP",
    "nathan.pond.sx",
]

@hook.command
def aignore(inp, input=None, say=None, conn=None):
    "aignore <nick> -- adds nick to relay ignore list"
    if input.host in trusted:
        if inp.lower() not in ignoreNicks:
            ignoreNicks.append(inp.lower())
            say("Ignoring %s"%inp)

@hook.command
def rignore(inp, input=None, say=None):
    "rignore <nick> -- removes nick from relay ignore list"
    if input.host in trusted:
        if inp.lower() in ignoreNicks:
            ignoreNicks.remove(inp.lower())
            say("Un-Ignoring %s"%inp)

@hook.command
def rignored(inp,input=None):
    "rignored -- returns list of ignored nicks in relay"
    if input.host in trusted:
        return str(ignoreNicks)

@hook.command(autohelp=False)
def relay(inp, input=None, say=None, conn=None):
    "relay <channel> [channel2] [channel3].. -- starts relay sending messages to active channel"
    if input.host in trusted:
        if inp:
            if inp[0] == "#":
                fromtmp = inp.split(" ")
                for chan in fromtmp:
                    relaychans["from"].append(chan.lower())
                relaychans["to"] = input.chan
                say("Relay started")
            elif inp == "stop":
                relaychans["from"] = []
                relaychans["to"] = None
                say("Relay stopped")
        else:
            if relaychans["from"] is not [] and relaychans["to"] is not None:
                rchans = ", ".join(relaychans["from"])
                return ("Relay already running between %s"%rchans)
            else:
                return ("No relay running")

formats = {'PRIVMSG': '<%(chan)s/%(nick)s> %(msg)s',
    'PART': '%(nick)s [%(user)s@%(host)s] has left %(chan)s',
    'JOIN': '%(nick)s [%(user)s@%(host)s] has joined %(param0)s',
    'MODE': 'mode/%(chan)s [%(param_tail)s] by %(nick)s',
    'KICK': '%(param1)s was kicked from %(chan)s by %(nick)s [%(msg)s]',
    'TOPIC': '%(nick)s changed the topic of %(chan)s to: %(msg)s',
    'QUIT': '%(nick)s has quit [%(msg)s]',
    'PING': '',
    'NOTICE': '<%(nick)s> %(msg)s',
    'NICK': '%(nick)s is now known as %(msg)s'
}

ctcp_formats = {'ACTION': '<%(chan)s/%(nick)s> * %(nick)s %(ctcpmsg)s'}

irc_color_re = re.compile(r'(\x03(\d+,\d+|\d)|[\x0f\x02\x16\x1f])')

def beautify(input):
    format = formats.get(input.command, '%(raw)s')
    args = dict(input)

    leng = len(args['paraml'])
    for n, p in enumerate(args['paraml']):
        args['param' + str(n)] = p
        args['param_' + str(abs(n - leng))] = p

    args['param_tail'] = ' '.join(args['paraml'][1:])
    #args['msg'] = irc_color_re.sub('', args['msg'])
    if input.command == 'PRIVMSG' and input.msg.count('\x01') >= 2:
        ctcp = input.msg.split('\x01', 2)[1].split(' ', 1)
        if len(ctcp) == 1:
            ctcp += ['']
        args['ctcpcmd'], args['ctcpmsg'] = ctcp
        format = ctcp_formats.get(args['ctcpcmd'],
                '%(nick)s [%(user)s@%(host)s] requested unknown CTCP '
                '%(ctcpcmd)s from %(chan)s: %(ctcpmsg)s')

    return format % args

@hook.singlethread
@hook.event('*')
def log(paraml, input=None, bot=None, conn=None):
    if relaychans.has_key("from") and relaychans.has_key("to") and input.nick.lower() not in ignoreNicks:
        if input.chan.lower() in relaychans["from"]:
            input.msg = u'%s'%input.msg
            beau = beautify(input)
            if beau == '':
                return
            conn.cmd(u'PRIVMSG %s :%s'%(relaychans["to"],beau))
