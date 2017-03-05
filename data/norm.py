from lxml.html import parse
i = open('./standard-09.03.0.1-bachelor-2016.html', "r")
tree = parse(i)
tree.write("./standard-09.03.0.1-bachelor-2016-norm.html",
           encoding="utf-8",
           method="xml",
           pretty_print=tree,
           xml_declaration=False,
           with_tail=True,
           standalone=None,
           compression=0,
           exclusive=False,
           with_comments=True,
           inclusive_ns_prefixes=True)
