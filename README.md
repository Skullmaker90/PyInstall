Introduction
======

This is a script to be deployed on new Centos 6 servers to allow a "One-Click" install of cPanel, Plesk, Wordpress, Webmin, Joomba, PrestaShop and LNMP Stack. 
This was orignally written by Anthony Smith on 4/24/2016 and will be updated and expanded periodically according to needs. Please 
direct all questions/concerns/suggestions to asmith@cari.net.

Installation
=======

There's a couple ways to download the script but the quickest would be to curl it. Since gitlab requires auth I'll be using my public 
github to host the file. To download using curl just cd to the desired directory and `curl -O https://raw.githubusercontent.com
/Skullmaker90/PyInstall/master/dl.py` and run it with `python dl.py`

Usage
=======

Once downloaded usage is as easy as `python panelinstall.py` and selecting an option. Speaking of:

cPanel
-----------

Downloads the latest installer to the configured directory and runs it using default settings. It seems as though cPanel opens it's own ports 
so no needed to run anything through the port_engine.

Plesk
-----------

Downloads latest version, installs Full and sends an email to service when finished. Will be adding this functionality to all commands 
eventually but currently this is working just fine. Opens plesk port 8443 afterwards.

LAMP Stack
------------

This installs your standard Apache, MySQL, Php configuration and in doing so automates the mysqld secure install process. Must specify 
password for root mysql user as this is when it'll be created. Opens http port after so please check for Apache start page when process is 
complete.

Wordpress
------------

By far the most irritating of the 4. Must specify both a root mysql user password **AND** a wordpress user password. Most config options 
reside here with the ability to specify the WP database name, and user. Upon selection prompts for both passwords, does a LAMP Stack install 
then proceeds with the download and configuration of Wordpress. Opens http port please check https://Server_Ip_Here/wp-admin/install.php to 
verify installation.

Misc.
=========

Default-Config.cfg
-----------

This is the file that is used for configuration settings in the script. currently just leave as is with name and sections, just change values 
as needed until I finish implementing a proper config file. Will update here once that is complete.
