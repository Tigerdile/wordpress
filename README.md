# wordpress
Wordpress Integration Module for Python

This is a very simple Python module that reads wp-config.php and parses the defines in it.  Admittedly, that's not a lot of value.  The value lies in the module's ability to validate WordPress session cookies, which took me a good deal of digging to implement correctly.

As of right now, it does not validate the WordPress cookies against the database.  A useful addition would be the ability for this module to interface with the database.  Tigerdile has a special database caching module that I wrote -- the module is kind of clunky and not really of general use; I should add those features to this module and make it more interesting.  But for now, here's what I've got!

Read the comments to see how it works!

# License
This module is Public Domain with no warranty.  Feel free to use it as you see fit.  It'd be awful nice, though not required, to keep the Tigerdile, LLC credit at the top of the file.

