#@@ -0,0 +1,175 @@
#!/usr/bin/python
# coding = utf-8
# 下载巨潮报告
import csv
import math
import os
import random
import time
import requests
import urllib.request
import urllib.parse
import urllib
import time

START_DATE = '2018-01-01'  # 首家农业上市企业的日期 开始时间
END_DATE = str(time.strftime('%Y-%m-%d'))  # 默认当前提取，可设定为固定值  结束时间

OUT_DIR = 'C:/Users/Public/Desktop/Python'  # 文件下载目录  修改成自己电脑上存在的目录
OUTPUT_FILENAME = '债券发行上市'
# 板块类型：shmb（沪市主板）、szmb（深市主板）、szzx（中小板）、szcy（创业板）
#PLATE = 'szzx;'
# 公告类型：category_scgkfx_szsh（首次公开发行及上市）、category_ndbg_szsh（年度报告）、category_bndbg_szsh（半年度报告）
CATEGORY = 'category_zqfxss_zqgg;'

URL = 'http://www.cninfo.com.cn/cninfo-new/announcement/query'
HEADER = {
   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
   'X-Requested-With': 'XMLHttpRequest'
 }
MAX_PAGESIZE = 1000
MAX_RELOAD_TIMES = 5
RESPONSE_TIMEOUT = 20

def standardize_dir(dir_str):
     assert (os.path.exists(dir_str)), 'Such directory \"' + str(dir_str) + '\" does not exists!'
     if dir_str[len(dir_str) - 1] != '/':
         return dir_str + '/'
     else:
         return dir_str


def getFile(url):
    file_name = url.split('/')[-1]
    urllib.request.urlretrieve(url, OUT_DIR + '/' + file_name)

    # u = urllib.request.urlopen(url)
    # f = open(file_name, 'wb')

    # block_sz = 8192
    # while True:
    #     buffer = u.read(block_sz)
    #     if not buffer:
    #         break
    #     f.write(buffer)
    # f.close()
    print ("Sucessful to download" + " " + OUT_DIR + '/' + file_name)

def get_response(page_num, return_total_count=False):
      query = {
         # 'stock': '',
         # 'searchkey': '',
        # 'plate': PLATE,
        # 'plate': '',
        'category': CATEGORY,
         # 'trade': '',
         'column': 'bond',
        'columnTitle': '历史公告查询',
         'pageNum': page_num,
        'pageSize': MAX_PAGESIZE,
         'tabName': 'fulltext',
         # 'sortName': '',
         # 'sortType': '',
         # 'limit': '',
         'showTitle': 'category_zqfxss_zqgg/category/债券发行上市',
         'seDate': START_DATE + '~' + END_DATE,
      }
      result_list = []
      result_arr = []
      reloading=0
      while True:
         reloading += 1
         if reloading > MAX_RELOAD_TIMES:
             return []
         elif reloading > 1:
             __sleeping(random.randint(5, 10))
             print('... reloading: the ' + str(reloading) + ' round ...')
         try:
             r = requests.post(URL, query, HEADER, timeout=RESPONSE_TIMEOUT,)
         except Exception as e:
             print(e)
             continue
         if r.status_code == requests.codes.ok and r.text != '':
             break
      my_query = r.json()
      try:
         r.close()
      except Exception as e:
         print(e)
      if return_total_count:
         return my_query['totalRecordNum']
      else:
         for each in my_query['announcements']:
             file_link = 'http://www.cninfo.com.cn/' + str(each['adjunctUrl'])
             file_name = __filter_illegal_filename(
                 str(each['secCode']) + str(each['secName']) + str(each['announcementTitle']) +
                 file_link[-file_link[::-1].find('.') - 1:]  # 最后一项是获取文件类型后缀名
             )
             add_time = time.localtime(each['announcementTime']/1000)
             arr = [each['secName'],each['announcementTitle'],file_link,time.strftime("%Y-%m-%d",add_time)]
             result_list.append(file_link)
             result_arr.append(arr)
      # for url in result_list[:]:
      #     getFile(url)
      #     print(result_arr)
      return result_arr





def __log_error(err_msg):
     err_msg = str(err_msg)
     print(err_msg)
     with open(error_log, 'a', encoding='gb18030') as err_writer:
         err_writer.write(err_msg + '\n')


def __sleeping(sec):
     if type(sec) == int:
         print('... sleeping ' + str(sec) + ' secong ...')
         time.sleep(sec)


def __filter_illegal_filename(filename):
     illegal_char = {
         ' ': '',
         '*': '',
        '/': '-',
         '\\': '-',
         ':': '-',
         '?': '-',
         '"': '',
         '<': '',
         '>': '',
         '|': '',
         '－': '-',
         '—': '-',
         '（': '(',
         '）': ')',
         'Ａ': 'A',
         'Ｂ': 'B',
         'Ｈ': 'H',
          '，': ',',
         '。': '.',
         '：': '-',
         '！': '_',
         '？': '-',
         '“': '"',
         '”': '"',
        '‘': '',
         '’': ''
     }
     for item in illegal_char.items():
         filename = filename.replace(item[0], item[1])
     return filename


if __name__ == '__main__':
     # 初始化重要变量
    out_dir = standardize_dir(OUT_DIR)
    error_log = out_dir + 'error.log'
    output_csv_file = out_dir + OUTPUT_FILENAME.replace('/', '')+ time.strftime('%Y%m%d%H%M%S',time.localtime()) + '.csv'
     # 获取记录数、页数
    item_count = get_response(1, True)
    assert (item_count != []), 'Please restart this script!'
    begin_pg = 1
    end_pg = int(math.ceil(item_count / MAX_PAGESIZE))
    print('Page count: ' + str(end_pg) + '; item count: ' + str(item_count) + '.')
    time.sleep(2)

     # 逐页抓取
    with open(output_csv_file, 'w', newline='', encoding='gb18030') as csv_out:
         writer = csv.writer(csv_out)
         for i in range(begin_pg, end_pg + 1):
             row = get_response(i)
             if not row:
                 __log_error('Failed to fetch page #' + str(i) +
                             ': exceeding max reloading times (' + str(MAX_RELOAD_TIMES) + ').')
                 continue
             else:
                 print (row)
                 url_re=writer.writerows(row)
                 last_item = i * MAX_PAGESIZE if i < end_pg else item_count
                 print('Page ' + str(i) + '/' + str(end_pg) + ' fetched, it contains items: (' +
                       str(1 + (i - 1) * MAX_PAGESIZE) + '-' + str(last_item) + ')/' + str(item_count) + '.')


