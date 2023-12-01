import uvicorn
from fastapi  import HTTPException
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from typing import Optional
from io import BytesIO
from typing import List
from pydantic import BaseModel
from pydantic import ValidationError
from dotenv import load_dotenv
from pymongo import MongoClient
import os

env_path = r'main의 env 경로'
load_dotenv()

app = FastAPI()

#cors설정 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 리액트 앱의 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#MONGO_DB_URL=os.getenv("MONGO_DB_URL")
MONGO_DB_URL = "mongodb://root:0707@172.16.210.121:27017/?authMechanism=DEFAULT/"

mongo_client=MongoClient(MONGO_DB_URL)
db = mongo_client.file

DEFAULT_THEME_IMG = "https://suhabuckettest.s3.ap-northeast-2.amazonaws.com/b038817e-8db9-11ee-aee7-1413338a0c50_image.jpg"

DEFAULT_PROFILE_IMG = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"

DEFAULT_THUMBNAIL = "https://allways-test-bucket.s3.ap-northeast-2.amazonaws.com/logo.png"

class UserByPostFeignRequest(BaseModel):
    postSeq: int
    userSeq: int

class UserByReplyFeignRequest(BaseModel):
    replySeq: int
    userSeq: int

class ThemeImgByThemeSeq(BaseModel):
    themeSeq : int

# 프로필 이미지 반환
@app.get("/api/file/profileImg/{userSeq}")
async def queryProfileImg(userSeq: int):
    # Your logic to fetch the profile image based on userSeq
    user = db.user.find_one({"userSeq": userSeq})
    if user is not None:
        profileImg = user.get("imageUrl", "")
        return {"profileImg": profileImg}
    else:
        # If user is not found, raise an HTTPException with a 404 status code
        raise HTTPException(status_code=404, detail="User not found")


# 테마 이미지 반환
@app.get("/api/file/theme/{themeSeq}")
async def queryThemeImg(themeSeq : int ):

    theme_seq = themeSeq
    theme = db.theme.find_one({"themeSeq":theme_seq})

    themeImg = theme.get("imageUrl") if theme else DEFAULT_THEME_IMG
    result_object = {"themeSeq":theme_seq,"themeImg":themeImg}

    return JSONResponse(content=result_object)
    

#썸네일 & 프로필 이미지 반환
@app.post("/api/feign/post")
async def queryImageUrlByPost(request: UserByPostFeignRequest):

    post_seq = request.postSeq
    user_seq = request.userSeq
    thumbnail = db.thumbnail.find_one({"postSeq":post_seq})
    user = db.user.find_one({"userSeq":user_seq})

    thumbImg = thumbnail.get("imageUrl") if thumbnail else DEFAULT_THUMBNAIL
    profileImg = user.get("imageUrl") if user else DEFAULT_PROFILE_IMG
    result_object = {"postSeq":post_seq,"userSeq":user_seq,"thumbImg":thumbImg,"profileImg":profileImg}

    return JSONResponse(content=result_object)


#썸네일 & 프로필 이미지 리스트 반환
@app.post("/api/feign/post/list")
async def queryImageUrlListByPost(requests: List[UserByPostFeignRequest]):
    # MongoDB에서 해당 postSeq 값을 가진 문서 조회
    result_list = []
    for request in requests:

        post_seq = request.postSeq
        user_seq = request.userSeq
        thumbnail = db.thumbnail.find_one({"postSeq":post_seq})
        user = db.user.find_one({"userSeq":user_seq})

        thumbImg = thumbnail.get("imageUrl","")
        profileImg = user.get("imageUrl","")
        result_object={"postSeq":post_seq,"userSeq":user_seq,"thumbImg":thumbImg,"profileImg":profileImg}
        result_list.append(result_object)
    #10개의 리스트 반환
    return JSONResponse(content=result_list)


#댓글 프로필 이미지 리스트 반환
@app.post("/api/feign/reply/list")
async def queryImageUrlListByReply(requests: List[UserByReplyFeignRequest]):
    result_list = []
    for request in requests:

        reply_seq = request.replySeq
        user_seq = request.userSeq
        user = db.user.find_one({"userSeq":user_seq})

        profileImg = user.get("imageUrl","")
        result_object={"replySeq":reply_seq, "userSeq":user_seq, "profileImg":profileImg}
        result_list.append(result_object)

    return JSONResponse(content=result_list)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
