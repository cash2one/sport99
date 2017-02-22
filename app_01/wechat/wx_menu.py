# coding=utf-8
__author__ = 'Van'


def menu(domain):
    return {
        'button': [
            {
                'name': '去运动',
                'type': 'view',
                'url': domain + "/#/events"

            },
            {
                'name': '俱乐部',
                'sub_button': [
                    {
                        'type': 'view',
                        'name': '发布活动',
                        'url': domain + "/#/events/create_step1"
                    },
                    {
                        'type': 'view',
                        'name': '创建俱乐部',
                        'url': domain + "/#/clubs/create_step1"
                    }
                ]
            },
            {
                'name': '个人信息',
                'sub_button': [
                    {
                        'type': 'view',
                        'name': '我的俱乐部',
                        'url': domain + "/#/clubs"
                    },
                    {
                        'type': 'view',
                        'name': '我的活动',
                        'url': domain + "/#/mine_events"
                    },
                    {
                        'type': 'view',
                        'name': '设置',
                        # 'key': 'V1001_GOOD'
                        'url': domain + "/#/info_set"
                    }
                ]
            }
        ]}
