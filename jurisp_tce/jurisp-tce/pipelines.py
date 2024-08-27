from collections import OrderedDict
import json



'''
Como esclarecido na documentação em
https://docs.scrapy.org/en/latest/topics/item-pipeline.html e
https://docs.scrapy.org/en/latest/topics/feed-exports.html ,
seria mais apropriado estabelecer um feed para exportação dos itens.

Para o propósito aqui estabelecido, mera demonstração, se estabeleceu esse simples método
de salvar os itens em arquivos .json separados por ano.
'''

class JsonWriterPipeline:
    def process_item(self, item, spider):
        #reorganizando o conteúdo do item, para ficar na ordem desejada
        ordered_dict = OrderedDict([('tipo_doc', item['tipo_doc']), ('num_proc',item['num_proc']), ('data_autuacao', item['data_autuacao']),
                                    ('partes', item['partes']), ('materia', item['materia']), ('link_doc', item['link_doc']),
                                    ('trechos_doc', item['trechos_doc'])])
        self.file = open(f"{item['data_autuacao'][-4:]}.json","a", encoding='utf-8')
        line = json.dumps(ordered_dict,ensure_ascii=False) + "\n" #ensure_ascii=False para evitar "p\u00e1gina", "Cart\u00f3rio" etc.
        self.file.write(line)
        return item


