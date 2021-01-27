# README #
Implementation of example web application in python with relational database. By Len Feremans, Sandy Moens and Joey De Pauw, assistants at the University of Antwerp (Belgium) within the Adrem data lab research group.

### What is this repository for? ###
Tutorial for Programming Project Database students, or persons interested in creating a web application in python.

We depend on the following technologies:

![stack](https://github.com/joeydp/PPDB-Template-App/blob/master/doc/stack.png?raw=true "Stack")

### Quick start ###
The implementation is written in Python.

#### 1. Postgres database and Python interface (server version may vary)
```bash
sudo apt install postgresql postgresql-server-dev-9.6 postgis python-psycopg2
```


#### 2. Create the database
First configure the database with `postgres` user:
```bash
sudo su postgres
psql
```
Then create a role 'app' that will create the database and be used by the application:
```sql
CREATE ROLE app WITH LOGIN CREATEDB;
CREATE DATABASE dbtutor OWNER app;
```

You need to 'trust' the role to be able to login. Add the following line to `/etc/postgresql/9.6/main/pg_hba.conf` (you need root access, version may vary). It needs to be the first rule (above local all all peer).
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# app
local   dbtutor         app                                     trust
```
and restart the service. Then initialize the database:
```bash
sudo systemctl restart postgresql

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

### Create GCP instance

Follow these steps to create a GCP compute instance.

#### 1. Create one GCP project and give every team member access
Via the console <https://console.cloud.google.com/>, you can create a project and add your team members.

#### 2. Create a Compute instance (VM)

These screenshots explain how to create a VM instance. Feel free to change any settings, this is only a suggestion, but make sure you have enough credit until the end of the semester.

![create vm0](https://github.com/joeydp/PPDB-Template-App/blob/master/doc/GCP/vm_create0.png?raw=true)

![create vm1](https://github.com/joeydp/PPDB-Template-App/blob/master/doc/GCP/vm_create1.png?raw=true)


#### 3. Set static IP address and add Firewall rule

Then in the settings of your instance, under network iterfaces, click `View details`.

![create vm](https://github.com/joeydp/PPDB-Template-App/blob/master/doc/GCP/instance.png?raw=true)

![create vm](https://github.com/joeydp/PPDB-Template-App/blob/master/doc/GCP/network_overview.png?raw=true)

This brings you to the network configuration page. Here you need to set the external IP address to static:

![create vm](https://github.com/joeydp/PPDB-Template-App/blob/master/doc/GCP/network_static.png?raw=true)

And create a new firewall rule if you want to run the debug server on port `5000`.

![firewall](https://github.com/joeydp/PPDB-Template-App/blob/master/doc/GCP/firewall_create.png?raw=true)

#### 4. Add SSH keys

In the VM settings, you can add SSH keys for each team member. The next step explains how to generate an SSH key, if you already have one, you can skip this step.

> (Optional) Create SSH key
>
> Use `ssh-keygen` to generate a private and public ssh key-pair. This is used to securely login to the remote server. Follow the instructions of this command. After this, a public and private key file will be created respectively `~/.ssh/id_rsa.pub` and `~/.ssh/id_rsa`.

Copy the contents of `~/.ssh/id_rsa.pub` to the VM instance.

#### 5. Test your connection

You should now be able to connect to the server with `ssh [username]@[external ip]`.

>Optionally you can add the following lines to `~/.ssh/config`:
>```
>Host ppdb
>    Hostname [external ip]
>    User [username]
>```
> Then you can connect simply with `ssh ppdb`



### Run on GCP using nginx and gunicorn

These steps demonstrate how to run this application with nginx. They are to be executed in addition to the setup in quick start. Instead of running the built in Flask debug server, we use an industrial grade webserver and reverse proxy server: nginx.

#### 1. Install dependencies
```bash
sudo apt install nginx
```

#### 2. Create user to run application
```bash
sudo useradd -m -s /bin/bash app
sudo su - app
```

#### 3. Clone the application in /home/app
```bash
git clone https://github.com/JoeyDP/PPDB-Template-App.git
```

#### 4. Follow Quick start to setup the project

#### 5. Test if wsgi entrypoint works
Instead of using the Flask debug server, we use gunicorn to serve the application.
```bash
cd src/ProgDBTutor
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

#### 6. Enable the webservice
As an account with sudo acces (not app), copy the file `service/webapp.service` to `/etc/systemd/system/` and enable the service:

```bash
sudo ln -s /home/app/PPDB-Template-App/service/webapp.service /etc/systemd/system/

sudo systemctl enable webapp
sudo systemctl start webapp
```
A file `src/ProgDBTutor/webapp.sock` should be created.

#### 7. Setup nginx
Link or copy the nginx server block configuration file to the right nginx folders:
```bash
sudo ln -s /home/app/PPDB-Template-App/nginx/webapp /etc/nginx/sites-available/
sudo ln -s /home/app/PPDB-Template-App/nginx/webapp /etc/nginx/sites-enabled/
```

The contents of this file can be changed for your setup. For example change the IP address to your external IP and add the correct DNS name (`team[x].ppdb.me`)
```
server {
    listen 80;
    server_name 0.0.0.0 ppdb.me;

location / {
  include proxy_params;
  proxy_pass http://unix:/home/app/PPDB-Template-App/src/ProgDBTutor/webapp.sock;
    }
}
```

Test the configuration with `sudo nginx -t`.

#### 8. Restart the server

Restart the server with `sudo systemctl restart nginx`. Your application should be available on port 80.
