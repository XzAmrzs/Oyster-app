# coding=utf-8
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True)
#     name = Column(String(64))
#
#     # association proxy of "user_words" collection
#     # to "content" attribute
#     words = association_proxy('user_words', 'content')
#
#     def __init__(self, name):
#         self.name = name


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))

    # association proxy of "user_word" collection to "word" attribute
    words = association_proxy('user_words', 'content')

    def __init__(self, name):
        self.name = name


# class UserWord(Base):
#     __tablename__ = 'user_word'
#     user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
#     word_id = Column(Integer, ForeignKey('words.id'), primary_key=True)
#     level = Column(String(50))
#
#     # bidirectional attribute/collection of "user"/"user_words"
#     user = relationship(User,
#                         backref=backref("user_words",
#                                         cascade="all, delete-orphan")
#                         )
#
#     # reference to the "Word" object
#     content = relationship("Word")
#
#     def __init__(self, content=None, user=None, level=None):
#         self.user = user
#         self.content = content
#         self.level = level



class UserWord(Base):
    __tablename__ = 'user_word'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    word_id = Column(Integer, ForeignKey('words.id'), primary_key=True)
    level = Column(Integer, default=0, index=True)

    # bidirectional attribute/collection of "user"/"user_words"
    user = relationship(User, backref=backref("user_words", cascade="all, delete-orphan"))
    # reference to the "Word" object
    content = relationship("Word")

    def __init__(self, content=None, user=None, level=None):
        self.user = user
        self.content = content
        self.level = level


class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    content = Column('content', String(64))

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return 'Word(%s)' % repr(self.content)


#
#

#
# class Word(Base):
#     __tablename__ = 'words'
#     id = Column(Integer, primary_key=True)
#     content = Column(String(64), unique=True, index=True)
#     rank = Column(Integer, index=True)
#     phonetic_symbol = Column(String(128))
#     # words表和notes表的一对多关系
#     notes = relationship('Note', backref='word', lazy='dynamic')
#
#     # words表和users表的多对多关系在user中定义
#
#     # 同义词功能还没有想好要怎么实现
#     # synonym = Column(Text())
#     def __init__(self, content):
#         self.content = content

if __name__ == '__main__':
    user = User('log')
    print(user.words)
    for kw in (Word('new_from_blammo'), Word('its_big')):
        user.words.append(kw)
    print(user.words)
