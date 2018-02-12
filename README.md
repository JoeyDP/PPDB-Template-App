# README #
Implementation of Example web-app in python with database
by Len Feremans, data scientist at the University of Antwerp (Belgium) within the Adrem data labs research group.

### What is this repository for? ###
Tutorial for Programming Project Database

### Quick start ###
The implementation is written in Python.

To create the database:
> psql -d postgres -U postgres -f sql/create_database.sql 
> psql -d dbtutor -U len -f sql/schema.sql 

To run development server
> cd src/ProgDBTutor
> python app.py

Then visit http://localhost:5000

To run unit tests:
> cd src/ProgDBTutor
> nosetests

### Dependencies ###
Python modules (install using "pip install name"):
* psycopg2,psycopg2-binary
* flask
 
Postgres database (install, then make sure psql is running)

### Code ###
Data:
- Example of data-access pattern, see /ProgDBTutor/quote_data_access.py
```python
#Data Access Object pattern: see http://best-practice-software-engineering.ifs.tuwien.ac.at/patterns/dao.html
#For clean separation of concerns, create separate data layer that abstracts all data access to/from RDBM
#
#Depends on psycopg2 librarcy: see (tutor) https://wiki.postgresql.org/wiki/Using_psycopg2_with_PostgreSQL
import psycopg2

class DBConnection:
    def __init__(self,dbname,dbuser,dbpass,dbhost):
        try:
            self.conn = psycopg2.connect("dbname='{}' user='{}' host='{}' password='{}'".format(dbname,dbuser,dbhost, dbpass))
        except:
            print('ERROR: Unable to connect to database')
            raise Exception('Unable to connect to database')
        
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
        #See also SO: https://stackoverflow.com/questions/45128902/psycopg2-and-sql-injection-security
        cursor.execute('SELECT id, text, author FROM Quote WHERE id=%s', (iden,))
        row = cursor.fetchone()   
        return Quote(row[0],row[1],row[2])
     
    def add_quote(self, quote_obj): 
        cursor = self.dbconnect.get_cursor()
        try:
            cursor.execute('INSERT INTO Quote(text,author) VALUES(%s,%s)', (quote_obj.text, quote_obj.author,))
            #get id and return updated object
            cursor.execute('SELECT LASTVAL()')
            iden = cursor.fetchone()[0]
            quote_obj.id = iden
            self.dbconnect.commit()
            return quote_obj
        except:
            self.dbconnect.rollback()
            raise Exception('Unable to save quote!')
```
- Example of unit test, see /ProgDBTutor/test_quote_data_access.py
```python
#Author: Len Feremans
#Unit tests for QuoteDataAccess 
import unittest
from quote_data_access import DBConnection, QuoteDataAccess, Quote
from config import *

class TestQuoteDataAccess(unittest.TestCase):

    def _connect(self):
        connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'] ,dbpass=config_data['dbpass'], dbhost=config_data['dbhost'])
        return connection
    
    def test_connection(self):
        connection = self._connect()
        connection.close()
        print("Connection: ok")
        
    def test_qet_quote(self):
        connection = self._connect()
        quote_dao = QuoteDataAccess(dbconnect=connection)
        quote_obj=quote_dao.get_quote(iden=1)
        print(quote_obj)
        self.assertEqual('If people do not believe that mathematics is simple, it is only because they do not realize how complicated life is.'.upper(), 
                         quote_obj.text.upper())
        connection.close();
    
    def test_qet_quotes(self):
        connection = self._connect()
        quote_dao = QuoteDataAccess(dbconnect=connection)
        quote_objects = quote_dao.get_quotes()
        print(quote_objects[1])
        self.assertEqual('If people do not believe that mathematics is simple, it is only because they do not realize how complicated life is.'.upper(), 
                         quote_objects[0].text.upper())
        connection.close()
        
    def test_insert(self):
        connection = self._connect()
        quote_dao = QuoteDataAccess(dbconnect=connection)
        quote_obj = Quote(iden=None,text='If Len can do it, anyone can ;-)',author='Len')
        quote_dao.add_quote(quote_obj)
        quote_objects = quote_dao.get_quotes()
        print(quote_objects[-1]);
        self.assertEqual('If Len can do it, anyone can ;-)'.upper(), 
                         quote_objects[-1].text.upper())
        self.assertEqual('Len', quote_objects[-1].author)
        connection.close()
```

Service:
- Example of REST api: see /ProgDBTutor/app.py
- Example of rendering views: see also /ProgDBTutor/app.py
```python
### TUTORIAL Len Feremans
###see tutor https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
from flask import Flask
from flask.templating import render_template
from flask import request, session, jsonify

from config import config_data
from quote_data_access import Quote, DBConnection, QuoteDataAccess

### INITIALIZE SINGLETON SERVICES ###
app = Flask('Tutorial ')
app.secret_key = '*^*(*&)(*)(*afafafaSDD47j\3yX R~X@H!jmM]Lwf/,?KT'
app_data = {}
app_data['app_name'] = config_data['app_name']
connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'] ,dbpass=config_data['dbpass'], dbhost=config_data['dbhost'])
quote_data_access = QuoteDataAccess(connection)

### REST API ###
### See https://www.ibm.com/developerworks/library/ws-restful/index.html ###
@app.route('/quotes',methods=['GET'])
def get_quotes(): 
    #Lookup row in table Quote, e.g. 'SELECT ID,TEXT FROM Quote'
    quote_objects = quote_data_access.get_quotes()
    #Translate to json
    return jsonify([obj.to_dct() for obj in quote_objects])

@app.route('/quote/<int:id>',methods=['GET'])
def get_quote(id): 
    #ID of quote must be passed as parameter, e.g. http://localhost:5000/quote?id=101
    #Lookup row in table Quote, e.g. 'SELECT ID,TEXT FROM Quote WHERE ID=?' and ?=101
    quote_obj = quote_data_access.get_quote(id)
    return jsonify(quote_obj.to_dct())

#To create resource use HTTP POST
@app.route('/addquote',methods=['POST'])
def add_quote(): 
    #Text value of <input type="text" id="text"> was posted by form.submit
    quote_text = request.form.get('text')
    quote_author = request.form.get('author')
    #Insert this value into table Quote(ID,TEXT)
    quote_obj = Quote(iden=None,text=quote_text,author=quote_author)
    print('Adding {}'.format(quote_obj.to_dct()))
    quote_obj = quote_data_access.add_quote(quote_obj)
    return jsonify(quote_obj.to_dct())

### VIEW ###
@app.route("/")
def main():
    return render_template('index.html', app_data=app_data)

@app.route("/show_quotes")
def show_quotes():
    quote_objects = quote_data_access.get_quotes()
    #Render quote_objects "server-side" using Jinja 2 template system
    return render_template('quotes.html', app_data=app_data, quote_objects=quote_objects)

@app.route("/show_quotes_ajax")
def show_quotes_ajax():
    #Render quote_objects "server-side" using Jinja 2 template system
    return render_template('quotes_ajax.html', app_data=app_data)


### RUN DEV SERVER ###
if __name__ == "__main__":
    app.run()
```
View:
- Example of rendering server-side: templates/quotes.html
```html
<html>
<head>
	<title>{{app_data['app_name']}}</title>
	<link  href="{{ url_for('static',filename='mystyle.css') }}" rel="stylesheet"> </link>
</head>
<body>	
	{% include 'header.html' %} 
    <div>
    		<a href="/">show main</a>
    		<div class="borderme">
    			<div class="smalltitle">Quotes:</div>
    			{% for quote_obj in quote_objects %}
    				 <div style="padding: 10px"><span style="font-style: italic;">{{quote_obj.text}}</span>
    				 		-- {{quote_obj.author}}
    				 </div>
    			{% endfor %}
  			</div>  			
    		</div>
    		<form action="/addquote" method="post">
    			Text: <input type ="text" name="text"/><br/>
           	Author: <input type ="text" name="author"/><br/>
           	<input type ="submit" value="save"/>
         </form>  
    </div>
    {% include 'footer.html' %}   
</body>
</html>
```

- Example of rendering client-side with ajax and using jQuery: see quotes_ajax.html 
```html
<html>
<head>
	<title>{{app_data['app_name']}}</title>
	<script src="{{ url_for('static',filename='jquery-3.2.1.js') }}"></script>
	<link  href="{{ url_for('static',filename='mystyle.css') }}" rel="stylesheet"> </link>
	<script>
function load_quotes(f){
	$.ajax({url: "/quotes", type: "GET", dataType: "json"}).done(f);
}

function save_quote(text,author,f){
	$.ajax({url: "/addquote", type: "POST", data: {'text': text, 'author': author}});
}

function render_quotes(data){
	$("#quotes").empty();
  	for(var i=0;i<data.length;i++){
  		$("#quotes").append(
  				'<div style="padding: 10px"><span style="font-style: italic;">' 
  				  + data[i]['text'] 
  				  + '</span> -- ' 
  				  + data[i]['author'] 
  				  + '</div>');
  	}
}
	
$(document).ready(function() {	
	 load_quotes(render_quotes);
	 $("#addQuoteForm").on("submit", function(event){
	 	event.preventDefault();
	 	var text = $("#text").val();
	 	var author = $("#author").val();
	 	save_quote(text,author);
	 	load_quotes(render_quotes);
	 });
});
	</script>
</head>
<body>	
	{% include 'header.html' %} 
    <div>
    		<a href="/">show main</a>
    		<div class="borderme">
    			<div class="smalltitle">Quotes:</div>
    			<div id="quotes"/>		
      	</div>
      	<form id="addQuoteForm" action="/" method="post">
    			Text: <input type ="text" name="text" id="text"/><br/>
           	Author: <input type ="text" name="author" id="author"/><br/>
           	<input type ="submit" value="save"/> <span id="status">
         </form>  
    </div>
    {% include 'footer.html' %}   
</body>
</html>
```
- Example of css file: ProgDBTutor/static/mystyle.css
```css
//Author: Len Feremans
//Simple css
p{
   font-family:"font-family: Helvetica, Arial, sans-serif!important";
   font-size: 12pt;
}
h1{
   font-family:"font-family: Helvetica, Arial, sans-serif!important";
   font-size: 20pt;
}
//css applicable to all elements that have class=smalltitle
.smalltitle{
	font-weight:bold;
	font-size:16pt;
}
//larger-font to all elements that have class=larger
.larger{
	font-size:14pt;
}
//applicable to all div elements that have class borderme
div.borderme{
	border: 1px solid darkgrey; 
	padding:10px;
	padding-bottom: 20px;
}
//applicable to div with class header
div.header{
	top:0;
	left:0;
	background-color:  #efefef;
	width:100%; 
	height:25px; 
	padding: 0px;
	margin:0 px;
	margin-bottom: 20px;
	font-family:"font-family: Helvetica, Arial, sans-serif!important";
    font-size: 14pt;
}
div.footer{
	//used absolute position relative to bottom-left
	position:absolute;
	background-color:  lightgrey;
	bottom:0;
	left:0;
	width:100%; 
	height:30px; 
	padding: 0px;
	font-family:"font-family: Helvetica, Arial, sans-serif!important";
    font-size: 15pt;
}
```

- Mores examples of Jinja2 (http://jinja.pocoo.org/docs/2.10/) templates with include and for loops.
Footer:
```html
<div class="footer">
    &copy; Len Feremans, Universiteit Antwerpen, 2018
    <img src="{{ url_for('static',filename='ua_logo.png') }}" style="float: right; height:30px;"/>
</div>
```

Header:
```html
<div class="header">
	<h1>{{app_data['app_name']}}</h1>
</div>
```

Index:
```html
<html>
<head>
	<title>{{app_data['app_name']}}</title>
	<link  href="{{ url_for('static',filename='mystyle.css') }}" rel="stylesheet"> </link>
</head>
<body>	
	{% include 'header.html' %} 
    <div>
    		
    		<div class="borderme">
    			<div class="smalltitle">Test REST api:</div>
    			GET <a class="larger" href="/quotes">/quotes</a><br/>
    			GET <a class="larger" href="/quote/1">/quote/1</a> <br/>
    			<form action="/addquote" method="post">
    				POST <a class="reststyle"> /addquote?text=X&author=Y</a> 
           		&nbsp;Text: <input type ="text" name="text"/>
           		&nbsp;Author: <input type ="text" name="author"/>
           		<input type = "submit"/>
         	</form>  
    		</div>
    		<div class="borderme">
    			<div class="smalltitle">User interface:</div>
    			<a class="larger" href="/show_quotes">show quotes (classic)</a><br/>
    			<a class="larger" href="/show_quotes_ajax">show quotes (ajax)</a>
    		</div>
    </div>
    {% include 'footer.html' %}   
</body>
</html>
```