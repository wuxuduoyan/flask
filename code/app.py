from flask import Flask, render_template
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from Config import APPCONFIG

# 创建一个SQLAlchemy对象 和当前的flask对象关联
db = SQLAlchemy()
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    head_img = db.Column(db.String(200), nullable=True)
    short_description = db.Column(db.String(300), nullable=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Boolean, default=False)  # 是否激活
    activekey = db.Column(db.String(50))  # 激活码

# 发邮件的对象
mail = Mail()


def create_app():
    app = Flask(__name__)

    # 配置session用的SECRET_KEY  相当于一个加密盐
    # app.config['SECRET_KEY'] = '123456abc'

    # 作为flask对象的属性来设置和获取
    # app.secret_key = '123456abc'

    # 1从配置对象中加载(常用)
    app.config.from_object(APPCONFIG['development'])

    # 2从配置文件中加载
    # app.config.from_pyfile('Config.ini')

    # 3从环境变量中加载(了解)
    # app.config.from_envvar('ENV_TEST_CONFIG')

    # 导入过滤器的文件

    from views.admin import admin_blu
    from views.index import index_blu

    # 把蓝图（蓝本）注册到app
    # url_prefix添加前缀 相当于 访问视图的时候 地址是127.0.0.0:5000/index或者admin
    app.register_blueprint(index_blu, url_prefix='/index')  # 前台个人页面的蓝图
    app.register_blueprint(admin_blu, url_prefix='/admin')  # 后台管理的蓝图

    @app.errorhandler(404)
    def internal_server_error(e):
        return render_template('common/404.html')

    # print(app.url_map)

    # print(app.config)
    # print(app.config['SECRET_KEY'])

    # 创建一个SQLAlchemy对象 和当前的flask对象关联
    # db = SQLAlchemy(app)
    db.init_app(app)  # 和当前的flask对象关联

    mail.init_app(app)  # 和当前的flask对象关联

    return app
if __name__ == '__main__':
    # 创建flask对象
    app = create_app()
    # 启动
    app.run(port=10000)