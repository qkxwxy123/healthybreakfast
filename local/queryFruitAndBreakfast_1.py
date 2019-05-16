from flask import Flask , request
import json
import logging
import logging.config
import allConfig                                                #加载allConfig模块

logging.config.fileConfig("queryFruitAndBreakfastlogging.conf")                       #加载配置文档
logger = logging.getLogger("queryFruitAndBreakfast")            #记录文件名为queryFruitAndBreakfast

@allConfig.app.route('/queryFruitAndBreakfast' , methods = ["GET"])
def queryFruitAndBreakfast():
    foodName = request.args.get('foodName')
    pageNo = request.args.get('pageNo')
    if not isinstance(pageNo , str):
        pageNo = 1
    pageSize = request.args.get('pageSize')
    if not isinstance(pageSize , str):
        pageSize = 10

    pageSize_debug = '传入查询参数pageSize :' + str(pageSize)
    pageNo_debug = '传入查询参数pageNo :' + str(pageNo)
    logger.info(pageSize_debug)
    logger.info(pageNo_debug)

    sql = "select * from fruitAndBreakfast where foodname like '%%%s%%' limit %d,%d" % (foodName , int(pageSize)*(int(pageNo)-1) , int(pageSize))  #模糊匹配得到的foodname
    cursor = allConfig.db.cursor()

    foodName_debug = '得到参数foodName：' + foodName
    logger.info(foodName_debug)

    try:
        pro_debug = '执行sql:' + sql
        logger.info(pro_debug)

        allConfig.db.ping(reconnect = True)
        cursor.execute(sql)

        if cursor:
            pro_debug = '尝试抓取查询数据'
            logger.info(pro_debug)

            results = cursor.fetchall()
            result = {}
            count = 1

            pro_debug = '抓取成功'
            logger.info(pro_debug)

            result['curPageNo'] = pageNo
            result['curPageSize'] = pageSize

            for row in results:
                foodList = {}
                foodList['foodId'] = row[0]
                foodList['sourceArea'] = row[1]
                foodList['salesVolume'] = row[2]
                foodList['pictures'] = row[3]
                foodList['foodfees'] = row[4]
                foodList['deliveryCost'] = row[5]
                foodList['foodName'] = row[6]
                foodList['foodType'] = row[7]
                result[count] = foodList
                count += 1

            response = {}
            response['status'] = 200
            response['message'] = 'ok'
            response['data'] = result

            pro_debug = '成功执行并返回'
            logger.info(pro_debug)

            return json.dumps(response)              #若查得数据，加入response返回

        else:
            pro_debug = '执行失败 ， 返回500'
            logger.info(pro_debug)

            response = {}
            response['status'] = 500
            response['message'] = 'erre'
            response['data'] = None
            return json.dumps(response)               #出现错误返回码500
    except:
        allConfig.db.rollback()
    finally:
        allConfig.db.close()

if __name__ == '__main__':
    allConfig.app.run()