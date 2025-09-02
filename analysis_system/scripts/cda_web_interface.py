import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from discourse_analyzer import CriticalDiscourseAnalyzer

def create_power_visualization(power_data):
    """Create a radar chart for power analysis dimensions."""
    categories = ['Authority Markers', 'Expertise Claims', 'Imperatives', 'Hedging (Inverse)']
    values = [
        power_data['authority_markers'],
        power_data['expertise_claims'], 
        power_data['imperatives'],
        max(0, 5 - power_data['hedging_patterns'])  # Inverse hedging for visualization
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Power Indicators'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(max(values), 5)]
            )),
        showlegend=True,
        title="Power Asymmetry Analysis"
    )
    
    return fig

def create_ideology_chart(ideology_data):
    """Create a bar chart for ideological positioning."""
    ideologies = ['Individualism', 'Collectivism', 'Neoliberal', 'Social Democratic']
    scores = [
        ideology_data['individualism_score'],
        ideology_data['collectivism_score'],
        ideology_data['neoliberal_score'],
        ideology_data['social_democratic_score']
    ]
    
    fig = px.bar(
        x=ideologies, 
        y=scores,
        title="Ideological Positioning Analysis",
        labels={'x': 'Ideological Framework', 'y': 'Score'},
        color=scores,
        color_continuous_scale='viridis'
    )
    
    return fig

def main():
    st.set_page_config(
        page_title="Critical Discourse Analysis Tool",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("🔍 Critical Discourse Analysis Tool")
    st.markdown("*Analyze texts for power relations, ideological positioning, and social representations*")
    
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = CriticalDiscourseAnalyzer()
    
    # Sidebar for instructions
    with st.sidebar:
        st.header("📋 Instructions")
        st.markdown("""
        1. **Enter your text** in the main text area
        2. **Click 'Analyze Text'** to run the analysis
        3. **Explore results** across different analytical dimensions
        4. **Download results** as needed for further analysis
        
        ### What this tool analyzes:
        - **Power Relations**: Authority markers, expertise claims, hedging patterns
        - **Ideological Positioning**: Political and economic discourse markers
        - **Social Representation**: How different groups are portrayed
        - **Hegemonic Discourse**: Naturalization and common-sense appeals
        """)
        
        st.header("⚠️ Important Notes")
        st.markdown("""
        - This tool provides **computational assistance** for CDA, not definitive interpretations
        - Results should be **validated by human experts**
        - Context and cultural knowledge are crucial for proper analysis
        - Consider multiple interpretations of the same text
        """)
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Text Input")
        text_input = st.text_area(
            "Enter the text you want to analyze:",
            height=300,
            placeholder="Paste your text here for Critical Discourse Analysis..."
        )
        
        analyze_button = st.button("🔍 Analyze Text", type="primary")
    
    with col2:
        st.header("📊 Quick Stats")
        if text_input:
            word_count = len(text_input.split())
            char_count = len(text_input)
            sentence_count = len([s for s in text_input.split('.') if s.strip()])
            
            st.metric("Word Count", word_count)
            st.metric("Character Count", char_count)
            st.metric("Estimated Sentences", sentence_count)
    
    # Analysis results
    if analyze_button and text_input:
        with st.spinner("Performing Critical Discourse Analysis..."):
            results = st.session_state.analyzer.comprehensive_analysis(text_input)
        
        st.success("Analysis Complete!")
        
        # Create tabs for different analysis dimensions
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", 
            "⚡ Power Analysis", 
            "🎯 Ideological Analysis", 
            "👥 Social Representation", 
            "🏛️ Hegemonic Discourse"
        ])
        
        with tab1:
            st.header("Analysis Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Power Score", 
                    f"{results['power_analysis']['power_score']:.2f}",
                    help="Higher scores indicate more authoritative/powerful discourse"
                )
            
            with col2:
                st.metric(
                    "Dominant Ideology", 
                    results['ideological_analysis']['dominant_ideology'].title(),
                    help="Most prominent ideological framework detected"
                )
            
            with col3:
                st.metric(
                    "Social Group References", 
                    results['social_representation']['marginalized_references'] + 
                    results['social_representation']['dominant_references'],
                    help="Total references to social groups"
                )
            
            with col4:
                st.metric(
                    "Hegemonic Markers", 
                    results['hegemonic_discourse']['naturalization_markers'] + 
                    results['hegemonic_discourse']['common_sense_appeals'],
                    help="Indicators of dominant discourse reproduction"
                )
        
        with tab2:
            st.header("Power Relations Analysis")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig_power = create_power_visualization(results['power_analysis'])
                st.plotly_chart(fig_power, use_container_width=True)
            
            with col2:
                st.subheader("Power Indicators")
                power_data = results['power_analysis']
                
                st.metric("Authority Markers", power_data['authority_markers'])
                st.metric("Expertise Claims", power_data['expertise_claims'])
                st.metric("Imperatives", power_data['imperatives'])
                st.metric("Hedging Patterns", power_data['hedging_patterns'])
            
            if results['power_analysis']['detailed_analysis']:
                st.subheader("Detailed Findings")
                for finding in results['power_analysis']['detailed_analysis']:
                    st.write(f"• {finding}")
        
        with tab3:
            st.header("Ideological Positioning Analysis")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig_ideology = create_ideology_chart(results['ideological_analysis'])
                st.plotly_chart(fig_ideology, use_container_width=True)
            
            with col2:
                st.subheader("Ideological Scores")
                ideology_data = results['ideological_analysis']
                
                st.metric("Individualism", ideology_data['individualism_score'])
                st.metric("Collectivism", ideology_data['collectivism_score'])
                st.metric("Neoliberal", ideology_data['neoliberal_score'])
                st.metric("Social Democratic", ideology_data['social_democratic_score'])
            
            if results['ideological_analysis']['detailed_analysis']:
                st.subheader("Detailed Findings")
                for finding in results['ideological_analysis']['detailed_analysis']:
                    st.write(f"• {finding}")
        
        with tab4:
            st.header("Social Group Representation")
            
            social_data = results['social_representation']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Group References")
                st.metric("Marginalized Groups", social_data['marginalized_references'])
                st.metric("Dominant Groups", social_data['dominant_references'])
            
            with col2:
                st.subheader("Characterization")
                st.metric("Positive Terms", social_data['positive_characterization'])
                st.metric("Negative Terms", social_data['negative_characterization'])
            
            if social_data['agency_patterns']:
                st.subheader("Agency Patterns")
                for pattern in social_data['agency_patterns']:
                    st.write(f"• {pattern}")
            
            if results['social_representation']['detailed_analysis']:
                st.subheader("Detailed Findings")
                for finding in results['social_representation']['detailed_analysis']:
                    st.write(f"• {finding}")
        
        with tab5:
            st.header("Hegemonic Discourse Analysis")
            
            hegemonic_data = results['hegemonic_discourse']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Dominance Markers")
                st.metric("Naturalization", hegemonic_data['naturalization_markers'])
                st.metric("Common Sense Appeals", hegemonic_data['common_sense_appeals'])
                st.metric("Status Quo Legitimation", hegemonic_data['status_quo_legitimation'])
            
            with col2:
                st.subheader("Counter-Discourse")
                st.metric("Resistance Markers", hegemonic_data['resistance_markers'])
                
                # Calculate hegemonic dominance ratio
                dominance_total = (hegemonic_data['naturalization_markers'] + 
                                 hegemonic_data['common_sense_appeals'] + 
                                 hegemonic_data['status_quo_legitimation'])
                resistance_total = hegemonic_data['resistance_markers']
                
                if resistance_total > 0:
                    dominance_ratio = dominance_total / resistance_total
                    st.metric("Dominance/Resistance Ratio", f"{dominance_ratio:.2f}")
                else:
                    st.metric("Dominance/Resistance Ratio", "∞ (No resistance)")
            
            if results['hegemonic_discourse']['detailed_analysis']:
                st.subheader("Detailed Findings")
                for finding in results['hegemonic_discourse']['detailed_analysis']:
                    st.write(f"• {finding}")
        
        # Download results
        st.header("📥 Export Results")
        
        # Convert results to downloadable format
        results_df = pd.DataFrame([{
            'Metric': 'Power Score',
            'Value': results['power_analysis']['power_score'],
            'Category': 'Power Analysis'
        }, {
            'Metric': 'Dominant Ideology',
            'Value': results['ideological_analysis']['dominant_ideology'],
            'Category': 'Ideological Analysis'
        }, {
            'Metric': 'Authority Markers',
            'Value': results['power_analysis']['authority_markers'],
            'Category': 'Power Analysis'
        }, {
            'Metric': 'Marginalized Group References',
            'Value': results['social_representation']['marginalized_references'],
            'Category': 'Social Representation'
        }])
        
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="📊 Download Analysis Results (CSV)",
            data=csv,
            file_name="cda_analysis_results.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
