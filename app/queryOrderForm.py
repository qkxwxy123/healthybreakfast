from flask import Flask , request
import json
import logging.config
import allConfig
import getOpenID

logging.config.fileConfig("queryOrderFormConfig.conf")
logger = logging.getLogger("queryOrderForm")

@allConfig.app.route('/queryOrderForm' , methods=["GET"])
def queryOrderForm():
    code = str(request.json['code'])
    pro_debug = '获得参数code：'+code
    logger.info(pro_debug)

    q_object = getOpenID.getOpenIdObject(code)
    thisOpenId = q_object.getOpenId()

    pro_debug = '换取openid成功'
    logger.info(pro_debug)

    sql = "select * from orderform where openid = '%s'" % thisOpenId
    cursor = allConfig.db.cursor()

    try:
        allConfig.db.ping(reconnect=True)
        cursor.execute(sql)

        pro_debug = '执行sql'+sql
        logger.info(pro_debug)

        if cursor:
            res = cursor.fetchall()
            pro_debug = '抓取数据成功'
            logger.info(pro_debug)

            orderList = {}
            count = 1

            for row in res:
                pro = {}
                pro['id'] = row[0]
                pro['location'] = row[1]
                pro['picture'] = row[2]
                pro['getTime'] = row[3]
                pro['openId'] = row[4]
                pro['randNum'] = row[5]
                orderList[count] = pro
                count += 1

            response = {}
            response['status'] = 200
            response['message'] = 'ok'
            response['data'] = orderList

            pro_debug = '执行成功，返回200'
            logger.info(pro_debug)

            return json.dumps(response)

        else:
            response = {}
            response['status'] = 500
            response['message'] = 'error'
            response['data'] = None

            pro_debug = '执行失败，返回500'
            logger.info(pro_debug)

            return json.dumps(response)

    except:
        allConfig.db.rollback()
    finally:
        allConfig.db.close()

if __name__ == '__main__':
    allConfig.app.run()
