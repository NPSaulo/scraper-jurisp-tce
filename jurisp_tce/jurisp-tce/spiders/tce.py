import scrapy
from ..items import JurispTceItem
from scrapy.loader import ItemLoader
from urllib.parse import urlencode, urljoin
from scrapy.exceptions import CloseSpider


class TceSpider(scrapy.Spider):
    name = "tce"
    allowed_domains = ["www.tce.sp.gov.br"]
    start_urls = "https://www.tce.sp.gov.br/jurisprudencia/pesquisar"
    # a variável offset determina a página de resultados, sobe de 10 em 10.
    offset = 0
    # parâmetros de busca
    params = {
            'acao': 'Executa',
            'txtTdPalvs': input('Todas estas palavras: '),
            'txtExp': input('Esta expressão ou frase exata: '),
            'txtQquma': input('Qualquer uma dessas palavras: '),
            'txtNenhPalvs': input('Nenhuma destas palavras: '),
            'txtNumIni': input('Números que variam de: '),
            'txtNumFim': input('Números que variam até: '),
            'tipoBuscaTxt': input('Tipo de busca: "Documento", "Partes" ou "Objeto"'),
            'quantTrechos': input('Quantidade de trechos, de 0 a 6: '),
            'processo': input('Número do processo: '),
            'exercicio': input('Exercício: '),
            'dataAutuacaoInicio': input('Data de autuação, início: DD/MM/YYYY '),
            'dataAutuacaoFim': input('Data de autuação, fim: DD/MM/YYYY '),
            'dataPubInicio': input('Data de publicação, início: DD/MM/YYYY '),
            'dataPubFim': input('Data de publicação, fim: DD/MM/YYYY '),
            'offset': offset,
            '_tipoBuscaTxt': 'on'
            }


    def start_requests(self):
        #gerando a url com os parâmetros de busca
        encoded_params = '?' + urlencode(self.params)
        url = urljoin(self.start_urls, encoded_params)
        #print(self.start_urls)
        #iniciando os requests, depois a análise e coleta de cada página
        yield scrapy.Request(url, callback=self.parse)

    def checar_conteudo_linha(self, row):
    #função criada em decorrência da estrutura das tabelas das páginas
        if row.css('td.small a[href$=".pdf"]::text'):
            return 'row_dados'
        elif row.css('.trechos-documento'):
            return 'row_trechos'
        else:
            return None


    def parse(self, response):
        #se não houver links para documentos na página, não há registros
        links_docs = response.css('a[href$=".pdf"]::attr(href)').getall()
        if len(links_docs) == 0:
            raise CloseSpider('Fim dos registros / Registros não localizados.')
        #para testes
        #elif self.offset == 30:
            #raise CloseSpider('Offset limite atingido')
        #corpo da tabela de documentos
        registros = response.css('.table.largura.table-docs tbody')
        # estrutura da tabela: uma linha com dados do doc e, após, pode ou não ser uma linha com trechos do documento
        rows = registros.css('tr')
        numero_de_linhas = len(rows) - 1  #desconsiderando a última row, que é o rodapé da tabela, sem informações
        for i in range(0, numero_de_linhas):
            #iniciando um ItemLoader https://docs.scrapy.org/en/latest/topics/loaders.html
            l = ItemLoader(item=JurispTceItem(), response=registros)
            row_atual = rows[i]
            #checando contéudo da linha atual e próxima
            cont_row_atual = self.checar_conteudo_linha(row_atual)
            cont_row_proxima = self.checar_conteudo_linha(rows[i+1])
            #hipótese 1 - row atual com trechos de documento
            if cont_row_atual == 'row_trechos':
                continue
            #hipótese 2 - row atual com dados e row seguinte com trechos
            elif cont_row_atual == 'row_dados' and cont_row_proxima == 'row_trechos':
                trechos_td = rows[i + 1].css('.trechos-documento')
                trechos_text = trechos_td.get()
                l.add_value('trechos_doc', trechos_text)
            #hipótese 3 - row atual com dados e row seguinte sem trechos
            elif cont_row_atual == 'row_dados' and not cont_row_proxima == 'row_trechos':
                l.add_value('trechos_doc', "")
            else:
                pass
            # coletando tipo_doc
            tipo_doc = row_atual.css('td.small a[href$=".pdf"]::text').get().strip()
            # capturando o link para o doc e link para página do proc (onde estão outros dados do doc/proc)
            link_doc = row_atual.css('td.small a[href$=".pdf"]::attr(href)').get()
            link_proc = row_atual.css('td.small a[href*="exibir?"]::attr(href)').get()
            url_pag_proc = 'https://www.tce.sp.gov.br/jurisprudencia/' + link_proc
            # capturando trechos do documento
            l.add_value('tipo_doc', tipo_doc)
            l.add_value('link_doc', link_doc)
            # entrando na página do proc para capturar os dados completos
            #passando o ItemLoader para esse request para não separar os dados em itens diferentes
            #utilizando o método follow da classe Request conforme a documentação https://docs.scrapy.org/en/1.8/topics/request-response.html
            yield response.follow(url_pag_proc, callback=self.parse_proc, meta={'itemloader': l}, dont_filter=True)
            # dont_filter=True porque muitos docs se originam do mesmo processo.
            #igual a
            #yield scrapy.Request(url_pag_proc, callback=self.parse_proc, meta={'itemloader': l}, #dont_filter=True)
        self.offset += 10  # ir para próxima página
        self.params['offset'] = self.offset
        #recriando a url
        encoded_params = '?' + urlencode(self.params)
        next_page = urljoin(self.start_urls, encoded_params)
        #print(next_page)
        yield response.follow(next_page, callback=self.parse)


    def parse_proc(self, response):
        #coletando dados da página do processo, pois incompletos na
        #página de retorno da pesquisa
        l = response.meta['itemloader']
        tabela = response.css('table')
        # [0] pois há outra tabela, [1], que contém a lista de docs do processo
        celulas = tabela[0].css('td')
        #em todas as páginas há, ao menos, 10 células, contendo
        #número do processo, data de autuação,
        #parte 1, parte 2 e matéria
        num_proc = celulas[1].get()
        data_autuacao = celulas[3].get()
        parte_1 = celulas[5].get()
        parte_2 = celulas[7].get()
        materia = celulas[9].get()
        #inserindo os valores no mesmo item criado anteriormente, encaminhado no atributo meta
        l.add_value('num_proc', num_proc)
        l.add_value('data_autuacao', data_autuacao)
        l.add_value('partes', [parte_1, parte_2])
        l.add_value('materia', materia)
        return l.load_item()
