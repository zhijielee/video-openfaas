# 项目主体需要packages
import requests
import json

import os
import oss2
import cv2
from cv2 import VideoWriter,VideoWriter_fourcc,imread,resize 

from PIL import Image, ImageDraw, ImageFont
import numpy as np


def decode(fileName, sourceName, outFolder):
    parts = []
    vc = cv2.VideoCapture(sourceName)
    c = 1
    if vc.isOpened():
        rval = vc.read
        frame = vc.read
    else:
        rval = False
    while rval:
        rval,frame = vc.read()
        if frame is None:
            break 
        cv2.imwrite(str(outFolder) + str(fileName) +str(c)+'.jpg',frame)
        parts.append(str(outFolder) + str(fileName) +str(c)+'.jpg')
        c = c + 1
        # cv2.waitKey(1)
    # print(parts)    
    vc.release()
    return parts


def filter():
    return 0

# 水印添加
def add_waterMark(img, waterMark):
    im = Image.open(img)
    mark = Image.open(waterMark)
    factor = 0.4
    mark = mark.resize(tuple(map(lambda x : int(x * factor), mark.size)))
    layer=Image.new('RGBA', im.size)
    layer.paste(mark, (im.size[0]-mark.size[0],im.size[1]-mark.size[1]))
    out=Image.composite(layer,im,layer)
    out.save(img)

# 图片转手绘
def draw_pic(img):
#读取彩色图片并转化为np数组
    a = np.array(Image.open(img).convert('L')).astype("float")

    # 设置深度为10
    depth = 10.
    # 对数组求梯度
    grad = np.gradient(a)
    grad_x, grad_y = grad
    grad_x = grad_x * depth / 100
    grad_y = grad_y * depth / 100
    A = np.sqrt(grad_x ** 2 + grad_y ** 2 + 1.)
    uni_x = grad_x / A
    uni_y = grad_y / A
    uni_z = 1. / A

    vec_el = np.pi / 2.2 #θ角度
    vec_ez = np.pi / 4.  #α角度
    dx = np.cos(vec_el)*np.cos(vec_ez)
    dy = np.cos(vec_el)*np.sin(vec_ez)
    dz = np.sin(vec_el)

    b = 255*(dx*uni_x + dy*uni_y + dz*uni_z)
    b = b.clip(0, 255)

    im = Image.fromarray(b.astype('uint8'))
    im.save(img)


def encode(sourceName, parts, fps, size):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    VideoWriter = cv2.VideoWriter(sourceName,fourcc,fps,size)

    # imNames = os.listdir(imgRoot)
    # for im_name in range(len(imNames)):
    #     frame = cv2.imread(imgRoot + str(imNames) + '.jpg')
    #     VideoWriter.write(frame)
    for order in parts:
        frame = cv2.imread(order)
        VideoWriter.write(frame)

    VideoWriter.release


def download(auth, url, bucketName, videoName, sourceName):
    bucket = oss2.Bucket(auth, url, bucketName)
    bucket.get_object_to_file(videoName, sourceName)


# def upload(auth, url, parts, bucketName):
#     bucket = oss2.Bucket(auth, url, bucketName)
#     for order in parts:
#         bucket.put_object_from_file('img/' + order + '.jpg', 'img/' + order +'.jpg')

def upload(auth, url, bucketName, videoName):
    bucket = oss2.Bucket(auth, url, bucketName)
    bucket.put_object_from_file(videoName, videoName)



def handle(req):
# if __name__ == "__main__":
    # 参数获取
    json_req = json.loads(req)
    url = json_req["url"]
    accessKeyId = json_req["accessKeyId"]
    accessKeySecret = json_req["accessKeySecret"]
    videoBucket = json_req["videoBucket"]
    videoName = json_req["videoName"]
    filterType = json_req["filterType"]
    waterMarkImg = json_req["waterMarkImg"]

    fileName = videoName.rsplit(".",1)[0]

    auth = oss2.Auth(accessKeyId, accessKeySecret)
    imgFloder = fileName + "imgs/"
    sourceName = "video/"+ videoName
    if os.path.exists("video") == False:
        os.makedirs("video")
    
    download(auth, url, videoBucket,  videoName, sourceName)
    video = cv2.VideoCapture(sourceName)
    fps = video.get(cv2.CAP_PROP_FPS)
    video.release
    if os.path.exists(imgFloder) == False :
        os.makedirs(imgFloder)

    # return os.path.getsize(sourceName)
    parts = decode(fileName, sourceName, imgFloder)
    # upload(auth, url, videoBucket)

    img = Image.open(parts[0])
    size = img.size

    if filterType == 1:
        for order in parts:
            draw_pic(order)
    else :
        download(auth, url, videoBucket, waterMarkImg, waterMarkImg)
        for order in parts:
            add_waterMark(order, waterMarkImg)
    
    # sourceName = "video/" + fileName + ".avi"
    encode(sourceName, parts, fps, size)

    # videoName = fileName + ".avi"
    upload(auth, url, videoBucket, sourceName)
