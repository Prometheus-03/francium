import motor.motor_asyncio as amotor
import asyncio
url = "mongodb+srv://botuser:9K4Am7njeSIesMLQ@cluster0.o0mhj.gcp.mongodb.net/Francium?retryWrites=true&w=majority"
class DB:
    def __init__(self,db):
        self.client\
            =amotor.AsyncIOMotorClient(url)
        self.db=self.client[db]
        self.collections=[]
        self.collection=""
    async def add_collection(self,name:str):
        self.collections+=[name]
        self.collections=list(set(self.collections))
        self.collection=name
        if name not in (await self.db.list_collection_names()):
            await self.db.create_collection(name=name)
    async def remove_collection(self,name:str):
        self.collections.remove(name)
        await self.db.drop_collection(name)
    def set_collection(self,name:str):
        self.collection=name
    async def insert(self,**kwargs):
        await self.db[self.collection].insert_one(kwargs)
    async def insert_many(self,*items):
        for i in items:
            await self.insert(**i)
    async def delete(self,**kwargs):
        await self.db[self.collection].delete_many(kwargs)
    async def find(self,length=1000,**kwargs):
        cursor=self.db[self.collection].find(kwargs)
        res=[]
        for doc in await cursor.to_list(length=length):
            doc.setdefault("")
            res.append(doc)
        return res
    async def insertnorepeat(self,**kwargs):
        if not (await self.find(**kwargs)):
            await self.insert(**kwargs)
    async def update(self,objid,**kwargs):
        await self.db[self.collection].update_one({"_id":objid},{"$set":kwargs})
    async def print_db(self):
        res=[]
        for i in (await self.find()):
            temp=[]
            for x in i.keys():
                if i!="_id":temp+=[x+":"+str(i[x])]
            res+=[",".join(temp)]
        return "\n".join(res)
"""
async def main():
    db=DB("users")
    await db.add_collection("currency")
    await db.insert(name="Test",content="woop")
    await db.insert_many({"name":"lol","content":"testing"},{"name":"lol","content":"testing"})
    #await db.delete()
    m=await db.print_db()
    print(m)
if __name__=="__main__":
    asyncio.get_event_loop().run_until_complete(main())
"""