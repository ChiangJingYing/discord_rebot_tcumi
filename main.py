import requests

import pandas as pd


class PointGeter:
    def proccess(self, **kwargs):
        try:
            ses = self.__login(number=kwargs['number'], password=kwargs['password'])
        except requests.exceptions.HTTPError:
            self.result = "HttpError(login)"
        except requests.exceptions.ConnectionError:
            self.result = "Website Error"
        except ValueError:
            self.result = 'Username or password not correct'
        else:
            self.result = self.__analyse(ses=ses)

    def __login(*args, **kwargs):
        ses = requests.Session()
        url = 'https://ican.tcu.edu.tw/login.aspx'
        data = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": '/wEPDwUJODg4OTg2MDQxD2QWAgIDD2QWAgIBD2QWAgIBD2QWBAIDD2QWAgIBD2QWAgIBDxBkZBYAZAIVD2QWAgIBD2QWAgIBDxBkZBYAZGRQ6KK53rQ52Qwwp8pr1B15z65w2Mb47omIhaas9cLyuQ==',
            "__VIEWSTATEGENERATOR": 'C2EE9ABB',
            "__EVENTVALIDATION": '/wEdAARrrcQ17zGL6HR/D1iqN/JRgwjh6STpseSMslTXnfzysD40AZ9v3xd7rnq+UnqBeXKinihG6d/Xh3PZm3b5AoMQCGiM2zxXas41LeOTeK4ZlTMEPnUgEJJ7TlG6kGOM3cU=',
            'tbManNo': kwargs['number'],
            'tbPwd': kwargs['password'],
            "btnLogin": "登入"
        }
        login_post = ses.post(url, data=data)
        if login_post.status_code == 200 and login_post.url == 'https://ican.tcu.edu.tw/default.aspx':
            return ses
        elif login_post.url == 'https://ican.tcu.edu.tw/error/ErrorAccountPwd.aspx':
            raise ValueError
        else:
            raise requests.exceptions.HTTPError

    def __analyse(*args, **kwargs):
        ses = kwargs['ses']
        response = ses.get('https://ican.tcu.edu.tw/course/course.aspx')
        table = pd.read_html(response.text)
        title = table[0].columns.values
        table[1].columns = title
        table.remove(table[0])

        count = table[0].shape[0] + 1
        new_table = table[0]
        while count < len(table):
            table[count].columns = title
            new_table = pd.concat([new_table, table[count]], join='outer')
            count += table[count].shape[0] + 1

        class_required = new_table[
            (~new_table['課程系組'].isin(['通識  1  A', '體育  1  A'])) & (new_table['必選修別'] == '必修 / Required') & (
                new_table['成績'] >= 60)]['學分數'].sum()
        class_elective = new_table[
            (~new_table['課程系組'].isin(['通識  1  A', '體育  1  A'])) & (new_table['必選修別'] == '選修 / Elective') & (
                new_table['成績'] >= 60)]['學分數'].sum()
        general = new_table[(new_table['課程系組'].isin(['通識  1  A', '體育  1  A'])) & (new_table['成績'] >= 60)][
            '學分數'].sum()
        print(f'必修： {class_required}')
        print(f'選修： {class_elective}')
        print(f'通識： {general}')
        return f'必修： {class_required}\n選修： {class_elective}\n通識： {general}'