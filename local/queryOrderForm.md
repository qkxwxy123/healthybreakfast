## 查询订单api文档

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

#### GET queryOrderForm

####参数

	{
		"openId" : String
	}

####说明
openId ： 用户的openId

####响应

```json
{
	"status" : Int ,
	"message" : String ,
	"data" : 
	{
		"orderList":
		[
			{
				"id" : Int ,
				"location" : String ,
				"pictures" : String ,
				"getTime" : String ,
				"randNum" : String
			}
			...
		]
	}
}
```

####说明

id:订单编号

location：送达地点

pictures：食物图片url

getTime：送餐时间

randNum:取货码
> data中的orderList为json数组