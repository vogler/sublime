import sublime, sublime_plugin
import threading
import atexit
import time
import SocketServer
import re
import os.path

print("ocaml_build loaded")
HOST, PORT = "localhost", 9999

def process(cwd, lines):
    window = sublime.active_window()
    for i,line in zip(range(len(lines)), lines):
        # print line
        m = re.match(r"File \"(.+)\", line (.+), characters (.+)-(.+):", line)
        if m:
            print "%s at line %s from %s-%s" % (m.group(1), m.group(2), m.group(3), m.group(4))
            filename = m.group(1)
            row, col1, col2 = map(int, [m.group(2), m.group(3), m.group(4)])
            suffix = ":%s:%s" % (row, col1)
            path = os.path.join(cwd, filename)
            if not os.path.exists(path):
                print("Couldn't find file %s"%path)
                # TODO save view to show message on UI-thread, otherwise sublime crashes
                # sublime.error_message("Couldn't find file %s"%path)
            else:
                view = window.open_file(path+suffix, sublime.ENCODED_POSITION)
                while view.is_loading():
                    time.sleep(.1)
                region_line = view.full_line(view.sel()[0])
                region = sublime.Region(region_line.begin()+col1, region_line.begin()+col2)
                view.show_at_center(region) # optionally center, open_file already brings region into view
                view.add_regions("ocaml_error", [region], "keyword", "dot", sublime.DRAW_OUTLINED)
            error = ''.join(lines[i+1:])
            print(error)
            # sublime.message_dialog(error)
            return True
    return False


class MyTCPHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        print("ocaml_build received error message")
        cwd = self.rfile.readline().strip()
        line = 1
        lines = []
        while line: # readlines() doesn't work :(
            line = self.rfile.readline()
            # print line
            if line.strip().startswith("Command exited with code"): break
            lines.append(line)
        msg = "showing error in sublime" if process(cwd, lines) else "error not found in sublime"
        self.wfile.write(msg+"\n")
        # global server
        # server.stop()


class Server(threading.Thread):

    def __init__(self):
        print("ocaml_build init server")
        self.server = None
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.start_server(PORT)
        except Exception:
            print('ocaml_build plugin can not start: port (' + str(PORT) + ') is already in use!')
            # sublime.error_message('ocaml_build plugin can not start: port (' + str(PORT) + ') is already in use!')
            # time.sleep(3)
            # self.start_server(PORT + 1)

    def start_server(self, port):
        print("ocaml_build start server")
        # Create the server, binding to HOST on port
        self.server = SocketServer.TCPServer((HOST, port), MyTCPHandler)
        # self.server.allow_reuse_address = True
        self.server.serve_forever()

    @atexit.register
    def stop(self):
        print("ocaml_build stop server")
        if self.server is not None:
            self.server.shutdown()
            # self.server.socket.close()


# start a new thread with a server listening for compile errors from ocamlbuild
server = Server()
server.start()

# f = open("ocaml_error.txt")

class Listener(sublime_plugin.EventListener):

    def __init__(self):
        print("ocaml_build init listener")
        sublime_plugin.EventListener.__init__(self)

    # def on_new(self, view):
    #     print "new file"
    #     global server
    #     server.stop()

    def on_pre_save(self, view):
        view.erase_regions("ocaml_error")

    # def on_post_save(self, view):
    #     print "saved file"
    #     global f
    #     process("/home/ralf/analyzer", f.readlines())
