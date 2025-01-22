from flask import Flask, render_template, jsonify
import pandas as pd
import altair as alt

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():

    # Read the CSV file into a DataFrame
    df = pd.read_csv(r'django_project/CBAS_col_rec_sample.csv') 

    # Convert `cr_date_of_issuance` to datetime
    df['cr_date_of_issuance'] = pd.to_datetime(df['cr_date_of_issuance'], errors='coerce', dayfirst=True)

    # Create a `year_month` column
    df['year_month'] = df['cr_date_of_issuance'].dt.strftime('%Y-%m')

    # Aggregate data for charts
    df_agg = df.groupby(['year_month']).agg(
        pa_amount=('pa_amount', 'sum'),
        cr_vault_number=('cr_vault_number', 'count')
    ).reset_index()

    # --- Limit df_agg to the last 12 months ---
    df_agg = df_agg.sort_values(by='year_month', ascending=False).head(36)

    # Aggregate data for scorecards
    df_agg_type = df.groupby('pa_type_of_p').agg(
        total_amount=('pa_amount', 'sum'),
        vault_count=('cr_vault_number', 'count')
    ).reset_index()

    # Aggregate data for scorecards (excluding "Vacant")
    df_agg_type = df[df['pa_type_of_p'] != 'Vacant'].groupby('pa_type_of_p').agg(
        total_amount=('pa_amount', 'sum'),
        vault_count=('cr_vault_number', 'count')
    ).reset_index()

    # --- Calculate total vault count (excluding "Vacant") ---
    total_vault_count = df[df['pa_type_of_p'] != 'Vacant']['cr_vault_number'].count()

    # --- Calculate total vacant vaults ---
    total_vacant_vaults = df[df['pa_type_of_p'] == 'Vacant']['cr_vault_number'].count()

    # Chart 1: Donut chart (include vacant count)
    chart1 = alt.Chart(df).mark_arc(innerRadius=50, outerRadius=120).encode(
        theta=alt.Theta(field="pa_type_of_p", aggregate="count", type="quantitative"),
        color=alt.Color(
        field="pa_type_of_p", 
        type="nominal", 
        legend=alt.Legend(orient="right", legendX=150, legendY=100)  # Adjust values as needed
        ),
        tooltip=['pa_type_of_p', 'count()'] 
    ).properties(
        title='Distribution of Type of Contribution'
    )

    # Chart 2 and 3: Combined bar and line chart 
    chart2 = alt.Chart(df_agg).mark_bar(color='steelblue').encode(  # Set bar color to steelblue
        x=alt.X('year_month', title='Month Year'),
        y=alt.Y('pa_amount', title='Total Amount'),
        tooltip=['year_month', 'pa_amount']
    )

    chart3 = alt.Chart(df_agg).mark_line(point=True, color='firebrick').encode(  # Set line color to firebrick
        x=alt.X('year_month', title='Month Year'),
        y=alt.Y('cr_vault_number', title='Vault Number Count'),
        tooltip=['year_month', 'cr_vault_number']
    )

    chart2_3 = alt.layer(chart2, chart3).resolve_scale(
        y='independent'
    ).properties(
        title='Total Amount and Vault Count by Month'
    )

    # Scorecards
    total_pa_amount = df['pa_amount'].sum()

    scorecard1 = alt.Chart(pd.DataFrame({'Total pa_amount': [total_pa_amount]})).mark_text(
        size=24, fontWeight='bold', align='center'
    ).encode(
        text=alt.Text('Total pa_amount:Q', format='.0f')
    ).properties(title='Total Amount of Contribution')

    scorecard2 = alt.Chart(pd.DataFrame({'Total Vault Count': [total_vault_count]})).mark_text(
        size=24, fontWeight='bold', align='center'
    ).encode(
        text='Total Vault Count:Q' 
    ).properties(title='Total Count of Occupied Vaults') # Changed title

    # --- Scorecard for vacant vaults ---
    scorecard3 = alt.Chart(pd.DataFrame({'Total Vacant Vaults': [total_vacant_vaults]})).mark_text(
        size=24, fontWeight='bold', align='center'
    ).encode(
        text='Total Vacant Vaults:Q'
    ).properties(title='Total Count of Vacant Vaults')

    # Scorecard 4 and 5 using `df_agg_type` (now excluding "Vacant")
    scorecard4 = alt.Chart(df_agg_type).mark_text(size=20).encode(
        y=alt.Y('pa_type_of_p', title='Payment Type'),
        x=alt.X('total_amount', title='Total Amount'),
        text=alt.Text('total_amount', format=',.0f'),
        tooltip=['pa_type_of_p', 'total_amount']
    ).properties(title='Total Amount of Contribution by Payment Type')

    scorecard5 = alt.Chart(df_agg_type).mark_text(size=20).encode(
        y=alt.Y('pa_type_of_p', title='Payment Type'),
        x=alt.X('vault_count', title='Vault Count'),
        text=alt.Text('vault_count', format=',.0f'),
        tooltip=['pa_type_of_p', 'vault_count']
    ).properties(title='Total Count of Vaults by Payment Type')

    # Combine into dashboard
    dashboard = alt.vconcat(
        # Place scorecard1, scorecard2, and scorecard3 side by side
        alt.hconcat(scorecard2, scorecard1, scorecard3), 
        alt.hconcat(scorecard4, scorecard5), 
        chart1,
        chart2_3
    ).configure_view(
        stroke=None
    ).configure(
        background='#ADD8E6',
        legend={
            "orient": "right"  # Set default legend position for all charts
        }
    )

    # Return dashboard as JSON for rendering
    return dashboard.to_json()

if __name__ == '__main__':
    app.run(debug=True)
