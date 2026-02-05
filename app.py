import streamlit as st
import pydicom
import numpy as np
import matplotlib.pyplot as plt
import zipfile
import plotly.graph_objects as go
from io import BytesIO
from collections import Counter
from skimage import measure

# --- Configuração da Página ---
st.set_page_config( 
    page_title="Visualizador 3D",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .slice-header-axial { color: #FF4A4A !important; border-bottom: 2px solid #FF4A4A; }
    .slice-header-sagittal { color: #F1C40F !important; border-bottom: 2px solid #F1C40F; }
    .slice-header-coronal { color: #2ECC71 !important; border-bottom: 2px solid #2ECC71; }
    .stButton > button { background-color: #126D83; color: white; border: none; width: 100%; }
    .stButton > button:hover { background-color: #1EB3B2; color: black; }
    .stAlert { color: white; }
    </style>
""", unsafe_allow_html=True)

# --- Funções Core ---
# --- Funções Core ---
@st.cache_data
def load_dicom_from_zip(zip_file):
    dicom_candidates = []
    
    # Abre o ZIP
    with zipfile.ZipFile(zip_file) as z:
        # Percorre TODOS os arquivos, não importa em que pasta estejam
        for filename in z.namelist():
            # Ignora pastas (que terminam com /) e arquivos de sistema
            if filename.endswith('/') or "__MACOSX" in filename:
                continue
                
            # Verifica se pode ser um DICOM (extensão .dcm ou sem extensão)
            # Muitos arquivos DICOM vêm sem extensão .dcm, apenas um código numérico
            try:
                with z.open(filename) as f:
                    # Tenta ler com pydicom. Se não for DICOM, ele vai dar erro e pular
                    dcm = pydicom.dcmread(BytesIO(f.read()), force=True)
                    
                    # Verifica se tem dados de pixel (imagem) e posição espacial
                    if hasattr(dcm, "pixel_array") and hasattr(dcm, "ImagePositionPatient"):
                        dicom_candidates.append(dcm)
            except:
                # Se der erro ao ler (não é DICOM), apenas continua para o próximo
                continue

    if not dicom_candidates: 
        print("Nenhum DICOM válido encontrado.")
        return None, None

    # Filtro de Consistência (Mantém apenas o tamanho de imagem mais comum)
    shapes = [d.pixel_array.shape for d in dicom_candidates]
    if not shapes: return None, None
    
    most_common_shape = Counter(shapes).most_common(1)[0][0]
    valid_dicoms = [d for d in dicom_candidates if d.pixel_array.shape == most_common_shape]
    
    # Ordenação Espacial (Essencial para o 3D funcionar)
    valid_dicoms.sort(key=lambda x: float(x.ImagePositionPatient[2]))
    
    # Empilha tudo num volume 3D
    volume = np.stack([d.pixel_array for d in valid_dicoms])
    
    return volume, valid_dicoms[0]

def normalize_image(image, brightness, contrast):
    img_norm = np.clip(image, brightness, contrast)
    return img_norm

def generate_mesh_3d(volume, threshold, step_size=2):
    """
    Gera malha 3D usando Marching Cubes.
    """
    # 1. Algoritmo Marching Cubes
    verts, faces, normals, values = measure.marching_cubes(volume, level=threshold, step_size=step_size)
    
    # 2. Criar objeto Mesh3d (CORRIGIDO: 'd' minúsculo)
    mesh = go.Mesh3d(
        x=verts[:, 2], 
        y=verts[:, 1],
        z=verts[:, 0],
        i=faces[:, 0],
        j=faces[:, 1],
        k=faces[:, 2],
        opacity=1.0,
        color='#1EB3B2',
        flatshading=True,
        lighting=dict(ambient=0.4, diffuse=0.5, roughness=0.1, specular=0.4, fresnel=0.2)
    )
    
    fig = go.Figure(data=[mesh])
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
            bgcolor='black'
        ),
        paper_bgcolor="black",
        margin=dict(l=0, r=0, b=0, t=0),
        height=600
    )
    return fig

# --- Sidebar ---
with st.sidebar:
    st.title("Visualizador 3D")
    st.markdown("---")
    
    with st.expander("Dados", expanded=True):
        uploaded_file = st.file_uploader("Carregar ZIP", type=['zip'])

    with st.expander("Controles 2D", expanded=False):
        contrast = st.slider("Max", 0, 3000, 1500)
        brightness = st.slider("Min", -1000, 1000, -200)

    with st.expander("Controles 3D", expanded=True):
        st.write("Geração de Malha")
        threshold = st.slider("Limiar de Densidade", -500, 1000, 300)
        
        quality = st.selectbox("Resolução da Malha", ["Baixa (Rápido)", "Média", "Alta"], index=0)
        
        if quality == "Baixa (Rápido)": step = 8
        elif quality == "Média": step = 5
        else: step = 2

# --- Main Area ---
st.title("Estação de Visualização")

if uploaded_file:
    with st.spinner("Lendo DICOM Gigante..."):
        volume, first_slice = load_dicom_from_zip(uploaded_file)

    if volume is not None:
        tab_3d, tab_2d = st.tabs(["Modelo 3D (Malha)", "Cortes 2D (MPR)"])

        # --- ABA 3D ---
        with tab_3d:
            st.markdown("### Modelo de Superfície (Marching Cubes)")
            st.caption(f"Fatias: {volume.shape[0]} | Passo: {step}")
            
            if st.button("Gerar Malha 3D"):
                with st.spinner("Calculando geometria..."):
                    try:
                        fig_3d = generate_mesh_3d(volume, threshold, step_size=step)
                        st.plotly_chart(fig_3d, width="stretch")
                    except Exception as e:
                        st.error(f"Erro: {e}.")

        # --- ABA 2D ---
        with tab_2d:
            z_size, y_size, x_size = volume.shape
            c1, c2, c3 = st.columns(3)
            with c1: z_idx = st.slider("Z (Axial)", 0, z_size-1, z_size//2)
            with c2: y_idx = st.slider("Y (Coronal)", 0, y_size-1, y_size//2)
            with c3: x_idx = st.slider("X (Sagital)", 0, x_size-1, x_size//2)

            col1, col2, col3 = st.columns(3)
            with col1:
                img = normalize_image(volume[z_idx, :, :], brightness, contrast)
                fig, ax = plt.subplots()
                ax.imshow(img, cmap='gray')
                ax.axis('off')
                fig.patch.set_facecolor('black')
                st.pyplot(fig)
            with col2:
                img = normalize_image(np.flipud(volume[:, :, x_idx]), brightness, contrast)
                fig, ax = plt.subplots()
                ax.imshow(img, cmap='gray', aspect='auto')
                ax.axis('off')
                fig.patch.set_facecolor('black')
                st.pyplot(fig)
            with col3:
                img = normalize_image(np.flipud(volume[:, y_idx, :]), brightness, contrast)
                fig, ax = plt.subplots()
                ax.imshow(img, cmap='gray', aspect='auto')
                ax.axis('off')
                fig.patch.set_facecolor('black')
                st.pyplot(fig)
    else:
        st.error("Erro ao ler dados.")
else:
    st.container()
    st.markdown("""
        <div style='background-color: #101010; padding: 50px; text-align: center; border: 1px dashed #126D83;'>
            <h2 style='color: #1EB3B2;'>Bem-vindo ao Visualizador 3D</h2>
            <p style='color: #7FF9C6;'>Carregue um arquivo ZIP contendo uma série DICOM para iniciar.</p>
        </div>
    """, unsafe_allow_html=True)