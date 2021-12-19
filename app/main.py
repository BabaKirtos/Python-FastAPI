from fastapi import FastAPI, Response, status, HTTPException, Depends
import psycopg2
from  psycopg2.extras import RealDictCursor
import time
import models, schemas
from database import engine, get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind= engine)

app = FastAPI() 

while True:
    try:
        conn = psycopg2.connect(host= 'localhost', database= 'FastAPI', user= 'postgres', 
        password= 'gnashermasher', cursor_factory= RealDictCursor )
        cursor = conn.cursor()
        print('Connected to database sucessfully!')
        break
    except Exception as error:
        print('Unable to connect to Postgres')
        print('Error :', error)
        time.sleep(3)

my_posts = [
                {"title": "title of post 1", "content": "content of post 1", "id": 1},
                {"title": "Good food!", "content": "I like white pasta", "id": 2}
            ]

def find_posts(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_posts(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Test path for SQL Alchemy
@app.get("/sqlalchemy")
async def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post_Alchemy).all()
    return {"data": posts}

# Commented out SQL based code below
# @app.get("/posts")
# async def get_posts():
#     cursor.execute("""SELECT * FROM posts ;""")
#     posts = cursor.fetchall()
#     return {"data" : posts}

# Code using SQL Alchemy
@app.get("/posts")
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post_Alchemy).all()
    return {"data": posts}

# Commented out SQL based code below
# @app.post("/posts", status_code= status.HTTP_201_CREATED)
# async def posts(post: Post):
#     cursor.execute("""INSERT INTO posts (title, content, published) 
#     VALUES  (%s, %s, %s) RETURNING *  ;""",
#     (post.title, post.content, post.published)) 
#     new_post = cursor.fetchone()
#     conn.commit()
#     return {"new_payload" : new_post}

# SQL Alchemy - Create a new post code below
@app.post("/posts", status_code= status.HTTP_201_CREATED)
async def posts(post: schemas.CreatePost, db: Session = Depends(get_db)):
    # ** is used to unpack dictionary in python
    new_post = models.Post_Alchemy(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post) # acts as 'Returning' of SQL
    return {"new_payload" : new_post}

# SQL based code below
# @app.get("/posts/{id}")
# async def get_posts(id: int, response: Response):
#     cursor.execute("""SELECT * FROM posts WHERE id = %s ;""", (str(id)) )
#     id_post = cursor.fetchone()
#     if id_post == None:
#         raise HTTPException(status.HTTP_404_NOT_FOUND, 
#         detail= f"Post with id: {id}, was not found!")
#     return {"post details": id_post }

# SQL Alchemy code below
@app.get("/posts/{id}")
async def get_posts(id: int, db: Session = Depends(get_db)):
    id_post = db.query(models.Post_Alchemy).filter(models.Post_Alchemy.id == id).first()
    if id_post == None: 
        raise HTTPException(status.HTTP_404_NOT_FOUND, 
        detail= f"Post with id: {id}, was not found!")
    return {"post details": id_post }

# SQL based code below
# @app.delete("/posts/{id}", status_code= status.HTTP_204_NO_CONTENT)
# async def delete_post(id: int):
#     cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * ;""", (str(id)))
#     deleted_post = cursor.fetchone()
#     conn.commit()
#     print(deleted_post)
#     if deleted_post == None: 
#         raise HTTPException(status.HTTP_404_NOT_FOUND, 
#         detail= f"Post with id: {id}, was not found!")
#     return Response(status_code= status.HTTP_204_NO_CONTENT)

# SQL alchemy based code below
@app.delete("/posts/{id}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db)):
    post_querry = db.query(models.Post_Alchemy).filter(models.Post_Alchemy.id == id) 
    print(post_querry)
    if post_querry.first() == None: 
        raise HTTPException(status.HTTP_404_NOT_FOUND, 
        detail= f"Post with id: {id}, was not found!")
    post_querry.delete(synchronize_session= False)
    db.commit()
    return Response(status_code= status.HTTP_204_NO_CONTENT)

# SQL based code below
@app.put("/posts/{id}")
# async def update_posts(id: int, post: Post):
#     cursor.execute("""UPDATE posts SET title = %s, content = %s, 
#     published = %s WHERE id = %s RETURNING * ;""",
#     (post.title, post.content, post.published, (str(id))))
#     updated_post = cursor.fetchone()
#     conn.commit( )
#     if updated_post == None: 
#         raise HTTPException(status.HTTP_404_NOT_FOUND, 
#         detail= f"Post with id: {id}, was not found!")
#     return {"data": updated_post}

# SQL Alchemy based code below
@app.put("/posts/{id}")
async def update_posts(id: int, post: schemas.PostBase, db: Session = Depends(get_db)):
    post_querry = db.query(models.Post_Alchemy).filter(models.Post_Alchemy.id == id) 
    if post_querry.first() == None: 
        raise HTTPException(status.HTTP_404_NOT_FOUND, 
        detail= f"Post with id: {id}, was not found!")
    post_querry.update(post.dict(), synchronize_session= False)
    db.commit()
    return {"data": post_querry.first()}
