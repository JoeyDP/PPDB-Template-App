# Author: Len Feremans
# Unit tests for QuoteDataAccess
import unittest
from .quote_data_access import DBConnection, QuoteDataAccess, Quote
from .config import *


class TestQuoteDataAccess(unittest.TestCase):

    def _connect(self):
        connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
        return connection
    
    def test_connection(self):
        connection = self._connect()
        connection.close()
        print("Connection: ok")
        
    def test_qet_quote(self):
        connection = self._connect()
        quote_dao = QuoteDataAccess(dbconnect=connection)
        quote_obj=quote_dao.get_quote(iden=1)
        print(quote_obj.to_dct())
        self.assertEqual('If people do not believe that mathematics is simple, it is only because they do not realize how complicated life is.'.upper(), 
                         quote_obj.text.upper())
        connection.close()
    
    def test_qet_quotes(self):
        connection = self._connect()
        quote_dao = QuoteDataAccess(dbconnect=connection)
        quote_objects = quote_dao.get_quotes()
        print(quote_objects[1].to_dct())
        self.assertEqual('If people do not believe that mathematics is simple, it is only because they do not realize how complicated life is.'.upper(), 
                         quote_objects[0].text.upper())
        connection.close()
        
    def test_insert(self):
        connection = self._connect()
        connection.get_cursor().execute('DELETE from Quote where author=\'Len\'')
        connection.get_connection().commit()
        quote_dao = QuoteDataAccess(dbconnect=connection)
        quote_obj = Quote(iden=None, text='If Len can do it, anyone can ;-)', author='Len')
        quote_dao.add_quote(quote_obj)
        quote_objects = quote_dao.get_quotes()
        print(quote_objects[-1].to_dct())
        self.assertEqual('If Len can do it, anyone can ;-)'.upper(), 
                         quote_objects[-1].text.upper())
        self.assertEqual('Len', quote_objects[-1].author)
        connection.get_cursor().execute('DELETE from Quote where author=\'Len\'')
        connection.get_connection().commit()
        connection.close()
