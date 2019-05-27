"""web应用程序框架"""
import re
import time
import traceback
import urllib

from pymysql import connect

TEMPLATES_ROOT = './templates'

# 定义一个字典 存放所有的路径和函数   实现文件和方法的映射
# g_url_func = {
#     '/center.py':center
#     '/index.py': index,
# }

g_url_func = {}


# file_name是文件名
def route(file_name):
    # func是对应的要执行的方法
    def set_url_func(func):
        # 通过装饰器实现 向字典 添加 文件名和方法
        g_url_func[file_name] = func

        def call_func():
            func()

        return call_func

    return set_url_func


@route(r'/index.html')
def index(file_name, url=None):
    """处理index页面数据"""

    # file_name  '/index.py'
    # file_name  '/index.html'
    # 修改后缀名
    file_name = file_name.replace('.py', '.html')

    try:
        # 读取file_name文件的内容
        with open(TEMPLATES_ROOT + file_name, 'r') as f:
            # 获取文件信息
            content = f.read()

            # 模拟一个从数据库查询的数据
            # data_from_mysql = '从数据库查询来的重要数据 呵呵'

            # 1 连接数据库
            db = connect(host='localhost', port=3306, user='root', password='python', database='stock_db',
                         charset='utf8')
            # 2 获取cursor对象
            cursor = db.cursor()
            # 3执行查询语句
            sql = """select * from info"""
            cursor.execute(sql)
            # 4 获取内容
            data_from_mysql = cursor.fetchall()
            # print(data_from_mysql) #注意data_from_mysql是个元组
            # 5关闭cursor
            cursor.close()
            # 6关闭db
            db.close()

            # 前后端不分离  导致后端开发人员也要写一些代码
            # (1, '000007', '全新好', '10.01%', '4.40%', Decimal('16.05'), Decimal('14.60'), datetime.date(2017, 7, 18))
            html_template_item = """
                                <tr>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>
                                        <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s">
                                    </td>
                                </tr>
                                """

            # html_template_all 用来存放拼接后的所有数据
            html_template_all = ''
            for data_item in data_from_mysql:
                # 遍历所有数据 累加每一条
                html_template_all += html_template_item % (
                    data_item[0], data_item[1], data_item[2], data_item[3], data_item[4], data_item[5], data_item[6],
                    data_item[7], data_item[1])

            # 从content里按照参数1的正则 找到内容 被data_from_mysql替换
            # 注意data_from_mysql是个元组
            content = re.sub(r'\{content\}', html_template_all, content)

            # 返回
            return content
    except Exception as e:
        traceback.print_exc()
        print(e)
        return '错误是------%s' % e


@route(r'/center.html')
def center(file_name, url=None):
    """处理center页面数据"""
    # file_name  '/index.py'
    # file_name  '/index.html'
    # 修改后缀名
    file_name = file_name.replace('.py', '.html')

    try:
        # 读取file_name文件的内容
        with open(TEMPLATES_ROOT + file_name, 'r') as f:
            # 获取文件信息
            content = f.read()

            # 1 连接数据库
            db = connect(host='localhost', port=3306, user='root', password='python', database='stock_db',
                         charset='utf8')
            # 2 获取cursor对象
            cursor = db.cursor()
            # 3执行查询语句
            sql = """
                    select i.code,i.short,i.chg,i.turnover,i.price,i.highs,f.note_info from info as i 
                    inner join focus as f on i.id = f.info_id;
                """
            cursor.execute(sql)
            # 4 获取内容
            data_from_mysql = cursor.fetchall()
            # print(data_from_mysql) #注意data_from_mysql是个元组
            # 5关闭cursor
            cursor.close()
            # 6关闭db
            db.close()

            # 前后端不分离  导致后端开发人员也要写一些代码
            #  300268 | 万福生科     | -10.00% | 0.27%    | 31.77 | 13.57 | 你确定要买这个？
            html_template_item = """
                                   <tr>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>
                                            <a type="button" class="btn btn-default btn-xs" href="/update/%s.html">
                                             <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
                                        </td>
                                        <td>
                                            <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s">
                                        </td>
                                    </tr>
                                   """

            # html_template_all 用来存放拼接后的所有数据
            html_template_all = ''
            for data_item in data_from_mysql:
                # 遍历所有数据 累加每一条
                html_template_all += html_template_item % (
                    data_item[0], data_item[1], data_item[2], data_item[3], data_item[4], data_item[5], data_item[6],
                    data_item[0], data_item[0])

            # 从content里按照参数1的正则 找到内容 被data_from_mysql替换
            # 注意data_from_mysql是个元组
            content = re.sub(r'\{content\}', html_template_all, content)

            # 返回
            return content
    except Exception as e:
        traceback.print_exc()
        print(e)
        return '错误是------%s' % e


@route(r'/update/(\d*)\.html')
def update(file_name, url=None):
    # 参数1 file_name    /update/300268.html
    # 参数2 url   r'/update/(\d*)\.html'
    try:
        # 读取file_name文件的内容
        with open(TEMPLATES_ROOT + '/update.html', 'r') as f:
            content = f.read()
            # ------- 1把content里的 {%code%} 替换 为股票的代码
            ret = re.match(url, file_name)
            if ret:
                # 通过正则获取股票代码
                stock_code = ret.group(1)
            else:
                # 没有，就给一个默认值
                stock_code = 0
            print('----------------stock_code-------------------', stock_code)
            # 把content里的 {%code%} 替换 为股票的代码 替换后返回数据覆盖content
            content = re.sub(r'\{%code%\}', stock_code, content)

            # --------2{%note_info%} 替换为备注信息

            # 1 连接数据库
            db = connect(host='localhost', port=3306, user='root', password='python', database='stock_db',
                         charset='utf8')
            # 2 获取cursor对象
            cursor = db.cursor()
            # 3执行查询语句
            sql = """
                   select f.note_info from info as i inner join focus as f on i.id = f.info_id where i.code = %s;
                """ % stock_code
            cursor.execute(sql)
            # 4 获取内容
            stock_info = cursor.fetchone()
            print('------stock_info-------', stock_info)  # 注意stock_info是个元组
            # 5关闭cursor
            cursor.close()
            # 6关闭db
            db.close()
            # {%note_info%} 替换为备注信息
            content = re.sub(r'\{%note_info%\}', stock_info[0], content)

            return content

    except Exception as e:
        traceback.print_exc()
        print(e)
        return '错误是---没有找到 404---%s' % e


@route(r'/update/(\d*)/(.*)\.html')
def update_note_info(file_name, url=None):
    """更新备注信息的方法
        file_name : /update/股票代码/备注信息.html"
    """
    ret = re.match(url, file_name)
    if ret:
        # 获取股票代码
        stock_code = ret.group(1)
        # 获取备注信息
        stock_note_info = ret.group(2)
        # 如果是汉字 那么会被编码 这里需要解码
        stock_note_info = urllib.parse.unquote(stock_note_info)

    else:
        # 有默认值 防止报错
        stock_code = 0
        stock_note_info = ''

    # 1 连接数据库
    db = connect(host='localhost', port=3306, user='root', password='python', database='stock_db',
                 charset='utf8')
    # 2 获取cursor对象
    cursor = db.cursor()
    # 3执行查询语句
    sql = """
    update focus as f inner join info as i on f.info_id = i.id set f.note_info = '%s' where i.code = '%s'
    """ % (stock_note_info, stock_code)
    # print('=====================修改备注信息----------'+sql)
    cursor.execute(sql)
    db.commit()
    # 5关闭cursor
    cursor.close()
    # 6关闭db
    db.close()

    return '更新成功'


@route(r'/add/(\d*)\.html')
def add(file_name, url=None):
    """更新备注信息的方法
        file_name : /add/股票代码.html"
    """
    ret = re.match(url, file_name)
    if ret:
        # 获取股票代码
        stock_code = ret.group(1)
    else:
        # 有默认值 防止报错
        stock_code = 0

    # 1 连接数据库
    db = connect(host='localhost', port=3306, user='root', password='python', database='stock_db',
                 charset='utf8')
    # 2 获取cursor对象
    cursor = db.cursor()

    # 3.判断有没有已经关注过
    sql = """
            select * from info as i inner  join focus as f on i.id=f.info_id where i.code = '%s';
          """ % stock_code
    cursor.execute(sql)
    if cursor.fetchone():
        # 5关闭cursor
        cursor.close()
        # 6关闭db
        db.close()
        return '已经关注过了'

    # 4 没有关注过 去关注  执行insert语句
    sql = """
        insert into focus(info_id) select id from info where code = %s;
        """ % stock_code
    # print('=====================修改备注信息----------'+sql)
    cursor.execute(sql)
    db.commit()
    # 5关闭cursor
    cursor.close()
    # 6关闭db
    db.close()

    return '关注成功'


@route(r'/del/(\d*)\.html')
def delete(file_name, url=None):
    """更新备注信息的方法
        file_name : /del/股票代码.html"
    """
    ret = re.match(url, file_name)
    if ret:
        # 获取股票代码
        stock_code = ret.group(1)
    else:
        # 有默认值 防止报错
        stock_code = 0

    # 1 连接数据库
    db = connect(host='localhost', port=3306, user='root', password='python', database='stock_db',
                 charset='utf8')
    # 2 获取cursor对象
    cursor = db.cursor()

    # 3.判断股票还在不在focus表中
    sql = """
            select * from info as i inner  join focus as f on i.id=f.info_id where i.code = '%s';
          """ % stock_code
    cursor.execute(sql)
    if not cursor.fetchone():
        # 5关闭cursor
        cursor.close()
        # 6关闭db
        db.close()
        return '你没有关注，你取消啥? 你是程序员吧?'

    # 4  如果关注过 去取消关注  执行delete语句
    sql = """
        delete from  focus where info_id = (select id from info where code = "%s");
        """ % stock_code
    # print('=====================修改备注信息----------'+sql)
    cursor.execute(sql)
    db.commit()
    # 5关闭cursor
    cursor.close()
    # 6关闭db
    db.close()

    return '取消关注成功'


# 函数 提供给 web服务器调用的函数
def application(environ, start_response):
    """

    :param environ:  字典 接收服务器传来的数据  请求相关的信息
    :param start_response:服务器传来的函数 用来返回头信息
    :return:
    """
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html; charset=utf-8'), ('Connection', 'Keep-Alive')]
    start_response(status, response_headers)

    # 获取服务器传来的 用户的访问的文件名字
    file_name = environ['PATH_INFO']

    # try:
    # 根据文件名  获取字典的里的函数 执行
    # return g_url_func[file_name](file_name)

    # 遍历字典获取所有的键值对  url和方法 注意url现在都变成了正则
    for url, call_func in g_url_func.items():
        print('正则', url)
        # 用正则匹配 用户访问 的文件名
        ret = re.match(url, file_name)
        if ret:
            # 如果匹配上 就找到对应的方法调用  然后停止循环
            # 把正则表达式url传入方法中 方法方法里用正则 获取数据
            return call_func(file_name, url)
    else:
        # 如果找不到 就返回错误信息
        return str(environ) + '---404---%s\n' % time.ctime()

    # except:
    #     # 如果找不到 就返回错误信息
    #     return str(environ) + '---404---%s\n' % time.ctime()
