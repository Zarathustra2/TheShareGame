Editor
======

Vim
---
For creating tags a custom ctags is provided in **.ctags.d/thesharegame.ctags**.
Now run from the root of the project::
    
    > ctags -R .

I use on tab for *frontend* directory and one tab for the *backend* directory.

Each directory - *frontend*, *backend*, *chat* - has is own Makefile for executing
a couple of *make* commands.

Use::

    > make help

to get a full list of all commands with an explanation.

Pycharm
-------
First make sure that the execution of the::
    
    > cd backend/
    > make deps 

has been successful.

Then import the whole project.

Now right click on the directories *backend* and *frontend* and hit::

    > Mark Directory as => Sources Root


It is common in Vue to write import statements like this:
    
    .. code-block:: javascript
    
        import Headline from "@/components/Headline.vue"

*@* is an alias for *src*, which *Pycharm* does not understand natively. To resolve this in *Pycharm* do::

    > Preferences => Languages & Framework => Webpack
    > /node_modules/@vue/cli-service/webpack.config.js

Now *Pycharm* can resolve *@* correctly.
