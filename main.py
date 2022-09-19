from datetime import datetime
import json
import os
from random import random
import string
from flask import Flask, redirect, render_template, request, send_file, url_for, Response
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "/static/images"
app.config["MAX_CONTENT_PATH"] = 50 * 1024 * 1024
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///utils/app.db"
db = SQLAlchemy(app)


class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(20))
    ext = db.Column(db.String(20))
    created = db.Column(db.String(68))


def random_name():
    return "".join(random.choices(string.ascii_lowercase, k=5))


def filename():
    random = random_name()
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    for file in files:
        while random == file:
            random = random_name()
        continue
    return random


@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template('index.html')


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, n):
        yield l[i::n]


@app.route('/images/<page>', methods=['GET'])
def view_images(page: int):
    if request.args.get("pswdpin") != '0p;1043%<AJ832£LDOwdhf9':
        return redirect(url_for("index"))

    images = Images.query.order_by(Images.created.desc()).paginate(
        page=int(page), per_page=21
    )

    files_list = []
    list_meta = list(chunks(images.items, 3))
    for file in images.items:
        filename, ext = file.filename.rsplit(".", 1)
        files_list.append([file, ext])

    return render_template(
        "images.html",
        file_amount=images.total,
        files_list=files_list,
        paginator=images,
        images=images.items
    )


@app.route('/i/<fn>')
def view_image(fn):
    try:
        filename2 = "images/" + fn
        return send_file(filename2, attachment_filename=fn)
    except:
        return redirect(url_for("index"))


@app.route("/api/v1.0/images/upload", methods=["POST"])
def api_image_upload():
    if request.method == "POST":
        image = request.files["api_image"]
        key = request.form.get("api_key")
        if key == "29u2q98dhq2dq'2qd09q2u3d#2qdq209hdj":
            ext = image.filename.rsplit(".", 1)[1].lower()
            if ext not in [
                "png",
                "jpg",
                "jpeg",
                "gif",
                "txt",
                "py",
                "json",
                "mp4",
                "pdf",
            ]:
                return Response(
                    response=json.dumps({"error code": "20"}),
                    status=404,
                    mimetype="application/json",
                )
            file = filename() + "." + ext
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], file))
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            img = Images(
                filename=file,
                ext=ext,
                created=now
            )
            db.session.add(img)
            db.session.commit()

            response = {
                "message": "image received",
                "url": f"https://harrysmith.dev/i/{file}",
            }

            return Response(
                response=json.dumps(response), status=200, mimetype="application/json"
            )


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)