## 按销量排序 热搜榜api

### 接口说明

- 本期接口响应都遵循以下格式

```json
{
    "status":Int,
    "message":String,
    "data":String
}
```

status : 状态信息。接口成功响应返回200，发生服务端错误返回500

message : 消息

data : json字符串

- 接口参数中，带括号[]的参数为可选参数，详见各接口说明

### GET queryHotMeal
####参数
	
	{
		["pageNo" : Int] ,
		["pageSize" : Int]
	}

####说明
pageNo ： 页码数 ，默认为1 ， 从头查起
pageSize ： 页码大小， 默认为10

####响应

```json
{
	"status" : Int ,
	"message" : String ,
	"data" : {
		"curPageNo" : Int ,
		"curPageSize" : Int ,
		"foodList" : 
		[
			{
				"sortedNo" : Int ,
				"foodName" : String,
				"salesVolume" : Int
			}
			...
		]
	}
}
```

####说明
curPageNo : 当前页码

curPageSize : 页面大小

sortedNo : 销量排名

foodName : 食物名称

salesVolume : 销量



> data中的foodList为json数组