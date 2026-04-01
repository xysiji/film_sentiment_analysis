import os
import time

from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from api.movieApi import movieBp
from api.userApi import userBp
from base.core import JSONEncoder
from base.response import ResMsg
from deeplearning.predict_lstm import sentimentalAnalysis_single

app = Flask(__name__)
# 配置CORS
CORS(app)
# 注册用户相关的方法
app.register_blueprint(userBp, url_prefix='/user')
# 注册电影相关的方法
app.register_blueprint(movieBp, url_prefix='/movie')

# ================= 统一数据库配置区 (演示时改这里即可) =================
DB_HOST = '127.0.0.1'
DB_PORT = '3306'  # 统一改为标准 3306 端口
DB_USER = 'root'
DB_PASS = '123456'
DB_NAME = 'flask_douban_comment'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ======================================================================

# 数据库连接池配置
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800  # 每30分钟重连一次
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 5
# 前端返回的JSON用ASCII编码关闭，否则浏览器里面看到的文本会是乱码
app.config['JSON_AS_ASCII'] = False
# Flask必须的配置
app.config['SECRET_KEY'] = 'KJDFLSjfldskj'

UPLOAD_FOLDER = "upload"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'xls', 'JPG', 'PNG', 'gif', 'GIF'])

# 返回json格式转换 使用这个的话就不需要每次都写json返回了，简化代码
app.json_encoder = JSONEncoder

# SQLAlchemy 为ORM框架
db = SQLAlchemy(app)
ma = Marshmallow(app)

@app.errorhandler(500)
def special_exception_handler(error):
    app.logger.error(error)
    return '请联系管理员', 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/file/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    res = ResMsg()
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['myfile']
    if f and allowed_file(f.filename):
        fname = f.filename
        print(fname)
        ext = fname.rsplit('.', 1)[1]
        unix_time = int(time.time())
        new_filename = str(unix_time) + '.' + ext
        f.save(os.path.join(file_dir, new_filename))
    res.update(data=new_filename, code=0)
    return res.data

@app.route('/file/download/<filename>/')
def api_download(filename):
    return send_from_directory('upload', filename, as_attachment=False)

# 深度学习情感分析接口
@app.route('/deeplearning/senti_single', methods=['POST'])
def senti_single():
    res = ResMsg()
    data = request.json['data']
    datas = [data]
    print(datas)
    result = sentimentalAnalysis_single(datas)
    res.update(msg="成功", code=0, data=result)
    return res.data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)