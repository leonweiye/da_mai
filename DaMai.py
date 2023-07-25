import os
import time
import pickle
from time import sleep
from selenium.webdriver.common.by import By
# from selenium import webdriver
from selenium.webdriver import ActionChains
import undetected_chromedriver as webdriver

# 大麦网主页
damai_url = "https://www.damai.cn/"
# 登录页
login_url = "https://passport.damai.cn/login?ru=https%3A%2F%2Fwww.damai.cn%2F"
# todo 抢票目标页
target_url = 'https://detail.damai.cn/item.htm?id=727437709222'
# ssss
class Concert:
    def __init__(self):
        self.status = 0  # 状态,表示如今进行到何种程度
        self.login_method = 1  # {0:模拟登录,1:Cookie登录}自行选择登录方式
        self.driver = webdriver.Chrome()  # 默认谷歌浏览器

    def set_cookie(self):
        self.driver.get(damai_url)
        print("###请点击登录###")
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:
            sleep(1)
        print('###请扫码登录###')

        while self.driver.title != '大麦网-全球演出赛事官方购票平台-100%正品、先付先抢、在线选座！':
            sleep(1)
        print("###扫码成功###")
        pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
        print("###Cookie保存成功###")
        self.driver.get(target_url)

    # 获取cookie
    def get_cookie(self):
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))  # 载入cookie
            for cookie in cookies:
                cookie_dict = {
                    'domain': '.damai.cn',  # 必须有，不然就是假登录
                    'name': cookie.get('name'),
                    'value': cookie.get('value')
                }
                self.driver.add_cookie(cookie_dict)
            print('###载入Cookie###')
        except Exception as e:
            print(e)

    # 登录
    def login(self):
        if self.login_method == 0:
            self.driver.get(login_url)
            # 载入登录界面
            print('###开始登录###')

        elif self.login_method == 1:
            if not os.path.exists('cookies.pkl'):
                # 如果不存在cookie.pkl,就获取一下
                self.set_cookie()
            else:
                self.driver.get(target_url)
                self.get_cookie()

    # 打开浏览器
    def enter_concert(self):
        """打开浏览器"""
        print('###打开浏览器，进入大麦网###')
        # self.driver.maximize_window()           # 最大化窗口
        # 调用登陆
        self.login()  # 先登录再说
        self.driver.refresh()  # 刷新页面
        self.status = 2  # 登录成功标识
        print("###登录成功###")
        # 后续德云社可以讲
        # if self.isElementExist('/html/body/div[2]/div[2]/div/div/div[3]/div[2]'):
        #     self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div/div[3]/div[2]').click()

    # 判断元素是否存在
    def isElementExist(self, element):
        flag = True
        browser = self.driver
        try:
            browser.find_element(by=By.XPATH, value=element)
            return flag

        except:
            flag = False
            return flag

    # 选票操作
    def choose_ticket(self):
        if self.status == 2:  # 登录成功入口
            print("=" * 30)
            print("###开始进行日期及票价选择###")
            # sleep(20)
            # print(self.driver.title.find('订单确认页'))
            # print(self.isElementExist("//span[text()='提交订单']"))

        while self.driver.title.find('订单确认页') == -1:  # 如果跳转到了订单结算界面就算这步成功了，否则继续执行此步

            # todo 修改抢票数量 num(抢票数量)
            # num = 1
            # num_input = self.driver.find_element(by=By.CLASS_NAME, value='cafe-c-input-number-handler-up')
            # for i in range(num-1):
            #     num_input.click()


            # todo 修改票档 sku_item_name(票档) 模糊匹配
            sku_item_name = "VIP票"
            sku_item_button_list = self.driver.find_elements(by=By.CLASS_NAME, value='sku_item')
            for sku_item_button in sku_item_button_list:
                if sku_item_name in sku_item_button.text:
                    sku_item_button.click()

            # todo 抢票
            try:
                try:
                    buy_button = self.driver.find_element(by=By.CLASS_NAME, value='buy-link')
                    buy_button_name = buy_button.text
                except:
                    buy_button = self.driver.find_element(by=By.CLASS_NAME, value='buybtn')
                    buy_button_name = buy_button.text
                print(buy_button_name)
                if buy_button_name == "提交缺货登记":
                    # 改变现有状态
                    self.status = 2
                    self.driver.get(target_url)
                    print('###抢票未开始，刷新等待开始###')
                    continue
                elif buy_button_name == "预约抢票":
                    # 改变现有状态
                    self.status = 2
                    self.driver.get(target_url)
                    print('###抢票未开始，刷新等待开始###')
                    continue
                elif buy_button_name == "立即预定":
                    buy_button.click()
                    # 改变现有状态
                    self.status = 3
                elif buy_button_name == "立即购买":
                    buy_button.click()
                    # 改变现有状态
                    self.status = 4
                # 选座购买暂时无法完成自动化
                elif buy_button_name == "选座购买":
                    buy_button.click()
                    self.status = 5
                elif buy_button_name == "不，立即购买":
                    buy_button.click()
                    self.status = 6
            except:
                print('###未跳转到订单结算界面###')
            title = self.driver.title
            if title == '选座购买':
                # 实现选座位购买的逻辑
                self.choice_seats()
            elif title == '订单确认页':
                while True:
                    # 如果标题为确认订单
                    print('waiting ......')
                    if self.isElementExist("//span[text()='提交订单']"):
                        self.check_order()
                        break

    # 选择座位
    def choice_seats(self):
        while self.driver.title == '选座购买':
            while self.isElementExist('//*[@id="app"]/div[2]/div[2]/div[1]/div[2]/img'):
                # 座位手动选择 选中座位之后//*[@id="app"]/div[2]/div[2]/div[1]/div[2]/img 就会消失
                print('请快速的选择您的座位！！！')
            # 消失之后就会出现 //*[@id="app"]/div[2]/div[2]/div[2]/div
            while self.isElementExist('//*[@id="app"]/div[2]/div[2]/div[2]/div'):
                # 找到之后进行点击确认选座
                self.driver.find_element(by=By.XPATH, value='//*[@id="app"]/div[2]/div[2]/div[2]/button').click()

    # 下单
    def check_order(self):
        if self.status in [3, 4, 5, 6]:
            print('###开始确认订单###')
            try:
                # 默认选第一个购票人信息
                element1 = self.driver.find_element(by=By.XPATH,
                                                   value='//div[@id = "dmViewerBlock_DmViewerBlock"]//div[2]//div//div[1]//div[3]')

                self.driver.execute_script("arguments[0].click()", element1)

                # todo 抢两个人票开启
                # # 第二个
                # element2 = self.driver.find_element(by=By.XPATH,
                #                                    value='//div[@id = "dmViewerBlock_DmViewerBlock"]//div[2]//div//div[2]//div[3]')
                # self.driver.execute_script("arguments[0].click()", element2)


                name_input = self.driver.find_element(by=By.XPATH,
                                         value='//div[@id = "dmContactBlock_DmContactBlock"]//div[2]//div//div//input')
                data = name_input.get_attribute("value")
                # todo 联系人名称
                contact_name = "联系人名称"
                if data is None:
                    name_input.send_keys(contact_name)
                else:
                    print(data)
                # self.driver.find_element(by=By.XPATH,
                #                          value='//div[@id = "dmViewerBlock_DmViewerBlock"]//div[2]//div//div//div[3]').click()

            except Exception as e:
                print("###购票人信息选中失败，自行查看元素位置###")
                print(e)
            # 最后一步提交订单
            time.sleep(0.5)  # 太快会影响加载，导致按钮点击无效
            print("提交订单成功")
            # todo 提交订单
            # self.driver.find_element(by=By.XPATH,
            #                          value="//span[text()='提交订单']").click()

    def finish(self):
        self.driver.quit()


if __name__ == '__main__':
    try:
        con = Concert()  # 具体如果填写请查看类中的初始化函数
        con.enter_concert()  # 打开浏览器
        con.choose_ticket()  # 开始抢票
        sleep(100)
    except Exception as e:
        print(e)
        con.finish()
