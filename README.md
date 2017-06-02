# Plant Catalog

This repository contains code for the **Item Catalog** project, which is part of the Udacity Full-Stack Web Developer nanodegree.

In this project, I developed a web application which provides a catalog of plant items within a variety of plant categories. It integrates third-party user registration and authentication. Once authenticated, users have the ability to create, edit, and delete their own plant items.

This project is built within a virtual machine implemented with VirtualBox and Vagrant. The Vagrant VM is a Linux server that runs on top of your computer. This is used to run a SQLalchemy database server and the Flask web apps that employ it.

### Plant Catalog Features

This application has the following features:

* The `/catalog` or `/` page is the home page for this application and displays a list of all the plant categories and the most recent plant items added to the catalog.
* The `/catalog/<category>` pages displays all the plant items belonging to the specified category.
* The `/catalog/<category>/<plant>` pages display the details of a particular plant entry.
* Authenticated users have the ability to create new plant items, as well as edit and delete the items that they have created. Forms are provided for each of these functions.
* Only authenticated users can add or update items in the database. They are prohibited from updating plant items that they do not own.
* Login is provided via 3rd-party authentication and authorization. Users with Google accounts can log into this application via Google. A link to the `Login` (or `Logout`) page is provided in the application header.
* The `/catalog/JSON`, `/catalog/<category>/JSON`, and  `/catalog/<category>/<plant>/JSON` pages provide JSON endpoints that display information on the entire plant catalog, plants within a category, or a particular plant respectively.

### Even more about the Plant Catalog

Within this repository, you will find the following files that comprise this application:

* `database_setup.py` - This file contains the `Users`, `PlantCategory`, and `PlantItem` database tables needed for this application. Run this Python code to set up the database.
* `lotsofplants.py` - This file contains Python code that populates the database with all the plant categories and a bunch of sample plant items.
* `application.py` - This is the main Python code that runs the Flask web application for the catalog.
* `client_secrets.json` - This JSON file contains the client ID and secret data needed by Google APIs to handle 3rd party Google Authentication.
* `templates/*.html` - This subdirectory contains all the HTML templates for the web pages in this application.
* `static/images/` - This subdirectory contains all the sample plant images, banners, and other image assets needed to render the preliminary pages.
* `static/styles.css` - The CSS styles for formatting the web pages.

### How to run the Plant Catalog

1. To run this code, you will first need to install VirtualBox and Vagrant on your machine. (See the instructions in the section below for how to do this.)

2. Next, you will need to download the source code for the VM configuration. This can be found here in the [fullstack-nanodegree-vm repository](https://github.com/udacity/fullstack-nanodegree-vm).

3. Next, download the catalog repository from my Github onto your machine and install it in the `/catalog` subdirectory in the Udacity VM repo.

4. To start the Virtual Machine:

  * Navigate to the `vagrant` subdirectory within your terminal window.
  * Run `vagrant up` to start the virtual machine. This generates lots of messages and may take a while. When finished, you will get your shell prompt back.
  * Run `vagrant ssh` to login into the Vagrant VM. (*Note:* Type `exit` or `Ctrl-D` to end the session and logout.)

5. Once in Vagrant VM, navigate to the catalog subdirectory using `cd /vagrant/catalog`.

6. Load the database by running `python database_setup.py` in your VM window.

7. Populate the database with preliminary plant data by executing `python lotsofplants.py` in your VM.

8. To allow for 3rd Party Authorization, you'll need to set up a Google project with OAuth credentials in your Google APIs Console - [https://console.developers.google.com/apis](https://console.developers.google.com/apis). Download your client ID and secret and save them a file called `client_secrets.json` in the `/catalog` subdirectory. Also copy your client ID into the `data-clientid` field in  `templates/input.html`.

9. Run the application by executing `python application.py` in your VM window.

10. Open your favorite browser and test the application locally by visiting [http://localhost:8000](http://localhost:8000)


### Installing VirtualBox and Vagrant

VirtualBox is software that actually runs the VM. You can download it from [https://www.virtualbox.org/wiki/Downloads](https://www.virtualbox.org/wiki/Downloads). Install the appropriate package for your operating system. You do not need the extension pack or the SDK. Don't launch VirtualBox after installation. We'll do that later with Vagrant.

Next, install Vagrant. You can download Vagrant from [https://www.vagrantup.com/downloads.html](https://www.vagrantup.com/downloads.html). Install the appropriate version for your operating system. If successfully installed, it will display the version number when you run `vagrant --version` in your Unix-style terminal window.

#### Attributions

This project is part of Udacity's Full-Stack Web Developer nanodegree. The source code for the VM configuration and database projects can be found here in the [fullstack-nanodegree-vm repository](https://github.com/udacity/fullstack-nanodegree-vm).
