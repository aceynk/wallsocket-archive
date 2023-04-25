Wallsocket-Archive was created to index and archive subdirectories of domains present in the underscores 'Wallsocket' ARG (Alternate Reality Game). It archives and creates logs every 1 hour, adjusting to run exactly on the hour (GMT).

Instructions for reading/handling logs can be found in src/log/LOG.txt.

To add domains, simply write the valid domain (no https:// or /) on a new line. Running the program again should allow it to index that new domain, or you can wait for it to next run the hourly cycle.

src/archive is a folder of archived site data, the basic html obtained from the site. This shouldn't be edited.

If you want to run this on your own computer, cd into the folder you want the repository in and run:

``git clone https://github.com/aceynk/wallsocket-archive``

After that, the archiving loop can be initiated with (where '...' is a placeholder for the directory to the index.py file):

``python3 .../index.py``

This script will need to remain active to continue archiving.