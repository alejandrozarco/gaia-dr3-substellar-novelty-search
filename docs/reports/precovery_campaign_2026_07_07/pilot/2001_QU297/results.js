/**
 * Pull the GET form contents and submit them to the Perl backend.
 */
(($, document) => {
    $(document).on('ajax-failed.wb', (event) => {
        if (event.target.classList.contains('skeleton-loader-container')) {
            // Remove the skeleton loader
            event.target.classList.remove('skeleton-loader-container')
            
            event.target.innerHTML = document.getElementById('query_ajax_error_message').innerHTML
            event.target.classList.add('alert', 'alert-warning')
        }
    })
    
    document.addEventListener('DOMContentLoaded', () => {
        const searchEndpoint = `/cadcbin/ssos/ssosclf.pl${window.location.search}`
        console.debug(`Searching from ${searchEndpoint}\n`)

        const resultsContainer = document.getElementById('ssois_results')

        showLoading()

        /*
         * Fetch the results from the search endpoint and display them in the results container.
         * This is a fix as the WET-BOEW data-ajax-replace attribute is not working as expected.
         * 2026.04.01 jenkinsd
         */
        fetch(searchEndpoint)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`)
                }
                return response.text()
            })
            .then((html) => {
                resultsContainer.classList.remove('skeleton-loader-container')
                resultsContainer.innerHTML = html
            })
            .catch(() => {
                resultsContainer.classList.remove('skeleton-loader-container')
                resultsContainer.innerHTML = document.getElementById('query_ajax_error_message').innerHTML
                resultsContainer.classList.add('alert', 'alert-warning')
            })
    })
})(jQuery, document)
