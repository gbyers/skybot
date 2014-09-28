# -- coding: utf-8 --
import re, urllib, HTMLParser, time

from util import hook, http

relaychans = {"from":[],"to":None}
ignoreNicks = []

trusted = [
    "gateway/web/b0rked.me/ip.127.0.0.69",
    "botters/doge",
    "dukdukd.uk",
    "-",
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
    "relay <channel> -- starts relay between active channel and <channel>"
    if input.host in trusted:
        if inp:
            if inp[0] == "#" or inp[0] == "&":
                relaychans["to"] = input.chan
                relaychans["from"] = inp
                say("Relay started")
            elif inp == "stop":
                relaychans["from"] = []
                relaychans["to"] = None
                say("Relay stopped")
        else:
            if relaychans["from"] is not None and relaychans["to"] is not None:
                rchans = "%s and %s"%(relaychans["from"],relaychans["to"])
                return ("Relay already running between %s"%rchans)
            else:
                return ("No relay running")

formats = {'PRIVMSG': '[%(chan)s] <-%(nick)s> %(msg)s',
    'PART': '[%(chan)s] -%(nick)s [%(user)s@%(host)s] has left',
    'JOIN': '[%(param0)s] -%(nick)s [%(user)s@%(host)s] has joined',
    'MODE': '[%(chan)s] -%(nick)s set modes %(param_tail)s',
    'KICK': '[%(chan)s] -%(param1)s was kicked by -%(nick)s [%(msg)s]',
    'TOPIC': '[%(chan)s] -%(nick)s changed the topic to: %(msg)s',
    'QUIT': '%(nick)s has quit [%(msg)s]',
    'PING': '',
    'NOTICE': '',
    'NICK': '%(nick)s is now known as %(msg)s'
}

ctcp_formats = {'ACTION': '<%(chan)s/-%(nick)s> * %(nick)s %(ctcpmsg)s'}

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
        input.msg = u'%s'%input.msg
        beau = beautify(input)
        if beau == '':
            return
        if input.chan.lower() == relaychans["from"]:
            conn.cmd(u'PRIVMSG %s :%s'%(relaychans["to"],beau))
        elif input.chan.lower() == relaychans["to"]:
            conn.cmd(u'PRIVMSG %s :%s'%(relaychans["from"],beau))
