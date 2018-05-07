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
        html = requests.get(url, verify=False)
        bs = BeautifulSoup(html.text, "html.parser")
        tables = bs.find(class_='right_cont')
        tables_a = tables.find_all("a")
        db = PickleShareDB('data')
        history_list = db.get("history_list", [])
        for row in tables_a:
            try:
                title = row["title"]
                url = "https://www.cdfangxie.com" + row["href"]
                # area = title.split("|")[0]
                # name = title.split("|")[1]
                # dic = {
                #     "area": title.split("|")[0],
                #     "name": title.split("|")[1]
                # }
                if title in history_list:
                    logger.info("Crawl:%s  result:pass", title)
                else:
                    logger.info("Crawl:%s  result:send_email", title)
                    if self.send_email(title, url):
                        logger.info("send_email success")
                        history_list.append(title)
                    else:
                        logger.info("send_email error")
            except:
                pass
        db["history_list"] = history_list

    def send_email(self, title, url):
        sender = 'pywechat@sina.com'
        receivers = ['zzyyshi@qq.com', 'pywechat@sina.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        # 第三方 SMTP 服务
        mail_host = "smtp.sina.com"  # 设置服务器
        mail_user = "pywechat@sina.com"  # 用户名
        mail_pass = "zywechat"  # 口令
        message = MIMEText("地址:{} \r\n\r\n\r\nFrom Joy's Python".format(url), 'plain', 'utf-8')
        message['From'] = Header(sender)
        message['To'] = Header(receivers[0], 'utf-8')
        message['Subject'] = Header(title, 'utf-8')
        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(mail_host, 25)
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
            return True
        except smtplib.SMTPException as e:
            logger.error(str(e))
            return False


if __name__ == "__main__":
    # Spider().get()
    Spider().send_email("x", "https://www.cdfangxie.com/Infor/index/id/4201.html")
