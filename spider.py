# File: spider
# Description:
# Created by joyyizhang on 2018/5/7.
# Version:python 3.6
import logging
from email.header import Header
from email.mime.text import MIMEText
import logging.handlers

import sys
from bs4 import BeautifulSoup
import smtplib
import requests
from pickleshare import PickleShareDB
from utils.header import getHeader
import etc.smtp_account as smtp_accounts

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
info_log = "log/spider_fxw.log"
info_file_handler = logging.handlers.RotatingFileHandler(
    info_log, maxBytes=50 * 1024 * 1024, backupCount=10, encoding="utf-8")
info_file_handler.setLevel(logging.INFO)
info_file_handler.setFormatter(
    logging.Formatter('%(asctime)s %(levelname)s: %(message)s '
                      '[in %(pathname)s:%(lineno)d]')
)
stream_handler = logging.StreamHandler(stream=sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(
    logging.Formatter('%(levelname)s %(asctime)s : %(message)s [%(filename)s:%(lineno)d]')
)
logger.addHandler(info_file_handler)
logger.addHandler(stream_handler)
logger = logging.getLogger(__name__)


class Spider:
    def get(self):
        url = "https://www.cdfangxie.com/Infor/type/typeid/36.html"
        html = requests.get(url, verify=False, headers=getHeader())
        bs = BeautifulSoup(html.text, "html.parser")
        tables = bs.find(class_='right_cont')
        tables_a = tables.find_all("a")
        db = PickleShareDB('data')
        history_list = db.get("history_list", [])
        smtpObj = self.get_smtp()
        for row in tables_a:
            try:
                title = row["title"]
                url = "https://www.cdfangxie.com" + row["href"]
                if title in history_list:
                    logger.info("Crawl:%s  result:pass", title)
                else:
                    logger.info("Crawl:%s  result:send_email", title)
                    if self.send_email(smtpObj, title, url):
                        logger.info("send_email success")
                        history_list.append(title)
                    else:
                        logger.info("send_email error")
            except:
                pass
        db["history_list"] = history_list
        smtpObj.quit()

    def send_email(self, smtpObj, title, url):
        sender = 'pywechat@sina.com'
        receivers = ['zzyyshi@qq.com', 'pywechat@sina.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        # 第三方 SMTP 服务
        message = MIMEText("地址:{} \r\n\r\n\r\nFrom Joy's Python".format(url), 'plain', 'utf-8')
        message['From'] = Header(sender)
        message['To'] = Header(receivers[0], 'utf-8')
        message['Subject'] = Header(title, 'utf-8')
        try:
            ans = smtpObj.sendmail(sender, receivers, message.as_string())
            logger.info(str(ans))
            return True
        except Exception as e:
            logger.error(str(e))
            return False

    def get_smtp(self, debug=False):
        for accounts in smtp_accounts.SMTP_ACCOUNT:
            logger.info("=============================================")
            logger.info("连接服务器 %s", accounts["smtp"])
            mail_host = accounts["smtp"]  # 设置服务器
            mail_user = accounts["name"]  # 用户名
            mail_pass = accounts["pwd"]  # 口令
            smtpObj = smtplib.SMTP_SSL(mail_host)
            try:
                ans = smtpObj.login(mail_user, mail_pass)
                if ans[0] == 235 or ans[0] == 503:
                    logger.info("登录成功")
                else:
                    logger.info("登录失败:%s %s", ans[0],
                                str(ans[1]))  # 235 == 'Authentication successful' 503 == 'Error: already authenticated'
                if debug:
                    logger.info("测试成功：%s", mail_user)
                else:
                    return smtpObj
            except Exception as e:
                logger.info("测试服务器失败%s", str(e))
        return False


if __name__ == "__main__":
    # Spider().get_smtp(debug=True)
    Spider().get()
