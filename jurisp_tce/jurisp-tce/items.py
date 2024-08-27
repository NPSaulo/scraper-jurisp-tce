from scrapy.item import Item, Field
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags


def remover_espaços_trechos(value):
    #função para retirar espaços em branco, tabs e newlines
    return value.replace('\n', '').replace('\t', '').strip()

class JurispTceItem(Item):
    #MapCompose(remove_tags) para remover as tags
    #TakeFirst para que os valores não fiquem salvos em lista, exceto para partes
    tipo_doc = Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    num_proc = Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    #removendo espaço após o fim da data
    data_autuacao = Field(input_processor=MapCompose(remove_tags, remover_espaços_trechos), output_processor=TakeFirst())
    partes = Field(input_processor=MapCompose(remove_tags))
    materia = Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    link_doc = Field(output_processor=TakeFirst())
    #removendo tabs, newlines e espaços
    trechos_doc = Field(input_processor=MapCompose(remove_tags, remover_espaços_trechos), output_processor=TakeFirst())

