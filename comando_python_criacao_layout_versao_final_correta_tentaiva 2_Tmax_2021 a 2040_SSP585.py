from qgis.core import (
    QgsProject, QgsLayoutItemLabel, QgsLayoutItemMap, QgsLayoutItemLegend,
    QgsPrintLayout, QgsLayoutExporter, QgsReadWriteContext, QgsLayoutItem
)
from qgis.PyQt.QtXml import QDomDocument
import os
import re

# Caminhos ajustados para SSP585 e Tmax
modelo_qpt = r"E:/Projeto GeoBSF/Access/Tmax/2021 a 2040/SSP245/Modelo Tmax BSF.qpt"
saida = r"E:/Projeto GeoBSF/Access/Tmax/2021 a 2040/SSP585"
os.makedirs(saida, exist_ok=True)

# Meses por extenso
meses = {
    "jan": "janeiro", "fev": "fevereiro", "mar": "março", "abr": "abril",
    "mai": "maio", "jun": "junho", "jul": "julho", "ago": "agosto",
    "set": "setembro", "out": "outubro", "nov": "novembro", "dez": "dezembro"
}

# Regex para nomes das camadas
padrao = re.compile(r"Temperatura máxima \(ºC\)_(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)", re.IGNORECASE)

projeto = QgsProject.instance()
manager = projeto.layoutManager()

print("📌 Camadas raster disponíveis no projeto:")
for lyr in projeto.mapLayers().values():
    print(" -", lyr.name())

for layer in projeto.mapLayers().values():
    if layer.type() != layer.RasterLayer:
        continue

    nome = layer.name()
    match = padrao.match(nome)
    if not match:
        continue

    mes = match.group(1).lower()
    mes_ext = meses[mes]
    nome_layout = f"Tmax_{mes}_2021_2040_SSP585"

    print(f"\n🧭 Criando layout: {nome_layout}")

    if not os.path.exists(modelo_qpt):
        print(f"❌ Modelo não encontrado: {modelo_qpt}")
        continue

    # Leitura do modelo
    with open(modelo_qpt, 'r', encoding='utf-8') as f:
        template_content = f.read()

    if not template_content.strip():
        print("❌ Modelo vazio.")
        continue

    # Substituições
    template_modificado = (
        template_content
        .replace("janeiro", mes_ext)
        .replace("Temperatura mínima", "Temperatura máxima")
        .replace("SSP245", "SSP585")
    )

    # Carregando o XML do layout
    doc = QDomDocument()
    if not doc.setContent(template_modificado):
        print("❌ Erro ao carregar XML.")
        continue

    layout = QgsPrintLayout(projeto)
    layout.initializeDefaults()
    layout.setName(nome_layout)
    context = QgsReadWriteContext()

    if not layout.readXml(doc.documentElement(), doc, context):
        print("❌ Erro ao carregar o layout.")
        continue

    if not layout.items():
        print("⚠️ Layout vazio.")
        continue

    # Atualiza mapa, legenda e rótulos
    for item in layout.items():
        if isinstance(item, QgsLayoutItemMap):
            item.setLayers([layer])
            item.zoomToExtent(layer.extent())
        elif isinstance(item, QgsLayoutItemLegend):
            item.model().rootGroup().clear()
            item.model().rootGroup().addLayer(layer)
            item.updateLegend()
        elif isinstance(item, QgsLayoutItemLabel):
            texto = item.text()
            if any(p in texto for p in ["janeiro", "Temperatura mínima", "SSP245"]):
                novo_texto = (
                    texto.replace("janeiro", mes_ext)
                         .replace("Temperatura mínima", "Temperatura máxima")
                         .replace("SSP245", "SSP585")
                )
                item.setText(novo_texto)

    # Exporta PNG
    caminho_png = os.path.join(saida, f"{nome_layout}.png")
    exportador = QgsLayoutExporter(layout)
    status = exportador.exportToImage(caminho_png, QgsLayoutExporter.ImageExportSettings())

    if status == QgsLayoutExporter.Success:
        print(f"✅ PNG exportado: {caminho_png}")
    else:
        print(f"❌ Erro ao exportar PNG: {nome_layout}")

    # Exporta QPT
    caminho_qpt = os.path.join(saida, f"{nome_layout}.qpt")
    doc_final = QDomDocument()
    layout.writeXml(doc_final, context)
    with open(caminho_qpt, 'w', encoding='utf-8') as f:
        f.write(doc_final.toString())
    print(f"📝 Modelo QPT salvo: {caminho_qpt}")

    # Adiciona ao projeto
    manager.addLayout(layout)

print("\n🏁 Geração de layouts finalizada com sucesso para Temperatura Máxima – SSP585.")
