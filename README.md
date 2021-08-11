# Essence-of-Life
A web application for managing organ donation and transplantation.

It is based flask based application with mysql and mongodb as the backend.
Here you can:
1. Register a government
2. Register a organization which acts as the organ bank.
3. Add recievers and donors
4. Add transplantation details
5. Get analytics with respect to the transplantation and donation details ( this is fetched through mongodb )

to execute this project clone the repository and make sure you have mysql and monogdb installed in your system.
You can also create a local cluster on MongoDb Atlas to access the mongodb part.
Change username and password in db.yaml file to connect to mysql database and change the mongo_uri based on the circumstance.
to include email functionality create a config file with username='your_username' and password='your_password'

