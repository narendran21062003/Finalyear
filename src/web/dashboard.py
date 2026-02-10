"""
Dashboard Module - Real-time Analytics Visualization
Streamlit-based interactive dashboard for lead analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.config.db_config import get_db_connection

# Page configuration
st.set_page_config(
    page_title="Autonomous Lead Intelligence",
    page_icon="🎯",
    layout="wide"
)

# Professional Styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    h1, h2, h3 {
        color: #1e3a8a;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

def fetch_leads_data():
    """Fetch all leads from MySQL database"""
    try:
        connection = get_db_connection()
        if not connection:
            return None
        
        query = "SELECT * FROM leads ORDER BY timestamp DESC"
        df = pd.read_sql(query, connection)
        connection.close()
        return df
    
    except Exception as e:
        st.error(f"Database error: {e}")
        return None

def main():
    # Header
    st.title("🎯 Autonomous Lead Identification Dashboard")
    st.markdown("---")
    
    # Refresh and Clear buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear All"):
            try:
                connection = get_db_connection()
                cursor = connection.cursor()
                cursor.execute("TRUNCATE TABLE leads")
                connection.commit()
                connection.close()
                st.success("Database cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing: {e}")
    
    # Create Tabs
    tab1, tab2 = st.tabs(["📊 Analytics Dashboard", "🚀 New Search"])
    
    with tab1:
        # Fetch data
        df = fetch_leads_data()
        
        if df is None or df.empty:
            st.warning("⚠️ No data available. Go to the 'New Search' tab to generate leads!")
        else:
            # KPI Metrics
            st.subheader("📈 Key Performance Indicators")
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.metric("Total Leads", len(df))
    
    with kpi2:
        active_sites = len(df[df['technical_status'] == 'Active'])
        st.metric("Active Websites", active_sites)
    
    with kpi3:
        # Check if email is not listed or null
        pending_contacts = len(df[df['email'] == 'Not listed'])
        st.metric("Pending Contacts", pending_contacts)
    
    with kpi4:
        unique_pain_points = df['pain_point'].nunique()
        st.metric("Unique Pain Points", unique_pain_points)
    
    st.markdown("---")
    
    # Charts Section
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🌐 Website Status Distribution")
        
        status_counts = df['technical_status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            hole=0.4, # Donut chart
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        fig_status.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col_right:
        st.subheader("🎯 Pain Point Analysis")
        
        pain_counts = df['pain_point'].value_counts().head(5)
        # Fix Plotly error by creating a clean DataFrame
        pain_df = pain_counts.reset_index()
        pain_df.columns = ['Pain Point', 'Count']
        
        fig_pain = px.bar(
            pain_df,
            x='Count',
            y='Pain Point',
            orientation='h',
            color='Count',
            color_continuous_scale='Viridis',
            text_auto=True
        )
        fig_pain.update_layout(
            showlegend=False,
            xaxis_title="Count",
            yaxis_title=None,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_pain, use_container_width=True)
        
        with st.expander("ℹ️ What do these Pain Points signify?"):
            st.markdown("""
            - **High Service Quality**: Positive reviews, satisfied customers (Minimal intervention needed).
            - **Standard Review Volume**: Average feedback, no major complaints but no rave reviews.
            - **Service Optimization**: Complaints about wait times, rude staff, or scheduling errors.
            - **Quality Control**: Reports of bad products, food, or workmanship.
            - **Pricing Strategy**: Complaints about high costs or poor value for money.
            - **Digital Presence**: Issues with website usage, booking systems, or online information.
            - **Logistics/Delivery**: Issues with shipping, late arrivals, or tracking.
            - **Inconclusive Data**: Not enough reviews to determine a helpful pattern.
            """)
    
    # Timeline Charts
    st.subheader("📅 Lead Acquisition Timeline")
    
    tab_time1, tab_time2 = st.tabs(["Daily Volume", "Cumulative Growth"])
    
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    timeline_data = df.groupby('date').size().reset_index(name='count')
    
    with tab_time1:
        fig_timeline = px.area(
            timeline_data,
            x='date',
            y='count',
            markers=True,
            title="Leads Collected Per Day",
            color_discrete_sequence=['#FF4B4B']
        )
        fig_timeline.update_layout(xaxis_title="Date", yaxis_title="Leads", hovermode="x unified")
        st.plotly_chart(fig_timeline, use_container_width=True)
        
    with tab_time2:
        timeline_data['cumulative'] = timeline_data['count'].cumsum()
        fig_cum = px.line(
            timeline_data,
            x='date',
            y='cumulative',
            markers=True,
            title="Total Leads Over Time",
            color_discrete_sequence=['#1e3a8a'] # Dark Blue
        )
        fig_cum.update_layout(xaxis_title="Date", yaxis_title="Total Leads", hovermode="x unified")
        # Fill area under line
        fig_cum.update_traces(fill='tozeroy')
        st.plotly_chart(fig_cum, use_container_width=True)
    
    st.markdown("---")
    
    # Data Table
    st.subheader("📋 Lead Details")
    
    # Filter options
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=df['technical_status'].unique(),
            default=df['technical_status'].unique()
        )
    
    with col_filter2:
        pain_filter = st.multiselect(
            "Filter by Pain Point",
            options=df['pain_point'].unique(),
            default=df['pain_point'].unique()
        )
    
    # Apply filters
    filtered_df = df[
        (df['technical_status'].isin(status_filter)) &
        (df['pain_point'].isin(pain_filter))
    ]
    
    # Display filtered data
    display_columns = ['business_name', 'website_url', 'technical_status', 
                      'pain_point', 'phone', 'email', 'timestamp']
    
    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=f"leads_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    with tab2:
        st.header("🔍 Advanced Area-Based Lead Search")
        
        # Initialize Session State for Multi-step Process
        if 'discovered_areas' not in st.session_state:
            st.session_state.discovered_areas = []
        if 'search_step' not in st.session_state:
            st.session_state.search_step = 1 # 1: Input, 2: Area Select, 3: Processing
        if 'initial_leads' not in st.session_state:
            st.session_state.initial_leads = []
        if 'search_params' not in st.session_state:
            st.session_state.search_params = {}

        # --- STEP 1: INPUTS ---
        if st.session_state.search_step == 1:
            with st.form("discovery_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    keyword = st.text_input("Industry/Keyword", placeholder="e.g. IT Companies, Text Showrooms")
                    country = st.text_input("Country", value="India")
                with col_b:
                    state = st.text_input("State", value="Tamil Nadu")
                    district = st.text_input("District", placeholder="e.g. Tirunelveli")

                submit_discovery = st.form_submit_button("🔎 Discover Areas & Leads")
            
            if submit_discovery and keyword and district:
                st.session_state.search_params = {
                    'keyword': keyword,
                    'country': country,
                    'state': state,
                    'district': district
                }
                
                status_text = st.empty()
                status_text.info(f"Step 1: Searching for main areas in {district}...")
                
                try:
                    # Import here to avoid circular imports if any
                    from src.modules.scout import WebScout
                    scout = WebScout()
                    
                    # Construct Broad Query
                    broad_query = f"{keyword} in {district} {state} {country}"
                    
                    # Run Broad Search (limit to 15 to get a good spread of areas)
                    leads = scout.find_leads(broad_query, max_results=15, location_context={'district': district, 'state': state})
                    scout.close()
                    
                    # Extract Areas
                    found_areas = set()
                    for lead in leads:
                        found_areas.update(lead.get('detected_areas', []))
                    
                    # Store Results
                    st.session_state.discovered_areas = sorted(list(found_areas))
                    st.session_state.initial_leads = leads # Keep these so we don't lose them
                    st.session_state.search_step = 2
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error during discovery: {e}")

        # --- STEP 2: AREA SELECTION & EXECUTION ---
        elif st.session_state.search_step == 2:
            st.success(f"✅ Found {len(st.session_state.discovered_areas)} potential areas in {st.session_state.search_params['district']}")
            
            with st.form("execution_form"):
                st.subheader("Select Areas to Target")
                
                # Multiselect for areas
                selected_areas = st.multiselect(
                    "Identified Areas (Select all that apply)",
                    options=st.session_state.discovered_areas,
                    default=st.session_state.discovered_areas[:5] # Default select first few
                )
                
                # Option to add custom areas
                custom_areas_input = st.text_area("Add Custom Areas (comma separated)", placeholder="e.g. Pettai, Melapalayam")
                
                # Limit limit
                leads_per_area = st.slider("Max leads per area", 5, 50, 10)
                
                start_scrape = st.form_submit_button("🚀 Start Deep Dive Scraping")
            
            if st.button("⬅️ Back to Search"):
                st.session_state.search_step = 1
                st.rerun()

            if start_scrape:
                # Merge Areas
                final_areas = list(selected_areas)
                if custom_areas_input:
                    custom_areas = [x.strip() for x in custom_areas_input.split(',') if x.strip()]
                    final_areas.extend(custom_areas)
                
                # Remove duplicates in areas
                final_areas = list(dict.fromkeys(final_areas))
                
                if not final_areas:
                    # If no areas selected, just use the district generic search
                    final_areas = ["Ordered Search"] 

                # --- EXECUTION LOGIC ---
                progress_text = st.empty()
                prog_bar = st.progress(0)
                result_area = st.container()
                
                try:
                    from src.modules.scout import WebScout
                    from src.modules.analyst import AIAnalyst
                    
                    scout = WebScout()
                    analyst = AIAnalyst()
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Deduplication Set (Load existing URLs to save time?)
                    # For now just deduplicate within this session + existing DB check
                    existing_urls = set()
                    cursor.execute("SELECT website_url FROM leads")
                    for (url,) in cursor.fetchall():
                        existing_urls.add(url)
                    
                    total_added = 0
                    
                    # Add initial leads first
                    progress_text.text("Processing initial discovery leads...")
                    for lead in st.session_state.initial_leads:
                         if lead['website_url'] not in existing_urls:
                            # ... (Save Logic - Logic Duplicated, should refactor but inline for now) ...
                            _process_and_save_lead(lead, analyst, cursor, conn)
                            existing_urls.add(lead['website_url'])
                            total_added += 1

                    # Iterate Areas
                    total_areas = len(final_areas)
                    
                    for i, area in enumerate(final_areas):
                        progress_val = int((i / total_areas) * 100)
                        prog_bar.progress(progress_val)
                        
                        target_query = ""
                        if area == "Ordered Search":
                             target_query = f"{st.session_state.search_params['keyword']} in {st.session_state.search_params['district']}"
                        else:
                             target_query = f"{st.session_state.search_params['keyword']} in {area}, {st.session_state.search_params['district']}"
                        
                        progress_text.text(f"Scraping Area: {area} ({i+1}/{total_areas})...")
                        
                        area_leads = scout.find_leads(target_query, max_results=leads_per_area)
                        
                        for lead in area_leads:
                            if lead['website_url'] not in existing_urls:
                                _process_and_save_lead(lead, analyst, cursor, conn)
                                existing_urls.add(lead['website_url'])
                                total_added += 1
                                
                    scout.close()
                    conn.close()
                    prog_bar.progress(100)
                    st.balloons()
                    st.success(f"🎉 Completed! Added {total_added} unique new leads.")
                    
                except Exception as e:
                    st.error(f"Execution Error: {e}")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Autonomous Customer Lead Identification System | "
        "Powered by MySQL + Hugging Face API + Streamlit"
        "</div>",
        unsafe_allow_html=True
    )

def _process_and_save_lead(lead, analyst, cursor, conn):
    """Helper to analyze and save a single lead"""
    try:
        # AI Analysis
        reviews = lead.get('reviews_snippet', 'No reviews')
        analysis = analyst.analyze_reviews(reviews)
        lead['pain_point'] = analysis['pain_point']
        
        # Draft
        lead['email_draft'] = analyst.generate_email_draft(
            lead['business_name'], 
            lead['pain_point']
        )
        lead['phone'] = lead.get('phone', 'Not listed')
        lead['email'] = lead.get('email', 'Not listed')
        
        # Save to DB
        insert_query = """
        INSERT IGNORE INTO leads (
            business_name, website_url, technical_status,
            reviews_snippet, pain_point, email_draft, phone, email
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            lead['business_name'], lead['website_url'], lead['technical_status'],
            lead['reviews_snippet'], lead['pain_point'], lead['email_draft'],
            lead['phone'], lead['email']
        )
        cursor.execute(insert_query, values)
        conn.commit()
    except Exception as e:
        print(f"Error saving lead: {e}")
                


if __name__ == "__main__":
    main()
