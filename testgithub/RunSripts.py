# coding:utf-8
from selenium import webdriver
import time
import os
import datetime
import smtplib
from email.mime.text import MIMEText
import ConfigParser
import zipfile
from email.mime.application import MIMEApplication
import email.mime.multipart
import email.mime.text


class conf_git():

    def ini_list(self,value):
        w_len = len(value)
        str_o = w_len - 1
        value_str = value.replace(value[0], '')
        value = value_str.replace(value[str_o], '')
        value_list = value.split(',')
        return value_list

    def _take_dict(self):

        cf = ConfigParser.ConfigParser()

        cf.read('github.ini')

        save_body={
            "name":None,
            "pwd":None,
            "Warehouse":None,
            "SensitiveKey":None,
            "from_email":None,
            "to_email":None

             }
        try:
            login_usr=cf.get("login","usr")
            login_pwd = cf.get("login", "pwd")
            from_email = cf.get("email", "from_email")
            from_email_list=self.ini_list(from_email)

            to_email = cf.get("email", "to_email")
            to_email_list = self.ini_list(to_email)




            # 读需要搜索的仓库转换list
            Warehouse = cf.get("Warehouse", "Warehouse_list")
            Warehouse_list=self.ini_list(Warehouse)

            # 需要搜索的敏感关键字
            SensitiveKey = cf.get("SensitiveKey", "keyWord_list")
            SensitiveKey_list = self.ini_list(SensitiveKey)

            save_body['name']=login_usr
            save_body['pwd'] = login_pwd
            save_body['Warehouse'] = Warehouse_list
            save_body['SensitiveKey'] = SensitiveKey_list

            save_body['from_email']=from_email_list

            save_body['to_email'] = to_email_list
            conf_dic=save_body
        except Exception as errorLog:
            print("读写错误，文件配置没有找到或没有匹配项")
            return False
        else:

                return conf_dic
        finally:
            pass

class _serch_git(conf_git):
    def __init__(self):
        conf_dic=self._take_dict()
        self.Warehouse_list=conf_dic['Warehouse']
        self.SensitiveKey_list = conf_dic['SensitiveKey']

        self.name=conf_dic['name']
        self.pwd = conf_dic['pwd']

        self.from_email=conf_dic['from_email']
        self.to_email = conf_dic['to_email']


    def get_time(self):
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 现在
        nowTime = str(nowTime)
        nowTime_str = nowTime.replace(' ', '')
        nowTime = nowTime_str.replace(':', '-')
        yymm = nowTime[0:10]
        hhmm = nowTime[10:]
        file_time=yymm + '-' + hhmm
        nowTime='reportIMG'+yymm + '-' + hhmm

        return nowTime,file_time

    def mkdir_file(self):
        nowTime = self.get_time()[0]
        for dir_f in self.Warehouse_list:
            for dir_key in self.SensitiveKey_list:
                if '/' in dir_f:
                    dir_f=dir_f.replace('/','$')
                else:
                    pass
                pr_files = nowTime + '/' + dir_f + '/' + dir_key
                os.makedirs(pr_files)

        return nowTime

    def _login_git_serch(self):
        file_master=self.mkdir_file()
        self.Warehouse_lists=self.Warehouse_list
        self.SensitiveKey_lists=self.SensitiveKey_list
        driver = webdriver.Firefox()
        driver.get('https://github.com/login')
        driver.maximize_window()
        driver.find_element_by_id('login_field').send_keys(self.name)
        driver.find_element_by_id('password').send_keys(self.pwd)
        driver.find_element_by_name('commit').click()
        time.sleep(3)
        _current_file=os.path.split(os.path.realpath(__file__))[0]
        file = self.get_time()[1]
        for Warehouse in self.Warehouse_lists:
            git_url = 'https://github.com/' + Warehouse
            for SensitiveKey in self.SensitiveKey_lists:
                git_urls = git_url+ '/search?q=' + SensitiveKey + '&unscoped_q=' + SensitiveKey
                driver.get(git_urls)
                # time.sleep(1)
                if '/' in Warehouse:
                    Warehouse_file=Warehouse.replace('/','$')
                else:
                    Warehouse_file=Warehouse
                try:
                    all_page_ele = driver.find_element_by_xpath('//*[@id="code_search_results"]/div[2]/div/em')
                    all_page = all_page_ele.get_attribute('data-total-pages')

                    # print(all_page)
                except:
                    # print (unicode('只有一页数据：', 'utf-8'))
                    # driver.save_screenshot(_current_file + '\\' +file_master+ '\\'+Warehouse_file + '\\'+SensitiveKey +'\\'+ file + '.png')
                    driver.save_screenshot(_current_file + '\\' + file_master + '\\' + Warehouse_file + '\\' + SensitiveKey + '\\' + Warehouse_file+ SensitiveKey+ '1.png')
                    # print (unicode('截图完成：', 'utf-8'))
                else:
                    true_ele = str(all_page)
                    # print(true_ele)
                    true_ele_int = int(true_ele)
                    # print(true_ele_int)

                    for pages in range(1,true_ele_int+1):
                        file = self.get_time()[1]
                        driver.get('https://github.com/' + Warehouse + '/search?p=' + str(pages) + '&q=' + SensitiveKey + '&type=&utf8=%E2%9C%93')
                        # driver.save_screenshot(_current_file + '\\' +file_master+ '\\'+Warehouse_file + '\\'+SensitiveKey +'\\'+ file + '.png')
                        driver.save_screenshot(
                            _current_file + '\\' + file_master + '\\' + Warehouse_file + '\\' + SensitiveKey + '\\' + Warehouse_file + SensitiveKey +str(pages)+ '.png')
                        # print(_current_file + '\\' +file_master+ Warehouse_file + '\\'+SensitiveKey +'\\'+ file + '.png')
                        # print a
                finally:
                    pass
        driver.quit()
        print (unicode('指定仓库根据指定的关键字已截图完成', 'utf-8'))
        return file_master

class sendEmail(_serch_git):

        def send_forUsr(self):

            file_name=self._login_git_serch()
            if ""  in self.to_email:
                print (unicode('脚本执行完成:', 'utf-8'))


            else:

                print (unicode('正在打包发送邮件：', 'utf-8'))
                f = zipfile.ZipFile(file_name + '.zip', 'w', zipfile.ZIP_DEFLATED)
                startdir = file_name
                for dirpath, dirnames, filenames in os.walk(startdir):
                    for filename in filenames:
                        f.write(os.path.join(dirpath, filename))

                time.sleep(3)


                # 发送邮件
                self.mailserver = 'smtp.mxhichina.com'
                self.username_send = self.from_email[0]
                self.password = self.from_email[1]
                self.user_list = self.to_email
                # 主题
                subject = 'Github敏感关键字自动化搜索测试报告[附件]'
                # 内容
                content = '具体截图请查收附件'
                for usr in self.user_list:
                    msg = email.mime.multipart.MIMEMultipart()
                    msg['from'] = self.username_send
                    msg['to'] = usr
                    msg['subject'] = subject
                    content = content
                    txt = email.mime.text.MIMEText(content, 'plain', 'utf-8')
                    msg.attach(txt)

                    # 添加附件
                    part = MIMEApplication(open(file_name+'.zip', 'rb').read())
                    part.add_header('Content-Disposition', 'attachment', filename=file_name+'.zip')
                    msg.attach(part)
                    time.sleep(3)

                    smtp = smtplib.SMTP()
                    smtp.connect(self.mailserver, '25')
                    smtp.login(self.username_send, self.password)
                    try:
                         smtp.sendmail(self.username_send, usr, str(msg))
                    except:
                        print (unicode('邮件未发送', 'utf-8'))
                    else:
                        print (unicode('邮件发送成功', 'utf-8'))
                    finally:
                        smtp.quit()



if __name__ =="__main__":
    sendEmail().send_forUsr()
else:
    pass