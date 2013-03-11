import sublime, sublime_plugin
from os import path
import re

class OcamlAnnotCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		path_ml   = path.abspath(self.view.file_name())
		basename  = path.basename(path_ml)
		base, ext = path.splitext(basename)
		if ext!='.ml':
			sublime.status_message('OCaml annotations only work for .ml-files')
			return
		path_annot = path.join(path.dirname(path_ml), base+'.annot')
		if not path.exists(path_annot):
			sublime.status_message('.annot-file not found! Run ocamlopt -annot '+basename)
			return
		if len(self.view.sel()) > 1:
			sublime.status_message('More than one region is selected. Will only take the first one.')
		region = self.view.sel()[0]
		if region.empty(): # grow selection one char to to the right if it is empty
			region = sublime.Region(region.begin(), region.end()+1)
		# print self.view.lines(region)

		# maybe use https://github.com/avsm/ocaml-annot
		f = open(path_annot)
		step = 0
		for line in f.readlines():
			if step==0 and line[0]=='"':
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
				sublime.status_message('Type: '+line.strip())
				return
		sublime.status_message('No type annotation found')
