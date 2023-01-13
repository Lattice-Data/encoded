## Changelog for processed_matrix_file.json

### Schema version 9
* Renamed *author_donor_column* to *demultiplexed_donor_column*
* Moved *layers.normalized* to *X_normalized*
* Moved *layers.feature_counts* to *feature_counts*
* Added *layers_to_keep*
* Removed *layers*
* Set default *file_format* to `hdf5`

### Schema version 8
* Removed *software*,*cell_annotation_method*,*author_cluster_column*,*layers.scaled*,*layers.filtering_cutoffs*

### Schema version 7
* Removed *is_primary_data* from *layers*

### Schema version 6
* Moved *is_primary_data* outside of *layers* so each object has only 1 value

### Schema version 5
* Added *is_primary_data* to *layers*

### Schema version 4
* Removed submitted *assembly* and *genome_annotation* in favor of calculated *assemblies* and *genome_annotations*
