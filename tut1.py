from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
@app.route("/souras")

def hello_souras():
    return " hello, souras e"

@app.route("/html-template")
def html_run():
    return render_template("index.html")

#making variable in python file and send it to html file
@app.route("/variable-html")
def variable_html():
    name="souras"
    return render_template("var-template-file.html",name2=name)


app.run(debug=True)