import util
import sys

# argv
trace_path = str(sys.argv[1])
adjlist_path = str(sys.argv[2])
outfile = str(sys.argv[3])

# get users
print("\nGetting users...")
Author = util.get_authors(trace_path)
users = set(Author.values())
del Author

# get filtered real graph
print("Writing filtered real graph...")
with open(outfile, 'w') as out:
    LeadGraph_real = dict()

    for i,line in enumerate(open(adjlist_path)):

        if i%1000 == 0:
            sys.stdout.flush()
            sys.stdout.write("Line {}...\r".format(i))

        line = line.split()
        lead, follow = int(line[0]), int(line[1])

        if lead in users and follow in users:
            out.write("{} {}\n".format(lead, follow))

# end
print("Done !\n")