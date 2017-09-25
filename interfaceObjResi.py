import pandas as pd
from pymol import stored
from pymol import cmd

def interfaceObjResi(object1, object2, cutoff=1.0, interface="interface"):
	"""
	Modified function from interface_residues.py from PyMOLwiki. Returns a dataframe of protein, resi, resn, dSASA(interface area)
	"""

	# create new objects to operate on
	cmd.create('chA', object1)
	cmd.create('chB', object2)
	
	# change the chain names of the objects so that they can easily be extracted from the complex
	cmd.alter('chA', "chain='A'")
	cmd.alter('chB', "chain='B'")
	
	# create the complex for ASA calculations
	cmd.create('cmpx', 'chA or chB')
	
	# get the area of the complete complex
	cmd.get_area('cmpx', load_b=1)
	# copy the areas from the loaded b to the q, field.
	cmd.alter('cmpx', 'q=b')
	
	# extract the two chains and calculate the new area
	# note: the q fields are copied to the new objects
	# obj1 and obj2
	cmd.extract('obj1', "cmpx and chain A")
	cmd.extract('obj2', "cmpx and chain B")
	cmd.get_area('obj1', load_b=1)
	cmd.get_area('obj2', load_b=1)
	
	# update the obj1 and obj2 objects with the difference
	cmd.alter( "%s or %s" % ('obj1','obj2'), "b=b-q" )

	stored.r = []
	cmd.iterate('%s or %s' % ('chA', 'chB'), 'stored.r.append((model,resi,b))')
 
	atom_df = pd.DataFrame(stored.r, columns=['object','resi','diff'])
	resi_df = atom_df.drop('object', 1)
	resi_df = resi_df.set_index('resi')
	resi_df = df.groupby([resi_df.resi]).sum()

	# delete the temporary objects
	cmd.delete('obj1')
	cmd.delete('obj2')
	cmd.delete('cmpx')
	cmd.delete('chA')
	cmd.delete('chB')

cmd.extend("interfaceObjResi", interfaceObjResi)