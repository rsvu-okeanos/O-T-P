# O-T-P
The Okeanos Trading Platform is a small app for setting prices interactively during a drink at my rowing club, Okeanos Amsterdam. 

At one point in time I had the idea of writing a small wrapper around our digital cash register so I could track transactions made. One idea led to another, and after some time I came up with the idea of dynamically adapting prices to the demand.

The app exposes a websocket over which the updated prices are pushed on a given interval (see app/conf/config.yml). Also, the app exposes a small REST api to facilitate individual trading between customers (i.e. they can sell any products bought from the bar to eachother). 