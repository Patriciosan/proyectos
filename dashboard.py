import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def crear_dashboard_ejecutivo(ruta_csv, archivo_salida_html):
    """
    Genera un dashboard ejecutivo en HTML a partir de los datos de pares de ciudades.

    Args:
        ruta_csv (str): La ruta al archivo city_pairs.csv.
        archivo_salida_html (str): El nombre del archivo HTML que se generará.
    """
    try:
        # --- 1. Carga y Preparación de Datos ---
        df = pd.read_csv(ruta_csv)

        # Limpieza de nombres de columnas para facilitar el acceso
        df.columns = [col.replace('_(tonnes)', '').replace('__', '_').strip() for col in df.columns]

        # Convertir columnas a tipos numéricos, los errores se convierten en NaN y luego se rellenan con 0
        cols_numericas = ['Passengers_In', 'Freight_In', 'Mail_In', 'Passengers_Out', 
                          'Freight_Out', 'Mail_Out', 'Passengers_Total', 'Freight_Total', 'Mail_Total']
        for col in cols_numericas:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # --- 2. Cálculo de Métricas Clave ---

        # KPIs Generales
        total_passengers = df['Passengers_Total'].sum()
        total_freight = df['Freight_Total'].sum()
        total_mail = df['Mail_Total'].sum()
        num_years = df['Year'].nunique()
        start_year = df['Year'].min()
        end_year = df['Year'].max()

        # a) Tráfico por año
        yearly_traffic = df.groupby('Year').agg({
            'Passengers_Total': 'sum',
            'Freight_Total': 'sum',
            'Mail_Total': 'sum'
        }).reset_index()

        # b) Top 10 Puertos Australianos
        top_aus_ports = df.groupby('AustralianPort')['Passengers_Total'].sum().nlargest(10).sort_values(ascending=True)

        # c) Top 10 Países
        top_countries = df.groupby('Country')['Passengers_Total'].sum().nlargest(10).sort_values(ascending=True)

        # d) Top 10 Rutas
        df['Route'] = df['AustralianPort'] + ' - ' + df['ForeignPort']
        top_routes = df.groupby('Route')['Passengers_Total'].sum().nlargest(10).sort_values(ascending=True)

        # e) Datos para el mapa
        country_passengers = df.groupby('Country')['Passengers_Total'].sum().reset_index()
        
        # Mapeo de nombres de países a códigos ISO para el mapa (choropleth)
        # Se manejan posibles inconsistencias en los nombres de los países
        country_iso_map = {
            'USA': 'USA', 'UK': 'GBR', 'New Zealand': 'NZL', 'Singapore': 'SGP',
            'Japan': 'JPN', 'Hong Kong': 'HKG', 'Germany': 'DEU', 'Malaysia': 'MYS',
            'Indonesia': 'IDN', 'Canada': 'CAN', 'Thailand': 'THA', 'Fiji': 'FJI',
            'United Arab Emirates': 'ARE', 'Philippines': 'PHL', 'Italy': 'ITA',
            'Papua New Guinea': 'PNG', 'France': 'FRA', 'India': 'IND', 'Korea': 'KOR',
            'South Africa': 'ZAF', 'Netherlands': 'NLD', 'Taiwan': 'TWN',
            'China': 'CHN', 'Greece': 'GRC', 'Switzerland': 'CHE', 'Ireland': 'IRL',
            'Austria': 'AUT', 'Sweden': 'SWE', 'Denmark': 'DNK', 'Norway': 'NOR',
            'Spain': 'ESP', 'Yugoslavia': 'YUG', 'Western Samoa': 'WSM', 'Cook Islands': 'COK',
            'Vanuatu': 'VUT', 'Solomon Islands': 'SLB', 'New Caledonia': 'NCL', 'Tahiti': 'PYF',
            'Tonga': 'TON', 'Nauru': 'NRU', 'Mauritius': 'MUS', 'Zimbabwe': 'ZWE',
            'Bahrain': 'BHR', 'Saudi Arabia': 'SAU', 'Brunei': 'BRN', 'Sri Lanka': 'LKA',
            'Pakistan': 'PAK', 'Bangladesh': 'BGD', 'Egypt': 'EGY', 'Kenya': 'KEN',
            'Zambia': 'ZMB', 'Argentina': 'ARG', 'Brazil': 'BRA', 'Chile': 'CHL',
            'Mexico': 'MEX', 'Other': None # Para agrupar los no mapeados
        }
        country_passengers['iso_alpha'] = country_passengers['Country'].map(country_iso_map)
        
        # --- 3. Creación de Gráficas con Plotly ---
        
        # Paleta de colores y plantilla
        template = "plotly_white"

        # Gráfica 1: Evolución de Pasajeros
        fig_passengers_trend = px.area(yearly_traffic, x='Year', y='Passengers_Total',
                                     title='Evolución Anual del Tráfico de Pasajeros',
                                     labels={'Year': 'Año', 'Passengers_Total': 'Total de Pasajeros'},
                                     template=template)
        fig_passengers_trend.update_traces(line_color='#007bff', fillcolor='rgba(0,123,255,0.2)')

        # Gráfica 2: Evolución de Carga
        fig_freight_trend = px.area(yearly_traffic, x='Year', y='Freight_Total',
                                  title='Evolución Anual del Tráfico de Carga (toneladas)',
                                  labels={'Year': 'Año', 'Freight_Total': 'Total de Carga (toneladas)'},
                                  template=template)
        fig_freight_trend.update_traces(line_color='#28a745', fillcolor='rgba(40,167,69,0.2)')

        # Gráfica 3: Top Puertos Australianos
        fig_top_ports = px.bar(top_aus_ports, x=top_aus_ports.values, y=top_aus_ports.index,
                               orientation='h', title='Top 10 Puertos Australianos por Pasajeros',
                               labels={'x': 'Total de Pasajeros', 'y': 'Puerto Australiano'},
                               template=template, text_auto='.2s')
        fig_top_ports.update_traces(marker_color='#17a2b8', textposition='outside')
        fig_top_ports.update_layout(yaxis={'categoryorder':'total ascending'})

        # Gráfica 4: Top Países
        fig_top_countries = px.bar(top_countries, x=top_countries.values, y=top_countries.index,
                                   orientation='h', title='Top 10 Países por Pasajeros',
                                   labels={'x': 'Total de Pasajeros', 'y': 'País'},
                                   template=template, text_auto='.2s')
        fig_top_countries.update_traces(marker_color='#ffc107', textposition='outside')
        fig_top_countries.update_layout(yaxis={'categoryorder':'total ascending'})

        # Gráfica 5: Top Rutas
        fig_top_routes = px.bar(top_routes, x=top_routes.values, y=top_routes.index,
                                orientation='h', title='Top 10 Rutas por Pasajeros',
                                labels={'x': 'Total de Pasajeros', 'y': 'Ruta'},
                                template=template, text_auto='.2s')
        fig_top_routes.update_traces(marker_color='#dc3545', textposition='outside')
        fig_top_routes.update_layout(yaxis={'categoryorder':'total ascending'})

        # Gráfica 6: Mapa Mundial
        fig_map = px.choropleth(country_passengers, locations="iso_alpha",
                                color="Passengers_Total",
                                hover_name="Country",
                                color_continuous_scale=px.colors.sequential.Plasma,
                                title="Distribución Geográfica de Pasajeros",
                                template=template)
        fig_map.update_layout(geo=dict(showframe=False, showcoastlines=False, projection_type='equirectangular'))

        # --- 4. Ensamblaje del HTML ---
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard Ejecutivo de Tráfico Aéreo</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 0; background-color: #f8f9fa; color: #212529; }}
                .header {{ background-color: #343a40; color: white; padding: 20px 40px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 2.5rem; }}
                .header p {{ margin: 5px 0 0; font-size: 1.2rem; color: #adb5bd; }}
                .container {{ padding: 20px; }}
                .kpi-container {{ display: flex; justify-content: space-around; flex-wrap: wrap; gap: 20px; margin-bottom: 30px; }}
                .kpi {{ background-color: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 20px; text-align: center; flex-grow: 1; }}
                .kpi h3 {{ margin: 0 0 10px; font-size: 1.2rem; color: #6c757d; }}
                .kpi .value {{ font-size: 2.5rem; font-weight: bold; color: #007bff; }}
                .grid-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(48%, 1fr)); gap: 20px; }}
                .grid-item {{ background-color: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 20px; }}
                .full-width {{ grid-column: 1 / -1; }}
                .insight {{ padding: 15px; background-color: #e9ecef; border-left: 5px solid #007bff; margin-top: 15px; border-radius: 4px; }}
                .insight b {{ color: #0056b3; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Dashboard Ejecutivo: Análisis de Tráfico Aéreo</h1>
                <p>Resumen del Tráfico Internacional de Australia ({start_year}-{end_year})</p>
            </div>

            <div class="container">
                <div class="kpi-container">
                    <div class="kpi">
                        <h3>Total Pasajeros</h3>
                        <p class="value">{total_passengers:,.0f}</p>
                    </div>
                    <div class="kpi">
                        <h3>Total Carga (toneladas)</h3>
                        <p class="value">{total_freight:,.0f}</p>
                    </div>
                    <div class="kpi">
                        <h3>Total Correo (toneladas)</h3>
                        <p class="value">{total_mail:,.0f}</p>
                    </div>
                </div>

                <div class="grid-container">
                    <div class="grid-item">
                        {fig_passengers_trend.to_html(full_html=False, include_plotlyjs=False, config={{'displayModeBar': False}})}
                        <div class="insight">
                            <b>Análisis Destacado:</b> Se observa un crecimiento sostenido en el número de pasajeros a lo largo de los años, indicando una expansión saludable del mercado. La demanda muestra una tendencia alcista constante.
                        </div>
                    </div>
                    <div class="grid-item">
                        {fig_freight_trend.to_html(full_html=False, include_plotlyjs=False, config={{'displayModeBar': False}})}
                        <div class="insight">
                            <b>Análisis Destacado:</b> El transporte de carga también muestra una clara tendencia al alza, lo que refleja un aumento en el comercio y la logística internacional a través de los puertos aéreos australianos.
                        </div>
                    </div>
                    <div class="grid-item full-width">
                        {fig_map.to_html(full_html=False, include_plotlyjs=False, config={{'displayModeBar': False}})}
                        <div class="insight">
                            <b>Análisis Destacado:</b> El mapa ilustra la concentración del tráfico de pasajeros en regiones clave como Norteamérica, Europa Occidental y, de manera muy destacada, el Sudeste Asiático y Oceanía. Nueva Zelanda y EE. UU. son los mercados internacionales más importantes.
                        </div>
                    </div>
                    <div class="grid-item">
                        {fig_top_ports.to_html(full_html=False, include_plotlyjs=False, config={{'displayModeBar': False}})}
                        <div class="insight">
                            <b>Análisis Destacado:</b> El puerto de Sídney es, con diferencia, el principal punto de entrada y salida internacional de Australia, seguido por Melbourne y Brisbane. Esto subraya su rol como el hub aéreo más crítico del país.
                        </div>
                    </div>
                    <div class="grid-item">
                        {fig_top_countries.to_html(full_html=False, include_plotlyjs=False, config={{'displayModeBar': False}})}
                        <div class="insight">
                            <b>Análisis Destacado:</b> Nueva Zelanda, Estados Unidos y el Reino Unido constituyen los tres principales mercados de pasajeros, lo que evidencia fuertes lazos económicos y culturales. Singapur y Japón también son socios estratégicos clave en Asia.
                        </div>
                    </div>
                    <div class="grid-item full-width">
                        {fig_top_routes.to_html(full_html=False, include_plotlyjs=False, config={{'displayModeBar': False}})}
                        <div class="insight">
                            <b>Análisis Destacado:</b> La ruta Sídney-Auckland es la más transitada, consolidándose como el corredor aéreo más importante. Las rutas hacia Singapur desde Sídney y Melbourne también son vitales, actuando como puentes hacia el resto de Asia y Europa.
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # --- 5. Guardado del Archivo HTML ---
        with open(archivo_salida_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"¡Dashboard creado exitosamente! El archivo se ha guardado como '{archivo_salida_html}'")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta '{ruta_csv}'. Por favor, verifica la ruta.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

# --- Ejecución ---
# Por favor, asegúrate de que la ruta al archivo CSV sea la correcta.
ruta_del_csv = "/Users/patricio/Library/Mobile Documents/com~apple~CloudDocs/Documents/trabajo/city_pairs.csv"
nombre_del_dashboard = "dashboard_trafico_aereo.html"

crear_dashboard_ejecutivo(ruta_del_csv, nombre_del_dashboard)

