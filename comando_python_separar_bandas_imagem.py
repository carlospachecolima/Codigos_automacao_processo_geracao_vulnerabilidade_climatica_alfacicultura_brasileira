import os
import processing
from qgis.core import QgsRasterLayer, QgsProject

# Caminho de saída
output_folder = r"E:/Projeto GeoBSF/Access/Tmin/2021 a 2040/SSP245"

# Lista com os nomes dos meses
nomes_meses = ["jan", "fev", "mar", "abr", "mai", "jun", 
               "jul", "ago", "set", "out", "nov", "dez"]

# Obter a primeira camada raster do projeto
camada = None
for layer in QgsProject.instance().mapLayers().values():
    if layer.type() == layer.RasterLayer:
        camada = layer
        break

if camada is None:
    raise Exception("❌ Nenhuma camada raster encontrada no projeto.")

# Verificar número de bandas
num_bandas = camada.bandCount()
if num_bandas != 12:
    raise Exception(f"❌ A camada selecionada tem {num_bandas} bandas, mas são esperadas 12.")

# Criar pasta de saída se não existir
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

print(f"✅ Camada selecionada: {camada.name()}")
print(f"Exportando bandas individuais para: {output_folder}")

# Exportar cada banda individualmente com -b no GDAL
for i in range(1, num_bandas + 1):
    nome_banda = nomes_meses[i - 1]
    output_path = os.path.join(output_folder, f"{nome_banda}.tif")

    processing.run("gdal:translate", {
        'INPUT': camada,
        'OUTPUT': output_path,
        'EXTRA': f"-b {i}"  # extrai apenas a banda i
    })

    # Carregar no QGIS
    banda_layer = QgsRasterLayer(output_path, f"Tmin_{nome_banda}")
    if banda_layer.isValid():
        QgsProject.instance().addMapLayer(banda_layer)
        print(f"📤 Banda {i} ({nome_banda}) salva e carregada.")
    else:
        print(f"⚠️ Erro ao carregar {nome_banda}.tif")

print("✅ Exportação finalizada. Cada arquivo contém apenas uma banda correspondente ao mês.")
