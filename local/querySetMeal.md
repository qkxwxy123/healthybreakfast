## 套餐查询 api

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

###GET querySetMeal 查询推荐套餐
####参数

	{
		["pageNo" : Int] ,
		["pageSize" : Int]
	}

####说明
pageNo : 页码数 ，默认为1 ， 从头查起
pageSize ： 页码大小 ， 默认为10

####响应

```json
{
	"status" : Int , 
	"message" : String ,
	"data" : {
		"curPageNo" : Int,
		"curPageSize" : Int,
		"contents" :
		[
			[
				{
				"foodId" : Int,
				"sourceArea" : String ,
				"salesVolume" : Int ,
				"pictures" : String ,
				"foodFees" : String ,
				"deliveryCost" : String ,
				"foodName" : String
				},
				...
			],
			[
				{
				"foodId" : Int,
				"sourceArea" : String ,
				"salesVolume" : Int ,
				"pictures" : String ,
				"foodFees" : String ,
				"deliveryCost" : String ,
				"foodName" : String
				},
				...
			]
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
> data中的contents为json数组，按发布时间排序