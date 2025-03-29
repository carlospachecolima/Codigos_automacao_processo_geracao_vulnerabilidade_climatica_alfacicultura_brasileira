import os
from qgis.core import (
    QgsProject,
    QgsProcessingFeedback,
    QgsRasterLayer,
    QgsVectorLayer
)
import processing

# Obtém todas as camadas carregadas no QGIS
project = QgsProject.instance()
layers = list(project.mapLayers().values())

# Identifica a primeira camada raster no projeto
raster_layer = next((layer for layer in layers if isinstance(layer, QgsRasterLayer)), None)

# Identifica a primeira camada vetor (shapefile) no projeto
vector_layer = next((layer for layer in layers if isinstance(layer, QgsVectorLayer)), None)

# Verifica se encontrou as camadas necessárias
if not raster_layer:
    print("Erro: Nenhuma camada raster encontrada no projeto.")
elif not vector_layer:
    print("Erro: Nenhuma camada shapefile encontrada no projeto.")
else:
    print(f"Raster encontrado: {raster_layer.name()}")
    print(f"Shapefile encontrado: {vector_layer.name()}")

    # Define caminho de saída para o arquivo recortado
    output_path = "E:/Mudanças Climáticas/Nova geografia da produção de hortaliças/Imagens Raster BR/raster_recortado.tif"

    # Configuração dos parâmetros do processamento
    params = {
        'INPUT': raster_layer,  # Camada raster de entrada
        'MASK': vector_layer,  # Camada de máscara (limites do Brasil)
        'TARGET_EXTENT': vector_layer.extent(),  # Define a extensão do shapefile como referência
        'NODATA': 10000000,  # Define valor NoData
        'DATA_TYPE': 0,  # Mantém o mesmo tipo de dados da entrada
        'ALPHA_BAND': False,  # Sem banda alfa
        'CROP_TO_CUTLINE': True,  # Recorta pela máscara
        'KEEP_RESOLUTION': True,  # Mantém a resolução do raster original
        'OUTPUT': output_path  # Caminho do arquivo de saída
    }

    # Execução do processamento no QGIS
    try:
        feedback = QgsProcessingFeedback()
        result = processing.runAndLoadResults("gdal:cliprasterbymasklayer", params, feedback=feedback)
        print("Processo concluído com sucesso! O raster recortado foi salvo e carregado no QGIS.")
    except Exception as e:
        print(f"Erro no processamento: {str(e)}")
