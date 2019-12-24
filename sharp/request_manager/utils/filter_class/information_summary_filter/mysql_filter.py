# 基于mysql的去重

from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from . import BaseFiltet

Base = declarative_base()

# class Filter(Base):
#
#     __tablename__ = 'filter'
#
#     id = Column(Integer,primary_key=True)
#     hash_value = Column(String(40),index=True,unique=True)

class MySQLFilter(BaseFiltet):
    '''基于mysql的去重'''

    def __init__(self,*args,**kwargs):

        self.table = type(
            kwargs['mysql_table_name'],
            (Base,),
            dict(
            __tablename__ = kwargs['mysql_table_name'],
            id = Column(Integer,primary_key=True),
            hash_value = Column(String(40), index=True, unique=True)
        ))

        BaseFiltet.__init__(*args,**kwargs)

    def _get_storage(self):
        '''返回一个mysql连接对象'''
        engine = create_engine(self.mysql_url)
        Base.metadata.create_all(engine)
        Session = sessionmaker(engine)
        return Session

    def _save(self,hash_value):
        session = self.storage()
        filter = self.table(hash_value=hash_value)
        session.add(filter)
        session.commit()
        session.close()


    def _is_exists(self,hash_value):
        session = self.storage()
        ret = session.query(self.table).filter_by(hash_value=hash_value).first()
        session.close()
        if ret is None:
            return False
        return True
