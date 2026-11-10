from flask import Flask, request

app = Flask(__name__)

HTML = """
<!doctype html>
<title>Mini GUI</title>
<h2>Mini GUI – Termux</h2>

<form method="post">
  <input name="text" placeholder="Text eingeben">
  <button type="submit">OK</button>
</form>

<p><b>Ausgabe:</b> {result}</p>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        result = request.form.get("text", "")
        print("Empfangen:", result)
    return HTML.format(result=result)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
