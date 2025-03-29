import os
from qgis.core import (
    QgsProject,
    QgsProcessingFeedback,
    QgsRasterLayer
)
import qgis.utils
import processing

# Permite ao usuário selecionar manualmente uma camada raster no QGIS
raster_layer = qgis.utils.iface.activeLayer()

# Verifica se a camada selecionada é um raster
if raster_layer is None or not isinstance(raster_layer, QgsRasterLayer):
    print("Erro: Nenhuma camada raster válida selecionada. Selecione uma camada raster no painel de camadas do QGIS e tente novamente.")
else:
    print(f"Raster selecionado: {raster_layer.name()}")

    # Extrai o nome do arquivo raster sem extensão
    raster_source = raster_layer.source()
    raster_filename = os.path.basename(raster_source)  # Nome do arquivo com extensão
    raster_name_without_ext = os.path.splitext(raster_filename)[0]  # Remove a extensão

    # Define o caminho de saída com o novo nome
    output_directory = "E:/Mudanças Climáticas/Nova geografia da produção de hortaliças/Imagens Raster BR/Vulnerabilidade"
    os.makedirs(output_directory, exist_ok=True)  # Garante que o diretório exista

    output_filename = f"{raster_name_without_ext}_vulnerabilidade_Tmax.tif"
    output_path = os.path.join(output_directory, output_filename)

    # Formata o nome da camada raster corretamente para a Calculadora Raster
    raster_calc_name = f'"{raster_layer.name()}@1"'  # Agora faz referência à banda 1 do raster

    # Expressão correta para a reclassificação com os novos critérios
    expression = (
        f"(({raster_calc_name} >= 0.0001 AND {raster_calc_name} <= 25.0000) * 1) + "
        f"(({raster_calc_name} > 25.0000 AND {raster_calc_name} <= 30.0000) * 2) + "
        f"(({raster_calc_name} > 30.0000 AND {raster_calc_name} <= 35.0000) * 3) + "
        f"(({raster_calc_name} > 35.0000 AND {raster_calc_name} <= 60.0000) * 4)"
    )

    # Configuração dos parâmetros do processamento
    params = {
        'EXPRESSION': expression,
        'LAYERS': raster_layer,
        'CELLSIZE': 0,
        'EXTENT': raster_layer.extent(),
        'CRS': raster_layer.crs(),
        'OUTPUT': output_path
    }

    # Execução do processamento no QGIS
    try:
        feedback = QgsProcessingFeedback()
        result = processing.run("qgis:rastercalculator", params, feedback=feedback)
        if result and 'OUTPUT' in result:
            output_layer = QgsRasterLayer(output_path, f"{raster_name_without_ext}_vulnerabilidade_Tmax")
            QgsProject.instance().addMapLayer(output_layer)
            print(f"Processo concluído com sucesso! O raster reclassificado foi salvo como: {output_filename}")
            print("Arquivo carregado no QGIS automaticamente.")
        else:
            print("Erro: O processamento não retornou saída válida.")
    except Exception as e:
        print(f"Erro no processamento: {str(e)}")
