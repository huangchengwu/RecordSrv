#!/bin/bash
#获取token
Token=`curl -X POST http://localhost/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'|jq ".access"|sed 's/"//g'`

#刷新token

Refresh=`curl -X POST http://localhost/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'|jq ".refresh"|sed 's/"//g'`

curl -X POST http://localhost/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$Refresh\"}"


#音频转文字
curl -X POST http://localhost/recordings/Recording/2/analyze/ \
  -H "Authorization: Bearer $Token" 





#上传录音
curl -X POST http://localhost/recordings/Recording/ \
  -H "Authorization: Bearer $Token" \
  -F "user=1" \
  -F "title=测试录音" \
  -F "audio_file=@recording-2025-07-30T13_04_47.mp4"



#获取所有录音
curl -X GET http://localhost/recordings/Recording/ \
  -H "Authorization: Bearer $Token"
#获取单个录音
  curl -X GET http://localhost/recordings/Recording/1/ \
  -H "Authorization: Bearer $Token"



#更新录音音频
curl -X PUT http://localhost/recordings/Recording/1/ \
  -H "Authorization: Bearer $Token" \
  -F "title=更新后的录音标题" \
  -F "user=1" \
  -F "audio_file=@recording-2025-07-30T13_04_47.mp4"
#修改标题
curl -X PATCH http://localhost/recordings/Recording/1/ \
  -H "Authorization: Bearer $Token" \
  -F "title=只改标题"
#删除录音
curl -X DELETE http://localhost/recordings/Recording/1/ \
  -H "Authorization: Bearer $Token"

