from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Define the Monte Carlo simulation function
def monte_carlo_simulation(initial_savings, withdrawal_rate, equity_allocation, bond_allocation, equity_mean_return, equity_std_dev, bond_mean_return, bond_std_dev, inflation_mean, inflation_std_dev, num_simulations, num_years_list):
    results = []
    zero_savings_likelihoods = []

    for years in num_years_list:
        savings_matrix = np.zeros((num_simulations, years + 1))
        zero_savings_count = 0
        for i in range(num_simulations):
            savings = initial_savings
            withdrawal = withdrawal_rate * savings
            for year in range(1, years + 1):
                equity_return = np.random.normal(equity_mean_return, equity_std_dev)
                bond_return = np.random.normal(bond_mean_return, bond_std_dev)
                inflation = np.random.normal(inflation_mean, inflation_std_dev)
                equity_portion = equity_allocation * savings
                bond_portion = bond_allocation * savings
                equity_gain = equity_portion * equity_return
                bond_gain = bond_portion * bond_return
                total_gain = equity_gain + bond_gain
                savings += total_gain
                withdrawal = (1 + inflation) * withdrawal
                savings -= withdrawal
                
                if savings < 0:
                    savings = 0
                    #print("Adding zero savings")
                    zero_savings_count += 1
                    break
                
                #print(f"Savings in Year {year} are {savings}")

                #print(f"savings are {savings} in year {year} and iteration {i}")
                                
                savings_matrix[i, year] = savings

        #print(zero_savings_count)
        zero_savings_likelihood = zero_savings_count / num_simulations
        zero_savings_likelihoods.append(zero_savings_likelihood)
        
        #print(savings_matrix.shape)
        percentiles = np.percentile(savings_matrix, [5, 10, 25, 50], axis=0)
        #print(percentiles)


                
        # Append the likelihood to the percentiles list
        results.append(percentiles)
    
    #print(zero_savings_likelihoods)

    columns = ['{} Years'.format(years) for years in num_years_list]
    index = ['5th Percentile', '10th Percentile', '25th Percentile', '50th Percentile']
    data = {column: {} for column in columns}

    for i, percentile in enumerate(index):
        for j, years in enumerate(num_years_list):
            data[columns[j]][percentile] = results[j][i, -1]
            #print(f"{results[j][i, -1]} = data[{columns[j]}][{percentile}]")
    
    df = pd.DataFrame(data)
    df = df.transpose()
    df['Likelihood of Zero Savings'] = zero_savings_likelihoods
    df = df.transpose()

    return df

# Route to handle the form submission and return the calculated DataFrame as JSON
@app.route('/calculate', methods=['POST'])
def calculate():
    # Get form data
    initial_savings = float(request.form['initialSavings'])
    withdrawal_rate = float(request.form['withdrawalRate'])
    equity_allocation = 0.2  # Example value
    bond_allocation = 0.8  # Example value
    equity_mean_return = 0.184  # Example value
    equity_std_dev = 0.351  # Example value
    bond_mean_return = 0.106  # Example value
    bond_std_dev = 0.032  # Example value
    inflation_mean = 0.094 # Example value
    inflation_std_dev = 0.053 # Example value
    num_simulations = 1000  # Example value
    num_years_list = [20, 25, 30, 35, 40, 45, 50]  # Example value

    # Perform Monte Carlo simulation
    results_df = monte_carlo_simulation(initial_savings, withdrawal_rate, equity_allocation, bond_allocation, equity_mean_return, equity_std_dev, bond_mean_return, bond_std_dev, inflation_mean, inflation_std_dev, num_simulations, num_years_list)

    # Convert DataFrame to JSON and return
    result = jsonify(results_df.to_dict())
    result.headers.add('Access-Control-Allow-Origin', '*')
    return result



@app.route('/')
def homepage():
    return app.send_static_file("index.html")

@app.route('/static/style.css')
def homepage_css():
    return app.send_static_file("style.css")

@app.route('/static/script.js')
def homepage_script():
    return app.send_static_file("script.js")

if __name__ == '__main__':
    app.run(debug=True)
