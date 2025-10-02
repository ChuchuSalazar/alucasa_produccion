import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Proceso Laminado", layout="wide")

def create_process_hierarchy():
    """Crea la estructura jerárquica del proceso con costos"""
    data = []
    
    # Nivel 1: Subsistemas
    subsistemas = [
        ('Laminado Aluminio', 'Colada', 'Fijo/Variable', 100000),
        ('Laminado Aluminio', 'Laminación', 'Variable', 150000),
        ('Laminado Aluminio', 'Acabado', 'Fijo', 80000),
        ('Laminado Aluminio', 'Empaque', 'Variable', 60000)
    ]
    
    # Nivel 2: Procesos por subsistema
    procesos = [
        # Colada
        ('Laminado Aluminio', 'Colada', 'Precalentado', 'Fijo', 35000),
        ('Laminado Aluminio', 'Colada', 'Horneado', 'Fijo', 45000),
        ('Laminado Aluminio', 'Colada', 'Gen. Bobinas', 'Variable', 20000),
        
        # Laminación
        ('Laminado Aluminio', 'Laminación', 'Lam. Gruesa', 'Variable', 78000),
        ('Laminado Aluminio', 'Laminación', 'Honeado', 'Variable', 24000),
        ('Laminado Aluminio', 'Laminación', 'Lam. Fina', 'Variable', 48000),
        
        # Acabado
        ('Laminado Aluminio', 'Acabado', 'Trat. Superficie', 'Fijo', 36000),
        ('Laminado Aluminio', 'Acabado', 'Control Calidad', 'Fijo', 44000),
        
        # Empaque
        ('Laminado Aluminio', 'Empaque', 'Corte/Medición', 'Variable', 17000),
        ('Laminado Aluminio', 'Empaque', 'Embalaje', 'Variable', 30000),
        ('Laminado Aluminio', 'Empaque', 'Etiquetado', 'Variable', 13000)
    ]
    
    # Nivel 3: Elementos del costo (para cada proceso)
    costos = []
    for sistema, subsistema, proceso, tipo, valor_total in procesos:
        # Distribuir en los 3 elementos del costo
        mo = valor_total * 0.40  # 40% Mano de Obra
        mp = valor_total * 0.35  # 35% Materia Prima
        cf = valor_total * 0.25  # 25% Carga Fabril
        
        costos.append((sistema, subsistema, proceso, 'Mano de Obra', mo))
        costos.append((sistema, subsistema, proceso, 'Materia Prima', mp))
        costos.append((sistema, subsistema, proceso, 'Carga Fabril', cf))
    
    # Crear DataFrame
    df_costos = pd.DataFrame(costos, columns=[
        'Sistema', 'Subsistema', 'Proceso', 'Elemento_Costo', 'Valor'
    ])
    
    return df_costos

def main():
    st.title("🏭 Proceso de Laminado de Aluminio")
    st.markdown("### Visualización Interactiva Multinivel - Haz clic en los segmentos")
    
    # Crear datos jerárquicos
    df = create_process_hierarchy()
    
    # Opciones de visualización
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown("### 📊 Opciones")
        nivel = st.radio(
            "Nivel de detalle:",
            ["Subsistemas", "Procesos", "Elementos de Costo"],
            index=2
        )
        
        mostrar_valores = st.checkbox("Mostrar valores", value=True)
        
        st.markdown("---")
        st.info("""
        **Instrucciones:**
        - Haz clic en cualquier segmento para expandir
        - Haz clic en el centro para retroceder
        - Pasa el mouse para ver detalles
        """)
    
    with col1:
        # Configurar path según el nivel seleccionado
        if nivel == "Subsistemas":
            path = ['Sistema', 'Subsistema']
        elif nivel == "Procesos":
            path = ['Sistema', 'Subsistema', 'Proceso']
        else:  # Elementos de Costo
            path = ['Sistema', 'Subsistema', 'Proceso', 'Elemento_Costo']
        
        # Crear gráfico Sunburst
        fig = px.sunburst(
            df,
            path=path,
            values='Valor',
            title=f"Proceso Productivo - Nivel: {nivel}",
            color='Elemento_Costo',
            color_discrete_map={
                'Mano de Obra': '#3498db',
                'Materia Prima': '#e74c3c',
                'Carga Fabril': '#2ecc71'
            },
            hover_data=['Valor']
        )
        
        fig.update_traces(
            textinfo='label+percent entry' if mostrar_valores else 'label',
            hovertemplate='<b>%{label}</b><br>Valor: $%{value:,.0f}<br>%{percentEntry}<extra></extra>'
        )
        
        fig.update_layout(
            height=700,
            margin=dict(t=50, l=0, r=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de resumen
    st.markdown("---")
    st.subheader("📋 Resumen por Subsistema")
    
    resumen = df.groupby(['Subsistema', 'Elemento_Costo'])['Valor'].sum().unstack(fill_value=0)
    resumen['Total'] = resumen.sum(axis=1)
    resumen.loc['TOTAL'] = resumen.sum()
    
    # Formatear como moneda
    st.dataframe(
        resumen.style.format('${:,.0f}'),
        use_container_width=True
    )
    
    # Clasificación de costos
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Clasificación de Costos")
        st.markdown("""
        - **Costos Fijos**: Colada (Precalentado, Horneado), Acabado
        - **Costos Variables**: Laminación, Empaque, Gen. Bobinas
        """)
    
    with col2:
        st.markdown("### 📊 Elementos del Costo")
        totales_elementos = df.groupby('Elemento_Costo')['Valor'].sum()
        
        for elemento, valor in totales_elementos.items():
            porcentaje = (valor / totales_elementos.sum()) * 100
            st.metric(elemento, f"${valor:,.0f}", f"{porcentaje:.1f}%")

if __name__ == "__main__":
    main()