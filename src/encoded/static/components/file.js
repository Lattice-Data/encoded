import React from 'react';
import PropTypes from 'prop-types';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import _ from 'underscore';
import { Panel, PanelHeading, PanelBody } from '../libs/ui/panel';
import { auditDecor } from './audit';
import { DbxrefList } from './dbxref';
import { DocumentsPanel } from './doc';
import * as globals from './globals';
import { requestFiles, requestObjects, requestSearch, ItemAccessories } from './objectutils';
import { ProjectBadge } from './image';
import { QualityMetricsPanel } from './quality_metric';
import { PickerActions, resultItemClass } from './search';
import { SortTablePanel, SortTable } from './sorttable';
import Status from './status';
import { FileTablePaged } from './typeutils';


dayjs.extend(utc);

/**
 * Display list of file.matching_md5sum accessions as links to their respective files. This assumes
 * no duplicates exist in the `matching_md5sum` array.
 */

// Columns to display in Deriving/Derived From file tables
const derivingCols = {
    accession: {
        title: 'Accession',
        display: file => <a href={file['@id']} title={`View page for file ${file.title}`}>{file.title}</a>,
    },
    dataset: { title: 'Dataset' },
    file_format: { title: 'File format' },
    title: {
        title: 'Lab',
        getValue: file => (file.lab && file.lab.title ? file.lab.title : ''),
    },
    assembly: { title: 'Reference assembly' },
    genome_annotation: { title: 'Reference annotation' },
    status: {
        title: 'File status',
        display: item => <Status item={item} badgeSize="small" inline />,
    },
};


// Sort files processed from <PagedFileTable>. The files come in an array of objects with the
// format:
// [{
//     @id: @id of the file
//     accession: accession of the file, if any
//     title: title of the file, if any (either this or accession must have a value)
// }, {next file}, {...}]
//
// This function returns the same array, but sorted by accession, and then by title (all files with
// accessions appear first, followed by all files with titles, each sorted independently).
function sortProcessedPagedFiles(files) {
    // Split the list into two groups for basic sorting first by those with accessions,
    // then those with external_accessions.
    const accessionList = _(files).groupBy(file => (file.accession ? 'accession' : 'external'));

    // Start by sorting the accessioned files.
    let sortedAccession = [];
    let sortedExternal = [];
    if (accessionList.accession && accessionList.accession.length > 0) {
        sortedAccession = accessionList.accession.sort((a, b) => (a.accession > b.accession ? 1 : (a.accession < b.accession ? -1 : 0)));
    }

    // Now sort the external_accession files
    if (accessionList.external && accessionList.external.length > 0) {
        sortedExternal = accessionList.external.sort((a, b) => (a.title > b.title ? 1 : (a.title < b.title ? -1 : 0)));
    }
    return sortedAccession.concat(sortedExternal);
}


/**
 * Display a table of files that derive from this one as a paged component. It first needs to find
 * these files with a search for qualifying files that have a `derived_from` of this file. To save
 * time and bandwidth we only request the @id of these files. The resulting list of @ids then gets
 * sent to FileTablePage to fetch the actual file objects and render them.
 */
const DerivedFiles = ({ file }) => {
    const [fileIds, setFileIds] = React.useState([]);

    React.useEffect(() => {
        requestSearch(`type=DataFile&limit=all&field=@id&status!=deleted&status!=revoked&status!=replaced&derived_from=${file['@id']}`).then((result) => {
            // The server has returned file search results. Generate an array of file @ids.
            if (Object.keys(result).length > 0 && result['@graph'] && result['@graph'].length > 0) {
                // Sort the files. We still get an array of search results from the server, just
                // sorted by accessioned files, followed by external_accession files.
                const sortedFiles = sortProcessedPagedFiles(result['@graph']);
                setFileIds(sortedFiles.map(sortedFile => sortedFile['@id']));
            }
        });
    }, [file]);

    return <FileTablePaged fileIds={fileIds} title={`Files deriving from ${file.title}`} />;
};

DerivedFiles.propTypes = {
    /** Query string fragment for the search that ultimately generates the table of files */
    file: PropTypes.object.isRequired,
};


// Display a table of files the current file derives from.
/* eslint-disable react/prefer-stateless-function */
class DerivedFromFiles extends React.Component {
    render() {
        const { file, derivedFromFiles } = this.props;

        return (
            <SortTablePanel header={<h4>{`Files ${file.title} derives from`}</h4>}>
                <SortTable
                    list={derivedFromFiles}
                    columns={derivingCols}
                    sortColumn="accession"
                />
            </SortTablePanel>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

DerivedFromFiles.propTypes = {
    file: PropTypes.object.isRequired, // File being analyzed
    derivedFromFiles: PropTypes.array.isRequired, // Array of derived-from files
};


class FileComponent extends React.Component {
    constructor() {
        super();
        this.state = {
            derivedFromFiles: [], // List of derived-from files
            fileFormatSpecs: [], // List of file_format_specifications
        };
    }

    componentDidMount() {
        // Now that this page is mounted, request the list of derived_from files and file
        // documents.
        this.requestFileDependencies();

        // In case the logged-in state changes, we have to keep track of the old logged-in state.
        this.loggedIn = !!(this.context.session && this.context.session['auth.userid']);
    }

    componentWillReceiveProps() {
        // If the logged-in state has changed since the last time we rendered, request files again
        // in case logging in changes the list of dependent files.
        const currLoggedIn = !!(this.context.session && this.context.session['auth.userid']);
        if (this.loggedIn !== currLoggedIn) {
            this.requestFileDependencies();
            this.loggedIn = currLoggedIn;
        }
    }

    requestFileDependencies() {
        // Perform GET requests of files that derive from this one, as well as file format
        // specification documents. This avoids embedding these arrays of objects in the file
        // object.
        const file = this.props.context;

        // Retrieve an array of file @ids that this file derives from. Once this array arrives.
        // it sets the derivedFromFiles React state that causes the list to render.
        const derivedFromFileIds = file.derived_from && file.derived_from.length > 0 ? file.derived_from : [];
        if (derivedFromFileIds.length > 0) {
            requestFiles(derivedFromFileIds).then((derivedFromFiles) => {
                this.setState({ derivedFromFiles });
            });
        }

        // Retrieve an array of file format specification document @ids. Once the array arrives,
        // set the fileFormatSpecs React state that causes the list to render.
        const fileFormatSpecs = file.file_format_specifications && file.file_format_specifications.length > 0 ? file.file_format_specifications : [];
        if (fileFormatSpecs.length > 0) {
            requestObjects(fileFormatSpecs, '/search/?type=Document&limit=all&status!=deleted&status!=revoked&status!=replaced').then((docs) => {
                this.setState({ fileFormatSpecs: docs });
            });
        }
    }

    render() {
        const { context, auditDetail, auditIndicators } = this.props;
        const itemClass = globals.itemClass(context, 'view-item');
        const aliasList = (context.aliases && context.aliases.length > 0) ? context.aliases.join(', ') : '';
        const loggedIn = !!(this.context.session && this.context.session['auth.userid']);
        const adminUser = !!this.context.session_properties.admin;

        return (
            <div className={itemClass}>
                <header>
                    <h2>File summary for {context.title} (<span className="sentence-case">{context.file_format}</span>)</h2>
                    <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'file-audit', except: context['@id'] }} />
                </header>
                {auditDetail(context.audit, 'file-audit', { session: this.context.session, sessionProperties: this.context.session_properties, except: context['@id'] })}
                <Panel>
                    <PanelBody addClasses="panel__split">
                        <div className="panel__split-element">
                            <div className="panel__split-heading panel__split-heading--file">
                                <h4>Summary</h4>
                            </div>
                            <dl className="key-value">
                                <div data-test="status">
                                    <dt>Status</dt>
                                    <dd><Status item={context} inline /></dd>
                                </div>

                                {context.file_format ?
                                    <div data-test="fileFormat">
                                        <dt>File format</dt>
                                        <dd>{context.file_format}</dd>
                                    </div>
                                : null}

                                {context.output_types ?
                                    <div data-test="outputTypes">
                                        <dt>Output types</dt>
                                        <dd>{context.output_types.join(",")}</dd>
                                    </div>
                                : null}

                                {context.assays ?
                                    <div data-test="assays">
                                        <dt>Assays</dt>
                                        <dd>{context.assays.join(",")}</dd>
                                    </div>
                                : null}

                                {context.file_size ?
                                    <div data-test="filesize">
                                        <dt>File size</dt>
                                        <dd>{globals.humanFileSize(context.file_size)}</dd>
                                    </div>
                                : null}

                                {context.read_type ?
                                    <div data-test="readType">
                                        <dt>Read type</dt>
                                        <dd>{context.read_type}</dd>
                                    </div>
                                : null}

                                {context.platform ?
                                    <div data-test="platform">
                                        <dt>Platform</dt>
                                        <dd>{context.platform.join(",")}</dd>
                                    </div>
                                : null}

                                {context.read_count ?
                                    <div data-test="readcount">
                                        <dt>Read count</dt>
                                        <dd>{context.read_count}</dd>
                                    </div>
                                : null}

                                {context.read_length ?
                                    <div data-test="readlength">
                                        <dt>Read length</dt>
                                        <dd>{context.read_length}</dd>
                                    </div>
                                : null}

                                {context.observation_count ?
                                    <div data-test="obsCount">
                                        <dt>Observation count</dt>
                                        <dd>{context.observation_count}</dd>
                                    </div>
                                : null}

                                {context.libraries ?
                                    <div data-test="libraries">
                                        <dt>Libraries</dt>
                                        <dd>{context.libraries.join(",")}</dd>
                                    </div>
                                : null}

                            </dl>
                        </div>

                        <div className="panel__split-element">
                            <div className="panel__split-heading panel__split-heading--file">
                                <h4>Attribution</h4>
                            </div>
                            <dl className="key-value">

                                {context.dataset ?
                                    <div data-test="dataset">
                                        <dt>Dataset</dt>
                                        <dd>{context.dataset}</dd>
                                    </div>
                                : null}

                                {context.lab ?
                                    <div data-test="lab">
                                        <dt>Lab</dt>
                                        <dd>{context.lab.title}</dd>
                                    </div>
                                : null}
                                {context.award ?
                                    <div data-test="award">
                                        <dt>Award</dt>
                                        <dd>{context.award.name}</dd>
                                    </div>
                                : null}
                                {context.award ?
                                    <div data-test="project">
                                        <dt>Project</dt>
                                        <dd>{context.award.project}</dd>
                                    </div>
                                : null}
                                {context.assembly ?
                                    <div data-test="assembly">
                                        <dt>Assembly</dt>
                                        <dd>{context.assembly}</dd>
                                    </div>
                                : null}
                                {context.genome_annotation ?
                                    <div data-test="genomeannotation">
                                        <dt>Genome annotation</dt>
                                        <dd>{context.genome_annotation}</dd>
                                    </div>
                                : null}
                                {context.date_created ?
                                    <div data-test="datecreated">
                                        <dt>Date added</dt>
                                        <dd>{dayjs.utc(context.date_created).format('YYYY-MM-DD')}</dd>
                                    </div>
                                : null}

                                {context.dbxrefs ?
                                    <div data-test="externalresources">
                                        <dt>External resources</dt>
                                        <dd><DbxrefList context={context} dbxrefs={context.dbxrefs} /></dd>
                                    </div>
                                : null}

                                {aliasList ?
                                    <div data-test="aliases">
                                        <dt>Aliases</dt>
                                        <dd className="sequence">{aliasList}</dd>
                                    </div>
                                : null}

                                {context.s3_uri ?
                                    <div data-test="s3Uri">
                                        <dt>S3 URI</dt>
                                        <dd>{context.s3_uri}</dd>
                                    </div>
                                : null}

                            </dl>
                        </div>
                    </PanelBody>
                </Panel>

                {context.flowcell_details ?
                    <SequenceFileInfo file={context} />
                : null}

                {this.state.derivedFromFiles && this.state.derivedFromFiles.length > 0 ? <DerivedFromFiles file={context} derivedFromFiles={this.state.derivedFromFiles} /> : null}

                <DerivedFiles file={context} />

            </div>
        );
    }
}

FileComponent.propTypes = {
    context: PropTypes.object.isRequired, // File object being displayed
    auditIndicators: PropTypes.func.isRequired, // Audit indicator rendering function from auditDecor
    auditDetail: PropTypes.func.isRequired, // Audit detail rendering function from auditDecor
};

FileComponent.contextTypes = {
    session: PropTypes.object, // Login information
    session_properties: PropTypes.object,
};

const File = auditDecor(FileComponent);

globals.contentViews.register(File, 'File');


// Display the sequence file summary panel for fastq files.
/* eslint-disable react/prefer-stateless-function */
class SequenceFileInfo extends React.Component {
    render() {
        const { file } = this.props;
        const pairedWithAccession = file.paired_with ? globals.atIdToAccession(file.paired_with) : '';

        return (
            <Panel>
                <PanelHeading>
                    <h4>Sequencing file information</h4>
                </PanelHeading>

                <PanelBody>
                    <dl className="key-value">
                        {file.flowcell_details && file.flowcell_details.length > 0 ?
                            <div data-test="flowcelldetails">
                                <dt>Flowcell</dt>
                                <dd>
                                    {file.flowcell_details.map((detail, i) => {
                                        const items = [
                                            detail.machine ? detail.machine : '',
                                            detail.flowcell ? detail.flowcell : '',
                                            detail.lane ? detail.lane : '',
                                            detail.barcode ? detail.barcode : '',
                                        ];
                                        return <span className="line-item" key={i}>{items.join(':')}</span>;
                                    })}
                                </dd>
                            </div>
                        : null}

                    </dl>
                </PanelBody>
            </Panel>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */


SequenceFileInfo.propTypes = {
    file: PropTypes.object.isRequired, // File being displayed
};


/* eslint-disable react/prefer-stateless-function */
class ListingComponent extends React.Component {
    render() {
        const result = this.props.context;

        return (
            <li className={resultItemClass(result)}>
                <div className="result-item">
                    <div className="result-item__data">
                        <a href={result['@id']} className="result-item__link">
                            {`${result.file_format}${result.file_format_type ? ` (${result.file_format_type})` : ''}`}
                        </a>
                        {result.lab ?
                        <div className="result-item__data-row">
                            <div><strong>Lab: </strong>{result.lab.title}</div>
                            {result.award.project ? <div><strong>Project: </strong>{result.award.project}</div> : null}
                        </div>
                        : null}
                    </div>
                    <PickerActions context={result} />
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, sessionProperties: this.context.session_properties })}
            </li>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

ListingComponent.propTypes = {
    context: PropTypes.object.isRequired, // File object being rendered
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

ListingComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'File');
