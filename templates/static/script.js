document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('calculatorForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent form submission
        
        // Get form data
        var formData = new FormData(this);

        // Send form data to the server using fetch
        fetch('http://localhost:5000/calculate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Display the results in the 'results' div
            var resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = ''; // Clear previous results

            // Create a responsive div container
            var responsiveDiv = document.createElement('div');
            responsiveDiv.className = 'table-responsive';

            var table = document.createElement('table');
            table.classList.add('results-table');

            // Add table headers
            var headerRow = document.createElement('tr');
            // Add empty cell for alignment with row names
            var emptyHeaderCell = document.createElement('th');
            emptyHeaderCell.textContent = '';
            headerRow.appendChild(emptyHeaderCell);
            var headers = Object.keys(data);
            headers.forEach(header => {
                var th = document.createElement('th');
                th.textContent = header;
                headerRow.appendChild(th);
            });
            table.appendChild(headerRow);

            // Add table rows
            var percentiles = Object.keys(data[headers[0]]);
            percentiles.forEach(percentile => {
                var row = document.createElement('tr');

                // Add row name cell
                var nameCell = document.createElement('td');
                nameCell.textContent = percentile;
                row.appendChild(nameCell);
                headers.forEach(header => {
                    var cell = document.createElement('td');
                    var value = data[header][percentile];
                    // Format rows except for the last one as currency and round to the nearest whole number
                    if (percentile !== 'Likelihood of Zero Savings') {
                        value = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Math.round(value)).split('.')[0];
                    } else {
                        // Format the last row as percentage and round to one decimal point
                        value = (value * 100).toFixed(1) + '%';
                    }
                    cell.textContent = value;
                    row.appendChild(cell);
                });
                table.appendChild(row);
            });

            // Append the table to the responsive div
            responsiveDiv.appendChild(table);
            // Append the responsive div to the results div
            resultsDiv.appendChild(responsiveDiv);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
