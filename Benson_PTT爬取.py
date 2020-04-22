from selenium import webdriver
from time import sleep as sl 
import datetime as dt 
import redis 
from socket import *
from threading import Thread 
import sys 
import traceback
from User_Agents import user_agents
import random
import csv




class PttCrawl(object):
    def __init__(self):
        self.url = "https://www.ptt.cc/bbs/index.html"
        self.postRedis = redis.Redis(host="localhost", port=6379, decode_responses=True)
        self.addr = ('127.0.0.1', 8000)
        #創建套接字
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.sockfd.bind(self.addr)
        self.ip = self.addr[0]
        self.port = self.addr[1]

    
    #設置初始chromedriver選項
    def changeUA(self):
        # 設置無介面瀏覽
        opt = webdriver.ChromeOptions()
        opt.set_headless()
        #設置隨機user-agent
        opt.add_argument("user-agent=" + random.choice(user_agents))
        self.driver = webdriver.Chrome(options=opt)


    #獲取頁面
    def getPage(self):
        self.changeUA()
        self.driver.get(self.url)
        sl(0.5)
        #點選分類看板
        self.driver.find_element_by_xpath('//div[@id="action-bar-container"]/div/div/a[2]').click()
        sl(0.5)
    
    #解析頁面
    def parsePage(self):
        #分類看板的url
        groupsUrl = self.driver.current_url
        #存放各組別內的第一層url列表
        firstLayerUrlList = []
        #存放各組別內的第二層url列表
        secondLayerUrlList = []
        #存放各組別內的第三層url列表
        thirdLayerUrlList = []
        #存放各組別內的第四層url列表
        fourthLayerUrlList = []
        #存放各組別內的第五層url列表
        fifthLayerUrlList = []
        #存放各組別內的第六層url列表
        sixthLayerUrlList = []
        #存放各組別內的第七層url列表
        seventhLayerUrlList = []
        #存放各組別內的第八層url列表
        eighthLayerUrlList = []

        #遍歷分類看版的各組別(共11個組別)
        for g in range(0, 11):
            if g == 0:
                #將爬取狀態存進csv文件
                with open("crawlStatus.csv", "a+", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["date", "status"])
            self.changeUA()
            self.driver.get(groupsUrl)
            sl(0.5)
            #找到組別元素(從第一個開始)
            group = self.driver.find_element_by_xpath('//div[@id="main-container"]/div[2]/div[' + str(g + 1) + ']')
            group.click()
            sl(0.5)
            #將各組別的第一層url加入到列表裡
            firstLayerUrlList.append(self.driver.current_url)
            #各組別內的第一層的總分類元素
            firstLayerTotal = self.driver.find_elements_by_xpath('//div[@id="main-container"]/div[2]/div')
            
            #遍歷各組別的第一層
            for o in range(0, len(firstLayerTotal)):
                secondLayerTotal = self.forLayerCheck(o, firstLayerUrlList, secondLayerUrlList)
                if secondLayerTotal == "This page is None":
                    continue
                elif secondLayerTotal == "Final":
                    self.parsePost()
                    continue            
            
                #遍歷各組別的第二層
                for s in range(0, len(secondLayerTotal)):
                    thirdLayerTotal = self.forLayerCheck(s, secondLayerUrlList, thirdLayerUrlList)
                    if thirdLayerTotal == "This page is None":
                        continue
                    elif thirdLayerTotal == "Final":
                        self.parsePost()
                        continue
                    elif thirdLayerUrlList == "0ClassRoot":
                        continue    

                    #遍歷各組別的第三層
                    for t in range(0, len(thirdLayerTotal)):
                        fourthLayerTotal = self.forLayerCheck(t, thirdLayerUrlList, fourthLayerUrlList)
                        if fourthLayerTotal == "This page is None":
                            continue
                        elif fourthLayerTotal == "Final":
                            self.parsePost()
                            continue
                        
                        #遍歷各組別的第四層
                        for fo in range(0, len(fourthLayerTotal)):
                            fifthLayerTotal = self.forLayerCheck(fo, fourthLayerUrlList, fifthLayerUrlList)
                            if fifthLayerTotal == "This page is None":
                                continue
                            elif fifthLayerTotal == "Final":
                                self.parsePost()
                                continue
                            
                            #遍歷各組別的第五層
                            for fif in range(0, len(fifthLayerTotal)):
                                sixthLayerTotal = self.forLayerCheck(fif, fifthLayerUrlList, sixthLayerUrlList)
                                if sixthLayerTotal == "This page is None":
                                    continue
                                elif sixthLayerTotal == "Final":
                                    self.parsePost()
                                    continue
                
                                #遍歷各組別的第六層
                                for six in range(0, len(sixthLayerTotal)):
                                    seventhLayerTotal = self.forLayerCheck(six, sixthLayerUrlList, seventhLayerUrlList)
                                    if seventhLayerTotal == "This page is None":
                                        continue
                                    elif seventhLayerTotal == "Final":
                                        self.parsePost()
                                        continue
                                    
                                    #遍歷各組別的第七層
                                    for sev in range(0, len(seventhLayerTotal)):
                                        eighthLayerTotal = self.forLayerCheck(sev, seventhLayerUrlList, eighthLayerUrlList)
                                        if eighthLayerTotal == "This page is None":
                                            continue
                                        elif eighthLayerTotal == "Final":
                                            self.parsePost()
                                            continue


    #遍歷組別
    def forLayerCheck(self, num, currentLayerUrlList, nextLayerUrlList):
        self.changeUA()
        self.driver.get(currentLayerUrlList[-1])
        layerElement = self.driver.find_element_by_xpath('//div[@id="main-container"]/div[2]/div[' + str(num + 1) + ']')
        clasRoot = self.driver.find_element_by_xpath('//div[@id="main-container"]/div[2]/div[' + str(num + 1) + ']/a/div[1]').text
        #因0ClassRoot為看板分類目錄，故需忽略
        if clasRoot == "0ClassRoot":
            return "0ClassRoot"
        layerElement.click()
        sl(0.5)

        #判斷是否到年齡分級規定處理的頁面
        if self.driver.page_source.find("btn-big") != -1:
            #18年齡限制的按鈕
            btn = self.driver.find_element_by_class_name('btn-big')
            btn.click()
            sl(0.5)

        #將各組別的第n層url加入到列表裡
        nextLayerUrlList.append(self.driver.current_url)
        try:
            #各組別內的第n層的總分類元素，如果沒有這個元素，代表此頁面為空
            nextLayerTotal = self.driver.find_elements_by_xpath('//div[@id="main-container"]/div[2]/div')
        except Exception as e:
            self.crawlStatus(e)
            return "This page is None"
        try:
            #獲取第n層貼文列表的日期，如果有這個元素，代表已經到貼文列表頁
            nextLayerDate = self.driver.find_element_by_xpath('//div[@id="main-container"]/div[2]/div[2]/div[3]/div[3]')
            return "Final"
        except Exception as e:
            self.crawlStatus(e)
        return nextLayerTotal
    

    #解析貼文
    def parsePost(self):
        #定義存放url的列表
        urlList = []
        urlList.append(self.driver.current_url)
        #url列表索引初始值
        urlIndex = 0

        #獲取此頁面的所有貼文元素
        postTotal = self.driver.find_elements_by_xpath('//div[@id="main-container"]/div[2]/div/div[2]/a') 
        # 因在最新貼文的下方如板規公告等等，不進行擷取，故循環偵測，假設有異常代表已到最新貼文
        for postNum in range(len(postTotal), 1, -1):
            try:
                post = self.driver.find_element_by_xpath('//div[@id="main-container"]/div[2]/div[' + str(postNum) + ']/div[2]/a')
            except Exception as e:
                self.crawlStatus(e)
                postNum -= 1
                break 

        while True:
            self.driver.get(urlList[urlIndex])
            sl(0.5)

            #偵測貼文已被刪除和到頂即將換頁的異常
            try:
                post = self.driver.find_element_by_xpath('//div[@id="main-container"]/div[2]/div[' + str(postNum) +']/div[2]/a')
            except Exception as e:
                self.crawlStatus(e)
                try:
                    post = self.driver.find_element_by_xpath('//div[@id="main-container"]/div[2]/div[' + str(postNum) +']/div[2]')
                    if "刪除" in post.text:
                        postNum -= 1
                        continue
                #此頁已擷取完畢，即將換頁
                except Exception as e:
                    self.crawlStatus(e)
                    #點擊上頁
                    self.driver.find_element_by_xpath('//div[@id="action-bar-container"]/div/div[2]/a[2]').click()
                    sl(0.5)
                    #將當前url加到url列表裡
                    urlList.append(self.driver.current_url)
                    urlIndex += 1
                    #獲取此頁面所有貼文元素的總個數
                    postNum = len(self.driver.find_elements_by_xpath('//div[@id="main-container"]/div[2]/div/div[2]/a'))
                    #因開頭最上面的貼文是從div[2]開始，其中總個數不會把已被刪除的算進去，所以加10來做以下偵測
                    #確保是從最下面的貼文開始擷取
                    postNum += 10
                    for postNum in range(postNum, 1, -1):
                        try:
                            post = self.driver.find_element_by_xpath('//div[@id="main-container"]/div[2]/div[' + str(postNum) + ']/div[2]/a')
                            break
                        except Exception as e:
                            self.crawlStatus(e)
                    continue
            
            postNum -= 1
            post.click()
            sl(0.5)
            try:
                #有些貼文作者會要求版主刪除，不會放上日期，所以用try偵測
                #把貼文裡的日期找出
                date = self.driver.find_element_by_xpath('//div[@id="main-content"]/div[4]/span[2]').text
            except Exception as e:
                self.crawlStatus(e)
                continue
            #"Fri Apr 17 16:01:44 2020"空格隔開變成列表
            dateList = date.split(' ')
            # 因有的貼文日期xpath不同，所以在這偵測，如有出現異常，轉成搜尋其他日期格式的xpath
            try:
                #取出月、日、年，在轉換成string
                dateMDY = ' '.join([dateList[1], dateList[2], dateList[-1]])
            except Exception as e:
                self.crawlStatus(e)
                dateList = self.driver.find_element_by_xpath('//div[@id="main-content"]/div[1]/span[2]').text.split(' ')
                dateMDY = ' '.join([dateList[1], dateList[2], dateList[-1]])
            try:
                #偵測時間日期是否多打一個空格，如異常重新定義
                #轉成datetime類型
                dateMDY = dt.datetime.strptime(dateMDY, '%b %d %Y').date()
            except Exception as e:
                self.crawlStatus(e)
                dateMDY = ' '.join([dateList[1], dateList[3], dateList[-1]])
                dateMDY = dt.datetime.strptime(dateMDY, '%b %d %Y').date()
            #判斷日期是否在我們想找的區間內
            if self.startDate <= dateMDY <= self.endDate:
                #把貼文裡的url找出
                #查找節點內的href屬性值裡須包含html
                try:
                    url = self.driver.find_element_by_xpath('//div[@id="main-content"]/span/a').get_attribute("herf")
                    if "html" not in url:
                        raise Exception
                except Exception as e:
                    self.crawlStatus(e)
                    url = self.driver.find_element_by_xpath('//div[@id="main-content"]/a').get_attribute("herf")
                #如有擷取到符合日期的url，存儲在csv文件裡並打印
                with open("crawlPTT.csv", "a+", newline="", encoding="utf-8") as f:
                    writer = csv.writerow(f)
                    writer.writerow([dt.datetime.now(), "success", str(url)])
                print(url)
                
                #將url放入到redis的urls列表裡
                self.postRedis.rpush("urls", url)
            
            elif self.startDate <= self.endDate < dateMDY:
                print("此日期大於初始和結束日期，繼續擷取...")
                continue
            else:
                print("此日期已小於初始和結束日期!即將跳出查找")
                # 只要日期已小於初始日期和結束日期，就跳出循環
                break
    

    #設置監聽等待其他機器連接
    def sendUrl(self):
        self.sockfd.listen(5)
        print("Listen the port %d..." % self.port)
        while True:
            try:
                connfd,addr = self.sockfd.accept()
                print("接收到來自" + str(addr) + "的連接...")
            except KeyboardInterrupt:
                self.sockfd.close()
                sys.exit("服務器退出")
            except Exception:
                traceback.print_exc()
                continue
            #創建新的線程處理請求
            clientThread = Thread(target = self.handleRequest,args = (connfd,))
            clientThread.setDaemon(True)
            clientThread.start()
    
    #機器端請求函數
    def handleRequest(self, connfd):
        while True:
            #接收機器端請求
            request = connfd.recv(4096).decode()
            sl(1)
            url = self.postRedis.lpop("urls")
            if not url:
                print("urls裡已經沒有url")
                connfd.send("##".encode())
                break

            if request == "y":
                connfd.send(url.encode())

        connfd.close()

    #將爬取狀況寫入csv文件的函數
    def crawlStatus(self, e):
        with open("crawlStatus.csv", "a+", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([dt.datetime.now(), "error", str(e)])

    

    #啟動程序
    def workOn(self):
        print("歡迎進入PTT貼文查找系統!")
        #查找的開始日期
        while True:
            startDate = input("請輸入您想查找的初始日期年月日(格式:2020/01/02):")
            if len(startDate.strip()) != 10:
                print("您輸入的格式有誤!請重新輸入")
                continue
            elif (startDate[4] or startDate[7]) != '/':
                print("您輸入的格式有誤!請重新輸入")
                continue
            else:
                break
        #查找的結束日期
        while True:
            endDate = input("請輸入結束日期(格式:2020/01/02):")
            if len(endDate.strip()) != 10:
                print("您輸入的格式有誤!請重新輸入")
                continue
            elif (endDate[4] or endDate[7]) != '/':
                print("您輸入的格式有誤!請重新輸入")
                continue
            else:
                break

        #把日期變成datetime類型
        self.startDate = dt.datetime.strptime(startDate, "%Y/%m/%d").date()
        self.endDate = dt.datetime.strptime(endDate, "%Y/%m/%d").date()
        

        self.getPage()
        self.parsePage()
        self.driver.close()
        self.sendUrl()

        #關閉套接字
        self.sockfd.close()

if __name__ == "__main__":
    spider = PttCrawl()
    spider.workOn()