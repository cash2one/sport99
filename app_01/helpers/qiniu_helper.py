# -*- coding: utf-8 -*-
__author__ = 'Van'
from qiniu import Auth
qiniu_access_key = "-49vt6XfIHSgDHY4yKM-efC7kId8Yy0N0_QOwPPW"
qiniu_secret_key = "2Gy12f21qDjo358ep48774zUQ6txO5SxgnsL2XaC"
qiniu_bucket_name = "mr-van-apps"


def get_token(key):
    q = Auth(qiniu_access_key, qiniu_secret_key)

    # 上传策略仅指定空间名和上传后的文件名，其他参数仅为默认值
    token = q.upload_token(qiniu_bucket_name, key)

    return token