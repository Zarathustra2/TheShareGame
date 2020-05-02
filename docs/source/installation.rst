Installation
============

If you want to run the whole project on your local machine, make sure you have installed the following pre requirements:

- `Redis <https://redis.io/>`_ (Backend)
- `Python3 & Pip3 <https://www.python.org/>`_ (Backend Django)
- `Postgresql <https://www.postgresql.org/>`_ (Backend)
- `Npm <https://www.npmjs.com/>`_ (Frontend)
- `Golang <https://golang.org/>`_ (Backend Chat)

If you are on Mac and use `Homebrew <https://brew.sh/>`_ run::

    > brew install postgresql redis go npm

If you use a Mac consider also running::

    > /usr/local/opt/postgres/bin/createuser -s postgres

Afterwards run the following command from your terminal::

    > git clone git@github.com:Zarathustra2/TheShareGame.git
    > cd TheShareGame
    > make deps

This will install dependencies for the frontend_ & backend_.

Verify the installation by running::
    
    > make test

If you no errors have been reported then you are good to go!

Backend
-------
The backend consists of multiple parts: *api*, *web sockets*, *queue*, *worker*.


Api
"""
`Django <https://www.djangoproject.com/>`_ is the used framework for the api.

All of the code is located in the folder *backend*.


Queue & Worker
""""""""""""""

The *queue* and *worker* are responsible for running periodic tasks such as:

- Bond payout
- Order matching
- etc.

Moreover, it allows us to let the `Django <https://www.djangoproject.com/>`_ api communicate
with the `Golang <https://golang.org/>`_ web sockets.

Frontend
--------

Work only on Frontend
"""""""""""""""""""""

In case you only want to work on the frontend, run::
    
    > cd frontend
    > make deps

This will install only the dependencies for the frontend.

Verify the installation by running::
    
    > cd frontend
    > make test

To start the development server run::
    
    > cd frontend
    > make runserver-live-backend

This will connect the frontend with the current deployed backend.

Work with local backend
"""""""""""""""""""""""

To connect the frontend with the local Backend_ run::

    > cd frontend
    > make runserver
