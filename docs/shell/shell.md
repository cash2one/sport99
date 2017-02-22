#### 进入shell
`python manage.py shell`

#### 创建数据库
`>>>db.create_all()`

#### 创建迁移仓库
`python manage.py db init`

#### 创建迁移脚本
`python manage.py db migrate -m "initial migration"`

#### 更新数据库
`python manage.py db upgrade`

#### 启动服务
`python manage.py runserver`

#### uwsgi启动服务
`uwsgi uwsgi.ini`


