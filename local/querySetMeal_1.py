from flask import Flask , request
import json
import logging.config
import allConfig                                                                            #导入配置模块

logging.config.fileConfig("querySetMeal.conf")                                              #配置日志文档
logger = logging.getLogger("querySetMeal")                                                  #以querySetMeal为名

@allConfig.app.route('/querySetMeal' , methods = ["GET"])
def querySetMeal():
    pageNo = request.args.get('pageNo')

    pro_debug = '获取参数pageNo...'
    logger.info(pro_debug)

    if not isinstance(pageNo , str):                                                        #如果没有得到参数pageNo
        pageNo = 1                                                                          #默认赋值1

        pro_debug = '未获得参数pageNo ， 赋值为1'
        logger.info(pro_debug)

    else:
        pro_debug = '得到参数pageNo为：' + pageNo
        logger.info(pro_debug)

    pageSize = request.args.get('pageSize')
    if not isinstance(pageSize , str):                                                      #如果没有得到参数pageSize
        pageSize = 10                                                                       #默认赋值为10

        pro_debug = '未获得参数pageSize ， 赋值为10'
        logger.info(pro_debug)

    else:
        pro_debug = '得到参数pageSize为：' + pageSize
        logger.info(pro_debug)

    sql = "select * from setmeal limit %d , %d" % (int(pageSize)*(int(pageNo)-1) , int(pageSize))
    cursor = allConfig.db.cursor()

    try:
        allConfig.db.ping(reconnect=True)
        cursor.execute(sql)
        pro_debug = '尝试执行sql语句' + sql
        logger.info(pro_debug)

        if cursor:
            pro_debug = '执行成功,尝试抓取数据'
            logger.info(pro_debug)

            results = cursor.fetchall()                                    #results为抓取的内容
            pro_debug = '抓取成功'
            logger.info(pro_debug)

            result = {}                                                    #result为data对应的内容
            contents = []
            everySetContent = []
            result['curPageNo'] = pageNo
            result['curPageSize'] = pageSize
            count = 1

            for row in results:                                           #row为一个套餐的记录,row[1]是mysql中存的content，格式为 1 ， 2 ， 3格式
                content = row[1]                                          #content为套餐中食物的id们
                everySetContent = []
                for foodId_i in content:                                  #foodId_i为食物id
                    if(foodId_i == ' '):                                  #如果为空，跳到下一个字符
                        continue

                    sql = "select * from fruitandbreakfast where id = %d" % int(foodId_i)  #去另一张表查找食物信息

                    try:
                        allConfig.db.ping(reconnect=True)
                        cursor.execute(sql)
                        pro_debug = '尝试执行sql语句' + sql
                        logger.info(pro_debug)

                        if cursor:
                            pro_debug = '执行成功，尝试抓取数据'
                            logger.info(pro_debug)
                            foodMsg = cursor.fetchall()                                          #foodMsg为抓取到的对象
                            pro_debug = '数据抓取成功，解析数据'
                            logger.info(pro_debug)

                            for rows in foodMsg:
                                foodmsg = {'foodId': rows[0], 'sourceArea': rows[1], 'salesVolume': rows[2],
                                           'pictures': rows[3], 'foodfees': rows[4], 'deliveryCost': rows[5],
                                           'foodName': rows[6], 'foodType': rows[7]}            #foodmsg为保存食物信息的字典
                                everySetContent.append(foodmsg)

                        else:
                            pro_debug = '执行失败，退出'
                            logger.info(pro_debug)
                            response = {}
                            response['status'] = 500
                            response['message'] = 'error'
                            response['data'] = None
                            return json.dumps(response)

                    except:
                        allConfig.db.rollback()
                contents.append(everySetContent)

            response = {}
            response['status'] = 200
            response['message'] = 'ok'
            result['contents'] = contents
            response['data'] = result

            return json.dumps(response)

        else:
            pro_debug = '执行失败，退出'
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