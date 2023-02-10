from db.attribute import col

class Person:
    def __init__(self,personalcode,name,info):
        self.personalcode = personalcode
        self.name = name
        self.info = {}
        for i,x in enumerate(info):
            self.info[col['PERSONALRECORDCol'][i]] = x