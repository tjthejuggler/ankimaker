# from googletrans import Translator
# translator = Translator()
# print(translator.translate('hola'))

from translate import Translator
translator= Translator(to_lang="es")
print(translator.translate("This is a pen."))