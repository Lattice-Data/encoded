import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { DbxrefList } from './dbxref';
import { PickerActions, resultItemClass } from './search';
import { auditDecor } from './audit';
import pubReferenceList from './reference';
import BiosampleTermId from './biosample';
import { ItemAccessories } from './objectutils';


const OntologyTermComponenet = (props, reactContext) => {
    const context = props.context;
    const itemClass = globals.itemClass(context, 'view-item');

    // Set up breadcrumbs
    const crumbs = [
        { id: 'OntologyTerms' },
        { id: context.term_name, query: `term_name=${context.term_name}`, tip: context.term_name },
    ];

    const crumbsReleased = (context.status === 'released');

    // Get a list of reference links, if any
    const references = pubReferenceList(context.references);

    return (
        <div className={itemClass}>
            <header>
                <Breadcrumbs root="/search/?type=OntologyTerm" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                <h1>
                    <span className="sentence-case">
                        {context.term_name}
                    </span>
                </h1>
                <ItemAccessories item={context} audit={{ auditIndicators: props.auditIndicators, auditId: 'biosample-type-audit' }} />
            </header>
            {props.auditDetail(context.audit, 'biosample-type-audit', { session: reactContext.session, sessionProperties: reactContext.session_properties })}
            <div className="panel">
                <dl className="key-value">
                    <div data-test="term-name">
                        <dt>Term name</dt>
                        <dd>{context.term_name}</dd>
                    </div>

                    <div data-test="term-id">
                        <dt>Term ID</dt>
                        <dd><BiosampleTermId termId={context.term_id} /></dd>
                    </div>

                    {context.notes ?
                        <div data-test="note">
                            <dt>Notes</dt>
                            <dd>{context.notes}</dd>
                        </div>
                    : null}

                    {context.dbxrefs ?
                        <div data-test="externalresources">
                            <dt>External resources</dt>
                            <dd><DbxrefList context={context} dbxrefs={context.dbxrefs} /></dd>
                        </div>
                    : null}

                    {references ?
                        <div data-test="references">
                            <dt>References</dt>
                            <dd>{references}</dd>
                        </div>
                    : null}
                </dl>
            </div>
        </div>
    );
};

OntologyTermComponenet.propTypes = {
    context: PropTypes.object.isRequired,
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

OntologyTermComponenet.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const OntologyTerm = auditDecor(OntologyTermComponenet);

globals.contentViews.register(OntologyTerm, 'OntologyTerm');


const ListingComponent = ({ context: result, auditIndicators, auditDetail }, reactContext) => (
    <li className={resultItemClass(result)}>
        <div className="result-item">
            <div className="result-item__data">
                <a href={result['@id']} className="result-item__link">
                    {result.term_name}
                </a>
                <div className="result-item__data-row">
                    <strong>Ontology ID: </strong><BiosampleTermId termId={result.term_id} />
                </div>
            </div>
            <div className="result-item__meta">
                <div className="type meta-title">Biosample Type</div>
                {auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
            </div>
            <PickerActions context={result} />
        </div>
        {auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, except: result['@id'], forcedEditLink: true })}
    </li>
);

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

globals.listingViews.register(Listing, 'OntologyTerm');
