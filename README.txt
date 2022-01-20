In order to run, this the only library that is necessary beyond standard
python libraries is the flask micro framework.

Python can easily be downloaded from the internet, any python3 version should
work fine.

To install Flask you first need to install the python installer program (pip).
You can check if you already have pip with the command "$pip3 help"
If pip responds you can skip this step, otherwise I suggest following the
pip installation guide at "https://pip.pypa.io/en/stable/installation/"

Once pip is installed, Flask can be added using the command 
"$pip3 install Flask"

Now that Flask is installed, and all the files are in the same folder
"$python3 app.py" should start the web server. Starting the web server will
return a bunch of text. The web server will be hosted at the link next to
the " *Running on" line ("http://127.0.0.1:5000/"). Pasting this into any 
modern web browser will take you to the server. The server can be closed using
CRTL+C back in the terminal or command prompt where it was started.

Example text after starting app.
 * Serving Flask app 'app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 113-246-181