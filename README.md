牡蛎单词
=================
`python2`,`Flask`,`Bootstrap`

This repository contains the source code for my shanbay interview using `Flask` + `bootstrap`

1. 用户可以根据自己的英语水平，例如 四级，六级，雅思，和托福 来设置自己背单词的范围；
2. 每个用户可以设置每天背多少单词
3. 用户背单词过程中能够添加笔记， 也可以查看其他用户共享的笔记
4. 用户背单词过程中，可以看到单词，单词的解释和例句。

## Usage:
create a virtualenv
```
$ virtualenv venv
```
Windows environment:
```
$ .\venv\Scripts\active
```
Linux environment:
```
$ source venv/bin/activate
```
Install the requirements
```
(venv)$ cd requirements 
(venv)$ pip install -r dev.text
(venv)$ cd ..   
```
Init database
```
(venv)$ python .\manage.py shell
>>>db.create_all()
>>>User.generate_fake()
>>>Word.generate_fake()
....
>>>exit()
```
Run
```
(venv)$ python manage.py runserver
```

默认用户:test@shanbay.com 密码:test

**TODO LIST**：

- [x] 用户信息设置
    - [x] 电子邮件设置
    - [x] 密码重置 
    - [x] 昵称 
    - [x] 时区
    - [x] 个人简介
    - [x] 邮件确认
- [x] 个人单词设置 
    - [x] 每日学习量
    - [x] 单词难度
    - [x] 单词的目标掌握程度
    - [x] 自动发音模式
- [x] 背单词功能
    - [x] ajax实现的背单词交互过程
    - [x] 查看解释
    - [x] 查看例句
    - [x] 查看发音
    - [ ] 查看同义词(两个)
- [x] 笔记功能
    - [x] 我的笔记
    - [x] 添加笔记
    - [x] 查看其他用户笔记
- [x] 权限功能(`@admin_required()`)
    - [x] 管理员权限
    - [x] 普通用户权限
    - [x] 管理员对普通用户资料的修改
    - [ ] 管理员对该单词共享笔记的增删改
- [x] 实现前后端分离
    - [x] model的REST-API
    - [x] REST-API权限设置
    - [x] 每日单词的getJSON
    - [x] 完成打卡的postJson
    
**待做改善**:

1. 每日单词一次请求过多会造成一开始加载单词变的很慢，修改成10个左右可满足响应速度
2. 邮箱使用的是我们班的公共邮箱，所以可能收不到邮件，使用的时候可以换成你自己的
3. Model层方法过多，太过臃肿，不好管理,可以考虑建立Model文件夹，将共有的方法抽离成Action层，我把它叫做`MAVC`?。
4. REST获取资源, 邮件服务，等耗时操作需要替换成MQ的方式，初步选择`Celery` + `Redis`
5. 部署方面初步决定使用：`Fabric`+`Supervisior`+`Tornado`+`nginx`
