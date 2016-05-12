shanbay-interview
=================

This repository contains the source code for my shanbay interview using `Flask` + `bootstrap`

1. 用户可以根据自己的英语水平，例如 四级，六级，雅思，和托福 来设置自己背单词的范围；
2. 每个用户可以设置每天背多少单词
3. 用户背单词过程中能够添加笔记， 也可以查看其他用户共享的笔记
4. 用户背单词过程中，可以看到单词，单词的解释和例句。
5. 背单词的时候还可以看到近义词，请考虑提供这个单词的两个近义词（如果有的话）
我们要求作业用 Python, 最好是 基于`Django`框架来完成， Web 页面可以基于`bootstrap`来简化你的开发流程。 我们希望你最迟在收到邮件的 2 周内能提交给我们代码，但如果你能在 1 周之内完成会有额外加分。 如果你需要额外延长你的时间，请务必提前和我们联系。

我们会非常认真得阅读你的代码，在后续的沟通中我们将基于你的代码来讨论，如果你在开发过程中有什么问题，可以和我们沟通。

## Usage:
Install the requirements
```
(venv)$ pip install -r requirements.txt    
```
Init database
```
(venv)$ python manage.py shell
(venv)$ db.create_all()
```
Run
```
(venv)$ python manage.py runserver
```

**TODO LIST**：

- [x] 用户信息设置
    - [x] 电子邮件设置
    - [x] 密码重置 
    - [x] 昵称 
    - [x] 时区
    - [x] 个人简介
    - [x] 邮件确认
- [x] 背单词设置 
    - [x] 每日学习量
    - [x] 单词难度
    - [x] 单词的目标掌握程度
    - [x] 自动发音模式
- [ ] 背单词功能
    - [ ] ajax实现的背单词交互过程
    - [x] 查看解释
    - [x] 查看例句
    - [x] 查看发音
    - [ ] 查看同义词(两个)
- [x] 笔记功能
    - [x] 我的笔记
    - [x] 添加笔记
    - [x] 查看其他用户笔记
    
    