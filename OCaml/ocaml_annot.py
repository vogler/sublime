import sublime, sublime_plugin
from os import path
import re

class OcamlAnnotCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		path_ml   = path.abspath(self.view.file_name())
		dir_ml    = path.dirname(path_ml)
		filename  = path.basename(path_ml)
		base, ext = path.splitext(filename)
		if ext!='.ml':
			sublime.status_message('OCaml annotations only work for .ml-files')
			return
		filename_annot = base+'.annot'
		path_annot = path.join(dir_ml, filename_annot)
		if not path.exists(path_annot): # .annot-file is not in the same directory as the source-file
			# ocamlbuild: go up the path and check if there is a directory called _build somewhere
			cwd = dir_ml; cwd_old = ''
			while cwd != cwd_old: # once at root, the path doesn't change anymore
				dir_src    = dir_ml[len(path.commonprefix([dir_ml, cwd]))+1:]
				path_annot  = path.join(path.join(path.join(cwd, '_build'), dir_src), filename_annot)
				# print(cwd, dir_src, path_annot)
				if path.exists(path_annot): break
				cwd_old = cwd
				cwd = path.abspath(path.join(cwd, path.pardir)) # go up one directory
			if not path.exists(path_annot): # nothing was found
				sublime.status_message('.annot-file not found! Run ocamlopt -annot '+filename)
				return
		if len(self.view.sel()) > 1:
			sublime.status_message('More than one region is selected. Will only take the first one.')
		region = self.view.sel()[0]
		if region.empty(): # grow selection one char to to the right if it is empty
			region = sublime.Region(region.begin(), region.end()+1)

		# maybe use https://github.com/avsm/ocaml-annot
		f = open(path_annot)
		step = 0
		for line in f.readlines():
			if step==0 and line[0]=='"':
				s = ""
				a = re.sub(r'".*?" ', r'', line).split()
				pl, p1, p2 = map(lambda x: int(x), [a[1], a[2], a[5]]) # editor starts at col 1
				# print 'Region from', p1, 'to', p2, 'on line', a[0], '(starting at char ' + str(pl) + ')'
				r = sublime.Region(p1, p2)
				if r.contains(region):
					step = 1
					self.view.add_regions("type", [r], "comment", "", sublime.DRAW_OUTLINED)
			elif step==1 and line.strip()=='type(':
				step = 2
			elif step==2:
				s += line[2:len(line)-1] # strip 2 spaces indentation in front and \n at the end
				if line[0]==')':
					step = 3
			elif step==3:
				sublime.status_message('Type: '+s.strip())
				return
		sublime.status_message('No type annotation found')
