## 地址管理api

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


####POST addSelfLocation

####参数

	{
		"dayOfWeek" : String ,
		"location" : String ,
		"code" : String
	}

####说明

dayOfWeek：周几

location：地点

code：用于兑换openid

####响应

```json
{
	"status":Int ,
	"message":String ,
	"data":String
}
```


####POST changeSelfLocation

####参数

	{
		"dayOfWeek" : String ,
		"location" : String ,
		"code" : String
	}

####说明
dayOfWeek：周几

location：更改后的地点

code：用于兑换openid

 > 选择将周几对应的地点改变

####响应
```json
{
	"status" : Int,
	"message" : String,
	"data" : String
}
```






####GET querySelfLocation

####参数

	{
		"code" : String
	}

####说明
code:用于换取openid

####响应
```json
{
	"status":Int ,
	"message":String ,
	"data":
	{
		"locationList":
		[
			{
				"id":Int ,
				"dayOfWeek":String ,
				"location":String 
			}
			...
		]
	}
}
```

####说明
id：地址序号

dayOfWeek：周几

location：地址

> data中的locationList是json数组


####POST deleteSelfLocation

####参数

	{
		"code" : String ,
		"dayOfWeek" : String ,
		"location" : String
	}
####说明
code：用于兑换openid

dayOfWeek：删除记录是周几

location：删除记录的地址

####响应
```json
{
	"status":Int,
	"message":String,
	"data":String
}
```