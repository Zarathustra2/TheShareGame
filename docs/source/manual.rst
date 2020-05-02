Manual
======

Key Figures
-----------

Book value
""""""""""
The book value is the sum of the cash and the depot.

Bonds_ in the value will be valued for the price they have been bought.
Shares_ will be valued with their current share price.
Taking this in consideration, one realizes the *book value* can be easily manipulated
by pushing the `share price`_ of a position in the depot.


Share price
"""""""""""
The share price is the last price the share has been traded at.

If the Bid_ is higher than the current share price, then the **Bid** is the new share price.


Ask
"""
The lowest price a company is offering shares for selling is called **Ask**.


Bid
"""
The counterpart is **Bid**, which is the highest price a company is willing to buy shares at.


TTOC
""""
TTOC stands for *Total Turnover Capital*. The idea and implementation of the key figure goes to *BernardCornfeld*.

It represents how much *cash* a company can get immediately.
It is the sum of bonds_, cash and the value of each position that can be sold.

For instance, *Company Global* has *1,000,000* in bonds, *500,000* in cash and the following depot position:

- *Company Europe* 2000 shares

Now one buy order exists for *Company Europe* with a price of *100$* over *1,000* shares.

So the position gets valued as *100$ * 1,000 = 100,000*, as that is the value that *Company Global* can get immediately
by selling. So the total TTOC for *Company Global* is: *1,000,000$ + 500,000$ + 100,000$ = 1,600,000$*.

The TTOC can never be higher than the `book value`_.


Investing
---------

Bonds
"""""
A bond is a fixed rate financial instrument. Companies buy bonds for the current given interest rate.
Bonds have a fixed runtime of 1 to 3 days. After the bond has expired the company receives its
invested money back including the rates.

Bonds are the safest way to invest a companies' cash but also have a low return rate.

.. graphviz::

   digraph bonds {
      "Company" -> "System" [ label="\lInvests \n100$" ];
      "System" -> "Company" [ label="   Pays 100$ + \nrates back" ];
   }


The rate is *higher* the less bonds are in the market, the more bonds are in the market
the *lower* the rate.


Shares
""""""
The heart of the game. If a company buys shares of another company it will become a shareholder of the company.

One can only buy shares of a company if another company is selling shares.

To determine the price of a share, one must interpret the company for them self and take multiple factors in consideration.

For instance there are several key figures such as the *book value*, *ttoc*, *activity* which can be helpful for
making a decision whether the share is overpriced or not.

**But numbers are not everything**. A stock market is always a psychological game. Companies which are active in the chat_, forum_
or newspaper_ have a value which is not represented by any key figure.

Your goal is to find out how other players value companies, how they interpret numbers to determine the price of a share.


Social
------


Chat
""""
The chat is a global place where you can chat with other players and ask questions.


Forum
"""""
The forum is the number one place if you seek a discussion, have an suggestion for the game
or have a question which cannot be answered in the chat as it is to complex.


Fonds
"""""
Fonds are a group of players which seek to work together. Every fond has an intern
forum_ and chat_ which can be used to exchange strategies or discuss the state of the market.


Newspaper
"""""""""
In the newspaper companies can publish articles about everything. It is a good starting to point to
introduce one. Companies can also write something about their strategies or plans for the future.
