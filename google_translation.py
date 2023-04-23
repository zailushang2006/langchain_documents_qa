import requests
import re
import html
from urllib import parse


class GoogleTranslation(object):
    def __init__(self):
        self.GOOGLE_TRANSLATE_URL = 'http://translate.google.com/m?q=%s&tl=%s&sl=%s'
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
        }

    # 谷歌翻译方法
    def google_translate(self, content, to_language="auto", text_language="auto"):
        '''实现谷歌的翻译处理超过字符限制的文章'''
        res_trans = ""
        if len(content) > 4500:
            while len(content) > 4500:
                temp = content[0:4000-len(content[0:4000].split(',')[-1])]
                content = content[4001-len(content[0:4000].split(',')[-1]):]
                temp_trans = self.translate(temp, to_language,text_language)
                res_trans = res_trans + temp_trans
            # print("实现多次翻译拼接，用这个分割一下\n")
            temp_trans = self.translate(content, to_language, text_language)
            res_trans += temp_trans
            #time.sleep(0.5)
            return res_trans
        else:
            return self.translate(content, to_language, text_language)

    def translate(self, text, to_language="auto", text_language="auto"):
        text = parse.quote(text)
        url = self.GOOGLE_TRANSLATE_URL % (text, to_language, text_language)
        response = requests.get(url)
        data = response.text
        expr = r'(?s)class="(?:t0|result-container)">(.*?)<'
        result = re.findall(expr, data)
        if (len(result) == 0):
            return ""

        return html.unescape(result[0])

    def translate_1(self, text, src_lang='auto', to_lang='en'):
        googleapis_url = 'https://translate.googleapis.com/translate_a/single'
        url = '%s?client=gtx&sl=%s&tl=%s&dt=t&q=%s' % (googleapis_url, src_lang, to_lang, text)
        data = requests.get(url).json()
        res = ''.join([s[0] for s in data[0]])
        return res


if __name__ == "__main__":
    trans = GoogleTranslation()
    print(trans.google_translate("百度の翻訳はインターネットのデータ資源と自然言語処理技術の優位性に頼って、ユーザーが言語のギャップを越えることを助けることに力を入れている。","zh-CN"))
    print(trans.google_translate("你吃饭了么?", "en","zh-CN")) #汉语转英语
    print(trans.google_translate("你吃饭了么？", "ja","zh-CN")) #汉语转日语
    print(trans.google_translate("about your situation", "zh-CN","en")) #英语转汉语
