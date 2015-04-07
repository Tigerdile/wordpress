# Class for interfacing with WordPress
#
# At this time, it allows you to read the wp-config.php's parameters
# and it provides WordPress cookie authentication checking.
#
# This could be expanded upon a lot, but just the implementation
# of the WordPress cookie authentication in Python is worth a lot.
#
# Released under Public Domain with no warranty.
# By : Tigerdile, LLC    https://www.tigerdile.com

import time, hmac, logging, hashlib, re

class WordPress(object) :
    #
    # @param str
    #
    # The init call requires the WordPress base path where wp-config.php lives
    #
    def __init__(self, basepath) :
        self._path = basepath

        # Try to open it
        wpconfig = None
        with open("%s/wp-config.php" % basepath, "r") as content_file :
            wpconfig = content_file.read()

        if wpconfig == None or not len(wpconfig) :
            raise Exception("Could not open or load wordpress configuration.")

        # Regex out what we want.
        self._params = { }

        for x in re.finditer("[\"'](.*)[\"'],\s*[\"'](.*)[\"']", wpconfig) :
            self._params[x.group(1)] = x.group(2)

        # Table prefix has to be added special, because it's a unique snowflake.
        matches = re.search("table_prefix\s*=\s*[\"'](.*)[\"\']", wpconfig)

        if matches :
            self._params["table_prefix"] = matches.group(1)

        # Compute our "logged_in" scheme salt
        self._salt = ("%s%s" % (self._params["LOGGED_IN_KEY"], self._params["LOGGED_IN_SALT"])).encode()


    # @param str (optional) WordPress define key
    # @return str
    #
    # Get a WordPress config parameter.  Only reads WordPress "define"s
    # in wp-config.php at this time.
    #
    # If no argument provided, will return entire dictionary of defines.
    def get(self, param = None) :
        if param == None :
            return self._params

        return self._params[param]

    # @return str
    #
    # Get WordPress base path
    #
    def getBasePath(self) :
        return self._path

    # NOTE : This will only work if you define COOKIEHASH in your wp-config.php!
    #
    # Validate a WordPress cookie
    #
    # @param str           Username
    # @param str           "Password fragment", the user's password range [8:12]
    # @param str|int       Expiration in UNIX timestamp, from the Word Press cookie
    # @param hmac_compare  hmac_compare from WordPress cookie
    # @param token         Token from wordpress cookie
    # @return bool
    #
    # WordPress cookies are | separated.  If you're using tornado, you can call
    # like this :
    #
    # 
    # wordPressCookie = self.get_cookie("wordpress_logged_in_%s" % wordpressConfig.get("COOKIEHASH"))
    #
    # # User has not logged into WP
    # if wordPressCookie == None :
    #   (handle not logged into WP)
    #
    # # Get WP User information -- see if we are already chat-authorized
    # wpCreds = tornado.escape.url_unescape(wordPressCookie).split("|")
    #
    # if (len(wpCreds) < 4) or not len(wpCreds[0]) :
    #   (handle cookie is broken)
    #
    # (Load user password from DB, compute fragment : it's password[8:12]
    #
    # # Validate the cookie
    # if not wordpressConfig.validateCookie(wpCreds[0], passwordFragment,
    #                                       wpCreds[1], wpCreds[3], wpCreds[2]) :
    #   (handle invalid login / login timed out)
    #
    # (If it's survived this far, user is authenticated)
    #
    def validateCookie(self, user, pass_frag, expiration, hmac_compare, token) :
        if int(expiration) < int(time.time()) :
            logging.debug("Denying user %s due to expired cookie." % user)
            return False

        key = hmac.new(self._salt, ("%s|%s|%s|%s" % (user, pass_frag, expiration, token)).encode(), hashlib.md5).hexdigest().encode()
        hash = hmac.new(key, ("%s|%s|%s" % (user, expiration, token)).encode(), hashlib.sha256).hexdigest().encode()

        # TODO (if I cared) : check user meta table for key 'session_tokens'
        # That will be a php encoded array of sessions.  Token is hashed
        # with sha256 and compared to what's in that array
        #
        # I really don't think I care, this is plenty secure for chat.

        return (hmac.new(key, hmac_compare.encode(), hashlib.md5).digest() == hmac.new(key, hash, hashlib.md5).digest())

