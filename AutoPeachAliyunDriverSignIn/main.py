import requests

from AutoPeachApi import Storage

URL_ACCESS_TOKEN = 'https://auth.aliyundrive.com/v2/account/token'
URL_SIGNIN_DAILY = 'https://member.aliyundrive.com/v1/activity/sign_in_list'


def update_access_token(account):
    refresh_token = account.get('refresh_token')
    headers = {'Content-Type': 'application/json'}
    payload = dict(grant_type='refresh_token', refresh_token=refresh_token)
    response = requests.post(URL_ACCESS_TOKEN, json=payload, headers=headers)
    rsp_json = response.json()
    if 'code' in rsp_json:
        if rsp_json['code'] in ['RefreshTokenExpired', 'InvalidParameter.RefreshToken']:
            return False, 'refresh_token 已过期或无效'
        else:
            return False, rsp_json['message']
    account['access_token'] = rsp_json.get('access_token')
    account['refresh_token'] = rsp_json.get('refresh_token', account.get('refresh_token'))
    account['nick_name'] = rsp_json.get('nick_name', account.get('nick_name'))
    return True, ''


def sing_in(account):
    msg = account.get('nick_name', '')
    if msg: msg += ' '
    access_token = account.get('access_token')
    refresh_token = account.get('refresh_token')
    headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
    payload = dict(grant_type='refresh_token', refresh_token=refresh_token)
    response = requests.post(URL_SIGNIN_DAILY, json=payload, headers=headers)
    rsp_json = response.json()
    if not rsp_json.get('success', False):
        msg += '签到失败'
        return False, msg
    msg += '签到成功'
    result = rsp_json.get('result', {})
    signInCount = result.get('signInCount', 0)
    signInLogs = result.get('signInLogs', [{}])
    msg += f'，本月累计签到 {signInCount} 天'
    currentSignInfo = signInLogs[signInCount - 1]
    reward = currentSignInfo.get('reward', {})
    if reward:
        reward_name = reward.get('name', '')
        reward_description = reward.get('description', '')
        if reward_name or reward_description:
            msg += f' 本次签到获得：{reward_name}{reward_description}'
    return True, msg


def main():
    for account in Storage('aliyun_driver').get_all():
        ok, msg = update_access_token(account)
        if not ok:
            continue
        ok, msg = sing_in(account)
        print(msg)
        Storage('aliyun_driver').save(account)


def add_account(refresh_token):
    Storage('aliyun_driver').save({'refresh_token': refresh_token})


if __name__ == '__main__':
    # add_account('***')
    main()
