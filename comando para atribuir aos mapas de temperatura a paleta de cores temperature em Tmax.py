from qgis.core import (
    QgsProject,
    QgsColorRampShader,
    QgsRasterShader,
    QgsSingleBandPseudoColorRenderer
)
from PyQt5.QtGui import QColor

# Nova faixa de temperatura: 24 a 50 °C
min_temp = 24.0
max_temp = 50.0

# Graduação de 2 em 2 °C — 14 intervalos
cores_temperature = [
    (24.0, QColor("#0000ff")),  # Azul escuro
    (26.0, QColor("#005fff")),  # Azul médio
    (28.0, QColor("#00bfff")),  # Azul claro
    (30.0, QColor("#00ffff")),  # Ciano
    (32.0, QColor("#80ff80")),  # Verde claro
    (34.0, QColor("#ffff00")),  # Amarelo
    (36.0, QColor("#ffd000")),  # Amarelo queimado
    (38.0, QColor("#ffa000")),  # Laranja claro
    (40.0, QColor("#ff7f00")),  # Laranja
    (42.0, QColor("#ff4000")),  # Vermelho alaranjado
    (44.0, QColor("#ff0000")),  # Vermelho intenso
    (46.0, QColor("#d00000")),  # Vermelho escuro
    (48.0, QColor("#a00000")),  # Bordô
    (50.0, QColor("#800000"))   # Vinho/marrom escuro
]

# Aplicar simbologia a todas as camadas raster
for layer in QgsProject.instance().mapLayers().values():
    if layer.type() == layer.RasterLayer:
        print(f"🎨 Estilizando: {layer.name()}")

        # Criar gradiente com base nos valores
        shader_items = []
        for valor, cor in cores_temperature:
            shader_items.append(QgsColorRampShader.ColorRampItem(valor, cor, f"{valor:.1f} °C"))

        shader = QgsColorRampShader()
        shader.setColorRampType(QgsColorRampShader.Interpolated)
        shader.setColorRampItemList(shader_items)
        shader.setMinimumValue(min_temp)
        shader.setMaximumValue(max_temp)

        raster_shader = QgsRasterShader()
        raster_shader.setRasterShaderFunction(shader)

        renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, raster_shader)
        layer.setRenderer(renderer)
        layer.triggerRepaint()

        print(f"✅ Estilo aplicado com faixa 24–50 °C a: {layer.name()}")

print("🎯 Estilização concluída com graduação de 2 °C (24–50 °C) para Temperatura Máxima.")
