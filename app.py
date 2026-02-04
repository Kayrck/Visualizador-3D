import streamlit as st
import pydicom
import numpy as np
import matplotlib.pyplot as plt
import zipfile
from io import BytesIO

# Configuração da Página
st.set_page_config( 
    page_title="Visualizador 3D",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Personalizado ---
st.markdown("""
    <style>
    .stButton > button {
        background-color: #126D83;
        color: white;
        border: none;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #1EB3B2;
        color: black;
    }
    h1, h2, h3 {
        color: #1EB3B2 !important;
    }
    .stPlotlyChart {
        background-color: #000000;
    }
    </style>
""", unsafe_allow_html=True)

# --- Função Robusta para Ler o ZIP ---
@st.cache_data
def load_dicom_from_zip(zip_file):
    dicom_files = []
    
    with zipfile.ZipFile(zip_file) as z:
        for filename in z.namelist():
            # Ignora pastas ou arquivos ocultos
            if not filename.endswith('.dcm') and "." in filename:
                continue
            
            try:
                with z.open(filename) as f:
                    dcm = pydicom.dcmread(BytesIO(f.read()))
                    
                    # --- O FILTRO MÁGICO ---
                    # Só aceitamos se tiver 'PixelData' (imagem) e 'ImagePositionPatient' (posição 3D)
                    # Isso elimina o arquivo DICOMDIR e relatórios que causam o erro
                    if hasattr(dcm, "pixel_array") and hasattr(dcm, "ImagePositionPatient") and hasattr(dcm, "Rows"):
                        dicom_files.append(dcm)
            except Exception:
                continue # Se der erro num arquivo específico, pula para o próximo

    # Ordenar espacialmente (Cabeça -> Pés)
    # Agora é seguro fazer isso pois filtramos os arquivos ruins acima
    if dicom_files:
        dicom_files.sort(key=lambda x: float(x.ImagePositionPatient[2]))
    
    return dicom_files

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    st.title("Visualizador 3D")
    st.markdown("---")
    
    st.header("Controles")
    uploaded_file = st.file_uploader("Carregar ZIP com DICOMs", type=['zip'])
    
    st.markdown("---")
    st.header("Segmentação")
    
    if st.button("Segmentar Próstata"):
        st.toast("Iniciando segmentação da Próstata...", icon="🔵")
    if st.button("Segmentar Rins"):
        st.toast("Iniciando segmentação dos Rins...", icon="🟢")
    if st.button("Segmentar Fígado"):
        st.toast("Iniciando segmentação do Fígado...", icon="🟤")

# --- Área Principal ---
st.title("Visualizador 3D")

if uploaded_file is not None:
    with st.spinner("Processando volume (pode demorar alguns segundos)..."):
        slices = load_dicom_from_zip(uploaded_file)
    
    if len(slices) > 0:
        first_slice = slices[0]
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Metadados")
            # Usa .get para evitar erros se o campo estiver vazio
            st.info(f"Paciente: {first_slice.get('PatientName', 'Anônimo')}")
            st.info(f"Fatias Carregadas: {len(slices)}")
            
            # Aqui estava o erro antes. Agora é seguro.
            st.info(f"Dimensões: {first_slice.Rows} x {first_slice.Columns}")

            st.subheader("Navegação")
            slice_index = st.slider("Fatia (Z-Axis)", 0, len(slices)-1, len(slices)//2)
            
            st.markdown("---")
            contrast = st.slider("Contraste (Max)", 0, 3000, 1500) # Aumentei o range para TC
            brightness = st.slider("Brilho (Min)", -1000, 1000, -200)

        with col2:
            st.subheader(f"Corte Axial - {slice_index}")
            
            # Recuperar array da imagem
            selected_slice = slices[slice_index].pixel_array
            
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.imshow(selected_slice, cmap='gray', vmin=brightness, vmax=contrast)
            ax.axis('off')
            
            fig.patch.set_facecolor('#000000')
            ax.set_facecolor('#000000')
            
            st.pyplot(fig)
            
    else:
        st.warning("O ZIP foi lido, mas não foram encontradas imagens válidas com dados 3D.")
        st.info("Verifique se o ZIP contém arquivos .dcm com ImagePositionPatient.")

else:
    st.container()
    st.write("⬅️ Por favor, carregue um arquivo .zip contendo a pasta DICOM.")
    st.markdown("""
        <div style='background-color: #101010; padding: 50px; text-align: center; border-radius: 10px; border: 1px dashed #126D83;'>
            <p style='color: #7FF9C6;'>A aguardar arquivo ZIP...</p>
        </div>
    """, unsafe_allow_html=True)