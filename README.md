
# Scraper de Jurisprudência do TCE-SP

## Spider (scraper da framework Scrapy) destinado à raspagem/extração de dados de documentos do TCE-SP pelo site https://www.tce.sp.gov.br/jurisprudencia/.


### Ideia da extração:
 - Envia-se um GET request a https://www.tce.sp.gov.br/jurisprudencia/pesquisar, com um payload na URL;
 - O payload determina os termos da pesquisa, determinado via input (ou lançado _hard-coded_ no script);
 - A estrutura das páginas a ser extraída é a seguinte:
 -  Há sempre uma tabela com a classe '.table.largura.table-docs'.
 -  Nesta, há sempre uma linha de rodapé, sem registros, e, havendo registros, as linhas com registros.
 -  Cada linha de registro pode ser de dois tipos: linha com dados do documento, linha com trechos do documento.
 - Seguindo a estrutura da página, faz-se uma iteração pelas linhas da tabela, excluindo-se a última;
 - Se tiver links para docs, há registros, extração. Se não, fim/ausência de registros;
 - Se houver, verifica-se a cada linha se é caso de linha com dados ou de linha com trechos, para fazer a captura adequada;
 - E, após extrair, salvam-se os dados em arquivos .json separados por ano.
 

### Instruções:

- Mudar para o diretório do projeto scrapy ('cd jurisp_tce');
- Iniciar o crawl pelo comando 'scrapy crawl tce;
- Os parâmetros de pesquisa serão definidos via input;
- Para deixá-los fixos - apropriado para testes - é só questão de trocar as definições no dict params, dentro da TceSpider;
- No mais, as instruções são as gerais para se utilizar Scrapy.

### Comentários:

- A exportação dos itens salvos está sendo feita para arquivos .json separados por ano, por meio de uma pipeline;
- Indo pela documentação, seria melhor fazer isso pelo FEED. Para simplificar, deixou-se assim;
- O delay em settings.py está definido em 3.
- Os dados são salvos após cada extração, ao invés de apenas no final de todo o roteiro.
