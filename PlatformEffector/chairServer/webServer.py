import BaseHTTPServer
import SimpleHTTPServer
server_address = ("", 8080)
DIR = 'curvegen'
FUNC = '/func/'



def runFunc(VAR):
	print VAR


class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def translate_path(self, path):
    	print self.path
    	if self.path.startswith(FUNC):
  			print "FUNCTION!!!!"
  			VAR =  self.path[len(FUNC):-1]
  			runFunc(VAR)
    	return "func.html"

httpd = BaseHTTPServer.HTTPServer(server_address, MyRequestHandler)
httpd.serve_forever()




# Example code shown below for greater file geneation etc

# import BaseHTTPServer
# import SimpleHTTPServer
# server_address = ("", 8888)
# PUBLIC_RESOURCE_PREFIX = '/public'
# PUBLIC_DIRECTORY = '/path/to/protected/public'

# class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
#     def translate_path(self, path):
#         if self.path.startswith(PUBLIC_RESOURCE_PREFIX):
#             if self.path == PUBLIC_RESOURCE_PREFIX or self.path == PUBLIC_RESOURCE_PREFIX + '/':
#                 return PUBLIC_DIRECTORY + '/index.html'
#             else:
#                 return PUBLIC_DIRECTORY + path[len(PUBLIC_RESOURCE_PREFIX):]
#         else:
#             return SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(self, path)

# httpd = BaseHTTPServer.HTTPServer(server_address, MyRequestHandler)
# httpd.serve_forever()