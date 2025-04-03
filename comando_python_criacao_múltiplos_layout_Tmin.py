from qgis.core import (
    QgsProject, QgsLayoutItemLabel, QgsLayoutItemMap, QgsLayoutItemLegend,
    QgsPrintLayout, QgsLayoutExporter, QgsReadWriteContext, QgsLayoutItem
)
from qgis.PyQt.QtXml import QDomDocument
import os
import re

# Caminhos
modelo_qpt = r"Diretório onde está o modelo de layout.qpt"
saida = r"Diretório para o qual se quer exportar os layouts prontos"
os.makedirs(saida, exist_ok=True)

# Meses
meses = {
    "jan": "janeiro", "fev": "fevereiro", "mar": "março", "abr": "abril",
    "mai": "maio", "jun": "junho", "jul": "julho", "ago": "agosto",
    "set": "setembro", "out": "outubro", "nov": "novembro", "dez": "dezembro"
}

# Regex para camadas mensais
padrao = re.compile(r"Temperatura mínima \(ºC\)_(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)", re.IGNORECASE)

projeto = QgsProject.instance()
manager = projeto.layoutManager()

# Verifica as camadas disponíveis
print("📌 Camadas encontradas no projeto:")
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
    nome_layout = f"Tmin_{mes}_2021_2040_SSP245"

    print(f"\n🧭 Criando layout: {nome_layout}")

    # Verifica se o modelo existe
    if not os.path.exists(modelo_qpt):
        print(f"❌ Arquivo de modelo não encontrado: {modelo_qpt}")
        continue

    # Carrega modelo base
    with open(modelo_qpt, 'r', encoding='utf-8') as f:
        template_content = f.read()

    if not template_content.strip():
        print("❌ Conteúdo do modelo está vazio.")
        continue

    # Substituições no XML
    template_modificado = template_content.replace("janeiro", mes_ext)
    template_modificado = template_modificado.replace("Temperatura máxima", "Temperatura mínima")

    # Carrega XML modificado
    doc = QDomDocument()
    if not doc.setContent(template_modificado):
        print("❌ Erro ao carregar XML do modelo modificado.")
        continue

    layout = QgsPrintLayout(projeto)
    layout.initializeDefaults()
    layout.setName(nome_layout)
    context = QgsReadWriteContext()

    if not layout.readXml(doc.documentElement(), doc, context):
        print("❌ Erro ao carregar layout a partir do modelo.")
        continue

    if not layout.items():
        print("⚠️ Layout criado, mas está vazio (nenhum item detectado).")
        continue

    # Substitui camada no mapa e legenda
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
            if "janeiro" in texto or "Temperatura máxima" in texto:
                novo_texto = texto.replace("janeiro", mes_ext).replace("Temperatura máxima", "Temperatura mínima")
                item.setText(novo_texto)

    # Exporta PNG
    caminho_png = os.path.join(saida, f"{nome_layout}.png")
    exportador = QgsLayoutExporter(layout)
    status = exportador.exportToImage(caminho_png, QgsLayoutExporter.ImageExportSettings())

    if status == QgsLayoutExporter.Success:
        print(f"✅ PNG exportado: {caminho_png}")
    else:
        print(f"❌ Falha ao exportar PNG de: {nome_layout}")

    # Salva .qpt final
    caminho_qpt = os.path.join(saida, f"{nome_layout}.qpt")
    doc_final = QDomDocument()
    layout.writeXml(doc_final, context)
    with open(caminho_qpt, 'w', encoding='utf-8') as f:
        f.write(doc_final.toString())
    print(f"📝 Modelo .qpt salvo: {caminho_qpt}")

    # Adiciona ao QGIS
    manager.addLayout(layout)

print("\n🏁 Processo concluído com sucesso.")




