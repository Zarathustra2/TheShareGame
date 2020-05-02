## Backend

The backend is written in [Django](https://www.djangoproject.com/) expect the chat which is written in [Golang](golang.org).

#### Table of Contents
- [Code Distribution](#code-distribution)
- [Why Go for the chat](#why-go-for-the-chat)
- [Commands](#commands)


## Code Distribution
Code is distributed in the following "apps":
- [common](common) - Contains generic base functionality such as pagination, test util etc.
- [core](core) - Contains the majority of the code and everything related to the stock market
- [fonds](fonds) - Contains all that is related to fonds
- [periodic tasks](periodic_tasks) - Contains all the tasks that need to be executed every X minutes.
- [stats](stats) - Contains everything related to gather statistics 
- [tsg](stats) - Contains the settings.py (The heart of a django project)
- [users](users) - Contains all that is related to socializing, for instance: Forum, Newspaper, Users
- [chat](chat) - Contains the chat code basis

## Why Go for The Chat
I could have used [Django Channels](https://github.com/django/channels) but currently it is not maintained actively, and it is on a 
best effort basis.

I also wanted to become a better golang programmer, so I started writing the chat in go.
 

## Commands

#### Start the Dev server
```bash
> make runserver
```

#### Run tests
```bash
> make test
```

#### Start the chat server
```bash
> cd chat
> make runserver
```
