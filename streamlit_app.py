import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Truck TCO Vergleichsrechner | Diesel vs. E-Truck",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional B2B look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #5A6C7D;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .diesel-card {
        background: linear-gradient(135deg, #434343 0%, #000000 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff6b6b;
    }
    .electric-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #38ef7d;
    }
    .highlight-green {
        color: #2ecc71;
        font-weight: bold;
    }
    .highlight-red {
        color: #e74c3c;
        font-weight: bold;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
    .info-box {
        background-color: #e8f4fd;
        border-left: 4px solid #1E88E5;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def format_currency(value):
    """Format value as Euro currency"""
    return f"{value:,.0f} €".replace(",", ".")


def format_number(value):
    """Format number with thousand separators"""
    return f"{value:,.0f}".replace(",", ".")


def calculate_diesel_tco(params, years):
    """Calculate Total Cost of Ownership for Diesel Truck"""
    # Initial costs
    purchase_price = params['diesel_purchase_price']

    # Annual operating costs
    annual_km = params['annual_km']
    fuel_consumption = params['diesel_consumption']  # L/100km
    fuel_price = params['diesel_price']  # €/L

    # Annual fuel cost
    annual_fuel_cost = (annual_km / 100) * fuel_consumption * fuel_price

    # Maintenance costs (higher for diesel)
    annual_maintenance = params['diesel_maintenance']

    # Insurance
    annual_insurance = params['diesel_insurance']

    # Road tax / Maut
    annual_toll = params['annual_toll_diesel']

    # AdBlue costs
    adblue_cost = (annual_km / 100) * params['adblue_consumption'] * params['adblue_price']

    # Annual operating cost
    annual_operating = annual_fuel_cost + annual_maintenance + annual_insurance + annual_toll + adblue_cost

    # Residual value calculation (linear depreciation)
    residual_value = purchase_price * params['diesel_residual_value_pct'] / 100

    # TCO over years
    tco_by_year = []
    cumulative_cost = purchase_price

    for year in range(1, years + 1):
        cumulative_cost += annual_operating
        # Adjust for residual value at end of period
        if year == years:
            effective_tco = cumulative_cost - residual_value
        else:
            effective_tco = cumulative_cost
        tco_by_year.append({
            'year': year,
            'cumulative_cost': cumulative_cost,
            'effective_tco': effective_tco,
            'annual_fuel': annual_fuel_cost,
            'annual_maintenance': annual_maintenance,
            'annual_insurance': annual_insurance,
            'annual_toll': annual_toll,
            'adblue': adblue_cost
        })

    return {
        'purchase_price': purchase_price,
        'annual_fuel_cost': annual_fuel_cost,
        'annual_maintenance': annual_maintenance,
        'annual_insurance': annual_insurance,
        'annual_toll': annual_toll,
        'adblue_cost': adblue_cost,
        'annual_operating': annual_operating,
        'residual_value': residual_value,
        'total_tco': cumulative_cost - residual_value,
        'cost_per_km': (cumulative_cost - residual_value) / (annual_km * years),
        'tco_by_year': tco_by_year
    }


def calculate_electric_tco(params, years):
    """Calculate Total Cost of Ownership for Electric Truck"""
    # Initial costs
    purchase_price = params['electric_purchase_price']

    # Subsidies/Förderung
    subsidy = params['electric_subsidy']
    effective_purchase = purchase_price - subsidy

    # Charging infrastructure (one-time)
    charging_infrastructure = params['charging_infrastructure']

    # Annual operating costs
    annual_km = params['annual_km']
    energy_consumption = params['electric_consumption']  # kWh/100km
    energy_price = params['electricity_price']  # €/kWh

    # Annual energy cost
    annual_energy_cost = (annual_km / 100) * energy_consumption * energy_price

    # Maintenance costs (lower for electric)
    annual_maintenance = params['electric_maintenance']

    # Insurance
    annual_insurance = params['electric_insurance']

    # Road tax / Maut (often reduced or exempt for electric)
    annual_toll = params['annual_toll_electric']

    # Annual operating cost
    annual_operating = annual_energy_cost + annual_maintenance + annual_insurance + annual_toll

    # Residual value calculation
    residual_value = purchase_price * params['electric_residual_value_pct'] / 100

    # TCO over years
    tco_by_year = []
    cumulative_cost = effective_purchase + charging_infrastructure

    for year in range(1, years + 1):
        cumulative_cost += annual_operating
        if year == years:
            effective_tco = cumulative_cost - residual_value
        else:
            effective_tco = cumulative_cost
        tco_by_year.append({
            'year': year,
            'cumulative_cost': cumulative_cost,
            'effective_tco': effective_tco,
            'annual_energy': annual_energy_cost,
            'annual_maintenance': annual_maintenance,
            'annual_insurance': annual_insurance,
            'annual_toll': annual_toll
        })

    return {
        'purchase_price': purchase_price,
        'subsidy': subsidy,
        'effective_purchase': effective_purchase,
        'charging_infrastructure': charging_infrastructure,
        'annual_energy_cost': annual_energy_cost,
        'annual_maintenance': annual_maintenance,
        'annual_insurance': annual_insurance,
        'annual_toll': annual_toll,
        'annual_operating': annual_operating,
        'residual_value': residual_value,
        'total_tco': cumulative_cost - residual_value,
        'cost_per_km': (cumulative_cost - residual_value) / (annual_km * years),
        'tco_by_year': tco_by_year
    }


def calculate_co2_emissions(params, years):
    """Calculate CO2 emissions for both truck types"""
    annual_km = params['annual_km']

    # Diesel CO2 emissions (Tank-to-Wheel + Well-to-Tank)
    diesel_ttw = (annual_km / 100) * params['diesel_consumption'] * 2.64  # kg CO2/L Diesel
    diesel_wtw = diesel_ttw * 1.2  # Well-to-Wheel factor

    # Electric CO2 emissions (based on electricity mix)
    electric_co2 = (annual_km / 100) * params['electric_consumption'] * params['electricity_co2']  # g CO2/kWh

    return {
        'diesel_annual_co2': diesel_wtw,
        'electric_annual_co2': electric_co2,
        'diesel_total_co2': diesel_wtw * years,
        'electric_total_co2': electric_co2 * years,
        'co2_savings_annual': diesel_wtw - electric_co2,
        'co2_savings_total': (diesel_wtw - electric_co2) * years
    }


def find_break_even_year(diesel_tco, electric_tco):
    """Find the year when E-Truck becomes more economical"""
    diesel_costs = [d['cumulative_cost'] for d in diesel_tco['tco_by_year']]
    electric_costs = [e['cumulative_cost'] for e in electric_tco['tco_by_year']]

    # Check if electric starts cheaper (due to subsidies)
    if electric_costs[0] < diesel_costs[0]:
        return 0

    for i in range(len(diesel_costs)):
        if electric_costs[i] <= diesel_costs[i]:
            return i + 1

    return None  # No break-even within analysis period


def create_tco_comparison_chart(diesel_tco, electric_tco, years):
    """Create TCO comparison line chart"""
    years_range = list(range(0, years + 1))

    # Build cumulative costs starting from purchase
    diesel_costs = [diesel_tco['purchase_price']]
    electric_costs = [electric_tco['effective_purchase'] + electric_tco['charging_infrastructure']]

    for d, e in zip(diesel_tco['tco_by_year'], electric_tco['tco_by_year']):
        diesel_costs.append(d['cumulative_cost'])
        electric_costs.append(e['cumulative_cost'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=years_range,
        y=diesel_costs,
        name='Diesel-LKW',
        line=dict(color='#e74c3c', width=3),
        fill='tozeroy',
        fillcolor='rgba(231, 76, 60, 0.1)'
    ))

    fig.add_trace(go.Scatter(
        x=years_range,
        y=electric_costs,
        name='E-LKW',
        line=dict(color='#27ae60', width=3),
        fill='tozeroy',
        fillcolor='rgba(39, 174, 96, 0.1)'
    ))

    # Find and mark break-even point
    break_even = find_break_even_year(diesel_tco, electric_tco)
    if break_even and break_even <= years:
        fig.add_vline(x=break_even, line_dash="dash", line_color="orange",
                      annotation_text=f"Break-Even: Jahr {break_even}")

    fig.update_layout(
        title='Kumulierte Gesamtkosten (TCO) im Zeitverlauf',
        xaxis_title='Jahre',
        yaxis_title='Kumulierte Kosten (€)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        height=450,
        yaxis_tickformat=',',
        yaxis_ticksuffix=' €'
    )

    return fig


def create_cost_breakdown_chart(diesel_tco, electric_tco, years):
    """Create cost breakdown comparison bar chart"""
    categories = ['Anschaffung\n(netto)', 'Kraftstoff/\nEnergie', 'Wartung', 'Versicherung', 'Maut/Steuern', 'Sonstige']

    diesel_values = [
        diesel_tco['purchase_price'],
        diesel_tco['annual_fuel_cost'] * years,
        diesel_tco['annual_maintenance'] * years,
        diesel_tco['annual_insurance'] * years,
        diesel_tco['annual_toll'] * years,
        diesel_tco['adblue_cost'] * years
    ]

    electric_values = [
        electric_tco['effective_purchase'] + electric_tco['charging_infrastructure'],
        electric_tco['annual_energy_cost'] * years,
        electric_tco['annual_maintenance'] * years,
        electric_tco['annual_insurance'] * years,
        electric_tco['annual_toll'] * years,
        0
    ]

    fig = go.Figure(data=[
        go.Bar(name='Diesel-LKW', x=categories, y=diesel_values, marker_color='#e74c3c'),
        go.Bar(name='E-LKW', x=categories, y=electric_values, marker_color='#27ae60')
    ])

    fig.update_layout(
        title=f'Kostenaufschlüsselung über {years} Jahre',
        barmode='group',
        yaxis_title='Kosten (€)',
        height=400,
        yaxis_tickformat=',',
        yaxis_ticksuffix=' €'
    )

    return fig


def create_annual_cost_chart(diesel_tco, electric_tco):
    """Create annual operating costs comparison"""
    categories = ['Kraftstoff/Energie', 'Wartung', 'Versicherung', 'Maut/Steuern', 'AdBlue']

    diesel_values = [
        diesel_tco['annual_fuel_cost'],
        diesel_tco['annual_maintenance'],
        diesel_tco['annual_insurance'],
        diesel_tco['annual_toll'],
        diesel_tco['adblue_cost']
    ]

    electric_values = [
        electric_tco['annual_energy_cost'],
        electric_tco['annual_maintenance'],
        electric_tco['annual_insurance'],
        electric_tco['annual_toll'],
        0
    ]

    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=categories,
        values=diesel_values,
        name='Diesel',
        domain={'x': [0, 0.45]},
        marker_colors=['#e74c3c', '#c0392b', '#a93226', '#922b21', '#7b241c'],
        title='Diesel-LKW'
    ))

    fig.add_trace(go.Pie(
        labels=categories,
        values=electric_values,
        name='Elektro',
        domain={'x': [0.55, 1]},
        marker_colors=['#27ae60', '#229954', '#1e8449', '#196f3d', '#145a32'],
        title='E-LKW'
    ))

    fig.update_layout(
        title='Jährliche Betriebskosten - Verteilung',
        height=350,
        annotations=[
            dict(text='Diesel', x=0.18, y=-0.1, font_size=14, showarrow=False),
            dict(text='Elektro', x=0.82, y=-0.1, font_size=14, showarrow=False)
        ]
    )

    return fig


def create_co2_chart(co2_data, years):
    """Create CO2 emissions comparison chart"""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Diesel-LKW',
        x=['Jährliche Emissionen', f'Gesamtemissionen ({years} Jahre)'],
        y=[co2_data['diesel_annual_co2'] / 1000, co2_data['diesel_total_co2'] / 1000],
        marker_color='#e74c3c'
    ))

    fig.add_trace(go.Bar(
        name='E-LKW',
        x=['Jährliche Emissionen', f'Gesamtemissionen ({years} Jahre)'],
        y=[co2_data['electric_annual_co2'] / 1000, co2_data['electric_total_co2'] / 1000],
        marker_color='#27ae60'
    ))

    fig.update_layout(
        title='CO₂-Emissionen Vergleich',
        yaxis_title='CO₂-Emissionen (Tonnen)',
        barmode='group',
        height=350
    )

    return fig


def create_sensitivity_chart(params, years, variable, variable_name, range_pct=30):
    """Create sensitivity analysis chart"""
    base_value = params[variable]
    variations = np.linspace(base_value * (1 - range_pct/100), base_value * (1 + range_pct/100), 7)

    diesel_tcos = []
    electric_tcos = []

    for val in variations:
        test_params = params.copy()
        test_params[variable] = val

        diesel = calculate_diesel_tco(test_params, years)
        electric = calculate_electric_tco(test_params, years)

        diesel_tcos.append(diesel['total_tco'])
        electric_tcos.append(electric['total_tco'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=variations,
        y=diesel_tcos,
        name='Diesel-LKW',
        line=dict(color='#e74c3c', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=variations,
        y=electric_tcos,
        name='E-LKW',
        line=dict(color='#27ae60', width=2)
    ))

    fig.add_vline(x=base_value, line_dash="dash", line_color="gray",
                  annotation_text="Aktueller Wert")

    fig.update_layout(
        title=f'Sensitivitätsanalyse: {variable_name}',
        xaxis_title=variable_name,
        yaxis_title='TCO (€)',
        height=350,
        yaxis_tickformat=',',
        yaxis_ticksuffix=' €'
    )

    return fig


def generate_report_data(params, diesel_tco, electric_tco, co2_data, years, fleet_size):
    """Generate report data for export"""
    report = {
        'Analysedatum': datetime.now().strftime('%d.%m.%Y'),
        'Analysezeitraum (Jahre)': years,
        'Flottengröße': fleet_size,
        'Jährliche Fahrleistung (km)': params['annual_km'],

        'Diesel-LKW Anschaffungspreis': diesel_tco['purchase_price'],
        'E-LKW Anschaffungspreis': electric_tco['purchase_price'],
        'E-LKW Förderung': electric_tco['subsidy'],

        'Diesel TCO (gesamt)': diesel_tco['total_tco'],
        'E-LKW TCO (gesamt)': electric_tco['total_tco'],
        'TCO Differenz': diesel_tco['total_tco'] - electric_tco['total_tco'],
        'TCO Ersparnis (%)': ((diesel_tco['total_tco'] - electric_tco['total_tco']) / diesel_tco['total_tco']) * 100,

        'Diesel Kosten/km': diesel_tco['cost_per_km'],
        'E-LKW Kosten/km': electric_tco['cost_per_km'],

        'Diesel CO2 (t/Jahr)': co2_data['diesel_annual_co2'] / 1000,
        'E-LKW CO2 (t/Jahr)': co2_data['electric_annual_co2'] / 1000,
        'CO2-Einsparung (t/Jahr)': co2_data['co2_savings_annual'] / 1000,

        'Flotte - Diesel TCO (gesamt)': diesel_tco['total_tco'] * fleet_size,
        'Flotte - E-LKW TCO (gesamt)': electric_tco['total_tco'] * fleet_size,
        'Flotte - TCO Ersparnis': (diesel_tco['total_tco'] - electric_tco['total_tco']) * fleet_size,
        'Flotte - CO2-Einsparung (t)': co2_data['co2_savings_total'] * fleet_size / 1000
    }

    return report


# Main Application
def main():
    # Header
    st.markdown('<p class="main-header">🚛 Truck TCO Vergleichsrechner</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Diesel vs. Elektro - Fundierte Entscheidungen für Ihre Flotte</p>', unsafe_allow_html=True)

    # Sidebar for inputs
    with st.sidebar:
        st.header("⚙️ Parameter konfigurieren")

        # Analysis period
        st.subheader("📅 Analysezeitraum")
        years = st.slider("Nutzungsdauer (Jahre)", 3, 15, 8)

        # Fleet size
        st.subheader("🚛 Flotte")
        fleet_size = st.number_input("Anzahl Fahrzeuge", min_value=1, max_value=1000, value=1, step=1)

        # Usage parameters
        st.subheader("📊 Nutzungsprofil")
        annual_km = st.number_input("Jährliche Fahrleistung (km)",
                                    min_value=10000, max_value=500000, value=120000, step=5000)

        # Diesel truck parameters
        st.subheader("🛢️ Diesel-LKW")
        diesel_purchase = st.number_input("Anschaffungspreis (€)",
                                          min_value=50000, max_value=300000, value=120000, step=5000,
                                          key='diesel_purchase')
        diesel_consumption = st.number_input("Verbrauch (L/100km)",
                                             min_value=15.0, max_value=50.0, value=32.0, step=0.5)
        diesel_price = st.number_input("Dieselpreis (€/L)",
                                       min_value=1.0, max_value=3.0, value=1.65, step=0.05)
        diesel_maintenance = st.number_input("Jährliche Wartungskosten (€)",
                                             min_value=2000, max_value=30000, value=12000, step=500,
                                             key='diesel_maint')

        # Electric truck parameters
        st.subheader("⚡ E-LKW")
        electric_purchase = st.number_input("Anschaffungspreis (€)",
                                            min_value=100000, max_value=500000, value=220000, step=5000,
                                            key='electric_purchase')
        electric_subsidy = st.number_input("Förderung/Zuschuss (€)",
                                           min_value=0, max_value=100000, value=30000, step=1000)
        electric_consumption = st.number_input("Verbrauch (kWh/100km)",
                                               min_value=80.0, max_value=200.0, value=120.0, step=5.0)
        electricity_price = st.number_input("Strompreis (€/kWh)",
                                            min_value=0.10, max_value=0.60, value=0.25, step=0.01)
        electric_maintenance = st.number_input("Jährliche Wartungskosten (€)",
                                               min_value=1000, max_value=20000, value=6000, step=500,
                                               key='electric_maint')
        charging_infra = st.number_input("Ladeinfrastruktur (einmalig, €)",
                                         min_value=0, max_value=100000, value=25000, step=1000)

        # Advanced parameters (expandable)
        with st.expander("🔧 Erweiterte Parameter"):
            st.markdown("**Versicherung**")
            diesel_insurance = st.number_input("Diesel - Jährlich (€)", value=8000, step=500, key='d_ins')
            electric_insurance = st.number_input("E-LKW - Jährlich (€)", value=9000, step=500, key='e_ins')

            st.markdown("**Maut & Steuern**")
            toll_diesel = st.number_input("Diesel - Jährlich (€)", value=15000, step=500, key='d_toll')
            toll_electric = st.number_input("E-LKW - Jährlich (€)", value=5000, step=500, key='e_toll')

            st.markdown("**Restwert**")
            diesel_residual = st.slider("Diesel-Restwert (%)", 5, 40, 15, key='d_res')
            electric_residual = st.slider("E-LKW-Restwert (%)", 5, 40, 20, key='e_res')

            st.markdown("**AdBlue (Diesel)**")
            adblue_consumption = st.number_input("Verbrauch (L/100km)", value=1.5, step=0.1)
            adblue_price = st.number_input("Preis (€/L)", value=0.80, step=0.05)

            st.markdown("**CO₂-Faktoren**")
            electricity_co2 = st.number_input("Strommix (g CO₂/kWh)", value=400, step=10)

    # Build parameters dictionary
    params = {
        'annual_km': annual_km,
        'diesel_purchase_price': diesel_purchase,
        'diesel_consumption': diesel_consumption,
        'diesel_price': diesel_price,
        'diesel_maintenance': diesel_maintenance,
        'diesel_insurance': diesel_insurance,
        'annual_toll_diesel': toll_diesel,
        'diesel_residual_value_pct': diesel_residual,
        'adblue_consumption': adblue_consumption,
        'adblue_price': adblue_price,
        'electric_purchase_price': electric_purchase,
        'electric_subsidy': electric_subsidy,
        'electric_consumption': electric_consumption,
        'electricity_price': electricity_price,
        'electric_maintenance': electric_maintenance,
        'electric_insurance': electric_insurance,
        'annual_toll_electric': toll_electric,
        'electric_residual_value_pct': electric_residual,
        'charging_infrastructure': charging_infra,
        'electricity_co2': electricity_co2
    }

    # Calculate TCO
    diesel_tco = calculate_diesel_tco(params, years)
    electric_tco = calculate_electric_tco(params, years)
    co2_data = calculate_co2_emissions(params, years)
    break_even = find_break_even_year(diesel_tco, electric_tco)

    # Key Metrics Row
    st.markdown("---")
    st.subheader("📈 Ergebnisübersicht")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🛢️ Diesel TCO",
            format_currency(diesel_tco['total_tco']),
            f"{diesel_tco['cost_per_km']:.2f} €/km"
        )

    with col2:
        st.metric(
            "⚡ E-LKW TCO",
            format_currency(electric_tco['total_tco']),
            f"{electric_tco['cost_per_km']:.2f} €/km"
        )

    with col3:
        savings = diesel_tco['total_tco'] - electric_tco['total_tco']
        savings_pct = (savings / diesel_tco['total_tco']) * 100
        st.metric(
            "💰 Ersparnis",
            format_currency(savings),
            f"{savings_pct:.1f}%" if savings > 0 else f"{savings_pct:.1f}%"
        )

    with col4:
        if break_even:
            st.metric(
                "📍 Break-Even",
                f"Jahr {break_even}",
                f"Nach {break_even * 12} Monaten"
            )
        else:
            st.metric(
                "📍 Break-Even",
                "Nicht erreicht",
                f"Im Zeitraum ({years} Jahre)"
            )

    # Recommendation box
    if savings > 0:
        st.success(f"""
        **✅ Empfehlung: E-LKW ist wirtschaftlicher!**

        Bei Ihrem Nutzungsprofil sparen Sie über {years} Jahre **{format_currency(savings)}**
        ({savings_pct:.1f}%) mit dem E-LKW. Der Break-Even-Punkt wird
        {"nach " + str(break_even) + " Jahren erreicht" if break_even else "nicht im Analysezeitraum erreicht"}.
        """)
    else:
        st.warning(f"""
        **⚠️ Hinweis: Diesel-LKW aktuell günstiger**

        Bei Ihrem aktuellen Nutzungsprofil ist der Diesel-LKW über {years} Jahre
        noch um **{format_currency(abs(savings))}** günstiger. Prüfen Sie die Parameter
        oder erwägen Sie einen längeren Analysezeitraum.
        """)

    # Main Charts
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 TCO-Vergleich",
        "💵 Kostenaufschlüsselung",
        "🌱 CO₂-Emissionen",
        "📈 Sensitivitätsanalyse",
        "🚛 Flottenrechner"
    ])

    with tab1:
        st.plotly_chart(create_tco_comparison_chart(diesel_tco, electric_tco, years),
                        use_container_width=True)

        # Detailed table
        st.subheader("Detaillierte Jahresübersicht")

        df_comparison = pd.DataFrame({
            'Jahr': list(range(1, years + 1)),
            'Diesel kumuliert (€)': [d['cumulative_cost'] for d in diesel_tco['tco_by_year']],
            'E-LKW kumuliert (€)': [e['cumulative_cost'] for e in electric_tco['tco_by_year']],
            'Differenz (€)': [d['cumulative_cost'] - e['cumulative_cost']
                            for d, e in zip(diesel_tco['tco_by_year'], electric_tco['tco_by_year'])]
        })

        st.dataframe(df_comparison.style.format({
            'Diesel kumuliert (€)': '{:,.0f}',
            'E-LKW kumuliert (€)': '{:,.0f}',
            'Differenz (€)': '{:,.0f}'
        }), use_container_width=True, hide_index=True)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(create_cost_breakdown_chart(diesel_tco, electric_tco, years),
                            use_container_width=True)

        with col2:
            st.plotly_chart(create_annual_cost_chart(diesel_tco, electric_tco),
                            use_container_width=True)

        # Cost breakdown table
        st.subheader("Kostendetails")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🛢️ Diesel-LKW**")
            diesel_breakdown = pd.DataFrame({
                'Kostenkategorie': ['Anschaffung', 'Kraftstoff (gesamt)', 'Wartung (gesamt)',
                                   'Versicherung (gesamt)', 'Maut (gesamt)', 'AdBlue (gesamt)',
                                   '- Restwert', '**TCO Gesamt**'],
                'Betrag (€)': [
                    diesel_tco['purchase_price'],
                    diesel_tco['annual_fuel_cost'] * years,
                    diesel_tco['annual_maintenance'] * years,
                    diesel_tco['annual_insurance'] * years,
                    diesel_tco['annual_toll'] * years,
                    diesel_tco['adblue_cost'] * years,
                    -diesel_tco['residual_value'],
                    diesel_tco['total_tco']
                ]
            })
            st.dataframe(diesel_breakdown.style.format({'Betrag (€)': '{:,.0f}'}),
                        use_container_width=True, hide_index=True)

        with col2:
            st.markdown("**⚡ E-LKW**")
            electric_breakdown = pd.DataFrame({
                'Kostenkategorie': ['Anschaffung', '- Förderung', 'Ladeinfrastruktur',
                                   'Energie (gesamt)', 'Wartung (gesamt)', 'Versicherung (gesamt)',
                                   'Maut (gesamt)', '- Restwert', '**TCO Gesamt**'],
                'Betrag (€)': [
                    electric_tco['purchase_price'],
                    -electric_tco['subsidy'],
                    electric_tco['charging_infrastructure'],
                    electric_tco['annual_energy_cost'] * years,
                    electric_tco['annual_maintenance'] * years,
                    electric_tco['annual_insurance'] * years,
                    electric_tco['annual_toll'] * years,
                    -electric_tco['residual_value'],
                    electric_tco['total_tco']
                ]
            })
            st.dataframe(electric_breakdown.style.format({'Betrag (€)': '{:,.0f}'}),
                        use_container_width=True, hide_index=True)

    with tab3:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.plotly_chart(create_co2_chart(co2_data, years), use_container_width=True)

        with col2:
            st.markdown("### 🌍 Umweltbilanz")

            st.metric(
                "CO₂-Einsparung pro Jahr",
                f"{co2_data['co2_savings_annual']/1000:.1f} t",
                f"{(co2_data['co2_savings_annual']/co2_data['diesel_annual_co2'])*100:.0f}% weniger"
            )

            st.metric(
                f"CO₂-Einsparung ({years} Jahre)",
                f"{co2_data['co2_savings_total']/1000:.1f} t",
                ""
            )

            # Equivalent calculations
            trees_equivalent = co2_data['co2_savings_total'] / 21  # ~21kg CO2/tree/year
            st.info(f"""
            **Das entspricht:**
            - 🌳 {trees_equivalent:.0f} Bäume (jährliche Absorption)
            - 🚗 {co2_data['co2_savings_total']/120:.0f} PKW-Kilometer vermieden
            """)

    with tab4:
        st.markdown("""
        Die Sensitivitätsanalyse zeigt, wie sich Änderungen einzelner Parameter auf die
        Gesamtkosten (TCO) auswirken.
        """)

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(create_sensitivity_chart(params, years, 'diesel_price',
                                                     'Dieselpreis (€/L)'), use_container_width=True)
            st.plotly_chart(create_sensitivity_chart(params, years, 'annual_km',
                                                     'Jährliche Fahrleistung (km)'), use_container_width=True)

        with col2:
            st.plotly_chart(create_sensitivity_chart(params, years, 'electricity_price',
                                                     'Strompreis (€/kWh)'), use_container_width=True)
            st.plotly_chart(create_sensitivity_chart(params, years, 'electric_subsidy',
                                                     'E-LKW Förderung (€)'), use_container_width=True)

    with tab5:
        st.subheader(f"🚛 Flottenanalyse für {fleet_size} Fahrzeuge")

        if fleet_size > 1:
            fleet_diesel_tco = diesel_tco['total_tco'] * fleet_size
            fleet_electric_tco = electric_tco['total_tco'] * fleet_size
            fleet_savings = fleet_diesel_tco - fleet_electric_tco
            fleet_co2_savings = co2_data['co2_savings_total'] * fleet_size / 1000

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Flotte Diesel TCO", format_currency(fleet_diesel_tco))
            with col2:
                st.metric("Flotte E-LKW TCO", format_currency(fleet_electric_tco))
            with col3:
                st.metric("Flotte Ersparnis", format_currency(fleet_savings))
            with col4:
                st.metric("CO₂-Einsparung", f"{fleet_co2_savings:.0f} t")

            # Fleet transition scenario
            st.markdown("---")
            st.subheader("📈 Flottenumstellung - Szenario")

            transition_years = st.slider("Umstellungszeitraum (Jahre)", 1, 10, 3, key='transition')

            vehicles_per_year = max(1, fleet_size // transition_years)
            remaining = fleet_size % transition_years

            transition_data = []
            cumulative_electric = 0
            cumulative_investment = 0

            for year in range(1, transition_years + 1):
                new_electric = vehicles_per_year + (1 if year <= remaining else 0)
                cumulative_electric += new_electric
                diesel_remaining = fleet_size - cumulative_electric

                year_investment = new_electric * (electric_tco['effective_purchase'] +
                                                  electric_tco['charging_infrastructure'])
                cumulative_investment += year_investment

                year_savings = cumulative_electric * (diesel_tco['annual_operating'] -
                                                      electric_tco['annual_operating'])

                transition_data.append({
                    'Jahr': year,
                    'Neue E-LKW': new_electric,
                    'E-LKW gesamt': cumulative_electric,
                    'Diesel verbleibend': diesel_remaining,
                    'Investition (€)': year_investment,
                    'Kum. Investition (€)': cumulative_investment,
                    'Jährl. Ersparnis (€)': year_savings
                })

            df_transition = pd.DataFrame(transition_data)
            st.dataframe(df_transition.style.format({
                'Investition (€)': '{:,.0f}',
                'Kum. Investition (€)': '{:,.0f}',
                'Jährl. Ersparnis (€)': '{:,.0f}'
            }), use_container_width=True, hide_index=True)

            # Transition visualization
            fig = go.Figure()
            fig.add_trace(go.Bar(name='E-LKW', x=df_transition['Jahr'],
                                 y=df_transition['E-LKW gesamt'], marker_color='#27ae60'))
            fig.add_trace(go.Bar(name='Diesel', x=df_transition['Jahr'],
                                 y=df_transition['Diesel verbleibend'], marker_color='#e74c3c'))
            fig.update_layout(title='Flottenumstellung - Fahrzeugverteilung',
                             barmode='stack', xaxis_title='Jahr', yaxis_title='Anzahl Fahrzeuge')
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("Erhöhen Sie die Flottenanzahl in der Seitenleiste, um die Flottenanalyse zu nutzen.")

    # Export section
    st.markdown("---")
    st.subheader("📥 Report exportieren")

    col1, col2, col3 = st.columns(3)

    report_data = generate_report_data(params, diesel_tco, electric_tco, co2_data, years, fleet_size)
    df_report = pd.DataFrame([report_data])

    with col1:
        csv = df_report.T.to_csv(header=['Wert'])
        st.download_button(
            label="📊 CSV herunterladen",
            data=csv,
            file_name=f"truck_tco_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    with col2:
        # Generate text report
        text_report = f"""
TRUCK TCO VERGLEICHSREPORT
==========================
Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}

ANALYSEPARAMETER
----------------
Nutzungsdauer: {years} Jahre
Flottengröße: {fleet_size} Fahrzeuge
Jährliche Fahrleistung: {format_number(params['annual_km'])} km

ERGEBNISSE (PRO FAHRZEUG)
-------------------------
Diesel-LKW TCO: {format_currency(diesel_tco['total_tco'])}
E-LKW TCO: {format_currency(electric_tco['total_tco'])}
Differenz: {format_currency(diesel_tco['total_tco'] - electric_tco['total_tco'])}

Kosten pro km (Diesel): {diesel_tco['cost_per_km']:.3f} €
Kosten pro km (E-LKW): {electric_tco['cost_per_km']:.3f} €

Break-Even: {'Jahr ' + str(break_even) if break_even else 'Nicht im Analysezeitraum'}

CO2-BILANZ
----------
Diesel CO2/Jahr: {co2_data['diesel_annual_co2']/1000:.1f} t
E-LKW CO2/Jahr: {co2_data['electric_annual_co2']/1000:.1f} t
Einsparung/Jahr: {co2_data['co2_savings_annual']/1000:.1f} t

FLOTTENBERECHNUNG ({fleet_size} Fahrzeuge)
------------------------------------------
Diesel Flotte TCO: {format_currency(diesel_tco['total_tco'] * fleet_size)}
E-LKW Flotte TCO: {format_currency(electric_tco['total_tco'] * fleet_size)}
Gesamtersparnis: {format_currency((diesel_tco['total_tco'] - electric_tco['total_tco']) * fleet_size)}
CO2-Einsparung: {co2_data['co2_savings_total'] * fleet_size / 1000:.1f} t
        """

        st.download_button(
            label="📄 Text-Report herunterladen",
            data=text_report,
            file_name=f"truck_tco_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

    with col3:
        # Detailed Excel-like CSV
        detailed_data = []
        for year in range(1, years + 1):
            detailed_data.append({
                'Jahr': year,
                'Diesel_Kumuliert': diesel_tco['tco_by_year'][year-1]['cumulative_cost'],
                'ELkw_Kumuliert': electric_tco['tco_by_year'][year-1]['cumulative_cost'],
                'Diesel_Kraftstoff': diesel_tco['annual_fuel_cost'],
                'ELkw_Energie': electric_tco['annual_energy_cost'],
                'Differenz': diesel_tco['tco_by_year'][year-1]['cumulative_cost'] -
                            electric_tco['tco_by_year'][year-1]['cumulative_cost']
            })

        df_detailed = pd.DataFrame(detailed_data)
        csv_detailed = df_detailed.to_csv(index=False)

        st.download_button(
            label="📈 Detaildaten (CSV)",
            data=csv_detailed,
            file_name=f"truck_tco_details_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p>🚛 Truck TCO Vergleichsrechner | Diesel vs. E-Truck</p>
        <p>Die Berechnungen basieren auf den eingegebenen Parametern und dienen als Entscheidungshilfe.
        Für verbindliche Angebote kontaktieren Sie bitte Ihren Fahrzeughändler.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
