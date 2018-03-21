# Udacity Item Catalog

## About the project

This is my implementation for the Item Catalog project for the
Udacity Full Stack Nanodegree (FSND) course.

The Item Catalog is a web application that provides a list of items
within a variety of categories as well as provides a third-party user
registration and authentication system. Registered users will have the
ability to post, edit and delete their own items. Users will be able
to login using either Google or Facebook.

## Requirements
This project was developed and tested using the following:
  * [Python2](https://www.python.org/)
  * [Vagrant](https://www.vagrantup.com/)
  * [VirtualBox](https://www.virtualbox.org/)

Users will also need either a Google or Facebook account to login and
access the full range of features.

## Instructions:

  1. Download and install Python.
  2. Download and install VirtualBox following the instructions on the site.
  3. Download and install Vagrant following the instructions on the site.
  4. Download or clone this repository into the /vagrant/catalog directory.
  5. Run `vagrant up` from the repo directory.  This may take a few minutes.
  6. Run `vagrant ssh` from the repo directory.
  7. Change directory to the catalog directory:
  ```
  $ cd /vagrant/catalog
  ```
  8. Install all python dependencies with the following command:
  ```
  $ pip install -r requirements.txt
  ```
  9. Create the application database using the following command:
  ```
  $ python database_setup.py
  ```
  10. Seed the database using the following command:
  ```
  $ python db_seed.py
  ```
  11. Run the application server using the following command:
  ```
  $ python application.py
  ```
  12. On your host machine, open your favorite browser and navigate to `http://localhost:5000/`.