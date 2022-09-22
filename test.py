from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.j6ve73r.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

comment = list(db.comment.find({'reviewId':19},{'_id':False}))

print(comment)