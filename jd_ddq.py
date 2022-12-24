import json
import time
from urllib.parse import quote

from utils.common import UserClass, printf, print_api_error, print_trace, wait, randomWait, get_sign, TaskClass


class Necklace(UserClass):
    def __init__(self, cookie):
        super(Necklace, self).__init__(cookie)
        self.appname = "50082"
        self.UA = self.jd_UA
        self.force_app_ck = True
        self.risk = False
        self.Origin = "https://h5.m.jd.com"
        self.referer = "https://h5.m.jd.com/"
        self.taskConfigVos = []
        self.exchangeGiftConfigs = []
        self.lastRequestTime = ''
        self.bubbles = []
        self.signInfo = []
        self.giftConfigId = ''
        self.taskItems = []

    def opt(self, opt):
        self.set_joyytoken()
        self.set_shshshfpb()
        _opt = {
            "method": "post",
            "api": "api",
            "log": False,
            "params": {
                "appid": "coupon-necklace",
                "client": "coupon-necklace",
                'loginType': '2',
                "t": str(int(time.time() * 1000))
            },
        }
        _opt.update(opt)
        return _opt

    def log_format(self, body, log_data):
        log_body = {
            "extraData": {
                "log": log_data["log"],
                "sceneid": "DDhomePageh5"
            },
            "random": log_data["random"]
        }
        body.update(log_body)
        body = f"body={quote(json.dumps(body, separators=(',', ':')))}"
        return body

    def necklace_homePage(self):
        if self.risk:
            return
        try:
            body = {

            }
            log_body = {
                "action": "",
                "log_id": "",
            }
            opt = {
                "functionId": "necklace_homePage",
                "body": body,
                "log_body": log_body,
                "log": True
            }
            status, data = self.jd_api(self.opt(opt))
            if data['rtn_code'] == 0:
                if data['data']['biz_code'] == 0:
                    result = data['data']['result']
                    self.taskConfigVos = result.get('taskConfigVos', [])
                    self.exchangeGiftConfigs = result.get('exchangeGiftConfigs', [])
                    self.lastRequestTime = result.get('lastRequestTime', '')
                    self.bubbles = result.get('bubbles', [])
                    self.signInfo = result.get('signInfo', [])
                    for exchangeGiftConfig in self.exchangeGiftConfigs:
                        if exchangeGiftConfig["giftType"] == 1:
                            self.giftConfigId = exchangeGiftConfig["id"]
        except Exception as e:
            printf(e)

    def necklace_chargeScores(self, bubleId):
        try:
            body = {
                "bubleId": bubleId
            }
            log_body = {
                "action": "chargeScores",
                "log_id": bubleId,
            }
            opt = {
                "functionId": "necklace_chargeScores",
                "body": body,
                "log_body": log_body,
                "log": True
            }
            status, data = self.jd_api(self.opt(opt))
            if data['rtn_code'] == 0:
                if data["data"]['biz_code'] == 0:
                    printf(f"[{self.Name}]\t领取奖励成功")
                elif data['rtn_code'] == 403 or '非法请求' in data.get('rtn_msg', ''):
                    printf(f"[{self.Name}]\t领取奖励失败：{data['rtn_msg']}")
                else:
                    printf(f"[{self.Name}]\t领取奖励失败：{json.dumps(data)}")
            else:
                print_api_error(opt, status)
        except:
            print_trace()

    def receiveBubbles(self):
        if self.risk:
            return
        for item in self.bubbles:
            printf(f"[{self.Name}]\t开始领取 [{item['bubbleName']}] 点点券")
            self.necklace_chargeScores(item['id'])
            randomWait(1, 2)
        pass

    def necklace_startTask(self, taskId, functionId='necklace_startTask', itemId=""):
        try:
            body = {
                'taskId': taskId,
                'currentDate': self.lastRequestTime.replace(":", "%3A")
            }
            if functionId == 'necklace_startTask':
                log_body = {
                    "action": "startTask",
                    "log_id": taskId,
                }
                opt = {
                    "functionId": functionId,
                    "body": body,
                    "log_body": log_body,
                    "log": True
                }
            else:
                if itemId:
                    body['itemId'] = itemId
                opt = {
                    "functionId": functionId,
                    "body": body,
                }
            status, res_data = self.jd_api(self.opt(opt))
            if res_data.get("rtn_code") == 0:
                if res_data.get('rtn_msg') == "未登录":
                    self.risk = False
                if "火爆" in res_data.get('rtn_msg', ''):
                    self.risk = True
                if "风控" in res_data.get('rtn_msg', ''):
                    self.risk = True
                if "风险" in res_data.get('rtn_msg', ''):
                    self.risk = True
                return res_data
            elif res_data.get("rtn_code") == 406:
                printf(f"[{self.Name}]\t{res_data.get('rtn_msg')}")
                self.risk = True
            else:
                printf(f"[{self.Name}]\t{res_data.get('rtn_msg')}")
                print_api_error(opt, status)
        except:
            print_trace()
            return {}

    def necklace_TaskApi(self, functionId, body={}):
        try:
            opt = {
                "functionId": functionId,
                "body": body,
            }
            status, res_data = self.jd_api(self.opt(opt))
            print(res_data)
            if res_data:
                pass
            else:
                print_api_error(opt, status)
        except:
            print_trace()

    def necklace_getTask(self, taskId):
        try:
            body = {
                'taskId': taskId,
                # 'currentDate': self.lastRequestTime.replace(":", "%3A")
            }
            opt = {
                "functionId": "necklace_getTask",
                "body": body,
            }
            status, res_data = self.jd_api(self.opt(opt))
            if res_data:
                if res_data['rtn_code'] == 0:
                    if res_data['data']['biz_code'] == 0 and res_data['data'].get("result"):
                        self.taskItems = res_data['data']['result'].get("taskItems", [])
                elif res_data['rtn_code'] == 403 or '非法请求' in res_data.get('rtn_msg', ''):
                    printf(f"[{self.Name}]\t浏览精选活动失败：{res_data['rtn_msg']}\n")
                else:
                    printf(f"[{self.Name}]\t浏览精选活动失败：{json.dumps(res_data)}\n")
            else:
                print_api_error(opt, status)
        except:
            print_trace()

    def postRequest(self, function_id, body={}):
        try:
            opt = {
                "functionId": function_id,
                "body": body,
                "api": "client.action",
                "params": {
                    "appid": "wh5",
                    "client": "apple",
                    "clientVersion": "10.2.4"
                }
            }
            self.Origin = "https://carry.m.jd.com"
            self.referer = "https://carry.m.jd.com"
            status, res_data = self.jd_api(self.opt(opt))
            if res_data:
                pass
            else:
                printf("\t东东农场: API查询请求失败 ‼️‼️")
                printf(json.dumps(res_data))
                print_api_error(opt, status)
        except:
            print_trace()
        self.Origin = "https://h5.m.jd.com"
        self.referer = "https://h5.m.jd.com/"

    def getCcTaskList(self):
        try:
            opt = {
                "functionId": "getCcTaskList",
                "body": {"pageClickKey": "CouponCenter",
                         "shshshfpb": "dPH6zeJy\/HFogCIf0ZGFYqSDOShGwmpjVOPM\/ViCGC5fgBLL9JoI9mjgUt46vjSFeSkmU9DZLEjFaeFTWBj4Axg==",
                         "eid": "eidIeb54812323sf AJEbj5LR0Kf6GUzM9DKXvgCReTpKTRyRwiuxY\/uvRHBqebAAKCAXkJFzhWtPj5uoHxNeK3DjTumb rfXOt1w0\/dGmOJzfbLuyNo",
                         "childActivityUrl": "openapp.jdmobile://virtual?params={\"category\":\"jump\",\"des\":\"couponCenter\"}",
                         "lat": "24.49441271645999", "globalLat": "24.49335", "lng": "118.1447713674174",
                         "globalLng": "118.1423"},
                "params": {},
                "sign": True
            }
            status, res_data = self.jd_api(self.opt(opt))
            if res_data:
                pass
            else:
                printf(json.dumps(res_data))
                print_api_error(opt, status)
        except:
            print_trace()

    def reportCcTask(self):
        try:
            pass
        except:
            print_trace()

    def reportSinkTask(self, task_id):
        try:
            opt = {
                "functionId": "reportSinkTask",
                "body": {"platformType": "1", "taskId": f"necklace_{task_id}"},
                "params": {
                    "appid": "XPMSGC2019"
                },
                "sign": True
            }
            status, res_data = self.jd_api(self.opt(opt))
            if res_data:
                pass
            else:
                printf(json.dumps(res_data))
                print_api_error(opt, status)
        except:
            print_trace()

    def doAppTask(self, task_id, _type="3"):
        self.getCcTaskList()
        if _type == "4":
            body = f'&appid=XPMSGC2019&monitorSource=&uuid={self.uuid}&body={"platformType":"1","taskId":"necklace_{task_id}"}&client=m&clientVersion=4.6.0&area=16_1315_1316_59175&geo=[object Object]'
            functionId = 'reportSinkTask'
            printf("需等待30秒")
            randomWait(30, 1)
            self.getCcTaskList(functionId, body, _type)
        elif _type == "3":
            body = {
                "to": 'https://m.jd.com',
                "action": "to"
            }
            sign = get_sign("genToken", json.dumps(body))
            opt = {
                "functionId": "reportCcTask",
                "body": body
            }
            # body =
            pass

    def reportTask(self, item):
        # 普通任务
        if item['taskType'] == 2:
            if item.get('requireBrowseSeconds', 0):
                self.necklace_TaskApi('necklace_timedTask', {"taskId": item['id'], "itemId": ""})
                printf(f"[{self.Name}]\t等待{item['requireBrowseSeconds']}s")
                wait(item['requireBrowseSeconds'])
            self.necklace_startTask(item['id'], 'necklace_reportTask')
        # 逛很多商品店铺等等任务
        if item['taskType'] == 6 or item['taskType'] == 5 or item['taskType'] == 9:
            self.necklace_getTask(item['id'])
            for vo in self.taskItems:
                if vo and vo["status"] != 0:
                    continue
                printf(f"[{self.Name}]\t浏览精选活动 【{vo['title']}】")
                if item.get('requireBrowseSeconds', 0):
                    self.necklace_TaskApi('necklace_timedTask', {"taskId": item['id'], "itemId": vo.get('id', "")})
                    printf(f"[{self.Name}]\t等待{item['requireBrowseSeconds']}s")
                    wait(item['requireBrowseSeconds'])
                self.necklace_startTask(item['id'], 'necklace_reportTask', vo['id'])
                randomWait(1, 2)
        # 关注精选频道
        if item['taskType'] == 7:
            self.necklace_getTask(item['id'])
            for vo in self.taskItems:
                printf(f"[{self.Name}]\t关注精选频道 【{vo['title']}】")
                if vo['status'] == 2:
                    printf(f"[{self.Name}]\t任务已完成！")
                    continue
                self.necklace_TaskApi('necklace_doTask', {"taskId": item['id'], "itemId": vo['id']})
                self.necklace_startTask(item['id'], 'necklace_reportTask', vo['id'])
                self.postRequest('isUserFollow',
                                 {
                                     "themeId": vo['id'],
                                     "informationParam": {
                                         "isRvc": "0", "fp": "-1",
                                         "eid": "eidIf12a8121eas2urxgGc+zS5+UYGu1Nbed7bq8YY+gPd0Q0t+iviZdQsxnK\/HTA7AxZzZBrtu1ulwEviYSV3QUuw2XHHC+PFHdNYx1A\/3Zt8xYR+d3",
                                         "shshshfp": "-1", "userAgent": "-1", "referUrl": "-1", "shshshfpa": "-1"},
                                     "businessId": "1"}
                                 )
                randomWait(1, 2)

        # 关注浏览10s
        if item['taskType'] == 8:
            self.necklace_getTask(item['id'])
            for vo in self.taskItems:
                if vo and vo["status"] != 0:
                    continue
                printf(f"[{self.Name}]\t关注浏览10s 【{vo['title']}】")
                self.necklace_TaskApi('necklace_doTask', {"taskId": item['id'], "itemId": vo['id']})
                if item.get('requireBrowseSeconds', 0):
                    self.necklace_TaskApi('necklace_timedTask', {"taskId": item['id'], "itemId": vo.get('id', "")})
                    printf(f"[{self.Name}]\t等待{item['requireBrowseSeconds']}s")
                    wait(item['requireBrowseSeconds'])
                self.necklace_startTask(item['id'], 'necklace_reportTask', vo['id'])
                randomWait(1, 2)

        # if item['taskType'] == 4:
        #     self.doAppTask('4', item['id'])
        # if item['taskType'] == 3:
        #     self.doAppTask('3', item['id'])

    def doTask(self):
        for item in self.taskConfigVos:
            if self.risk:
                return
            if item['taskStage'] == 0:
                printf(f"[{self.Name}]\t【{item['taskName']}】 任务未领取, 开始领取此任务")
                self.taskId = item['id']
                res = self.necklace_startTask(item['id'])
                if res and res['rtn_code'] == 0:
                    printf(f"[{self.Name}]\t【{item['taskName']}】 任务领取成功, 开始完成此任务")
                    self.reportTask(item)
                    randomWait(1, 2)
            elif item['taskStage'] == 2:
                printf(f"[{self.Name}]\t【{item['taskName']}】 任务已做完,奖励未领取")
            elif item['taskStage'] == 3:
                printf(f"[{self.Name}]\t【{item['taskName']}】 奖励已领取")
            elif item['taskStage'] == 1:
                printf(f"[{self.Name}]\t【{item['taskName']}】 任务已领取但未完成,开始完成此任务")
                self.reportTask(item)
                randomWait(1, 2)

    def main(self):
        self.necklace_homePage()
        if self.risk:
            return
        wait(2)
        self.doTask()
        wait(2)
        self.necklace_homePage()
        self.receiveBubbles()


if __name__ == '__main__':
    task = TaskClass("task")
    task.name = 'DDQ'
    task.init_config(Necklace)
    task.main("点点券-任务")
