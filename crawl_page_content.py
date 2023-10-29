from selenium import webdriver
import pymysql
import warnings
from time import strptime, mktime, sleep as sl 
import socket
from lxml import etree
from User_Agents import user_agents
import csv
from datetime import datetime as dt  



class URLCrawl(object):
    def __init__(self):
        self.sockfd = socket.socket()
        self.server_addr = ('127.0.0.1', 8000)
        self.db = pymysql.connect(host="localhost", user="root", password="bb0937508578", charset="utf8")
        self.cursor = self.db.cursor()

    def getUrl(self):
        sockfd.connect(server_addr)
        sl(1)

        data = input("是否開始爬取(y/n)")
        if data.strip().lower() == "y":
            while True:
                #發送消息
                sl(0.5)
                sockfd.send("y".encode())

                data = sockfd.recv(1024).decode()
                if data == "##":
                    print("url已全部爬取完畢")
                    break
                print("接收到：",data)
                self.parseHtml(data)

                #如存儲成功，紀錄在csv文件裡
                with open("crawlURL.csv", "a+", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([dt.now(), date, "success"])
    
    #設置初始chromedriver選項
    def changeUA(self):
        # 設置無介面瀏覽
        opt = webdriver.ChromeOptions()
        opt.set_headless()
        #設置隨機user-agent
        opt.add_argument('user-agent=' + random.choice(user_agents))
        self.driver = webdriver.Chrome(options=opt)
    
    #解析頁面
    def parseHtml(self, data):
        self.changeUA()
        self.driver.get(data)
        sl(0.5)


        #判斷是否到年齡分級規定處理的頁面
        if self.driver.page_source.find("btn-big") != -1:
            #18年齡限制的按鈕
            btn = self.driver.find_element_by_class_name('btn-big')
            btn.click()
            sl(0.5)
        
        #作者編號，作者暱稱
        authorId, authorName = self.driver.find_element_by_xpath('//div[@id="main-content"]/div[1]').text.split(' ')
        authorId = authorId[2:]
        authorName = authorName[1:-1]
        #標題
        title = self.driver.find_element_by_xpath('//div[@id="main-content"]/div[3]').text.split(' ')[-1]
        #文章分類
        postCls = self.driver.find_element_by_xpath('//div[@id="main-content"]/div[2]').text[2:]
        

        html = self.driver.page_source
        #使用lxml的etree獲取文章內容
        parseHtml = etree.HTML(html)
        #文章內容
        content = parseHtml.xpath('//div[@id="main-content"]/text()')[0].strip()

        
        date = self.driver.find_element_by_xpath('//div[@id="main-content"]/div[4]/span[2]').text
        #轉成時間數組
        dateArray = strptime(date, "%a %b %d %H:%M:%S %Y")
        
        #發布時間轉成時間撮
        publishedTime = mktime(dateArray)
        
        #貼文網址
        canonicalUrl = data
        
        postDataList = [authorId, authorName, title, postCls, content, publishedTime, canonicalUrl]
        self.saveToPostData(postDataList)
        
        
        #推文者的div[a]初始值
        a = 5
        while True:
            try:
                comment = self.driver.find_element_by_xpath('//div[@id="main-content"]/div[' + str(a) + ']/span[4]')
                break
            except Exception:
        	    a += 1
        
        commentTotal = len(self.driver.find_elements_by_xpath('//div[@id="main-content"]/div/span[4]'))
        for i in range(0, commentTotal):
            #推文者編號
            commentId = self.driver.find_element_by_xpath('//div[@id="main-content"]/div[' + str(a + i) + ']/span[2]').text
            #推文者內容
            commentContent = self.driver.find_element_by_xpath('//div[@id="main-content"]/div[' + str(a + i) + ']/span[3]').text[2:]
            #推文者發布時間
            commentTime =  self.driver.find_element_by_xpath('//div[@id="main-content"]/div[' + str(a + i) + ']/span[4]').text.split(' ')
            #組合成'202002/0417:59'格式（年月/日分:秒)
            commentTime = date.split(' ')[-1] + commentTime[-2] + commentTime[-1] 
            #轉成時間數組
            commentTime = strptime(commentTime, '%Y%m/%d%M:%S')
            #轉成時間撮
            commentTime = mktime(commentTime)

            commentDataList = [commentId, commentContent, commentTime, data]

            self.saveToCommentData(commentDataList)

    #創建數據庫，存進貼文表
    def saveToPostData(self, postDataList):
        c_db = "create database if not exists PTT default charset utf8"
        c_use = "use PTT"
        
        #貼文表
        c_tab = "create table if not exists postData(\
                  id int primary key auto_increment,\
                  authorId varchar(20),\
                  authorName varchar(20),\
                  title varchar(50),\
                  postCls varchar(20),\
                  content text,\
                  publishedTime varchar(20),\
                  canonicalUrl varchar(100),\
                  createTime datetime,\
                  updateTime datetime\
                  )charset=utf8"
        
        ins = "insert into postData(authorId, authorName, title, postCls, content, publishedTime,\
               canonicalUrl, createTime, updateTime) values(%s, %s, %s, %s, %s, %s, %s, now(), now())"
        
        #過濾警告
        warnings.filterwarnings("ignore")
        try:
            self.cursor.execute(c_db)
        except Warning:
            pass
        self.cursor.execute(c_use)
        try:
            self.cursor.execute(c_tab)
        except Warning:
            pass
        self.cursor.execute(ins, postDataList)
        self.db.commit()
        print("存入貼文表成功！")
        
    #存進評論表
    def saveToCommentData(self, commentDataList):
        #評論表
        c_tab = "create table if not exists commentData(\
                  postId int,\
                  commentId varchar(20),\
                  commentContent varchar(500),\
                  commentTime varchar(20),\
                  createTime datetime,\
                  updateTime datetime,\
                  foreign key(postId) references postData(id) on delete cascade on update cascade\
                  )charset=utf8"
        
        ins = "insert into commentData(postId, commentId, commentContent, commentTime, createTime, updateTime) \
                values(%s, %s, %s, %s, now(), now())"
        
        #過濾警告
        warnings.filterwarnings("ignore")
        try:
            self.cursor.execute(c_tab)
        except Warning:
            pass
        #購過查找條件URL得到此貼文的主鍵
        postSelect = "select id from postData where canonicalUrl='" + commentDataList[-1] + "'"
        self.cursor.execute(postSelect)  
        postId = self.cursor.fetchone()[0]

        self.cursor.execute(ins, [postId] + commentDataList[0:3])
        self.db.commit()
        print("存入評論表成功!")


    def workOn(self):
        self.getUrl()
        self.parseHtml()

        #關閉套接字
        self.sockfd.close()
        self.cursor.close()
        self.db.close()

if __name__ == "__main__":
    spider = URLCrawl()
    spider.workOn()