from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsProcessingFeedback,
    QgsField,
    QgsExpression,
    QgsFeature,
    QgsExpressionContext,
    QgsExpressionContextUtils
)
from PyQt5.QtCore import QVariant
import processing
import os

# Definir a pasta de saída para os resultados
output_folder = "E:/Artigo vulnerabilidade alface/Estatísticas/Vulnerabilidade/Tmin"

# Garantir que o diretório existe
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Obter todas as camadas raster carregadas no QGIS
raster_layers = [layer for layer in QgsProject.instance().mapLayers().values() if isinstance(layer, QgsRasterLayer)]

if not raster_layers:
    print("Nenhuma camada raster encontrada no projeto.")
else:
    for raster_layer in raster_layers:
        raster_filename = os.path.splitext(os.path.basename(raster_layer.source()))[0]  # Nome do raster sem extensão
        
        print(f"Processando a camada raster: {raster_filename}")

        # Definir caminho de saída para o shapefile vetorial e arquivo .txt
        output_vector = os.path.join(output_folder, f"{raster_filename}.shp")
        output_txt = os.path.join(output_folder, f"{raster_filename}_estatisticas.txt")

        # Executar a vetorização com GDAL
        params = {
            'INPUT': raster_layer.source(),
            'BAND': 1,
            'FIELD': 'DN',
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'OUTPUT': output_vector
        }

        feedback = QgsProcessingFeedback()
        processing.run("gdal:polygonize", params, feedback=feedback)

        # Adicionar a camada vetorizada ao projeto
        vector_layer = QgsVectorLayer(output_vector, raster_filename, "ogr")

        if vector_layer.isValid():
            QgsProject.instance().addMapLayer(vector_layer)
            print(f"Conversão concluída. Camada vetorial '{raster_filename}' adicionada ao projeto.")

            # --- Calcular área e porcentagem ---

            classification_field = "DN"

            # Iniciar edição para adicionar campo de área se não existir
            vector_layer.startEditing()
            if "area_calc" not in [field.name() for field in vector_layer.fields()]:
                vector_layer.addAttribute(QgsField("area_calc", QVariant.Double))

            # Criar expressão para calcular área
            expression = QgsExpression("$area")
            context = QgsExpressionContext()
            context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(vector_layer))

            # Calcular e salvar área de cada feição
            for feature in vector_layer.getFeatures():
                context.setFeature(feature)
                feature["area_calc"] = expression.evaluate(context)
                vector_layer.updateFeature(feature)

            vector_layer.commitChanges()  # Salvar mudanças

            # Criar dicionário para armazenar áreas por classe
            area_by_class = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            total_area = 0

            # Calcular soma das áreas por classe
            for feature in vector_layer.getFeatures():
                class_value = feature[classification_field]
                area_value = feature["area_calc"]
                total_area += area_value

                if class_value in area_by_class:
                    area_by_class[class_value] += area_value

            # Criar e salvar resultados no arquivo .txt
            with open(output_txt, "w", encoding="utf-8") as file:
                file.write("Classe\tÁrea (m²)\tPorcentagem (%)\n")
                file.write("=" * 40 + "\n")

                for class_value, area_value in area_by_class.items():
                    percentage = (area_value / total_area) * 100 if total_area > 0 else 0
                    file.write(f"{class_value}\t{area_value:.2f}\t{percentage:.2f}\n")

            print(f"Estatísticas salvas em: {output_txt}")

        else:
            print(f"Falha na conversão da camada raster: {raster_filename}")



