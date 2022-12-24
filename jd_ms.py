import json
import os
from urllib.parse import quote

from utils.common import UserClass, printf, print_trace, TaskClass, print_api_error, wait, randomWait


class MSUserClass(UserClass):
    def __init__(self, cookie):
        super(MSUserClass, self).__init__(cookie)
        self.inviteCode = ""
        self.appname = "50086"
        self.UA = self.jd_UA
        self.force_app_ck = True
        self.encryptProjectId = ''
        self.sourceCode = ''
        self.sign = True
        self.risk = False
        self.score = 0
        self.Origin = "https://h5.m.jd.com"
        self.referer = "https://h5.m.jd.com/babelDiy/Zeus/2NUvze9e1uWf4amBhe1AV6ynmSuH/index.html"

    def opt(self, opt):
        self.set_joyytoken()
        self.set_shshshfpb()
        _opt = {
            "method": "post",
            "api": "client.action",
            "log": False,
            "params": {
                "client": "wh5",
                "clientVersion": "1.0.0",
                "osVersion": ""
            },
        }
        _opt.update(opt)
        return _opt

    def log_format(self, body, log_data):
        extParam = {
            "businessData": {
                "random": log_data['random']
            },
            "signStr": log_data['log'],
            "sceneid": "MShPageh5"
        }
        body.update({"extParam": extParam})
        return f"body={quote(json.dumps(body, separators=(',', ':')))}"

    def log_format2(self, body, log_data):
        body.update({"log": log_data["log"]})
        body.update({"random": log_data["random"]})
        body = f"body={quote(json.dumps(body, separators=(',', ':')))}"
        return body

    def getActInfo(self):
        try:
            body = {"sceneid": "MShPageh5"}
            opt = {
                "functionId": "assignmentList",
                "body": body,
                # "log": True,
                "params": {
                    "appid": "jwsp",
                    "client": "wh5",
                    "clientVersion": "1.0.0",
                }
            }
            status, result = self.jd_api(self.opt(opt))
            if result:
                if result['code'] == 200:
                    self.encryptProjectId = result['result']['assignmentResult']['encryptProjectId']
                    if "风控" in result['result']['assignmentResult']['projectName']:
                        printf(result['result']['assignmentResult']['projectName'])
                        self.risk = True
                    printf(f"活动名称：{result['result']['assignmentResult']['projectName']}")
                    self.sourceCode = result['result']['sourceCode']
                elif result['code'] == 202:
                    if "风控" in result['result']['msg']:
                        printf(result['result']['msg'])
                        self.risk = True
                    printf(f"活动名称：{result['result']['msg']}")
                else:
                    printf("获取projectId失败")
            else:
                print_api_error(opt, status)
        except:
            print_trace()

    def getUserInfo(self, info=True):
        try:
            body = {"sceneid": "MShPageh5"}
            opt = {
                "functionId": "homePageV2",
                "body": body,
                "log": True,
                "params": {
                    "appid": "SecKill2020",
                    "client": "wh5",
                    "clientVersion": "1.0.0",
                }
            }
            status, result = self.jd_api(self.opt(opt))
            if result.get("code") == 2060:
                self.score = result['result']['assignment'].get('assignmentPoints', 0)
                if info:
                    printf(f"当前秒秒币: {self.score}")
            elif result.get("code") == 2041:
                self.score = result['result']['assignment'].get('assignmentPoints', 0)
                if info:
                    printf(f"当前秒秒币: {self.score}")
            else:
                self.score = 0
                print_api_error(opt, status)
        except:
            print_trace()
            self.score = 0
        return self.score

    def doTask(self, body):
        try:
            body.update(
                {
                    "encryptProjectId": self.encryptProjectId,
                    "sourceCode": self.sourceCode,
                    "ext": {},
                }
            )
            opt = {
                "functionId": "doInteractiveAssignment",
                "body": body,
                "log": True
            }
            status, result = self.jd_api(self.opt(opt))
            printf(f'[{self.Name}]\t{result.get("msg")}')
            if '风险等级未通过' in result.get("msg"):
                self.risk = True
            elif '火爆' in result.get("msg"):
                self.risk = True
            elif '未登录' in result.get("msg"):
                self.risk = True
            elif '风控' in result.get("msg"):
                self.risk = True
        except:
            print_trace()

    def signRedPackage(self):
        try:
            self.log_format = self.log_format2
            body = {"ext": {"platform": "1",
                            "eid": "eidAa85e812093sffr+fvK2/SCSkQWkpv5XVsn6/oUBcVJZ674/gMj9RMLH1pw16SYzR8Xd3B5gUqZ8V2jMZGUKR5GEFPanzOWqx2KH75ET+nvS+fiN3",
                            "referUrl": -1, "userAgent": -1}}
            opt = {
                "functionId": "signRedPackage",
                "body": body,
                'log': True,
                "params": {
                    "appid": "SecKill2020",
                    "client": "wh5",
                    "clientVersion": "1.0.0",
                }
            }
            status, result = self.jd_api(self.opt(opt))
            data = result
            if data['code'] == 200:
                rewardsInfo = data['result']['assignmentResult']['msg']
                printf(f'{rewardsInfo}')
            elif data['code'] == 2025:
                rewardsInfo = data['result']['assignmentResult']['title']
                printf(f'{rewardsInfo}')
                printf("可能是黑号")
            else:
                print_api_error(opt, status)
        except:
            print_trace()

    def getTaskList(self):
        try:
            body = {"encryptProjectId": self.encryptProjectId, "sourceCode": "wh5"}
            opt = {
                "functionId": "queryInteractiveInfo",
                "body": body,
                'log': True
            }
            status, result = self.jd_api(self.opt(opt))
            if result.get("code") == '0':
                for vo in result.get('assignmentList', []):
                    if self.risk:
                        return
                    if not vo.get("completionCnt") and vo.get("completionCnt") != 0:
                        continue
                    if vo['completionCnt'] < vo['assignmentTimesLimit']:
                        if vo['assignmentType'] == 5:
                            self.sign = False
                        if vo['assignmentType'] == 1:
                            if len(vo['ext'][vo['ext']['extraType']]) == 0:
                                continue
                            i = vo['completionCnt']
                            for i in range(i, vo['assignmentTimesLimit']):
                                printf(
                                    f"[{self.Name}]\t去做{vo['assignmentName']}任务：{i + 1} / {vo['assignmentTimesLimit']}")
                                body = {
                                    "encryptAssignmentId": vo['encryptAssignmentId'],
                                    "itemId": vo['ext'][vo['ext']['extraType']][i]['itemId'],
                                    "actionType": 1,
                                    "completionFlag": ""
                                }
                                self.doTask(body)
                                randomWait(vo['ext']['waitDuration'], 1)
                                if vo['ext']['waitDuration']:
                                    body['actionType'] = 0
                                    self.doTask(body)

                        elif vo['assignmentType'] == 0:
                            i = vo['completionCnt']
                            for i in range(i, vo['assignmentTimesLimit']):
                                printf(f"[{self.Name}]去{vo['assignmentName']}任务：{i + 1} / {vo['assignmentTimesLimit']}")
                                body = {
                                    "encryptAssignmentId": vo['encryptAssignmentId'],
                                    "itemId": "",
                                    "actionType": "0",
                                    "completionFlag": True
                                }
                                self.doTask(body)
                                randomWait(1, 1)
                        elif vo['assignmentType'] == 3:
                            i = vo['completionCnt']
                            for i in range(i, vo['assignmentTimesLimit']):
                                printf(f"[{self.Name}]去{vo['assignmentName']}任务：{i + 1} / {vo['assignmentTimesLimit']}")
                                body = {
                                    "encryptAssignmentId": vo['encryptAssignmentId'],
                                    "itemId": vo['ext'][vo['ext']['extraType']][i]['itemId'],
                                    "actionType": 0,
                                    "completionFlag": ""
                                }
                                self.doTask(body)
                                randomWait(1, 1)
            else:
                print_api_error(opt, status)
        except:
            print_trace()

    def main(self):
        self.getActInfo()
        score = self.getUserInfo()
        self.getTaskList()
        if not self.sign:
            printf(f"[{self.Name}]:\t去完成每日签到")
            self.signRedPackage()
        end_score = self.getUserInfo(False)
        printf(f"[{self.Name}]本次运行共获得: {end_score - score}秒秒币\n\n")


if __name__ == '__main__':
    task = TaskClass("task")
    task.name = 'MS'
    task.init_config(MSUserClass)
    task.main("秒秒币-任务")
