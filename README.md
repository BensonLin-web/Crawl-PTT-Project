# Crawl-PTT-Project
首先環境需要有MySQL、Selenium、Lxml、Redis這幾個庫，使用的版本在requirements.txt裡。
使用Selenium+Chromedriver爬取頁面，循環遍歷每個分類看板的每一頁。
如果遇到異常狀況以csv文件存儲。
將符合日期的URL爬取下來，存進csv文件和redis的urls列表裡。
當全部的urls爬取完畢後，使用socket開始監聽其他機器。
Benson_PTT爬取.py文件為主機器的程序，負責爬取url。
Benson_爬取網址端.py文件為其他多台機器的程序，負責將url請求過來後，開始爬取頁面資料，存進MySQL DB。
完成分布式爬蟲的過程。





