from docxtpl import DocxTemplate
from profiles import *
import sys
import os
from number_to_word.number_to_word import convert_to_word

TEMPLATE = "template.docx"
OUTPUT = "contract.docx"

def gen_info(service, client, ej):
    # Necessário para gerar contrato: tipo de contrato, deadline, descrição curta, preço,
    # parcelas, lista de serviços que serão prestados, nome da loja, endereço, cnpj, nome do cliente, rg, cpf
    contract_info = {
        "type_contract":             service.type_contract.upper(),
        "type_contract_lower":       service.type_contract.lower(),
        "deadline":                  service.deadline,
        "cursive_deadline":          convert_to_word(service.deadline),
        "short_service_description": service.short_service_description,
        "price":                     service.price,
        "cursive_price":             convert_to_word(service.price),
        "price_currency":            get_correct_number_flexion(service.price, "real", "reais"),
        "cursive_payment":           get_fem_gender_flexion(convert_to_word(service.payment)),
        "payment_price":             service.payment_price,
        "cursive_payment_price":     convert_to_word(service.payment_price),
        "payment_currency":          get_correct_number_flexion(service.payment_price, "real", "reais"),
        "service_list":              service.service_list,
        "client_store_name":         client.store.name.upper(),
        "client_address":            client.address,
        "client_cnpj":               client.store.get_formated_cnpj(),
        "client_name":               client.client.name,
        "client_rg":                 client.client.rg,
        "client_cpf":                client.client.get_formated_cpf(),
        "ata_date":                  format_date(ej.ata_date),
        "pixel_president":           ej.president.name,
        "pixel_president_rg":        ej.president.rg,
        "pixel_president_cpf":       ej.president.get_formated_cpf(),
        "pixel_gi":                  ej.gi.name,
        "pixel_gi_rg":               ej.gi.rg,
        "pixel_gi_cpf":              ej.gi.get_formated_cpf()
}
    return contract_info

def format_date(date_iso_format):
    date_list = str(date_iso_format).split("-")
    months = {
        "01": "janeiro",
        "02": "fevereiro",
        "03": "março",
        "04": "abril",
        "05": "maio",
        "06": "junho",
        "07": "julho",
        "08": "agosto",
        "09": "setembro",
        "10": "outubro",
        "11": "novembro",
        "12": "dezembro"    
    }

    return f"{'primeiro' if date_list[2] == '01' else convert_to_word(date_list[2])} de {months[date_list[1]]} de {date_list[0]}"

def get_correct_number_flexion(number, singular, plural):
    if number == "1":
        return singular
    return plural

def get_fem_gender_flexion(word_number):
    if word_number == "um":
        return "uma"
    elif word_number == "dois":
        return "duas"
    return word_number

def gen_contract(template, info, output):
    contract_template = DocxTemplate(template)
    contract_template.render(info)
    contract_template.save(output)

def temp_wizard():
    (t_c, deadline, s_s_d, price, payment,
     payment_price, date, s_list, store_name, address, 
     cnpj, name, rg, cpf, ata, ej_p, ej_p_rg, ej_p_cpf, ej_gi,
     ej_gi_rg, ej_gi_cpf) = sys.argv[1:]
    service = Service(t_c, deadline, s_s_d, price, payment,
              payment_price, date, s_list)
    client = Client(store_name, address, cnpj, name, rg, cpf)
    ej = EJ(ata, ej_p, ej_p_rg, ej_p_cpf, ej_gi, ej_gi_rg, ej_gi_cpf)

    return service, client, ej

def main():
    if len(sys.argv) < 24:
        sys.exit(-1)
    service, client, ej = temp_wizard()
    info = gen_info(service, client, ej)
    gen_contract(TEMPLATE, info, OUTPUT)

if __name__ == "__main__":
        main()
