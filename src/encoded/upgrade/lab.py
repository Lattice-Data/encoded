from snovault import upgrade_step


@upgrade_step('lab', '1', '2')
def lab_1_2(value, system):
	remove = ['address1', 'address2', 'city', 'country', 'institute_label',
		'institute_name', 'phone', 'postal_code', 'state', 'url',
		'principal_investigators']
	for p in remove:
		if p in value:
			del value[p]

inst_naming = {
	'Anderson': 'University of Texas MD Anderson Cancer Center',
	'ASU': 'Arizona State University',
	'BCH, HMS': "Boston Children's Hospital, Harvard Medical School",
	'BCM': 'Baylor College of Medicine',
	'Beijing': 'Beijing University',
	'BGU': 'Ben-Gurion University of the Negev',
	'BRC': 'Biological Research Centre of the Hungarian Academy of Sciences',
	'Broad': 'Broad Institute of MIT and Harvard',
	'BWH': "Brigham and Women's Hospital",
	'Cambridge': 'University of Cambridge',
	'CCHMC': "Cincinnati Children's Hospital Medical Center",
	'Chicago': 'University of Chicago',
	'CNAG-CRG': 'Centre for Genomic Regulation',
	'CNRS': 'Centre National de la Recherche Scientifique',
	'Columbia': 'Columbia University',
	'CRG': 'Centre for Genomic Regulation',
	'CSHL': 'Cold Spring Harbor Laboratory',
	'Dana-Farber': 'Dana-Farber Cancer Institute',
	'Duke': 'Duke University',
	'Edinburgh': 'University of Edinburgh',
	'EMBL Heidelberg': 'European Molecular Biology Laboratory Heidelberg',
	'EPFL': 'École Polytechnique Fédérale de Lausanne',
	'FMI': 'Friedrich Miescher Ist for Biomedical Research',
	'Fred Hutch': 'Fred Hutchinson Cancer Research Center',
	'Garvan': 'Garvan Institute of Medical Research',
	'Ghent': 'Ghent University',
	'GIS': 'Genome Institute of Singapore',
	'Harvard': 'Harvard University',
	'HMGU': 'Helmholtz Zentrum Munich',
	'HMS': 'Harvard Medical School',
	'HUJI': 'Hebrew University of Jerusalem',
	'Imperial': 'Imperial College London',
	'IOB': 'Institute of Molecular and Clinical Opthalmology Basel',
	'IU': 'Indiana University School of Medicine',
	'JHU': 'Johns Hopkins University',
	'KI': 'Karolinska Institutet',
	'KTH': 'KTH Royal Institute of Technology',
	'KU Leuven': 'Katholieke Universiteit Leuven',
	'Leipzig': 'University of Leipzig',
	'LMU': 'Ludwig Maximilians University Munich',
	'Mahidol': 'Mahidol University',
	'Mass General': 'Massachusetts General Hospital',
	'MDC': 'Max Delbruck Center for Molecular Medicine',
	'MEE': 'Massachusetts Eye and Ear',
	'MIT': 'Massachusetts Institute of Technology',
	'Mount Sinai': 'Icahn School of Medicine at Mount Sinai',
	'MP Biochem': 'Max Planck Institute of Biochemistry',
	'MP Immuno': 'Max Planck Institute Immunobiology and Epigenetics',
	'Newcastle': 'Newcastle University',
	'NIBMG': 'National Institute of Biomedical Genetics',
	'NIH': 'National Institutes of Health',
	'Northeastern': 'Northeastern University',
	'Northwestern': 'Northwestern University',
	'NYGC': 'New York Genome Center',
	'Oxford': 'University of Oxford',
	'Penn': 'University of Pennsylvania',
	'Princeton': 'Princeton University',
	'Salk': 'Salk Institute for Biological Studies',
	'Sanger': 'Wellcome Sanger Institute',
	'SGI': 'Samsung Genome Institute',
	'Sloan': 'Sloan Kettering Institute',
	'Stanford': 'Stanford University',
	'Toronto': 'University of Toronto',
	'UCB': 'Weizmann institute of Science',
	'UCD': 'University of California, Davis',
	'UCH': 'University of Chicago',
	'UCI': 'University of California, Irvine',
	'UCLA': 'University of California, Los Angeles',
	'UCPH': 'University of Copenhagen',
	'UCSD': 'University of California, San Diego',
	'UCSF': 'University of California, San Francisco',
	'UMich': 'University of Michigan',
	'UNH': 'University of Toronto',
	'UNICAMP': 'State University of Campinas',
	'Univ of Zurich': 'University of Zurich',
	'USC': 'University of Southern California',
	'Utah': 'University of Utah School of Medicine',
	'UWash': 'University of Washington',
	'Vanderbilt': 'Vanderbilt University',
	'WashU': 'Washington University, St. Louis',
	'WEHI': 'Walter and Eliza Hall Institute of Medical Research',
	'Weizmann': 'Weizmann Institute of Science',
	'Yale': 'Yale University'
}


@upgrade_step('lab', '2', '3')
def lab_2_3(value, system):
	inst = value['title'].split(', ')[-1]
	inst = inst_naming.get(inst, inst)
	value['institute_name'] = inst
