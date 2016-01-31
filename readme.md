Arithmetic Simple Service
---------------------------------------------------------------------------------

Requirements:

* Develop a client which is able to send the information given at operations.7z

    ** send the information using sockets to the service

    ** receive information through the sockets and store the results in a file

* Develop a service (python) which is build with the following features:

    ** receive information using sockets

    ** It is built by 2 different processes (at least). Consider having more processes to speed calculations.

    ** Processes must be able to exchange information using PIPES. Please DO NOT use Threading or Pool.

    ** Parent process must create and destroy child process for the arithmetic operations given at operations.7z

    ** Once the arithmetic operation is finished on the second process, such process should be destroyed by the parent process

    ** Consider that operations should not be calculated using EVAL.

    ** Consider using logging instead of console prints

Dependencies:

   see requirements file.


Usage:

   1) Demo mode: launcher.sh script will run service and client in localhost.
   2) Start service with default configuration ( to change them edit config.py ):

         > python service.py

      Run client:

         > python client.py --host host --port port --input-file inputfile [ 7z, txt ] --output-file outputfilename

   3) Run service with parameters:

         >  python service.py [ --verbose ] --host host --port port

      Run client

         > python client.py --host host --port port --input-file inputfile [ 7z, txt ] --output-file outputfilename

    To stop the server kill the process or Ctrl + C

 Enjoy your calculus!







