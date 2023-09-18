# Booker
A library project with Django, mysql and Docker

Application available on http://ip_adresse:8000/catalog  

To init the library, upload the ebooks (pdf, epub) in the server directory and launch :  
http://ip_adresse:8000/catalog/init

**configuration.py:**  
storage_directory : define where your books files are stored  
container_mode: set to true to use environment variables (define in .env at
the same level as manage.py)  
  
**.env:**  
Create a .env file at the same level as manage.py  
and set your database configuration

DB_NAME=  
DB_USER=  
DB_PASSWORD=  
DB_HOST=db_mysql  
DB_PORT=3306  

**compose.yaml:**  
Used for development    
In "volumes", define your storage directory for development purpose  
With synology path, take care of the "V" in capital letter  

**docker-compose.yaml:**  
Used for production mode on synology NAS
In "Volumes" define storage directory for production  
In "image" define the version to use