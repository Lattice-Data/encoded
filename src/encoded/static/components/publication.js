import React from 'react';
import PropTypes from 'prop-types';
import Cache from '../libs/cache';
import Pager from '../libs/ui/pager';
import { Panel, PanelHeading, PanelBody } from '../libs/ui/panel';
import { CartAddAllElements, CartToggle } from './cart';
import { auditDecor } from './audit';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { DbxrefList } from './dbxref';
import { PickerActions, resultItemClass } from './search';
import Status from './status';
import { ItemAccessories, requestObjects } from './objectutils';
import { SortTablePanel, SortTable } from './sorttable';


/**
 * Renders a table of PublicationData file sets included in this publication.
 */
// Display a publication object.
const PublicationComponent = (props, reactContext) => {
    const context = props.context;
    const itemClass = globals.itemClass(context, 'view-item');

    // Set up breadcrumbs
    const categoryTerms = context.categories && context.categories.map(category => `categories=${category}`);
    const crumbs = [
        { id: 'Publications' },
        {
            id: context.categories ? context.categories.join(' + ') : null,
            query: (categoryTerms && categoryTerms.join('&')),
            tip: context.categories && context.categories.join(' + '),
        },
    ];

    const crumbsReleased = (context.status === 'released');
    return (
        <div className={itemClass}>
            <Breadcrumbs root="/search/?type=Publication" crumbs={crumbs} crumbsReleased={crumbsReleased} />
            <h2>{context.title}</h2>
            <ItemAccessories item={context} audit={{ auditIndicators: props.auditIndicators, auditId: 'publication-audit' }} />
            {props.auditDetail(context.audit, 'publication-audit', { session: reactContext.session, sessionProperties: reactContext.session_properties, except: context['@id'] })}
            {context.authors ? <div className="authors">{context.authors}.</div> : null}
            <div className="journal">
                <Citation context={context} />
            </div>

            {context.abstract || context.data_used || (context.identifiers && context.identifiers.length > 0) ?
                <Panel>
                    <PanelBody>
                        <Abstract context={context} />
                    </PanelBody>
                </Panel>
            : null}
        </div>
    );
};

PublicationComponent.propTypes = {
    context: PropTypes.object.isRequired,
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired,
};

PublicationComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

// Note that Publication needs to be exported for Jest tests.
const Publication = auditDecor(PublicationComponent);
export default Publication;

globals.contentViews.register(Publication, 'Publication');


const Citation = (props) => {
    const context = props.context;
    return (
        <span>
            {context.journal ? <i>{context.journal}. </i> : ''}{context.date_published ? `${context.date_published};` : <span>&nbsp;</span>}
            {context.volume ? context.volume : ''}{context.issue ? `(${context.issue})` : '' }{context.page ? `:${context.page}.` : <span>&nbsp;</span>}
        </span>
    );
};

Citation.propTypes = {
    context: PropTypes.object.isRequired, // Citation object being displayed
};


const Abstract = (props) => {
    const context = props.context;
    return (
        <dl className="key-value">
            {context.abstract ?
                <div data-test="abstract">
                    <dt>Abstract</dt>
                    <dd>{context.abstract}</dd>
                </div>
            : null}

            {context.data_used ?
                <div data-test="dataused">
                    <dt>Consortium data used in this publication</dt>
                    <dd>{context.data_used}</dd>
                </div>
            : null}

            {context.doi ?
                <div data-test="doireference">
                    <dt>DOI</dt>
                    <dd><a href={'https://doi.org/doi:'.concat(context.doi)}>{context.doi}</a></dd>
                </div>
            : null}

            {context.pmid ?
                <div data-test="pmreference">
                    <dt>PubMed ID</dt>
                    <dd><a href={'https://www.ncbi.nlm.nih.gov/pubmed/?term='.concat(context.pmid)}>{context.pmid}</a></dd>
                </div>
            : null}
        </dl>
    );
};

Abstract.propTypes = {
    context: PropTypes.object.isRequired, // Abstract being displayed
};


const ListingComponent = (props, context) => {
    const result = props.context;
    const authorList = result.authors && result.authors.length > 0 ? result.authors.split(', ', 4) : [];
    const authors = authorList.length === 4 ? `${authorList.splice(0, 3).join(', ')}, et al` : result.authors;

    return (
        <li className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">{result.title}</a>
                    <div className="result-item__data-row">
                        {authors ? <p className="list-author">{authors}.</p> : null}
                        <p className="list-citation"><Citation context={result} /></p>
                        {result.identifiers && result.identifiers.length ? <DbxrefList context={result} dbxrefs={result.identifiers} addClasses="list-reference" /> : '' }
                        {result.supplementary_data && result.supplementary_data.length ?
                            <React.Fragment>
                                {result.supplementary_data.map((data, i) =>
                                    <section className="list-supplementary" key={i}>
                                        <SupplementaryDataListing data={data} id={result['@id']} index={i} />
                                    </section>
                                )}
                            </React.Fragment>
                        : null}
                    </div>
                </div>
                <div className="result-item__meta">
                    <div className="result-item__meta-title">Publication</div>
                    <Status item={result.status} badgeSize="small" css="result-table__status" />
                    {props.auditIndicators(result.audit, result['@id'], { session: context.session, sessionProperties: context.session_properties, search: true })}
                </div>
                <PickerActions context={result} />
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: context.session, sessionProperties: context.session_properties, forcedEditLink: true })}
        </li>
    );
};

ListingComponent.propTypes = {
    context: PropTypes.object.isRequired,
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

ListingComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'Publication');
