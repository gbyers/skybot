import re

from util import hook

@hook.command(autohelp=False)
def help(inp, bot=None, notice=None):
    "help [command] -- gives a list of commands/help for a command"
    funcs = {}
    disabled = bot.config.get('disabled_plugins', [])
    disabled_comm = bot.config.get('disabled_commands', [])
    for command, (func, args) in bot.commands.iteritems():
        fn = re.match(r'^plugins.(.+).py$', func._filename)
        if fn.group(1).lower() not in disabled:
            if command not in disabled_comm:
                if func.__doc__ is not None:
                    if func in funcs:
                        if len(funcs[func]) < len(command):
                            funcs[func] = command
                    else:
                        funcs[func] = command

    commands = dict((value, key) for key, value in funcs.iteritems())
    if not inp:
        return ('available commands: ' + ' '.join(sorted(commands)).replace(" ",", "))
        #return "A list of my commands can be found at http://nathan.pond.sx:5498/bot"
    elif inp in commands:
        if inp == "help": return "No help for you!"
        notice(commands[inp].__doc__)
    else:
        notice("No help for %s found"%inp)
