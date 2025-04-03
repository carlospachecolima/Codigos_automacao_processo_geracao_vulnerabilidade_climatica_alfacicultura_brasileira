from qgis.core import QgsProject

# Lista dos meses abreviados
meses_abrev = [
    "jan", "fev", "mar", "abr", "mai", "jun",
    "jul", "ago", "set", "out", "nov", "dez"
]

# Renomear camadas com nome igual a mês para o padrão desejado
for layer in QgsProject.instance().mapLayers().values():
    if layer.type() != layer.RasterLayer:
        continue

    nome_original = layer.name().strip().lower()

    if nome_original in meses_abrev:
        novo_nome = f"Temperatura máxima (ºC)_{nome_original}"
        layer.setName(novo_nome)
        print(f"🔄 Camada renomeada: {nome_original} → {novo_nome}")
    else:
        print(f"⏭️ Camada ignorada: {nome_original}")
