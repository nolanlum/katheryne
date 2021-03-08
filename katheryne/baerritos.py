def constant(f):
    def fset(self, value):
        raise TypeError
    def fget(self):
        return f()
    return property(fget, fset)

class BaerritoConstants(object):
    @constant
    def BAERRITOS_GUILD_ID():
        return 689238357670232083

    @constant
    def BAERRITOS_GENSHIN_ACCOUNTABILITY_22():
        return (148954595350151168, 325944609463205888)

    @constant
    def BAERRITOS_GENSHIN_ACCOUNTABILITY_25():
        return (417473397769895951, )

    @constant
    def BAERRITOS_GENSHIN_CHANNELS():
        return {780579621040422932, 698338845502078987}

    @constant
    def BAERRITOS_ACCOUNTABILITY_CHANNEL():
        return 802399940109664296

    @constant
    def BAERRITOS_GAMES_CHANNEL():
        return 701297706148167741

    @constant
    def BAERRITOS_GENSHIN_CHECKIN_USERS():
        return [688585099112874034, ]