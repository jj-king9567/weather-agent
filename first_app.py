

import requests

from flask import Flask, render_template, request, jsonify  #flask 是制作网站应用  render_template 是渲染html页面
                      #json 是json -->字典                                            #把文件填上数据发给浏览器
import time           #request 是接收用户的请求   jsonify 就是把python字典转化成JSON格式（普通话）
import os             #os 操作系统   读取系统环境变量
from dotenv import load_dotenv   #dotenv 将 .env 文件内容注入系统‘环境变量’




app = Flask(__name__)   #如果他运行就变成main（主角） ，如果是别的文件就是他自己的名字
#flask在这 相当于一个中介，接收到用户请求，跑到后端拿数据，在传递
#__name__是内置变量  ，在这里翻译就是当前文件的身份是谁
load_dotenv()    #将 .env文件 里键值对注释到环境变量来
gaode_key =os.getenv("API_KEY")    ##去操作系统里寻找‘API_KEY'标签  如果没有：None
def get_weather(city):       #括号里面 就是工具能给你的结果
    url = f"https://restapi.amap.com/v3/weather/weatherInfo"  #restapi 是高德后端（数据）的专线
                            #v3 是第3版接口（目前最高）     这个是information 实况信息
    params = {"city":city,"key":gaode_key}
    try :
        response = requests.get(url ,params=params ,timeout=5)   #这个timeout  是等待最多5秒 ，等完直接停
      #response 回应  requests.get 是访问网站 按回车  这个红的params是要额外的参数
        if response.status_code == 200 :
            #status 翻译：状态   完整意思是http状态码
            data = response.json()    #将取到的数据 转化成python字典
            if data.get('status') == '1' and data.get('lives'):
                                                # 这个列表 lives  是高德开发文档里说的（实况天气）
                life = data['lives'][0] #这个是大列表里的小字典
                return f"城市:{life['city']},天气：{life['weather']},温度:{life['temperature']},湿度:{life['humidity']}%"
            else:
                return f"高德返回错误：{data.get('info','未知错误')}"
        else:
            return "网络请求失败，jjk站台无法收到信号，讲述完毕！"
    except Exception as e:
        return f"网络连接出现异常。原因可能是:{e}"
@app.route('/' ,methods=['POST','GET'])    #@是给函数（穿外套）绑定网站，能在你不动他的时候自己调用
def index():      #一个 / 代表一个界面（网页） 但是你可以在flask里写多个@app。route(/)
    weather_result =None
    error_msg = None
    history =[]
    if request.method == 'POST' :        #method 是方法  get 获取   post 发送
        city_input =request.form.get('city','').strip()    #这里的‘’是空字符串
        if not city_input:
            error_msg ="请输入城市名，朋友"
        elif len(city_input) >10 :
            error_msg = "输入太长的城市名了,jjk网站消化不了"
        else:
            result =get_weather(city_input)
            now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                        #strftime 字符串格式化时间                      local 当地  time 时间
            if "未找到" in result or "失败" in result or "异常" in result or "INVALID" in result or "OK" in result :
                 error_msg = result
                 with open("历史天气写入失败.txt","a",encoding="utf-8") as f:
                    f.write(f"[{now_time}]查询的城市：{city_input}")
            else:
                weather_result = result

                try :
                    with open("历史天气数据.txt","a",encoding="utf-8") as f:
                        f.write(f"[{now_time}]查询城市：{city_input} |结果：{weather_result}\n")
                except Exception as e:           #这个Exception 是所以错误的抓
                    print("历史记录写入失败",e)     #这里print 天生支持 ，（逗号） 隔开参数
                try:
                    with open("历史天气数据.txt","r",encoding="utf-8") as f:
                        history =f.readlines()[-10:]    #f.readlines 就是把文本所有行，装到一个列表读取
                        #这里的[-10:] 是取倒数10行  例如 8，9，10 （旧到新）
                        history.reverse()      #这个是让列表倒过来，因为这里是从倒数10开始数，10，9，8
                except FileNotFoundError:     # fileNotFoundError   这里是 r 就是读取 所以风险就是怕没有这个文件
                         pass                 # 这个就是精准打击（只抓取文件找不到的错误）
    return render_template('index.html',result = weather_result,error=error_msg,history=history)
        #render 是渲染 template 是模板  参数 快递盒（数据要去那） 还有，天气数据 错误报告 历史记录
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)

