import cx_Oracle

class Connection:
    def __init__(self):
        self.connection = None
    
    def getConnection(self,username,pword):
        print (cx_Oracle.version)
        self.connection = cx_Oracle.connect(
                        user= username,
                        password= pword,
                        dsn="29.157.144.12:19412/fcdb")
        print("Connected to database")
        return self.connection

# 分别初始化连接聚源和财汇数据库
conn = Connection().getConnection(username="findataread",pword = "Ce_Sh1.Pa2s_ordb")
conn_jy = Connection().getConnection(username="gildataread",pword = "gildataread$RFV518k")
