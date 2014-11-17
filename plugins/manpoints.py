from util import hook

def getManpoints(user,db):
    points = db.execute("select points from manpoints where nick = ?",(user.lower(),)).fetchone()
    if points:
        return int(points[0])
    else:
        return 0

@hook.regex("(.*)\s([-+])(\d+)\sman\s?points")
def manpoints(inp, input=None, db=None):
    nick = inp.group(1).replace(":","").replace(",","").replace(" ","")
    points = inp.group(3)  
    db.execute("create table if not exists manpoints(nick primary key, points)")
    db.commit()
    try:
        mp = int(points)
    except:
        return "points must be a number"
    if mp >= 1 and mp <= 5000:
        if input.nick.lower() == nick.lower():
            mp = getManpoints(input.nick.lower(),db)-1000
            db.execute("insert or replace into manpoints(nick,points) values(?,?)",(input.nick.lower(),mp))
            db.commit()
            return "You cannot give yourself manpoints. -1000 manpoints."
        else:
            if inp.group(2) == "+":
                mp = getManpoints(nick,db)+mp
            elif inp.group(2) == "-":
                mp = getManpoints(nick,db)-mp
            db.execute("insert or replace into manpoints(nick,points) values(?,?)",(nick.lower(),mp))
            db.commit()
            return "{} now has {} manpoints".format(nick,mp)
