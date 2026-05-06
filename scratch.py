import os, uuid
from sqlalchemy import create_engine
from backend.database import SessionLocal, ConversationModel, init_db

os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_GSlc6jATdE0i@ep-frosty-grass-aogi1xbi-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

init_db()

with SessionLocal() as db:
    new_conv = ConversationModel(id=str(uuid.uuid4()), title="Test", avatar_color="#000", messages=[])
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    cid = new_conv.id
    print("Created ID:", cid)
    
with SessionLocal() as db:
    c = db.query(ConversationModel).filter(ConversationModel.id == cid).first()
    if c:
        print("Found:", c.id)
    else:
        print("NOT FOUND!")
