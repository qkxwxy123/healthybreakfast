##搜索 api

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

### GET   queryFruitAndBreakfast (查询水果或者早餐)
####参数

	{
		"foodName" : String ,
		["pageNo" : Int] ,
		["pageSize" : Int]
	}

####说明

foodName ： 搜索的食物名称
pageNo : 可选参数页码，默认为1从首页查询
pageSize ：可选参数页码大小 ，默认为10

####响应

```json
{
	"status" : Int , 
	"message" : String ,
	"data" : {
		"curPageNo":Int ,
		"curPageSize":Int,
		"foodList":
		[
			{
			"foodId" : Int,
			"sourceArea" : String ,
			"salesVolume" : Int ,
			"pictures" : String ,
			"foodFees" : String ,
			"deliveryCost" : String ,
			"foodName" : String,
			"foodType" : String
			}
			...
		]
	}
}
```

####说明
foodId ：食物编号

sourceArea ： 食物原产地

salesVolume ： 销量

pictures ： 食物图片的url

foodFees ： 食物价格

deliveryCost ：食物配送费

foodName : 食物名称

foodType : 食物种类

> data中的foodList是json数组