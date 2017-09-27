from pymol import stored
 
def interface_objects(object1, object2, cutoff=1.0):

	# Set dot_solvent to SASA
	cmd.set("dot_solvent", 1)

	# get ch1ins of object inputs
	obj1_chain = cmd.get_chains(object1)[0]
	obj2_chain = cmd.get_chains(object2)[0]

	# set up variable names so I don't have to write so many quotes later
	cmpx,ch1,ch2='cmpx','ch1','ch2'
	interface_selection = "interface_selection"
	
	# create objects to work on so as to not disturb input objects
	cmd.create(cmpx, object1 + " or " + object2)
 
	# remove cruft and inrrelevant ch1ins
	cmd.remove(cmpx + " and NOT polymer")
 
	# get the area of the complete complex
	cmd.get_area(cmpx, load_b=1)
	# copy the areas from the loaded b to the q, field.
	cmd.alter(cmpx, 'q=b')
 
	# extract the two ch1ins and calc. the new area
	# note: the q fields are copied to the new objects
	# ch1 and ch2
	cmd.extract(ch1, cmpx + " and chain " + obj1_chain)
	cmd.extract(ch2, cmpx + " and chain " + obj2_chain)
	cmd.get_area(ch1, load_b=1)
	cmd.get_area(ch2, load_b=1)
 
	# update the ch1in-only objects w/the difference
	cmd.alter( "%s or %s" % (ch1,ch2), "b=b-q" )
 
	# The calculations are done.  Now, all we need to
	# do is to determine which residues are over the cutoff
	# and save them.
	stored.r, rVal, seen = [], [], []
	cmd.iterate('%s or %s' % (ch1, ch2), 'stored.r.append((model,resi,resn,b))')
 
	cmd.select(interface_selection, None)
	for (model,resi,resn,diff) in stored.r:
		key=resi+"-"+model
		if abs(diff)>=float(cutoff):
			if key in seen: continue
			else: seen.append(key)
			rVal.append( (model,resi,resn,diff) )
			# expand the selection here; I chose to iterate over stored.r instead of
			# creating one large selection b/c if there are too many residues PyMOL
			# might crash on a very large selection.  This is pretty much guaranteed
			# not to kill PyMOL; but, it might take a little longer to run.
			cmd.select( interface_selection, interface_selection + " or (%s and i. %s)" % (model,resi))
 
	# create objects from interface_selection
	cmd.create(object1+"-"+object2+"_interaction", interface_selection)
	cmd.create(object1+"_interface", interface_selection+" and chain " + obj1_chain)
	cmd.create(object2+"_interface", interface_selection+" and chain " + obj2_chain)

	# remove temporary objects
	cmd.delete(interface_selection)
	cmd.delete(ch1)
	cmd.delete(ch2)
	cmd.delete(cmpx)
 
	return rVal
 
cmd.extend(interface_objects)