from qgis.core import (
    QgsProject,
    QgsColorRampShader,
    QgsRasterShader,
    QgsSingleBandPseudoColorRenderer
)
from PyQt5.QtGui import QColor

# Faixa de temperatura ajustada para a região (Cerrado, Tmin)
min_temp = 15.0
max_temp = 25.0

# Cores inspiradas na paleta cpt-city "temperature" com 6 pontos
cores_temperature = [
    (15.0, QColor("#0000ff")),   # azul escuro
    (17.0, QColor("#007fff")),   # azul médio
    (19.0, QColor("#00ffff")),   # ciano
    (21.0, QColor("#ffff00")),   # amarelo
    (23.0, QColor("#ff7f00")),   # laranja
    (25.0, QColor("#ff0000"))    # vermelho
]

# Aplicar simbologia a todas as camadas raster
for layer in QgsProject.instance().mapLayers().values():
    if layer.type() == layer.RasterLayer:
        print(f"🎨 Estilizando: {layer.name()}")

        # Criar shader com interpolação contínua
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

        print(f"✅ Estilo contínuo aplicado a: {layer.name()}")

print("🎯 Todas as camadas raster foram estilizadas com gradiente contínuo de 15–25 °C.")
