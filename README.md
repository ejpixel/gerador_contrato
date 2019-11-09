# Gerador de contrato
Para reduzir o tempo necessário na geração de novos contratos e evitar erros nas informações, esse projeto tenta facilitar ao máximo esse processo

## Uso
É necessário clonar de forma recursiva para utilizar o submodulo de conversão de números
```
git clone https://github.com/ejpixel/pixel_auto.git --recursive
```

### Database
Para acessar alguns dados pessoais, é necessário um banco de dados protegido. Por conta disso, o programa necessita que seja criado uma variável de ambiente com o link de acesso ao banco.

### Linux
```
make setup
export DATABASE_URI=<url do banco>
make run
```

### Windows
TODO

### Final
Visitar http://localhost:5000 e preencher todos os campos para no fim submeter o formulário e criar o arquivo de contrato (em docx)

## Erros
```
Error: pg_config executable not found.
```
Solução: instalar libpq-dev (ubuntu)
