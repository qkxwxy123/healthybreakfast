## 下订单 api

###接口说明

- 本接口响应都遵循以下格式

```json
{
	"status" : Int ,
	"message" : String ,
	"data" : String
}
```

status : 状态信息。接口成功响应返回200，发生服务端错误返回500

message : 消息

data : json字符串

- 接口参数中 ， 带括号[]的参数为可选参数 ， 详见各接口说明

####POST placeOrder

####参数

	{
		"code":String ,
		"location":String ,
		"getTime":String ,
		"foodId":Int ,
		"orderNum":Int
	}

####说明
code：用于换取openId

location：用户选择的地址

getTime：用户填写的送货时间

foodId：通过查询以后选择的食物传回的食物id

orderNum:订单数

####响应
```json
{
	"status":Int ,
	"message":String ,
	"data":{
		"randNum" : Int
	}
}
```
####说明
randNum：随机数取货码