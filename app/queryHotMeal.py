from flask import Flask , request
import json
import logging.config
import allConfig                                                        #导入配置模块allConfig

logging.config.fileConfig("queryHotMeallogging.conf")                   #加载配置工作日志文档
logger = logging.getLogger("queryHotMeal")                              #工作日志名queryHotMeal

@allConfig.app.route('/queryHotMeal' , methods = ["GET"])               #接口名queryHotMeal,方法为GET
def queryHotMeal():
    pageNo = str(request.json['pageNo'])

    pro_debug = '尝试得到参数pageNo'
    logger.info(pro_debug)

    if not isinstance(pageNo , str):                                    #未从前端获得参数pageNo
        pageNo = 1                                                      #赋值为1

        pro_debug = '未得到参数pageNo，赋值为1'
        logger.info(pro_debug)
    else:
        pro_debug = '得到参数pageNo :' + pageNo
        logger.info(pro_debug)

    pro_debug = '尝试得到参数pageSize'
    logger.info(pro_debug)

    pageSize = str(request.json['pageSize'])
    if not isinstance(pageSize , str):                                  #未从前端获得参数pageSize
        pageSize = 10                                                   #赋值为10

        pro_debug = '未得到参数pageSize ， 赋值为10'
        logger.info(pro_debug)

    else:
        pro_debug = '得到参数pageSize ：' + pageSize
        logger.info(pro_debug)
    sql = "select * from fruitandbreakfast order by salesvolume desc limit %d , %d" % (int(pageSize)*(int(pageNo)-1) , int(pageSize))

    pro_debug = 'sql语句为：' + sql
    logger.info(pro_debug)

    cursor = allConfig.db.cursor()
    try:
        allConfig.db.ping(reconnect=True)
        cursor.execute(sql)

        pro_debug = '尝试执行sql语句'
        logger.info(pro_debug)

        if cursor:

            pro_debug = '执行成功，进行数据抓取'
            logger.info(pro_debug)

            results = cursor.fetchall()

            pro_debug = '数据抓取成功'
            logger.info(pro_debug)

            count = 1                                                   #从数据库获得记录，count为记录数
            sortId = 1                                                  #sortId：排序后的基数，与count等值
            result = {'curPageNo': pageNo, 'curpageSize': pageSize}     #resul为data对应的值

            for row in results:
                foodList = {}
                foodList['sortedNo'] = sortId
                foodList['foodName'] = row[6]
                foodList['salesVolume'] = row[2]
                sortId += 1
                result[count] = foodList
                count += 1

            response = {}
            response['status'] = 200
            response['message'] = 'ok'
            response['data'] = result
            return json.dumps(response)
        else:
            pro_debug = '执行失败，返回'
            logger.info(pro_debug)

            response = {}
            response['status'] = 500
            response['message'] = 'error'
            response['data'] = None
            return json.dumps(response)
    except:
        allConfig.db.rollback()
    finally:
        allConfig.db.close()

if __name__ == '__main__':
    allConfig.app.run()
