from flask import Flask , request
import pymysql
import logging.config
import json
import allConfig
import getOpenID

logging.config.fileConfig("selfLocationConfig.conf")
logger = logging.getLogger()

@allConfig.app.route('/addSelfLocation' , methods = ["POST"])
def addSelfLocation():
    dayOfWeek = str(request.json['dayOfWeek'])
    location = str(request.json['location'])
    code = str(request.json['code'])

    pro_debug = '获得参数dayOfWeek：'+dayOfWeek+' location:'+location+' code:'+code
    logger.info(pro_debug)

    l_object = getOpenID.getOpenIdObject(code)
    thisOpenId = l_object.getOpenId()

    pro_debug = '获取openid成功'
    logger.info(pro_debug)

    sql = "insert into selflocation (dayofweek , location , openid) values ('%s' , '%s' , '%s')" % (dayOfWeek , location , thisOpenId)
    cursor = allConfig.db.cursor()

    try:
        allConfig.db.ping(reconnect=True)
        cursor.execute(sql)

        pro_debug = '执行sql：'+sql
        logger.info(pro_debug)

        if cursor:
            pro_debug = '执行成功，返回200'
            logger.info(pro_debug)

            response = {}
            response['status'] = 200
            response['message'] = 'ok'
            response['data'] = None
            return json.dumps(response)
        else:
            pro_debug = '执行失败，返回500'
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


@allConfig.app.route('/deleteSelfLocation' , methods=["POST"])
def deleteSelfLocation():
    dayOfWeek = str(request.json['dayOfWeek'])
    location = str(request.json['location'])
    code = str(request.json['code'])

    pro_debug = '获得参数dayOfWeek:'+dayOfWeek+' location:'+location+' code:'+code
    logger.info(pro_debug)

    l_object = getOpenID.getOpenIdObject(code)
    thisOpenId = l_object.getOpenId()

    pro_debug = '换取openid成功'
    logger.info(pro_debug)

    sql = "delete from selfLocation where openid = '%s' and dayofweek = '%s' and location = '%s'" % (thisOpenId , dayOfWeek , location)
    cursor = allConfig.db.cursor()


    try:
        allConfig.db.ping(reconnect=True)
        cursor.execute(sql)
        allConfig.db.commit()

        pro_debug = '执行sql：' + sql
        logger.info(pro_debug)

        if cursor:
            pro_debug = '执行成功，返回200'
            logger.info(pro_debug)

            response = {}
            response['status'] = 200
            response['message'] = 'ok'
            response['data'] = None
            return json.dumps(response)
        else:
            pro_debug = '执行失败，返回500'
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

@allConfig.app.route('/querySelfLocation' , methods = ["GET"])
def querySelfLocation():
    code = str(request.json['code'])

    pro_debug = '获得参数code：'+code
    logger.info(pro_debug)

    q_object = getOpenID.getOpenIdObject(code)
    thisOpenId = q_object.getOpenId()
    pro_debug = '换取openid成功'
    logger.info(pro_debug)

    sql = "select * from selflocation where openid = '%s'" % thisOpenId
    cursor = allConfig.db.cursor()

    try:
        allConfig.db.ping(reconnect=True)
        cursor.execute(sql)
        pro_debug = '执行sql：'+sql
        logger.info(pro_debug)

        if cursor:
            res = cursor.fetchall()
            pro_debug = '抓取数据成功'
            logger.info(pro_debug)

            locationList = {}
            count = 1
            for row in res:
                lists = {}
                lists['id'] = row[0]
                lists['dayOfWeek'] = row[1]
                lists['location'] = row[2]
                locationList[count] = lists
                count += 1
            response = {}
            response['status'] = 200
            response['message'] = 'ok'
            response['data'] = locationList
            pro_debug = '执行成功，返回200'
            logger.info(pro_debug)

            return json.dumps(response)
        else:
            pro_debug = '执行失败，返回500'
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

@allConfig.app.route('/changeSelfLocation' , methods = ["POST"])
def changeSelfLocation():
    dayOfWeek = str(request.json['dayOfWeek'])
    location = str(request.json['location'])
    code = str(request.json['code'])
    pro_debug ='获取参数dayOfWeek：'+dayOfWeek+' location:'+location+' code:'+code
    logger.info(pro_debug)

    c_object = getOpenID.getOpenIdObject(code)
    thisOpenId = c_object.getOpenId()
    pro_debug = '换取openid成功'
    logger.info(pro_debug)

    sql = "update selflocation set location = '%s' where dayofweek = '%s' and openid = '%s'" % (location , dayOfWeek , thisOpenId)
    cursor = allConfig.db.cursor()

    try:
        allConfig.db.ping(reconnect=True)
        cursor.execute(sql)
        allConfig.db.commit()
        pro_debug = '执行sql：'+sql
        logger.info(pro_debug)

        if cursor:
            pro_debug = '执行成功，返回200'
            logger.info(pro_debug)

            response = {}
            response['status'] = 200
            response['message'] = 'ok'
            response['data'] = None
            return json.dumps(response)
        else:
            pro_debug = '执行失败，返回500'
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