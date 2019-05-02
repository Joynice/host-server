#主动式系统服务指纹识别Api开发文档
___
##介绍
现阶段主要实现了任务下发、查询、更新、删除功能，更多功能继续增加。以下各个API的调用需要验证Secret Key。

###下发任务
```text
 url : /v1/task/
 method: post
```
传入参数：


 |名称|类型|是否必须|描述|
|:----:|:----:|:----:|:---:|
|url|String|Y|扫描任务url
|cycle|Inter|Y|扫描周期(1,3,7)
|number|Inter|N|默认为1(1：立即执行)
|secret_key|String|Y|身份验证

返回参数

 |名称|类型|描述|
|:----:|:----:|:---:|
|code|Inter|状态码
|data|Json|返回数据
|result_id|String|查询结果需要ID
|task_id|String|成功下发后，任务ID
|message|String|返回消息

#查询结果
```text
url : /v1/result/
method: get
```
传入参数

|名称|类型|是否必须|描述
|:----:|:----:|:----:|:----|
|result_id|String|Y|查询ID
|secret_key|String|Y|身份验证

返回参数

|名称|类型|描述
|:----:|:----:|:----:|
|code|Inter|状态码
|data|Json|返回数据
|result_id|String|查询结果需要ID
|task_id|String|成功下发后，任务ID
|result|String|返回结果
message|String|返回消息

##更新任务
```text
url : /v1/task/
method: put
```

传入参数

|名称|类型|是否必须|描述
|:----:|:----:|:----:|:----|
task_id|String|Y|需要更新任务ID
|cycle|Inter|N|扫描周期(1,3,7)
|number|Inter|N|默认为1(1：立即执行)
|secret_key|String|Y|身份验证

返回参数

|名称|类型|描述
|:---:|:---:|:---:|
|code|Inter|状态码|
|message|String|返回消息

##删除任务
```text
url : /v1/task/
method: delete
```

传入参数

|名称|类型|是否必须|描述
|:---:|:---:|:---:|:---:
task_id|String|Y|需要输出任务ID
|secret_key|String|Y|身份验证

返回参数

|名称|类型|描述
|:---:|:---:|:---:|
|code|Inter|状态码
|message|String|返回消息

##查询任务状态
```text
url : /v1/task/
method : get
```
传入参数

|名称|类型|是否必须|描述
|:----:|:---:|:---:|:---:|
task_id|String|Y|查询任务ID
|secret_key|String|Y|身份验证

返回参数

|名称|类型|描述|
|:---:|:---:|:---:|
|code|Inter|状态码|
|data|Json|返回数据
task_id|String|任务ID
|url|String|任务url
|cycle|Inter|周期
|number|Inter|扫描次数
|status|String|任务状态
|result_id|String|结果ID
|message|String|返回消息

##状态码

|名称|描述|
|:----:|:---|
|200|成功
|400|传参错误
|401|身份验证失败
|405|请求方法不支持
|500|服务器内部错误