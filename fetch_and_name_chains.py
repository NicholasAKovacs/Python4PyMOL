from pymol import cmd
import pypdb
import re
import os

def fetch_and_name_chains(cif_id):
    '''
DESCRIPTION

    1. Fecth a cif structure from the pdb
    2. Rename the cif file accoring to its 4-letter PDB-code followed by its Genus species name
    3. Create a PyMOL object for each of its chains and name them according to whats on the PDB

    '''

    polymers = pypdb.get_all_info(cif_id)['polymer']

    taxonomy = set()
    chain_to_name = {}
    for poly in range(len(polymers)):
        taxonomy.add(polymers[poly]['Taxonomy']['@name'])
        polymer_description = polymers[poly]['polymerDescription']['@description'].split(',')[0]
        entry_name = re.sub('\(|\)', '', polymer_description)
        chain = polymers[poly]['chain']['@id']
        name = re.sub('ribosomal\s|protein\s|60S\s|40S\s|subunit\s|\sprotein', '', entry_name, flags=re.IGNORECASE)
        chain_to_name[name] = chain

    if len(taxonomy) > 1:
        print('multiple species in structure')
        exit

    for organism in taxonomy:
        Genus_species = organism.replace(' ', '_')
        ge_sp = organism.split()
        GeSp=ge_sp[0][:2]+ge_sp[1][0].capitalize()+ge_sp[1][1]

    cmd.fetch(cif_id, cif_id+'_'+GeSp)
    os.rename(cif_id+'.cif', cif_id+'_'+Genus_species+'.cif')
#    os.remove(cif_id+'.cif') # Not sure why this isn't working

    for obj_name in chain_to_name:
        cmd.create(GeSp+'_'+cif_id+'_'+obj_name, cif_id+'_'+GeSp+' and chain '+chain_to_name[obj_name])

    cmd.show_as('cartoon')

cmd.extend(fetch_and_name_chains)