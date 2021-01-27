# Data Access Object pattern: see http://best-practice-software-engineering.ifs.tuwien.ac.at/patterns/dao.html
# For clean separation of concerns, create separate data layer that abstracts all data access to/from RDBM

# Depends on psycopg2 librarcy: see (tutor) https://wiki.postgresql.org/wiki/Using_psycopg2_with_PostgreSQL
import psycopg2


class DBConnection:
    def __init__(self, dbname, dbuser):
        try:
            self.conn = psycopg2.connect("dbname='{}' user='{}'".format(dbname, dbuser))
        except:
            print('ERROR: Unable to connect to database')
            raise
        
    def close(self):
        self.conn.close()
        
    def get_connection(self):
        return self.conn
    
    def get_cursor(self):
        return self.conn.cursor()
    
    def commit(self):
        return self.conn.commit()
    
    def rollback(self):
        return self.conn.rollback()


class Quote:
    def __init__(self, iden, text, author):
        self.id = iden
        self.text = text
        self.author = author
        
    def to_dct(self):
        return {'id': self.id, 'text': self.text, 'author': self.author}


class QuoteDataAccess:
    def __init__(self, dbconnect):
        self.dbconnect = dbconnect
       
    def get_quotes(self):
        cursor = self.dbconnect.get_cursor()
        cursor.execute('SELECT id, text, author FROM Quote')  
        quote_objects = list()
        for row in cursor:
            quote_obj = Quote(row[0],row[1],row[2]) 
            quote_objects.append(quote_obj)
        return quote_objects
    
    def get_quote(self, iden):
        cursor = self.dbconnect.get_cursor()
        # See also SO: https://stackoverflow.com/questions/45128902/psycopg2-and-sql-injection-security
        cursor.execute('SELECT id, text, author FROM Quote WHERE id=%s', (iden,))
        row = cursor.fetchone()   
        return Quote(row[0], row[1], row[2])
     
    def add_quote(self, quote_obj): 
        cursor = self.dbconnect.get_cursor()
        try:
            cursor.execute('INSERT INTO Quote(text,author) VALUES(%s,%s)', (quote_obj.text, quote_obj.author,))
            # get id and return updated object
            cursor.execute('SELECT LASTVAL()')
            iden = cursor.fetchone()[0]
            quote_obj.id = iden
            self.dbconnect.commit()
            return quote_obj
        except:
            self.dbconnect.rollback()
            raise Exception('Unable to save quote!')
