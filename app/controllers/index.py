__author__ = 'Van.zx'

from flask import Blueprint, render_template

main = Blueprint('h5', __name__)  # url_prefix='/h5'


@main.route('/', methods=['GET'])
def h5_index():
    return render_template("index.html")