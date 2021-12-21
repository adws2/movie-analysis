import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
from datetime import datetime
from bs4 import BeautifulSoup
import pickle

class crawling_kobis():
        
    def open(self):
        webpage = 'http://www.kobis.or.kr/kobis/business/stat/boxs/findFormerBoxOfficeList.do'
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs',{'download.default_directory' : os.getcwd() + '\save'})
        browser = webdriver.Chrome('chromedriver', chrome_options=options)
        cookies = browser.get_cookies()
        browser.get(webpage)
        self.browser = browser
        

    def get_excel_files_all_time(self,rank_list = np.arange(0,10), dir = 'save'):
        ## 역대 rank_list 순위의 영화들의 데이터를 엑셀로 가져옴.
        
        for i in rank_list:
            ## 영화로 들어감
            button = self.browser.find_element_by_xpath("//tr[@id='tr_%d']//span[@class='ellip per90']"%(i))
            button.click()
            time.sleep(5)

            ## 통계정보 클릭
            test01=self.browser.find_elements_by_class_name('tab')
            test01[1].send_keys(Keys.ENTER)
            time.sleep(50) ### 굉장히 오래걸림

            ## 다운로드 클릭
            test02=self.browser.find_elements_by_class_name('btn_small')
            test02[5].send_keys(Keys.ENTER)
            time.sleep(5)

            ## 다운로드 확인
            al = self.browser.switch_to_alert()
            al.accept()
            time.sleep(5)

            ## 탈출
            self.browser.refresh()
            
            ## 이름을 바꿈 (다운받으면 자동으로 현재 날짜로 됨)
            today = datetime.today().strftime("%Y-%m-%d")
            os.rename('{0}/KOBIS_일자별_통계정보_{1}.xls'.format(dir,today) ,'{0}/{1}_{2}.xls'.format(dir,today,i))
            
        self.browser.close()
            
    
class parsing():
    
    def __init__(self,folder = 'save'):
        file_names = os.listdir('{}'.format(folder))
        self.folder = folder
        self.file_names = []
        for file in file_names:
            if file[-3:] == 'xls':
                self.file_names.append('{}/{}'.format(folder, file))
        
    def dict_from_xls(self):
        for file_dir in self.file_names:
            dict = {}
            data = open(file_dir , 'r' , encoding = 'utf-8')
            ## soup 로 열기
            soup = BeautifulSoup(data, 'html.parser') 
            ## title : body -> td -> string 
            title = soup.find('body')
            title = title.find('td')
            title = title.get_text().strip()[3:-10]

            ## 일 하나에 대한 정보 set : tbody -> tr -> td ##
            datalist = soup.find('tbody')
            datalist = datalist.find_all('tr')
            date = 0
            for data in datalist:
                ## 점유율 데이터를 봐서 시사회나 무의미한 정보를 걸러준다.
                share = float(eval(data.find_all('td')[4].get_text()[:-1])) 
                
                if share > 5:

                    cumulative = eval(data.find_all('td')[-2].get_text().replace(',',''))
                    date += 1 # eval(data.find_all('td')[0].get_text().replace('-',''))
                    dict[ title + ' {}'.format(date)] = cumulative

                else:
                    pass
            
            with open('{0}/{1}.pickle'.format(self.folder, title),'wb') as fw:
                pickle.dump(dict, fw)