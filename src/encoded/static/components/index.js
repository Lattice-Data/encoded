// Require all components to ensure javascript load ordering
require('./lib');
require('./view_controls.js');
require('./app');
require('./award');
require('./image');
require('./biosample');
require('./cart');
require('./collection');
require('./datacolors');
require('./dataset');
require('./dbxref');
require('./errors');
require('./genetic_modification');
require('./footer');
require('./globals');
require('./graph');
require('./doc');
require('./donor');
require('./file');
require('./item');
require('./page');
require('./facets');
require('./search');
require('./report');
require('./target');
require('./publication');
require('./testing');
require('./edit');
require('./inputs');
require('./blocks');
require('./user');
require('./schema');
require('./summary');
require('./gene');
require('./ontology_term');


module.exports = require('./app');
