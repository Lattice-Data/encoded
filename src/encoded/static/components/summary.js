import React from 'react';
import PropTypes from 'prop-types';
import queryString from 'query-string';
import url from 'url';
import * as encoding from '../libs/query_encoding';
import QueryString from '../libs/query_string';
import { Panel, PanelBody } from '../libs/ui/panel';
import { LabChart, CategoryChart, createNewBarChart } from './award';
import * as globals from './globals';
import { requestSearch } from './objectutils';
import { FacetList, ClearFilters } from './search';
import { getObjectStatuses, sessionToAccessLevel } from './status';
import { ViewControls } from './view_controls';

/**
 * Generate an array of data from one facet bucket for displaying in a chart, with one array entry
 * per experiment status. The order of the entries in the resulting array correspond to the order
 * of the statuses in `labels`.
 *
 * @param {array} buckets - Buckets for one facet returned in summary search results.
 * @param {array} labels - Experiment status labels.
 * @return {array} - Data extracted from buckets with an order of values corresponding to `labels`.
 */

// Data field for organism
// We will display different facets depending on the selected organism
const organismField = 'donors.organism.scientific_name';

// Mapping of shortened organism name and full scientific organism name
const organismTerms = [
    'Homo sapiens',
    'Mus musculus',
];

function generateStatusData(buckets, labels) {
    // Fill the array to the proper length with zeroes to start with. Actual non-zero data will
    // overwrite the appropriate entries.
    const statusData = Array.from({ length: labels.length }, (() => 0));

    // Convert statusData to a form createBarChart understands.
    if (buckets && buckets.length > 0) {
        buckets.forEach((bucketItem) => {
            const statusIndex = labels.indexOf(bucketItem.key);
            if (statusIndex !== -1) {
                statusData[statusIndex] = bucketItem.doc_count;
            }
        });
    }
    return statusData;
}


// Column graph of experiment statuses.
class SummaryStatusChart extends React.Component {
    constructor() {
        super();
        this.chart = null;
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.props.totalStatusData) {
            this.createChart();
        }
    }

    componentDidUpdate() {
        if (this.props.totalStatusData) {
            if (this.chart) {
                this.updateChart(this.chart, this.props.statusData);
            } else {
                this.createChart();
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    createChart() {
        const { statusData } = this.props;

        var ethnicityFacet = []
        this.props.facets.forEach(function(element) {
            if (element['field'] == 'donors.ethnicity.term_name') {
                ethnicityFacet = element['terms'];
            }
        });
        const ethnicityNames = Array.from(ethnicityFacet, x => x['key']);

        // Initialize data object to pass to createBarChart.
        const data = {
            femaleDataset: null,
            maleDataset: null,
            unknownDataset: null,
            labels: ethnicityNames,
        };

        // Convert statusData to a form createBarChart understands.
        let facetData = statusData.find(facet => facet.key === 'female');
        data.femaleDataset = facetData ? generateStatusData(facetData["donors.ethnicity.term_name"].buckets, data.labels) : [];
        facetData = statusData.find(facet => facet.key === 'male');
        data.maleDataset = facetData ? generateStatusData(facetData["donors.ethnicity.term_name"].buckets, data.labels) : [];
        facetData = statusData.find(facet => facet.key === 'unknown');
        data.unknownDataset = facetData ? generateStatusData(facetData["donors.ethnicity.term_name"].buckets, data.labels) : [];

        // Generate colors to use for each sex value.
        const colors = globals.donorSexColors.colorList(globals.donorSexList);

        createNewBarChart(this.chartId, data, colors, globals.donorSexList, this.props.linkUri, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    updateChart(chart, statusData) {
        const donorSexColors = globals.donorSexColors.colorList(globals.donorSexList);

        var ethnicityFacet = []
        this.props.facets.forEach(function(element) {
            if (element['field'] == 'donors.ethnicity.term_name') {
                ethnicityFacet = element['terms'];
            }
        });
        const ethnicityNames = Array.from(ethnicityFacet, x => x['key']);

        // For each sex value, extract the data for each status to assign to the existing
        // chart's dataset.
        const datasets = [];
        globals.donorSexList.forEach((donorSex, donorSexIndex) => {
            const facetData = statusData.find(facet => facet.key === donorSex);
            if (facetData) {
                // Get an array of replicate data per status from the facet data.
                const data = generateStatusData(facetData["donors.ethnicity.term_name"].buckets, ethnicityNames);

                datasets.push({
                    backgroundColor: donorSexColors[donorSexIndex],
                    data,
                    label: donorSex,
                });
            }
        });

        // Update the chart data, then force a redraw of the chart and legend.
        chart.data.datasets = datasets;
        chart.data.labels = ethnicityNames;
        chart.update();
        document.getElementById(`${this.chartId}-legend`).innerHTML = chart.generateLegend();
    }

    render() {
        const { totalStatusData } = this.props;

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        this.chartId = 'status-chart-experiments';

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Donors
                </div>
                {totalStatusData ?
                    <div className="award-charts__visual">
                        <div id={this.chartId} className="award-charts__canvas">
                            <canvas id={`${this.chartId}-chart`} />
                        </div>
                        <div id={`${this.chartId}-legend`} className="award-charts__legend" />
                    </div>
                :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }
}

SummaryStatusChart.propTypes = {
    statusData: PropTypes.array.isRequired, // Experiment status data from /summary/ search results
    totalStatusData: PropTypes.number.isRequired, // Number of items in statusData
    linkUri: PropTypes.string.isRequired, // URI of base link for each bar to link to
};

SummaryStatusChart.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
    navigate: PropTypes.func,
};

// Render the horizontal facets.
// Note: these facets are not necessarily horizontal, it depends on the screen width
const SummaryHorizontalFacets = ({ context, facetList }, reactContext) => {
    let horizFacets;
    if (facetList === 'all') {
        horizFacets = context.facets.filter(f => ['donors.organism.scientific_name', 'donors.ethnicity.term_name', 'donors.sex', 'donors.life_stage', 'biosample_ontologies.organ_slims', 'biosample_ontologies.term_name', 'award.project', 'award.coordinating_pi.title', 'lab.title'].includes(f.field));
    } else {
        horizFacets = context.facets.filter(f => [].includes(f.field));
    }

    // Calculate the searchBase, which is the current search query string fragment that can have
    // terms added to it.
    const searchBase = `${url.parse(reactContext.location_href).search}&` || '?';

    // Note: we subtract one from the horizontal facet length because "date-released" and "date-submitted" are collapsed into one facet
    return (
        <FacetList
            context={context}
            facets={horizFacets}
            filters={context.filters}
            searchBase={searchBase}
            addClasses={`summary-horizontal-facets facet-num-${horizFacets.length - 1} ${facetList}`}
            supressTitle
            orientation="horizontal"
        />
    );
};

SummaryHorizontalFacets.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
    facetList: PropTypes.string,
};

SummaryHorizontalFacets.defaultProps = {
    facetList: '',
};

SummaryHorizontalFacets.contextTypes = {
    location_href: PropTypes.string, // Current URL
    navigate: PropTypes.func, // encoded navigation
};

// Update all charts to resize themselves on print.
const printHandler = () => {
    Object.keys(window.Chart.instances).forEach((id) => {
        window.Chart.instances[id].resize();
    });
};


// Render the data for the summary in the main panel. Note that we use the charting components from
// awards.js for labs and categories, but not for the status chart. That's because the data gets
// retrieved so differently -- through multiple search requests in awards.js, but in its own
// property with this summary page. Might be good for a refactor later to share common code.

// "displayCharts" is an optional parameter which allows for display of subset of all possible charts
// Possible parameter values are "all", "donuts" or "area", and the default is "all"
class SummaryData extends React.Component {
    constructor() {
        super();
        this.mediaQueryInfo = null;
    }

    componentDidMount() {
        if (window.matchMedia) {
            this.mediaQueryInfo = window.matchMedia('print');
            this.mediaQueryInfo.addListener(printHandler);
        }

        // In case matchMedia doesn't work (e.g. FF and IE).
        window.onbeforeprint = printHandler;
        window.onafterprint = printHandler;
    }

    componentWillUnmount() {
        if (this.mediaQueryInfo) {
            this.mediaQueryInfo.removeListener(printHandler);
            this.mediaQueryInfo = null;
        }
    }

    render() {
        const { context } = this.props;

        // Find the labs and assay facets in the search results.
        const labFacet = context.facets.find(facet => facet.field === 'lab.title');
        let labs = labFacet ? labFacet.terms : null;
        const assayFacet = context.facets.find(facet => facet.field === 'assay');
        let assays = assayFacet ? assayFacet.terms : null;

        const filteredOutLabs = context.filters.filter(c => c.field === 'lab.title!');
        const filteredOutAssays = context.filters.filter(c => c.field === 'assay_title!');

        // Filter the assay list if any assay facets have been selected so that the assay graph will be
        // filtered accordingly. Find assay_title filters. Same applies to the lab filters.
        if (context.filters && context.filters.length > 0) {
            const assayTitleFilters = context.filters.filter(filter => filter.field === 'assay_title');
            if (assayTitleFilters.length > 0) {
                const assayTitleFilterTerms = assayTitleFilters.map(filter => filter.term);
                assays = assays.filter(assayItem => assayTitleFilterTerms.indexOf(assayItem.key) !== -1);
            }
            const labFilters = context.filters.filter(filter => filter.field === 'lab.title');
            if (labFilters.length > 0) {
                const labFilterTerms = labFilters.map(filter => filter.term);
                labs = labs.filter(labItem => labFilterTerms.indexOf(labItem.key) !== -1);
            }
        }

        // Get the status data with a process completely different from the others because it comes
        // in its own property in the /summary/ context. Start by getting the name of the property
        // that contains the status data, as well as the number of items within it.
        const statusProp = context.matrix.y.group_by[0];
        const statusSection = context.matrix.y[statusProp];
        const statusDataCount = context.total;
        const statusData = statusSection.buckets;

        // Collect selected facet terms to add to the base linkUri.
        let searchQuery = '';
        if (context.filters && context.filters.length > 0) {
            searchQuery = context.filters.map(filter => `${filter.field}=${encoding.encodedURIComponentOLD(filter.term)}`).join('&');
        }
        const linkUri = `/report/?${searchQuery}`;
        const displayCharts = this.props.displayCharts;

        return (
            <div className="summary-content__data">
                {(displayCharts === 'all' || displayCharts === 'donuts') ?
                    <div className="summary-content__snapshot">
                        {labs ? <LabChart labs={labs} linkUri={linkUri} ident="experiments" filteredOutLabs={filteredOutLabs} /> : null}
                        {assays ? <CategoryChart categoryData={assays} categoryFacet="assay" title="Assay" linkUri={linkUri} ident="assay" filteredOutAssays={filteredOutAssays} /> : null}
                        {statusDataCount ? <SummaryStatusChart statusData={statusData} totalStatusData={statusDataCount} linkUri={linkUri} facets={context.facets} ident="term_name" /> : null}
                    </div>
                : null}
            </div>
        );
    }
}

SummaryData.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
    displayCharts: PropTypes.string, // Optional property that allows display of subset of charts
};

SummaryData.defaultProps = {
    displayCharts: 'all',
};

class SummaryBody extends React.Component {
    constructor(props) {
        super(props);
        const searchQuery = url.parse(this.props.context['@id']).search;
        const terms = queryString.parse(searchQuery);
        this.state = {
            selectedOrganism: terms[organismField] ? terms[organismField] : [],
        };
        this.chooseOrganism = this.chooseOrganism.bind(this);
    }

    chooseOrganism(e) {
        this.setState({
            selectedOrganism: e.currentTarget.id,
        });
        const parsedUrl = url.parse(this.props.context['@id']);
        const query = new QueryString(parsedUrl.query);
        query.deleteKeyValue(systemsField);
        query.deleteKeyValue(organField);
        query.replaceKeyValue(organismField, e.currentTarget.id, '');
        const href = `?${query.format()}`;
        this.context.navigate(href);
    }
    render() {
        const searchQuery = url.parse(this.props.context['@id']).search;
        const query = new QueryString(searchQuery);
        const nonPersistentQuery = query.clone();
        nonPersistentQuery.deleteKeyValue('?type');
        const clearButton = nonPersistentQuery.queryCount() > 0 && query.queryCount('?type') > 0;
        return (
            <div className="summary-header">
                <div className="summary-header__title_control">
                    <div className="summary-header__title">
                        <h1>{this.props.context.title}</h1>
                    </div>
                    <ClearFilters searchUri={this.props.context.clear_filters} enableDisplay={!!clearButton} />
                </div>
                <div className="summary-controls">
                    <div className={`results-controls ${this.state.selectedOrganism.length > 0 ? `${this.state.selectedOrganism.replace(' ', '-')}` : ''}`}>
                        <div className="results-count">There {this.props.context.total > 1 ? 'are' : 'is'} <b className="bold-total">{this.props.context.total}</b> result{this.props.context.total > 1 ? 's' : ''}.</div>
                        <div className="view-controls-container">
                            <ViewControls results={this.props.context} alternativeNames={['Tabular report', 'Summary matrix']} />
                        </div>
                    </div>
                    {(this.state.selectedOrganism === 'Homo sapiens') ?
                        <React.Fragment>
                            <div className="flex-container">
                                <BodyMap context={this.props.context} />
                                <SummaryData context={this.props.context} displayCharts={'donuts'} />
                            </div>
                            <div className="summary-content">
                                <SummaryData context={this.props.context} displayCharts={'area'} />
                            </div>
                        </React.Fragment>
                    :
                        <React.Fragment>
                            <SummaryHorizontalFacets context={this.props.context} facetList={'all'} />
                            <div className="summary-content">
                                <SummaryData context={this.props.context} displayCharts={'all'} />
                            </div>
                        </React.Fragment>
                    }
                </div>
            </div>
        );
    }
}

SummaryBody.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
};

SummaryBody.contextTypes = {
    navigate: PropTypes.func,
    location_href: PropTypes.string,
};

// Render the entire summary page based on summary search results.
const Summary = (props) => {
    const { context } = props;
    const itemClass = globals.itemClass(context, 'view-item');

    if (context.total) {
        return (
            <Panel addClasses={itemClass}>
                <PanelBody>
                    <SummaryBody context={context} />
                </PanelBody>
            </Panel>
        );
    }
    return <h4>No results found</h4>;
};

Summary.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
};

globals.contentViews.register(Summary, 'Summary');
