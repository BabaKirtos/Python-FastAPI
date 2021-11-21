from operator import pos
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange

# test comment

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

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

@app.get("/posts")
async def get_posts():
    return {"data" : my_posts}

@app.post("/posts", status_code= status.HTTP_201_CREATED)
async def posts(post: Post):
    post_dict = post.dict()
    post_dict["id"] = randrange(0, 10000)
    print(post_dict)
    my_posts.append(post_dict)
    return {"new_payload" : post_dict}

@app.get("/posts/{id}")
async def get_posts(id: int, response: Response):
    post = find_posts(id) 
    if post == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail= f"Post with id: {id}, was not found!")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"Post with id: {id}, was not found!"}
    return {"post details": post}

@app.delete("/posts/{id}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    i = find_index_posts(id)
    if i == None: 
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail= f"Post with id: {id}, was not found!")
    my_posts.pop(i)
    return Response(status_code= status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
async def update_posts(id: int, post: Post):
    print(post)
    i = find_index_posts(id)
    if i == None: 
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail= f"Post with id: {id}, was not found!")
    post_dict = post.dict()
    post_dict["id"] = id
    my_posts[i] = post_dict
    return {"data": post_dict}
