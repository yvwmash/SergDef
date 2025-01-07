import locale
import sys

locale.setlocale(locale.LC_ALL, 'uk_UA.utf8')
to_str = locale.str

argc = len(sys.argv)
argv = sys.argv

exit  = sys.exit
true  = True
false = False
none  = None