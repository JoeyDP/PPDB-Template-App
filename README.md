# README #
Implementation of example web application in python with relational database. By Len Feremans assistant at the University of Antwerp (Belgium) within the Adrem data labs research group.

### What is this repository for? ###
Tutorial for Programming Project Database students, or persons interested in creating a web application in python.

We depend on the following technologies:

![stack](https://github.com/joeydp/PPDB-Template-App/blob/master/doc/stack.png?raw=true "Stack")

### Quick start ###
The implementation is written in Python.

#### 1. Postgres database and Python interface
```bash
sudo apt install postgresql postgresql-server-dev-11
sudo apt install python-psycopg2
```

#### 2. create the database
First configure the database with `postgresql` user:
```bash
sudo su postgres
psql
```
Then create a role 'app' that will create the database and be used by the application:
```sql
CREATE ROLE app WITH LOGIN CREATEDB;
CREATE DATABASE dbtutor owner app;
```

You need to 'trust' the role to be able to login. Add the following line to `/etc/postgresql/11/main/pg_hba.conf`
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# app
local   dbtutor         app                                     trust
```

Then initialize the database:
```bash
psql dbtutor -U app -f sql/schema.sql
```

#### 3. Download Dependencies

```bash
virtualenv -p python3 env
source env/bin/activate
pip3 install -r requirements.txt
```


#### 4. Run development server
```bash
cd src/ProgDBTutor
python app.py
```
Then visit http://localhost:5000


#### 5. Run unit tests:
```bash
cd src/ProgDBTutor
nosetests
```


### Result ###
![index](https://github.com/joeydp/PPDB-Template-App/blob/master/doc/dbtutor_index.png?raw=true "Index page")
![rest](https://github.com/joeydp/PPDB-Template-App/blob/master/doc/dbtutor_rest.png?raw=true "Output rest service")
![quotes](https://github.com/joeydp/PPDB-Template-App/blob/master/doc/dbtutor_quotes.png?raw=true "Viewing and adding quotes")

### Code ###

### Web Service ###
Example of implementation REST API and main view controller in *python* using *Flask* library, see [app.py].

```python
### TUTORIAL Len Feremans
### see also Flask tutor https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
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

@app.route('/quotes/<int:id>',methods=['GET'])
def get_quote(id):
    #ID of quote must be passed as parameter, e.g. http://localhost:5000/quotes?id=101
    #Lookup row in table Quote, e.g. 'SELECT ID,TEXT FROM Quote WHERE ID=?' and ?=101
    quote_obj = quote_data_access.get_quote(id)
    return jsonify(quote_obj.to_dct())

#To create resource use HTTP POST
@app.route('/quotes',methods=['POST'])
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
### View: ###

##### Basics #####

Jinja2 template [header.html]
```html
<div class="header row">
    <div class="col">
	   <h1>{{app_data['app_name']}}</h1>
    </div>
</div>
```

Jinja2 template [footer.html]
```html
<div class="fixed-bottom footer row">
    <div class="col-md-8">
        &copy; Len Feremans &amp; Sandy Moens &ndash; Universiteit Antwerpen &ndash; 2018
    </div>
    <div class="col-md-4">
        <img src="{{ url_for('static',filename='ua_logo.png') }}" style="float: right; height:30px;"/>
    </div>
</div>
```

CSS file: [mystyle.css]
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
...
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
}
...
}
```

##### Rendering with templates (server-side) #####
Jinja2 template example of *rendering server-side*: [quotes.html]
```html
<html>
<head>
	<title>{{app_data['app_name']}}</title>

	<link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">

	<link rel="stylesheet" href="{{ url_for('static',filename='bootstrap-4.0.0.min.css') }}">
	<link rel="stylesheet" href="{{ url_for('static',filename='mystyle.css') }}">

	<script src="{{ url_for('static',filename='jquery-3.2.1.js') }}"></script>
	<script src="{{ url_for('static',filename='bootstrap-4.0.0.min.js') }}"></script>
</head>
<body>
	{% include 'header.html' %}

    <!--
        Bootstrap has a grid system for aligning elements in a responsive layout.

        The outer element is a container, which contains rows and columns.
        Each row can should contain up to 12 columns. However, excess columns
        will simply be stacked.

        When adding multiple columns to a row, the framework automatically assigns
        equal width to all columns. For variable with columns, one can use for
        instance col-1, col-sm-2, col-md-4 or col-xl-8.

        More information can be found using the following URL:
            https://getbootstrap.com/docs/4.0/layout/grid/
    -->

    <div class="container-fluid">
        <div class="row">
            <div class="borderme col-md-8">
                <div class="row">
                    <div class="col">
                        <div class="smalltitle">Test REST api:</div>
                    </div>
                </div>
                <div class="row">
                    <div class="col">
                        GET <a class="larger" href="/quotes">/quotes</a><br/>
                    </div>
                </div>
                <div class="row">
                    <div class="col">
                        GET <a class="larger" href="/quotes/1">/quotes/1</a> <br/>
                    </div>
                </div>
                <form action="/quotes" method="post">
                    <div class="row">
                        <div class="col-xl">
                            POST <a class="reststyle"> /quotes?text=X&author=Y</a>
                        </div>
                        <div class="col-xl">
                            <div class="row">
                                <div class="col-md-4">
                                    Text:
                                </div>
                                <div class="col-md-8">
                                    <input type="text" name="text"/>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-4">
                                    Author:
                                </div>
                                <div class="col-md-8">
                                    <input type="text" name="author"/>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-12">
                                    <input type = "submit"/>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>
            </div>

            <div class="borderme col-md-4">
                <div class="smalltitle">User interface:</div>
                <a class="larger" href="/show_quotes">show quotes (classic)</a><br/>
                <a class="larger" href="/show_quotes_ajax">show quotes (ajax)</a>
            </div>
        </div>
    </div>

    {% include 'footer.html' %}   
</body>
</html>
```

##### Rendering with JavaScript/jQuery/Ajax (client-side) #####
Alternative Jinja2 template example of *rendering client-side* with *ajax* and using *jQuery*: [quotes_ajax.html]
```html
<html>
<head>
	<title>{{app_data['app_name']}}</title>

	<link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">

	<link rel="stylesheet" href="{{ url_for('static',filename='bootstrap-4.0.0.min.css') }}">
	<link rel="stylesheet" href="{{ url_for('static',filename='mystyle.css') }}">

	<script src="{{ url_for('static',filename='jquery-3.2.1.js') }}"></script>
	<script src="{{ url_for('static',filename='bootstrap-4.0.0.min.js') }}"></script>

	<script>
        function load_quotes(f){
            $.ajax({url: "/quotes", type: "GET", dataType: "json"}).done(f);
        }

        function save_quote(text,author,f){
            $.ajax({url: "/quotes", type: "POST", data: {'text': text, 'author': author}});
        }

        function render_quotes(data){
            $("#quotes").empty();
            for(var i=0;i<data.length;i++){
                $("#quotes").append(
                        '<div style="padding: 10px"><span style="font-style: italic;">\"'
                          + data[i]['text']
                          + '\"</span> -- '
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

    <div class="container-fluid">
        <div class="row">
            <div class="col">
                <a href="/">show main</a>
            </div>
        </div>
        <div class="row">
            <div class="borderme col-md-8">
                <div class="smalltitle row">
                    <div class="col">Quotes (A:</div>
                </div>
                <div class="row">
                    <div class="col">
                        <div id="quotes"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="smalltitle row">
                    <div class="col">Add quote:</div>
                </div>
                <div class="row">
                    <div class="col">
                        <form id="addQuoteForm" action="/" method="post">
                                Text: <input type ="text" name="text" id="text"/><br/>
                            Author: <input type ="text" name="author" id="author"/><br/>
                            <input type ="submit" value="save"/>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    {% include 'footer.html' %}   
</body>
</html>
```

### Data layer: ###
Example of data-access pattern [quote_data_access.py] for executing *SQL* queries from python using *psycopg2*

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
        cursor.execute('SELECT id, text, author FROM Quote WHERE id=%s', (iden,))         #See also SO: https://stackoverflow.com/questions/45128902/psycopg2-and-sql-injection-security
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

Example of *unit test* of data access code, see [test_quote_data_access.py]
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

    ....
```

Example of database sql files, see [create_database.sql].
```sql
CREATE ROLE len WITH LOGIN PASSWORD 'len';
ALTER ROLE len CREATEDB;
CREATE DATABASE dbtutor owner len;
```

SQL schema and example data, see [schema.sql].
```sql
CREATE TABLE Quote(
	id SERIAL PRIMARY KEY,
	text VARCHAR(256) UNIQUE NOT NULL,
	author VARCHAR(128)
);

INSERT INTO Quote(text,author) VALUES('If people do not believe that mathematics is simple, it is only because they do not realize how complicated life is.','John Louis von Neumann');
INSERT INTO Quote(text,author) VALUES('Computer science is no more about computers than astronomy is about telescopes','Edsger Dijkstra');
INSERT INTO Quote(text,author) VALUES('To understand recursion you must first understand recursion..', 'Unknown');
INSERT INTO Quote(text,author) VALUES('You look at things that are and ask, why? I dream of things that never were and ask, why not?','Unknown');
INSERT INTO Quote(text,author) VALUES('Mathematics is the key and door to the sciences.', 'Galileo Galilei');
INSERT INTO Quote(text,author) VALUES('Not everyone will understand your journey. Thats fine. Its not their journey to make sense of. Its yours.','Unknown');
```
