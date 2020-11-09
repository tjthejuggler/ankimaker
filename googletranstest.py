# from googletrans import Translator
# translator = Translator()
# print(translator.translate('hola'))

# from translate import Translator
# translator= Translator(from_lang="tr",to_lang="en")
# print(translator.translate("Bu bir dolma kalemdir."))

from translation import baidu, google, youdao, iciba

#print(google('hello world!', dst = 'zh-CN'))
#print(google('hello world!', dst = 'ru'))
print(baidu('hello world!', dst = 'zh'))
print(baidu('hello world!', dst = 'ru'))
print(youdao('hello world!', dst = 'zh-CN'))
print(iciba('hello world!', dst = 'zh'))
print(bing('hello world!', dst = 'zh-CHS'))