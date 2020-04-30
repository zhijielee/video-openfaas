# 基于openfaas的视频处理

### 一、部署

```sh
faas-cli build -f video-py3.yml
faas-cli deploy -f video-py3.yml
```



### 二、使用

```json
{
    "url":"",
    "accessKeyId":"",
    "accseeKeySecret":"",
    "videoBucket":"",
    "videoName":"",
    "filterType":1代表视频转手绘，0代表水印添加(传int值),
    "waterMarkImg":""
}
```

- 用户将需处理的视频分片上传至阿里oss
- 用户提供此oss访问方式，权限，bucket及要处理的视频名称
- 用户选择视频处理方式  转手绘 或 添加水印
- 如果添加水印，提供水印图片在阿里oss的bucket的名称



### 三、设计方式

- 服务架构

  ![处理流程](https://img.alicdn.com/tfs/TB1mWfesSf2gK0jSZFPXXXsopXa-8496-4928.png)

- 处理思路调整

  - 为什么需要用户先做分片上传oss？

    单个视频文件过大，若用户直接传给serverless端，上传时间过长，将抵消掉serverless并行处理节约的大量时间。

    处理好的视频同样返回用户上传到oss的视频分片。

  - 将三次处理分别于oss进行通信和为一次通信







