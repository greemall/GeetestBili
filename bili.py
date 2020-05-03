# !usr/bin/env python
# -*- conding:utf-8 -*-

'''
@project:验证码
@fileName:极验滑块.py
@date:2020/4/28 22:36
@author:tian
'''

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
import time
from PIL import Image
from io import BytesIO

USER = 'username'
PASSWORD = 'word'
URL = 'https://passport.bilibili.com/login'
BORDER = 6

class BiLi():
    '''初始化'''
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.url = URL
        self.wait = WebDriverWait(self.driver,30)
        self.user = USER
        self.password = PASSWORD

    def __del__(self):
        '''自动销毁对象
        class count():
            def __init__(self,name):
                self.name = name
                print('******')
            def __del__(self):
                print(f'删除{self.name}')
        c =count('apple')
        print('------')
        input:del c
        ******
        删除apple
        ------
        '''
        self.driver.close()

    def get_login_button(self):
        '''获取登录点击按钮'''
        login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.btn.btn-login')))
        return login_button

    def get_position(self):
        '''获取验证图片位置'''
        img = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.geetest_canvas_img')))
        time.sleep(2)
        location = img.location
        size = img.size
        top,bottom,left,right = location['y'],location['y'] + size['height'],location['x'],location['x'] + size['width']
        return (top,bottom,left,right)

    def get_full_img(self):
        '''js语句获取不带缺口图片'''
        js = 'document.getElementsByClassName("geetest_canvas_fullbg")[0].setAttribute("style","")'
        self.driver.execute_script(js)

    def recover_img(self):
        '''恢复带缺口图片'''
        js = 'document.getElementsByClassName("geetest_canvas_fullbg")[0].setAttribute("style","display: none;")'
        self.driver.execute_script(js)
    def get_screenshot(self):
        '''获取页面截图'''
        screenshot = self.driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        # driver.get_screenshot_as_file('bili.png')
        return screenshot

    def get_slider(self):
        '''获取滑块'''
        slider = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.geetest_slider_button')))
        return slider

    def get_bili_image(self,name='bili_obj.png'):
        '''对滑块验证码进行切图'''
        top,bottom,left,right  = self.get_position()
        print('验证码位置：',top,bottom,left,right)
        screenshot = self.get_screenshot()
        region = screenshot.crop((left*1.25,top*1.25,right*1.25,bottom*1.25))
        region.save(name)
        return region

    def open_url(self):
        '''输入账号密码登录'''
        self.driver.get(self.url)
        user = self.wait.until(EC.presence_of_element_located((By.ID, 'login-username')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'login-passwd')))
        user.send_keys(self.user)
        password.send_keys(self.password)

    def get_offerst(self,image1,image2):
        '''
        获取偏移量
        :param image1: 带缺口图片bili.jpg
        :param image2: 完整图片bili_full.jpg
        :return:
        '''
        left = 20
        for i in range(left,image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_piexl_equal(image1,image2,i,j):
                    left = i
                    return left
        return left

    def is_piexl_equal(self,image1,image2,x,y):
        '''
        比较两个像素值，piexl = image.laod()[x,y]输出元组
        :param image1:带缺口图片
        :param image2:完整图片
        :param x:x轴像素
        :param y:y轴像素
        :return:像素是否相等
        '''
        piexl_one = image1.load()[x,y]
        piexl_two = image2.load()[x,y]
        threshold = 40
        if abs(piexl_one[0]-piexl_two[0]) < threshold and abs(piexl_one[1]-piexl_two[1]) <threshold and abs(piexl_one[2]-piexl_two[2]) <threshold and abs(piexl_one[3]-piexl_two[3])< threshold:
            return True
        else:
            return False

    def get_track(self,distance):
        '''
        获取移动轨迹列表，时间间隔t
        :param distance:偏移量
        :return:移动轨迹
        '''
        track = []
        # 当前距离
        current = 0
        # 减速阈值
        mid =4/5*distance
        # 单位间隔
        t = 0.2
        # 初始速度
        v = 0

        while current < distance:
            if current < mid:
                a = 2
            else:
                a = -3
            v0 = v
            v = v0 + a * t
            move = v0 * t + 0.5 * a * t* t
            current += move
            track.append(round(current))
        return track

    def move_to_gap(self,slider,track):
        '''
        拖动滑块到缺口
        :param slider:滑块
        :param track:轨迹
        :return:
        '''
        ActionChains(self.driver).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.driver).move_by_offset(xoffset=x,yoffset=0).perform()
        time.sleep(1)
        ActionChains(self.driver).release().perform()

    def login(self):
        '''点击登录'''
        submit = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'btn-login')))
        submit.click()
        print('登录成功')

    def crack(self):
        '''输入用户名密码'''
        self.open_url()
        '''点击登录，呼出滑块'''
        button = self.get_login_button()
        button.click()
        '''获取带缺口图片'''
        image1 = self.get_bili_image('bili.png')
        '''获取完整图片'''
        self.get_full_img()
        image2 = self.get_bili_image('bili_full.png')
        '''恢复带缺口图片'''
        self.recover_img()
        '''获取缺口位置'''
        gap = self.get_offerst(image1,image2)
        gap -= BORDER
        '''获取运动轨迹'''
        track = self.get_track(gap)
        print(f'滑动轨迹{track}')
        '''拖动滑块'''
        slider = self.get_slider()
        self.move_to_gap(slider,track)
        success = self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'.geetest_success_radar_tip_content'),'验证成功'))
        print(success)
        time.sleep(1)
        if not success:
            self.login()
        else:
            self.crack()
if __name__ == '__main__':
    c = BiLi()
    c.crack()












