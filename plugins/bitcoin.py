from util import http, hook

"""
@hook.command(autohelp=False)
def bitcoin(inp, say=None):
    "bitcoin -- gets current exchange rate for bitcoins from mtgox"
    data = http.get_json("https://data.mtgox.com/api/2/BTCUSD/money/ticker")
    data = data['data']
    ticker = {
        'buy': data['buy']['display_short'],
        'high': data['high']['display_short'],
        'low': data['low']['display_short'],
        'vol': data['vol']['display_short'],
    }
    say("Current: \x0307%(buy)s\x0f - High: \x0307%(high)s\x0f"
        " - Low: \x0307%(low)s\x0f - Volume: %(vol)s" % ticker)
"""
@hook.command(autohelp=False)
def bitcoin(inp, say=None):
    ".bitcoin -- gets current exchange rate for bitcoins from BTC-e"
    data = http.get_json("https://btc-e.com/api/2/btc_usd/ticker")
    say("USD/BTC: \x0307{buy:.0f}\x0f - High: \x0307{high:.0f}\x0f"
            " - Low: \x0307{low:.0f}\x0f - Volume: {vol_cur:.0f}".format(**data['ticker']))
