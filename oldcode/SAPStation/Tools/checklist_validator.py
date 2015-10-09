__author__ = 'markjacobsen'

from argparse import ArgumentParser
import checklist


parser = ArgumentParser(description='Process some integers.')
parser.add_argument('filename', action='store', help='XML checklist filename')
args = parser.parse_args()

c = checklist.Checklist()
c.load(args.filename)


