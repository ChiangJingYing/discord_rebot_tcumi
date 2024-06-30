import requests
import pandas as pd

from fake_useragent import UserAgent


class PointGeter:
    def proccess(self, **kwargs):
        try:
            html_content = self.__login(
                number=kwargs['number'], password=kwargs['password'])
        except requests.exceptions.HTTPError:
            self.result = "HttpError(login)"
        except requests.exceptions.ConnectionError:
            self.result = "Website Error"
        except ValueError:
            self.result = 'Username or password not correct'
        else:
            self.result = self.__analyse(html_content=html_content)

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
        header = {
            "Accept-Encoding": "gzip",
            'user-agent': UserAgent().random
        }
        login_post = ses.post(url, data=data, headers=header)

        if login_post.status_code == 200 and login_post.url == 'https://ican.tcu.edu.tw/default.aspx':
            # response = ses.get('https://ican.tcu.edu.tw/course/course.aspx')
            response = ses.get(
                'https://ican.tcu.edu.tw/ScoreManager/score_history.aspx')
            ses.get('https://ican.tcu.edu.tw/Logout.aspx')
            return response
        elif login_post.url == 'https://ican.tcu.edu.tw/error/ErrorAccountPwd.aspx':
            raise ValueError
        elif login_post.url == 'https://ican.tcu.edu.tw/login.aspx':
            raise ValueError
        else:
            raise requests.exceptions.HTTPError

    def __analyse(*args, **kwargs):
        html_content = kwargs['html_content']
        table = pd.read_html(html_content.text)
        title = ['身分', '課程系組', '課程名稱', '科目代碼', '必選修別', '學分數', '成績']
        table[1].columns = title
        table.remove(table[0])

        count = 1
        new_table = table[0]
        while count < len(table):
            table[count].columns = title
            new_table = pd.concat([new_table, table[count]], join='outer')
            count += 1

        # 修正抵免學分 分數
        new_table.loc[new_table['成績'] == '抵', '成績'] = 60

        # 修改欄位資料型態
        new_table['學分數'] = new_table['學分數'].astype(int)
        new_table.loc[pd.isna(new_table['成績']), '成績'] = 0
        new_table['成績'] = new_table['成績'].astype(int)

        # 分離通識學分
        general = new_table[(new_table['課程系組'] == "通識  1  A")
                            | (new_table['課程系組'].isna())]
        new_table = pd.concat([new_table, general, general]
                              ).drop_duplicates(keep=False)

        # 修正 通識必選修別：通識->必修
        general.loc[general['課程名稱'].str.contains(
            r"生命教育.*|中文閱讀與書寫.*|慈濟人文暨服務教育.*|網頁視覺程式設計.*|基礎英文.*"), '必選修別'] = '必修'

        # 分離體育學分、系上學分
        PE = new_table[new_table['課程系組'].isin(['體育  1  A'])]
        deparetment = pd.concat(
            [new_table, PE, PE]).drop_duplicates(keep=False)

        a, b, c, d, e, f = (
            f"系必修： {(tmp1:=(deparetment[(deparetment['必選修別'] == '必修') & (deparetment['成績'] >= 60)]['學分數'].sum()))}/41",
            f"系選修： {(tmp2:=(deparetment[(deparetment['必選修別'] == '選修') & (deparetment['成績'] >= 60)]['學分數'].sum()))}/54",
            f"系總學分: {tmp1+tmp2}/95",
            f"通識必修： {general[(general['必選修別'] == '必修') & (general['成績'] >= 60)]['學分數'].sum()}/10",
            f"通識選修： {general[(general['必選修別'] != '必修') & (general['成績'] >= 60)]['學分數'].sum()}/18",
            f"體育： {PE[PE['成績'] >= 60]['學分數'].sum()}/3"
        )

        print(a, b, c, d, e, f)
        return "\n".join([a, b, c, d, e, f])


point = PointGeter().proccess(number='110316118', password='R125124015')
