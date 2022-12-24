import json
import os
from urllib.parse import quote

from utils.common import UserClass, printf, print_trace, TaskClass, print_api_error, wait, randomWait

XmfRewardList = os.environ.get("XmfRewardList", '').split(",")


class XMFUserClass(UserClass):
    def __init__(self, cookie):
        super(XMFUserClass, self).__init__(cookie)
        self.inviteCode = ""
        self.appname = "50091"
        self._help_num = None
        self.UA = self.jd_UA
        self.force_app_ck = True
        self.projectId = ''
        self.ProjectPoolId = ''
        self.giftProjectId = ''
        self.giftProjectPoolId = ''
        self.risk = False
        self.mofang_exchage = True
        self.Origin = "https://h5.m.jd.com"
        self.referer = "https://h5.m.jd.com/pb/010631430/2bf3XEEyWG11pQzPGkKpKX2GxJz2/index.html"

    def opt(self, opt):
        self.set_joyytoken()
        self.set_shshshfpb()
        _opt = {
            "method": "post",
            "api": "client.action",
            "log": False,
            "params": {
                "appid": "content_ecology",
                "client": "wh5",
                "clientVersion": "1.0.0",
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
            "sceneid": "XMFhPageh5"
        }
        body.update({"extParam": extParam})
        return f"body={quote(json.dumps(body, separators=(',', ':')))}"

    def getInteractionHomeInfo(self):
        body = {"sign": "u6vtLQ7ztxgykLEr"}
        opt = {
            "functionId": "getInteractionHomeInfo",
            "body": body,
            "log": True
        }
        status, res_data = self.jd_api(self.opt(opt))
        if res_data:
            if res_data['result'].get('giftConfig'):
                self.projectId = res_data['result']['taskConfig']['projectId']
                self.ProjectPoolId = res_data['result']['taskConfig']['projectPoolId']
                self.giftProjectId = res_data['result']['giftConfig']['projectId']
                self.giftProjectPoolId = res_data['result']['giftConfig']['projectPoolId']
            else:
                printf("获取projectId失败")
        else:
            print_api_error(opt, status)

    def queryInteractiveInfo(self, reward=False):
        try:
            body = {"encryptProjectId": self.projectId, "sourceCode": "acexinpin0823", "ext": {}}
            if reward:
                body = {
                    "encryptProjectId": self.giftProjectId,
                    "sourceCode": "acexinpin0823",
                    "ext": {"couponUsableGetSwitch": "1"}
                }
            opt = {
                "functionId": "queryInteractiveInfo",
                "body": body,
                'log': True
            }
            status, res_data = self.jd_api(self.opt(opt))
            # data = json.loads(res.data.decode())
            if res_data:
                return res_data['assignmentList']
            else:
                print_api_error(opt, status)
                return []
        except:
            print_trace()
            return []

    def doInteractiveAssignment(self, encryptAssignmentId, itemId, actionType=None, ext={}, reward=False,
                                completionFlag=""):
        try:
            body = {
                "encryptProjectId": self.projectId,
                "encryptAssignmentId": encryptAssignmentId,
                "sourceCode": "acexinpin0823",
                "itemId": itemId,
                "actionType": actionType,
                "completionFlag": completionFlag,
                "ext": ext,
            }
            if reward:
                body["encryptProjectId"] = self.giftProjectId
            opt = {
                "functionId": "doInteractiveAssignment",
                "body": body,
                "log": True
            }
            status, res_data = self.jd_api(self.opt(opt))
            if res_data:
                if reward:
                    if res_data.get("subCode") == "0":
                        if not res_data["rewardsInfo"]["successRewards"].get("3"):
                            printf(f"[{self.Name}]\t兑换成功")
                        else:
                            prize = res_data["rewardsInfo"]["successRewards"]["3"][0]["rewardName"]
                            printf(f"[{self.Name}]\t恭喜你抽中：" + prize)
                    elif res_data.get("subCode") == "103":
                        printf(f"[{self.Name}]\t已经兑换过了")
                    elif res_data.get("subCode") == "1703":
                        printf(f"[{self.Name}]\t{res_data['msg']}")
                    else:
                        print_api_error(opt, status)
                else:
                    printf(f"[{self.Name}]\t{res_data['msg']}")
                if res_data['msg'] == "兑换积分不足":
                    self.mofang_exchage = False
                if res_data['msg'] == "未登录":
                    self.mofang_exchage = False
                    self.risk = True
                if "火爆" in res_data['msg']:
                    self.risk = True
                if "风控" in res_data['msg']:
                    self.risk = True
                if "风险" in res_data['msg']:
                    self.risk = True
            else:
                print_api_error(opt, status)
        except:
            print_trace()

    def main(self):
        self.getInteractionHomeInfo()
        if not self.projectId:
            return
        taskList = self.queryInteractiveInfo()
        if taskList:
            for vo in taskList:
                if vo.get('encryptAssignmentId') == '44M5m7wZs5vDAMkaTmYXeppqTsZR' or (
                        vo.get("ext") and vo['ext'].get('extraType') != 'brandMemberList' and vo['ext'].get(
                        'extraType') != 'assistTaskDetail'):
                    if vo['completionCnt'] < vo['assignmentTimesLimit']:
                        if self.risk:
                            printf(f"[{self.Name}]\t黑号了，跳过该账号")
                            return
                        printf(
                            f"[{self.Name}]任务：{vo['assignmentName']}，进度：{vo['completionCnt']}/{vo['assignmentTimesLimit']}，去完成")
                        if vo.get('encryptAssignmentId') == '44M5m7wZs5vDAMkaTmYXeppqTsZR':
                            for i in range(vo['assignmentTimesLimit']):
                                randomWait(2, 1)
                                if vo['completionCnt'] < vo['assignmentTimesLimit']:
                                    self.doInteractiveAssignment(vo['encryptAssignmentId'], itemId=None, completionFlag=True)
                                    vo['completionCnt'] += 1
                        if vo['ext']:
                            if vo['ext']['extraType'] == 'sign1':
                                self.doInteractiveAssignment(vo['encryptAssignmentId'],
                                                             vo['ext']['sign1']['itemId'])

                        for vi in vo['ext'].get('productsInfo', []):
                            if self.risk:
                                printf(f"[{self.Name}]\t黑号了，跳过该账号")
                                return
                            if vi['status'] == 1 and vo['completionCnt'] < vo['assignmentTimesLimit']:
                                self.doInteractiveAssignment(vo['encryptAssignmentId'], vi['itemId'], 1)
                                vo['completionCnt'] += 1
                                randomWait(1, 3)

                        for vi in vo['ext'].get('shoppingActivity', []):
                            if self.risk:
                                printf(f"[{self.Name}]\t黑号了，跳过该账号")
                                return
                            if vi['status'] == 1 and vo['completionCnt'] < vo['assignmentTimesLimit']:
                                self.doInteractiveAssignment(vo['encryptAssignmentId'], vi['advId'], 1)
                                randomWait(vo['ext']['waitDuration'], 1)
                                if vo['ext']['waitDuration']:
                                    self.doInteractiveAssignment(vo['encryptAssignmentId'], vi['advId'], 0)
                                vo['completionCnt'] += 1

                        for vi in vo['ext'].get('browseShop', []):
                            if self.risk:
                                printf(f"[{self.Name}]\t黑号了，跳过该账号")
                                return
                            if vi['status'] == 1 and vo['completionCnt'] < vo['assignmentTimesLimit']:
                                self.doInteractiveAssignment(vo['encryptAssignmentId'], vi['itemId'], 1)
                                randomWait(vo['ext']['waitDuration'], 1)
                                if vo['ext']['waitDuration']:
                                    self.doInteractiveAssignment(vo['encryptAssignmentId'], vi['itemId'], 0)
                                vo['completionCnt'] += 1

                        for vi in vo['ext'].get('addCart', []):
                            if self.risk:
                                printf(f"[{self.Name}]\t黑号了，跳过该账号")
                                return
                            if vi['status'] == 1 and vo['completionCnt'] < vo['assignmentTimesLimit']:
                                self.doInteractiveAssignment(vo['encryptAssignmentId'], vi['itemId'], 1)
                                wait(500)
                                vo['completionCnt'] += 1
                        randomWait(2, 1)
                    else:
                        printf(
                            f"[{self.Name}]任务：{vo['assignmentName']}，进度：{vo['completionCnt']}/{vo['assignmentTimesLimit']}，已完成")
            else:
                printf(f"[{self.Name}]\t任务：做任务结束")
        else:
            printf(f'[{self.Name}]\t没有获取到活动信息')

        printf(f"\n[{self.Name}]\t开始魔方兑换")
        res = self.queryInteractiveInfo(True)
        for item in res:
            if self.risk:
                break
            randomWait(2, 1)
            if item["assignmentName"] == '魔方':
                i = -1
                while not self.risk and self.mofang_exchage:
                    randomWait(2, 1)
                    i += 1
                    self.doInteractiveAssignment(item['encryptAssignmentId'], "", "", {"exchangeNum": 1},
                                                 reward=True)
                printf(f"[{self.Name}]成功兑换魔方数量:\t{i}")
                continue
            prize = [prize_item["rewardName"] for prize_item in item['rewards']]
            printf(f"奖品：{'/'.join(prize)}:\t去兑换")
            if XmfRewardList == ['']:
                self.doInteractiveAssignment(item["encryptAssignmentId"], itemId='', ext={"exchangeNum": 1}, reward=True)
            else:
                if str(item["exchangeRate"]) in XmfRewardList:
                    self.doInteractiveAssignment(item["encryptAssignmentId"], itemId='', ext={"exchangeNum": 1}, reward=True)
                else:
                    printf(f"设置的不兑换")
        printf("\n\n")


if __name__ == '__main__':
    task = TaskClass("task")
    task.name = 'XMF'
    task.init_config(XMFUserClass)
    task.main("小魔方-任务")
