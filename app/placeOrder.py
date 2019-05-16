from flask import Flask , request
import pymysql
import logging.config
import json
import random
import allConfig
import getOpenID

logging.config.fileConfig("placeOrderConfig.conf")
logger = logging.getLogger("placeOrder")

@allConfig.app.route('/placeOrder' , methods = ["POST"])
def placeOrder():
    code = str(request.json['code'])
    location = str(request.json['location'])
    getTime = str(request.json['getTime'])
    foodId = str(request.json['foodId'])

    pro_debug = '获得参数code：'+code+' location：'+location+' getTime：'+getTime+' foodId：'+foodId
    logger.info(pro_debug)

    Orders = getOpenID.getOpenIdObject(code)
    thisOrderOpenId = Orders.getOpenId()

    pro_debug = '换取openid成功'
    logger.info(pro_debug)

    #get randomnum 4位数 保证不重复
    randNum = 0
    while(True):
        random_num = int(random.random()*10000)

        pro_debug = '得到随机数：'+str(random_num)
        logger.info(pro_debug)

        sql = "select 1 from orderform where randomnum=%d limit 1;" % random_num
        cursor = allConfig.db.cursor()

        pro_debug = '查重...'
        logger.info(pro_debug)

        try:
            allConfig.db.ping(reconnect=True)
            cursor.execute(sql)
            allConfig.db.commit()
            res = cursor.fetchall()
            if not res:
                randNum = random_num

                pro_debug = '未重复，返回'
                logger.info(pro_debug)

                break

        except:
            allConfig.db.rollback()
        finally:
            allConfig.db.close()

    #通过foodId抓取图片
    sql = "select * from fruitandbreakfast where id=%d" % int(foodId)
    cursor = allConfig.db.cursor()

    pro_debug = '拿foodId抓取图片'
    logger.info(pro_debug)

    pictures = ''
    try:
        allConfig.db.ping(reconnect=True)
        cursor.execute(sql)
        if cursor:
            res = cursor.fetchall()
            for row in res:
                pictures = row[3]
    except:
        allConfig.db.rollback()
    finally:
        allConfig.db.close()

    sql = "insert into orderform (location , picture , gettime , openId , randomnum) values ('%s' , '%s' , '%s' , '%s' , %d)" % (location , pictures , getTime , thisOrderOpenId , randNum)
    cursor = allConfig.db.cursor()

    pro_debug = '执行sql：'+sql
    logger.info(pro_debug)

    try:
        allConfig.db.ping(reconnect=True)
        cursor.execute(sql)
        #allConfig.db.commit()

        if cursor:
            pro_debug = '下单成功 ，返回200'
            logger.info(pro_debug)
            response = {}
            response['status'] = 200
            response['message'] = 'ok'
            response['data'] = randNum
            return json.dumps(response , ensure_ascii=False)
        else:
            pro_debug = '下单失败 ，返回500'
            logger.info(pro_debug)
            response = {}
            response['status'] = 500
            response['message'] = 'error'
            response['data'] = None
            return json.dumps(response , ensure_ascii=False)
    except:
        allConfig.db.rollback()
    finally:
        allConfig.db.close()

if __name__ == '__main__':
    allConfig.app.run()